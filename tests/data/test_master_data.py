"""Layer 1 — every master-data doctype listed in after_install.py has >=1 row after restore+migrate.

The doctype list is NOT hand-copied — it's parsed directly from after_install.py
at import time via `ast`, so it stays in sync automatically.
"""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.data


def _extract_doctype_list() -> list[str]:
    """Parse mrvtools/mrvtools/after_install.py and return the `doctype_list` literal."""
    repo_root = Path(__file__).resolve().parents[2]
    source = (repo_root / "mrvtools" / "mrvtools" / "after_install.py").read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "doctype_list":
                    if isinstance(node.value, ast.List):
                        return [
                            elt.value for elt in node.value.elts
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                        ]
    raise RuntimeError(
        "Could not find `doctype_list = [...]` in mrvtools/mrvtools/after_install.py — "
        "the tripwire source changed; update this parser."
    )


MASTER_DATA_DOCTYPES = _extract_doctype_list()


@pytest.mark.parametrize("doctype", MASTER_DATA_DOCTYPES)
def test_master_data_rows_present(frappe_site, doctype):
    import frappe
    if not frappe.db.exists("DocType", doctype):
        pytest.fail(f"Master DocType {doctype!r} missing after migrate — schema regression")
    count = frappe.db.count(doctype)
    assert count >= 1, f"Master data doctype {doctype!r} has 0 rows after restore"
