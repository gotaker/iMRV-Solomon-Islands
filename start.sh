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

# --- Phases (filled in by later tasks) -----------------------------------
verify_system_services() { step "verify_system_services"; info "(not yet implemented)"; }
start_bench()            { step "start_bench";            info "(not yet implemented)"; }
start_vite()             { step "start_vite";             info "(not yet implemented)"; }
wait_for_readiness()     { step "wait_for_readiness";     info "(not yet implemented)"; }
print_summary()          { step "print_summary";          info "(not yet implemented)"; }

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
