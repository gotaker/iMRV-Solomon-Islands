# v16 Test Harness Design

**Date:** 2026-04-24
**Status:** Design approved, pending implementation plan.
**Context:** Frappe v14→v16 upgrade for iMRV-Solomon-Islands. Eight SQL-string query-builder breaks already fixed; a static sweep surfaced 3 BREAKING items (guest-accessible mutation endpoints) and found no further v16-specific regressions. This harness is the runtime counterpart to that static sweep — it verifies the v16 upgrade actually works end-to-end, exercises the security boundaries v16 tightened, and establishes infrastructure the project can grow into.

## Goals and non-goals

**Goals**
- Catch v16 regressions across data, integration, UI, pinned behavior, and security boundaries.
- Ship reusable fixture infrastructure so future Frappe bumps (v16→v17, etc.) re-use the same harness.
- Provide a single `pytest`-based entrypoint with layer-specific opt-outs for fast local iteration.
- Wire blocking CI on PRs to prevent v16 regressions merging.

**Non-goals**
- Not a coverage-chasing pyramid. No unit tests for every doctype controller.
- Not a replacement for `bench run-tests`. The existing [.github/workflows/ci-frappe-tests.yml](../../.github/workflows/ci-frappe-tests.yml) fresh-install path keeps running alongside.
- Not filling the 40 empty `test_*.py` doctype stubs.
- Not a Playwright per-route sweep — only 4 critical user journeys.

## Architecture

Single pytest-based harness driving five layers from one entrypoint. Frappe v16's `bench run-tests` is pytest-backed under the hood, so this meets the framework where it already is.

```
tests/                               (new, repo root)
├── conftest.py                      session + per-test fixtures
├── factories.py                     helpers for the rare case tests need fresh data
├── run.sh                           local entrypoint with --layer / --fast flags
├── data/                            Layer 1 — seed/migration/fixture integrity
├── integration/                     Layer 2 — HTTP against bench webserver
├── ui/                              Layer 3 — 4 Playwright journeys
├── regression/                      Layer 4 — golden outputs pinning v16 behavior
├── security/                        Layer 5 — auth, injection, secret exposure
└── golden/                          snapshot files (committed)
```

**Runtime flow per session**
1. Session-scoped fixture restores `.Sample DB/*.sql.gz` (or downloads from `$SAMPLE_DB_URL`) and runs `bench migrate`. Hard-fail if neither source is available — no silent skip.
2. Session fixture starts `bench serve --port $TEST_PORT` (default `8001`, decoupled from dev `8000`).
3. Every test auto-wraps in `frappe.db.begin()` / `frappe.db.rollback()` so mutations don't leak between tests.
4. UI journeys drive Playwright against the same running bench — no separate docker stack.

## Layered test design

### Layer 1 — Data (6 tests, `tests/data/`)

Verifies the install/migrate/seed pipeline — not business logic.

| Test | What it pins |
|---|---|
| `test_sample_db_restore_and_migrate` | Restore + `bench migrate` exit 0; no v16-migration errors in Error Log |
| `test_master_data_rows_present` | Parametrized over the 35 doctypes in [after_install.py](../../mrvtools/mrvtools/after_install.py) `doctype_list`; each has ≥1 row |
| `test_singles_synced` | MrvFrontend, Website Settings, Navbar Settings, Side Menu Settings exist with non-null core fields |
| `test_default_files_extracted` | Every File row referenced by MrvFrontend child tables resolves to an on-disk file (recovery-trap regression) |
| `test_no_legacy_desktop_icon_table` | `SHOW TABLES LIKE 'tabDesktop Icon'` is empty |
| `test_workspace_records_v16_shape` | `tabWorkspace` rows carry v16 columns (`public`, `is_hidden`, `for_user`) |

### Layer 2 — Integration (15 tests, `tests/integration/`)

HTTP against `http://localhost:$TEST_PORT`. Each whitelisted endpoint exercised for happy path and auth boundary.

