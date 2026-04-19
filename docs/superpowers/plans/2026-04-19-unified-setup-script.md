# Unified Setup Script Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap a fresh macOS, Ubuntu, or Windows-via-WSL2 laptop into a working MRV Solomon Islands dev or prod environment with a single command, while also relicensing the repo to MIT and renaming the legacy `NetZeroLabs` vendor string to `NetZeroLabs`.

**Architecture:** One idempotent bash script (`install.sh`) at the repo root orchestrates every install phase: OS package install → `bench` CLI → `bench init` → `new-site` → `get-app`/`install-app` for both Frappe apps → `yarn build` → dev/prod finalization. Zero runtime dependencies beyond a POSIX shell. All configuration via environment variables. Separate mechanical passes handle the `NetZeroLabs` → `NetZeroLabs` rename, the Bitbucket → GitHub URL update, and the MIT license rewrite.

**Tech Stack:** Bash, `shellcheck`, Python 3 (inline JSON edits only), Frappe bench CLI, `yarn`, `vite`, `sed`.

**Spec:** [docs/superpowers/specs/2026-04-19-unified-setup-script-design.md](../specs/2026-04-19-unified-setup-script-design.md)

**Working directory note:** The repo already has uncommitted work (`CLAUDE.md`, `frappe_side_menu/`, `setup_sidebarmenu.py`, `requirements 2.txt`, modified `.gitignore` / `MANIFEST.in` / `README.md`) that was part of the "initial commit" preparation. Leave that alone — this plan's commits are strictly additive to what is already staged-but-unclean on `master`.

---

## Task 1: Relicense — rewrite `license.txt` with full MIT text

**Files:**

- Modify: `license.txt`

- [ ] **Step 1: Replace `license.txt` with the full MIT License text**

Overwrite the entire contents of `license.txt` with:

```text
MIT License

Copyright (c) 2023-2026 NetZeroLabs and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Verify contents**

Run: `head -1 license.txt && wc -l license.txt`
Expected: First line is `MIT License`, total line count is between 18 and 25.

- [ ] **Step 3: Commit**

```bash
git add license.txt
git commit -m "chore: relicense under MIT with full license text"
```

---

## Task 2: Update `package.json` — MIT license field and GitHub URLs

**Files:**

- Modify: `package.json` (lines 13, 17, 18)

- [ ] **Step 1: Read current contents**

Run: `cat package.json`
Confirm lines 13, 17, 18 currently read:

```json
    "url": "git+ssh://git@bitbucket.org/NetZeroLabs2019/mrv-tool-custom-app.git"
  "license": "ISC",
  "homepage": "https://bitbucket.org/NetZeroLabs2019/mrv-tool-custom-app#readme"
```

- [ ] **Step 2: Apply three literal replacements**

Replace the three lines with:

```json
    "url": "git+https://github.com/gotaker/iMRV-Solomon-Islands.git"
  "license": "MIT",
  "homepage": "https://github.com/gotaker/iMRV-Solomon-Islands#readme"
```

Preserve surrounding JSON structure (commas, braces, indentation) exactly.

- [ ] **Step 3: Verify JSON is valid and fields are correct**

Run: `python3 -c 'import json; d=json.load(open("package.json")); print(d["license"], d["repository"]["url"], d["homepage"])'`
Expected: `MIT git+https://github.com/gotaker/iMRV-Solomon-Islands.git https://github.com/gotaker/iMRV-Solomon-Islands#readme`

- [ ] **Step 4: Verify no bitbucket references remain in package.json**

Run: `grep -c bitbucket package.json || true`
Expected: `0`

- [ ] **Step 5: Commit**

```bash
git add package.json
git commit -m "chore: update package.json to MIT license and current GitHub origin"
```

---

## Task 3: Rename `NetZeroLabs` → `NetZeroLabs` across the repo

**Files:**

- Modify: every file (tracked or untracked) under the repo root that contains `NetZeroLabs` (case-insensitive). Expected ~100 files. `package.json` is excluded — it was already handled in Task 2 and its `NetZeroLabs2019` substring must not become `NetZeroLabs2019`.

**Important:** the repo already has pre-existing uncommitted work (`CLAUDE.md`, `setup_sidebarmenu.py`, `frappe_side_menu/`, modified `.gitignore` / `MANIFEST.in` / `README.md`, and `requirements 2.txt`) that is NOT part of this plan. The commands below stage only files the rename actually touched, so that pre-existing dirty state is left exactly as it was.

- [ ] **Step 1: Snapshot the set of files to rewrite**

Run, from the repo root:

