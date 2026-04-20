# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository shape

This repo contains **two Frappe apps** side-by-side plus a **Vue 3 SPA**:

- `mrvtools/` — the main Frappe app (MRV tooling: projects, adaptation, mitigation, GHG inventory, climate finance, reports). Declared in [setup.py](setup.py), version in [mrvtools/__init__.py](mrvtools/__init__.py). Ships two Frappe modules listed in [mrvtools/modules.txt](mrvtools/modules.txt): `Mrvtools` (under [mrvtools/mrvtools/](mrvtools/mrvtools/)) and `GHG Inventory` (under [mrvtools/ghg_inventory/](mrvtools/ghg_inventory/)).
- `frappe_side_menu/` — a second, independent Frappe app providing a custom sidebar/workspace UI. Has its own [setup_sidebarmenu.py](setup_sidebarmenu.py), [hooks.py](frappe_side_menu/hooks.py), and doctypes (`Side Menu`, `Sub Menu`, `Sub Menu Group`, `Side Menu Settings`). It is installed as a separate bench app, not as a subpackage of `mrvtools`.
- `frontend/` — a Vue 3 + Vite + TailwindCSS + Frappe UI SPA that is built into `mrvtools/public/frontend/` and served by Frappe at `/frontend/*`. Served page routes: Home, About, Projects, Climate Change Division, Reports, Support, Knowledge Resource, What's New, Login ([frontend/src/router.js](frontend/src/router.js)).

When working on a change, first identify which of these three layers owns the behavior — they have different build/deploy paths and different entrypoints.

Two pip entry points live at the repo root: [setup.py](setup.py) packages `mrvtools`, [setup_sidebarmenu.py](setup_sidebarmenu.py) packages `frappe_side_menu`. `requirements.txt` is the real dependency manifest; `requirements 2.txt` (note the space in the filename) is a stray duplicate — ignore it.

## Build and run

Frontend dev (proxies to bench on :8000):

```bash
yarn --cwd frontend install     # or: cd frontend && yarn
yarn dev                         # runs `cd frontend && yarn dev` — Vite on :8080
yarn build                       # builds into mrvtools/public/frontend/ and copies index.html → mrvtools/www/frontend.html
```

The build's `copy-html-entry` step (see [frontend/package.json](frontend/package.json)) is what makes `/frontend` resolve in production — Frappe serves `mrvtools/www/frontend.html`. The actual `build` script is `vite build --base=/assets/mrvtools/frontend/ && yarn copy-html-entry` — the `--base` flag, the `copy-html-entry` destination, and the `website_route_rules` / `app_include_*` entries in [mrvtools/hooks.py](mrvtools/hooks.py) all have to stay in sync; editing one without the others breaks asset URLs or the SPA mount.

Dev-server requirement (from [frontend/README.md](frontend/README.md)): add `"ignore_csrf": 1` to `site_config.json` while running Vite on :8080, otherwise CSRF errors block API calls. [frontend/vite.config.js](frontend/vite.config.js) contains a commented-out proxy block pointing at `http://192.168.0.183:8080` — a hint of a past dev-host setup, not active.

[frontend/src/main.js](frontend/src/main.js) wires Frappe-UI with `frappeRequest` as the resource fetcher and registers `Button`/`Card`/`Input` globally; AOS (animate-on-scroll) is initialized in `App.vue`. If a Frappe-UI component looks unresolved, it needs registering here.

There is no CI (`.github/workflows/` is absent) and no enforced linting — only [frontend/.prettierrc.json](frontend/.prettierrc.json) exists and nothing runs it automatically.

For a one-command bootstrap (fresh macOS, Ubuntu, or Windows/WSL2 laptop → working dev or prod install), run [install.sh](install.sh) at the repo root: `MYSQL_ROOT_PASSWORD=<pw> ./install.sh --dev` (or `--prod`). The script is idempotent — it automates exactly the `bench get-app` / `install-app` / `migrate` / `yarn build` sequence documented above, plus OS package install (Homebrew on macOS, apt on Ubuntu/WSL2), `bench init`, `new-site`, and the `ignore_csrf` / `developer_mode` flip for dev. Env vars (`BENCH_DIR`, `SITE_NAME`, `FRAPPE_BRANCH`, `PROD_DOMAIN`, `PROD_ENABLE_TLS`, etc.) override defaults; `DRY_RUN=1` prints what would run without executing it. Prod-only: set `PROD_DOMAIN=<fqdn>` to run `bench setup add-domain`, and `PROD_ENABLE_TLS=1` (Ubuntu only) to provision a Let's Encrypt cert via `bench setup lets-encrypt`. See [docs/superpowers/specs/2026-04-19-unified-setup-script-design.md](docs/superpowers/specs/2026-04-19-unified-setup-script-design.md) for the full spec.

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

