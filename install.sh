#!/usr/bin/env bash
# install.sh — unified bootstrap for MRV Solomon Islands
# See docs/superpowers/specs/2026-04-19-unified-setup-script-design.md
set -euo pipefail

# --- Usage ---------------------------------------------------------------
usage() {
  cat <<'EOF'
Usage: install.sh [--dev | --prod] [--with-sample-data | --no-sample-data] [--help]

Bootstraps a fresh macOS, Ubuntu, or Windows-via-WSL2 laptop into a working
mrvtools + frappe_side_menu + frontend environment.

Modes:
  --dev              Local development environment (Vite dev server, ignore_csrf enabled)
  --prod             Production environment (supervisor + nginx via bench setup production)

Sample data:
  --with-sample-data Force-restore the demo DB after install (default in --dev)
  --no-sample-data   Skip demo-DB restore (default in --prod)

Environment variables (defaults in parens):
  BENCH_DIR               ($HOME/frappe-bench)  Where bench init lives
  FRAPPE_BRANCH           (version-16)          Frappe branch for bench init
  PYTHON_VERSION          (3.14)                Python for bench venv
  NODE_VERSION            (24)                  Node for bench init
  SITE_NAME               (mrv.localhost)       Site to create
  ADMIN_PASSWORD          (admin)               Frappe admin password
  MYSQL_ROOT_PASSWORD     (REQUIRED)            MariaDB root password
  MRVTOOLS_SRC            (auto)                Repo path for bench get-app mrvtools
  SIDE_MENU_SRC           (auto)                Repo path for bench get-app frappe_side_menu
  SKIP_SYSTEM_DEPS        (0)                   Set to 1 to skip OS package install
  LOAD_SAMPLE_DATA        (auto)                1/0 — overrides the mode-based default above
  SAMPLE_DB_PATH          (auto)                Explicit path to the *.sql.gz to restore;
                                                otherwise newest match in .Sample DB/ is used
  PROD_USER               ($USER)                       User for bench setup production
  PROD_DOMAIN             (demo.imrv.netzerolabs.io)    In --prod, the FQDN attached via bench setup add-domain
  PROD_ENABLE_TLS         (0)                            If 1 in --prod, run bench setup lets-encrypt (Ubuntu only)
  DRY_RUN                 (0)                   Set to 1 to echo commands instead of running
EOF
}

# --- Config --------------------------------------------------------------
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
BENCH_DIR="${BENCH_DIR:-$HOME/frappe-bench}"
FRAPPE_BRANCH="${FRAPPE_BRANCH:-version-16}"
PYTHON_VERSION="${PYTHON_VERSION:-3.14}"
NODE_VERSION="${NODE_VERSION:-24}"
SITE_NAME="${SITE_NAME:-mrv.localhost}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-}"
MRVTOOLS_SRC="${MRVTOOLS_SRC:-$SCRIPT_DIR}"
SIDE_MENU_SRC="${SIDE_MENU_SRC:-$MRVTOOLS_SRC/frappe_side_menu}"
SKIP_SYSTEM_DEPS="${SKIP_SYSTEM_DEPS:-0}"
PROD_USER="${PROD_USER:-${USER:-root}}"
PROD_DOMAIN="${PROD_DOMAIN:-demo.imrv.netzerolabs.io}"
PROD_ENABLE_TLS="${PROD_ENABLE_TLS:-0}"
DRY_RUN="${DRY_RUN:-0}"
LOAD_SAMPLE_DATA="${LOAD_SAMPLE_DATA:-}"
SAMPLE_DB_PATH="${SAMPLE_DB_PATH:-}"

MODE=""
OS=""
IS_WSL=0
CURRENT_PHASE=""

# --- Logging -------------------------------------------------------------
step() { CURRENT_PHASE="$1"; printf '\n==> %s\n' "$1" >&2; }
info() { printf '    %s\n' "$*" >&2; }
skip() { printf -- '--> skipping %s: already done\n' "$*" >&2; }
warn() { printf 'WARN: %s\n' "$*" >&2; }
err()  { printf 'ERR:  %s\n' "$*" >&2; }

