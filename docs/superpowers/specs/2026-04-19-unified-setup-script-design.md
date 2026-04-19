# Unified setup script — design

**Status:** Proposed
**Date:** 2026-04-19
**Target file:** [install.sh](../../../install.sh) at the repo root

## Context

The repo ships two Frappe apps (`mrvtools`, `frappe_side_menu`) and a Vue 3 SPA under `frontend/`. A contributor cloning the repo currently has to derive the full install path from [CLAUDE.md](../../../CLAUDE.md) and [README.md](../../../README.md): install system prerequisites (Python, Node, MariaDB, redis, wkhtmltopdf), install `bench`, run `bench init`, create a site, `bench get-app` each app, install and migrate them, patch `site_config.json` with `ignore_csrf` for dev, and run `yarn install && yarn build`. That is five+ documents of implicit knowledge, and a partial failure on any step requires manual resume.

A single `install.sh` at the repo root unifies the bootstrap into one command that works from a clean macOS, Ubuntu, or Windows-via-WSL2 laptop, supports both dev and prod targets, is idempotent (safe to re-run after a failure), and is configured entirely through environment variables so it's scriptable for CI.

Goal: run the app as-is. No refactoring of the two Frappe apps, the frontend, or the existing `setup.py` / `setup_sidebarmenu.py`. The script only orchestrates existing entry points.

## Non-goals

- Native Windows support (WSL2 is supported — see OS detection below).
- Docker/containerized setup (a separate design, not this one).
- Consolidating the two `setup.py` files or changing packaging. Three options were considered (true merge into one Frappe app; colocating `setup_sidebarmenu.py` inside the app dir; no change) and **no change** was chosen — `bench get-app <name> <path>` requires each app's source path to contain a `setup.py` declaring a matching package name, so "one pip manifest + two bench apps" is not achievable without restructuring. The unified `install.sh` provides the single-command install surface; the two packaging files stay as they are.
- Editing any Frappe app code, hooks, or doctypes.
- CI pipeline wiring (the design makes CI *possible* via env vars, but does not add workflows).

## Architecture

One file at the repo root: `install.sh`. Zero runtime dependencies beyond a POSIX shell — everything else (Python, Node, `bench`, `yarn`) is installed by the script itself.

Structure inside the file:

```text
install.sh
├── Shebang + `set -euo pipefail` + usage/help text
├── CONFIG block — env var reads with defaults
├── LOG helpers — info / warn / err / step
├── OS detection — sets $OS to 'macos' or 'ubuntu' (covers WSL2), errs otherwise
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

### OS detection

`$OS` is set by inspecting `uname -s` and `/proc/version`:

- `Darwin` → `macos`
- `Linux` and `/proc/version` contains `microsoft` or `WSL` → `ubuntu` (WSL2 is treated as an Ubuntu variant; tested only against the default `Ubuntu` WSL distro — other distros may work but are not supported)
- `Linux` otherwise with `/etc/os-release` ID=`ubuntu` or `debian` → `ubuntu`
- Anything else → error with a clear message pointing native-Windows users at WSL2.

No helper scripts, no sub-files. Only one new file in the repo; a short pointer is added to [CLAUDE.md](../../../CLAUDE.md).

## Configuration

All configuration is read from environment variables at the top of the script. Users override by exporting before running: `SITE_NAME=mrv.local ./install.sh --dev`.

| Env var | Default | Purpose |
| --- | --- | --- |
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

```text
brew list <pkg> &>/dev/null || brew install <pkg>
```

for each of: `python@3.11`, `node@18`, `yarn`, `mariadb`, `redis`, `wkhtmltopdf`, `pipx`.
Then `brew services start mariadb` and `brew services start redis` (idempotent — brew skips if already started).

**Ubuntu (including WSL2):**

```text
dpkg -s <pkg> &>/dev/null || apt install -y <pkg>
```

for each of: `python3.11`, `python3.11-venv`, `python3-dev`, `mariadb-server`, `redis-server`, `wkhtmltopdf`, `build-essential`, `libssl-dev`, `libffi-dev`, `xvfb`, `libfontconfig`, `pipx`.
Node via NodeSource setup script (only if `node -v` reports a version below `$NODE_VERSION`); yarn via `corepack enable`.

Service startup branches on WSL vs native Linux: WSL2 does not run `systemd` by default, so on WSL the script starts MariaDB and redis via `sudo service mariadb start` and `sudo service redis-server start`; on native Ubuntu it uses `systemctl start mariadb` and `systemctl start redis-server`. Detection reuses the OS check (`/proc/version` WSL marker).

**MariaDB root password:** probe with `mysqladmin ping -u root -p"$MYSQL_ROOT_PASSWORD"`. If the probe succeeds, root is already set and the phase is done. If the probe fails and root has no password set, run `mysqladmin -u root password "$MYSQL_ROOT_PASSWORD"`. If the probe fails and a different password is already set, abort with a clear error telling the user to fix `$MYSQL_ROOT_PASSWORD`.

### `install_bench_cli`

`command -v bench &>/dev/null || pipx install frappe-bench`.

### `init_bench`

```bash
[ -d "$BENCH_DIR" ] || bench init \
  --python "python$PYTHON_VERSION" \
  --frappe-branch "$FRAPPE_BRANCH" \
  "$BENCH_DIR"
