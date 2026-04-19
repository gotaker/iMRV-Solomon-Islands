# Start / Shutdown Scripts — Design

**Date:** 2026-04-19
**Status:** Design (approved)
**Related:** [2026-04-19-unified-setup-script-design.md](2026-04-19-unified-setup-script-design.md)

## Goal

Make the local stack a one-command lifecycle: `install.sh` brings everything up to a working URL, and a clean shutdown is one command away. Today the installer ends with a "next steps" block telling the user to run `bench start` and `yarn dev` in two terminals; there is no shutdown script and orphaned `redis-server` processes from killed bench sessions are a recurring failure mode.

## Scope

In scope:

- New `start.sh` at the repo root: brings up bench + (in dev) Vite, verifies system services (MariaDB, Redis), waits until the URL responds.
- New `shutdown.sh` at the repo root: stops what `start.sh` started, sweeps orphaned ports, and (with `--full`) stops MariaDB/Redis system services.
- `install.sh` invokes `start.sh` as its final phase so install ends with a live URL.
- `install.md` updated to document the lifecycle.

Out of scope:

- Subcommand wrapper (`mrv.sh install|start|stop`). Considered and rejected — too large a change for the value.
- Production supervisor management. `start.sh --prod` is a health check, not a substitute for `supervisorctl`.
- Restart helper. `./shutdown.sh && ./start.sh --dev` is fine; a `restart.sh` is YAGNI for now.

## Approach

Three scripts, symmetric:

```text
install.sh   one-time bootstrap (existing) — last phase calls start.sh
start.sh     bring up an installed stack (new)
shutdown.sh  bring it down (new)
```

`start.sh` and `shutdown.sh` are mirror operations against the same per-bench state directory, so they can be re-run independently of install.sh after a reboot.

**Why three scripts, not phases inside install.sh:** install is one-time; start/stop is daily. Folding start into install means a reboot (or a desired restart) requires re-running the whole installer or doing manual `bench start` / `yarn dev`. Symmetric `start.sh` / `shutdown.sh` also makes the shutdown logic easier to reason about — it knows exactly what start created.

**Why background with PID files (not tmux, not foreground-blocking):** PID files keep `install.sh` exit-clean (so it can be re-run idempotently without orphaning a hung foreground process), and they give shutdown a precise, race-free target. The orphaned-redis problem we hit during development is exactly what stale-PID detection prevents on next start/shutdown.

## File layout & state

State lives inside the bench, not in `/tmp` and not in the repo:

```text
$BENCH_DIR/.mrv/
├── pids/
│   ├── bench.pid          # pid of `bench start`
│   └── vite.pid           # pid of `yarn dev` (dev only)
└── logs/
    ├── bench.log          # stdout+stderr from bench
    └── vite.log           # stdout+stderr from Vite
```

Rationale: `BENCH_DIR` is the natural home (both scripts already know it), surviving a reboot is a feature (a stale PID with no live process is exactly the signal shutdown needs to do orphan cleanup), and multi-bench support comes free since each bench has its own `.mrv/`.

## Shared env contract

Both new scripts source the same defaults block `install.sh` already uses, so a custom `BENCH_DIR` flows through all three identically. No new env vars are introduced.

| Variable | Default | Purpose |
| --- | --- | --- |
| `BENCH_DIR` | `$HOME/frappe-bench` | Where bench lives. |
| `SITE_NAME` | `mrv.localhost` | Site name (used for URL hint). |
| `MRVTOOLS_SRC` | this repo's path | Used by `start.sh` to find the `frontend/` dir for `yarn dev`. |
| `DRY_RUN` | `0` | Honored by both new scripts via the same `run`/`run_sh` helpers as install.sh. |

`MYSQL_ROOT_PASSWORD` is **not** required by `start.sh` or `shutdown.sh` — bench reads its own credentials from `site_config.json`.

## `start.sh`

**Invocation:** `./start.sh --dev | --prod`

**Phases (in order):**

1. **Verify system services** (the OS-level dependencies installed by `install.sh`).
   - macOS: `brew services list` — if `mariadb` / `redis` not started, `brew services start <svc>`.
   - Ubuntu/WSL2: `systemctl is-active` (or `service <name> status` on WSL2). Start if down. If not root and they're already up, skip with a warning.
2. **Pre-flight: stale PID detection.** For each pid file:
   - If file exists and PID is dead → log `stale pid, removing` and unlink.
   - If PID is alive → skip starting that process (idempotent re-run).
   - If file missing → start fresh.