```bash
grep -r -l -i "NetZeroLabs" . \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  --exclude-dir=__pycache__ \
  --exclude="package.json" \
  > /tmp/NetZeroLabs_files.txt
wc -l /tmp/NetZeroLabs_files.txt
```

Expected: a positive count (~100). Save this list — the subsequent steps operate on exactly these files.

- [ ] **Step 2: Verify `package.json` is already clean (from Task 2)**

Run: `grep -c NetZeroLabs package.json || true`
Expected: `0`. If non-zero, Task 2 was not fully applied — fix before continuing.

- [ ] **Step 3: First pass — rewrite email forms (fix `.om` typo, lowercase both variants)**

Run:

```bash
xargs -a /tmp/NetZeroLabs_files.txt sed -i.bak -E 's/NetZeroLabs\.om/netzerolabs.io/g; s/NetZeroLabs\.com/netzerolabs.io/g'
```

Both GNU sed (Linux) and BSD sed (macOS) accept `-i.bak`; the `.bak` files are cleaned up in step 6.

- [ ] **Step 4: Second pass — rewrite remaining bare `NetZeroLabs` → `NetZeroLabs`**

Run:

```bash
xargs -a /tmp/NetZeroLabs_files.txt sed -i.bak 's/NetZeroLabs/NetZeroLabs/g'
```

- [ ] **Step 5: Verify no `NetZeroLabs` references remain**

Run:

```bash
grep -r -i -l NetZeroLabs . \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  --exclude-dir=__pycache__ \
  || echo CLEAN
```

Expected: `CLEAN`.

- [ ] **Step 6: Clean up `.bak` files left by sed**

Run: `find . -name '*.bak' -type f -not -path './.git/*' -delete`

- [ ] **Step 7: Spot-check two files**

Run: `head -1 mrvtools/mrvtools/doctype/my_approval/my_approval.py`
Expected: `# Copyright (c) 2024, NetZeroLabs and contributors`

Run: `grep -E '^(app_publisher|app_email)' mrvtools/hooks.py`
Expected output contains `app_publisher = "NetZeroLabs"` and `app_email = "info@netzerolabs.io"`.

- [ ] **Step 8: Stage only the files the rename touched**

Run: `xargs -a /tmp/NetZeroLabs_files.txt git add --`

This stages both previously-tracked-and-modified files and untracked files that the rename rewrote, while leaving all unrelated pre-existing uncommitted work alone. Do NOT use `git add -A`.

- [ ] **Step 9: Verify staged set matches expectation**

Run: `git diff --cached --name-only | wc -l`
Expected: within a few of the line count from Step 1. If dramatically lower, investigate.

- [ ] **Step 10: Commit**

```bash
git commit -m "chore: rename NetZeroLabs -> NetZeroLabs across the repo"
```

---

## Task 4: Scaffold `install.sh` — header, config, logging, OS detection, arg parsing

**Files:**

- Create: `install.sh`

- [ ] **Step 1: Create `install.sh` with the full skeleton**

Write the following to `install.sh`:

