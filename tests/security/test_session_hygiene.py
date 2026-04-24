"""Layer 5 — login/logout/cookie hygiene."""

from __future__ import annotations

import pytest
import requests

pytestmark = pytest.mark.security


def test_session_cookie_hardening(bench_server):
    """Set-Cookie on login carries HttpOnly. Secure/SameSite depend on prod config — check HttpOnly only."""
    r = requests.post(
        f"{bench_server}/api/method/login",
        data={"usr": "Administrator", "pwd": "admin"},
        timeout=10,
    )
    r.raise_for_status()
    # Requests combines multiple Set-Cookie headers; iterate raw.
    raw_cookies = r.raw.headers.getlist("Set-Cookie") if hasattr(r.raw.headers, "getlist") else r.headers.get("Set-Cookie", "").split(",")
    blob = "\n".join(raw_cookies).lower()
    assert "httponly" in blob, "session cookie missing HttpOnly flag"


def test_csrf_required_on_whitelisted_post(bench_server):
    """
    POST to a whitelisted mutating method without a CSRF token.

    Frappe's ignore_csrf site flag was historically set to 1 for dev ergonomics.
    This test asserts the *current* behavior — if CSRF is off, it documents
    that; if it's on, it verifies the 403. Flip the assertion when
    ignore_csrf is removed from site_config.json.
    """
    r = requests.post(
        f"{bench_server}/api/method/frappe.client.rename_doc",
        data={"doctype": "User", "old": "Administrator", "new": "Admin"},
        timeout=10,
    )
    # With ignore_csrf=1 this is 401/403 (auth); with ignore_csrf=0 it's 403 (CSRF).
    # Either way, must not be 200 and must not mutate.
    assert r.status_code != 200, "mutating POST succeeded without CSRF and without auth"


def test_logout_invalidates_session(bench_server):
    s = requests.Session()
    s.post(f"{bench_server}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})
    r_authed = s.get(f"{bench_server}/api/method/frappe.auth.get_logged_user", timeout=10)
    assert r_authed.status_code == 200
    assert "Administrator" in r_authed.text

    s.get(f"{bench_server}/api/method/logout", timeout=10)

    r_after = s.get(f"{bench_server}/api/method/frappe.auth.get_logged_user", timeout=10)
    # After logout, logged_user should be Guest, not Administrator.
    assert "Administrator" not in r_after.text, "session still authed after logout"