trap 'err "phase [${CURRENT_PHASE:-startup}] failed at line $LINENO"; exit 1' ERR

# --- Command runner (honours DRY_RUN) ------------------------------------
run() {
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN:'; printf ' %q' "$@"; printf '\n'
  else
    "$@"
  fi
}

# Shell-eval variant for pipelines that need shell metacharacters.
# Accepts exactly one pre-formed shell-command string, e.g.:
#   run_sh "curl -fsSL https://example.com | sudo -E bash -"
run_sh() {
  if [[ $# -ne 1 ]]; then
    err "run_sh requires exactly one pre-formed shell string (got $# args)"
    exit 1
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: %s\n' "$1"
  else
    bash -c "$1"
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
  local pkgs=(git "python@${PYTHON_VERSION}" "node@${NODE_VERSION}" yarn redis pipx)
  local pkg
  for pkg in "${pkgs[@]}"; do
    if brew list "$pkg" &>/dev/null; then
      skip "brew $pkg"
    else
      run brew install "$pkg"
    fi
  done
  _install_mariadb_macos
  _ensure_wkhtmltopdf_macos
  run brew services start mariadb
  run brew services start redis
}

_install_mariadb_macos() {
  if brew list mariadb@12.2 &>/dev/null || brew list mariadb &>/dev/null; then
    skip "brew mariadb"
    return
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: brew install mariadb@12.2 (fallback: brew install mariadb)\n'
    return
  fi
  if brew install mariadb@12.2; then
    info "installed mariadb@12.2 via Homebrew"
  else
    warn "brew install mariadb@12.2 failed; falling back to plain mariadb formula"
    brew install mariadb
    info "installed mariadb (current stable) via Homebrew"
  fi
}

_ensure_wkhtmltopdf_macos() {
  # wkhtmltopdf was removed from Homebrew (upstream abandoned). Accept any
  # existing patched-Qt binary on PATH; otherwise fail with a manual-install hint.
  if command -v wkhtmltopdf &>/dev/null && \
     wkhtmltopdf --version 2>&1 | grep -qi 'with patched qt'; then
    skip "wkhtmltopdf (patched Qt build already on PATH)"
    return
  fi
  err "wkhtmltopdf with patched Qt not found. Download the macOS pkg from"
  err "  https://github.com/wkhtmltopdf/packaging/releases/tag/0.12.6-2"
  err "install it, then re-run this script."
  exit 1
}

_install_system_deps_ubuntu() {
  run sudo apt-get update
  _add_deadsnakes_ppa_if_ubuntu
  _add_mariadb_repo
  local pkgs=(git cron "python${PYTHON_VERSION}" "python${PYTHON_VERSION}-venv" "python${PYTHON_VERSION}-dev"
              python3-dev mariadb-server mariadb-client redis-server
              build-essential libssl-dev libffi-dev xvfb libfontconfig pipx)
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
  _install_wkhtmltopdf_patched
}

_add_deadsnakes_ppa_if_ubuntu() {
  # Python 3.14 is not in Ubuntu's default repos; deadsnakes PPA ships it.
  # Only safe on actual Ubuntu — skip on Debian/WSL-Debian where the PPA
  # doesn't apply. The OS detector collapses Ubuntu+Debian into OS=ubuntu,
  # so re-read /etc/os-release here to distinguish.
  local distro_id=""
  if [[ -r /etc/os-release ]]; then
    # shellcheck disable=SC1091
    distro_id="$(. /etc/os-release && echo "${ID:-}")"
  fi
  if [[ "$distro_id" != "ubuntu" ]]; then
    skip "deadsnakes PPA (distro is '$distro_id', not ubuntu)"
    return
  fi
  run sudo add-apt-repository -y ppa:deadsnakes/ppa
  run sudo apt-get update
}

_add_mariadb_repo() {
  # Pin MariaDB to 12.2 via MariaDB's official repo. The setup script is
  # idempotent — re-running it rewrites the same apt source list.
  run_sh "curl -LsS https://r.mariadb.com/downloads/mariadb_repo_setup | sudo bash -s -- --mariadb-server-version=\"mariadb-12.2\""
  run sudo apt-get update
}

_ensure_mariadb_root_password() {
  # Frappe connects via TCP with a password, so we must verify TCP+password auth
  # actually works — not just a socket ping. `mysqladmin ping` exits 0 even on
  # auth failure (errors go to stderr), so use `mariadb -e 'SELECT 1'` instead,
  # forcing TCP with -h 127.0.0.1 so socket `unix_socket` auth doesn't mask failure.
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: verify/set mariadb root password\n'
    return
  fi
  if mariadb -u root -p"$MYSQL_ROOT_PASSWORD" -h 127.0.0.1 -e 'SELECT 1' &>/dev/null; then
    skip "mariadb root password already matches"
  elif sudo mariadb -u root -e 'SELECT 1' &>/dev/null; then
    # On Ubuntu, root uses the unix_socket auth plugin by default — socket
    # login only works as OS root, hence sudo. ALTER USER ... IDENTIFIED BY
    # switches the plugin to mysql_native_password so TCP+password works.
    info "setting mariadb root password via socket (sudo) login"
    sudo mariadb -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '$MYSQL_ROOT_PASSWORD'; FLUSH PRIVILEGES;"
  else
    err "mariadb root password is set to something different from \$MYSQL_ROOT_PASSWORD"
    err "and socket (sudo) login also failed. Reset root auth manually and re-run."
    exit 1
  fi
}

_install_wkhtmltopdf_patched() {
  # Only Ubuntu/WSL. macOS brew already ships the patched Qt build.
  if [[ "$OS" != "ubuntu" ]]; then
    return
  fi
  if command -v wkhtmltopdf &>/dev/null && \
     wkhtmltopdf --version 2>&1 | grep -qi 'with patched qt'; then
    skip "wkhtmltopdf (patched Qt build already installed)"
    return
  fi
  local codename arch version='0.12.6.1-2'
  # shellcheck disable=SC1091
  codename="$(. /etc/os-release && echo "$VERSION_CODENAME")"
  arch="$(dpkg --print-architecture)"
  if [[ -z "$codename" || -z "$arch" ]]; then
    err "could not determine Ubuntu codename or architecture for wkhtmltopdf download"
    exit 1
  fi
  # wkhtmltopdf upstream only publishes debs for jammy (22.04) and bullseye.
  # Newer Ubuntu releases (noble and later) use the jammy build as fallback;
  # it is binary-compatible aside from a libjpeg-turbo8 vs ...8t64 rename that
  # the subsequent `apt-get install -f` fixup resolves.
  case "$codename" in
    jammy|bullseye) ;;
    *) info "no wkhtmltopdf asset for '$codename'; using jammy build as fallback"
       codename=jammy ;;
  esac
  local deb_name="wkhtmltox_${version}.${codename}_${arch}.deb"
  local url="https://github.com/wkhtmltopdf/packaging/releases/download/${version}/${deb_name}"
  local tmp="/tmp/${deb_name}"
  info "downloading patched wkhtmltopdf: $url"
  run_sh "curl -fsSL -o '$tmp' '$url'"
  # Stock wkhtmltopdf (if present) conflicts with wkhtmltox; remove it quietly.
  if dpkg -s wkhtmltopdf &>/dev/null; then
    run sudo apt-get remove -y wkhtmltopdf
  fi
  run_sh "sudo dpkg -i '$tmp' || sudo apt-get install -f -y"
  run rm -f "$tmp"
}

