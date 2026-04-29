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


def _step_scan_master_data(page, base_url: str, options: dict | None) -> None:
    """
    Hit Frappe's REST API to enumerate record names across a list of doctypes,
    then concatenate them into the page's `_captured_text` so typo deny-list
    assertions cover not just rendered HTML but also master-data record names.

    The "document resorce tool" typo lived in a Side Menu record name — the
    drawer rendered a corrected display label, so a screenshot scan alone
    couldn't catch it. This step pulls record names directly.

    Options:
        doctypes: ["Side Menu", "Sub Menu", "Master Data"]    # default below
        max_per_doctype: 500
    """
    options = options or {}
    doctypes = options.get("doctypes") or [
        "Side Menu", "Sub Menu", "Sub Menu Group",
        "Knowledge Resource", "MrvFrontend",
    ]
    max_per_doctype = int(options.get("max_per_doctype", 500))

    # Reuse the page's existing session by extracting cookies and posting to
    # the Frappe REST API via JS. Avoids a parallel Python requests session.
    collected_text = page.evaluate(
        """async (args) => {
            const { doctypes, max_per_doctype } = args;
            const lines = [];
            for (const dt of doctypes) {
                try {
                    const url = `/api/resource/${encodeURIComponent(dt)}`
                                + `?limit_page_length=${max_per_doctype}&fields=${encodeURIComponent('["name"]')}`;
                    const r = await fetch(url, { credentials: 'include' });
                    if (!r.ok) continue;
                    const json = await r.json();
                    for (const row of (json.data || [])) {
                        if (row && row.name) lines.push(`[${dt}] ${row.name}`);
                    }
                } catch (_) { /* doctype may not exist; skip */ }
            }
            return lines.join('\\n');
        }""",
        {"doctypes": doctypes, "max_per_doctype": max_per_doctype},
    )
    existing = getattr(page, "_captured_text", "") or ""
    page._captured_text = existing + "\n" + collected_text  # type: ignore[attr-defined]


