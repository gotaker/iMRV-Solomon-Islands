"""Smoke test — verifies conftest fixtures compose without error."""

import pytest
from tests.conftest import TEST_SITE

pytestmark = pytest.mark.data


def test_frappe_site_connects(frappe_site):
    import frappe
    assert frappe.local.site == frappe_site
    assert frappe.db.sql("SELECT 1")[0][0] == 1


def test_bench_server_responds(bench_server):
    import requests
    headers = {"Host": TEST_SITE}
    r = requests.get(f"{bench_server}/api/method/ping", headers=headers, timeout=5)
    assert r.status_code == 200
    assert r.json()["message"] == "pong"