install_bench_cli() {
  step "install_bench_cli"
  # bench 5.29+ shells out to `uv` for venv creation, so install it alongside.
  if command -v uv &>/dev/null; then
    skip "uv already on PATH"
  else
    run pipx install uv
  fi
  if command -v bench &>/dev/null; then
    skip "bench CLI already on PATH"
  else
    run pipx install frappe-bench
  fi
  # pipx installs into ~/.local/bin which may not be on PATH in this shell.
  if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]] && [[ -d "$HOME/.local/bin" ]]; then
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
    [[ "$DRY_RUN" == "1" ]] || cd "$BENCH_DIR"
    run bench new-site \
      --mariadb-root-password "$MYSQL_ROOT_PASSWORD" \
      --admin-password "$ADMIN_PASSWORD" \
      "$SITE_NAME"
  )
}
get_and_install_apps() {
  step "get_and_install_apps"
  _stage_frappe_side_menu
  _get_and_install_one mrvtools          "$MRVTOOLS_SRC"
  _get_and_install_one frappe_side_menu  "$SIDE_MENU_SRC"
  _ensure_bench_redis
  info "running bench migrate"
  (
    [[ "$DRY_RUN" == "1" ]] || cd "$BENCH_DIR"
    run bench --site "$SITE_NAME" migrate
  )
  _stop_bench_redis_daemons
}

