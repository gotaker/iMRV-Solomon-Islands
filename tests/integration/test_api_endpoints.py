"""Layer 2 — HTTP contracts for every whitelisted endpoint."""

import pytest
import requests

pytestmark = pytest.mark.integration


def _admin_session(bench_server: str) -> requests.Session:
    s = requests.Session()
    r = s.post(
        f"{bench_server}/api/method/login",
        data={"usr": "Administrator", "pwd": "admin"},
        timeout=10,
    )
    r.raise_for_status()
    return s


# --- mrvtools/api.py ---------------------------------------------------------

def test_api_get_approvers(bench_server):
    s = _admin_session(bench_server)
    r = s.get(f"{bench_server}/api/method/mrvtools.api.get_approvers", timeout=10)
    assert r.status_code == 200
    assert "message" in r.json()


def test_api_route_user(bench_server):
    s = _admin_session(bench_server)
    r = s.get(f"{bench_server}/api/method/mrvtools.api.route_user", timeout=10)
    assert r.status_code == 200


def test_api_get_data_guest_readable(bench_server):
    """get_data is allow_guest=True — verify it still responds under v16."""
    r = requests.get(
        f"{bench_server}/api/method/mrvtools.api.get_data",
        params={"doctype": "Project Key Sector"},
        timeout=10,
    )
    assert r.status_code == 200
    assert "message" in r.json()


# --- mrvtools/mrvtools/doctype/mrvfrontend/mrvfrontend.py -------------------

def test_mrvfrontend_get_all_guest(bench_server):
    r = requests.get(
        f"{bench_server}/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all",
        timeout=10,
    )
    assert r.status_code == 200
    payload = r.json().get("message", {})
    for key in ("knowledge_resource_details", "knowledge_resource_details2",
                "climate_change_division_images", "add_new_content"):
        assert key in payload, f"{key!r} missing from SPA home payload"


# --- mrvtools/mrvtools/doctype/my_approval/my_approval.py -------------------

def test_my_approval_insert_record_guest(bench_server):
    """Contract pin — records current guest-callable behavior.

    The static sweep flagged this as BREAKING; hardening is a separate PR.
    When the endpoint is locked down, flip this test from 200 to 403.
    """
    r = requests.post(
        f"{bench_server}/api/method/mrvtools.mrvtools.doctype.my_approval.my_approval.insert_record",
        data={"doctype": "Project", "docname": "NONEXISTENT"},
        timeout=10,
    )
    # Current behavior: returns 200 (even on invalid input) because allow_guest=True
    assert r.status_code in (200, 417), f"unexpected status {r.status_code}"


def test_my_approval_delete_record_guest(bench_server):
    """Contract pin — same shape."""
    r = requests.post(
        f"{bench_server}/api/method/mrvtools.mrvtools.doctype.my_approval.my_approval.delete_record",
        data={"doctype": "Project", "docname": "NONEXISTENT"},
        timeout=10,
    )
    assert r.status_code in (200, 417)


# --- mrvtools/mrvtools/doctype/user_registration/user_registration.py ------

def test_user_registration_createUser_guest(bench_server):
    """Contract pin — allow_guest=True mutation endpoint."""
    r = requests.post(
        f"{bench_server}/api/method/mrvtools.mrvtools.doctype.user_registration.user_registration.createUser",
        data={"email": "smoke@example.com", "first_name": "Smoke", "last_name": "Test"},
        timeout=10,
    )
    assert r.status_code in (200, 417)


def test_user_registration_insert_approved_users_guest(bench_server):
    """Contract pin."""
    r = requests.post(
        f"{bench_server}/api/method/mrvtools.mrvtools.doctype.user_registration.user_registration.insert_approved_users",
        data={"email": "smoke@example.com"},
        timeout=10,
    )
    assert r.status_code in (200, 417)


def test_user_registration_createApprovedUser_guest(bench_server):
    """Contract pin."""
    r = requests.post(
        f"{bench_server}/api/method/mrvtools.mrvtools.doctype.user_registration.user_registration.createApprovedUser",
        data={"email": "smoke@example.com"},
        timeout=10,
    )
    assert r.status_code in (200, 417)


# --- frappe_side_menu/frappe_side_menu/api.py ------------------------------

def test_side_menu_get_menulist_authed(bench_server):
    s = _admin_session(bench_server)
    r = s.get(f"{bench_server}/api/method/frappe_side_menu.frappe_side_menu.api.get_menulist", timeout=10)
    assert r.status_code == 200
    payload = r.json().get("message", {})
    assert isinstance(payload, (dict, list))


def test_side_menu_guest_helpers(bench_server):
    """get_all_records / get_list / get_doctype are allow_guest=True."""
    for method in ("get_all_records", "get_list", "get_doctype"):
        r = requests.get(
            f"{bench_server}/api/method/frappe_side_menu.frappe_side_menu.api.{method}",
            params={"doctype": "Project Key Sector"},
            timeout=10,
        )
        assert r.status_code in (200, 417), f"{method} returned {r.status_code}"


# --- Login redirect (hits set_default_route) -------------------------------

def test_login_redirect_on_session_creation(bench_server):
    """Administrator login → GET /app/ → 302 to configured route."""
    s = requests.Session()
    r = s.post(
        f"{bench_server}/api/method/login",
        data={"usr": "Administrator", "pwd": "admin"},
        timeout=10,
        allow_redirects=False,
    )
    assert r.status_code == 200

    r2 = s.get(f"{bench_server}/app", timeout=10, allow_redirects=False)
    # Accept either a direct 200 (already on landing) or a 302 into /app/<route>
    assert r2.status_code in (200, 302, 303), f"unexpected /app status: {r2.status_code}"
    if r2.status_code in (302, 303):
        loc = r2.headers.get("Location", "")
        assert loc.startswith("/app/"), f"unexpected redirect target: {loc!r}"
