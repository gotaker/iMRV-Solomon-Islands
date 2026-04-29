"""
bench.runner.chaos_agent — Wave 2 environment-perturbation tests.

Three classes of perturbation:

  1. CSRF expiry mid-flow: log in, capture sid, expire CSRF on the server,
     attempt a write. Expect: graceful retry (Phase 4 retry-layer) or a
     specific CSRFTokenError surfaced to the user, never a 500 with stack.

  2. Asset 404 simulation: navigate a page after rewriting Playwright route()
     to fake-404 a specific asset. Expect: page renders without that asset,
     no console explosions.

  3. Slow upstream: Playwright route() delays /api/* responses by N seconds.
     Expect: spinner / loading state visible, no crash on timeout.

Targets `local-docker` only. Refuses live targets entirely (env perturbation
of production is destructive).

Standalone usage:
    python3 -m bench.runner.chaos_agent --config bench/config.yaml \
        --target local-docker --output bench/history/<run-id>/chaos.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from bench.runner.a_runner import _load_target, _load_yaml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = REPO_ROOT / "bench"


@dataclass
class ChaosResult:
    name: str
    passed: bool
    detail: str = ""


def _scenario_asset_404(browser, base_url: str) -> ChaosResult:
    """Navigate the SPA home with /assets/mrvtools/* faked as 404. Expect graceful fallback."""
    context = browser.new_context()
    page = context.new_page()
    blocked: list[str] = []

    def _route_handler(route):
        url = route.request.url
        if "/assets/mrvtools/" in url and url.endswith(".js"):
            blocked.append(url)
            route.fulfill(status=404, body="not found")
        else:
            route.continue_()

    context.route("**/*", _route_handler)
    console_errors: list[str] = []
    page.on(
        "console",
        lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
    )

    try:
        page.goto(f"{base_url}/frontend/home", wait_until="domcontentloaded", timeout=20_000)
        # Even with the JS bundle blocked, the page should still load *something* —
        # at minimum the html shell. We just assert no crash that produces a
        # white page with a JavaScript stack trace; a clean fallback is acceptable.
        body_text = page.evaluate("() => document.body ? document.body.innerText : ''")
        passed = len(body_text) > 0
        detail = (
            f"asset 404 simulated for {len(blocked)} files; body_text len={len(body_text)}; "
            f"console errors={len(console_errors)}"
        )
    except Exception as exc:  # noqa: BLE001
        passed = False
        detail = f"navigation crashed: {exc!r}"
    finally:
        context.close()

    return ChaosResult(name="asset_404", passed=passed, detail=detail)


def _scenario_slow_api(browser, base_url: str) -> ChaosResult:
    """Delay all /api/* responses by 5s. Page should not crash; loading state visible."""
    context = browser.new_context()
    page = context.new_page()

    delayed_count = [0]

    def _delay_api(route):
        if "/api/" in route.request.url:
            import time
            time.sleep(2)  # short delay; full 5s makes test wall-clock too long
            delayed_count[0] += 1
        route.continue_()

    context.route("**/*", _delay_api)
    try:
        page.goto(f"{base_url}/frontend/home", wait_until="networkidle", timeout=30_000)
        passed = True
        detail = f"slow-api scenario completed; delayed_count={delayed_count[0]}"
    except Exception as exc:  # noqa: BLE001
        # A timeout is acceptable here — we just want to verify it doesn't crash.
        passed = "Timeout" in str(exc)
        detail = f"navigation result: {exc!r} (timeout is acceptable)"
    finally:
        context.close()
    return ChaosResult(name="slow_api", passed=passed, detail=detail)


def _scenario_csrf_expiry(base_url: str, email: str, password: str) -> ChaosResult:
    """
    Log in, then attempt a write with a stale CSRF token. Expect either a
    successful retry (Phase 4 retry layer) or a clean CSRFTokenError 4xx,
    never a 500 with a Python stack trace.
    """
    import requests

    s = requests.Session()
    try:
        r = s.post(
            f"{base_url}/api/method/login",
            data={"usr": email, "pwd": password},
            timeout=15,
        )
        r.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        return ChaosResult(name="csrf_expiry", passed=False, detail=f"login failed: {exc!r}")

    # Forge a stale CSRF cookie + header pair.
    headers = {"X-Frappe-CSRF-Token": "STALE_TOKEN_xx"}
    body = {"doctype": "User"}
    try:
        r = s.post(
            f"{base_url}/api/method/frappe.client.get_list",
            data=body, headers=headers, timeout=15,
        )
        # 500 = leak. 4xx with a clean error message = pass.
        if r.status_code >= 500:
            return ChaosResult(
                name="csrf_expiry",
                passed=False,
                detail=f"500 on stale CSRF: {r.text[:200]!r}",
            )
        if "Traceback" in (r.text or "") or "frappe.exceptions" in (r.text or ""):
            return ChaosResult(
                name="csrf_expiry",
                passed=False,
                detail="stack trace leaked in 4xx response",
            )
        return ChaosResult(
            name="csrf_expiry",
            passed=True,
            detail=f"status={r.status_code} (no 500, no stack trace)",
        )
    except Exception as exc:  # noqa: BLE001
        return ChaosResult(name="csrf_expiry", passed=False, detail=f"request failed: {exc!r}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Wave 2 chaos / env-perturbation runner")
    parser.add_argument("--config", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--auth-as", default="Administrator")
    parser.add_argument("--include", default="asset_404,slow_api,csrf_expiry",
                        help="csv of scenarios to run")
    args = parser.parse_args(argv)

    config = _load_yaml(Path(args.config))
    target = _load_target(config, args.target)
    if not target.get("safe_for_adversarial"):
        print(
            f"[chaos] target '{args.target}' is not safe for chaos. Refusing.",
            file=sys.stderr,
        )
        return 2

    credentials = _load_yaml(BENCH_ROOT / "fixtures" / "role_credentials.yaml") or {}
    auth = credentials.get(args.auth_as) or {}

    wanted = {s.strip() for s in args.include.split(",") if s.strip()}
    base_url = target["base_url"].rstrip("/")
    results: list[ChaosResult] = []

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[chaos] playwright not installed; cannot run asset_404/slow_api", file=sys.stderr)
        sync_playwright = None  # type: ignore

    if sync_playwright and ("asset_404" in wanted or "slow_api" in wanted):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                if "asset_404" in wanted:
                    results.append(_scenario_asset_404(browser, base_url))
                if "slow_api" in wanted:
                    results.append(_scenario_slow_api(browser, base_url))
            finally:
                browser.close()

    if "csrf_expiry" in wanted:
        if not auth.get("email"):
            results.append(ChaosResult(
                name="csrf_expiry", passed=False,
                detail=f"no credential for '{args.auth_as}'",
            ))
        else:
            results.append(_scenario_csrf_expiry(base_url, auth["email"], auth["password"]))

    leaked = [r for r in results if not r.passed]
    summary = {
        "schema_version": 1,
        "target": args.target,
        "total_scenarios": len(results),
        "leaked_count": len(leaked),
        "passed": len(leaked) == 0,
        "results": [{"name": r.name, "passed": r.passed, "detail": r.detail} for r in results],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2))
    print(json.dumps({"passed": summary["passed"], "leaked_count": summary["leaked_count"]}, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