_ensure_bench_redis() {
  # bench migrate talks to redis_cache (port 13000) and redis_queue (port 11000),
  # which bench manages separately from the system redis. These normally start
  # with `bench start`, but we need them up now.
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: start bench redis_cache and redis_queue if not running\n'
    return
  fi
  (
    cd "$BENCH_DIR"
    for name in redis_cache redis_queue; do
      local conf="config/$name.conf"
      local port
      port="$(awk '/^port/ {print $2; exit}' "$conf" 2>/dev/null || true)"
      if [[ -n "$port" ]] && lsof -iTCP:"$port" -sTCP:LISTEN &>/dev/null; then
        skip "$name on :$port"
      else
        info "starting $name"
        redis-server "$conf" --daemonize yes
      fi
    done
  )
}

_stop_bench_redis_daemons() {
  # Stops the daemonized redis processes that _ensure_bench_redis started for `bench migrate`.
  # Necessary so `bench start` (run later via start_services) can claim those ports.
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: stop bench-managed redis daemons started for migrate\n'
    return
  fi
  (
    cd "$BENCH_DIR"
    for name in redis_cache redis_queue; do
      local conf="config/$name.conf"
      local port pid
      port="$(awk '/^port/ {print $2; exit}' "$conf" 2>/dev/null || true)"
      [[ -z "$port" ]] && continue
      pid="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
      if [[ -n "$pid" ]]; then
        info "stopping $name (pid $pid on :$port)"
        kill "$pid" 2>/dev/null || true
      fi
    done
  )
}

_stage_frappe_side_menu() {
  # frappe_side_menu shares the repo root with mrvtools and has no standalone
  # setup.py in its module dir — bench get-app can't install it directly.
  # Build a pip-shaped staging dir with setup.py next to the module, and point
  # SIDE_MENU_SRC at it. Skipped if SIDE_MENU_SRC already has a setup.py
  # (user pointing at a pre-staged dir or a proper standalone clone).
  if [[ -f "$SIDE_MENU_SRC/setup.py" ]]; then
    skip "SIDE_MENU_SRC has setup.py (no staging needed)"
    return
  fi
  local stage="$BENCH_DIR/.stage/frappe_side_menu"
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: stage %s as pip package at %s\n' "$SIDE_MENU_SRC" "$stage"
    SIDE_MENU_SRC="$stage"
    return
  fi
  info "staging frappe_side_menu at $stage"
  rm -rf "$stage"
  mkdir -p "$stage"
  cp -R "$SIDE_MENU_SRC" "$stage/frappe_side_menu"
  cp "$MRVTOOLS_SRC/setup_sidebarmenu.py" "$stage/setup.py"
  cp "$MRVTOOLS_SRC/requirements.txt" "$stage/requirements.txt"
  [[ -f "$MRVTOOLS_SRC/license.txt" ]] && cp "$MRVTOOLS_SRC/license.txt" "$stage/license.txt"
  # bench get-app calls git.Repo(src) on local paths — stage must be a git
  # repo or bench falls back to URL parsing and dies on missing org attribute.
  (
    cd "$stage"
    git -c init.defaultBranch=master init -q
    git add -A
    git -c user.name=install.sh -c user.email=install@localhost commit -q -m "stage"
  )
  SIDE_MENU_SRC="$stage"
}