def _step_walk_drawer(page, base_url: str, options: dict | None = None) -> None:
    """
    Open the floating drawer, click each top-level link, capture the destination's
    health (status, body text length, h1/page-title presence, console errors,
    failed responses), then return to the drawer between entries.

    The result is stashed on the page object as `_drawer_walk_results` so the
    `drawer_destinations_healthy` assertion can read it without re-walking.

    Memory cross-ref: feedback_qa_clickthrough_required.md says drawer tests
    must click destinations — this step is that rule turned into automation.
    """
    options = options or {}
    selector_link = options.get("link_selector", "#fsm-drawer a[href]")
    settle_ms = int(options.get("settle_timeout_ms", 5000))
    raw_skip = options.get("skip_patterns", ["logout", "mailto:", "tel:"])
    # YAML parses `mailto:` (unquoted colon) as a `{mailto: None}` dict in flow
    # lists. Coerce defensively so a malformed scenario doesn't TypeError mid-walk.
    skip_patterns: list[str] = []
    for p in raw_skip:
        if isinstance(p, str):
            skip_patterns.append(p)
        elif isinstance(p, dict):
            skip_patterns.extend(f"{k}:" for k in p.keys())

    # Open the drawer if not already open. Idempotent click.
    try:
        page.click(".fsm-trigger", timeout=settle_ms)
    except Exception:
        pass  # may already be open, or trigger not present (SPA pages)
    page.wait_for_selector(selector_link, timeout=settle_ms)

    # Snapshot drawer entries up front: text + href, so a navigation doesn't
    # invalidate the locator handle mid-loop.
    entries: list[dict[str, str]] = page.locator(selector_link).evaluate_all(
        "els => els.map(e => ({"
        "  href: e.href || e.getAttribute('href') || '',"
        "  text: (e.textContent || '').trim().replace(/\\s+/g, ' ')"
        "}))"
    )

    # Also collect *text-bearing items in the drawer that look like nav entries
    # but have NO href / data-route / click handler*. These are the dead-link
    # class: visible "MITIGATION" text rendered as <a> but going nowhere.
    # Stashed on the page object for the `drawer_no_dead_links` assertion.
    dead_links: list[dict[str, str]] = page.evaluate(
        """() => {
            const drawer = document.querySelector('#fsm-drawer, .main-sidebar');
            if (!drawer) return [];
            const items = Array.from(drawer.querySelectorAll('a, button, [role="link"], [data-route]'));
            return items
                .filter(el => {
                    const text = (el.textContent || '').trim();
                    if (text.length < 2) return false;
                    if (text.length > 80) return false;            // skip large containers
                    const href = el.getAttribute('href') || '';
                    const dataRoute = el.getAttribute('data-route') || '';
                    const onclick = el.getAttribute('onclick') || '';
                    const looksNavigable = (href && href !== '#' && !href.startsWith('javascript:'))
                                           || dataRoute || onclick;
                    return !looksNavigable;
                })
                .map(el => ({
                    text: (el.textContent || '').trim().replace(/\\s+/g, ' '),
                    tag: el.tagName,
                    classes: el.className || '',
                }));
        }"""
    )
    page._drawer_dead_links = dead_links  # type: ignore[attr-defined]
    # De-dupe by canonical href (some drawers repeat the same link inline).
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for e in entries:
        if not e["href"] or any(p in e["href"].lower() for p in skip_patterns):
            continue
        if e["href"] in seen:
            continue
        seen.add(e["href"])
        unique.append(e)

    results: list[dict] = []
    for entry in unique:
        href = entry["href"]
        text = entry["text"] or "(no text)"

        # Per-destination instrumentation: console errors and failed responses
        # are scoped to this navigation only.
        local_errors: list[str] = []
        local_failed: list[tuple[str, int]] = []
        err_handler = lambda msg: local_errors.append(msg.text) if msg.type == "error" else None
        resp_handler = lambda r: local_failed.append((r.url, r.status)) if r.status >= 400 else None
        page.on("console", err_handler)
        page.on("response", resp_handler)

        try:
            response = page.goto(href, wait_until="domcontentloaded", timeout=settle_ms * 3)
            status = response.status if response else 0
            # Settle: wait briefly for h1 / page-title / SPA mount; not all
            # destinations have all three, so any-of is enough.
            try:
                page.wait_for_selector(
                    "h1, .page-title, [data-v-app], .layout-main-section",
                    timeout=settle_ms,
                    state="attached",
                )
            except Exception:
                pass
            body_length = page.evaluate("() => document.body ? document.body.innerText.length : 0")
            has_heading = page.evaluate(
                "() => !!document.querySelector('h1, .page-title')"
            )
            has_main = page.evaluate(
                "() => !!document.querySelector('main, .layout-main-section, [data-v-app]')"
            )
            results.append({
                "drawer_text": text,
                "href": href,
                "final_url": page.url,
                "status": status,
                "body_text_length": body_length,
                "has_heading": has_heading,
                "has_main": has_main,
                "console_errors": list(local_errors),
                "failed_responses": [{"url": u, "status": s} for u, s in local_failed],
            })
        except Exception as exc:  # noqa: BLE001
            results.append({
                "drawer_text": text,
                "href": href,
                "final_url": "",
                "status": 0,
                "body_text_length": 0,
                "has_heading": False,
                "has_main": False,
                "console_errors": [f"navigation exception: {exc!r}"],
                "failed_responses": [],
            })
        finally:
            page.remove_listener("console", err_handler)
            page.remove_listener("response", resp_handler)

    page._drawer_walk_results = results  # type: ignore[attr-defined]


def _step_capture_text(page, name: str, run_dir: Path, scenario_id: str) -> str:
    """Persist the visible text content of the page for typo/spelling checks."""
    out_dir = run_dir / "text"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^a-z0-9_-]+", "_", f"{scenario_id}__{name}".lower())
    path = out_dir / f"{safe}.txt"
    text = page.evaluate("() => document.body ? document.body.innerText : ''")
    path.write_text(text or "", encoding="utf-8")
    page._captured_text = text or ""  # type: ignore[attr-defined]
    return str(path.relative_to(REPO_ROOT))


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
        elif kind == "walk_drawer":
            _step_walk_drawer(page, base_url, value if isinstance(value, dict) else None)
        elif kind == "capture_text":
            _step_capture_text(page, value, run_dir, scenario_id)
        elif kind == "scan_master_data":
            _step_scan_master_data(page, base_url, value if isinstance(value, dict) else None)
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