```bash
#!/usr/bin/env bash
# install.sh — unified bootstrap for MRV Solomon Islands
# See docs/superpowers/specs/2026-04-19-unified-setup-script-design.md
set -euo pipefail

# --- Usage ---------------------------------------------------------------
usage() {
  cat <<'EOF'
Usage: install.sh [--dev | --prod] [--help]

Bootstraps a fresh macOS, Ubuntu, or Windows-via-WSL2 laptop into a working
mrvtools + frappe_side_menu + frontend environment.

Modes:
  --dev    Local development environment (Vite dev server, ignore_csrf enabled)
  --prod   Production environment (supervisor + nginx via bench setup production)

Environment variables (defaults in parens):
  BENCH_DIR               ($HOME/frappe-bench)  Where bench init lives
  FRAPPE_BRANCH           (version-15)          Frappe branch for bench init
  PYTHON_VERSION          (3.11)                Python for bench venv
  NODE_VERSION            (18)                  Node for bench init
  SITE_NAME               (mrv.localhost)       Site to create
  ADMIN_PASSWORD          (admin)               Frappe admin password
  MYSQL_ROOT_PASSWORD     (REQUIRED)            MariaDB root password
  MRVTOOLS_SRC            (auto)                Repo path for bench get-app mrvtools
  SIDE_MENU_SRC           (auto)                Repo path for bench get-app frappe_side_menu
  SKIP_SYSTEM_DEPS        (0)                   Set to 1 to skip OS package install
  PROD_USER               ($USER)               User for bench setup production
  DRY_RUN                 (0)                   Set to 1 to echo commands instead of running
EOF
}

# --- Config --------------------------------------------------------------
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
BENCH_DIR="${BENCH_DIR:-$HOME/frappe-bench}"
FRAPPE_BRANCH="${FRAPPE_BRANCH:-version-15}"
PYTHON_VERSION="${PYTHON_VERSION:-3.11}"
NODE_VERSION="${NODE_VERSION:-18}"
SITE_NAME="${SITE_NAME:-mrv.localhost}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-}"
MRVTOOLS_SRC="${MRVTOOLS_SRC:-$SCRIPT_DIR}"
SIDE_MENU_SRC="${SIDE_MENU_SRC:-$MRVTOOLS_SRC/frappe_side_menu}"
SKIP_SYSTEM_DEPS="${SKIP_SYSTEM_DEPS:-0}"
PROD_USER="${PROD_USER:-${USER:-root}}"
DRY_RUN="${DRY_RUN:-0}"

MODE=""
OS=""
IS_WSL=0
CURRENT_PHASE=""

# --- Logging -------------------------------------------------------------
step() { CURRENT_PHASE="$1"; printf '\n==> %s\n' "$1" >&2; }
info() { printf '    %s\n' "$*" >&2; }
skip() { printf '--> skipping %s: already done\n' "$*" >&2; }
warn() { printf 'WARN: %s\n' "$*" >&2; }
err()  { printf 'ERR:  %s\n' "$*" >&2; }

trap 'err "phase [${CURRENT_PHASE:-startup}] failed at line $LINENO"; exit 1' ERR

# --- Command runner (honours DRY_RUN) ------------------------------------
run() {
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: %s\n' "$*"
  else
    "$@"
  fi
}

# Shell-eval variant for pipelines that need shell metacharacters.
run_sh() {
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: %s\n' "$*"
  else
    bash -c "$*"
  fi
}

# --- OS detection --------------------------------------------------------
detect_os() {
  local uname_s
  uname_s="$(uname -s)"
  case "$uname_s" in
    Darwin)
      OS=macos
      ;;
    Linux)
      if [[ -r /proc/version ]] && grep -qiE 'microsoft|wsl' /proc/version; then
        OS=ubuntu; IS_WSL=1
      elif [[ -r /etc/os-release ]] && grep -qE '^ID=(ubuntu|debian)' /etc/os-release; then
        OS=ubuntu
      else
        err "Unsupported Linux distribution (only Ubuntu/Debian and WSL2 are supported)"
        exit 1
      fi
      ;;
    *)
      err "Unsupported OS: $uname_s. On Windows, install WSL2 with Ubuntu and re-run."
      exit 1
      ;;
  esac
  info "detected OS: $OS (WSL=$IS_WSL)"
}

# --- Phase stubs (filled in by later tasks) ------------------------------
install_system_deps()  { step "install_system_deps"; :; }
install_bench_cli()    { step "install_bench_cli"; :; }
init_bench()           { step "init_bench"; :; }
create_site()          { step "create_site"; :; }
get_and_install_apps() { step "get_and_install_apps"; :; }
patch_site_config()    { step "patch_site_config"; :; }
build_frontend()       { step "build_frontend"; :; }
configure_dev()        { step "configure_dev"; :; }
configure_prod()       { step "configure_prod"; :; }

# --- Arg parsing ---------------------------------------------------------
parse_args() {
  if [[ $# -eq 0 ]]; then usage; exit 2; fi
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dev)     MODE=dev;  shift ;;
      --prod)    MODE=prod; shift ;;
      --help|-h) usage; exit 0 ;;
      *)         err "Unknown argument: $1"; usage; exit 2 ;;
    esac
  done
  if [[ -z "$MODE" ]]; then
    err "One of --dev or --prod is required"; usage; exit 2
  fi
}

# --- Main ----------------------------------------------------------------
main() {
  parse_args "$@"
  detect_os

  if [[ -z "${MYSQL_ROOT_PASSWORD:-}" ]]; then
    err "MYSQL_ROOT_PASSWORD must be set (export MYSQL_ROOT_PASSWORD=...)"
    exit 2
  fi

  install_system_deps
  install_bench_cli
  init_bench
  create_site
  get_and_install_apps
  build_frontend

  if [[ "$MODE" == "dev" ]]; then
    patch_site_config
    configure_dev
  else
    configure_prod
  fi

  printf '\n==> install.sh finished (mode=%s)\n' "$MODE" >&2
}

main "$@"
```

- [ ] **Step 2: Make executable**

