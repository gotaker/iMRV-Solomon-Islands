"""Layer 1 — key Single doctypes exist and have non-null core fields."""

import pytest

pytestmark = pytest.mark.data


def test_singles_synced(frappe_site):
    import frappe
    singles = ["Website Settings", "Navbar Settings", "Side Menu Settings", "MrvFrontend"]
    for single in singles:
        if not frappe.db.exists("DocType", single):
            pytest.fail(f"Single DocType {single!r} missing — schema regression")
        doc = frappe.get_single(single)
        assert doc is not None, f"{single!r} could not be loaded"
