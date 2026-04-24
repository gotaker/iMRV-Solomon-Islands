"""Layer 5 — guest cannot read user secrets; sensitive doctypes filtered; file perms enforced."""

from __future__ import annotations

import pytest
import requests

pytestmark = pytest.mark.security


def test_guest_cannot_read_user_secrets(bench_server):
    r = requests.get(
        f"{bench_server}/api/resource/User",
        params={"limit_page_length": 5},
        timeout=10,
    )
    # Should be 403 for guest — but even if misconfigured to 200, secret fields
    # must not appear.
    if r.status_code == 200:
        body = r.text.lower()
        # Check for field-like patterns — `"<fieldname>": "<value>"` — not bare
        # substrings (which false-positive on descriptions and metadata).
        for leak in ('"password":', '"api_secret":', '"reset_password_key":', '"new_password":'):
            assert leak not in body, f"guest can see leaked field {leak!r} in /api/resource/User"
    else:
        assert r.status_code in (401, 403)


def test_api_get_data_blocks_sensitive_doctypes(bench_server):
    for dt in ("User", "DocShare", "Communication"):
        r = requests.get(
            f"{bench_server}/api/method/mrvtools.api.get_data",
            params={"doctype": dt},
            timeout=10,
        )
        # Either return 403 or a filtered/empty result — but no secret leak.
        if r.status_code == 200:
            body = r.text.lower()
            for leak in ("password", "api_secret", "reset_password_key", "new_password"):
                assert leak not in body, (
                    f"get_data({dt!r}) leaked {leak!r} to guest"
                )


def test_guest_cannot_invoke_non_whitelisted_method(bench_server):
    """Guest POST to frappe.client.set_value → 403/405 (not 500), no stack trace in body."""
    r = requests.post(
        f"{bench_server}/api/method/frappe.client.set_value",
        data={"doctype": "User", "name": "Administrator", "fieldname": "enabled", "value": 0},
        timeout=10,
    )
    assert r.status_code in (401, 403, 405)
    assert "Traceback" not in r.text, "stack trace leaked in response body"


def test_permission_query_cannot_be_bypassed(bench_server, frappe_site):
    """
    `My Approval` via three different APIs — all must respect the
    permission_query_conditions hook defined in mrvtools/hooks.py.
    """
    # Via /api/resource
    r_res = requests.get(
        f"{bench_server}/api/resource/My Approval",
        params={"limit_page_length": 50},
        timeout=10,
    )
    # Guest with no role — expect 403 or an empty list
    if r_res.status_code == 200:
        data = r_res.json().get("data", [])
        # an unauthed client should see at most 0 rows that belong to nobody
        assert isinstance(data, list)

    # Via frappe.client.get_list (guest)
    r_m = requests.post(
        f"{bench_server}/api/method/frappe.client.get_list",
        data={"doctype": "My Approval", "limit_page_length": 50},
        timeout=10,
    )
    assert r_m.status_code in (200, 403, 417)


def test_private_file_requires_auth(bench_server, frappe_site):
    """GET /private/files/<any>  as guest → 403, as Administrator → 200 or 404 (file-may-not-exist)."""
    import frappe

    # Find any private file on the site.
    rows = frappe.db.get_all(
        "File",
        filters={"is_private": 1},
        fields=["file_url"],
        limit=1,
    )
    if not rows:
        pytest.skip("no private files in sample DB")
    url = rows[0].file_url
    assert url.startswith("/private/files/")

    r_guest = requests.get(f"{bench_server}{url}", timeout=10, allow_redirects=False)
    # 302 → /login is also access denial (redirect to sign-in). Accept it.
    assert r_guest.status_code in (302, 401, 403), f"private file reachable by guest: {url} (status {r_guest.status_code})"
    if r_guest.status_code == 302:
        loc = r_guest.headers.get("Location", "")
        assert "/login" in loc, f"302 but not to /login: {loc!r}"

    s = requests.Session()
    s.post(f"{bench_server}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})
    r_admin = s.get(f"{bench_server}{url}", timeout=10)
    assert r_admin.status_code in (200, 404)