Run: `chmod +x install.sh`

- [ ] **Step 3: Syntax check**

Run: `bash -n install.sh`
Expected: no output, exit 0.

- [ ] **Step 4: Shellcheck**

Run: `shellcheck install.sh || true`
Expected: no errors. Warnings permitted but read them. (If `shellcheck` is not installed, install it via `brew install shellcheck` or `apt install shellcheck`.)

- [ ] **Step 5: Smoke-test `--help`**

Run: `./install.sh --help`
Expected: prints the usage block; exit 0.

- [ ] **Step 6: Smoke-test missing-flag behaviour**

Run: `./install.sh; echo "exit=$?"`
Expected: prints usage to stderr; prints `exit=2`.

- [ ] **Step 7: Smoke-test DRY_RUN flow (phase stubs only for now)**

Run: `DRY_RUN=1 MYSQL_ROOT_PASSWORD=test ./install.sh --dev`
Expected output contains all of these `==>` header lines in order:

```text
==> install_system_deps
==> install_bench_cli
==> init_bench
==> create_site
==> get_and_install_apps
==> build_frontend
==> patch_site_config
==> configure_dev
==> install.sh finished (mode=dev)
```

- [ ] **Step 8: Commit**

```bash
git add install.sh
git commit -m "feat: scaffold install.sh with OS detection, arg parsing, and phase stubs"
```

---

## Task 5: Implement `install_system_deps` (macOS, Ubuntu/WSL, MariaDB root password)

**Files:**

- Modify: `install.sh` (replace the `install_system_deps() { step "install_system_deps"; :; }` stub)

- [ ] **Step 1: Replace the stub with the full implementation**

In `install.sh`, find the line:

```bash
install_system_deps()  { step "install_system_deps"; :; }
```

Replace it with:

```bash
install_system_deps() {
  step "install_system_deps"
  if [[ "$SKIP_SYSTEM_DEPS" == "1" ]]; then
    skip "system deps: SKIP_SYSTEM_DEPS=1"
    return
  fi
  if [[ "$OS" == "macos" ]]; then
    _install_system_deps_macos
  else
    _install_system_deps_ubuntu
  fi
  _ensure_mariadb_root_password
}

_install_system_deps_macos() {
  if ! command -v brew &>/dev/null; then
    err "Homebrew is required on macOS. Install from https://brew.sh and re-run."
    exit 1
  fi
  local pkgs=(python@3.11 node@18 yarn mariadb redis wkhtmltopdf pipx)
  local pkg
  for pkg in "${pkgs[@]}"; do
    if brew list "$pkg" &>/dev/null; then
      skip "brew $pkg"
    else
      run brew install "$pkg"
    fi
  done
  run brew services start mariadb
  run brew services start redis
}

_install_system_deps_ubuntu() {
  run sudo apt-get update
  local pkgs=(python3.11 python3.11-venv python3-dev mariadb-server redis-server
              wkhtmltopdf build-essential libssl-dev libffi-dev xvfb libfontconfig pipx)
  local pkg
  for pkg in "${pkgs[@]}"; do
    if dpkg -s "$pkg" &>/dev/null; then
      skip "apt $pkg"
    else
      run sudo apt-get install -y "$pkg"
    fi
  done

  # Node via NodeSource if missing or too old
  local current_major=0
  if command -v node &>/dev/null; then
    current_major="$(node -v | sed -E 's/^v([0-9]+).*/\1/')"
  fi
  if [[ "$current_major" -lt "$NODE_VERSION" ]]; then
    run_sh "curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -"
    run sudo apt-get install -y nodejs
  else
    skip "node (current v$current_major >= v$NODE_VERSION)"
  fi
  run sudo corepack enable

  if [[ "$IS_WSL" == "1" ]]; then
    run sudo service mariadb start
    run sudo service redis-server start
  else
    run sudo systemctl start mariadb
    run sudo systemctl start redis-server
  fi
}

_ensure_mariadb_root_password() {
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: verify/set mariadb root password\n'
    return
  fi
  if mysqladmin ping -u root -p"$MYSQL_ROOT_PASSWORD" &>/dev/null; then
    skip "mariadb root password already matches"
  elif mysqladmin ping -u root &>/dev/null; then
    info "setting mariadb root password"
    mysqladmin -u root password "$MYSQL_ROOT_PASSWORD"
  else
    err "mariadb root password is set to something different from \$MYSQL_ROOT_PASSWORD"
    exit 1
  fi
}
```

- [ ] **Step 2: Syntax check**

Run: `bash -n install.sh`
Expected: no output, exit 0.

