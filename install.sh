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
