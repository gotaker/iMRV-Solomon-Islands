"""Layer 1 — sample DB restored cleanly and migrate exited 0 with no errors logged."""

import pytest

pytestmark = pytest.mark.data


def test_sample_db_restore_and_migrate(frappe_site):
    """If the session fixture got here, restore + migrate succeeded. Assert no Error Log rows from the migration."""
    import frappe
    # Any Error Log row written by a migration patch during session setup would
    # indicate a silent v16 migration failure.
    error_count = frappe.db.count(
        "Error Log",
        filters={"method": ["like", "%migrate%"]},
    )
    assert error_count == 0, f"{error_count} migration-related Error Log rows present"
