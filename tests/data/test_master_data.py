"""Layer 1 — every master-data doctype listed in after_install.py has >=1 row after restore+migrate."""

import pytest

pytestmark = pytest.mark.data

# Copied from mrvtools/mrvtools/after_install.py `doctype_list`.
# If that list changes, update this one — it's an intentional tripwire.
MASTER_DATA_DOCTYPES = [
    "Adaptation Category", "Adaptation Objective", "Disbursement Category",
    "Ministry", "Project Included In", "Project Key Sector", "Project Key Sub Sector",
    "Project Programme", "Project Objective", "Project Actions",
    "NDP Objective Coverage", "SDG Assessment",
    "GHG Sector", "GHG Sub Sector", "GHG Category", "GHG Sub Category",
    "Energy Fuel Master List", "Livestock Population Master List",
    "Livestock Emission Factor Master List", "IPPU Emission Factors Master List",
    "IPPU GWP Master List", "Forest Category Master List",
    "Direct and Indirect Managed Soils Master List",
    "Waste Population Master List", "Parameter Master List",
    "GHG Inventory Table Name Master List",
    "GHG Inventory Report Categories", "GHG Inventory Report Formulas",
    "Mitigation Non GHG Mitigation Benefits",
    "Climate Finance Monitoring Information",
]


@pytest.mark.parametrize("doctype", MASTER_DATA_DOCTYPES)
def test_master_data_rows_present(frappe_site, doctype):
    import frappe
    if not frappe.db.exists("DocType", doctype):
        pytest.fail(f"Master DocType {doctype!r} missing after migrate — schema regression")
    count = frappe.db.count(doctype)
    assert count >= 1, f"Master data doctype {doctype!r} has 0 rows after restore"
