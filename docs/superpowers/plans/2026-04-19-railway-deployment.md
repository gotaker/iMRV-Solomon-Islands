# Railway Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy the full MRV stack (Frappe desk + SPA + login + persistent data) to Railway as a single-container monolith running Supervisor, with MariaDB and Redis as separate Railway services.

**Architecture:** Multi-stage Dockerfile at repo root. Stage 1 builds the Vue SPA. Stage 2 runs `bench init` (Frappe v15), stages both Frappe apps, installs them, then runs Supervisor managing gunicorn + node socketio + 2 RQ workers + scheduler behind Nginx. An entrypoint script bootstraps the Frappe site on first boot and runs `bench migrate` on subsequent boots. MariaDB 10.6 and Redis are Railway services wired via env-var-driven `common_site_config.json`.

**Tech Stack:** Docker (multi-stage), Python 3.11, Node 20, Frappe v15, MariaDB 10.6, Redis 7, Supervisor, Nginx, `envsubst`, Railway.

**Spec:** [docs/superpowers/specs/2026-04-19-railway-deployment-design.md](../specs/2026-04-19-railway-deployment-design.md)

**Note on TDD:** Container plumbing doesn't fit classical TDD — the "test" for each Dockerfile step is `docker build --target <stage>` succeeding and a local `docker compose up` producing expected runtime state. Verification commands are explicit at each step. Phase 2 introduces a `docker-compose.yml` purely for local integration testing before we touch Railway.

**File map:**

```
/
├── Dockerfile                              [new]
├── .dockerignore                           [new]
├── railway.json                            [new]
└── deploy/
    └── railway/
        ├── README.md                       [new — operator runbook]
        ├── supervisord.conf                [new]
        ├── nginx.conf.template             [new]
        ├── entrypoint.sh                   [new — rendered + run as PID 1]
        └── docker-compose.local.yml        [new — local integration test only]
```

No existing files are modified.

---

## Phase 1: Container image

### Task 1: Scaffold `deploy/railway/` + `.dockerignore`

**Files:**
- Create: `deploy/railway/` directory
- Create: `.dockerignore`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p deploy/railway
```

- [ ] **Step 2: Write `.dockerignore`** at repo root

```
.git
.github
docs
frontend/node_modules
frontend/dist
mrvtools/public/frontend
mrvtools/www/frontend.html
frappe-bench
*.pyc
__pycache__
.venv
venv
.env
.DS_Store
node_modules
```

Rationale: keeps build context small. The `mrvtools/public/frontend` and `mrvtools/www/frontend.html` exclusions are important — those are SPA build artifacts the Dockerfile will regenerate; stale local copies would otherwise get COPY'd into the image.

- [ ] **Step 3: Verify context size**

```bash
docker build --progress=plain --no-cache -f /dev/null --build-arg _ . 2>&1 | grep "sending build context"
```

Expected: build context <50 MB. If it's >200 MB, `.dockerignore` isn't being honored.

- [ ] **Step 4: Commit**

```bash
git add .dockerignore deploy/railway
git commit -m "chore(railway): scaffold deploy directory and dockerignore"
```

---

### Task 2: Dockerfile stage 1 — frontend build

**Files:**
- Create: `Dockerfile`

- [ ] **Step 1: Write stage 1 only**

```dockerfile
# syntax=docker/dockerfile:1.7

# ---------- Stage 1: Build Vue SPA ----------
FROM node:20-alpine AS frontend-build

WORKDIR /build

# Copy only what Vite needs (avoids invalidating cache on unrelated changes)
COPY frontend/package.json frontend/yarn.lock ./frontend/
RUN cd frontend && yarn install --frozen-lockfile

COPY frontend ./frontend
COPY mrvtools/public ./mrvtools/public
COPY mrvtools/www ./mrvtools/www

# The frontend package.json `build` script does:
#   vite build --base=/assets/mrvtools/frontend/ && yarn copy-html-entry
# which writes into ../mrvtools/public/frontend/ and ../mrvtools/www/frontend.html
RUN cd frontend && yarn build

# Sanity — fail the build if expected artifacts are missing
RUN test -d /build/mrvtools/public/frontend \
 && test -f /build/mrvtools/www/frontend.html
```

- [ ] **Step 2: Build stage 1 alone**

```bash
docker build --target frontend-build -t mrv-fe-test .
```

Expected: finishes successfully in ~2–5 min on first run. Subsequent runs hit yarn cache.

- [ ] **Step 3: Inspect artifacts inside the stage image**

```bash
docker run --rm mrv-fe-test ls /build/mrvtools/public/frontend
docker run --rm mrv-fe-test ls /build/mrvtools/www/frontend.html
```

Expected: first command lists built JS/CSS assets; second prints the path (no error).

- [ ] **Step 4: Commit**

```bash
git add Dockerfile
git commit -m "feat(railway): add Dockerfile stage 1 (SPA build)"
```

---

### Task 3: Dockerfile stage 2 — runtime base with system deps

**Files:**
- Modify: `Dockerfile` (append stage 2)

- [ ] **Step 1: Append stage 2 base to `Dockerfile`**

```dockerfile