3. **Start bench.** In `--prod`, first check if supervisor is already managing bench (`pgrep -f supervisord` AND presence of `/etc/supervisor/conf.d/frappe-bench-*`); if so, skip with `bench managed by supervisor, skipping`. Otherwise:
   - `cd $BENCH_DIR && nohup bench start >>$BENCH_DIR/.mrv/logs/bench.log 2>&1 &`
   - `echo $! > $BENCH_DIR/.mrv/pids/bench.pid`
4. **Start Vite** (dev only).
   - `cd $MRVTOOLS_SRC/frontend && nohup yarn dev >>$BENCH_DIR/.mrv/logs/vite.log 2>&1 &`
   - `echo $! > $BENCH_DIR/.mrv/pids/vite.pid`
5. **Wait for readiness.**
   - Poll `curl -fsS http://127.0.0.1:8000/api/method/ping` every 1s, 60s timeout.
   - Dev only: also poll `curl -fsS http://127.0.0.1:8080`, 30s timeout.
   - On timeout → print last 20 lines of the relevant log + non-zero exit.
6. **Print URLs and tail hints** on success:

   ```text
   Frappe:  http://mrv.localhost:8000   (logs: tail -f $BENCH_DIR/.mrv/logs/bench.log)
   Vite:    http://localhost:8080       (logs: tail -f $BENCH_DIR/.mrv/logs/vite.log)
   Stop:    ./shutdown.sh
   ```

**On `--prod` and supervisor:** in a real prod install, `bench setup production` configures supervisor to manage bench, so a manual `bench start` would conflict. Phase 3's supervisor probe handles this — if supervisor is running and a `frappe-bench-*` conf is present, `start.sh --prod` skips the bench-start step and treats itself as a verification path (system services up, supervisor managing bench, ready). On a dev-flavored install run with `--prod` (no supervisor), bench is started normally.

**Exit codes:**

- `0` — all started (or already running)
- `1` — startup failure (timeout, service refused, port held by foreign process)
- `2` — argument or env error

## `shutdown.sh`

**Invocation:** `./shutdown.sh` (default = soft) or `./shutdown.sh --full`

**Phases (in order):**

1. **Resolve `BENCH_DIR`** from env or default. If `$BENCH_DIR/.mrv/pids/` doesn't exist, log `no managed services found` and continue to step 4 (orphan cleanup) — stale processes from older runs are exactly when shutdown is most needed.
2. **Stop tracked processes** (Vite first, then bench — reverse start order, since Vite proxying to bench can throw noisy errors if bench dies first):
   - For each pid file: read pid; if alive → `kill -TERM <pid>`; wait up to 10s for exit; if still alive → `kill -KILL <pid>`; remove pid file.
   - If pid file missing or pid dead → log `not running`, continue (no error).
3. **Orphan port sweep.** Scan `lsof -iTCP:8000,8080,9000,11000,13000 -sTCP:LISTEN`. For any listener whose pid is the user's own and whose command name is in `{bench, node, redis-server, gunicorn}`, log + SIGTERM (10s wait) → SIGKILL. (This catches the orphan-redis case where bench died without cleanup.)
4. **`--full` only:** stop MariaDB and Redis system services.
   - macOS: `brew services stop mariadb && brew services stop redis`.
   - Ubuntu native: `sudo systemctl stop mariadb redis-server`.
   - Ubuntu WSL2: `sudo service mariadb stop && sudo service redis-server stop`.
5. **Final verification.** Re-check the same port list — if anything is still bound, print which command holds it and exit non-zero. Otherwise print `all stopped` and exit 0.

**No `--dev`/`--prod` flag** — shutdown infers what's running from PID files + ports. Prod note: in real production, supervisor will restart anything we kill. Full prod teardown requires `--full` *plus* `sudo supervisorctl stop <bench-group>`; this is documented in install.md, not implemented in shutdown.sh.

**Exit codes:**

- `0` — everything down
- `1` — something still running after attempts
- `2` — argument error

## `install.sh` changes

Minimal and additive — no restructuring of existing phases.

1. **New phase function** at the bottom of the script:

   ```sh
   start_services() {
     step "start_services"
     run "$SCRIPT_DIR/start.sh" "--$MODE"
   }
   ```

2. **Wire into `main()`** after the mode-specific configure step:

   ```sh
   if [[ "$MODE" == "dev" ]]; then
     patch_site_config
     configure_dev
   else
     configure_prod
   fi
   start_services      # ← new
   ```

