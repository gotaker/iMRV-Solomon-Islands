# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```
- Execute in parallel where feasible.
-Stress test convergence

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

## Repository shape

This repo contains **two Frappe apps** side-by-side plus a **Vue 3 SPA**:

- `mrvtools/` — the main Frappe app (MRV tooling: projects, adaptation, mitigation, GHG inventory, climate finance, reports). Declared in [setup.py](setup.py), version in [mrvtools/__init__.py](mrvtools/__init__.py). Ships two Frappe modules listed in [mrvtools/modules.txt](mrvtools/modules.txt): `Mrvtools` (under [mrvtools/mrvtools/](mrvtools/mrvtools/)) and `GHG Inventory` (under [mrvtools/ghg_inventory/](mrvtools/ghg_inventory/)).
- `frappe_side_menu/` — a second, independent Frappe app providing the desk's **floating navigation drawer** (top-left burger button → click-triggered slide-in panel over a translucent backdrop). Has its own [setup_sidebarmenu.py](setup_sidebarmenu.py), [hooks.py](frappe_side_menu/hooks.py), and doctypes (`Side Menu`, `Sub Menu`, `Sub Menu Group`, `Side Menu Settings`). It is installed as a separate bench app, not as a subpackage of `mrvtools`.
- `frontend/` — a Vue 3 + Vite + TailwindCSS + Frappe UI SPA that is built into `mrvtools/public/frontend/` and served by Frappe at `/frontend/*`. Served page routes: Home, About, Projects, Climate Change Division, Reports, Support, Knowledge Resource, What's New, Login ([frontend/src/router.js](frontend/src/router.js)).

When working on a change, first identify which of these three layers owns the behavior — they have different build/deploy paths and different entrypoints.

Two pip entry points live at the repo root: [setup.py](setup.py) packages `mrvtools`, [setup_sidebarmenu.py](setup_sidebarmenu.py) packages `frappe_side_menu`. `requirements.txt` is the dependency manifest.

The top-level [iMRV-Solomon-Islands/public/frontend/](iMRV-Solomon-Islands/public/frontend/) directory is a stray misplaced build artifact — the real Vite output lives at `mrvtools/public/frontend/`. Don't edit anything inside the top-level path; changes there are not served.

**Design specs.** Significant subsystems have written design docs in [docs/superpowers/specs/](docs/superpowers/specs/) — currently CI pipeline, Railway deployment, install/start/shutdown scripts, v16 test harness, and the LLM council skill. When investigating *why* a feature works the way it does, check there before reverse-engineering from code; this CLAUDE.md links each spec near its topic.

## Build and run

Frontend dev (proxies to bench on :8000):

```bash
yarn --cwd frontend install     # or: cd frontend && yarn
yarn dev                         # runs `cd frontend && yarn dev` — Vite on :8080
yarn build                       # builds into mrvtools/public/frontend/ and copies index.html → mrvtools/www/frontend.html
```

The build pipeline is driven by [frontend/vite.config.mjs](frontend/vite.config.mjs), which invokes `frappe-ui/vite`'s plugin with `buildConfig: { outDir, baseUrl, indexHtmlPath }` — the plugin does three things in one pass: writes the bundle to `mrvtools/public/frontend/`, injects `/assets/mrvtools/frontend/` as the production base URL, and copies the emitted `index.html` to `mrvtools/www/frontend.html` (which is what Frappe serves under `/frontend`). Those three paths, plus the `website_route_rules` / `app_include_*` entries in [mrvtools/hooks.py](mrvtools/hooks.py), all have to stay in sync — changing the app name or URL prefix means editing `vite.config.mjs` and `hooks.py` together. Note the `.mjs` extension is load-bearing: `frappe-ui/vite` is ESM-only and can't be `require`d, and the `frontend/package.json` has no `"type": "module"` (so the tailwind/postcss CommonJS configs keep working).

**Verifying a production build locally.** Don't use `vite preview` — it serves from `frontend/dist` with the dev base URL and doesn't reflect what Frappe will actually ship. Instead, after `yarn build`, serve the real output dir: `python3 -m http.server -d mrvtools/public/frontend 8090` and load `http://localhost:8090/`. This catches base-URL rewrite bugs and missing-asset 404s that `vite preview` hides.

