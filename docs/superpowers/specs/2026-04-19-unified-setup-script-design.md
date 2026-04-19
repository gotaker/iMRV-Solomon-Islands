# Unified setup script — design

**Status:** Proposed
**Date:** 2026-04-19
**Target file:** [install.sh](../../../install.sh) at the repo root

## Context

The repo ships two Frappe apps (`mrvtools`, `frappe_side_menu`) and a Vue 3 SPA under `frontend/`. A contributor cloning the repo currently has to derive the full install path from [CLAUDE.md](../../../CLAUDE.md) and [README.md](../../../README.md): install system prerequisites (Python, Node, MariaDB, redis, wkhtmltopdf), install `bench`, run `bench init`, create a site, `bench get-app` each app, install and migrate them, patch `site_config.json` with `ignore_csrf` for dev, and run `yarn install && yarn build`. That is five+ documents of implicit knowledge, and a partial failure on any step requires manual resume.

A single `install.sh` at the repo root unifies the bootstrap into one command that works from a clean macOS or Ubuntu laptop, supports both dev and prod targets, is idempotent (safe to re-run after a failure), and is configured entirely through environment variables so it's scriptable for CI.

Goal: run the app as-is. No refactoring of the two Frappe apps, the frontend, or the existing `setup.py` / `setup_sidebarmenu.py`. The script only orchestrates existing entry points.

## Non-goals

- Windows support.
- Docker/containerized setup (a separate design, not this one).
- Consolidating the two `setup.py` files or changing packaging.
- Editing any Frappe app code, hooks, or doctypes.
- CI pipeline wiring (the design makes CI *possible* via env vars, but does not add workflows).

## Architecture

One file at the repo root: `install.sh`. Zero runtime dependencies beyond a POSIX shell — everything else (Python, Node, `bench`, `yarn`) is installed by the script itself.

Structure inside the file:

```
install.sh
├── Shebang + `set -euo pipefail` + usage/help text
├── CONFIG block — env var reads with defaults
├── LOG helpers — info / warn / err / step
├── OS detection — sets $OS to 'macos' or 'ubuntu', errs otherwise
├── Per-phase functions (each idempotent, each logs its step):
│     install_system_deps()
│     install_bench_cli()
│     init_bench()
│     create_site()
│     get_and_install_apps()
│     patch_site_config()      # dev only
│     build_frontend()
│     configure_dev()
│     configure_prod()
├── parse_args()                # --dev | --prod | --help
└── main()                      # dispatches phases, branches dev/prod at the end
```

No helper scripts, no sub-files. Only one new file in the repo; a short pointer is added to [CLAUDE.md](../../../CLAUDE.md).

## Configuration

All configuration is read from environment variables at the top of the script. Users override by exporting before running: `SITE_NAME=mrv.local ./install.sh --dev`.

| Env var | Default | Purpose |
|---|---|---|
| `BENCH_DIR` | `$HOME/frappe-bench` | Where `bench init` lives |
| `FRAPPE_BRANCH` | `version-15` | Frappe branch passed to `bench init` |
| `PYTHON_VERSION` | `3.11` | Python used for the bench venv |
| `NODE_VERSION` | `18` | Node used for `bench init` |
| `SITE_NAME` | `mrv.localhost` | Site to create |
| `ADMIN_PASSWORD` | `admin` | Frappe admin password |
| `MYSQL_ROOT_PASSWORD` | *(required — script errors if unset)* | MariaDB root password |
| `MRVTOOLS_SRC` | *auto — repo root containing `install.sh`* | Path passed to `bench get-app mrvtools` |
| `SIDE_MENU_SRC` | `$MRVTOOLS_SRC/frappe_side_menu` | Path passed to `bench get-app frappe_side_menu` |
| `SKIP_SYSTEM_DEPS` | `0` | Set to `1` to skip OS package install (CI / re-runs) |
| `PROD_USER` | `$USER` | User passed to `bench setup production <user>` (prod only) |

`MYSQL_ROOT_PASSWORD` is the only required variable — every other default is safe for a local dev install. The script validates its presence before doing any work.

Exactly one of `--dev` / `--prod` must be passed. Passing neither, both, or any other flag causes `--help` to print and the script to exit non-zero.

## Phase breakdown

Each phase is idempotent: it checks state before acting and logs `--> skipping <thing>: already done` when it short-circuits.

### `install_system_deps`

Branches on `$OS`. Skipped entirely if `SKIP_SYSTEM_DEPS=1`.

**macOS:**
```
brew list <pkg> &>/dev/null || brew install <pkg>
```
for each of: `python@3.11`, `node@18`, `yarn`, `mariadb`, `redis`, `wkhtmltopdf`, `pipx`.
Then `brew services start mariadb` and `brew services start redis` (idempotent — brew skips if already started).

**Ubuntu:**
```
dpkg -s <pkg> &>/dev/null || apt install -y <pkg>
```
for each of: `python3.11`, `python3.11-venv`, `python3-dev`, `mariadb-server`, `redis-server`, `wkhtmltopdf`, `build-essential`, `libssl-dev`, `libffi-dev`, `xvfb`, `libfontconfig`, `pipx`.
Node via NodeSource setup script (only if `node -v` reports a version below `$NODE_VERSION`); yarn via `corepack enable`.
`systemctl start mariadb` and `systemctl start redis-server`.