There is no standalone Python test harness in this repo — every `test_*.py` lives next to a doctype and depends on the Frappe test runner.

## Continuous integration

CI runs via GitHub Actions. Two workflows:

- [.github/workflows/ci-fast.yml](.github/workflows/ci-fast.yml) — runs on every PR and on pushes to `master`. Three parallel jobs: `frontend-build` (Vite build), `frontend-format` (Prettier `--check` against `frontend/src/**/*.{js,vue,css}`), `python-lint` (ruff on both Frappe apps). Target <2 min.
- [.github/workflows/ci-frappe-tests.yml](.github/workflows/ci-frappe-tests.yml) — runs on PRs targeting `master` and nightly at 02:00 UTC. Spins up MariaDB 10.6 + Redis 7 service containers, runs `bench init`, installs both apps into a fresh `test_site`, then `bench run-tests --app mrvtools` and `--app frappe_side_menu`. On failure, uploads `frappe-bench/logs/` as an artifact; nightly failures also auto-open a GitHub issue labelled `ci-nightly-failure` (the label must exist in the repo).

Design spec: [docs/superpowers/specs/2026-04-19-ci-pipeline-design.md](docs/superpowers/specs/2026-04-19-ci-pipeline-design.md).

Version pins live in both workflow files and in [install.sh](install.sh) — keep them in sync. Bumping Python, Node, or the Frappe branch in `install.sh` requires a matching edit to `ci-frappe-tests.yml` in the same PR.

Branch protection on `master` requires these status checks (configure manually via repo Settings → Branches): `frontend-build`, `frontend-format`, `python-lint`, `frappe-tests`.

Secrets needed: `MARIADB_ROOT_PASSWORD` (any strong password — only used inside the ephemeral MariaDB service container).

## Architecture notes worth knowing before editing

**Routing handoff.** [mrvtools/hooks.py](mrvtools/hooks.py) defines `website_route_rules` mapping `/frontend/<path:app_path>` to the `frontend` web template, and redirects `/` → `/frontend/home`. Inside the SPA, `createWebHistory('/frontend')` takes over. A route that "doesn't work" may be failing at either the Frappe route-rule layer or the Vue router layer — check both. `/login` is also overridden to a `custom_login` web template.

**Seed data on install.** `after_install = "mrvtools.mrvtools.after_install.after_install"` runs three loaders from [mrvtools/mrvtools/after_install.py](mrvtools/mrvtools/after_install.py):
1. `load_master_data` — inserts records for a hard-coded list of ~35 doctypes from JSON files in [mrvtools/master_data/](mrvtools/master_data/). The doctype list is maintained in code; adding a new master-data doctype requires both the JSON file and a line in the `doctype_list`.
2. `load_default_files` — unzips `mrvtools/public/mrv_default_files.zip` into Frappe's File doctype.
3. `load_single_doc` — upserts Single doctypes (Website Settings, Navbar Settings, Side Menu Settings, MrvFrontend).

All three use `ignore_permissions=True` and swallow exceptions into `frappe.log_error`. When install appears to "silently succeed" but data is missing, check the Error Log doctype.

