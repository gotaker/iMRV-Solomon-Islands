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
    for child_field in ["knowledge_resource_details", "knowledge_resource_details2",
                        "climate_change_division_images", "add_new_content"]:
        rows = getattr(frontend, child_field, None) or []
        for row in rows:
            for attr in dir(row):
                val = getattr(row, attr, None)
                if isinstance(val, str) and val.startswith("/files/"):
                    # public file URL
                    disk_path = base / "public" / val.lstrip("/")
                    if not disk_path.exists():
                        missing.append(str(disk_path))
                elif isinstance(val, str) and val.startswith("/private/files/"):
                    disk_path = base / val.lstrip("/")
                    if not disk_path.exists():
                        missing.append(str(disk_path))

    assert missing == [], (
        f"{len(missing)} File records point at missing on-disk files. "
        f"Run `bench --site {frappe_site} execute "
        f"mrvtools.mrvtools.after_install.load_default_files` to recover. "
        f"First few: {missing[:3]}"
    )