- [ ] **Step 3: Shellcheck**

Run: `shellcheck install.sh`
Expected: no errors.

- [ ] **Step 4: DRY_RUN smoke test — verify the correct branch runs**

Run: `DRY_RUN=1 MYSQL_ROOT_PASSWORD=test ./install.sh --dev 2>&1 | head -60`

Expected on macOS: output contains `DRY_RUN: brew install …` lines for each package (or `skipping brew <pkg>` if already installed) and `DRY_RUN: brew services start mariadb`.
Expected on Ubuntu/WSL: output contains `DRY_RUN: sudo apt-get install -y …` lines and either `DRY_RUN: sudo service mariadb start` (WSL) or `DRY_RUN: sudo systemctl start mariadb` (native).

- [ ] **Step 5: Commit**

```bash
git add install.sh
git commit -m "feat(install.sh): implement install_system_deps for macOS and Ubuntu/WSL"
```

---

## Task 6: Implement `install_bench_cli`, `init_bench`, `create_site`

**Files:**

- Modify: `install.sh` (replace three stubs)

- [ ] **Step 1: Replace the three stubs**

In `install.sh`, find the three lines:

```bash
install_bench_cli()    { step "install_bench_cli"; :; }
init_bench()           { step "init_bench"; :; }
create_site()          { step "create_site"; :; }
```

Replace them with:

```bash
install_bench_cli() {
  step "install_bench_cli"
  if command -v bench &>/dev/null; then
    skip "bench CLI already on PATH"
    return
  fi
  run pipx install frappe-bench
  # pipx installs into ~/.local/bin which may not be on PATH in this shell.
  if ! command -v bench &>/dev/null && [[ -x "$HOME/.local/bin/bench" ]]; then
    export PATH="$HOME/.local/bin:$PATH"
    info "prepended \$HOME/.local/bin to PATH for this session"
  fi
}

init_bench() {
  step "init_bench"
  if [[ -d "$BENCH_DIR" ]]; then
    skip "bench directory exists at $BENCH_DIR"
    return
  fi
  run bench init \
    --python "python$PYTHON_VERSION" \
    --frappe-branch "$FRAPPE_BRANCH" \
    "$BENCH_DIR"
}

create_site() {
  step "create_site"
  if [[ -d "$BENCH_DIR/sites/$SITE_NAME" ]]; then
    skip "site $SITE_NAME already exists"
    return
  fi
  (
    cd "$BENCH_DIR"
    run bench new-site \
      --mariadb-root-password "$MYSQL_ROOT_PASSWORD" \
      --admin-password "$ADMIN_PASSWORD" \
      "$SITE_NAME"
  )
}
```

- [ ] **Step 2: Syntax check**

Run: `bash -n install.sh`
Expected: no output, exit 0.

- [ ] **Step 3: Shellcheck**

Run: `shellcheck install.sh`
Expected: no errors.

- [ ] **Step 4: DRY_RUN smoke test**

Run: `DRY_RUN=1 MYSQL_ROOT_PASSWORD=test BENCH_DIR=/tmp/nonexistent-bench ./install.sh --dev 2>&1 | grep -E '(install_bench_cli|init_bench|create_site|DRY_RUN:.*bench)'`

Expected output (among other lines):

```text
==> install_bench_cli
DRY_RUN: pipx install frappe-bench
==> init_bench
DRY_RUN: bench init --python python3.11 --frappe-branch version-15 /tmp/nonexistent-bench
==> create_site
DRY_RUN: bench new-site --mariadb-root-password test --admin-password admin mrv.localhost
```

- [ ] **Step 5: Commit**

```bash
git add install.sh
git commit -m "feat(install.sh): implement install_bench_cli, init_bench, create_site"
```

---

## Task 7: Implement `get_and_install_apps` (plus post-install migrate)

**Files:**

- Modify: `install.sh` (replace the `get_and_install_apps` stub)

- [ ] **Step 1: Replace the stub**

In `install.sh`, find:

```bash
get_and_install_apps() { step "get_and_install_apps"; :; }
```

Replace it with:

```bash
get_and_install_apps() {
  step "get_and_install_apps"
  _get_and_install_one mrvtools          "$MRVTOOLS_SRC"
  _get_and_install_one frappe_side_menu  "$SIDE_MENU_SRC"
  info "running bench migrate"
  (
    cd "$BENCH_DIR"
    run bench --site "$SITE_NAME" migrate
  )
}

_get_and_install_one() {
  local app="$1"
  local src="$2"
  (
    cd "$BENCH_DIR"
    if [[ -d "apps/$app" ]]; then
      skip "apps/$app already fetched"
    else
      run bench get-app "$app" "$src"
    fi
    if [[ "$DRY_RUN" == "1" ]]; then
      printf 'DRY_RUN: bench --site %s install-app %s (if not already installed)\n' \
        "$SITE_NAME" "$app"
    else
      if bench --site "$SITE_NAME" list-apps 2>/dev/null | grep -q "^$app$"; then
        skip "$app already installed on $SITE_NAME"
      else
        bench --site "$SITE_NAME" install-app "$app"
      fi
    fi
  )
}
```

- [ ] **Step 2: Syntax check**

Run: `bash -n install.sh`
Expected: no output, exit 0.

- [ ] **Step 3: Shellcheck**

Run: `shellcheck install.sh`
Expected: no errors.

- [ ] **Step 4: DRY_RUN smoke test**

Run: `DRY_RUN=1 MYSQL_ROOT_PASSWORD=test BENCH_DIR=/tmp/nonexistent-bench ./install.sh --dev 2>&1 | grep -E '(get_and_install_apps|bench get-app|install-app|migrate)'`

Expected output includes (paths may differ by environment):

```text
==> get_and_install_apps
DRY_RUN: bench get-app mrvtools <absolute path to this repo>
DRY_RUN: bench --site mrv.localhost install-app mrvtools (if not already installed)
DRY_RUN: bench get-app frappe_side_menu <absolute path to this repo>/frappe_side_menu
DRY_RUN: bench --site mrv.localhost install-app frappe_side_menu (if not already installed)
DRY_RUN: bench --site mrv.localhost migrate
```

- [ ] **Step 5: Commit**

```bash
git add install.sh
git commit -m "feat(install.sh): implement get_and_install_apps with migrate"
```

---

## Task 8: Implement `patch_site_config` (dev-only JSON patch)

**Files:**

- Modify: `install.sh` (replace the `patch_site_config` stub)

- [ ] **Step 1: Replace the stub**

In `install.sh`, find:

```bash
patch_site_config()    { step "patch_site_config"; :; }
```

Replace it with:

```bash
patch_site_config() {
  step "patch_site_config"
  local config_path="$BENCH_DIR/sites/$SITE_NAME/site_config.json"
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: patch %s (ignore_csrf=1, developer_mode=1)\n' "$config_path"
    return
  fi
  if [[ ! -f "$config_path" ]]; then
    err "site_config.json not found at $config_path"
    exit 1
  fi
  python3 - "$config_path" <<'PY'
import json, sys
path = sys.argv[1]
with open(path) as f:
    cfg = json.load(f)
changed = False
for key, want in (("ignore_csrf", 1), ("developer_mode", 1)):
    if cfg.get(key) != want:
        cfg[key] = want
        changed = True
if changed:
    with open(path, "w") as f:
        json.dump(cfg, f, indent=1, sort_keys=True)
    print(f"patched {path}")
else:
    print(f"no changes needed: {path}")
PY
}
```

- [ ] **Step 2: Syntax check**

Run: `bash -n install.sh`
Expected: no output, exit 0.

- [ ] **Step 3: Shellcheck**

Run: `shellcheck install.sh`
Expected: no errors.

- [ ] **Step 4: DRY_RUN smoke test — dev branch only**

Run: `DRY_RUN=1 MYSQL_ROOT_PASSWORD=test BENCH_DIR=/tmp/nonexistent-bench ./install.sh --dev 2>&1 | grep -A1 patch_site_config`

Expected:

```text
==> patch_site_config
DRY_RUN: patch /tmp/nonexistent-bench/sites/mrv.localhost/site_config.json (ignore_csrf=1, developer_mode=1)
```

- [ ] **Step 5: Unit-test the JSON patch in isolation (real run on a temp file)**

Run:

```bash
tmp=$(mktemp)
echo '{"db_name":"x","ignore_csrf":0,"developer_mode":0}' > "$tmp"
python3 -c '
import json,sys
p=sys.argv[1]
cfg=json.load(open(p))
changed=False
for k,v in (("ignore_csrf",1),("developer_mode",1)):
    if cfg.get(k)!=v: cfg[k]=v; changed=True
if changed:
    json.dump(cfg,open(p,"w"),indent=1,sort_keys=True); print("patched")
else:
    print("no changes needed")
' "$tmp"
cat "$tmp"
rm "$tmp"
```

Expected: prints `patched`; the printed JSON has `"ignore_csrf": 1` and `"developer_mode": 1`.