3. **Trim `configure_dev`'s "Next steps" block** so it no longer instructs the user to run `bench start` / `yarn dev` manually. Replace with one line: `Starting services...`. The actual URL output comes from `start.sh` so we don't duplicate it.
4. **`configure_prod`** is unchanged.
5. **`DRY_RUN=1` flow:** `start.sh` honors `DRY_RUN` itself, so `start_services` prints what would happen.

## `install.md` updates

Edits, not a rewrite:

1. **Top of file** — change the "one command bootstraps" paragraph to note that install also *starts* the stack; the URL is live when the script exits.
2. **New section "Service lifecycle"** between "What the script does" and "Environment variables":
   - `./start.sh --dev|--prod` — start an installed stack. Idempotent.
   - `./shutdown.sh` — soft stop (bench + Vite only). Leaves system MariaDB/Redis up.
   - `./shutdown.sh --full` — full teardown including system services.
   - PID files at `$BENCH_DIR/.mrv/pids/`, logs at `$BENCH_DIR/.mrv/logs/`.
   - Note that prod uses supervisor; `start.sh --prod` is a health check, not a substitute for `supervisorctl`.
3. **"Quick starts → Developer laptop"** — replace the two-terminal `bench start` / `yarn dev` instructions with: install completes → URL is live → `./shutdown.sh` when done.
4. **"Uninstall"** — prepend `./shutdown.sh --full` before the `rm -rf` and `brew services stop` lines.
5. **"Troubleshooting"** — new row:
   - *Symptom:* `start.sh` reports "stale pid, removing" or port 13000/11000 bound by orphaned `redis-server`.
   - *Cause:* previous `bench start` killed without cleanup.
   - *Fix:* `./shutdown.sh` is safe to run any time — it sweeps orphan ports.
6. **"See also"** — add `start.sh` and `shutdown.sh` lines.

## Idempotency contracts

- `start.sh` re-run with services already up → prints `already running, pid=N` for each, exit 0.
- `start.sh` re-run after a dirty shutdown → detects stale PIDs, removes, restarts cleanly.
- `shutdown.sh` re-run when nothing is up → prints `nothing to stop`, exit 0.
- Pid files are the source of truth; ports are the fallback (catches orphans).

## Edge cases handled

- `BENCH_DIR` not set or doesn't exist → `start.sh` exits with helpful "run install.sh first" message.
- MariaDB/Redis not installed → `start.sh` prints clear "install.sh needs to run first", non-zero exit. Doesn't try to install them.
- Vite port 8080 held by something else → `start.sh` detects on readiness probe and reports.
- `bench start` crashes inside the first 60s → readiness times out, last 20 lines of `bench.log` are dumped.
- `DRY_RUN=1` honored in both new scripts via the same `run`/`run_sh` helpers as `install.sh`.
- Supervisor-managed bench in real prod → `start.sh --prod` detects and skips the bench-start step.

## Testing approach

No Frappe test runner needed — these are bash scripts.

- `DRY_RUN=1 ./start.sh --dev` and `DRY_RUN=1 ./shutdown.sh --full` on the dev box; spot-check command output.
- Live test against the existing `~/frappe-bench-mrv` install:
  1. `./shutdown.sh` (current state — verify it handles "nothing to stop")
  2. `./start.sh --dev` — verify URL responds within timeout
  3. `./start.sh --dev` again — verify idempotent skip
  4. `./shutdown.sh` — verify ports free
- Manually kill `bench start` (SIGKILL) leaving an orphaned redis, then `./shutdown.sh` — verify orphan cleanup.
- Run install.sh end-to-end (against a different `BENCH_DIR`) and confirm it ends with a live URL.

## Risks

- **Vite log under bench's `.mrv/`** — colocates Vite log with bench state even though Vite runs from the source repo, not bench. Acceptable: keeps shutdown's log search single-rooted.
- **Orphan port sweep is heuristic** — matching by command name (`redis-server`, `node`) could in theory hit a user-owned process from another project. Scoped to the user's own pids and the specific bench/Vite ports list, so blast radius is small. Worst case: user gets a clear log line about which pid was killed and can re-launch their other thing.
- **`start.sh --prod` divergence from real prod** — supervisor detection is the only safety net. If detection fails and supervisor is running, we'd start a duplicate `bench`. Mitigation: detect via both `pgrep -f supervisord` and presence of `/etc/supervisor/conf.d/frappe-bench-*` files.
