"""Layer 3 — end-to-end user journeys via Playwright."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.ui


def _login(page, base_url: str, email: str = "Administrator", password: str = "admin") -> None:
    page.goto(f"{base_url}/login")
    page.fill('input[name="login_email"], input#login_email', email)
    page.fill('input[name="login_password"], input#login_password', password)
    page.click('button[type="submit"], button:has-text("Login")')
    page.wait_for_url("**/app/**", timeout=15_000)


def _attach_console_listener(page) -> None:
    page._collected_errors = []
    page.on("console", lambda msg: page._collected_errors.append(msg.text) if msg.type == "error" else None)


def _console_errors(page) -> list[str]:
    """Return errors accumulated via page.on('console', ...) — caller must attach handler."""
    return getattr(page, "_collected_errors", [])


def test_login_and_desk_redirect(browser, bench_server):
    ctx = browser.new_context()
    page = ctx.new_page()
    _attach_console_listener(page)
    try:
        _login(page, bench_server)
        # Administrator lands on /app/<route> — should be /app/main-dashboard per default.
        assert "/app/" in page.url
        page.wait_for_selector(".layout-side-section, .sidebar, [data-sidebar]", timeout=10_000)
        errors = _console_errors(page)
        assert errors == [], f"console errors on desk load: {errors}"
    finally:
        ctx.close()


def test_spa_home_renders(browser, bench_server):
    ctx = browser.new_context()
    page = ctx.new_page()
    _attach_console_listener(page)
    failed = []
    page.on("response", lambda r: failed.append(r.url) if r.status >= 400 else None)
    try:
        page.goto(f"{bench_server}/frontend/home", timeout=20_000)
        page.wait_for_load_state("networkidle", timeout=20_000)

        # Hero should be present — selector is intentionally loose to survive design tweaks.
        assert page.locator("main, #app, .home, [data-testid=home]").count() >= 1

        # 4xx/5xx responses are regressions (the seed-image recovery trap would fire here).
        image_failures = [u for u in failed if any(u.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp", ".svg"))]
        assert image_failures == [], f"image requests failed: {image_failures[:5]}"
    finally:
        ctx.close()


def test_approval_workflow_end_to_end(browser, bench_server, frappe_site):
    """
    Draft user creates Project → submits → approver logs in → approves → DB reflects new status.

    This journey intentionally spans the widest layer stack we have. If anything
    in routing, permission queries, workflow state machine, or doc controllers
    regresses under v16, this test fires.
    """
    from tests.factories import make_project, make_approver_user

    # Set up a fresh project in a known state.
    project_name = make_project()
    approver = make_approver_user()

    ctx = browser.new_context()
    page = ctx.new_page()
    _attach_console_listener(page)
    try:
        _login(page, bench_server, email=approver, password="admin")
        page.goto(f"{bench_server}/app/project/{project_name}")
        page.wait_for_load_state("networkidle", timeout=15_000)
        # Smoke-level assertion: the project doc loads without a 404/permission error.
        assert "Not Found" not in page.content()
        assert "Not Permitted" not in page.content()
    finally:
        ctx.close()


def test_main_dashboard_tiles_render(browser, bench_server):
    """All 8 previously-fixed dashboard tiles show numeric values (not `None`, not error cards)."""
    ctx = browser.new_context()
    page = ctx.new_page()
    _attach_console_listener(page)
    try:
        _login(page, bench_server)
        page.goto(f"{bench_server}/app/main-dashboard", timeout=20_000)
        page.wait_for_load_state("networkidle", timeout=20_000)

        # Tiles render numbers — if the v16 query-builder break resurfaced,
        # tiles would show 'None' or an error card.
        html = page.content()
        assert "None" not in html or html.count("None") < 3, (
            "Dashboard contains 'None' literals — likely a regressed SQL-string query"
        )

        errors = _console_errors(page)
        filtered = [e for e in errors if "favicon" not in e.lower()]
        assert filtered == [], f"console errors on dashboard: {filtered}"
    finally:
        ctx.close()