def _assert_drawer_destinations_healthy(page, options: dict | None) -> AssertionResult:
    """
    Verify every drawer entry walked by `walk_drawer` produced a healthy destination.

    Health = status is 2xx/3xx, body text length above min, has a heading or
    main region, no console errors. Per-entry results live on the page object
    via `_drawer_walk_results`.

    This is the assertion the bench was missing — the screenshot-only Approver
    scenario opens the drawer but never clicks. This walks AND asserts.
    """
    options = options or {}
    min_body_text = int(options.get("min_body_text_length", 50))
    require_heading = options.get("require_heading", True)
    allowed_4xx = set(options.get("allowed_4xx_for_paths", []))

    results = getattr(page, "_drawer_walk_results", None)
    if results is None:
        return AssertionResult(
            "drawer_destinations_healthy",
            passed=False,
            detail="walk_drawer step was not executed before this assertion",
        )

    failures: list[str] = []
    for r in results:
        text = r.get("drawer_text") or "(no text)"
        href = r.get("href") or ""
        status = r.get("status") or 0
        body_len = r.get("body_text_length") or 0

        if status < 200 or status >= 400:
            # Allow specific paths to 4xx (e.g., logout intentionally redirects).
            if not any(p in href for p in allowed_4xx):
                failures.append(f"[{text}] {href} → status={status}")
                continue

        if body_len < min_body_text:
            failures.append(f"[{text}] {href} → body_text={body_len}<{min_body_text}")
            continue

        if require_heading and not r.get("has_heading"):
            failures.append(f"[{text}] {href} → no h1/.page-title")
            continue

        # Console errors with hard-error keywords are leaks.
        for err in r.get("console_errors", []):
            if any(k in err for k in ("TypeError", "ReferenceError", "404", "PermissionError")):
                failures.append(f"[{text}] {href} → console: {err[:80]}")
                break

    return AssertionResult(
        "drawer_destinations_healthy",
        passed=not failures,
        detail=(
            f"walked {len(results)} entries; failures={len(failures)}: " + "; ".join(failures[:5])
            if failures else f"all {len(results)} drawer destinations healthy"
        ),
    )


def _assert_drawer_no_dead_links(page, options: dict | None) -> AssertionResult:
    """
    Assert that no drawer item presents itself as a nav link without actually
    being navigable. Catches the class where a designer styles a `<span>` /
    href-less `<a>` as a link but no router target is wired.

    `walk_drawer` must run first (populates `_drawer_dead_links`).

    Allowlist via `decorative_text_allowlist: ["ACTIONS", "USERS"]` for known
    section *labels* that are intentionally non-navigable. Anything outside
    the allowlist is a leak.
    """
    options = options or {}
    allowlist = {s.upper() for s in options.get("decorative_text_allowlist", [])}

    items = getattr(page, "_drawer_dead_links", None)
    if items is None:
        return AssertionResult(
            "drawer_no_dead_links",
            passed=False,
            detail="walk_drawer step was not executed before this assertion",
        )

    leaks = [it for it in items if it.get("text", "").upper() not in allowlist]
    return AssertionResult(
        "drawer_no_dead_links",
        passed=not leaks,
        detail=(
            f"{len(leaks)} dead nav item(s): "
            + "; ".join(f"[{it['tag']}] {it['text']!r}" for it in leaks[:10])
            if leaks else f"all {len(items)} non-navigable drawer items are in allowlist"
        ),
    )


def _assert_no_text_matching(page, value: dict | str) -> AssertionResult:
    """
    Assert the captured page text does NOT contain any pattern in a deny-list.

    Two forms:
      - value: "<pattern>"           — single regex
      - value: { denylist_file: "...", patterns: [...] }
                                     — patterns inline + load file (one per line)

    Matches the typo class of bug — "resorce" instead of "resource", common
    misspellings of "committee", "occurrence", etc. The deny-list at
    bench/fixtures/typo_denylist.txt is the seed corpus.
    """
    text = getattr(page, "_captured_text", None)
    if text is None:
        try:
            text = page.evaluate("() => document.body ? document.body.innerText : ''")
        except Exception:
            text = ""

    patterns: list[str] = []
    if isinstance(value, str):
        patterns = [value]
    elif isinstance(value, dict):
        patterns = list(value.get("patterns") or [])
        denylist_file = value.get("denylist_file")
        if denylist_file:
            path = Path(denylist_file)
            if not path.is_absolute():
                path = REPO_ROOT / path
            if path.exists():
                for line in path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)

    if not patterns:
        return AssertionResult("no_text_matching", True, "no patterns supplied")

    matched: list[tuple[str, str]] = []
    for p in patterns:
        try:
            rgx = re.compile(p, re.IGNORECASE)
        except re.error as exc:
            matched.append((p, f"invalid regex: {exc}"))
            continue
        m = rgx.search(text)
        if m:
            # Capture short context for triage.
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 30)
            matched.append((p, f"...{text[start:end]!r}..."))

    return AssertionResult(
        "no_text_matching",
        passed=not matched,
        detail=(
            f"{len(matched)} pattern(s) matched: "
            + "; ".join(f"{p} → {ctx}" for p, ctx in matched[:5])
            if matched else f"none of {len(patterns)} deny-list patterns matched"
        ),
    )


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
            elif kind == "drawer_destinations_healthy":
                results.append(_assert_drawer_destinations_healthy(page, value if isinstance(value, dict) else None))
            elif kind == "drawer_no_dead_links":
                results.append(_assert_drawer_no_dead_links(page, value if isinstance(value, dict) else None))
            elif kind == "no_text_matching":
                results.append(_assert_no_text_matching(page, value))
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
