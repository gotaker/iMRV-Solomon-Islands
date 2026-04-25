"""Layer 5 — SQL injection and XSS surfaces."""

from __future__ import annotations

import pytest
import requests

pytestmark = pytest.mark.security


def test_sql_injection_in_side_menu_interpolation(bench_server, frappe_site):
    """
    frappe_side_menu/api.py lines 52-74 build dynamic CASE WHEN clauses via
    str.format() on ROLE NAMES returned by frappe.get_roles(user).

    Attack vector: create a role whose name contains SQL metacharacters,
    assign it to a user, log in as that user, call get_menulist. If the
    .format() interpolation is vulnerable, the SQL executes.

    We verify (a) the request doesn't 500 with a traceback, and (b) the
    tabUser table is intact afterward — both are necessary safety invariants.
    """
    import uuid

    import frappe

    # Sanity snapshot before.
    before = frappe.db.sql("SELECT COUNT(*) FROM `tabUser`")[0][0]

    # Seed an attacker-named role and user. Use a benign-looking metacharacter
    # combination that would break an unparameterized .format() if one existed.
    # The single-quote and semicolon are the load-bearing characters.
    role_name = f"rogue'; SELECT 1; -- {uuid.uuid4().hex[:6]}"
    user_email = f"rogue-{uuid.uuid4().hex[:8]}@example.com"

    try:
        frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(ignore_permissions=True)
    except Exception:
        pytest.skip("Frappe rejected the rogue role name — interpolation surface not reachable via role names on this version")

    user_doc = frappe.get_doc({
        "doctype": "User",
        "email": user_email,
        "first_name": "Rogue",
        "send_welcome_email": 0,
        "new_password": "roguepass123",
        "roles": [{"role": role_name}],
    })
    user_doc.insert(ignore_permissions=True)

    # Log in as the rogue user via HTTP, then invoke get_menulist.
    s = requests.Session()
    login = s.post(
        f"{bench_server}/api/method/login",
        data={"usr": user_email, "pwd": "roguepass123"},
        timeout=10,
    )
    assert login.status_code == 200, f"rogue-user login failed: {login.status_code}"

    r = s.get(
        f"{bench_server}/api/method/frappe_side_menu.frappe_side_menu.api.get_menulist",
        timeout=15,
    )
    # Not 500; no traceback leak.
    assert r.status_code != 500, f"500 on menulist with rogue role — possible injection: {r.text[:300]}"
    assert "Traceback" not in r.text, "stack trace leaked in response body"

    # The critical invariant: tabUser is intact.
    after = frappe.db.sql("SELECT COUNT(*) FROM `tabUser`")[0][0]
    assert after == before, (
        "tabUser row count changed — rogue role interpolation may have executed SQL. "
        f"before={before} after={after}"
    )


def test_xss_in_user_registration_fields(bench_server, frappe_site):
    """Submit <script> in createUser first_name; verify escaped in HTML-rendered list view."""
    import uuid

    payload = "<script>alert('xss-probe')</script>"
    probe_email = f"xss-{uuid.uuid4().hex[:8]}@example.com"

    # Submit via the guest-callable createUser (factory would require auth).
    requests.post(
        f"{bench_server}/api/method/mrvtools.mrvtools.doctype.user_registration.user_registration.createUser",
        data={"email": probe_email, "first_name": payload, "last_name": "Probe"},
        timeout=10,
    )

    # Log in as Administrator and fetch the HTML list view (not JSON).
    s = requests.Session()
    s.post(f"{bench_server}/api/method/login", data={"usr": "Administrator", "pwd": "admin"}, timeout=10)
    r = s.get(f"{bench_server}/app/user-registration", timeout=15)

    # If desk returns HTML, raw unescaped <script> would be a real XSS.
    # If the endpoint 404s or returns JSON (Frappe changed paths), skip rather than pass blindly.
    ct = r.headers.get("Content-Type", "")
    if "html" not in ct.lower():
        pytest.skip(f"/app/user-registration did not return HTML (Content-Type={ct!r}) — surface moved or unauth'd")

    # Must not contain the literal payload in executable form.
    assert "<script>alert('xss-probe')" not in r.text, (
        "raw <script> survived rendering — XSS surface in user-registration list view"
    )