_get_and_install_one() {
  local app="$1"
  local src="$2"
  (
    [[ "$DRY_RUN" == "1" ]] || cd "$BENCH_DIR"
    if [[ -d "apps/$app" ]]; then
      skip "apps/$app already fetched"
    else
      # --skip-assets: frontend build happens later in build_frontend, and the
      # mrvtools frontend needs `yarn install` in apps/mrvtools/frontend first
      # or the auto-build fails with "vite: command not found".
      run bench get-app --skip-assets "$app" "$src"
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
load_sample_data() {
  step "load_sample_data"
  if [[ "$LOAD_SAMPLE_DATA" != "1" ]]; then
    skip "load_sample_data: LOAD_SAMPLE_DATA=$LOAD_SAMPLE_DATA"
    return
  fi
  _resolve_sample_db_path
  if [[ -z "$SAMPLE_DB_PATH" ]]; then
    warn "LOAD_SAMPLE_DATA=1 but no *.sql.gz found in .Sample DB/ — skipping"
    return
  fi
  if [[ ! -f "$SAMPLE_DB_PATH" ]]; then
    err "SAMPLE_DB_PATH does not exist: $SAMPLE_DB_PATH"
    exit 1
  fi
  info "sample DB: $SAMPLE_DB_PATH"
  # bench restore shells out to zgrep/gunzip without quoting the path — if
  # SAMPLE_DB_PATH contains spaces (it does by default, sitting in ".Sample DB/"),
  # the call falls apart with "No such file or directory". Copy to a clean temp.
  local tmp_db
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: cp %q to temp dir and bench --site %s --force restore <tmp>\n' \
      "$SAMPLE_DB_PATH" "$SITE_NAME"
    printf 'DRY_RUN: bench --site %s migrate (post-restore)\n' "$SITE_NAME"
    printf 'DRY_RUN: bench --site %s execute mrvtools.mrvtools.after_install.load_single_doc (re-seed singles)\n' \
      "$SITE_NAME"
    printf 'DRY_RUN: bench --site %s execute mrvtools.mrvtools.after_install.load_default_files (re-extract seed files)\n' \
      "$SITE_NAME"
    return
  fi
  tmp_db="$(mktemp -t mrv-sample-db.XXXXXX)" || { err "mktemp failed"; exit 1; }
  tmp_db="${tmp_db}.sql.gz"
  cp "$SAMPLE_DB_PATH" "$tmp_db"
  # shellcheck disable=SC2064
  trap "rm -f '$tmp_db'" RETURN
  _ensure_bench_redis
  (
    cd "$BENCH_DIR"
    run bench --site "$SITE_NAME" --force restore "$tmp_db" \
      --mariadb-root-password "$MYSQL_ROOT_PASSWORD"
    info "running bench migrate (post-restore)"
    run bench --site "$SITE_NAME" migrate
    # A sample DB can land with NULL values for singles the app seeds on
    # install (Side Menu Settings.application_logo is the common casualty —
    # it makes the sidebar flag 404). load_single_doc() re-upserts the four
    # seeded singles from master_data/*.json and is idempotent.
    info "re-seeding singles from master_data (post-restore)"
    run bench --site "$SITE_NAME" execute mrvtools.mrvtools.after_install.load_single_doc
    # Re-extract seed files whose physical file is missing from the volume
    # (the sidebar flag PNG, NDC PDFs). load_default_files() skips anything
    # already on disk and is idempotent.
    info "re-extracting seed files from zip (post-restore)"
    run bench --site "$SITE_NAME" execute mrvtools.mrvtools.after_install.load_default_files
  )
  _stop_bench_redis_daemons
}

_resolve_sample_db_path() {
  # If caller set SAMPLE_DB_PATH explicitly, leave it alone.
  if [[ -n "$SAMPLE_DB_PATH" ]]; then
    return
  fi
  local dir="$SCRIPT_DIR/.Sample DB"
  [[ -d "$dir" ]] || return
  # Sample backups use ISO-ish timestamped names (YYYYMMDD_HHMMSS-...); sort
  # lexicographically and take the last → newest.
  local newest=""
  while IFS= read -r -d '' f; do
    [[ -z "$newest" || "$f" > "$newest" ]] && newest="$f"
  done < <(find "$dir" -maxdepth 1 -type f -name '*.sql.gz' -print0 2>/dev/null)
  SAMPLE_DB_PATH="$newest"
}

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
build_frontend() {
  step "build_frontend"
  # Build inside the bench's app clone, not the source repo — Frappe serves
  # /assets/mrvtools/frontend/ from apps/mrvtools/mrvtools/public/ and the
  # Vite build's outDir resolves relative to this frontend/ location.
  local fe="$BENCH_DIR/apps/mrvtools/frontend"
  local src_fe="$MRVTOOLS_SRC/frontend"
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: yarn install --frozen-lockfile (in %s)\n' "$fe"
    printf 'DRY_RUN: yarn build (in %s)\n' "$fe"
    printf 'DRY_RUN: yarn install --frozen-lockfile (in %s) — for start.sh yarn dev\n' "$src_fe"
    return
  fi
  if [[ ! -d "$fe" ]]; then
    err "frontend directory not found at $fe (did bench get-app mrvtools run?)"
    exit 1
  fi
  (
    cd "$fe"
    run yarn install --frozen-lockfile
    run yarn build
  )
  # Source-repo frontend needs node_modules so start.sh can run `yarn dev` here.
  # Skip if already installed.
  if [[ -d "$src_fe" && ! -d "$src_fe/node_modules" ]]; then
    info "installing source-repo frontend deps for start.sh's yarn dev"
    (
      cd "$src_fe"
      run yarn install --frozen-lockfile
    )
  elif [[ -d "$src_fe/node_modules" ]]; then
    skip "source-repo frontend deps (node_modules exists)"
  fi
}
configure_dev() {
  step "configure_dev"
  info "site_config patched (developer_mode=1, ignore_csrf=1)"
  info "starting services..."
  info "(admin user: 'Administrator', password: '$ADMIN_PASSWORD')"
}

configure_prod() {
  step "configure_prod"
  (
    [[ "$DRY_RUN" == "1" ]] || cd "$BENCH_DIR"
    run bench config dns_multitenant on
    run sudo bench setup production "$PROD_USER"
    run bench --site "$SITE_NAME" set-config developer_mode 0
    run bench --site "$SITE_NAME" set-config ignore_csrf 0
  )
  if [[ -n "$PROD_DOMAIN" ]]; then
    info "attaching domain $PROD_DOMAIN to $SITE_NAME"
    (
      [[ "$DRY_RUN" == "1" ]] || cd "$BENCH_DIR"
      run bench setup add-domain "$PROD_DOMAIN" --site "$SITE_NAME"
    )
  fi
  if [[ "$PROD_ENABLE_TLS" == "1" ]]; then
    if [[ -z "$PROD_DOMAIN" ]]; then
      err "PROD_ENABLE_TLS=1 requires PROD_DOMAIN to be set"
      exit 1
    fi
    if [[ "$OS" != "ubuntu" ]]; then
      warn "TLS setup skipped: Let's Encrypt path is Ubuntu-only (current OS: $OS)"
    else
      info "provisioning Let's Encrypt certificate for $PROD_DOMAIN"
      (
        [[ "$DRY_RUN" == "1" ]] || cd "$BENCH_DIR"
        run sudo -H bench setup lets-encrypt "$SITE_NAME" --custom-domain "$PROD_DOMAIN"
      )
    fi
  fi
}

ensure_asset_symlinks() {
  step "ensure_asset_symlinks"
  # bench get-app --skip-assets (used above to avoid yarn-install ordering
  # issues) also skips the sites/assets/<app> symlinks that Frappe needs to
  # serve /assets/<app>/* as static files. Without these, requests 404 and
  # the browser reports 'Loading module ... was blocked because of a
  # disallowed MIME type ("text/html")'. Create them explicitly.
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: symlink sites/assets/{mrvtools,frappe_side_menu} -> apps/<app>/<app>/public\n'
    return
  fi
  local assets_dir="$BENCH_DIR/sites/assets"
  run mkdir -p "$assets_dir"
  local app link target
  for app in mrvtools frappe_side_menu; do
    link="$assets_dir/$app"
    target="../../apps/$app/$app/public"
    if [[ -L "$link" && "$(readlink "$link")" == "$target" ]]; then
      skip "symlink sites/assets/$app"
    else
      run ln -sfn "$target" "$link"
    fi
  done
}

ensure_site_hostname() {
  step "ensure_site_hostname"
  # Linux's Node.js does not auto-resolve *.localhost per RFC 6761 — the
  # socketio daemon fails with 'getaddrinfo ENOTFOUND <site>' even though the
  # browser resolves it fine (Windows and macOS both handle .localhost via
  # built-in resolvers). Ensure an /etc/hosts entry exists on Ubuntu/WSL.
  if [[ "$OS" != "ubuntu" ]]; then
    skip "hostname mapping (not needed on $OS)"
    return
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: ensure /etc/hosts maps %s to 127.0.0.1\n' "$SITE_NAME"
    return
  fi
  if getent hosts "$SITE_NAME" &>/dev/null; then
    skip "hostname $SITE_NAME already resolves"
    return
  fi
  info "adding '127.0.0.1 $SITE_NAME' to /etc/hosts"
  run_sh "echo '127.0.0.1 $SITE_NAME' | sudo tee -a /etc/hosts >/dev/null"
}

start_services() {
  step "start_services"
  run "$SCRIPT_DIR/start.sh" "--$MODE"
}

# --- Arg parsing ---------------------------------------------------------
parse_args() {
  if [[ $# -eq 0 ]]; then usage; exit 2; fi
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dev)               MODE=dev;  shift ;;
      --prod)              MODE=prod; shift ;;
      --with-sample-data)  LOAD_SAMPLE_DATA=1; shift ;;
      --no-sample-data)    LOAD_SAMPLE_DATA=0; shift ;;
      --help|-h)           usage; exit 0 ;;
      *)                   err "Unknown argument: $1"; usage; exit 2 ;;
    esac
  done
  if [[ -z "$MODE" ]]; then
    err "One of --dev or --prod is required"; usage; exit 2
  fi
  # Default: dev loads sample data (if present), prod does not. Explicit flag
  # or LOAD_SAMPLE_DATA env var wins over the mode-based default.
  if [[ -z "$LOAD_SAMPLE_DATA" ]]; then
    LOAD_SAMPLE_DATA=$([[ "$MODE" == "dev" ]] && echo 1 || echo 0)
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
  load_sample_data
  build_frontend

  if [[ "$MODE" == "dev" ]]; then
    patch_site_config
    configure_dev
  else
    configure_prod
  fi

  ensure_asset_symlinks
  ensure_site_hostname
  start_services

  printf '\n==> install.sh finished (mode=%s)\n' "$MODE" >&2
}

main "$@"
