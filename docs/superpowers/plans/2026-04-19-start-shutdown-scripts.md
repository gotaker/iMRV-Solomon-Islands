# Start / Shutdown Scripts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `start.sh` and `shutdown.sh` scripts at the repo root, wire `start.sh` into `install.sh` as a final phase, and update `install.md` so the developer experience is one command up, one command down.

**Architecture:** Three symmetric scripts at the repo root (`install.sh` / `start.sh` / `shutdown.sh`), backed by per-bench state at `$BENCH_DIR/.mrv/{pids,logs}/`. `install.sh` invokes `start.sh` as its last phase; `start.sh` is idempotent (alive PID → skip); `shutdown.sh` reads PID files, falls back to a port sweep for orphan cleanup, and supports `--full` to also stop MariaDB/Redis system services.

**Tech Stack:** Bash 4+, `lsof`, `curl`, `pgrep`, OS service tooling (`brew services` on macOS; `systemctl`/`service` on Ubuntu/WSL2). No test framework — verification is via `DRY_RUN=1` and live tests against the existing `~/frappe-bench-mrv` install.

**Spec:** [docs/superpowers/specs/2026-04-19-start-shutdown-scripts-design.md](../specs/2026-04-19-start-shutdown-scripts-design.md)

---

## Files

- **Create:** `start.sh` — bring up dev/prod stack
- **Create:** `shutdown.sh` — bring down dev/prod stack
- **Modify:** `install.sh` — add `start_services` phase, trim `configure_dev` next-steps block
- **Modify:** `install.md` — document service lifecycle, update Quick start / Uninstall / Troubleshooting / See also

State directory layout (created by `start.sh` on first run):

```text
$BENCH_DIR/.mrv/
├── pids/{bench.pid, vite.pid}
└── logs/{bench.log, vite.log}
```

---

## Conventions for this plan

- Working directory for all `./script.sh` invocations: the repo root (`/Users/utahjazz/Library/CloudStorage/OneDrive-Personal/Github/iMRV-Solomon-Islands` on the dev machine).
- Live tests use `BENCH_DIR=$HOME/frappe-bench-mrv` (the install completed earlier in this session). If that bench is gone, set `BENCH_DIR` to whichever bench is current; the scripts honor the env var.
- `chmod +x` the new scripts as part of their first commit. (`install.sh` is already executable; the same convention applies.)
- Bash strict mode (`set -euo pipefail`) and the same `step`/`info`/`skip`/`warn`/`err`/`run`/`run_sh` helper shape as `install.sh` — this gives consistent output across all three scripts.
- No new env vars beyond what `install.sh` already exports.

---

## Task 1: `start.sh` skeleton — args, env, helpers, no-op phases

**Files:**

- Create: `start.sh`

- [ ] **Step 1.1: Create `start.sh` with shebang, env defaults, helpers, arg parser, no-op `main()`**

```bash
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
```

- [ ] **Step 1.2: Make executable**

Run: `chmod +x start.sh`

- [ ] **Step 1.3: Verify arg parsing — no args**

Run: `./start.sh; echo "exit=$?"`
Expected: usage block, then `exit=2`

- [ ] **Step 1.4: Verify arg parsing — bogus arg**

Run: `./start.sh --bogus; echo "exit=$?"`
Expected: `ERR: Unknown argument: --bogus`, usage block, then `exit=2`

- [ ] **Step 1.5: Verify arg parsing — help**

Run: `./start.sh --help; echo "exit=$?"`
Expected: usage block, then `exit=0`

- [ ] **Step 1.6: Verify env-validation — missing BENCH_DIR**

Run: `BENCH_DIR=/nonexistent ./start.sh --dev; echo "exit=$?"`
Expected: `ERR: BENCH_DIR=/nonexistent does not exist. Run install.sh first.` and `exit=1`

- [ ] **Step 1.7: Verify happy-path skeleton runs against existing bench**

Run: `BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev`
Expected: `detected OS`, all five `==>` phases print `(not yet implemented)`, finishes with `==> start.sh finished (mode=dev)`. Verify `~/frappe-bench-mrv/.mrv/{pids,logs}/` exist after.

- [ ] **Step 1.8: Verify DRY_RUN propagates**

Run: `DRY_RUN=1 BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev`
Expected: `mkdir` calls become `DRY_RUN: mkdir -p ...` lines; no directories created if `~/frappe-bench-mrv/.mrv` doesn't exist. (If it already exists from step 1.7, that's fine.)

- [ ] **Step 1.9: Commit**

```bash
git add start.sh
git commit -m "feat(start.sh): scaffold script with args, env, helpers, no-op phases"
```

---

