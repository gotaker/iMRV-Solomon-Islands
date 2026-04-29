"""
bench.runner.a_runner — A-tier deterministic scenario runner.

Reads YAML scenario files, drives Playwright through their `steps`, evaluates
`assertions`, and emits a scorecard. A-tier is a hard gate: any failed assertion
across any scenario → exit 1 → deploy blocked.

The runner is intentionally small. Step + assertion vocabularies are
declarative; complex logic belongs in custom_runner: <file>.py (not used in
Phase 1).

Entry point: invoked by bench/bench.sh as `python3 -m bench.runner.a_runner`.
Standalone usage:
    python3 -m bench.runner.a_runner --config bench/config.yaml \
        --target local-docker --tier a [--scenarios <glob>] [--roles <csv>]
        [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = REPO_ROOT / "bench"


@dataclass
class AssertionResult:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class ScenarioResult:
    scenario_id: str
    role: str
    persona: str
    journey_path: str
    duration_ms: int
    passed: bool
    assertions: list[AssertionResult] = field(default_factory=list)
    error: str | None = None
    screenshot_path: str | None = None


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_target(config: dict[str, Any], target: str) -> dict[str, Any]:
    targets = config.get("targets", {})
    if target not in targets:
        raise SystemExit(f"[bench] unknown target '{target}'. Configured: {sorted(targets)}")
    spec = dict(targets[target])
    if "base_url" not in spec:
        env_var = spec.get("base_url_env")
        if not env_var:
            raise SystemExit(f"[bench] target '{target}' has neither base_url nor base_url_env")
        url = os.environ.get(env_var)
        if not url:
            raise SystemExit(
                f"[bench] target '{target}' requires env var {env_var} (not set). "
                f"Export it before running."
            )
        spec["base_url"] = url.rstrip("/")
    spec["name"] = target
    return spec


def _discover_scenarios(glob: str | None) -> list[Path]:
    """Return the list of scenario YAML files to run, sorted for stable ordering."""
    if glob:
        # User-supplied glob is interpreted relative to bench/.
        return sorted(BENCH_ROOT.glob(glob))
    paths: list[Path] = []
    for sub in ("journeys", "regression"):
        paths.extend((BENCH_ROOT / "scenarios" / sub).rglob("*.yaml"))
    return sorted(paths)


def _git_short_sha() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, text=True
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _new_run_id() -> str:
    return f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{_git_short_sha()}"


# --- Step executor ---------------------------------------------------------
#
# Each step has exactly one keyword key (navigate, wait_for_selector, capture,
# fill, click, login_as). Unknown keywords surface as "unknown step" assertion
# failures — we never silently ignore.

def _step_navigate(page, value: str, base_url: str) -> None:
    if value.startswith("/"):
        url = base_url + value
    else:
        url = value
    page.goto(url, wait_until="domcontentloaded")


def _step_wait_for_selector(page, value: dict | str, default_timeout_ms: int) -> None:
    if isinstance(value, str):
        page.wait_for_selector(value, timeout=default_timeout_ms)
        return
    selector = value.get("selector") or value.get("value")
    timeout = value.get("timeout_ms", default_timeout_ms)
    page.wait_for_selector(selector, timeout=timeout)


def _step_capture(page, name: str, run_dir: Path, scenario_id: str) -> str:
    out_dir = run_dir / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^a-z0-9_-]+", "_", f"{scenario_id}__{name}".lower())
    path = out_dir / f"{safe}.png"
    page.screenshot(path=str(path), full_page=True)
    return str(path.relative_to(REPO_ROOT))


def _step_fill(page, value: dict) -> None:
    page.fill(value["selector"], value["value"])


def _step_click(page, value: str) -> None:
    page.click(value)


def _step_login_as(page, role: str, base_url: str, credentials: dict[str, dict]) -> None:
    creds = credentials.get(role)
    if not creds:
        raise RuntimeError(f"no fixture credentials for role '{role}'")
    page.goto(f"{base_url}/login", wait_until="domcontentloaded")
    page.fill('input[name="login_email"], input#login_email', creds["email"])
    page.fill('input[name="login_password"], input#login_password', creds["password"])
    page.click('button[type="submit"], button:has-text("Login")')
    page.wait_for_url(re.compile(r".*/(app|desk)/.*"), timeout=15_000)


def _execute_steps(page, steps: list[dict], ctx: dict) -> str | None:
    """Run each step. Returns the first capture's screenshot path (for scorecard)."""
    first_capture: str | None = None
    base_url = ctx["base_url"]
    default_timeout = ctx["settle_timeout_ms"]
    credentials = ctx["credentials"]
    run_dir = ctx["run_dir"]
    scenario_id = ctx["scenario_id"]

    for step in steps:
        if not isinstance(step, dict) or len(step) != 1:
            raise RuntimeError(f"malformed step (expected single-key dict): {step!r}")
        ((kind, value),) = step.items()
        if kind == "navigate":
            _step_navigate(page, value, base_url)
        elif kind == "wait_for_selector":
            _step_wait_for_selector(page, value, default_timeout)
        elif kind == "capture":
            path = _step_capture(page, value, run_dir, scenario_id)
            if first_capture is None:
                first_capture = path
        elif kind == "fill":
            _step_fill(page, value)
        elif kind == "click":
            _step_click(page, value)
        elif kind == "login_as":
            _step_login_as(page, value, base_url, credentials)
        else:
            raise RuntimeError(f"unknown step kind '{kind}'")
    return first_capture


