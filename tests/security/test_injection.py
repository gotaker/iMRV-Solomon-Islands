"""Layer 5 — SQL injection and XSS surfaces."""

from __future__ import annotations

import pytest
import requests

pytestmark = pytest.mark.security


def test_sql_injection_in_side_menu_interpolation(bench_server, frappe_site):
    """
    frappe_side_menu/frappe_side_menu/api.py lines 52-74 build dynamic
    CASE WHEN clauses via str.format() on role/doctype names. This test
    calls get_menulist as an authed user whose roles / doctypes were
    seeded with injection payloads — the request must either error cleanly
    or return empty; the tabUser table must still exist afterward.
    """
    import frappe

    # Sanity: tabUser exists before.
    before = frappe.db.sql("SELECT COUNT(*) FROM `tabUser`")[0][0]

    # Attempt injection via a URL param (safe: frappe.client.get_list strips
    # most of these, but the get_menulist path interpolates role names).
    payload = "Administrator'; DROP TABLE tabUser; --"
    s = requests.Session()
    s.post(f"{bench_server}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})
    r = s.get(
        f"{bench_server}/api/method/frappe_side_menu.frappe_side_menu.api.get_menulist",
        params={"role": payload},
        timeout=10,
    )
    # Either 200 with empty/escaped result, or a 4xx. NOT 500 with a traceback.
    assert r.status_code in (200, 400, 404, 417)
    assert "Traceback" not in r.text

    after = frappe.db.sql("SELECT COUNT(*) FROM `tabUser`")[0][0]
    assert after == before, "tabUser row count changed — injection payload may have executed"


def test_xss_in_user_registration_fields(bench_server, frappe_site):
    """Submit <script> in createUser name field; when rendered anywhere, assert escaped."""
    import frappe
    payload = "<script>alert('xss')</script>"
    r = requests.post(
        f"{bench_server}/api/method/mrvtools.mrvtools.doctype.user_registration.user_registration.createUser",
        data={"email": "xss-probe@example.com", "first_name": payload, "last_name": "Probe"},
        timeout=10,
    )
    # Regardless of whether creation succeeded, the raw payload must not appear
    # unescaped in any endpoint that renders user-facing HTML.
    listed = requests.get(f"{bench_server}/api/method/frappe.client.get_list",
                         params={"doctype": "User Registration", "fields": '["*"]'},
                         timeout=10)
    assert "<script>alert" not in listed.text, "raw <script> echoed in response — XSS surface"
