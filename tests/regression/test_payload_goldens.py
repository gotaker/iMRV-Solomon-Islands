"""Layer 4 — structural snapshots for two critical shared payloads."""

from __future__ import annotations

import pytest
import requests

from tests.regression._golden import assert_golden

pytestmark = pytest.mark.regression


def _shape(value):
    if isinstance(value, dict):
        return {k: _shape(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        if not value:
            return []
        return [_shape(value[0]), f"<{len(value)} rows>"]
    return type(value).__name__


def test_golden_mrvfrontend_get_all_shape(bench_server):
    r = requests.get(
        f"{bench_server}/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all",
        timeout=15,
    )
    r.raise_for_status()
    assert_golden("mrvfrontend_get_all.json", _shape(r.json().get("message")))


def test_golden_side_menu_menulist_structure(frappe_site):
    import frappe

    fn = frappe.get_attr("frappe_side_menu.frappe_side_menu.api.get_menulist")
    original_user = frappe.session.user
    try:
        frappe.set_user("Administrator")
        result = fn()
    finally:
        frappe.set_user(original_user)
    # result may contain HTML — snapshot structural keys only.
    shape = _shape(result) if not isinstance(result, str) else "str"
    assert_golden("side_menu_menulist.json", shape)
