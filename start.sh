#!/usr/bin/env bash
# start.sh — bring up the MRV stack (bench + dev: Vite) on an installed bench.
# See docs/superpowers/specs/2026-04-19-start-shutdown-scripts-design.md
set -euo pipefail

# --- Usage ---------------------------------------------------------------
usage() {
  cat <<'EOF'
Usage: start.sh [--dev | --prod] [--help]

Brings up an installed mrvtools stack: verifies system services
(MariaDB, Redis), starts bench in the background, starts the Vite dev
server (--dev only), waits for URLs to respond.

Idempotent: re-running with services already up is a no-op.

Environment variables (defaults in parens):
  BENCH_DIR        ($HOME/frappe-bench)  Bench root (must already exist)
  SITE_NAME        (mrv.localhost)       Site name (used for URL hint)
  MRVTOOLS_SRC     (auto)                Repo path (for frontend dir in --dev)
  DRY_RUN          (0)                   1 = print commands, do not execute
EOF
}

# --- Config --------------------------------------------------------------
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
BENCH_DIR="${BENCH_DIR:-$HOME/frappe-bench}"
SITE_NAME="${SITE_NAME:-mrv.localhost}"
MRVTOOLS_SRC="${MRVTOOLS_SRC:-$SCRIPT_DIR}"
DRY_RUN="${DRY_RUN:-0}"

MODE=""
OS=""
IS_WSL=0
CURRENT_PHASE=""

STATE_DIR=""
PID_DIR=""
LOG_DIR=""
BENCH_PID_FILE=""
VITE_PID_FILE=""
BENCH_LOG=""
VITE_LOG=""

WEB_PORT=8000
SOCKETIO_PORT=9000
REDIS_CACHE_PORT=13000
REDIS_QUEUE_PORT=11000

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
    Darwin) OS=macos ;;
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
      err "Unsupported OS: $uname_s"
      exit 1
      ;;
  esac
  info "detected OS: $OS (WSL=$IS_WSL)"
}

# --- State paths ---------------------------------------------------------
init_state_paths() {
  STATE_DIR="$BENCH_DIR/.mrv"
  PID_DIR="$STATE_DIR/pids"
  LOG_DIR="$STATE_DIR/logs"
  BENCH_PID_FILE="$PID_DIR/bench.pid"
  VITE_PID_FILE="$PID_DIR/vite.pid"
  BENCH_LOG="$LOG_DIR/bench.log"
  VITE_LOG="$LOG_DIR/vite.log"
}

verify_bench_dir() {
  if [[ ! -d "$BENCH_DIR" ]]; then
    err "BENCH_DIR=$BENCH_DIR does not exist. Run install.sh first."
    exit 1
  fi
  if [[ ! -d "$BENCH_DIR/sites/$SITE_NAME" ]]; then
    err "Site $SITE_NAME not found in $BENCH_DIR/sites/. Run install.sh first."
    exit 1
  fi
  run mkdir -p "$PID_DIR" "$LOG_DIR"
}

# --- Bench port discovery ------------------------------------------------
# Reads $BENCH_DIR/sites/common_site_config.json and sets WEB_PORT,
# SOCKETIO_PORT, REDIS_CACHE_PORT, REDIS_QUEUE_PORT. Falls back to defaults
# (8000/9000/13000/11000) if the file or a key is missing.
discover_bench_ports() {
  local cfg="$BENCH_DIR/sites/common_site_config.json"
  if [[ ! -f "$cfg" ]]; then
    info "common_site_config.json not found; using default ports (8000/9000/13000/11000)"
    return
  fi
  local out
  out="$(python3 - "$cfg" <<'PY'
import json, re, sys
cfg = json.load(open(sys.argv[1]))
def port_of(url, default):
    m = re.search(r':(\d+)', url or "")
    return int(m.group(1)) if m else default
print(cfg.get("webserver_port", 8000))
print(cfg.get("socketio_port", 9000))
print(port_of(cfg.get("redis_cache"), 13000))
print(port_of(cfg.get("redis_queue"), 11000))
PY
)"
  { read -r WEB_PORT
    read -r SOCKETIO_PORT
    read -r REDIS_CACHE_PORT
    read -r REDIS_QUEUE_PORT
  } <<<"$out"
  info "bench ports: web=$WEB_PORT socketio=$SOCKETIO_PORT redis_cache=$REDIS_CACHE_PORT redis_queue=$REDIS_QUEUE_PORT"
}