## Task 2: `verify_system_services` phase in `start.sh`

**Files:**

- Modify: `start.sh` — replace the no-op `verify_system_services` stub.

- [ ] **Step 2.1: Replace the `verify_system_services` stub with real implementation**

Find this block in `start.sh`:

```bash
verify_system_services() { step "verify_system_services"; info "(not yet implemented)"; }
```

Replace with:

```bash
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
```

- [ ] **Step 2.2: DRY_RUN smoke test**

Run: `DRY_RUN=1 BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev`
Expected: `verify_system_services` step now either prints `--> skipping mariadb (brew service already started)` (if running) or `DRY_RUN: brew services start mariadb`. Same for redis. No errors.

- [ ] **Step 2.3: Live verification — services already up**

First confirm both are up: `brew services list | grep -E '^(mariadb|redis)'`. Expected: both show `started`.

Run: `BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev`
Expected output (in `verify_system_services` phase):

```text
--> skipping mariadb (brew service already started): already done
--> skipping redis (brew service already started): already done
```

Other phases continue as no-ops, script finishes cleanly.

- [ ] **Step 2.4: Commit**

```bash
git add start.sh
git commit -m "feat(start.sh): add system-services verification (mariadb, redis)"
```

---

## Task 3: stale-PID detection + `start_bench` in `start.sh`

**Files:**

- Modify: `start.sh` — replace the `start_bench` stub, add helpers.

- [ ] **Step 3.1: Add helper functions above the phase stubs**

In `start.sh`, after `verify_bench_dir()` and before the phase stubs, insert:

```bash
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
```

- [ ] **Step 3.2: Replace `start_bench` stub**

Replace:

```bash
start_bench()            { step "start_bench";            info "(not yet implemented)"; }
```

With:

```bash
start_bench() {
  step "start_bench"
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
```

- [ ] **Step 3.3: DRY_RUN smoke test**

Run: `DRY_RUN=1 BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev`
Expected: `start_bench` step shows `DRY_RUN: cd ~/frappe-bench-mrv && nohup bench start ...` and `DRY_RUN: echo $! > .../bench.pid`. No process started.

- [ ] **Step 3.4: Live test — first start**

Pre-check: `lsof -i :8000 -P -n` should show nothing.

Run: `BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev`
Expected: `start_bench` prints `starting bench`, then `bench pid: <N>`. Verify:

```bash
cat ~/frappe-bench-mrv/.mrv/pids/bench.pid    # a PID
ps -p $(cat ~/frappe-bench-mrv/.mrv/pids/bench.pid)  # process exists, "bench start" or "honcho"
lsof -i :8000 -P -n | grep LISTEN                    # something listening within ~10s
```

- [ ] **Step 3.5: Live test — idempotent re-run**

Run: `BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev`
Expected: `--> skipping bench (already running, pid=<N>): already done`. Same pid as before.

- [ ] **Step 3.6: Live test — stale PID detection**

Manually corrupt the PID file:

```bash
echo 99999 > ~/frappe-bench-mrv/.mrv/pids/bench.pid   # likely-dead pid
```

Run: `BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev`
Expected: `bench: stale pid 99999 in .../bench.pid, removing`, then `starting bench`, new pid file written.

- [ ] **Step 3.7: Cleanup before next task**

Kill the test bench so the next task starts clean:

```bash
kill $(cat ~/frappe-bench-mrv/.mrv/pids/bench.pid) 2>/dev/null
sleep 2
# also sweep orphaned bench-managed redis processes (bench start spawns these)
for p in 11000 13000; do
  pid=$(lsof -tiTCP:$p -sTCP:LISTEN 2>/dev/null)
  [[ -n "$pid" ]] && kill "$pid"
done
rm -f ~/frappe-bench-mrv/.mrv/pids/bench.pid
```

- [ ] **Step 3.8: Commit**

```bash
git add start.sh
git commit -m "feat(start.sh): add stale-PID detection and bench background-start"
```

---

## Task 4: bench port discovery + `start_vite` + `wait_for_readiness` + `print_summary`

**Files:**

- Modify: `start.sh` — add port-discovery helper + replace three stubs.

- [ ] **Step 4.0: Add `discover_bench_ports` helper and call it from `main()`**

The bench's actual ports come from `$BENCH_DIR/sites/common_site_config.json` (e.g. a second bench on the same host gets `webserver_port=8001`, `redis_cache=redis://127.0.0.1:13001`, etc.). Hardcoding 8000/9000/13000/11000 makes the scripts only work for the first bench. Defaults stay at the well-known values when the config file or a key is missing.