```

### `create_site`

From inside `$BENCH_DIR`:

```bash
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

```bash
cd "$MRVTOOLS_SRC/frontend"
yarn install --frozen-lockfile
yarn build
```

Runs in both dev and prod. Dev needs at least one build so `mrvtools/www/frontend.html` exists before `yarn dev` is run — otherwise `/frontend` 404s in the browser while Vite is serving.

### `configure_dev`

No actions beyond printing next-step instructions:

```bash
cd $BENCH_DIR && bench start      # terminal 1
cd $MRVTOOLS_SRC/frontend && yarn dev    # terminal 2
# then open http://$SITE_NAME:8000
```

### `configure_prod`

```bash
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
- **Modified (rename):** ~100 files touched by a `NetZeroLabs` → `NetZeroLabs` rename — details below.

The existing `requirements.txt`, app hooks, and frontend build remain structurally unchanged; the two `setup.py` files stay as separate pip entry points (the author/email metadata inside them is rewritten by the rename step).

## Rename: `NetZeroLabs` → `NetZeroLabs`

A repo-wide find/replace covers every occurrence of the string `NetZeroLabs` (case-insensitive match, case-preserving replacement to `NetZeroLabs`). Occurrences fall into four buckets:

1. **Copyright headers** in ~90 DocType `.py` and `.js` files — `# Copyright (c) 2023, NetZeroLabs and contributors` / `// Copyright (c) 2024, NetZeroLabs and Contributors`. Mechanical replace.
2. **Package metadata:** [setup.py](../../../setup.py) (`author`, `author_email`), [setup_sidebarmenu.py](../../../setup_sidebarmenu.py) (`author`, `author_email`), [mrvtools/hooks.py](../../../mrvtools/hooks.py) (`app_publisher`, `app_email`), [frappe_side_menu/hooks.py](../../../frappe_side_menu/hooks.py) (`app_publisher`, `app_email`).
3. **Email addresses:** `info@netzerolabs.io` in `setup.py` / `mrvtools/hooks.py`, and the already-broken `info@netzerolabs.io` (missing `c`) in `setup_sidebarmenu.py` / `frappe_side_menu/hooks.py`. The rename fixes both addresses and the typo in one pass — rewritten as `info@netzerolabs.io` (lowercase by email convention).
4. **External URLs in `package.json`:** the old Bitbucket URLs point at a repo (`bitbucket.org/NetZeroLabs2019/mrv-tool-custom-app`) that no longer exists. They are rewritten to the current GitHub origin:
   - `repository.url` → `git+https://github.com/rajeshscs/MRV-Solomon-Islands.git`
   - `homepage` → `https://github.com/rajeshscs/MRV-Solomon-Islands#readme`

Implementation approach: a single `sed -i` pass over the tracked files under buckets 1–3, driven by `git ls-files`. `package.json` is rewritten separately (the Bitbucket URL pair is a literal two-line substitution, not driven by the `NetZeroLabs` regex) to avoid collateral damage from replacing `NetZeroLabs2019` with `NetZeroLabs2019`.

Verification: after the rename, `grep -r -i "NetZeroLabs" .` returns zero matches and `grep -r "bitbucket.org/NetZeroLabs2019" .` returns zero matches.

## License: switch to MIT

The repo currently has an inconsistent license declaration:

- [license.txt](../../../license.txt) is a one-line file containing `License: MIT` — it declares MIT but ships no actual license text.
- [package.json](../../../package.json) line 17 declares `"license": "ISC"` — contradicts `license.txt`.
- Source files carry `# Copyright (c) YYYY, NetZeroLabs and contributors` headers with no SPDX notice.

Two changes:

1. **Rewrite `license.txt`** with the full MIT License text. Copyright line: `Copyright (c) 2023-2026 NetZeroLabs and contributors` (aligns with the post-rename copyright string and covers the range of years already present in source headers). Filename stays as-is — renaming to `LICENSE` would ripple through `MANIFEST.in` and is out of scope.
2. **Update `package.json`** line 17: `"license": "ISC"` → `"license": "MIT"`.

No changes to per-file copyright headers beyond the `NetZeroLabs` → `NetZeroLabs` rename already covered above. The root `license.txt` is authoritative for the whole repo; SPDX per-file notices are not being added.

Verification: `license.txt` begins with `MIT License`, contains the standard permission/warranty paragraphs; `jq -r .license package.json` returns `MIT`.