Dev-server: `yarn dev` runs Vite on :8080. The plugin's `frappeProxy` reads `common_site_config.json` from the adjacent bench and proxies `/api`, `/method`, `/assets`, `/files`, `/private`, `/app`, `/login`, `/logout`, and `/socket.io` to the Frappe webserver (host-header-aware — visiting `http://mrv.localhost:8080` proxies to `http://mrv.localhost:8000`). The old `"ignore_csrf": 1` workaround in `site_config.json` is no longer strictly required since CSRF tokens round-trip through the proxy, but leave it on for dev ergonomics if other tooling expects it.

[frontend/src/main.js](frontend/src/main.js) wires Frappe-UI with `frappeRequest` as the resource fetcher and registers `Button`/`Card`/`Input` globally; AOS (animate-on-scroll) is initialized in `App.vue`. If a Frappe-UI component looks unresolved, it needs registering here.

There is no CI (`.github/workflows/` is absent) and no enforced linting — only [frontend/.prettierrc.json](frontend/.prettierrc.json) exists and nothing runs it automatically.

Day-to-day stack lifecycle on an already-installed bench: [start.sh](start.sh) and [shutdown.sh](shutdown.sh) at the repo root. `./start.sh --dev` brings up MariaDB/Redis (if needed), `bench start` in the background, and Vite on :8080; `./start.sh --prod` skips Vite. `./shutdown.sh` stops bench + Vite (sweeps orphan listeners on the bench's actual ports, read from `common_site_config.json`); `./shutdown.sh --full` also stops MariaDB/Redis. Both honour `BENCH_DIR`, `SITE_NAME`, and `DRY_RUN=1`. Spec: [docs/superpowers/specs/2026-04-19-start-shutdown-scripts-design.md](docs/superpowers/specs/2026-04-19-start-shutdown-scripts-design.md).

For a one-command bootstrap (fresh macOS, Ubuntu, or Windows/WSL2 laptop → working dev or prod install), run [install.sh](install.sh) at the repo root: `MYSQL_ROOT_PASSWORD=<pw> ./install.sh --dev` (or `--prod`). The script is idempotent — it automates exactly the `bench get-app` / `install-app` / `migrate` / `yarn build` sequence documented above, plus OS package install (Homebrew on macOS, apt on Ubuntu/WSL2), `bench init`, `new-site`, and the `ignore_csrf` / `developer_mode` flip for dev. Env vars (`BENCH_DIR`, `SITE_NAME`, `FRAPPE_BRANCH`, `PROD_DOMAIN`, `PROD_ENABLE_TLS`, etc.) override defaults; `DRY_RUN=1` prints what would run without executing it. Prod-only: set `PROD_DOMAIN=<fqdn>` to run `bench setup add-domain`, and `PROD_ENABLE_TLS=1` (Ubuntu only) to provision a Let's Encrypt cert via `bench setup lets-encrypt`. See [docs/superpowers/specs/2026-04-19-unified-setup-script-design.md](docs/superpowers/specs/2026-04-19-unified-setup-script-design.md) for the full spec.

**Sample data on install.** `./install.sh --dev` force-restores the newest `*.sql.gz` from [.Sample DB/](.Sample%20DB/) (gitignored — drop a current dump there before running install on a fresh clone) and re-runs `bench migrate` after restore so the schema tracks the app code. `--prod` skips the restore by default. Override either way with `--with-sample-data` / `--no-sample-data` or `LOAD_SAMPLE_DATA=1/0`; `SAMPLE_DB_PATH=<file>` selects a specific dump. The restore step copies the file to `mktemp` first because Frappe's `bench restore` shells out to `zgrep`/`gunzip` without quoting the path and chokes on the space in `.Sample DB/`.

**Publishing a new sample DB release.** Railway consumes sample DBs via `SAMPLE_DB_URL` pointing at a GitHub Release asset; cut a new release from the latest `.Sample DB/*.sql.gz` using the `gh release create` recipe in [deploy/railway/README.md](deploy/railway/README.md) (tag format `sample-db-YYYYMMDD`, no PII scrub — demo data only).

Frappe app install (run from your bench root, not this directory):

```bash
bench get-app mrvtools <path-or-url>
bench --site <site> install-app mrvtools
bench --site <site> install-app frappe_side_menu
bench --site <site> migrate
```

Tests (Frappe's doctype test runner — per-app, requires a bench + site):

```bash
bench --site <site> run-tests --app mrvtools
bench --site <site> run-tests --app mrvtools --doctype "Adaptation"
bench --site <site> run-tests --app frappe_side_menu
```

Legacy doctype tests (every `test_*.py` next to a doctype) depend on Frappe's test runner above. The modern test loop lives in `tests/` — see the pytest harness section below.

**Pytest test harness ([tests/](tests/)).** A second, parallel test stack — five layers (data, integration, ui, regression, security), ~50 tests — driven by `./tests/run.sh`. This is the primary local test loop; `bench run-tests` is for legacy doctype tests only. Layout and design intent: [docs/superpowers/specs/2026-04-24-v16-test-harness-design.md](docs/superpowers/specs/2026-04-24-v16-test-harness-design.md). Quick reference:

```bash
./tests/run.sh                       # all layers, ~2–3 min
./tests/run.sh --layer integration   # one layer (data|integration|ui|regression|security)
./tests/run.sh --fast                # layers 1+2+5 (no UI), ~45s
./tests/run.sh --update-golden       # regenerate Layer 4 snapshots
```

Uses `TEST_SITE=test_mrv.localhost` and `TEST_PORT=8001` (decoupled from dev's `8000`) so it can run alongside `./start.sh --dev`. Layer 3 (UI) needs `playwright install chromium`; set `TESTS_SKIP_UI=1` to skip. If `bench migrate` fails during session setup, that *is* the v16 gate firing — fix the migration, don't bypass the harness. Common failures and env vars: [tests/README.md](tests/README.md).

For browser-based manual QA outside the harness, [.mcp.json](.mcp.json) registers `chrome-devtools` and `playwright` MCP servers — useful for driving the SPA against a running `./start.sh --dev` without writing a Playwright test.

If your bench's MariaDB root password isn't `admin`, export `MARIADB_ROOT_PASSWORD=…` before running — [tests/conftest.py](tests/conftest.py) passes it to `bench restore` and `bench new-site`, and a mismatch surfaces as a cryptic restore failure mid-session.

Test isolation: an autouse `rollback_after_test` fixture wraps every test in a Frappe savepoint that rolls back on teardown ([tests/conftest.py:215](tests/conftest.py#L215)). Tests can mutate the database freely without cleanup or cross-test leakage; don't add `frappe.db.commit()` to a test unless you genuinely need to break that guarantee.

## Continuous integration

CI runs via GitHub Actions. Three workflows:

- [.github/workflows/ci-fast.yml](.github/workflows/ci-fast.yml) — runs on every PR and on pushes to `Main`. Three parallel jobs: `frontend-build` (Vite build), `frontend-format` (Prettier `--check` against `frontend/src/**/*.{js,vue,css}`), `python-lint` (ruff on both Frappe apps). Target <2 min.
- [.github/workflows/ci-frappe-tests.yml](.github/workflows/ci-frappe-tests.yml) — runs on PRs targeting `Main` and nightly at 02:00 UTC. Spins up MariaDB 10.6 + Redis 7 service containers, runs `bench init`, installs both apps into a fresh `test_site`, then `bench run-tests --app mrvtools` and `--app frappe_side_menu`. On failure, uploads `frappe-bench/logs/` as an artifact; nightly failures also auto-open a GitHub issue labelled `ci-nightly-failure` (the label must exist in the repo).
- [.github/workflows/ci-test-harness.yml](.github/workflows/ci-test-harness.yml) — runs the pytest harness (data / integration / ui / security as required checks; regression advisory for two weeks then blocking). Restores the `SAMPLE_DB_URL` dump into a throwaway bench, then invokes `pytest` directly (not `./tests/run.sh`) so it can split layers across jobs. Reuses [.github/actions/setup-bench-harness/](.github/actions/setup-bench-harness/) for the bench bootstrap.

Design spec: [docs/superpowers/specs/2026-04-19-ci-pipeline-design.md](docs/superpowers/specs/2026-04-19-ci-pipeline-design.md).

Version pins live in both workflow files and in [install.sh](install.sh) — keep them in sync. Bumping Python, Node, or the Frappe branch in `install.sh` requires a matching edit to `ci-frappe-tests.yml` in the same PR.

[ruff.toml](ruff.toml) is intentionally conservative: only `E`/`F`/`I` are selected, and ~10 specific rules (`E501`, `E711`, `E712`, `E722`, `F841`, …) are explicitly ignored as "pre-existing legacy patterns" in Frappe controllers. The ignores are baseline, not aspirational — don't widen ruff's scope or "clean up" `== None` / bare `except:` / unused locals as a side-effect of unrelated work; that's a separate, opt-in cleanup.

Branch protection on `Main` requires these status checks (configure manually via repo Settings → Branches): `frontend-build`, `frontend-format`, `python-lint`, `frappe-tests`.

The test harness adds three more required checks: `harness-data-integration`, `harness-ui`, `harness-security`. `harness-regression` is advisory for the first two weeks, then flipped to blocking in [ci-test-harness.yml](.github/workflows/ci-test-harness.yml).

Secrets needed: `SAMPLE_DB_URL` (URL to a `sample-db-YYYYMMDD` GitHub release asset, per [deploy/railway/README.md](deploy/railway/README.md)).

Secrets needed: `MARIADB_ROOT_PASSWORD` (any strong password — only used inside the ephemeral MariaDB service container).

## Architecture notes worth knowing before editing

**Routing handoff.** [mrvtools/hooks.py](mrvtools/hooks.py) defines `website_route_rules` mapping `/frontend/<path:app_path>` to the `frontend` web template, and redirects `/` → `/frontend/home`. Inside the SPA, `createWebHistory('/frontend')` takes over. A route that "doesn't work" may be failing at either the Frappe route-rule layer or the Vue router layer — check both. `/login` is also overridden to a `custom_login` web template.

**Seed data on install.** `after_install = "mrvtools.mrvtools.after_install.after_install"` runs three loaders from [mrvtools/mrvtools/after_install.py](mrvtools/mrvtools/after_install.py):
1. `load_master_data` — inserts records for a hard-coded list of ~35 doctypes from JSON files in [mrvtools/master_data/](mrvtools/master_data/). The doctype list is maintained in code; adding a new master-data doctype requires both the JSON file and a line in the `doctype_list`.
2. `load_default_files` — unzips `mrvtools/public/mrv_default_files.zip` into Frappe's File doctype.
3. `load_single_doc` — upserts Single doctypes (Website Settings, Navbar Settings, Side Menu Settings, MrvFrontend).

All three use `ignore_permissions=True` and swallow exceptions into `frappe.log_error`. When install appears to "silently succeed" but data is missing, check the Error Log doctype.

`load_default_files` decouples the on-disk and DB-record checks: a missing physical file is always re-extracted from `mrv_default_files.zip` even when the `File` DB record still exists (see [mrvtools/mrvtools/after_install.py:16](mrvtools/mrvtools/after_install.py#L16)). This closes the old recovery trap where a Railway volume remount would leave orphan DB records pointing at files that no longer exist, and neither a reinstall nor re-running `load_default_files` could recover on its own. If seed images 404 after a volume wipe now, run `bench --site <site> execute mrvtools.mrvtools.after_install.load_default_files` — or on Railway, set `SINGLES_FORCE_SYNC=1` and redeploy (the entrypoint's force-sync block calls both `load_single_doc` and `load_default_files`).

**Permission query conditions.** [mrvtools/hooks.py](mrvtools/hooks.py) wires `My Approval` and `Approved User` to `get_query_conditions` functions in their respective doctype modules — these filter list views server-side. Changes to approval visibility belong there, not in client-side JS.

**Doctype conventions.** Doctypes ending in `_childtable` are Frappe child tables and must be embedded in a parent doctype; they are not independently listable. Doctypes ending in `_master_list` are reference/lookup tables seeded by `load_master_data`. The `edited_*` doctypes (e.g. `edited_project_details`, `edited_ghg_inventory_details`) appear to be revision/draft variants of their base doctypes — treat them as paired.

**Frontend data layer (in flight, untracked).** [frontend/src/main.js](frontend/src/main.js) imports `./router`, so [frontend/src/router.js](frontend/src/router.js) is the live router — its `beforeEach` only sets `document.title`, there is currently no auth guard and no `/account/login` route. A parallel set of files exists but is **not yet wired in**: `frontend/src/routes.js` (alternate route table with Login + Landing), `frontend/src/pages/Login.vue`, `frontend/src/pages/Landing.vue`, and `frontend/src/data/{session,user}.js` (Frappe UI `createResource` for login/logout/`frappe.auth.get_logged_user`). All five are untracked. When you touch auth/redirect flow: confirm whether the work has been wired into `main.js`/`router.js` yet, or whether you're meant to finish wiring it.

**Two hooks.py files.** `mrvtools/hooks.py` and `frappe_side_menu/hooks.py` are independent — each is read by Frappe for its own app. Don't consolidate.

**Post-login redirect.** [frappe_side_menu/hooks.py](frappe_side_menu/hooks.py) sets `on_session_creation = "frappe_side_menu.frappe_side_menu.api.set_default_route"`, which sends every logged-in user — including System Users like `Administrator` — to `/app/<route>` on the Frappe desk, not the SPA. The route comes from `Side Menu Settings → Post-Login Landing Route` (the underlying field is still `route_logo` for backwards compatibility), and falls back to `main-dashboard` when blank ([frappe_side_menu/frappe_side_menu/api.py:182](frappe_side_menu/frappe_side_menu/api.py#L182)). This split is intentional: the SPA at `/frontend/home` is the public-facing site, reachable without login. Login-redirect bugs usually originate here, not in `mrvtools/hooks.py`.

**Desk customisations are narrow.** `mrvtools/hooks.py` injects `doctype_js` / `doctype_list_js` only for the `User` doctype; `frappe_side_menu/hooks.py` injects `doctype_list_js` only for `Project`. Most `doc_events` / `scheduler_events` / `override_doctype_class` lines in both files are commented-out stubs — don't read them as active wiring.

**Floating navigation drawer.** The `frappe_side_menu` app renders the desk nav as a click-triggered overlay drawer, NOT a fixed left rail. JS in [frappe_side_menu/public/js/frappe_side_menu.js](frappe_side_menu/public/js/frappe_side_menu.js) injects a floating `.fsm-trigger` button (top-left, `z-index: 1041`) and wires the prepended `<aside class="main-sidebar">` (`id="fsm-drawer"`, `role="dialog"`) with `body.fsm-open` toggling, focus trap, scroll-lock, hashchange/Escape/modal-open close handlers, and inline-accordion submenu behavior via a unified `toggleSubMenu`. Drawer surface is frosted-glass (`var(--ed-frost-bg) + blur(20px) saturate(140%)`) over a translucent forest backdrop (`rgba(1,71,46,0.4) + blur(4px)`). The three template variants (`side_menu1.html`, `drill_down_menu.html`, `drill_down_tab.html`) retain DB-color customisation Jinja blocks but their inline rail-positioning styles are zeroed. **Frappe v16 gotchas wired in**: (a) modal `show` events are NOT `show.bs.modal` in v16 — the listener handles both for compat; (b) wizard guard checks both `/app/setup-wizard` AND `/desk/setup-wizard` because v16 canonicalises desk URLs to `/desk/*`; (c) Page JS like `main_dashboard.js` should guard cross-doctype queries with `frappe.boot.user.can_read.includes('<DocType>')` to avoid 403s for users without read perm — see [mrvtools/mrvtools/page/main_dashboard/main_dashboard.js:65-68](mrvtools/mrvtools/page/main_dashboard/main_dashboard.js#L65-L68). Layout invariants: `.fsm-trigger` is `position: fixed` at `top: 12px; left: 12px; width: 40px;` so the desk top-bar's `.navbar-breadcrumbs` / `.page-head .page-title` rules in [frappe_side_menu.css](frappe_side_menu/public/css/frappe_side_menu.css) MUST keep their `margin-left: 60px` to clear the trigger — without it the page title (e.g. "Main Dashboard") sits under the button and reads as `n Dashboard`.

**Drawer permission filtering — what to fix at, what to fix above.** [frappe_side_menu/frappe_side_menu/api.py](frappe_side_menu/frappe_side_menu/api.py) `get_menulist()` filters drawer entries by user permissions. Two pitfalls recurring in this code:
1. **Don't substring-test against the SQL fragment.** The function builds a comma-joined `permitted_docs` string for the `IN (...)` clauses; the *Python* side has separate `permitted_docs_set` (and `_reports_set` / `_pages_set`). Use the sets for `if menu_doc not in …` checks. A previous regression used the SQL string, and substring matching let "User" match `'"User Registration","Approved User"'` so the USERS section leaked to read-only roles.
2. **`get_permitted_docs_for_role` over-reports.** It returns every doctype with *any* DocPerm row for the role, including rows where `read=write=create=0` (the sample DB has Custom DocPerms like `Observer GHG Inventory Report` on `GHG Inventory` with all three at 0). Always narrow the resulting set with `frappe.has_permission(d, "read", user=user)` before building the SQL fragment, or the drawer shows top-level entries (GHG INVENTORY) whose target page then 403s on click.

**Railway deployment.** Staging/demo runs on Railway using the image built from [Dockerfile](Dockerfile), launched by [deploy/railway/entrypoint.sh](deploy/railway/entrypoint.sh), fronted by [deploy/railway/nginx.conf.template](deploy/railway/nginx.conf.template). Operational runbook: [deploy/railway/README.md](deploy/railway/README.md). Local integration test of the same image: `docker compose -f deploy/railway/docker-compose.local.yml up --build`. Three non-obvious invariants:

1. **`/files/` must be an nginx `alias`, not a `proxy_pass` to gunicorn.** Frappe's WSGI handler returns 404 for public File URLs in this single-tenant setup — so proxying breaks every seed image on the SPA home page. Keep the alias block shape identical to the `/assets/` block above it. `${SITE_NAME}` is pre-approved in the `envsubst` allowlist at [entrypoint.sh:44](deploy/railway/entrypoint.sh#L44); adding any new variable there is a breaking change for the template.
2. **Sites volume is seeded from a baked-in template only when empty.** The entrypoint copies `/home/frappe/sites-template` into `/home/frappe/frappe-bench/sites` only when `apps.txt` is missing. Once a site is created, a volume remount that loses `<site>/public/files/` will **not** re-trigger seeding, and `after_install`'s skip-guard (see seed-data note above) won't re-extract either. Manual recovery is the only path.
3. **`ADMIN_PASSWORD` is read only on first boot.** [entrypoint.sh:87](deploy/railway/entrypoint.sh#L87) passes it to `bench new-site` once, then ignores the env var forever. To rotate, use `bench --site $SITE_NAME set-admin-password …` inside the container — not the Railway dashboard.
4. **`frappe_side_menu` lives at a *nested* path inside the container.** The Python import `frappe_side_menu.frappe_side_menu.api` resolves to `apps/frappe_side_menu/frappe_side_menu/frappe_side_menu/api.py` (note the doubled directory) — there is also a sibling `apps/frappe_side_menu/frappe_side_menu/api.py` from the bench layout, but it is NOT what gets imported. Hot-patching the outer copy with `docker cp` and restarting workers looks like it should work and silently doesn't. Same shape applies to other py files in this app. Mrvtools doesn't have this nesting; only `frappe_side_menu` does.

## Server-side entry points

Whitelisted endpoints are spread across several files — knowing where each lives prevents accidentally creating a duplicate:

- [mrvtools/api.py](mrvtools/api.py) — `get_approvers()`, `route_user()`, and `get_data(doctype)` (the last is `allow_guest=True` and returns every row of any doctype; audit carefully before adding similar generic fetchers).
- [mrvtools/mrvtools/doctype/mrvfrontend/mrvfrontend.py](mrvtools/mrvtools/doctype/mrvfrontend/mrvfrontend.py) — `get_all()` (`allow_guest=True`) is the SPA home-page loader; it returns the MrvFrontend single doc plus child tables (`knowledge_resource_details`, `knowledge_resource_details2`, `climate_change_division_images`, `add_new_content`, with hidden `whatsNew` entries filtered). Homepage payload shape changes go here.
- [mrvtools/mrvtools/doctype/my_approval/my_approval.py](mrvtools/mrvtools/doctype/my_approval/my_approval.py) — `insert_record()` and `delete_record()` for approval tracking; the doctype itself is also the one referenced by the `My Approval` permission query condition.
- [frappe_side_menu/frappe_side_menu/api.py](frappe_side_menu/frappe_side_menu/api.py) — `get_menulist()` (renders Side Menu / Drill Down Menu / Side Menu With Tab and returns HTML + JSON), `set_default_route()` (the `on_session_creation` handler), and several guest-accessible helpers (`get_all_records`, `get_list`, `get_doctype`).

## Assets and build output

`app_include_css`/`app_include_js` in [mrvtools/hooks.py](mrvtools/hooks.py) reference `/assets/mrvtools/...`, which Frappe serves from `mrvtools/public/`. The Vite build writes into `mrvtools/public/frontend/`, so after a frontend build the desk-injected assets and the SPA bundle coexist under the same `public/` tree.
