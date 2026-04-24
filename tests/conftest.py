"""
Session-level fixtures for the v16 test harness.

Contract:
- `frappe_site`: restores sample DB, runs `bench migrate`, connects frappe; yields site name.
- `bench_server`: starts `bench serve` on $TEST_PORT; yields base URL.
- `browser`: launches Playwright chromium; skipped cleanly if playwright missing.
- `rollback_after_test` (autouse): wraps each test in a Frappe savepoint.

Env vars (all optional, sensible defaults):
- TEST_SITE (default `test_mrv.localhost`)
- TEST_PORT (default `8001`)
- BENCH_DIR (default `../frappe-bench`)
- SAMPLE_DB_URL (fallback when no local dump)
- TESTS_SKIP_UI (skip Playwright cleanly)
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

import pytest
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
BENCH_DIR = Path(os.environ.get("BENCH_DIR", REPO_ROOT.parent / "frappe-bench")).resolve()
TEST_SITE = os.environ.get("TEST_SITE", "test_mrv.localhost")
TEST_PORT = int(os.environ.get("TEST_PORT", "8001"))
SAMPLE_DB_URL = os.environ.get("SAMPLE_DB_URL")


def _find_local_sample_db() -> Path | None:
    """Return newest .sql.gz in `.Sample DB/` or None."""
    sample_dir = REPO_ROOT / ".Sample DB"
    if not sample_dir.is_dir():
        return None
    candidates = sorted(sample_dir.glob("*.sql.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _download_sample_db(url: str, dest: Path) -> None:
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 16):
                f.write(chunk)


def _resolve_sample_db() -> Path:
    local = _find_local_sample_db()
    if local is not None:
        # Copy to mktemp to sidestep the `.Sample DB/` space-in-path zgrep bug.
        tmp = Path(tempfile.mkdtemp(prefix="mrv-sampledb-")) / "sample.sql.gz"
        shutil.copy2(local, tmp)
        return tmp
    if SAMPLE_DB_URL:
        tmp = Path(tempfile.mkdtemp(prefix="mrv-sampledb-")) / "sample.sql.gz"
        _download_sample_db(SAMPLE_DB_URL, tmp)
        return tmp
    pytest.fail(
        "No sample DB available. Place a .sql.gz in `.Sample DB/` or set $SAMPLE_DB_URL.",
        pytrace=False,
    )


def _bench(*args: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    cmd = ["bench", *args]
    return subprocess.run(
        cmd,
        cwd=BENCH_DIR,
        check=check,
        capture_output=capture,
        text=True,
    )


def _wait_for_port(port: int, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                # port open — ping the API to confirm WSGI is alive
                try:
                    r = requests.get(f"http://127.0.0.1:{port}/api/method/ping", timeout=5)
                    if r.status_code == 200:
                        return
                except requests.RequestException:
                    pass
        time.sleep(0.5)
    raise RuntimeError(f"bench serve on port {port} did not become ready within {timeout}s")


@pytest.fixture(scope="session")
def frappe_site():
    """Restore sample DB, migrate, connect frappe. Yields site name."""
    if not BENCH_DIR.is_dir():
        pytest.fail(f"BENCH_DIR {BENCH_DIR} not found. Run ./install.sh --dev.", pytrace=False)

    dump = _resolve_sample_db()

    # Create site if missing (idempotent via --force on restore)
    sites_dir = BENCH_DIR / "sites" / TEST_SITE
    if not sites_dir.is_dir():
        _bench("new-site", TEST_SITE,
               "--admin-password", "admin",
               "--mariadb-root-password", os.environ.get("MARIADB_ROOT_PASSWORD", "admin"),
               "--install-app", "mrvtools",
               "--install-app", "frappe_side_menu")

    _bench("--site", TEST_SITE, "--force", "restore", str(dump))
    _bench("--site", TEST_SITE, "migrate")  # <-- THE v16 gate

    # Connect frappe in this process for tests that use the python API directly.
    import frappe
    frappe.init(site=TEST_SITE, sites_path=str(BENCH_DIR / "sites"))
    frappe.connect()

    yield TEST_SITE

    frappe.destroy()


@pytest.fixture(scope="session")
def bench_server(frappe_site):
    """Start `bench serve --port $TEST_PORT`. Yields base URL."""
    proc = subprocess.Popen(
        ["bench", "serve", "--port", str(TEST_PORT)],
        cwd=BENCH_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_port(TEST_PORT)
        yield f"http://127.0.0.1:{TEST_PORT}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture(scope="session")
def browser():
    """Playwright chromium. Skipped cleanly if playwright is missing or TESTS_SKIP_UI=1."""
    if os.environ.get("TESTS_SKIP_UI") == "1":
        pytest.skip("TESTS_SKIP_UI=1")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("playwright not installed")
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        yield b
        b.close()


@pytest.fixture(autouse=True)
def rollback_after_test(request, frappe_site):
    """Wrap each test in a Frappe savepoint so mutations don't leak across tests."""
    import frappe
    savepoint = f"testsave_{uuid.uuid4().hex[:12]}"
    frappe.db.savepoint(savepoint)
    try:
        yield
    finally:
        frappe.db.rollback(save_point=savepoint)