- [ ] **Step 6: Commit**

```bash
git add install.sh
git commit -m "feat(install.sh): implement patch_site_config for dev mode"
```

---

## Task 9: Implement `build_frontend`

**Files:**

- Modify: `install.sh` (replace the `build_frontend` stub)

- [ ] **Step 1: Replace the stub**

In `install.sh`, find:

```bash
build_frontend()       { step "build_frontend"; :; }
```

Replace it with:

```bash
build_frontend() {
  step "build_frontend"
  local fe="$MRVTOOLS_SRC/frontend"
  if [[ ! -d "$fe" ]]; then
    err "frontend directory not found at $fe"
    exit 1
  fi
  (
    cd "$fe"
    run yarn install --frozen-lockfile
    run yarn build
  )
}
```

- [ ] **Step 2: Syntax check**

Run: `bash -n install.sh`
Expected: no output, exit 0.

- [ ] **Step 3: Shellcheck**

Run: `shellcheck install.sh`
Expected: no errors.

- [ ] **Step 4: DRY_RUN smoke test**

Run: `DRY_RUN=1 MYSQL_ROOT_PASSWORD=test ./install.sh --dev 2>&1 | grep -A2 build_frontend`

Expected:

```text
==> build_frontend
DRY_RUN: yarn install --frozen-lockfile
DRY_RUN: yarn build
```

- [ ] **Step 5: Commit**

```bash
git add install.sh
git commit -m "feat(install.sh): implement build_frontend"
```

---

## Task 10: Implement `configure_dev` and `configure_prod`

**Files:**

- Modify: `install.sh` (replace both stubs)

- [ ] **Step 1: Replace the two stubs**

In `install.sh`, find:

```bash
configure_dev()        { step "configure_dev"; :; }
configure_prod()       { step "configure_prod"; :; }
```

Replace them with:

```bash
configure_dev() {
  step "configure_dev"
  cat <<EOF

Dev install complete. Next steps:

  1) In terminal A, start the Frappe bench:
       cd "$BENCH_DIR" && bench start

  2) In terminal B, start the Vite dev server:
       cd "$MRVTOOLS_SRC/frontend" && yarn dev

  3) Open the site:
       http://$SITE_NAME:8000

Admin credentials: user 'Administrator', password '$ADMIN_PASSWORD'.
EOF
}

configure_prod() {
  step "configure_prod"
  run sudo bench setup production "$PROD_USER"
  (
    cd "$BENCH_DIR"
    run bench --site "$SITE_NAME" set-config developer_mode 0
    run bench --site "$SITE_NAME" set-config ignore_csrf 0
  )
}
```

- [ ] **Step 2: Syntax check**

Run: `bash -n install.sh`
Expected: no output, exit 0.

- [ ] **Step 3: Shellcheck**

Run: `shellcheck install.sh`
Expected: no errors.

- [ ] **Step 4: DRY_RUN smoke test — dev**

Run: `DRY_RUN=1 MYSQL_ROOT_PASSWORD=test ./install.sh --dev 2>&1 | sed -n '/==> configure_dev/,/install.sh finished/p'`

Expected output contains the "Next steps" block with both `bench start` and `yarn dev` instructions and the site URL.

- [ ] **Step 5: DRY_RUN smoke test — prod**

Run: `DRY_RUN=1 MYSQL_ROOT_PASSWORD=test PROD_USER=ubuntu ./install.sh --prod 2>&1 | sed -n '/==> configure_prod/,/install.sh finished/p'`

Expected:

```text
==> configure_prod
DRY_RUN: sudo bench setup production ubuntu
DRY_RUN: bench --site mrv.localhost set-config developer_mode 0
DRY_RUN: bench --site mrv.localhost set-config ignore_csrf 0

==> install.sh finished (mode=prod)
```

Also confirm that prod mode does NOT print a `==> patch_site_config` line.

- [ ] **Step 6: Commit**

```bash
git add install.sh
git commit -m "feat(install.sh): implement configure_dev and configure_prod"
```

---

## Task 11: Final verification — shellcheck clean, both DRY_RUN smoke tests pass

**Files:**

- None modified (verification only)

- [ ] **Step 1: Syntax check**

Run: `bash -n install.sh`
Expected: no output, exit 0.

- [ ] **Step 2: Full shellcheck**

Run: `shellcheck install.sh`
Expected: zero errors. Any warnings must be either fixed or silenced with an inline `# shellcheck disable=SCxxxx` directive that includes a one-line reason.

- [ ] **Step 3: DRY_RUN full dev pipeline**