# ---------- Stage 2: Runtime ----------
FROM python:3.11-slim-bookworm AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PATH=/home/frappe/.local/bin:$PATH

# System deps. wkhtmltopdf is used by Frappe's PDF rendering.
# libmariadb-dev + mariadb-client needed for the mysqlclient Python driver.
# nginx + supervisor are the process orchestration layer.
# gosu lets entrypoint.sh drop from root to frappe user for bench commands.
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      curl \
      git \
      gosu \
      libmariadb-dev \
      libssl-dev \
      mariadb-client \
      nginx \
      pkg-config \
      redis-tools \
      supervisor \
      wkhtmltopdf \
      xfonts-75dpi \
      xfonts-base \
   && rm -rf /var/lib/apt/lists/*

# Node 20 for socketio + yarn
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
 && apt-get install -y --no-install-recommends nodejs \
 && npm install -g yarn \
 && rm -rf /var/lib/apt/lists/*

# Create frappe user (uid 1000 to align with most Linux hosts for volume perms)
RUN groupadd -g 1000 frappe \
 && useradd -m -u 1000 -g 1000 -s /bin/bash frappe

# frappe-bench CLI, installed for the frappe user
USER frappe
WORKDIR /home/frappe
RUN pip install --user --no-cache-dir frappe-bench==5.22.6
USER root
```

- [ ] **Step 2: Build stage 2**

```bash
docker build --target runtime -t mrv-runtime-test .
```

Expected: finishes in ~3–8 min (apt downloads dominate). No errors.

- [ ] **Step 3: Verify key binaries present**

```bash
docker run --rm mrv-runtime-test bash -lc 'which nginx && which supervisord && which wkhtmltopdf && node --version && yarn --version'
docker run --rm -u frappe mrv-runtime-test bash -lc 'which bench && bench --version'
```

Expected: each command prints a path/version. `bench --version` prints `5.22.6`.

- [ ] **Step 4: Commit**

```bash
git add Dockerfile
git commit -m "feat(railway): add Dockerfile stage 2 runtime base (deps + bench)"
```

---

### Task 4: Run `bench init` inside the image

**Files:**
- Modify: `Dockerfile` (append)

- [ ] **Step 1: Append `bench init` to `Dockerfile`**

```dockerfile

# ---------- bench init ----------
# Creates /home/frappe/frappe-bench with frappe framework checked out.
# --skip-assets: we build assets explicitly later (needs apps installed first).
# --skip-redis-config-generation: we point at Railway-managed Redis via
# common_site_config.json at runtime, not the local redis configs bench
# generates by default.
USER frappe
WORKDIR /home/frappe
RUN bench init \
      --python python3.11 \
      --frappe-branch version-15 \
      --skip-assets \
      --skip-redis-config-generation \
      --no-backups \
      frappe-bench

WORKDIR /home/frappe/frappe-bench
```

- [ ] **Step 2: Build and verify `bench init` completed**

```bash
docker build --target runtime -t mrv-runtime-test .
docker run --rm -u frappe mrv-runtime-test bash -lc 'ls /home/frappe/frappe-bench/apps'
```

Expected: `frappe` listed (the Frappe framework clone). Build time: +5–8 min for the first run (bench clones frappe from GitHub, compiles deps). Subsequent builds hit the layer cache.

- [ ] **Step 3: Verify frappe version**

```bash
docker run --rm -u frappe mrv-runtime-test bash -lc 'cd /home/frappe/frappe-bench && bench version'
```

Expected output includes `frappe 15.x.x`.

- [ ] **Step 4: Commit**

```bash
git add Dockerfile
git commit -m "feat(railway): run bench init in Dockerfile (frappe v15)"
```

---

### Task 5: Stage `frappe_side_menu` + install both apps

**Rationale:** `frappe_side_menu` has no standalone `setup.py` in its module dir — it uses the repo-root `setup_sidebarmenu.py`. Per [install.sh:354-386](install.sh#L354-L386), `bench get-app` requires a git repo with `setup.py` at its root, so we stage `frappe_side_menu` into a directory with a copied `setup.py` + `git init`. We do the same inside the image build.

**Files:**
- Modify: `Dockerfile` (append)

- [ ] **Step 1: Append app staging + install to `Dockerfile`**

```dockerfile

# ---------- Stage apps into the build context ----------
USER root

# Copy the whole repo into /src, owned by frappe. We then stage from /src into
# apps/<name> using bench get-app, which requires each source to be a git repo
# with setup.py at its root.
RUN mkdir -p /src && chown frappe:frappe /src
COPY --chown=frappe:frappe . /src

USER frappe
WORKDIR /home/frappe/frappe-bench

# --- Stage mrvtools ---
# The repo root IS the mrvtools Python package (setup.py at /src/setup.py
# installs the mrvtools module at /src/mrvtools). bench get-app calls
# git.Repo(src), so /src must be a git repo — we copied .git via the COPY.
# If .git is excluded by .dockerignore in future, this step will need to
# init a fresh git repo first.
RUN bench get-app --skip-assets mrvtools /src

# --- Stage frappe_side_menu ---
# frappe_side_menu's module lives at /src/frappe_side_menu/ but its setup file
# is /src/setup_sidebarmenu.py. bench get-app can't handle that shape, so we
# stage it into .stage/frappe_side_menu/ with setup.py copied in + git-init'd.
RUN set -eux; \
    STAGE=/home/frappe/frappe-bench/.stage/frappe_side_menu; \
    rm -rf "$STAGE"; \
    mkdir -p "$STAGE"; \
    cp -R /src/frappe_side_menu "$STAGE/frappe_side_menu"; \
    cp /src/setup_sidebarmenu.py "$STAGE/setup.py"; \
    cp /src/requirements.txt "$STAGE/requirements.txt"; \
    if [ -f /src/license.txt ]; then cp /src/license.txt "$STAGE/license.txt"; fi; \
    cd "$STAGE"; \
    git -c init.defaultBranch=master init -q; \
    git add -A; \
    git -c user.name=docker -c user.email=docker@local commit -q -m stage; \
    cd /home/frappe/frappe-bench; \
    bench get-app --skip-assets frappe_side_menu "$STAGE"
```

- [ ] **Step 2: Build and verify both apps landed**

```bash
docker build --target runtime -t mrv-runtime-test .
docker run --rm -u frappe mrv-runtime-test bash -lc 'ls /home/frappe/frappe-bench/apps'
```

Expected: `frappe`, `frappe_side_menu`, `mrvtools` all listed.

- [ ] **Step 3: Verify apps importable**

```bash
docker run --rm -u frappe mrv-runtime-test bash -lc \
  'cd /home/frappe/frappe-bench && env/bin/python -c "import mrvtools; import frappe_side_menu; print(mrvtools.__version__)"'
```

Expected: prints the version from `mrvtools/__init__.py` (e.g. `0.0.1`). No `ImportError`.

- [ ] **Step 4: Commit**

```bash
git add Dockerfile
git commit -m "feat(railway): stage and install mrvtools + frappe_side_menu in image"
```

---

### Task 6: Copy SPA artifacts + run `bench build`

**Files:**
- Modify: `Dockerfile` (append)

- [ ] **Step 1: Append SPA copy + bench build**

```dockerfile

# ---------- Inject pre-built SPA from stage 1 ----------
# The SPA was already built in the frontend-build stage. Copy it into the
# mrvtools app inside the bench so /assets/mrvtools/frontend/ resolves.
COPY --from=frontend-build --chown=frappe:frappe \
    /build/mrvtools/public/frontend \
    /home/frappe/frappe-bench/apps/mrvtools/mrvtools/public/frontend

COPY --from=frontend-build --chown=frappe:frappe \
    /build/mrvtools/www/frontend.html \
    /home/frappe/frappe-bench/apps/mrvtools/mrvtools/www/frontend.html

# ---------- bench build ----------
# Bundles Frappe's own JS/CSS + mrvtools + frappe_side_menu into
# sites/assets/. Required for the Frappe desk to load.
RUN cd /home/frappe/frappe-bench \
 && bench build --apps frappe,mrvtools,frappe_side_menu
```

- [ ] **Step 2: Build and verify assets landed**

```bash
docker build -t mrv-runtime-test .
docker run --rm -u frappe mrv-runtime-test bash -lc \
  'ls /home/frappe/frappe-bench/sites/assets/mrvtools/frontend | head -5'
```

Expected: lists built JS/CSS files (e.g. `index-<hash>.js`, `index-<hash>.css`).

- [ ] **Step 3: Verify SPA HTML entry exists**

```bash
docker run --rm -u frappe mrv-runtime-test bash -lc \
  'test -f /home/frappe/frappe-bench/apps/mrvtools/mrvtools/www/frontend.html && echo OK'
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add Dockerfile
git commit -m "feat(railway): inject built SPA and run bench build"
```

---

### Task 7: Write `supervisord.conf`

**Files:**
- Create: `deploy/railway/supervisord.conf`

- [ ] **Step 1: Write the config**

```ini
; supervisord.conf — runs as PID 1 inside the Railway container
; Manages: gunicorn (web), node socketio, 2 RQ workers, scheduler, nginx

[supervisord]
nodaemon=true
user=root
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid
childlogdir=/var/log/supervisor

[unix_http_server]
file=/var/run/supervisor.sock
chmod=0700

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock

[rpcinterface:supervisor]
supervisor.rpcinterface_factory=supervisor.rpcinterface.make_main_rpcinterface

; ---------- Frappe gunicorn web ----------
[program:frappe-web]
command=/home/frappe/frappe-bench/env/bin/gunicorn
    -b 127.0.0.1:8000
    --workers 4
    --timeout 120
    --worker-tmp-dir /dev/shm
    frappe.app:application
directory=/home/frappe/frappe-bench/sites
user=frappe
autostart=true
autorestart=true
stdout_logfile=/dev/fd/1
stdout_logfile_maxbytes=0
redirect_stderr=true

; ---------- Frappe socketio (realtime) ----------
[program:frappe-socketio]
command=/usr/bin/node /home/frappe/frappe-bench/apps/frappe/socketio.js
directory=/home/frappe/frappe-bench
user=frappe
environment=NODE_ENV="production"
autostart=true
autorestart=true
stdout_logfile=/dev/fd/1
stdout_logfile_maxbytes=0
redirect_stderr=true

; ---------- RQ worker: short queue ----------
[program:frappe-worker-short]
command=/home/frappe/frappe-bench/env/bin/bench worker --queue short
directory=/home/frappe/frappe-bench
user=frappe
autostart=true
autorestart=true
stdout_logfile=/dev/fd/1
stdout_logfile_maxbytes=0
redirect_stderr=true

; ---------- RQ worker: long + default queues ----------
[program:frappe-worker-long]
command=/home/frappe/frappe-bench/env/bin/bench worker --queue long,default
directory=/home/frappe/frappe-bench
user=frappe
autostart=true
autorestart=true
stdout_logfile=/dev/fd/1
stdout_logfile_maxbytes=0
redirect_stderr=true

; ---------- Scheduler ----------
[program:frappe-schedule]
command=/home/frappe/frappe-bench/env/bin/bench schedule
directory=/home/frappe/frappe-bench
user=frappe
autostart=true
autorestart=true
stdout_logfile=/dev/fd/1
stdout_logfile_maxbytes=0
redirect_stderr=true

; ---------- Nginx (HTTP entrypoint) ----------
[program:nginx]
command=/usr/sbin/nginx -g 'daemon off;'
user=root
autostart=true
autorestart=true
stdout_logfile=/dev/fd/1
stdout_logfile_maxbytes=0
redirect_stderr=true
```

- [ ] **Step 2: Verify syntactic validity (no build yet — just shape check)**

The file is INI — we can't validate it fully without a container, but we can grep for obvious structural issues:

```bash
grep -c '^\[program:' deploy/railway/supervisord.conf
```

Expected: `6` (web, socketio, 2 workers, schedule, nginx).

- [ ] **Step 3: Commit**

```bash
git add deploy/railway/supervisord.conf
git commit -m "feat(railway): add supervisord config for 6 processes"
```

---

### Task 8: Write `nginx.conf.template`

**Files:**
- Create: `deploy/railway/nginx.conf.template`

- [ ] **Step 1: Write the template** (`$PORT` substituted at runtime by `envsubst`)

```nginx
# Rendered at container start by entrypoint.sh:
#   envsubst '$PORT' < nginx.conf.template > /etc/nginx/nginx.conf

worker_processes 1;
error_log /dev/stderr warn;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    sendfile on;
    keepalive_timeout 65;
    client_max_body_size 25M;
    access_log /dev/stdout;

    # Long timeouts — Frappe reports/exports can take minutes
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
    proxy_connect_timeout 10s;

    upstream frappe_web { server 127.0.0.1:8000 fail_timeout=0; }
    upstream frappe_socketio { server 127.0.0.1:9000 fail_timeout=0; }

    server {
        listen ${PORT} default_server;
        server_name _;

        # Static bench-built assets (JS/CSS bundles, Frappe desk assets)
        location /assets/ {
            alias /home/frappe/frappe-bench/sites/assets/;
            try_files $uri =404;
            expires 1h;
        }

        # User-uploaded files (served through Frappe so permissions apply)
        location /files/ {
            proxy_pass http://frappe_web;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Realtime websocket
        location /socket.io/ {
            proxy_pass http://frappe_socketio;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Everything else → gunicorn
        location / {
            proxy_pass http://frappe_web;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_redirect off;
        }
    }
}
```

- [ ] **Step 2: Validate structure**

```bash
grep -c 'location ' deploy/railway/nginx.conf.template
```

Expected: `4` (`/assets/`, `/files/`, `/socket.io/`, `/`).

- [ ] **Step 3: Commit**

```bash
git add deploy/railway/nginx.conf.template
git commit -m "feat(railway): add nginx config template with PORT substitution"
```

---

### Task 9: Write `entrypoint.sh`

**Files:**
- Create: `deploy/railway/entrypoint.sh`

- [ ] **Step 1: Write the entrypoint**

```bash
#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# Railway entrypoint for Frappe MRV stack.
# Runs as root (PID 1) because Supervisor needs to spawn nginx on $PORT.
# Delegates to the frappe user for all bench commands via gosu.
# ---------------------------------------------------------------------------

BENCH=/home/frappe/frappe-bench
SITES="$BENCH/sites"

# ---- Required env vars ----
: "${SITE_NAME:?SITE_NAME must be set (e.g. mrv-staging.up.railway.app)}"
: "${ADMIN_PASSWORD:?ADMIN_PASSWORD must be set}"
: "${DB_HOST:?DB_HOST must be set (e.g. Railway MariaDB private domain)}"
: "${DB_ROOT_PASSWORD:?DB_ROOT_PASSWORD must be set}"
: "${REDIS_CACHE_URL:?REDIS_CACHE_URL must be set}"
: "${REDIS_QUEUE_URL:?REDIS_QUEUE_URL must be set}"
: "${REDIS_SOCKETIO_URL:?REDIS_SOCKETIO_URL must be set}"
: "${PORT:?PORT must be set (Railway injects this)}"

DB_PORT="${DB_PORT:-3306}"

echo "[entrypoint] starting ($(date -u +%FT%TZ))"
echo "[entrypoint] SITE_NAME=$SITE_NAME DB_HOST=$DB_HOST PORT=$PORT"

# ---- 1. Fix volume ownership ----
# On first mount, the Railway volume is owned by root. bench runs as frappe.
chown -R frappe:frappe "$SITES"

# ---- 2. Render nginx config ----
# envsubst swaps $PORT from env; all other $vars in the template are nginx
# variables (prefixed $http_*, $proxy_*, $uri, etc.) — we whitelist only PORT.
envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
echo "[entrypoint] nginx config rendered for PORT=$PORT"

# ---- 3. Render common_site_config.json ----
# This tells Frappe where the DB and Redis live. Frappe reads these keys
# on every bench command. We write it with jq-shaped python to avoid
# needing jq in the image.
gosu frappe python3 - <<PY
import json, os
path = "$SITES/common_site_config.json"
existing = {}
if os.path.exists(path):
    with open(path) as f:
        existing = json.load(f)
existing.update({
    "db_host": "$DB_HOST",
    "db_port": int("$DB_PORT"),
    "redis_cache": "$REDIS_CACHE_URL",
    "redis_queue": "$REDIS_QUEUE_URL",
    "redis_socketio": "$REDIS_SOCKETIO_URL",
    "webserver_port": 8000,
    "socketio_port": 9000,
    "background_workers": 1,
    "file_watcher_port": 0,
    "serve_default_site": True,
    "auto_update": False,
    "restart_supervisor_on_update": False,
})
with open(path, "w") as f:
    json.dump(existing, f, indent=1, sort_keys=True)
print(f"[entrypoint] wrote {path}")
PY

# ---- 4. First-boot site creation OR routine migrate ----
SITE_DIR="$SITES/$SITE_NAME"
if [[ ! -f "$SITE_DIR/site_config.json" ]]; then
    echo "[entrypoint] first boot — creating site $SITE_NAME"
    gosu frappe bash -c "cd $BENCH && bench new-site \
        --mariadb-root-password '$DB_ROOT_PASSWORD' \
        --admin-password '$ADMIN_PASSWORD' \
        --no-mariadb-socket \
        --install-app mrvtools \
        --install-app frappe_side_menu \
        '$SITE_NAME'"
    echo "[entrypoint] site created and apps installed"
else
    echo "[entrypoint] existing site — running migrate"
    gosu frappe bash -c "cd $BENCH && bench --site '$SITE_NAME' migrate"
fi

# ---- 5. Set current site ----
echo "$SITE_NAME" > "$SITES/currentsite.txt"
chown frappe:frappe "$SITES/currentsite.txt"

# ---- 6. Hand off to supervisor ----
echo "[entrypoint] handing off to supervisord"
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
```

**Note on `bench new-site --install-app`:** Passing `--install-app` flags to `bench new-site` installs apps as part of site creation, which is simpler and more atomic than separate `install-app` calls. This also triggers `after_install` hooks in the correct order.

- [ ] **Step 2: Make executable + shellcheck (if available)**

```bash
chmod +x deploy/railway/entrypoint.sh
command -v shellcheck >/dev/null && shellcheck deploy/railway/entrypoint.sh || echo "shellcheck not installed — skipping"
```

Expected: no shellcheck errors. (If shellcheck reports warnings for the heredoc, they're acceptable — the heredoc is quoted with `<<PY` which disables shell expansion inside except for the `$VAR` substitutions we actually want.)

- [ ] **Step 3: Install `gettext-base` in the image** (provides `envsubst`)

In `Dockerfile`, locate the apt-get block added in Task 3 and add `gettext-base` to the package list. It should now read (showing only the changed block):

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      curl \
      gettext-base \
      git \
      gosu \
      libmariadb-dev \
      libssl-dev \
      mariadb-client \
      nginx \
      pkg-config \
      redis-tools \
      supervisor \
      wkhtmltopdf \
      xfonts-75dpi \
      xfonts-base \
   && rm -rf /var/lib/apt/lists/*
```

- [ ] **Step 4: Commit**

```bash
git add deploy/railway/entrypoint.sh Dockerfile
git commit -m "feat(railway): add entrypoint script with first-boot and migrate paths"
```

---

### Task 10: Finalize `Dockerfile` (COPY configs, ENTRYPOINT)

**Files:**
- Modify: `Dockerfile` (append)

- [ ] **Step 1: Append config copies + entrypoint**

```dockerfile

# ---------- Configs + entrypoint ----------
USER root

COPY deploy/railway/supervisord.conf /etc/supervisor/supervisord.conf
COPY deploy/railway/nginx.conf.template /etc/nginx/nginx.conf.template
COPY deploy/railway/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Pre-create log + run dirs for supervisor/nginx
RUN mkdir -p /var/log/supervisor /var/run \
 && rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf 2>/dev/null || true

# Railway injects $PORT. We expose a conventional value for documentation;
# actual listen port is set by envsubst at entrypoint time.
EXPOSE 8080

WORKDIR /home/frappe/frappe-bench

ENTRYPOINT ["/entrypoint.sh"]
```

- [ ] **Step 2: Full image build**

```bash
docker build -t mrv-railway:local .
```

Expected: completes without error. First build ~15–20 min; cached rebuilds ~1–2 min.

- [ ] **Step 3: Smoke-test that the image starts (without DB — expect it to fail at step 3 of entrypoint, which is fine; we just want to confirm the script runs past `[entrypoint] starting`)**

```bash
docker run --rm \
  -e SITE_NAME=test.local \
  -e ADMIN_PASSWORD=x \
  -e DB_HOST=nowhere \
  -e DB_ROOT_PASSWORD=x \
  -e REDIS_CACHE_URL=redis://nowhere:6379/0 \
  -e REDIS_QUEUE_URL=redis://nowhere:6379/1 \
  -e REDIS_SOCKETIO_URL=redis://nowhere:6379/2 \
  -e PORT=8080 \
  mrv-railway:local 2>&1 | head -20
```

Expected first lines:
```
[entrypoint] starting (2026-...)
[entrypoint] SITE_NAME=test.local DB_HOST=nowhere PORT=8080
[entrypoint] nginx config rendered for PORT=8080
[entrypoint] wrote /home/frappe/frappe-bench/sites/common_site_config.json
[entrypoint] first boot — creating site test.local
```

Then it will fail on `bench new-site` (can't reach MariaDB). That's the expected outcome for a no-DB smoke test.

- [ ] **Step 4: Commit**

```bash
git add Dockerfile
git commit -m "feat(railway): finalize Dockerfile with configs + ENTRYPOINT"
```

---

### Task 11: Write `railway.json`

**Files:**
- Create: `railway.json`

- [ ] **Step 1: Write the config**

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "healthcheckPath": "/api/method/ping",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

Notes:
- `startCommand` is omitted — the image's `ENTRYPOINT` handles start. Railway will not override ENTRYPOINT unless we specify `startCommand`.
- `healthcheckTimeout: 300` covers the first-boot `bench new-site` + `install-app` duration (~2–3 min).
- `/api/method/ping` is Frappe's built-in liveness endpoint that returns `{"message": "pong"}`.

- [ ] **Step 2: Validate JSON**

```bash
python3 -c "import json; json.load(open('railway.json'))" && echo OK
```

Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add railway.json
git commit -m "feat(railway): add railway.json with Dockerfile builder + healthcheck"
```

---

## Phase 2: Local integration verification

Before pushing to Railway, verify the image actually boots a working Frappe site against real MariaDB + Redis locally. This is a throwaway `docker-compose.local.yml` — Railway doesn't use it.

### Task 12: Write `docker-compose.local.yml` for local integration test

**Files:**
- Create: `deploy/railway/docker-compose.local.yml`

- [ ] **Step 1: Write compose file**

```yaml
# Local integration test only. Simulates the Railway service topology:
#   app  ←→  mariadb  ←→  redis
# Run:  docker compose -f deploy/railway/docker-compose.local.yml up --build
# Then: open http://localhost:8080
services:
  mariadb:
    image: mariadb:10.6
    environment:
      MYSQL_ROOT_PASSWORD: devrootpw
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
      - --skip-character-set-client-handshake
    volumes:
      - mariadb-data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "127.0.0.1", "-proot", "-pdevrootpw"]
      interval: 5s
      retries: 20

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 10

  app:
    build:
      context: ../..
      dockerfile: Dockerfile
    depends_on:
      mariadb:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      SITE_NAME: mrv.local
      ADMIN_PASSWORD: admin
      DB_HOST: mariadb
      DB_PORT: "3306"
      DB_ROOT_PASSWORD: devrootpw
      REDIS_CACHE_URL: redis://redis:6379/0
      REDIS_QUEUE_URL: redis://redis:6379/1
      REDIS_SOCKETIO_URL: redis://redis:6379/2
      PORT: "8080"
    ports:
      - "8080:8080"
    volumes:
      - app-sites:/home/frappe/frappe-bench/sites

volumes:
  mariadb-data:
  app-sites:
```

- [ ] **Step 2: Bring up the stack** (from repo root)

```bash
docker compose -f deploy/railway/docker-compose.local.yml up --build
```

Expected (in logs):
1. `mariadb` and `redis` report healthy
2. `app` logs show the entrypoint running through first-boot site creation
3. After ~2–3 min: `[entrypoint] site created and apps installed`
4. Supervisor starts all 6 processes; nginx listens on `:8080`
5. Periodic `frappe-web` gunicorn access logs

- [ ] **Step 3: Verify site responds**

From another terminal:
```bash
curl -s http://localhost:8080/api/method/ping
```

Expected: `{"message":"pong"}`.

- [ ] **Step 4: Verify SPA and desk routes**

```bash
curl -sI http://localhost:8080/frontend/home | head -1
curl -sI http://localhost:8080/app | head -1
curl -sI http://localhost:8080/login | head -1
```

Expected: each returns `HTTP/1.1 200 OK` or `HTTP/1.1 302 Found`.

- [ ] **Step 5: Verify seed data loaded**

```bash
curl -s -u "Administrator:admin" \
  "http://localhost:8080/api/method/frappe.client.get_count?doctype=Country"
```

Expected: JSON with a count > 0 (Frappe's standard Country doctype has seeded records).

- [ ] **Step 6: Verify mrvtools seeds**

```bash
curl -s -u "Administrator:admin" \
  "http://localhost:8080/api/method/frappe.client.get_list?doctype=DocType&filters=%5B%5B%22module%22%2C%22%3D%22%2C%22Mrvtools%22%5D%5D&limit_page_length=0"
```

Expected: JSON listing mrvtools doctypes (Project, Adaptation, etc.). If empty, `install-app mrvtools` didn't run.

- [ ] **Step 7: Verify redeploy path (site preservation)**

Bring stack down without removing volumes, then back up:
```bash
docker compose -f deploy/railway/docker-compose.local.yml down
docker compose -f deploy/railway/docker-compose.local.yml up
```

Expected (in app logs): `[entrypoint] existing site — running migrate` — NOT `first boot`. Site still responds at `/api/method/ping`.

- [ ] **Step 8: Tear down**

```bash
docker compose -f deploy/railway/docker-compose.local.yml down -v
```

- [ ] **Step 9: Commit**

```bash
git add deploy/railway/docker-compose.local.yml
git commit -m "test(railway): add docker-compose for local integration verification"
```

---

## Phase 3: Railway deploy

### Task 13: Write operator runbook `deploy/railway/README.md`

**Files:**
- Create: `deploy/railway/README.md`

- [ ] **Step 1: Write the runbook**

````markdown
# Railway Deployment Runbook

Staging/demo deployment of the full MRV stack to Railway. See the design spec at [docs/superpowers/specs/2026-04-19-railway-deployment-design.md](../../docs/superpowers/specs/2026-04-19-railway-deployment-design.md) for the architectural rationale.

## One-time Railway project setup

1. **Create a new Railway project.** Connect it to this GitHub repo. Railway auto-detects `railway.json` at the repo root and will build the `app` service from the Dockerfile.

2. **Add MariaDB as a second service:**
   - *New → Empty Service → Deploy from Docker Image*
   - Image: `mariadb:10.6`
   - Variables:
     - `MYSQL_ROOT_PASSWORD` = *(strong random string — save for the app service too)*
   - *Settings → Volumes → Add Volume* — mount path `/var/lib/mysql`, size 5 GB.
   - *Settings → Deploy → Start Command* — leave blank (image default is fine).
   - Deploy.

3. **Add Redis as a third service:**
   - *New → Database → Redis* (Railway's managed Redis plugin).
   - No configuration needed.

4. **Attach volume to the `app` service:**
   - Open the `app` service → Settings → Volumes → Add Volume.
   - Mount path: `/home/frappe/frappe-bench/sites`, size 5 GB.

5. **Set environment variables on the `app` service:**

   | Variable | Value |
   |---|---|
   | `SITE_NAME` | `${{RAILWAY_PUBLIC_DOMAIN}}` (Railway reference — expands to the generated `.up.railway.app` domain) |
   | `ADMIN_PASSWORD` | *(generate a strong random string — save it securely)* |
   | `DB_HOST` | `${{mariadb.RAILWAY_PRIVATE_DOMAIN}}` |
   | `DB_PORT` | `3306` |
   | `DB_ROOT_PASSWORD` | *same value as MariaDB's `MYSQL_ROOT_PASSWORD`* |
   | `REDIS_CACHE_URL` | `redis://${{redis.RAILWAY_PRIVATE_DOMAIN}}:6379/0` |
   | `REDIS_QUEUE_URL` | `redis://${{redis.RAILWAY_PRIVATE_DOMAIN}}:6379/1` |
   | `REDIS_SOCKETIO_URL` | `redis://${{redis.RAILWAY_PRIVATE_DOMAIN}}:6379/2` |

   `PORT` is auto-injected by Railway — do not set it manually.

6. **Trigger a deploy.** Push to the branch Railway tracks, or click Deploy in the UI.

## What to expect on first deploy

- **Build:** 15–20 minutes (bench init clones frappe, compiles Python deps, builds SPA).
- **First boot:** 2–3 minutes inside the container (bench new-site + install-app + seed data loaders).
- During first boot, healthchecks will fail — this is expected. `healthcheckTimeout` in `railway.json` is set to 300s to cover this.

## Verifying the deploy

Once the app service reports "Active":

```bash
# From your laptop
curl -s https://<your-app>.up.railway.app/api/method/ping
# → {"message":"pong"}
```

Browser:
- `https://<your-app>.up.railway.app/frontend/home` — public SPA
- `https://<your-app>.up.railway.app/login` — login page
- `https://<your-app>.up.railway.app/app` — Frappe desk (after login as `Administrator` / `$ADMIN_PASSWORD`)

## Subsequent deploys

Push to the tracked branch → Railway rebuilds → container restarts → entrypoint sees existing `site_config.json` → runs `bench --site $SITE_NAME migrate` → supervisor restarts processes.

Build time drops to 1–3 minutes (Docker layer cache). Boot time <30 s.

## Custom domain

1. Add domain in Railway UI (app service → Settings → Domains).
2. Update `SITE_NAME` env var to the custom domain.
3. `railway run --service app bench --site <new-name> set-config host_name https://<new-domain>`
4. Redeploy.

## Backups (manual — staging acceptance)

No automated backups. For an ad-hoc backup:

```bash
railway run --service mariadb mysqldump \
  -u root -p"$MYSQL_ROOT_PASSWORD" \
  --all-databases --single-transaction --quick \
  > backup-$(date +%F).sql
```

Store the resulting file somewhere durable.

## Troubleshooting

- **`app` service keeps restarting.** Railway dashboard → app → Deployments → latest → View Logs. Most common cause is missing env vars (entrypoint's `: "${VAR:?}"` checks will print exactly which one).
- **First boot takes >5 min.** Check MariaDB is healthy and reachable; check the container can resolve `${{mariadb.RAILWAY_PRIVATE_DOMAIN}}`.
- **SPA routes 404.** `bench build` didn't run or `mrvtools/www/frontend.html` isn't in the image. Check build logs for the `--from=frontend-build` COPY step.
- **`CSRFTokenError` on API calls from the SPA.** `ignore_csrf` should be `0` in prod. Only set to `1` for local Vite dev.
- **Want to shell into the app service.** `railway shell --service app` then `gosu frappe bash`.

## Cost guide (April 2026)

- App service (Docker): ~$5–10/mo depending on memory footprint
- MariaDB custom service: ~$5/mo
- Redis plugin: free tier available, ~$5/mo beyond
- Total typical staging: ~$10–20/mo
````

- [ ] **Step 2: Commit**

```bash
git add deploy/railway/README.md
git commit -m "docs(railway): add operator runbook for Railway deployment"
```

---

### Task 14: Manual Railway deploy + smoke test

**This task is manual — Railway project setup happens in the Railway UI, not from code.** The runbook in [deploy/railway/README.md](../../deploy/railway/README.md) is the authoritative step-by-step. This task box is to capture the outcome.

- [ ] **Step 1: Follow the runbook** (`deploy/railway/README.md` sections 1–6).

- [ ] **Step 2: Watch first deploy logs**

In Railway UI → `app` service → Deployments → active deploy → View Logs.

Expected log sequence:
1. Docker build completes
2. Container starts; `[entrypoint] starting ...`
3. `[entrypoint] first boot — creating site <domain>`
4. Frappe's own install output (creating database, running patches)
5. mrvtools install output (including `after_install` seed loading)
6. frappe_side_menu install output
7. `[entrypoint] site created and apps installed`
8. `[entrypoint] handing off to supervisord`
9. supervisor output: each program `entered RUNNING state`
10. nginx access logs begin

- [ ] **Step 3: Smoke test**

```bash
APP_URL=https://<your-generated>.up.railway.app

curl -sf "$APP_URL/api/method/ping" | grep pong
curl -sI "$APP_URL/frontend/home" | head -1
curl -sI "$APP_URL/login" | head -1
```

Expected: first prints `pong`; other two return 200 or 302.

- [ ] **Step 4: Log in and confirm persistence**

1. Browse to `$APP_URL/login`. Log in as `Administrator` / `$ADMIN_PASSWORD`.
2. Create a test doctype record (e.g. a new Project).
3. Trigger a redeploy from Railway UI (Deployments → Redeploy).
4. After redeploy completes, log in again and confirm the Project record is still there.

- [ ] **Step 5: Capture final URLs in project memory**

Note the Railway app URL in the team's shared doc. No commit needed — this is an operational record, not a code change.

---

## Self-review complete

**Spec coverage check:**
- Services (`app`, `mariadb`, `redis`) → Task 13 (runbook documents Railway UI setup)
- Volumes → Tasks 12, 13
- Dockerfile 2-stage build → Tasks 2, 3, 4, 5, 6, 10
- Entrypoint behavior (first-boot vs migrate) → Task 9
- Supervisor-managed processes → Task 7
- Nginx routing → Task 8
- Env vars → Tasks 9 (validation), 13 (Railway UI)
- `railway.json` → Task 11
- First-boot seed data → Tasks 9, 12 (verification)
- Redeploy path preserves data → Tasks 12 (local verify), 14 (Railway verify)
- Success criteria (SPA + desk + API + seed data + persistence) → Task 14 (steps 3-4)

All spec sections covered. No placeholders. Method names (`bench new-site`, `bench migrate`, `bench build`, `bench worker --queue ...`) consistent across tasks. File paths consistent.
