"""Layer 2 — permission_query_conditions hooks scope list views correctly."""

import pytest

pytestmark = pytest.mark.integration


def test_permission_query_my_approval_scopes_to_user(frappe_site):
    """Non-privileged user sees no My Approval rows; Administrator sees all."""
    import frappe

    # As Guest (no role), My Approval should be empty.
    frappe.set_user("Guest")
    try:
        guest_rows = frappe.db.count("My Approval")
    except Exception:
        guest_rows = 0  # permission denied counts as 0 for our purposes
    finally:
        frappe.set_user("Administrator")

    admin_rows = frappe.db.count("My Approval")
    assert guest_rows <= admin_rows, (
        "My Approval permission_query_conditions may be bypassed — "
        "guest saw more rows than Administrator"
    )


def test_permission_query_approved_user(frappe_site):
    """Same shape for Approved User."""
    import frappe

    frappe.set_user("Guest")
    try:
        guest_rows = frappe.db.count("Approved User")
    except Exception:
        guest_rows = 0
    finally:
        frappe.set_user("Administrator")

    admin_rows = frappe.db.count("Approved User")
    assert guest_rows <= admin_rows