# --- Assertion evaluator ---------------------------------------------------
#
# Each assertion is a single-key dict. The runner evaluates each independently
# so one failure doesn't short-circuit the rest — full failure context per
# scenario aids triage.

def _assert_selector(page, value: dict) -> AssertionResult:
    selector = value["selector"]
    count_spec = value.get("count")
    locator = page.locator(selector)
    actual = locator.count()
    if count_spec is None:
        passed = actual >= 1
        detail = f"{selector!r} count={actual}"
    elif isinstance(count_spec, dict):
        lo = count_spec.get("min")
        hi = count_spec.get("max")
        passed = (lo is None or actual >= lo) and (hi is None or actual <= hi)
        detail = f"{selector!r} count={actual} (expected min={lo} max={hi})"
    else:
        passed = actual == int(count_spec)
        detail = f"{selector!r} count={actual} (expected {count_spec})"

    if passed and value.get("has_natural_width"):
        widths = locator.evaluate_all(
            "els => els.map(e => e.naturalWidth || 0)"
        )
        zero = [i for i, w in enumerate(widths) if not w]
        if zero:
            passed = False
            detail += f"; {len(zero)} of {len(widths)} have naturalWidth=0"
    return AssertionResult("selector", passed, detail)


def _assert_no_console_error_matching(console_errors: list[str], pattern: str) -> AssertionResult:
    rgx = re.compile(pattern)
    matched = [e for e in console_errors if rgx.search(e)]
    return AssertionResult(
        "no_console_error_matching",
        passed=not matched,
        detail=f"pattern={pattern!r} matched={len(matched)} (showing 3): {matched[:3]}",
    )


def _assert_no_network_4xx_for_path(failed_responses: list[tuple[str, int]], path_glob: str) -> AssertionResult:
    pattern = re.compile(_glob_to_regex(path_glob))
    matched = [(u, s) for (u, s) in failed_responses if pattern.search(u) and 400 <= s < 500]
    return AssertionResult(
        "no_network_4xx_for_path",
        passed=not matched,
        detail=f"path={path_glob!r} matched={len(matched)} (showing 3): {matched[:3]}",
    )


def _assert_url_matches(page, value: str) -> AssertionResult:
    actual = page.url
    if value.startswith("regex:"):
        rgx = re.compile(value[len("regex:") :])
        passed = bool(rgx.search(actual))
        detail = f"url={actual!r} regex={value!r}"
    else:
        passed = value in actual
        detail = f"url={actual!r} expected_substring={value!r}"
    return AssertionResult("url_matches", passed, detail)


def _glob_to_regex(glob: str) -> str:
    """Convert a simple URL glob (e.g. /files/*) to a regex. * → [^?#]*."""
    parts = glob.split("*")
    return ".*".join(re.escape(p) for p in parts) if "*" in glob else f"^{re.escape(glob)}"