# --- PID file helpers ----------------------------------------------------
# pid_alive PID — returns 0 if the pid is alive, non-zero otherwise.
pid_alive() {
  local pid="$1"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

# read_pid FILE — echoes the pid in FILE (empty if file missing/empty).
read_pid() {
  local file="$1"
  [[ -f "$file" ]] && tr -d '[:space:]' <"$file"
}

# check_or_clean_pid LABEL FILE
#   Echoes one of: "alive <pid>", "stale", "missing".
#   Removes the file if stale.
check_or_clean_pid() {
  local label="$1" file="$2" pid
  pid="$(read_pid "$file" || true)"
  if [[ -z "$pid" ]]; then
    echo "missing"
    return
  fi
  if pid_alive "$pid"; then
    echo "alive $pid"
    return
  fi
  info "$label: stale pid $pid in $file, removing"
  run rm -f "$file"
  echo "stale"
}

# --- Phases (filled in by later tasks) -----------------------------------
verify_system_services() {
  step "verify_system_services"
  if [[ "$OS" == "macos" ]]; then
    _verify_services_macos
  else
    _verify_services_ubuntu
  fi
}

_verify_services_macos() {
  local svc
  for svc in mariadb redis; do
    if brew services list 2>/dev/null | awk -v s="$svc" '$1==s && $2=="started" {found=1} END {exit !found}'; then
      skip "$svc (brew service already started)"
    else
      info "starting $svc via brew services"
      run brew services start "$svc"
    fi
  done
}

_verify_services_ubuntu() {
  local svc check_cmd start_cmd
  for svc in mariadb redis-server; do
    if [[ "$IS_WSL" == "1" ]]; then
      check_cmd=(service "$svc" status)
      start_cmd=(sudo service "$svc" start)
    else
      check_cmd=(systemctl is-active --quiet "$svc")
      start_cmd=(sudo systemctl start "$svc")
    fi
    if "${check_cmd[@]}" &>/dev/null; then
      skip "$svc (already running)"
    else
      info "starting $svc"
      run "${start_cmd[@]}"
    fi
  done
}
# Returns 0 if supervisor is running AND a frappe-bench supervisor conf exists.
# Used by --prod start_bench to skip starting bench manually when the
# real prod stack is already supervisor-managed.
_bench_managed_by_supervisor() {
  if ! command -v pgrep &>/dev/null; then
    return 1
  fi
  if ! pgrep -f supervisord &>/dev/null; then
    return 1
  fi
  # Ubuntu/Debian: /etc/supervisor/conf.d/frappe-bench-*.conf
  # macOS prod is unusual; we only check the linux path.
  compgen -G '/etc/supervisor/conf.d/frappe-bench-*' >/dev/null
}

start_bench() {
  step "start_bench"
  if [[ "$MODE" == "prod" ]] && _bench_managed_by_supervisor; then
    skip "bench (managed by supervisor)"
    return
  fi
  local status
  status="$(check_or_clean_pid bench "$BENCH_PID_FILE")"
  case "$status" in
    "alive "*)
      skip "bench (already running, pid=${status#alive })"
      return
      ;;
  esac
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: cd %q && nohup bench start >>%q 2>&1 &\n' "$BENCH_DIR" "$BENCH_LOG"
    printf 'DRY_RUN: echo $! > %q\n' "$BENCH_PID_FILE"
    return
  fi
  info "starting bench (logs: $BENCH_LOG)"
  (
    cd "$BENCH_DIR"
    nohup bench start >>"$BENCH_LOG" 2>&1 &
    echo $! >"$BENCH_PID_FILE"
  )
  info "bench pid: $(cat "$BENCH_PID_FILE")"
}
start_vite() {
  step "start_vite"
  local fe="$MRVTOOLS_SRC/frontend"
  if [[ ! -d "$fe" ]]; then
    err "frontend dir not found at $fe (set MRVTOOLS_SRC to repo root)"
    exit 1
  fi
  local status
  status="$(check_or_clean_pid vite "$VITE_PID_FILE")"
  case "$status" in
    "alive "*)
      skip "vite (already running, pid=${status#alive })"
      return
      ;;
  esac
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: cd %q && nohup yarn dev >>%q 2>&1 &\n' "$fe" "$VITE_LOG"
    printf 'DRY_RUN: echo $! > %q\n' "$VITE_PID_FILE"
    return
  fi
  info "starting vite (logs: $VITE_LOG)"
  (
    cd "$fe"
    nohup yarn dev >>"$VITE_LOG" 2>&1 &
    echo $! >"$VITE_PID_FILE"
  )
  info "vite pid: $(cat "$VITE_PID_FILE")"
}
# wait_for_url URL TIMEOUT_SECONDS LABEL LOG_FILE
#   Polls URL once per second up to TIMEOUT_SECONDS. On timeout, prints the
#   last 20 lines of LOG_FILE and exits the script with status 1.
wait_for_url() {
  local url="$1" timeout="$2" label="$3" log="$4" elapsed=0
  info "waiting for $label at $url (timeout ${timeout}s)"
  while (( elapsed < timeout )); do
    if curl -fsS -o /dev/null --max-time 2 "$url"; then
      info "$label is up after ${elapsed}s"
      return 0
    fi
    sleep 1
    elapsed=$((elapsed + 1))
  done
  err "$label did not respond within ${timeout}s. Last 20 lines of $log:"
  if [[ -f "$log" ]]; then
    tail -20 "$log" >&2
  else
    err "(log file not found)"
  fi
  exit 1
}

wait_for_readiness() {
  step "wait_for_readiness"
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: poll http://%s:%s/api/method/ping (60s)\n' "$SITE_NAME" "$WEB_PORT"
    if [[ "$MODE" == "dev" ]]; then
      printf 'DRY_RUN: poll http://127.0.0.1:8080 (30s)\n'
    fi
    return
  fi
  wait_for_url "http://$SITE_NAME:$WEB_PORT/api/method/ping" 60 "Frappe (bench)" "$BENCH_LOG"
  if [[ "$MODE" == "dev" ]]; then
    wait_for_url "http://127.0.0.1:8080" 30 "Vite" "$VITE_LOG"
  fi
}
print_summary() {
  step "print_summary"
  local frappe_url="http://$SITE_NAME:$WEB_PORT"
  cat >&2 <<EOF

Stack is up.

  Frappe:  $frappe_url   (logs: tail -f $BENCH_LOG)
EOF
  if [[ "$MODE" == "dev" ]]; then
    cat >&2 <<EOF
  Vite:    http://localhost:8080       (logs: tail -f $VITE_LOG)
EOF
  fi
  cat >&2 <<EOF
  Stop:    ./shutdown.sh

EOF
}

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
  init_state_paths
  verify_bench_dir
  discover_bench_ports

  verify_system_services
  start_bench
  if [[ "$MODE" == "dev" ]]; then
    start_vite
  fi
  wait_for_readiness
  print_summary

  printf '\n==> start.sh finished (mode=%s)\n' "$MODE" >&2
}

main "$@"
