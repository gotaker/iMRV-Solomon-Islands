# Installation Guide

One command bootstraps a fresh laptop or server into a working MRV Solomon Islands environment. Runs on **macOS**, **Ubuntu**, and **Windows (via WSL2 + Ubuntu)**.

```bash
MYSQL_ROOT_PASSWORD=<pw> ./install.sh --dev     # local development
MYSQL_ROOT_PASSWORD=<pw> ./install.sh --prod    # production server
```

`MYSQL_ROOT_PASSWORD` is the only required variable. Everything else has sensible defaults; override via environment variables.

The script is **idempotent** — re-running after a partial failure picks up where it left off.

## Prerequisites

| OS | Prerequisite |
| --- | --- |
| **macOS** | [Homebrew](https://brew.sh) installed. The script uses `brew` to install Python, Node, MariaDB, redis, wkhtmltopdf, and more. |
| **Ubuntu / WSL2** | `sudo` access. The script uses `apt-get` for system packages and starts MariaDB / redis via `service` (WSL2) or `systemctl` (native). |
| **Windows** | Install [WSL2 with Ubuntu](https://learn.microsoft.com/en-us/windows/wsl/install), then run the script from inside the WSL shell. Native Windows is not supported. |

The script also needs:

- `git` (auto-installed if missing)
- `curl` (present by default on all supported systems)
- Internet access to pull Frappe, npm packages, and the patched wkhtmltopdf `.deb` on Ubuntu

## What the script does

In order:

1. **System packages** — Homebrew/apt installs Python 3.11, Node 18, yarn, MariaDB, redis, wkhtmltopdf, build tools, git, cron.
2. **Patched wkhtmltopdf (Ubuntu/WSL2)** — replaces distro wkhtmltopdf with the Qt-patched build from [wkhtmltopdf/packaging](https://github.com/wkhtmltopdf/packaging/releases); required for PDF export.
3. **MariaDB root password** — probes and sets if not already configured.
4. **Frappe bench CLI** — `pipx install frappe-bench` if not already on `PATH`.
5. **Bench init** — `bench init --frappe-branch version-15` in `$BENCH_DIR` (default `~/frappe-bench`).
6. **Site creation** — `bench new-site` with the MariaDB root password and the Frappe admin password.
7. **Apps** — `bench get-app` + `install-app` for `mrvtools` and `frappe_side_menu`, then `bench migrate`.
8. **Frontend build** — `yarn install && yarn build` in `frontend/`.
9. **Mode-specific finishing:**
   - `--dev`: patches `site_config.json` to set `developer_mode=1` and `ignore_csrf=1`, then prints next-step instructions.
   - `--prod`: enables `dns_multitenant`, runs `bench setup production <user>` (supervisor + nginx), attaches `PROD_DOMAIN`, optionally provisions Let's Encrypt TLS.

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `MYSQL_ROOT_PASSWORD` | **required** | MariaDB root password. Script aborts if unset. |
| `BENCH_DIR` | `$HOME/frappe-bench` | Where `bench init` lives. |
| `FRAPPE_BRANCH` | `version-15` | Frappe branch used by `bench init`. |
| `PYTHON_VERSION` | `3.11` | Python interpreter for the bench venv. |
| `NODE_VERSION` | `18` | Node version; NodeSource repo used on Ubuntu if the shipped Node is older. |
| `SITE_NAME` | `mrv.localhost` | Site created by `bench new-site`. |
| `ADMIN_PASSWORD` | `admin` | Frappe `Administrator` password. |
| `MRVTOOLS_SRC` | this repo's path | Source path passed to `bench get-app mrvtools`. |
| `SIDE_MENU_SRC` | `$MRVTOOLS_SRC/frappe_side_menu` | Source path for `frappe_side_menu`. |
| `SKIP_SYSTEM_DEPS` | `0` | Set to `1` to skip the OS package install phase (CI / re-runs where deps are already known-good). |
| `PROD_USER` | `$USER` | User passed to `bench setup production`. |
| `PROD_DOMAIN` | `demo.imrv.netzerolabs.io` | In `--prod`, the FQDN attached via `bench setup add-domain`. |
| `PROD_ENABLE_TLS` | `0` | In `--prod` with `PROD_DOMAIN` set, run `bench setup lets-encrypt` (Ubuntu only). |
| `DRY_RUN` | `0` | Set to `1` to print what would run, without executing anything. |

## Quick starts

### Developer laptop (macOS or Linux)

```bash
# Clone, cd in, then:
MYSQL_ROOT_PASSWORD=changeme ./install.sh --dev

# Then, in two terminals:
cd ~/frappe-bench && bench start                          # terminal A
cd <repo>/frontend && yarn dev                            # terminal B

# Open http://mrv.localhost:8000
```

### Production server (Ubuntu, with TLS)

```bash
MYSQL_ROOT_PASSWORD=<strong-pw> \
PROD_USER=ubuntu \
PROD_ENABLE_TLS=1 \
./install.sh --prod

# PROD_DOMAIN defaults to demo.imrv.netzerolabs.io.
# For a different FQDN:
MYSQL_ROOT_PASSWORD=<strong-pw> \
PROD_USER=ubuntu \
PROD_DOMAIN=mrv.gov.example \
PROD_ENABLE_TLS=1 \
./install.sh --prod
```

Make sure DNS for `$PROD_DOMAIN` already points at the server before running with `PROD_ENABLE_TLS=1`, otherwise Let's Encrypt validation will fail.

### CI / reproducible installs

```bash
SKIP_SYSTEM_DEPS=1 \
MYSQL_ROOT_PASSWORD=<pw> \
SITE_NAME=ci.local \
./install.sh --dev
```

### Dry run (preview without executing)

```bash
DRY_RUN=1 MYSQL_ROOT_PASSWORD=test ./install.sh --dev
```

Every command the script would run is printed, prefixed with `DRY_RUN:`. Nothing is installed or changed.

## Re-running after a failure

The script is idempotent. Every phase checks state before acting:

- `brew list <pkg>` / `dpkg -s <pkg>` before installing
- `[ -d $BENCH_DIR ]` before `bench init`
- `[ -d sites/$SITE_NAME ]` before `bench new-site`
- `[ -d apps/<app> ]` before `bench get-app`
- `bench --site <site> list-apps` before `install-app`

If a step fails, fix the underlying cause and re-run — completed phases log `--> skipping <thing>: already done` and the script resumes from the first incomplete phase.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `ERR: MYSQL_ROOT_PASSWORD must be set` | Required env var not exported. | `export MYSQL_ROOT_PASSWORD=<pw>` then re-run. |
| `ERR: mariadb root password is set to something different from $MYSQL_ROOT_PASSWORD` | The value you passed doesn't match the current root password. | Pass the correct password, or reset MariaDB root externally. |
| `ERR: Homebrew is required on macOS` | Running on a Mac without Homebrew. | Install from <https://brew.sh> and re-run. |
| `ERR: Unsupported OS` on Windows | Native Windows is not supported. | Install WSL2 + Ubuntu and run the script inside the WSL shell. |
| Site responds `403 CSRF` in dev | Vite dev server running but `ignore_csrf` wasn't set. | The dev path patches `site_config.json` automatically. Confirm with `grep ignore_csrf ~/frappe-bench/sites/mrv.localhost/site_config.json`. |
| Blank `/frontend/*` page | `mrvtools/www/frontend.html` missing. | Re-run the script (or `cd frontend && yarn build`) — the copy-html step must succeed. |
| wkhtmltopdf PDF export breaks | Stock distro `wkhtmltopdf` (unpatched Qt) on Ubuntu. | The script replaces it with the patched `.deb` automatically. Verify with `wkhtmltopdf --version` — output must include `with patched qt`. |

## Verification

After a successful run:

```bash
which bench                                          # pipx-installed bench CLI on PATH
ls ~/frappe-bench/apps                               # frappe, mrvtools, frappe_side_menu
bench --site mrv.localhost list-apps                 # all three apps installed
ls ~/frappe-bench/sites/mrv.localhost                # site_config.json, etc.
wkhtmltopdf --version                                # Ubuntu: must say "with patched qt"
```

## Uninstall

The script does not provide a destroy command. To remove a dev install:

```bash
# drop the bench (includes the site and all fetched apps)
rm -rf ~/frappe-bench

# on macOS, stop and optionally uninstall services
brew services stop mariadb redis
brew uninstall mariadb redis node@18 yarn wkhtmltopdf       # optional

# on Ubuntu
sudo service mariadb stop
sudo service redis-server stop
sudo apt-get remove mariadb-server redis-server             # optional
```

## See also

- [install.sh](install.sh) — the script itself
- [CLAUDE.md](CLAUDE.md) — high-level repo architecture
- [docs/superpowers/specs/2026-04-19-unified-setup-script-design.md](docs/superpowers/specs/2026-04-19-unified-setup-script-design.md) — full design spec
- [docs/superpowers/plans/2026-04-19-install-manual-deltas.md](docs/superpowers/plans/2026-04-19-install-manual-deltas.md) — deltas applied from the upstream SI-iMRV installation manual