`load_default_files` has a recovery trap: it skips extraction when a `File` DB record with the matching name already exists, **even if the physical file on disk is gone** (see [mrvtools/mrvtools/after_install.py:28](mrvtools/mrvtools/after_install.py#L28)). If seed images 404 after a volume wipe, re-running `load_default_files` is a no-op — you have to unzip `mrv_default_files.zip` directly into `sites/<site>/public/files/`. The Railway container ships without `unzip`, so use `python3 -c "import zipfile; …"` for any extraction work inside it.

**Permission query conditions.** [mrvtools/hooks.py](mrvtools/hooks.py) wires `My Approval` and `Approved User` to `get_query_conditions` functions in their respective doctype modules — these filter list views server-side. Changes to approval visibility belong there, not in client-side JS.

**Doctype conventions.** Doctypes ending in `_childtable` are Frappe child tables and must be embedded in a parent doctype; they are not independently listable. Doctypes ending in `_master_list` are reference/lookup tables seeded by `load_master_data`. The `edited_*` doctypes (e.g. `edited_project_details`, `edited_ghg_inventory_details`) appear to be revision/draft variants of their base doctypes — treat them as paired.

**Frontend data layer.** The SPA uses Frappe UI's resource pattern; `session` lives at [frontend/src/data/session.js](frontend/src/data/session.js) and is consulted by the router guard in [frontend/src/router.js](frontend/src/router.js) to gate `/account/login`. Note the router guard references `userResource` without importing it — bugs in auth redirect flow likely originate here.

**Two hooks.py files.** `mrvtools/hooks.py` and `frappe_side_menu/hooks.py` are independent — each is read by Frappe for its own app. Don't consolidate.

**Post-login redirect.** [frappe_side_menu/hooks.py](frappe_side_menu/hooks.py) sets `on_session_creation = "frappe_side_menu.frappe_side_menu.api.set_default_route"`, which hardcodes `home_page = "/app/" + route_logo` (see [frappe_side_menu/frappe_side_menu/api.py:181](frappe_side_menu/frappe_side_menu/api.py#L181)). This means every logged-in user — including System Users like `Administrator` — lands on the Frappe desk, not the SPA. This is intentional; the SPA at `/frontend/home` is the public-facing site, reachable without login. Login-redirect bugs usually originate here, not in `mrvtools/hooks.py`.

**Desk customisations are narrow.** `mrvtools/hooks.py` injects `doctype_js` / `doctype_list_js` only for the `User` doctype; `frappe_side_menu/hooks.py` injects `doctype_list_js` only for `Project`. Most `doc_events` / `scheduler_events` / `override_doctype_class` lines in both files are commented-out stubs — don't read them as active wiring.

**Railway deployment.** Staging/demo runs on Railway using the image built from [Dockerfile](Dockerfile), launched by [deploy/railway/entrypoint.sh](deploy/railway/entrypoint.sh), fronted by [deploy/railway/nginx.conf.template](deploy/railway/nginx.conf.template). Operational runbook: [deploy/railway/README.md](deploy/railway/README.md). Three non-obvious invariants:

1. **`/files/` must be an nginx `alias`, not a `proxy_pass` to gunicorn.** Frappe's WSGI handler returns 404 for public File URLs in this single-tenant setup — so proxying breaks every seed image on the SPA home page. Keep the alias block shape identical to the `/assets/` block above it. `${SITE_NAME}` is pre-approved in the `envsubst` allowlist at [entrypoint.sh:44](deploy/railway/entrypoint.sh#L44); adding any new variable there is a breaking change for the template.
2. **Sites volume is seeded from a baked-in template only when empty.** The entrypoint copies `/home/frappe/sites-template` into `/home/frappe/frappe-bench/sites` only when `apps.txt` is missing. Once a site is created, a volume remount that loses `<site>/public/files/` will **not** re-trigger seeding, and `after_install`'s skip-guard (see seed-data note above) won't re-extract either. Manual recovery is the only path.
3. **`ADMIN_PASSWORD` is read only on first boot.** [entrypoint.sh:87](deploy/railway/entrypoint.sh#L87) passes it to `bench new-site` once, then ignores the env var forever. To rotate, use `bench --site $SITE_NAME set-admin-password …` inside the container — not the Railway dashboard.

## Server-side entry points

Whitelisted endpoints are spread across several files — knowing where each lives prevents accidentally creating a duplicate:

- [mrvtools/api.py](mrvtools/api.py) — `get_approvers()`, `route_user()`, and `get_data(doctype)` (the last is `allow_guest=True` and returns every row of any doctype; audit carefully before adding similar generic fetchers).
- [mrvtools/mrvtools/doctype/mrvfrontend/mrvfrontend.py](mrvtools/mrvtools/doctype/mrvfrontend/mrvfrontend.py) — `get_all()` (`allow_guest=True`) is the SPA home-page loader; it returns the MrvFrontend single doc plus child tables (`knowledge_resource_details`, `knowledge_resource_details2`, `climate_change_division_images`, `add_new_content`, with hidden `whatsNew` entries filtered). Homepage payload shape changes go here.
- [mrvtools/mrvtools/doctype/my_approval/my_approval.py](mrvtools/mrvtools/doctype/my_approval/my_approval.py) — `insert_record()` and `delete_record()` for approval tracking; the doctype itself is also the one referenced by the `My Approval` permission query condition.
- [frappe_side_menu/frappe_side_menu/api.py](frappe_side_menu/frappe_side_menu/api.py) — `get_menulist()` (renders Side Menu / Drill Down Menu / Side Menu With Tab and returns HTML + JSON), `set_default_route()` (the `on_session_creation` handler), and several guest-accessible helpers (`get_all_records`, `get_list`, `get_doctype`).

## Assets and build output

`app_include_css`/`app_include_js` in [mrvtools/hooks.py](mrvtools/hooks.py) reference `/assets/mrvtools/...`, which Frappe serves from `mrvtools/public/`. The Vite build writes into `mrvtools/public/frontend/`, so after a frontend build the desk-injected assets and the SPA bundle coexist under the same `public/` tree.