| Test | Target |
|---|---|
| `test_api_get_approvers` | [mrvtools/api.py](../../mrvtools/api.py) `get_approvers` |
| `test_api_route_user` | `route_user` |
| `test_api_get_data_guest_readable` | `get_data` — guest-callable generic fetcher |
| `test_mrvfrontend_get_all_guest` | SPA homepage payload shape |
| `test_my_approval_insert_record_guest` | **Contract pin** — records current guest-callable behavior pending hardening |
| `test_my_approval_delete_record_guest` | Same shape |
| `test_user_registration_createUser_guest` | Same shape |
| `test_user_registration_insert_approved_users_guest` | Same shape |
| `test_user_registration_createApprovedUser_guest` | Same shape |
| `test_side_menu_get_menulist_authed` | HTML + JSON keys |
| `test_side_menu_guest_helpers` | `get_all_records`, `get_list`, `get_doctype` as guest |
| `test_login_redirect_on_session_creation` | POST login → GET `/app/` → 302 to configured route (exercises `set_default_route`) |
| `test_permission_query_my_approval_scopes_to_user` | User-without-role → empty; approver → rows |
| `test_permission_query_approved_user` | Same shape for Approved User |
| `test_frontend_route_rules_redirect` | `/` → 302 `/frontend/home`; `/frontend/foo` → 200 |

Tests flagged **Contract pin** intentionally record the flagged BREAKING guest-access behavior. Their docstrings link to the hardening follow-up; when the endpoints are locked down, these tests flip from asserting 200 to asserting 403. They exist so we notice if v16 already changed the behavior silently.

### Layer 3 — UI (4 Playwright journeys, `tests/ui/`)

| Test | Journey |
|---|---|
| `test_login_and_desk_redirect` | Administrator log in → `/app/main-dashboard`, no console errors, sidebar renders |
| `test_spa_home_renders` | `/frontend/home` — hero visible, Knowledge Resource cards ≥1, CCD images load without 404s |
| `test_approval_workflow_end_to_end` | Draft user creates Project, submits; approver logs in, approves via My Approval; verify DB status transition |
| `test_main_dashboard_tiles_render` | All 8 previously-fixed dashboard tiles show numeric values (not `None`, not error cards) |

Playwright runs headless chromium; screenshot + trace captured on failure. Each journey asserts both final state and the absence of console errors / failed network requests during navigation.

### Layer 4 — Regression (10 tests, `tests/regression/`)

Golden-output pinning. First run captures response to `tests/golden/<name>.json`; subsequent runs diff. `TESTS_UPDATE_GOLDEN=1` regenerates when expected behavior legitimately changes.

| Test | Pins |
|---|---|
| `test_golden_*` ×8 | One per previously-fixed SQL-string query (dashboard/report responses) |
| `test_golden_mrvfrontend_get_all_shape` | SPA homepage payload structural snapshot |
| `test_golden_side_menu_menulist_structure` | `get_menulist` DOM skeleton snapshot |

Golden tests couple to sample DB content. They must only run against the committed/released sample DB version, not arbitrary dumps. CI pins the sample DB version via GitHub release tag; local runs use the newest `.Sample DB/*.sql.gz` and accept that goldens will drift when the dump changes.

### Layer 5 — Security (10 tests, `tests/security/`)

Exercises the auth, injection, and data-exposure boundaries that v16 tightened. Scoped to the surface area actually present in this codebase — not a generic OWASP sweep.