**MariaDB root password:** probe with `mysqladmin ping -u root -p"$MYSQL_ROOT_PASSWORD"`. If the probe succeeds, root is already set and the phase is done. If the probe fails and root has no password set, run `mysqladmin -u root password "$MYSQL_ROOT_PASSWORD"`. If the probe fails and a different password is already set, abort with a clear error telling the user to fix `$MYSQL_ROOT_PASSWORD`.

### `install_bench_cli`

`command -v bench &>/dev/null || pipx install frappe-bench`.

### `init_bench`

```
[ -d "$BENCH_DIR" ] || bench init \
  --python "python$PYTHON_VERSION" \
  --frappe-branch "$FRAPPE_BRANCH" \
  "$BENCH_DIR"
```

### `create_site`

From inside `$BENCH_DIR`:
```
[ -d "sites/$SITE_NAME" ] || bench new-site \
  --mariadb-root-password "$MYSQL_ROOT_PASSWORD" \
  --admin-password "$ADMIN_PASSWORD" \
  "$SITE_NAME"
```

### `get_and_install_apps`

For each pair `(app_name, source_path)` in `(mrvtools, $MRVTOOLS_SRC)` and `(frappe_side_menu, $SIDE_MENU_SRC)`:

1. `[ -d "apps/<app>" ] || bench get-app <app> "<source>"`
2. If `bench --site $SITE_NAME list-apps` does not include `<app>`, then `bench --site $SITE_NAME install-app <app>`.

After both apps are installed, run once: `bench --site $SITE_NAME migrate`.

### `patch_site_config` *(dev only)*

Inline `python3 -c` loads `sites/$SITE_NAME/site_config.json`, sets `ignore_csrf = 1` and `developer_mode = 1`, writes back only if the file changed. Native JSON handling avoids bash string-munging of a JSON file.

### `build_frontend`

```
cd "$MRVTOOLS_SRC/frontend"
yarn install --frozen-lockfile
yarn build
```
Runs in both dev and prod. Dev needs at least one build so `mrvtools/www/frontend.html` exists before `yarn dev` is run — otherwise `/frontend` 404s in the browser while Vite is serving.

### `configure_dev`

No actions beyond printing next-step instructions:

```
cd $BENCH_DIR && bench start      # terminal 1
cd $MRVTOOLS_SRC/frontend && yarn dev    # terminal 2
# then open http://$SITE_NAME:8000
```

### `configure_prod`

```
sudo bench setup production "$PROD_USER"
bench --site "$SITE_NAME" set-config developer_mode 0
bench --site "$SITE_NAME" set-config ignore_csrf 0
```

The explicit `ignore_csrf 0` handles the case where the same install is later switched from dev to prod — `patch_site_config` would have set it to `1` on the earlier dev run, and prod must not leave it on.

## Flow

`main()` runs these in order:

1. `install_system_deps`       *(both)*
2. `install_bench_cli`          *(both)*
3. `init_bench`                 *(both)*
4. `create_site`                *(both)*
5. `get_and_install_apps`       *(both, includes `migrate`)*
6. `build_frontend`             *(both)*
7. Dev branch: `patch_site_config` → `configure_dev`
   Prod branch: `configure_prod`

## Error handling & logging

- `set -euo pipefail` plus an `ERR` trap that prints the failing line number and the current phase before exiting non-zero.
- Each phase logs `==> <phase name>` on entry via a `step` helper.
- Idempotent skips log `--> skipping <thing>: already done`.
- No retry loops, no partial-failure rollback. A failed run is fixed by the operator and resumed by re-running the script — idempotency is what makes resume safe.
- All output goes to stdout/stderr. No log file written by the script itself; the user pipes to `tee` if they want one.

## Testing

Three layers, from cheapest to most expensive:

1. **Syntax + lint** *(required before landing)* — `bash -n install.sh` and `shellcheck install.sh` run locally. Catches the majority of scripting bugs.
2. **Dry-run smoke test** *(required before landing)* — a `DRY_RUN=1` env var that short-circuits every `brew`/`apt`/`bench`/`yarn`/`systemctl`/`mysqladmin` call to `echo` the command instead of executing it. Verifies the control flow on any machine, including the reviewer's, without side effects.
3. **End-to-end in a clean container** *(recommended)* — spin up a fresh Ubuntu 22.04 Docker container, run `MYSQL_ROOT_PASSWORD=test ./install.sh --dev`, verify the site comes up, then re-run the script and confirm every phase logs `--> skipping` (proves idempotency). macOS path has to be tested on a real Mac.

## Files touched

- **New:** `install.sh` at the repo root.
- **Modified:** [CLAUDE.md](../../../CLAUDE.md) — add one paragraph under "Build and run" pointing contributors at `install.sh` as the unified entry point and noting that the documented `bench`/`yarn` sequence is what the script automates.

No other files are touched. The existing `setup.py`, `setup_sidebarmenu.py`, `requirements.txt`, app hooks, and frontend build remain as they are.
