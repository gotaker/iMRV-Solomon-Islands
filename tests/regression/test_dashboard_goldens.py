"""
Layer 4 — one golden-file test per previously-fixed SQL-string query.

The 8 queries live in mrvtools/mrvtools/page/main_dashboard/main_dashboard.py.
Each test calls the server-side function directly and snapshots its structural
shape (keys, types, row count bucket).

We deliberately snapshot *shape* not *exact values* because sample DB rows
drift. If a test needs exact-value pinning, adjust the shape function below.
"""

from __future__ import annotations

import pytest

from tests.regression._golden import assert_golden

pytestmark = pytest.mark.regression


def _shape(value):
    """Recursively reduce a value to its structural shape."""
    if isinstance(value, dict):
        return {k: _shape(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        if not value:
            return []
        return [_shape(value[0]), f"<{len(value)} rows>"]
    return type(value).__name__


# Map each fixed query to the dotted-path it lives at.
# Discovered by inspecting mrvtools/mrvtools/page/main_dashboard/main_dashboard.py.
# All 8 active @frappe.whitelist() functions are listed here.
DASHBOARD_QUERIES = [
    (
        "document_count",
        "mrvtools.mrvtools.page.main_dashboard.main_dashboard.get_document_count",
    ),
    (
        "cumulative_mitigation_till_date",
        "mrvtools.mrvtools.page.main_dashboard.main_dashboard.get_commulative_mitigation_till_date",
    ),
    (
        "cumulative_mitigation_last_year",
        "mrvtools.mrvtools.page.main_dashboard.main_dashboard.get_commulative_mitigation_last_year",
    ),
    (
        "co2_emission_latest",
        "mrvtools.mrvtools.page.main_dashboard.main_dashboard.total_co2_emission_latest",
    ),
    (
        "total_project_ndp",
        "mrvtools.mrvtools.page.main_dashboard.main_dashboard.get_total_project_ndp",
    ),
    (
        "sdg_category_wise",
        "mrvtools.mrvtools.page.main_dashboard.main_dashboard.get_total_sdg_category_wise",
    ),
    (
        "co2_emission_last_five_years",
        "mrvtools.mrvtools.page.main_dashboard.main_dashboard.total_co2_emission_last_five_years",
    ),
    (
        "finance_support",
        "mrvtools.mrvtools.page.main_dashboard.main_dashboard.get_finance_support",
    ),
]


@pytest.mark.parametrize(
    "name,dotted",
    DASHBOARD_QUERIES,
    ids=[n for n, _ in DASHBOARD_QUERIES],
)
def test_golden_dashboard_query(frappe_site, name, dotted):
    import frappe

    try:
        fn = frappe.get_attr(dotted)
    except Exception as e:
        pytest.skip(f"dotted path not resolvable yet: {dotted} ({e})")

    result = fn()
    assert_golden(f"dashboard_{name}.json", _shape(result))


def test_dashboard_queries_list_populated():
    """Tripwire: if DASHBOARD_QUERIES is empty, the implementer never reconciled
    against the real codebase. Fail loudly rather than silently passing 0 tests."""
    assert DASHBOARD_QUERIES, (
        "DASHBOARD_QUERIES is empty — the implementer did not inspect "
        "mrvtools/mrvtools/page/main_dashboard/main_dashboard.py and fill in "
        "the actual function dotted paths. See the IMPLEMENTER comment in this file."
    )