In `start.sh`, after the `BENCH_LOG=""` / `VITE_LOG=""` lines in the env-defaults block, add:

```bash
WEB_PORT=8000
SOCKETIO_PORT=9000
REDIS_CACHE_PORT=13000
REDIS_QUEUE_PORT=11000
```

Then, after the `verify_bench_dir()` function (and before the `# --- PID file helpers ---` block from Task 3), add:

```bash
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
```

Then in `main()`, insert the call between `verify_bench_dir` and `verify_system_services`:

```bash
main() {
  parse_args "$@"
  detect_os
  init_state_paths
  verify_bench_dir
  discover_bench_ports     # ← new

  verify_system_services
  start_bench
  ...
```

DRY_RUN smoke test: `DRY_RUN=1 BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev` — the new step should print `bench ports: web=8001 socketio=9001 redis_cache=13001 redis_queue=11001` (because the test bench has offset ports). On a default bench it would print `web=8000 socketio=9000 redis_cache=13000 redis_queue=11000`.

- [ ] **Step 4.1: Replace `start_vite` stub**

Replace:

```bash
start_vite()             { step "start_vite";             info "(not yet implemented)"; }
```

With:

```bash
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
```

- [ ] **Step 4.2: Replace `wait_for_readiness` stub**

Replace:

```bash
wait_for_readiness()     { step "wait_for_readiness";     info "(not yet implemented)"; }
```

With:

```bash
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
    printf 'DRY_RUN: poll http://127.0.0.1:%s/api/method/ping (60s)\n' "$WEB_PORT"
    if [[ "$MODE" == "dev" ]]; then
      printf 'DRY_RUN: poll http://127.0.0.1:8080 (30s)\n'
    fi
    return
  fi
  wait_for_url "http://127.0.0.1:$WEB_PORT/api/method/ping" 60 "Frappe (bench)" "$BENCH_LOG"
  if [[ "$MODE" == "dev" ]]; then
    wait_for_url "http://127.0.0.1:8080" 30 "Vite" "$VITE_LOG"
  fi
}
```

- [ ] **Step 4.3: Replace `print_summary` stub**

Replace:

```bash
print_summary()          { step "print_summary";          info "(not yet implemented)"; }
```

With:

```bash
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
```

- [ ] **Step 4.4: DRY_RUN smoke test**

Run: `DRY_RUN=1 BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev`
Expected: `start_vite` shows DRY_RUN lines for `cd ... yarn dev`. `wait_for_readiness` prints DRY_RUN lines for both URLs. `print_summary` prints the URL block.

- [ ] **Step 4.5: Live test — full dev stack startup**

The test bench `~/frappe-bench-mrv` runs on offset ports (8001/9001/11001/13001) because `~/frappe-bench` already uses the defaults. The discover_bench_ports step at the start of the run will print which ports are in use; expected output below uses 8001 for that reason. On a default-port bench, substitute 8000.