def _evaluate_assertions(
    assertions: list[dict],
    page,
    console_errors: list[str],
    failed_responses: list[tuple[str, int]],
) -> list[AssertionResult]:
    results: list[AssertionResult] = []
    for spec in assertions:
        if not isinstance(spec, dict) or len(spec) != 1:
            results.append(AssertionResult("malformed", False, f"expected single-key dict: {spec!r}"))
            continue
        ((kind, value),) = spec.items()
        try:
            if kind == "selector":
                results.append(_assert_selector(page, value))
            elif kind == "no_console_error_matching":
                results.append(_assert_no_console_error_matching(console_errors, value))
            elif kind == "no_network_4xx_for_path":
                results.append(_assert_no_network_4xx_for_path(failed_responses, value))
            elif kind == "url_matches":
                results.append(_assert_url_matches(page, value))
            elif kind == "design_system":
                from bench.runner.design_system_checks import check_page, summarize
                aspects = value if isinstance(value, dict) else {}
                ds_results = check_page(page, aspects)
                passed, detail = summarize(ds_results)
                results.append(AssertionResult("design_system", passed, detail))
            else:
                results.append(AssertionResult(kind, False, f"unknown assertion kind '{kind}'"))
        except Exception as exc:  # noqa: BLE001 — explicit assertion-level error reporting
            results.append(AssertionResult(kind, False, f"exception: {exc!r}"))
    return results


# --- Per-scenario driver ---------------------------------------------------

def _run_scenario(
    scenario_path: Path,
    target: dict,
    credentials: dict,
    run_dir: Path,
    config: dict,
    browser,
    dry_run: bool,
) -> ScenarioResult:
    spec = _load_yaml(scenario_path)
    scenario_id = spec.get("id") or scenario_path.stem
    perspective = spec.get("perspective", {}) or {}
    role = perspective.get("role", "guest")
    persona = perspective.get("persona", "standard")
    steps = spec.get("steps", []) or []
    assertions = spec.get("assertions", []) or []

    if dry_run:
        return ScenarioResult(
            scenario_id=scenario_id,
            role=role,
            persona=persona,
            journey_path=str(scenario_path.relative_to(REPO_ROOT)),
            duration_ms=0,
            passed=True,
        )

    viewport = config["defaults"]["viewport"]
    settle = config["defaults"]["settle_timeout_ms"]
    nav_timeout = config["defaults"]["navigation_timeout_ms"]

    context = browser.new_context(viewport=viewport)
    page = context.new_page()
    page.set_default_navigation_timeout(nav_timeout)
    page.set_default_timeout(settle)

    console_errors: list[str] = []
    failed_responses: list[tuple[str, int]] = []
    page.on(
        "console",
        lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
    )
    page.on(
        "response",
        lambda r: failed_responses.append((r.url, r.status)) if r.status >= 400 else None,
    )

    started = time.monotonic()
    error: str | None = None
    screenshot_path: str | None = None
    assertion_results: list[AssertionResult] = []

    try:
        ctx = {
            "base_url": target["base_url"].rstrip("/"),
            "settle_timeout_ms": settle,
            "credentials": credentials,
            "run_dir": run_dir,
            "scenario_id": scenario_id,
        }
        screenshot_path = _execute_steps(page, steps, ctx)
        assertion_results = _evaluate_assertions(
            assertions, page, console_errors, failed_responses
        )
    except Exception as exc:  # noqa: BLE001 — per-scenario error containment
        error = f"step execution failed: {exc!r}"
        # Best-effort failure screenshot.
        try:
            screenshot_path = _step_capture(page, "step-failure", run_dir, scenario_id)
        except Exception:
            pass
    finally:
        context.close()

    duration_ms = int((time.monotonic() - started) * 1000)
    passed = error is None and all(a.passed for a in assertion_results)
    return ScenarioResult(
        scenario_id=scenario_id,
        role=role,
        persona=persona,
        journey_path=str(scenario_path.relative_to(REPO_ROOT)),
        duration_ms=duration_ms,
        passed=passed,
        assertions=assertion_results,
        error=error,
        screenshot_path=screenshot_path,
    )


# --- Scorecard -------------------------------------------------------------

