"""
Record-factory helpers for the few tests that need a specific starter state
(e.g. a draft Project for the approval-workflow journey).

Keep this file small — most tests should read existing sample-DB rows rather
than create new ones.
"""

from __future__ import annotations

import uuid

import frappe


def make_project(**overrides) -> str:
    """Insert a minimal Project. Status defaults to the doctype's configured default; pass `status=...` to override. Returns its name."""
    doc = frappe.get_doc({
        "doctype": "Project",
        "project_name": overrides.pop("project_name", f"Test Project {uuid.uuid4().hex[:8]}"),
        **overrides,
    })
    doc.insert(ignore_permissions=True)
    return doc.name


def make_approver_user(email: str | None = None) -> str:
    """Create a User with the Approver role. Returns email."""
    email = email or f"approver-{uuid.uuid4().hex[:8]}@example.com"
    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": "Test",
        "last_name": "Approver",
        "send_welcome_email": 0,
        "roles": [{"role": "Approver"}] if frappe.db.exists("Role", "Approver") else [],
    })
    user.insert(ignore_permissions=True)
    return email


def make_requester_user(email: str | None = None) -> str:
    """Create a plain User with no elevated roles."""
    email = email or f"requester-{uuid.uuid4().hex[:8]}@example.com"
    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": "Test",
        "last_name": "Requester",
        "send_welcome_email": 0,
    })
    user.insert(ignore_permissions=True)
    return email


def set_session_user(email: str) -> None:
    """Switch frappe.session.user for the duration of a test."""
    frappe.set_user(email)


def login_via_http(base_url: str, email: str, password: str = "admin") -> dict:
    """
    Authenticate via HTTP and return a dict with `cookies` and `csrf_token`
    suitable for subsequent requests.
    """
    import requests
    session = requests.Session()
    r = session.post(
        f"{base_url}/api/method/login",
        data={"usr": email, "pwd": password},
        timeout=10,
    )
    r.raise_for_status()
    csrf = session.cookies.get("csrf_token") or ""
    return {"session": session, "csrf_token": csrf}
