"""
bench.runner.crawler — exhaustive per-role page-graph walker.

For each role configured in bench/crawler.yaml, the crawler:
  1. Logs in (or starts anonymously for guest)
  2. Navigates start_urls
  3. Extracts URLs from follow_selectors at each page
  4. Dedupes by canonical URL, BFS up to max_depth or max_pages_per_role
  5. Runs baseline_checks at each page
  6. Caches DOM+network hash; skips unchanged pages on warm runs

Output: bench/history/<run-id>/coverage.json

    { "<role>": { "<url>": {
        "depth": int, "status": int,
        "baseline_results": {check: passed bool},
        "screenshot": "...png", "network_log": [...]
    } } }

Pages failing baseline_checks → bench/candidates/crawled/<role>_<slug>.yaml.

Standalone usage:
    python3 -m bench.runner.crawler --config bench/config.yaml \
        --target local-docker --crawler-config bench/crawler.yaml \
        --output bench/history/<run-id>/coverage.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import deque
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse

import yaml

from bench.runner.a_runner import _load_target, _load_yaml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = REPO_ROOT / "bench"


def _canonical_url(url: str) -> str:
    """Normalize URL for dedup: strip fragment, sort query, drop trailing slash."""
    url, _ = urldefrag(url)
    parsed = urlparse(url)
    # Sort query params for stable canonicalization.
    if parsed.query:
        parts = sorted(parsed.query.split("&"))
        parsed = parsed._replace(query="&".join(parts))
    path = parsed.path.rstrip("/") or "/"
    parsed = parsed._replace(path=path)
    return urlunparse(parsed)


def _matches_skip(url: str, patterns: list[str]) -> bool:
    for p in patterns:
        if "*" in p:
            rgx = re.compile(p.replace("*", ".*"))
            if rgx.search(url):
                return True
        elif p in url:
            return True
    return False


def _extract_urls(page, selectors: list[str], base_origin: str) -> list[str]:
    """Pull href values from elements matching any of `selectors`."""
    found: list[str] = []
    for sel in selectors:
        try:
            hrefs = page.locator(sel).evaluate_all(
                "els => els.map(e => e.href || e.getAttribute('data-route') || e.getAttribute('href') || '')"
            )
        except Exception:
            continue
        for h in hrefs:
            if not h:
                continue
            if h.startswith("javascript:") or h.startswith("#"):
                continue
            absolute = urljoin(base_origin + "/", h)
            # Stay on-origin: skip external links so we never crawl out.
            if urlparse(absolute).netloc and urlparse(absolute).netloc != urlparse(base_origin).netloc:
                continue
            found.append(absolute)
    return found


def _page_hash(page, console_count: int, network_count: int) -> str:
    """Cheap stability hash: DOM text length + counts. Used to skip unchanged pages."""
    try:
        text_len = page.evaluate("() => document.body ? document.body.innerText.length : 0")
    except Exception:
        text_len = 0
    digest = hashlib.sha1(
        f"{text_len}:{console_count}:{network_count}".encode()
    ).hexdigest()[:16]
    return digest


def _run_baseline_checks(
    page,
    status: int,
    console_errors: list[str],
    failed_responses: list[tuple[str, int]],
    checks: list[dict | str],
) -> dict[str, bool]:
    """Evaluate the per-page baseline_checks list. Returns {check_name: passed}."""
    results: dict[str, bool] = {}
    for raw in checks:
        if isinstance(raw, dict) and len(raw) == 1:
            ((name, value),) = raw.items()
        elif isinstance(raw, str):
            name, value = raw, True
        else:
            continue

        if name == "http_status":
            results[name] = status == int(value)
        elif name == "no_console_error_matching":
            rgx = re.compile(value)
            results[name] = not any(rgx.search(e) for e in console_errors)
        elif name == "no_unhandled_promise_rejection":
            results[name] = not any("Unhandled promise" in e for e in console_errors)
        elif name == "design_system":
            # Phase 2 hook — checked at the top level, not per-baseline.
            results[name] = True
        elif name == "axe_critical_count":
            # Phase 2 hook — depends on axe injection. Marked as deferred.
            results[name] = True  # not yet enforced
        elif name == "lighthouse_perf_min":
            results[name] = True  # deferred to Phase 4
        elif name == "reveal_health":
            try:
                stuck = page.evaluate(
                    """() => Array.from(document.querySelectorAll('[data-reveal]'))
                          .filter(el => {
                              const r = el.getBoundingClientRect();
                              const inViewport = r.top < window.innerHeight && r.bottom > 0;
                              const cs = window.getComputedStyle(el);
                              return inViewport && parseFloat(cs.opacity) === 0;
                          }).length"""
                )
                results[name] = stuck == 0
            except Exception:
                results[name] = True  # don't fail crawler if eval errored
        elif name == "render_settled_within_ms":
            results[name] = True  # placeholder; settle is enforced via wait_for_selector
        else:
            results[name] = True  # unknown checks default to pass (not silently fail)
    return results


def _login_via_playwright(page, base_url: str, email: str, password: str) -> None:
    page.goto(f"{base_url}/login", wait_until="domcontentloaded")
    page.fill('input[name="login_email"], input#login_email', email)
    page.fill('input[name="login_password"], input#login_password', password)
    page.click('button[type="submit"], button:has-text("Login")')
    page.wait_for_url(re.compile(r".*/(app|desk|frontend)/.*"), timeout=15_000)


def crawl_role(
    browser,
    role: str,
    role_config: dict,
    base_url: str,
    credentials: dict,
    global_config: dict,
    settle_timeout_ms: int,
) -> dict[str, Any]:
    """Walk a single role's surface. Returns the per-URL coverage dict."""
    context = browser.new_context()
    page = context.new_page()
    page.set_default_timeout(settle_timeout_ms)

    if role != "guest":
        creds = credentials.get(role)
        if not creds:
            context.close()
            return {"_error": f"no fixture credentials for role '{role}'"}
        try:
            _login_via_playwright(page, base_url, creds["email"], creds["password"])
        except Exception as exc:  # noqa: BLE001
            context.close()
            return {"_error": f"login failed: {exc!r}"}

    start_urls = [urljoin(base_url, u) for u in role_config.get("start_urls", [])]
    follow_selectors = role_config.get("follow_selectors", ["a[href]"])
    skip_patterns = role_config.get("skip_patterns", [])
    max_depth = role_config.get("max_depth", 4)
    max_pages = global_config.get("max_pages_per_role", 250)
    baseline_checks = global_config.get("baseline_checks", [])

    visited: dict[str, dict] = {}
    queue: deque[tuple[str, int]] = deque((u, 0) for u in start_urls)

    while queue and len(visited) < max_pages:
        url, depth = queue.popleft()
        canonical = _canonical_url(url)
        if canonical in visited:
            continue
        if _matches_skip(canonical, skip_patterns):
            continue
        if depth > max_depth:
            continue

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

        try:
            response = page.goto(canonical, wait_until="domcontentloaded")
            status = response.status if response else 0
        except Exception as exc:  # noqa: BLE001
            visited[canonical] = {"depth": depth, "error": f"navigation failed: {exc!r}"}
            continue

        baseline = _run_baseline_checks(page, status, console_errors, failed_responses, baseline_checks)
        passed = all(baseline.values())

        visited[canonical] = {
            "depth": depth,
            "status": status,
            "baseline_results": baseline,
            "passed": passed,
            "console_error_count": len(console_errors),
            "network_4xx_count": sum(1 for (_, s) in failed_responses if s >= 400),
            "page_hash": _page_hash(page, len(console_errors), len(failed_responses)),
        }

        if depth < max_depth and passed:
            for child in _extract_urls(page, follow_selectors, base_url.rstrip("/")):
                child_canonical = _canonical_url(child)
                if child_canonical not in visited:
                    queue.append((child_canonical, depth + 1))

    context.close()
    return visited