Run: `DRY_RUN=1 MYSQL_ROOT_PASSWORD=test ./install.sh --dev 2>&1 | tee /tmp/install-dev.out`

Expected output contains, in order, the headers:

```text
==> install_system_deps
==> install_bench_cli
==> init_bench
==> create_site
==> get_and_install_apps
==> build_frontend
==> patch_site_config
==> configure_dev
==> install.sh finished (mode=dev)
```

Verify with: `grep -c '^==> ' /tmp/install-dev.out`
Expected: `9`.

- [ ] **Step 4: DRY_RUN full prod pipeline**

Run: `DRY_RUN=1 MYSQL_ROOT_PASSWORD=test PROD_USER=ubuntu ./install.sh --prod 2>&1 | tee /tmp/install-prod.out`

Expected the same headers except `patch_site_config` is absent and `configure_dev` is replaced by `configure_prod`.

Verify with: `grep -c '^==> ' /tmp/install-prod.out`
Expected: `8`.

Verify with: `grep -c patch_site_config /tmp/install-prod.out`
Expected: `0`.

- [ ] **Step 5: Missing-password error path**

Run: `./install.sh --dev; echo exit=$?`
Expected: prints `ERR:  MYSQL_ROOT_PASSWORD must be set …` and `exit=2`.

- [ ] **Step 6: No-arg error path**

Run: `./install.sh; echo exit=$?`
Expected: prints the usage block and `exit=2`.

- [ ] **Step 7: `--help` path**

Run: `./install.sh --help`
Expected: usage block, exit 0.

- [ ] **Step 8: Confirm no other files were modified**

Run: `git status --short`
Expected: only `install.sh` appears in the commit set for this phase (plus whatever was already dirty from Task 3). No incidental changes.

---

## Task 12: Update `CLAUDE.md` with a pointer to `install.sh`

**Files:**

- Modify: `CLAUDE.md` (inside the existing "Build and run" section, after the dev-server paragraph)

- [ ] **Step 1: Insert the new paragraph**

In `CLAUDE.md`, find the line:

```markdown
There is no CI (`.github/workflows/` is absent) and no enforced linting — only [frontend/.prettierrc.json](frontend/.prettierrc.json) exists and nothing runs it automatically.
```

Immediately after it, insert a blank line and the following paragraph:

```markdown
For a one-command bootstrap (fresh macOS, Ubuntu, or Windows/WSL2 laptop → working dev or prod install), run [install.sh](install.sh) at the repo root: `MYSQL_ROOT_PASSWORD=<pw> ./install.sh --dev` (or `--prod`). The script is idempotent — it automates exactly the `bench get-app` / `install-app` / `migrate` / `yarn build` sequence documented above, plus OS package install (Homebrew on macOS, apt on Ubuntu/WSL2), `bench init`, `new-site`, and the `ignore_csrf` / `developer_mode` flip for dev. Env vars (`BENCH_DIR`, `SITE_NAME`, `FRAPPE_BRANCH`, etc.) override defaults; `DRY_RUN=1` prints what would run without executing it. See [docs/superpowers/specs/2026-04-19-unified-setup-script-design.md](docs/superpowers/specs/2026-04-19-unified-setup-script-design.md) for the full spec.
```

- [ ] **Step 2: Verify the insertion**

Run: `grep -A1 "install.sh" CLAUDE.md | head -5`
Expected: the inserted paragraph is present; `install.sh` is referenced.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: point CLAUDE.md at install.sh for one-command bootstrap"
```

---

## Post-plan checklist

- [ ] All 12 tasks committed; `git log --oneline` shows 12 new commits above the starting `master` HEAD.
- [ ] `git grep -i NetZeroLabs` returns zero matches (or exits 1 with no output).
- [ ] `grep -c bitbucket package.json || true` prints `0`.
- [ ] `head -1 license.txt` prints `MIT License`.
- [ ] `shellcheck install.sh` exits cleanly.
- [ ] `DRY_RUN=1 MYSQL_ROOT_PASSWORD=test ./install.sh --dev` exits 0.
- [ ] `DRY_RUN=1 MYSQL_ROOT_PASSWORD=test ./install.sh --prod` exits 0.
- [ ] (Recommended, out of the required scope) End-to-end on a fresh Ubuntu 22.04 Docker container: `docker run --rm -it -v "$PWD":/src ubuntu:22.04 bash -c "apt update && apt install -y sudo curl && cd /src && MYSQL_ROOT_PASSWORD=test ./install.sh --dev"` — script completes and site is reachable; re-running logs `--> skipping` for every phase.
