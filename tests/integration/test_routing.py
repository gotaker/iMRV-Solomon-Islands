"""Layer 2 — Frappe website_route_rules redirect / SPA handoff."""

import pytest
import requests

pytestmark = pytest.mark.integration


def test_frontend_route_rules_redirect(bench_server):
    """`/` → 302 `/frontend/home`; `/frontend/foo` → 200 (served by frontend web template)."""
    r_root = requests.get(bench_server + "/", timeout=10, allow_redirects=False)
    assert r_root.status_code in (301, 302, 303)
    assert "/frontend/home" in r_root.headers.get("Location", "")

    r_route = requests.get(bench_server + "/frontend/home", timeout=10)
    assert r_route.status_code == 200
    # Web template should serve the SPA shell — assert some recognizable marker.
    assert "<html" in r_route.text.lower()
