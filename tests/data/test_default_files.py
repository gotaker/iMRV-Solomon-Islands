"""
Layer 1 — every File row referenced by MrvFrontend child tables resolves to an
on-disk file. Catches the recovery-trap regression documented in CLAUDE.md
("Seed data on install").
"""

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.data


def _files_base_path(site: str) -> Path:
    bench_dir = Path(os.environ.get("BENCH_DIR", "../frappe-bench")).resolve()
    return bench_dir / "sites" / site


def test_default_files_extracted(frappe_site):
    import frappe
    frontend = frappe.get_single("MrvFrontend")
    base = _files_base_path(frappe_site)

    missing = []
    frontend_meta = frappe.get_meta("MrvFrontend")
    child_fields = [f for f in frontend_meta.fields if f.fieldtype == "Table"]

    for child_fieldmeta in child_fields:
        child_field = child_fieldmeta.fieldname
        rows = getattr(frontend, child_field, None) or []
        if not rows:
            continue
        child_doctype = child_fieldmeta.options
        child_meta = frappe.get_meta(child_doctype)
        attach_fields = [f.fieldname for f in child_meta.fields if f.fieldtype in ("Attach", "Attach Image")]
        for row in rows:
            for fname in attach_fields:
                val = getattr(row, fname, None) or ""
                if not isinstance(val, str) or not val:
                    continue
                if val.startswith("/files/"):
                    disk_path = base / "public" / val.lstrip("/")
                elif val.startswith("/private/files/"):
                    disk_path = base / val.lstrip("/")
                else:
                    continue
                if not disk_path.exists():
                    missing.append(str(disk_path))

    assert missing == [], (
        f"{len(missing)} File records point at missing on-disk files. "
        f"Run `bench --site {frappe_site} execute "
        f"mrvtools.mrvtools.after_install.load_default_files` to recover. "
        f"First few: {missing[:3]}"
    )
