"""Layer 1 — v14→v16 schema transitions completed: no legacy Desktop Icon table, Workspace has v16 columns."""

import pytest

pytestmark = pytest.mark.data


def test_no_legacy_desktop_icon_table(frappe_site):
    import frappe
    rows = frappe.db.sql("SHOW TABLES LIKE 'tabDesktop Icon'")
    assert not rows, "Legacy `tabDesktop Icon` table still present after v16 migrate"


def test_workspace_records_v16_shape(frappe_site):
    import frappe
    cols = {row[0] for row in frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace`")}
    required = {"public", "is_hidden", "for_user"}
    missing = required - cols
    assert not missing, f"Workspace table missing v16 columns: {missing}"