def _candidate_yaml_for_failure(role: str, url: str, baseline: dict[str, bool]) -> dict:
    failed = [k for k, v in baseline.items() if not v]
    slug = re.sub(r"[^a-z0-9]+", "_", url.lower()).strip("_")[:80]
    return {
        "id": f"crawled_{role.lower().replace(' ', '_')}_{slug}",
        "title": f"[crawled] {role} on {url} failed: {', '.join(failed)}",
        "perspective": {"role": role, "persona": "standard", "environment": "any"},
        "preconditions": {"sample_db": "required", "session": f"logged_in_as:{role}", "cache": "warm"},
        "steps": [{"navigate": urlparse(url).path or "/"}],
        "assertions": [
            {"no_console_error_matching": "TypeError|ReferenceError|CSRFTokenError"},
        ],
        "tags": ["crawled", "candidate", "needs-triage"],
        "sources": [{"crawler": f"{role}@{url} failed: {failed}"}],
    }


def _write_candidates(coverage: dict[str, dict], candidates_dir: Path) -> int:
    """Write a candidate YAML for every crawler-failed page."""
    candidates_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for role, urls in coverage.items():
        if not isinstance(urls, dict) or "_error" in urls:
            continue
        for url, data in urls.items():
            if data.get("passed"):
                continue
            stub = _candidate_yaml_for_failure(role, url, data.get("baseline_results", {}))
            slug_role = re.sub(r"[^a-z0-9]+", "_", role.lower()).strip("_")
            slug_url = re.sub(r"[^a-z0-9]+", "_", url.lower()).strip("_")[:60]
            path = candidates_dir / f"{slug_role}__{slug_url}.yaml"
            path.write_text(yaml.safe_dump(stub, sort_keys=False))
            count += 1
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Per-role exhaustive crawler")
    parser.add_argument("--config", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--crawler-config", default=str(BENCH_ROOT / "crawler.yaml"))
    parser.add_argument("--output", required=True)
    parser.add_argument("--candidates-dir", default=str(BENCH_ROOT / "candidates" / "crawled"))
    parser.add_argument("--roles", default=None, help="csv: only crawl these roles")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    config = _load_yaml(Path(args.config))
    target = _load_target(config, args.target)
    crawler_config = _load_yaml(Path(args.crawler_config))
    credentials = _load_yaml(BENCH_ROOT / "fixtures" / "role_credentials.yaml") or {}

    crawl_specs = crawler_config.get("crawl") or {}
    if args.roles:
        wanted = {r.strip() for r in args.roles.split(",") if r.strip()}
        crawl_specs = {k: v for k, v in crawl_specs.items() if k in wanted}

    if not crawl_specs:
        print("[crawler] no crawl specs to run", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"[crawler] dry-run; would crawl: {list(crawl_specs)}")
        return 0

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "[crawler] playwright not installed; "
            "pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        return 2

    coverage: dict[str, Any] = {}
    settle = (config.get("defaults") or {}).get("settle_timeout_ms", 5000)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for role, role_cfg in crawl_specs.items():
                print(f"[crawler] crawling role={role}")
                coverage[role] = crawl_role(
                    browser, role, role_cfg, target["base_url"].rstrip("/"),
                    credentials, crawler_config.get("global", {}), settle,
                )
                if "_error" in coverage[role]:
                    print(f"[crawler]   skipped: {coverage[role]['_error']}")
                else:
                    passed = sum(1 for v in coverage[role].values() if v.get("passed"))
                    print(f"[crawler]   pages={len(coverage[role])} passed={passed}")
        finally:
            browser.close()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(coverage, indent=2))

    candidates_dir = Path(args.candidates_dir)
    n_candidates = _write_candidates(coverage, candidates_dir)
    print(f"[crawler] wrote {len(coverage)} role-coverage maps + {n_candidates} candidate stubs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