| Test | What it pins |
|---|---|
| `test_guest_cannot_read_user_secrets` | `GET /api/resource/User` as guest never returns `password`, `api_secret`, `reset_password_key`, `new_password` fields |
| `test_api_get_data_blocks_sensitive_doctypes` | [api.get_data](../../mrvtools/api.py) as guest with `doctype=User` / `DocShare` / `Communication` returns 403 or filtered response; no secret fields leak |
| `test_csrf_required_on_whitelisted_post` | POST to any whitelisted method without CSRF token → 403 under v16 strict mode |
| `test_session_cookie_hardening` | `Set-Cookie` on login carries `HttpOnly` and (in prod config) `Secure`, `SameSite=Lax` |
| `test_sql_injection_in_side_menu_interpolation` | The `.format()`-built SQL at [frappe_side_menu/api.py:52-74](../../frappe_side_menu/frappe_side_menu/api.py#L52-L74) — pass role/doctype names containing `'; DROP TABLE tabUser; --` payload, assert no table dropped, query returns empty/error |
| `test_xss_in_user_registration_fields` | Submit `<script>alert(1)</script>` in `createUser` name field; when rendered in any list/detail view, assert HTML-escaped |
| `test_logout_invalidates_session` | Authed session → `/api/method/logout` → retry authed endpoint returns 403, not 200 |
| `test_permission_query_cannot_be_bypassed` | `My Approval` via `/api/resource/My Approval`, `/api/method/frappe.client.get_list`, and direct `frappe.db.get_list` all respect the `get_query_conditions` hook |
| `test_guest_cannot_invoke_non_whitelisted_method` | Guest POST to `frappe.client.set_value` → 403/405 (not 500); response body doesn't leak stack trace |
| `test_private_file_requires_auth` | GET `/private/files/<any>` as guest → 403; as authed user without perm → 403; as owner → 200 |

**Contract-pin caveat**: the 5 guest-callable mutation tests in Layer 2 (`test_my_approval_insert_record_guest`, etc.) document *current* behavior. Layer 5's `test_guest_cannot_read_user_secrets` and `test_api_get_data_blocks_sensitive_doctypes` test *correct* behavior. If either fails, fix the endpoint — don't relax the test.

**Out of scope for v1:** rate limiting, CSRF token rotation cadence, password policy enforcement, 2FA flows, secret scanning in logs. These belong in a dedicated security-hardening PR, not the v16 gate harness.

## Fixtures and conftest

`tests/conftest.py` — three session fixtures, one autouse per-test fixture.

```python
@pytest.fixture(scope="session")
def frappe_site():
    # 1. Resolve sample DB: prefer newest .Sample DB/*.sql.gz, else download from
    #    $SAMPLE_DB_URL. Hard-fail if neither — no silent skip.
    # 2. Copy to mktemp (handles the ".Sample DB/" space-in-path gotcha).
    # 3. bench --site $TEST_SITE --force restore <dump>  (creates site if missing)
    # 4. bench --site $TEST_SITE migrate — must exit 0; this IS the v16 gate.
    # 5. yield site name.
    # 6. Teardown: leave site in place for re-runs; operator-driven cleanup.

@pytest.fixture(scope="session")
def bench_server(frappe_site):
    # Start `bench serve --port $TEST_PORT` subprocess; poll /api/method/ping;
    # yield base_url. Terminate on session end.

@pytest.fixture(scope="session")
def browser():
    # Playwright chromium headless. Skip Layer 3 cleanly if playwright not
    # installed — don't let missing browser fail Layers 1/2/4/5.

@pytest.fixture(autouse=True)
def rollback_after_test(frappe_site):
    # frappe.db.begin() before; frappe.db.rollback() after. Inherits
    # FrappeTestCase semantics without forcing every test class to extend it —
    # works for plain pytest functions too.
```

`tests/factories.py` — thin helpers for the few cases a test needs a specific starter record (e.g. a draft Project for the approval journey). Not factory-boy — just `make_project(**overrides)`, `make_approver_user()`, ~5 functions.

## Environment variables

| Var | Default | Purpose |
|---|---|---|
| `TEST_SITE` | `test_mrv.localhost` | Target bench site |
| `TEST_PORT` | `8001` | bench serve port (decoupled from dev `8000`) |
| `BENCH_DIR` | `../frappe-bench` | Consistent with `start.sh` / `install.sh` |
| `SAMPLE_DB_URL` | — | Fallback dump URL when no local file present |
| `TESTS_UPDATE_GOLDEN` | `0` | Regenerate Layer 4 snapshots |
| `TESTS_SKIP_UI` | `0` | Fast mode — skip Playwright without downloading chromium |

## Local entrypoint

`./tests/run.sh` — wraps pytest with sensible defaults.

| Invocation | Behavior |
|---|---|
| `./tests/run.sh` | All layers, ~2–3 min |
| `./tests/run.sh --layer data` | Only `tests/data/` |
| `./tests/run.sh --layer integration` | Only `tests/integration/` |
| `./tests/run.sh --layer ui` | Only `tests/ui/` |
| `./tests/run.sh --layer regression` | Only `tests/regression/` |
| `./tests/run.sh --layer security` | Only `tests/security/` |
| `./tests/run.sh --fast` | Layers 1+2+5 only (`TESTS_SKIP_UI=1`), ~45s |
| `./tests/run.sh --update-golden` | `TESTS_UPDATE_GOLDEN=1 pytest tests/regression/` |

## CI integration

**Do not extend [ci-frappe-tests.yml](../../.github/workflows/ci-frappe-tests.yml).** It remains as the fresh-install sanity signal. Add a second workflow for the sample-DB harness.

**New: `.github/workflows/ci-test-harness.yml`**

- **Triggers**: PRs to `master`, nightly at 03:00 UTC (1h after ci-frappe-tests to avoid runner contention).
- **Service containers**: MariaDB 10.6 + Redis 7, same pins as ci-frappe-tests.yml. Version pins in both workflows and [install.sh](../../install.sh) must stay in sync (per CLAUDE.md CI section).
- **Sample DB acquisition**: downloads from GitHub release asset using the `sample-db-YYYYMMDD` tag convention already documented in [deploy/railway/README.md](../../deploy/railway/README.md). Release asset URL passed via `SAMPLE_DB_URL` secret.
- **Jobs** (fail-fast split for clearer signal):
  | Job | Duration | Status |
  |---|---|---|
  | `harness-data-integration` | ~90s | Blocking |
  | `harness-ui` | ~120s | Blocking |
  | `harness-security` | ~45s | Blocking |
  | `harness-regression` | ~60s | **Advisory for 2 weeks**, then blocking |
- **On failure**: upload `frappe-bench/logs/`, Playwright traces, and failure screenshots as artifacts. Nightly failures auto-open a GitHub issue labelled `ci-harness-failure` (reuse existing label machinery from ci-frappe-tests.yml).
- **Fork PR safety**: if `SAMPLE_DB_URL` secret unavailable (forks), workflow skips with a clear status message. `ci-frappe-tests.yml` fresh-install path still runs — fork PRs remain testable.

**Branch protection update**: add `harness-data-integration`, `harness-ui`, and `harness-security` as required checks alongside existing four (`frontend-build`, `frontend-format`, `python-lint`, `frappe-tests`). Regression is advisory initially.

## Scope boundaries

**In scope for v1:**
- 45 tests enumerated above (6 data + 15 integration + 4 UI + 10 regression + 10 security).
- Fixture infrastructure (conftest, factories, run.sh).
- New CI workflow with blocking/advisory split.
- Documentation in `tests/README.md` covering local setup, env vars, common failures.

**Explicitly out of scope (deferred):**
- Unit tests for individual doctype controllers (the 40 empty stubs stay empty).
- Coverage reporting.
- Performance/load testing.
- Visual regression via Playwright screenshots (too flaky for v1).
- Hardening the 3 BREAKING guest-access endpoints — that's a separate security-hardening PR. Layer 2 contract-pin tests flag them; they don't fix them.

## Success criteria

1. `./tests/run.sh` runs green against the current sample DB on v16.
2. A deliberate regression (e.g. reverting one of the 8 SQL-string fixes) causes at least one test in Layers 1, 2, 4, or 5 to fail with a clear diff.
3. CI blocks PR merges on `harness-data-integration`, `harness-ui`, or `harness-security` failure.
4. Full local suite completes under 3 minutes on a mid-range dev laptop; `--fast` under 45 seconds.

## Open questions

None at design time. Any discoveries during implementation (e.g. `bench serve` port contention patterns, Playwright chromium cache behavior in CI) will be resolved in the implementation plan rather than revisited here.
