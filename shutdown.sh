#!/usr/bin/env bash
# shutdown.sh — stop the MRV stack started by start.sh / install.sh.
# See docs/superpowers/specs/2026-04-19-start-shutdown-scripts-design.md
set -euo pipefail

# --- Usage ---------------------------------------------------------------
usage() {
  cat <<'EOF'
Usage: shutdown.sh [--full] [--help]

Stops the MRV stack:
  default   Stop bench + Vite only. System MariaDB/Redis are left running.
  --full    Also stop MariaDB and Redis system services.

Always sweeps orphan listeners on the bench's actual ports (read from
common_site_config.json, defaults 8000/9000/13000/11000) plus 8080 (Vite).
Safe to run any time.

Environment variables (defaults in parens):
  BENCH_DIR        ($HOME/frappe-bench)  Bench root
  DRY_RUN          (0)                   1 = print commands, do not execute
EOF
}

# --- Config --------------------------------------------------------------
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
BENCH_DIR="${BENCH_DIR:-$HOME/frappe-bench}"
DRY_RUN="${DRY_RUN:-0}"

FULL=0
OS=""
IS_WSL=0
CURRENT_PHASE=""

STATE_DIR=""
PID_DIR=""
BENCH_PID_FILE=""
VITE_PID_FILE=""

# Bench ports — defaults; discover_bench_ports() overrides these from
# $BENCH_DIR/sites/common_site_config.json (offset benches use 8001/9001/etc).
WEB_PORT=8000
SOCKETIO_PORT=9000
REDIS_CACHE_PORT=13000
REDIS_QUEUE_PORT=11000

# Vite is not bench-managed and stays on 8080.
VITE_PORT=8080

# Populated by main() after discover_bench_ports.
SWEEP_PORTS=()

# Process names we are willing to kill during the orphan sweep.
ORPHAN_COMMANDS_REGEX='^(bench|node|redis-ser|gunicorn|honcho)$'

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
        err "Unsupported Linux distribution"
        exit 1
      fi
      ;;
    *)
      err "Unsupported OS: $uname_s"
      exit 1
      ;;
  esac
}

init_state_paths() {
  STATE_DIR="$BENCH_DIR/.mrv"
  PID_DIR="$STATE_DIR/pids"
  BENCH_PID_FILE="$PID_DIR/bench.pid"
  VITE_PID_FILE="$PID_DIR/vite.pid"
}

# --- Bench port discovery ------------------------------------------------
# Reads $BENCH_DIR/sites/common_site_config.json and overrides WEB_PORT,
# SOCKETIO_PORT, REDIS_CACHE_PORT, REDIS_QUEUE_PORT. Falls back to the
# globals' defaults if the file or a key is missing.
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

# --- PID helpers ---------------------------------------------------------

# pid_alive PID — returns 0 if the pid is alive.
pid_alive() {
  local pid="$1"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

# stop_pid LABEL FILE
#   If FILE has a live pid: SIGTERM, wait up to 10s, then SIGKILL if needed.
#   Always removes the pid file at the end (even if it was missing/stale).
stop_pid() {
  local label="$1" file="$2" pid waited
  if [[ ! -f "$file" ]]; then
    info "$label: no pid file"
    return
  fi
  pid="$(tr -d '[:space:]' <"$file")"
  if [[ -z "$pid" ]] || ! pid_alive "$pid"; then
    info "$label: pid file present but process not running (pid=$pid)"
    run rm -f "$file"
    return
  fi
  info "$label: SIGTERM pid $pid"
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: kill -TERM %s; wait up to 10s; SIGKILL if alive; rm %s\n' "$pid" "$file"
    return
  fi
  kill -TERM "$pid" 2>/dev/null || true
  waited=0
  while pid_alive "$pid" && (( waited < 10 )); do
    sleep 1
    waited=$((waited + 1))
  done
  if pid_alive "$pid"; then
    warn "$label: did not exit on SIGTERM; sending SIGKILL"
    kill -KILL "$pid" 2>/dev/null || true
    sleep 1
  fi
  if pid_alive "$pid"; then
    err "$label: pid $pid still alive after SIGKILL"
    return 1
  fi
  info "$label: stopped"
  run rm -f "$file"
}

# --- Phases (filled in by later tasks) -----------------------------------
stop_tracked_processes() {
  step "stop_tracked_processes"
  # Reverse of start order: vite first (so it doesn't error-spam during bench shutdown), then bench.
  stop_pid vite  "$VITE_PID_FILE"
  stop_pid bench "$BENCH_PID_FILE"
}
sweep_orphan_ports()     { step "sweep_orphan_ports";     info "(not yet implemented)"; }
stop_system_services()   { step "stop_system_services";   info "(not yet implemented)"; }
final_verification()     { step "final_verification";     info "(not yet implemented)"; }

# --- Arg parsing ---------------------------------------------------------
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --full)    FULL=1; shift ;;
      --help|-h) usage; exit 0 ;;
      *)         err "Unknown argument: $1"; usage; exit 2 ;;
    esac
  done
}

# --- Main ----------------------------------------------------------------
main() {
  parse_args "$@"
  detect_os
  init_state_paths
  discover_bench_ports
  SWEEP_PORTS=("$WEB_PORT" "$VITE_PORT" "$SOCKETIO_PORT" "$REDIS_QUEUE_PORT" "$REDIS_CACHE_PORT")

  if [[ ! -d "$PID_DIR" ]]; then
    info "no managed services found at $PID_DIR (continuing to orphan sweep)"
  fi

  stop_tracked_processes
  sweep_orphan_ports
  if [[ "$FULL" == "1" ]]; then
    stop_system_services
  fi
  final_verification

  printf '\n==> shutdown.sh finished (full=%s)\n' "$FULL" >&2
}

main "$@"