Pre-check (use the bench's actual web port — read from `$BENCH_DIR/sites/common_site_config.json` or just `cat`): ports for that bench are free, PID files absent.

Run: `BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev`
Expected output ends with:

```text
==> wait_for_readiness
    waiting for Frappe (bench) at http://127.0.0.1:8001/api/method/ping (timeout 60s)
    Frappe (bench) is up after Ns
    waiting for Vite at http://127.0.0.1:8080 (timeout 30s)
    Vite is up after Ns

==> print_summary

Stack is up.

  Frappe:  http://mrv.localhost:8001   (logs: tail -f .../bench.log)
  Vite:    http://localhost:8080       (logs: tail -f .../vite.log)
  Stop:    ./shutdown.sh

==> start.sh finished (mode=dev)
```

Verify URL responds in another shell: `curl -I http://127.0.0.1:8001` → expect `HTTP/1.1 200`.
Verify Vite responds: `curl -I http://127.0.0.1:8080` → expect `HTTP/1.1 200`.

- [ ] **Step 4.6: Live test — Vite already running, skip path**

Re-run: `BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev`
Expected: both `start_bench` and `start_vite` print `--> skipping ... (already running, pid=N): already done`. Readiness still passes immediately.

- [ ] **Step 4.7: Live test — readiness timeout simulation**

Stop bench (leaves Vite alone, simulates a half-up state). Use the (yet-to-be-built) Task 7 logic manually:

```bash
kill $(cat ~/frappe-bench-mrv/.mrv/pids/bench.pid)
sleep 2
rm -f ~/frappe-bench-mrv/.mrv/pids/bench.pid
# Force-fail bench: temporarily move the bench binary out of PATH
hash -d bench 2>/dev/null || true
PATH=/usr/bin:/bin BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev || echo "exit=$?"
```

Expected: `start_bench` runs (since `nohup bench` would fail), `wait_for_readiness` times out at 60s with `ERR: Frappe (bench) did not respond within 60s. Last 20 lines of ...`, then `exit=1`.

(If `nohup bench` errors out before backgrounding, the trap will fire earlier — also acceptable, exit=1.)

Cleanup before next task (use the bench's actual redis ports — for `~/frappe-bench-mrv` they are 11001/13001):

```bash
# remove the broken pid file
rm -f ~/frappe-bench-mrv/.mrv/pids/bench.pid
# kill any half-started bench/vite
kill $(cat ~/frappe-bench-mrv/.mrv/pids/vite.pid) 2>/dev/null
rm -f ~/frappe-bench-mrv/.mrv/pids/vite.pid
for p in 11001 13001 8080; do
  pid=$(lsof -tiTCP:$p -sTCP:LISTEN 2>/dev/null)
  [[ -n "$pid" ]] && kill "$pid"
done
```

- [ ] **Step 4.8: Commit**

```bash
git add start.sh
git commit -m "feat(start.sh): start vite, wait for readiness, print summary"
```

---

## Task 5: supervisor detection for `--prod` in `start_bench`

**Files:**

- Modify: `start.sh` — extend `start_bench` with a supervisor probe.

- [ ] **Step 5.1: Add `_bench_managed_by_supervisor` helper above `start_bench`**

In `start.sh`, just above the `start_bench` function, insert:

```bash
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
```

- [ ] **Step 5.2: Add the supervisor short-circuit at the top of `start_bench`**

Find the existing `start_bench()` function. Insert the supervisor check between `step "start_bench"` and the existing `local status` line:

```bash
start_bench() {
  step "start_bench"
  if [[ "$MODE" == "prod" ]] && _bench_managed_by_supervisor; then
    skip "bench (managed by supervisor)"
    return
  fi
  local status
  status="$(check_or_clean_pid bench "$BENCH_PID_FILE")"
  # ... (rest unchanged)
```

- [ ] **Step 5.3: DRY_RUN test on the dev mac (no supervisor)**

Run: `DRY_RUN=1 BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --prod`
Expected: `start_bench` does NOT print `managed by supervisor`. It proceeds to the DRY_RUN bench-start lines. (On the mac, `pgrep -f supervisord` finds nothing, so the check returns 1.)

Note: this test only confirms the negative path. The positive path (supervisor present) can only be exercised on a real prod box. The implementation is small and the spec calls this out as a known limitation.

- [ ] **Step 5.4: Commit**

```bash
git add start.sh
git commit -m "feat(start.sh): skip bench-start in --prod when supervisor manages bench"
```

---

## Task 6: `shutdown.sh` skeleton — args, env, helpers, no-op phases

**Files:**

- Create: `shutdown.sh`

- [ ] **Step 6.1: Create `shutdown.sh`**

```bash
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

# --- Phases (filled in by later tasks) -----------------------------------
stop_tracked_processes() { step "stop_tracked_processes"; info "(not yet implemented)"; }
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
```

- [ ] **Step 6.2: Make executable**

Run: `chmod +x shutdown.sh`

- [ ] **Step 6.3: Verify arg parsing — bogus arg**

Run: `./shutdown.sh --bogus; echo "exit=$?"`
Expected: `ERR: Unknown argument: --bogus`, usage, `exit=2`

- [ ] **Step 6.4: Verify arg parsing — help**

Run: `./shutdown.sh --help; echo "exit=$?"`
Expected: usage, `exit=0`

- [ ] **Step 6.5: Verify happy-path skeleton runs against existing bench**

Run: `BENCH_DIR=$HOME/frappe-bench-mrv ./shutdown.sh`
Expected: each phase prints `(not yet implemented)`, finishes with `==> shutdown.sh finished (full=0)`.

- [ ] **Step 6.6: Commit**

```bash
git add shutdown.sh
git commit -m "feat(shutdown.sh): scaffold script with args, env, helpers, no-op phases"
```

---

## Task 7: `stop_tracked_processes` in `shutdown.sh`

**Files:**

- Modify: `shutdown.sh` — replace one stub, add a helper.

- [ ] **Step 7.1: Add the `stop_pid` helper above the phase stubs**

In `shutdown.sh`, after `init_state_paths()` and before `stop_tracked_processes`:

```bash
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
```

- [ ] **Step 7.2: Replace the `stop_tracked_processes` stub**

```bash
stop_tracked_processes() {
  step "stop_tracked_processes"
  # Reverse of start order: vite first (so it doesn't error-spam during bench shutdown), then bench.
  stop_pid vite  "$VITE_PID_FILE"
  stop_pid bench "$BENCH_PID_FILE"
}
```

- [ ] **Step 7.3: Live test — start, then shutdown**

```bash
BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev
# wait for readiness... then:
BENCH_DIR=$HOME/frappe-bench-mrv ./shutdown.sh
```

Expected `shutdown.sh` output:

```text
==> stop_tracked_processes
    vite: SIGTERM pid <N>
    vite: stopped
    bench: SIGTERM pid <N>
    bench: stopped
```

Verify: `ls ~/frappe-bench-mrv/.mrv/pids/` is empty. `lsof -i :8000 -i :8080 -P -n` shows nothing.

(Bench-managed redis on 11000/13000 may still be alive — that's the orphan sweep's job in Task 8.)

- [ ] **Step 7.4: Live test — shutdown when nothing is running**

Run: `BENCH_DIR=$HOME/frappe-bench-mrv ./shutdown.sh`
Expected:

```text
==> stop_tracked_processes
    vite: no pid file
    bench: no pid file
```

Exit 0.

- [ ] **Step 7.5: Live test — stale pid file**

```bash
mkdir -p ~/frappe-bench-mrv/.mrv/pids
echo 99999 > ~/frappe-bench-mrv/.mrv/pids/bench.pid
BENCH_DIR=$HOME/frappe-bench-mrv ./shutdown.sh
ls ~/frappe-bench-mrv/.mrv/pids/
```

Expected:

```text
bench: pid file present but process not running (pid=99999)
```

PID file is removed.

- [ ] **Step 7.6: Cleanup orphan redis (manual, before next task verifies the sweep)**

```bash
for p in 11000 13000; do
  pid=$(lsof -tiTCP:$p -sTCP:LISTEN 2>/dev/null)
  [[ -n "$pid" ]] && kill "$pid"
done
```

- [ ] **Step 7.7: Commit**

```bash
git add shutdown.sh
git commit -m "feat(shutdown.sh): stop tracked bench and vite processes via pid files"
```

---

## Task 8: orphan port sweep in `shutdown.sh`

**Files:**

- Modify: `shutdown.sh` — replace `sweep_orphan_ports` stub.

- [ ] **Step 8.1: Replace the `sweep_orphan_ports` stub**

```bash
sweep_orphan_ports() {
  step "sweep_orphan_ports"
  if ! command -v lsof &>/dev/null; then
    warn "lsof not found; cannot sweep orphan ports"
    return
  fi
  local me port pid_list pid cmd
  me="$(id -un)"
  for port in "${SWEEP_PORTS[@]}"; do
    # -t = pid only, one per line
    pid_list="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
    [[ -z "$pid_list" ]] && continue
    while IFS= read -r pid; do
      [[ -z "$pid" ]] && continue
      # Skip pids we don't own (avoid touching root/system processes).
      local owner
      owner="$(ps -o user= -p "$pid" 2>/dev/null | tr -d '[:space:]')"
      if [[ "$owner" != "$me" ]]; then
        info "port $port held by pid $pid (user=$owner) — not ours, skipping"
        continue
      fi
      cmd="$(ps -o comm= -p "$pid" 2>/dev/null | awk -F/ '{print $NF}' | tr -d '[:space:]')"
      if [[ ! "$cmd" =~ $ORPHAN_COMMANDS_REGEX ]]; then
        info "port $port held by pid $pid (cmd=$cmd) — not in allowlist, skipping"
        continue
      fi
      info "port $port: orphan $cmd (pid=$pid), SIGTERM"
      if [[ "$DRY_RUN" == "1" ]]; then
        printf 'DRY_RUN: kill -TERM %s; wait up to 10s; SIGKILL if alive\n' "$pid"
        continue
      fi
      kill -TERM "$pid" 2>/dev/null || true
      local waited=0
      while pid_alive "$pid" && (( waited < 10 )); do
        sleep 1
        waited=$((waited + 1))
      done
      if pid_alive "$pid"; then
        warn "port $port: pid $pid did not exit on SIGTERM; SIGKILL"
        kill -KILL "$pid" 2>/dev/null || true
      fi
    done <<<"$pid_list"
  done
}
```

- [ ] **Step 8.2: Live test — orphan redis cleanup (the original bug)**

Reproduce the orphan scenario:

```bash
BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev
# wait for readiness
# SIGKILL bench (its pid file lingers; bench-managed redis becomes orphan)
kill -9 $(cat ~/frappe-bench-mrv/.mrv/pids/bench.pid)
sleep 1
lsof -i :11000 -i :13000 -P -n     # confirm orphans exist
```

Expected `lsof` output: `redis-server` LISTEN on both ports, PPID 1.

Now run shutdown:

```bash
BENCH_DIR=$HOME/frappe-bench-mrv ./shutdown.sh
```

Expected output (excerpt):

```text
==> stop_tracked_processes
    vite: SIGTERM pid <N>
    vite: stopped
    bench: pid file present but process not running (pid=<N>)
==> sweep_orphan_ports
    port 11000: orphan redis-ser (pid=<N>), SIGTERM
    port 13000: orphan redis-ser (pid=<N>), SIGTERM
```

Verify clean: `lsof -i :8000 -i :8080 -i :9000 -i :11000 -i :13000 -P -n` returns nothing.

- [ ] **Step 8.3: Live test — sweep is idempotent / safe when nothing is bound**

Run: `BENCH_DIR=$HOME/frappe-bench-mrv ./shutdown.sh`
Expected: `sweep_orphan_ports` produces no per-port lines (all ports already empty). Exit 0.

- [ ] **Step 8.4: Commit**

```bash
git add shutdown.sh
git commit -m "feat(shutdown.sh): orphan port sweep for bench/vite/redis listeners"
```

---

## Task 9: `--full` system-services stop + `final_verification`

**Files:**

- Modify: `shutdown.sh` — replace two stubs.

- [ ] **Step 9.1: Replace `stop_system_services` stub**

```bash
stop_system_services() {
  step "stop_system_services"
  if [[ "$OS" == "macos" ]]; then
    run brew services stop mariadb
    run brew services stop redis
  else
    if [[ "$IS_WSL" == "1" ]]; then
      run sudo service mariadb stop
      run sudo service redis-server stop
    else
      run sudo systemctl stop mariadb redis-server
    fi
  fi
}
```

- [ ] **Step 9.2: Replace `final_verification` stub**

```bash
final_verification() {
  step "final_verification"
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'DRY_RUN: re-check sweep ports for any remaining listeners\n'
    return
  fi
  if ! command -v lsof &>/dev/null; then
    warn "lsof not found; skipping verification"
    return
  fi
  local port out remaining=0
  for port in "${SWEEP_PORTS[@]}"; do
    out="$(lsof -iTCP:"$port" -sTCP:LISTEN -P -n 2>/dev/null | tail -n +2 || true)"
    if [[ -n "$out" ]]; then
      remaining=1
      err "port $port still bound:"
      printf '%s\n' "$out" >&2
    fi
  done
  if (( remaining )); then
    err "shutdown incomplete — see above"
    exit 1
  fi
  info "all stopped"
}
```

- [ ] **Step 9.3: DRY_RUN test for `--full`**

Run: `DRY_RUN=1 BENCH_DIR=$HOME/frappe-bench-mrv ./shutdown.sh --full`
Expected: `stop_system_services` prints `DRY_RUN: brew services stop mariadb` and `DRY_RUN: brew services stop redis`. `final_verification` prints DRY_RUN line.

- [ ] **Step 9.4: Live test — soft shutdown final verification**

```bash
BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev
# wait for readiness
BENCH_DIR=$HOME/frappe-bench-mrv ./shutdown.sh
```

Expected: ends with `==> final_verification` then `all stopped`. Exit 0.
Verify: `brew services list | grep -E '^(mariadb|redis)'` still shows `started` — system services were NOT touched.

- [ ] **Step 9.5: Live test — `--full` actually stops system services**

```bash
BENCH_DIR=$HOME/frappe-bench-mrv ./shutdown.sh --full
brew services list | grep -E '^(mariadb|redis)'
```

Expected: `--full` prints `Stopping ...` lines from brew. `brew services list` shows both as `stopped` (or `none`).

Restart them so other work isn't broken:

```bash
brew services start mariadb
brew services start redis
```

- [ ] **Step 9.6: Commit**

```bash
git add shutdown.sh
git commit -m "feat(shutdown.sh): --full system-services stop and final port verification"
```

---

## Task 10: wire `start.sh` into `install.sh`

**Files:**

- Modify: `install.sh` — add a `start_services` phase, wire it into `main()`, trim the `configure_dev` next-steps block.

- [ ] **Step 10.1: Add the `start_services` function near the bottom of `install.sh`**

Insert the function after `configure_prod()` and before `# --- Arg parsing ---`:

```bash
start_services() {
  step "start_services"
  run "$SCRIPT_DIR/start.sh" "--$MODE"
}
```

- [ ] **Step 10.2: Trim `configure_dev` so it doesn't duplicate `start.sh`'s output**

Locate the existing `configure_dev` function in `install.sh`:

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
```

Replace it with:

```bash
configure_dev() {
  step "configure_dev"
  info "site_config patched (developer_mode=1, ignore_csrf=1)"
  info "starting services..."
  info "(admin user: 'Administrator', password: '$ADMIN_PASSWORD')"
}
```

- [ ] **Step 10.3: Wire `start_services` into `main()`**

Locate the existing `main()` in `install.sh`:

```bash
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
```

Replace with (only the addition of `start_services` after the dev/prod branch):

```bash
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

  start_services

  printf '\n==> install.sh finished (mode=%s)\n' "$MODE" >&2
}
```

- [ ] **Step 10.4: DRY_RUN smoke test**

Run: `DRY_RUN=1 MYSQL_ROOT_PASSWORD=test BENCH_DIR=$HOME/frappe-bench-mrv ./install.sh --dev`
Expected: every existing phase shows `DRY_RUN:` lines (or skip-because-already-done lines), then a new `==> start_services` step that delegates to `start.sh --dev` (which runs but in DRY_RUN mode, since the env propagates).

- [ ] **Step 10.5: Live end-to-end test against an existing install**

Make sure shutdown.sh has cleaned everything first:

```bash
BENCH_DIR=$HOME/frappe-bench-mrv ./shutdown.sh
```

Then re-run install:

```bash
MYSQL_ROOT_PASSWORD=catch22 BENCH_DIR=$HOME/frappe-bench-mrv ./install.sh --dev
```

Expected: all install phases skip (already-done), then `==> start_services` runs, then `==> start.sh finished (mode=dev)`, then `==> install.sh finished (mode=dev)`. `curl -I http://127.0.0.1:8000` returns 200.

- [ ] **Step 10.6: Cleanup**

```bash
BENCH_DIR=$HOME/frappe-bench-mrv ./shutdown.sh
```

- [ ] **Step 10.7: Commit**

```bash
git add install.sh
git commit -m "feat(install.sh): start the stack at the end of install via start.sh"
```

---

## Task 11: update `install.md`

**Files:**

- Modify: `install.md`

- [ ] **Step 11.1: Update the top paragraph**

Find:

```markdown
One command bootstraps a fresh laptop or server into a working MRV Solomon Islands environment. Runs on **macOS**, **Ubuntu**, and **Windows (via WSL2 + Ubuntu)**.
```

Replace with:

```markdown
One command bootstraps a fresh laptop or server into a working MRV Solomon Islands environment, **with the stack started and the URL live when the script exits**. Runs on **macOS**, **Ubuntu**, and **Windows (via WSL2 + Ubuntu)**. After install, `start.sh` and `shutdown.sh` manage the stack day-to-day.
```

- [ ] **Step 11.2: Add new "Service lifecycle" section between "What the script does" and "Environment variables"**

Insert this section immediately after "9. **Mode-specific finishing:** ..." (step 9 of the install flow) and before "## Environment variables":

```markdown
## Service lifecycle

After install, three scripts manage the stack:

| Script | What it does |
| --- | --- |
| `./install.sh --dev|--prod` | One-time bootstrap. Final phase calls `start.sh`. |
| `./start.sh --dev|--prod` | Bring up an installed stack. Idempotent — re-running with services already up is a no-op. |
| `./shutdown.sh` | Soft stop: bench + Vite. Leaves system MariaDB and Redis running. |
| `./shutdown.sh --full` | Full teardown: also stops MariaDB and Redis system services. |

State files (created by `start.sh` on first run, survive reboot):

- PIDs: `$BENCH_DIR/.mrv/pids/{bench,vite}.pid`
- Logs: `$BENCH_DIR/.mrv/logs/{bench,vite}.log`

Tail logs with `tail -f $BENCH_DIR/.mrv/logs/bench.log` (or `vite.log`).

`shutdown.sh` always runs an orphan-port sweep over `8000, 8080, 9000, 11000, 13000` — safe to run any time, even when nothing is recorded in the PID files (it cleans up bench-managed Redis processes left behind by a hard kill).

**Production note:** real prod stacks managed by supervisor (set up by `bench setup production` during `--prod` install) are detected automatically. `start.sh --prod` will skip the bench-start step if it sees supervisor managing bench, and `shutdown.sh` does NOT stop supervisor — full prod teardown requires `./shutdown.sh --full` plus `sudo supervisorctl stop <bench-group>`.
```

- [ ] **Step 11.3: Update "Quick starts → Developer laptop"**

Find:

```markdown
### Developer laptop (macOS or Linux)

```bash
# Clone, cd in, then:
MYSQL_ROOT_PASSWORD=changeme ./install.sh --dev

# Then, in two terminals:
cd ~/frappe-bench && bench start                          # terminal A
cd <repo>/frontend && yarn dev                            # terminal B

# Open http://mrv.localhost:8000
```
```

Replace with:

```markdown
### Developer laptop (macOS or Linux)

```bash
# Clone, cd in, then:
MYSQL_ROOT_PASSWORD=changeme ./install.sh --dev

# When install.sh exits, the URL is already live:
#   http://mrv.localhost:8000
# Logs:    tail -f ~/frappe-bench/.mrv/logs/bench.log
# Stop:    ./shutdown.sh
# Restart: ./start.sh --dev
```
```

- [ ] **Step 11.4: Update "Uninstall"**

Find:

```markdown
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
```

Replace with:

```markdown
The script does not provide a destroy command. To remove a dev install:

```bash
# stop everything, including system services
./shutdown.sh --full

# drop the bench (includes the site and all fetched apps)
rm -rf ~/frappe-bench

# (optional) uninstall packages
# macOS:
brew uninstall mariadb redis node@18 yarn wkhtmltopdf
# Ubuntu:
sudo apt-get remove mariadb-server redis-server
```
```

- [ ] **Step 11.5: Add a Troubleshooting row**

Find the troubleshooting table and add this row before the closing of the table (anywhere in the table is fine; suggest just before "wkhtmltopdf PDF export breaks"):

```markdown
| `start.sh` reports stale pid OR port 11000/13000 bound by `redis-server` | Previous `bench start` killed without cleanup, leaving an orphaned bench-managed Redis. | `./shutdown.sh` is safe to run any time — it sweeps orphan listeners on the bench/vite ports. |
```

- [ ] **Step 11.6: Update "See also"**

Find:

```markdown
## See also

- [install.sh](install.sh) — the script itself
- [CLAUDE.md](CLAUDE.md) — high-level repo architecture
- [docs/superpowers/specs/2026-04-19-unified-setup-script-design.md](docs/superpowers/specs/2026-04-19-unified-setup-script-design.md) — full design spec
- [docs/superpowers/plans/2026-04-19-install-manual-deltas.md](docs/superpowers/plans/2026-04-19-install-manual-deltas.md) — deltas applied from the upstream SI-iMRV installation manual
```

Replace with:

```markdown
## See also

- [install.sh](install.sh) — the installer
- [start.sh](start.sh) — bring up an installed stack
- [shutdown.sh](shutdown.sh) — bring it down
- [CLAUDE.md](CLAUDE.md) — high-level repo architecture
- [docs/superpowers/specs/2026-04-19-unified-setup-script-design.md](docs/superpowers/specs/2026-04-19-unified-setup-script-design.md) — installer design spec
- [docs/superpowers/specs/2026-04-19-start-shutdown-scripts-design.md](docs/superpowers/specs/2026-04-19-start-shutdown-scripts-design.md) — start/shutdown scripts design spec
- [docs/superpowers/plans/2026-04-19-install-manual-deltas.md](docs/superpowers/plans/2026-04-19-install-manual-deltas.md) — deltas applied from the upstream SI-iMRV installation manual
```

- [ ] **Step 11.7: Visual review**

Open `install.md` and confirm:

- Top paragraph mentions `start.sh` / `shutdown.sh` and "URL live when the script exits".
- "Service lifecycle" section appears between "What the script does" and "Environment variables".
- "Quick starts → Developer laptop" shows the simplified one-command flow.
- "Uninstall" begins with `./shutdown.sh --full`.
- Troubleshooting table has the new orphan-redis row.
- "See also" lists `start.sh`, `shutdown.sh`, and the new design spec.

- [ ] **Step 11.8: Commit**

```bash
git add install.md
git commit -m "docs(install.md): document start.sh/shutdown.sh lifecycle and orphan recovery"
```

---

## Done

After Task 11, the following invariants hold:

- `./install.sh --dev` ends with a live URL.
- `./start.sh --dev` is idempotent and the standard "bring it up" command after a reboot.
- `./shutdown.sh` cleanly stops the stack and sweeps orphan listeners.
- `./shutdown.sh --full` adds system-services teardown.
- `install.md` documents the new lifecycle and the orphan-recovery troubleshooting row.

Final smoke (run from the repo root, once everything is committed):

```bash
BENCH_DIR=$HOME/frappe-bench-mrv ./shutdown.sh
BENCH_DIR=$HOME/frappe-bench-mrv ./start.sh --dev    # → URL live
curl -I http://127.0.0.1:8000                         # → 200
BENCH_DIR=$HOME/frappe-bench-mrv ./shutdown.sh
lsof -i :8000 -i :8080 -i :9000 -i :11000 -i :13000 -P -n   # → empty
```