def _emit_scorecard(results: list[ScenarioResult], target: dict, run_dir: Path) -> dict:
    by_role: dict[str, dict[str, int]] = {}
    for r in results:
        slot = by_role.setdefault(r.role, {"passed": 0, "total": 0})
        slot["total"] += 1
        if r.passed:
            slot["passed"] += 1

    total = len(results)
    passed = sum(1 for r in results if r.passed)

    scorecard = {
        "schema_version": 1,
        "run_id": run_dir.name,
        "target": target["name"],
        "base_url": target["base_url"],
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "a_tier": {
            "passed": passed,
            "total": total,
            "rate": (passed / total) if total else 1.0,
            "by_role": by_role,
            "failures": [
                {
                    "scenario_id": r.scenario_id,
                    "role": r.role,
                    "persona": r.persona,
                    "journey_path": r.journey_path,
                    "error": r.error,
                    "failed_assertions": [
                        {"kind": a.name, "detail": a.detail} for a in r.assertions if not a.passed
                    ],
                }
                for r in results
                if not r.passed
            ],
        },
        "scenarios": [
            {
                "scenario_id": r.scenario_id,
                "role": r.role,
                "persona": r.persona,
                "journey_path": r.journey_path,
                "duration_ms": r.duration_ms,
                "passed": r.passed,
                "screenshot_path": r.screenshot_path,
                "assertions": [
                    {"kind": a.name, "passed": a.passed, "detail": a.detail} for a in r.assertions
                ],
            }
            for r in results
        ],
    }
    (run_dir / "scorecard.json").write_text(json.dumps(scorecard, indent=2))
    return scorecard


def _render_terminal_summary(scorecard: dict) -> None:
    a = scorecard["a_tier"]
    rate_pct = a["rate"] * 100
    verdict = "PASS" if a["rate"] >= 1.0 else "FAIL"
    bar = "═" * 63
    print(bar)
    print(f"  iMRV Test Bench — {scorecard['run_id']}")
    print(f"  Target: {scorecard['target']} ({scorecard['base_url']})")
    print(bar)
    print(f"  A-tier: {a['passed']} / {a['total']} pass  ({rate_pct:.1f}%)  -> {verdict}")
    if a["by_role"]:
        print()
        print("  Per-role sub-scores:")
        for role, slot in sorted(a["by_role"].items()):
            r_pct = (slot["passed"] / slot["total"] * 100) if slot["total"] else 0.0
            print(f"    {role:<24} {slot['passed']:>3} / {slot['total']:<3}  ({r_pct:.1f}%)")
    if a["failures"]:
        print()
        print(f"  FAILED ({len(a['failures'])}):")
        for f in a["failures"]:
            err_summary = f["error"] or (
                f["failed_assertions"][0]["detail"] if f["failed_assertions"] else "no assertions"
            )
            print(f"    ✗ {f['scenario_id']} — {err_summary[:80]}")
    print(bar)


# --- Entry point -----------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="iMRV bench A-tier runner")
    parser.add_argument("--config", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--tier", default="a")
    parser.add_argument("--scenarios", default=None)
    parser.add_argument("--roles", default=None)
    parser.add_argument("--update-golden", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--run-id", default=None,
                        help="explicit run-id (default = generated from now+sha)")
    args = parser.parse_args(argv)

    config = _load_yaml(Path(args.config))
    target = _load_target(config, args.target)

    creds_path = BENCH_ROOT / "fixtures" / "role_credentials.yaml"
    credentials = _load_yaml(creds_path) if creds_path.exists() else {}

    scenarios = _discover_scenarios(args.scenarios)
    if not scenarios:
        print("[bench] no scenarios discovered; nothing to run", file=sys.stderr)
        return 2

    if args.roles:
        wanted = {r.strip() for r in args.roles.split(",") if r.strip()}
        scenarios = [s for s in scenarios if (_load_yaml(s).get("perspective") or {}).get("role") in wanted]

    run_id = args.run_id or _new_run_id()
    run_dir = BENCH_ROOT / "history" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"[bench] target={args.target} base_url={target['base_url']} scenarios={len(scenarios)}")

    if args.dry_run:
        print("[bench] --dry-run set — listing scenarios only:")
        for s in scenarios:
            print(f"  {s.relative_to(REPO_ROOT)}")
        return 0

    # Lazy import: keeps `--dry-run` and `--help` working without Playwright.
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "[bench] playwright not installed. From the bench root:\n"
            "  pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        return 2

    results: list[ScenarioResult] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for scenario in scenarios:
                rel = scenario.relative_to(REPO_ROOT)
                print(f"[bench] running {rel}")
                result = _run_scenario(
                    scenario, target, credentials, run_dir, config, browser, args.dry_run
                )
                results.append(result)
                status = "PASS" if result.passed else "FAIL"
                print(f"        -> {status} ({result.duration_ms} ms)")
        finally:
            browser.close()

    scorecard = _emit_scorecard(results, target, run_dir)
    _render_terminal_summary(scorecard)
    return 0 if scorecard["a_tier"]["rate"] >= 1.0 else 1


if __name__ == "__main__":
    sys.exit(main())
