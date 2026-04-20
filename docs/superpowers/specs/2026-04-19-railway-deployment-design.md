# Railway Deployment Design (Staging)

**Status:** Draft — awaiting user review
**Date:** 2026-04-19
**Scope:** Deploy the full MRV tool (Frappe desk + SPA + login + persistent data) to Railway as a staging/demo target.

## Goal

Produce a Railway configuration that deploys this repository — two Frappe apps (`mrvtools`, `frappe_side_menu`) plus the Vue 3 SPA — as a working Frappe site accessible over the public internet, suitable for stakeholder demos and internal review.

Explicit non-goals: production-grade reliability, automated offsite backups, horizontal scaling, custom domain + TLS on day one.

## Background

Frappe is not a standard `pip install && run` Python app. It requires:

- **MariaDB 10.6+** (Postgres support is experimental; Frappe v15 expects MariaDB).
- **Redis**, conventionally three logical instances (cache, queue, socketio).
- **Multiple long-running processes** — gunicorn web, Node socketio, RQ workers, scheduler — normally managed by Supervisor.
- **Persistent storage** for `sites/<site>/public/files` and `private/files`.
- **A one-time site-creation step** (`bench new-site` + `install-app`) distinct from routine deploys (`bench migrate`).

Railway's model is one process per service, managed Postgres / MySQL / Redis plugins (no managed MariaDB), Docker- or Nixpacks-based builds, and named volumes. This spec reconciles the two.

## Architecture

### Railway services

| Service | Source | Purpose |
|---------|--------|---------|
| `app` | Built from this repo via `Dockerfile` at repo root | Runs Frappe web + socketio + 2 workers + scheduler under Supervisor, with Nginx terminating `$PORT`. |
| `mariadb` | Public image `mariadb:10.6` (Railway "deploy from Docker image") | Primary database. |
| `redis` | Railway managed Redis plugin | Shared between Frappe's three logical uses via separate DB numbers (0/1/2). |

Three services total. Adding MariaDB and Redis is a manual step in the Railway UI — they cannot be declared from this repo's `railway.json` (that file only describes the service being deployed from this repo, i.e. `app`).

### Volumes

| Volume | Service | Mount point | Reason |
|--------|---------|-------------|--------|
| `app-sites-data` | `app` | `/home/frappe/frappe-bench/sites` | Preserves `site_config.json`, uploaded files (`public/files/`, `private/files/`), and site metadata across redeploys. |
| `mariadb-data` | `mariadb` | `/var/lib/mysql` | Database persistence. |

Redis has no volume — staging cache/queue loss on restart is acceptable.

### Container image

A single `Dockerfile` at the repo root, two build stages:

**Stage 1: `frontend-build`**
- Base: `node:20-alpine`
- Copy `frontend/` and `mrvtools/public/` into stage
- `yarn install --frozen-lockfile && yarn build`
- Output artifacts to stage filesystem: `mrvtools/public/frontend/*` and `mrvtools/www/frontend.html`

**Stage 2: `runtime`**
- Base: `python:3.11-slim-bookworm`
- Install system deps: `wkhtmltopdf`, `libmariadb-dev`, `mariadb-client`, `redis-tools`, `nginx`, `supervisor`, `git`, `curl`, Node 20.x (for socketio), Yarn, build-essential
- Create `frappe` user, set home to `/home/frappe`
- As `frappe`: `pip install frappe-bench`, then `bench init --frappe-branch version-15 frappe-bench --skip-assets --skip-redis-config-generation`
- Copy this repo into `/home/frappe/frappe-bench/apps/mrvtools`, pip-install it (`pip install -e apps/mrvtools`)
- Copy this repo's `frappe_side_menu/` subset into `/home/frappe/frappe-bench/apps/frappe_side_menu`, pip-install via `setup_sidebarmenu.py`
- Copy built SPA artifacts from stage 1 into `apps/mrvtools/mrvtools/public/frontend/` and `apps/mrvtools/mrvtools/www/frontend.html`
- `bench build --apps mrvtools,frappe_side_menu`
- Copy `deploy/railway/supervisord.conf` → `/etc/supervisor/supervisord.conf`
- Copy `deploy/railway/nginx.conf.template` → `/etc/nginx/nginx.conf.template` (rendered at entrypoint time with `envsubst` to substitute `$PORT`)
- Copy `deploy/railway/entrypoint.sh` → `/entrypoint.sh`, chmod +x
- `EXPOSE 8080`
- `ENTRYPOINT ["/entrypoint.sh"]`

### Entrypoint script (`deploy/railway/entrypoint.sh`)

Runs as PID 1 when the container starts. Flow:

1. `chown -R frappe:frappe /home/frappe/frappe-bench/sites` — idempotent, handles first-mount ownership of the Railway volume.
2. Render `/home/frappe/frappe-bench/sites/common_site_config.json` from env vars using `bench set-common-config` (or `jq`/heredoc):
   - `db_host`, `db_port`
   - `redis_cache`, `redis_queue`, `redis_socketio` (read from `REDIS_CACHE_URL`, etc.)
3. If `/home/frappe/frappe-bench/sites/$SITE_NAME/site_config.json` does **not** exist (first boot):
   - `bench new-site "$SITE_NAME" --admin-password "$ADMIN_PASSWORD" --mariadb-root-password "$DB_ROOT_PASSWORD" --no-mariadb-socket --mariadb-user-host-login-scope="%"`
   - `bench --site "$SITE_NAME" install-app mrvtools` (triggers `after_install` seed loaders: master data, default files, single docs — see `mrvtools/mrvtools/after_install.py`)
   - `bench --site "$SITE_NAME" install-app frappe_side_menu`
   - `bench --site "$SITE_NAME" set-config ignore_csrf 0` (defensive; should already be 0 in prod)
4. Else (subsequent boots): `bench --site "$SITE_NAME" migrate`
5. Write `$SITE_NAME` to `sites/currentsite.txt`
6. `exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf`

All `bench` commands run as the `frappe` user via `gosu` or `su-exec`.

### Supervisor-managed processes (`deploy/railway/supervisord.conf`)

| Program | Command | Purpose |
|---------|---------|---------|
| `frappe-web` | `gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 frappe.app:application` | HTTP backend |
| `frappe-socketio` | `node apps/frappe/socketio.js` (listens on `:9000`) | Realtime |
| `frappe-worker-short` | `bench worker --queue short` | Short RQ jobs |
| `frappe-worker-long` | `bench worker --queue long,default` | Long RQ jobs + default queue |
| `frappe-schedule` | `bench schedule` | Cron events |
| `nginx` | `nginx -g 'daemon off;'` | Terminates `$PORT`, proxies |

Supervisor runs as root (needed for nginx to bind `$PORT`); `frappe-*` programs drop to the `frappe` user via `user=frappe` directive.

### Nginx config (`deploy/railway/nginx.conf`)

Listens on `$PORT` (injected via `envsubst` at entrypoint time into a template). Routes:

- `/socket.io/` → `http://127.0.0.1:9000` (WebSocket upgrade headers)
- `/assets/` → serves from `/home/frappe/frappe-bench/sites/assets/` as static
- `/files/` → serves from `/home/frappe/frappe-bench/sites/$SITE_NAME/public/files/` as static
- everything else → `http://127.0.0.1:8000` (gunicorn)

### Environment variables

| Var | Set on | Value | Notes |
|-----|--------|-------|-------|
| `SITE_NAME` | `app` | e.g. `mrv-staging.up.railway.app` | Must match the Railway-generated domain, or a custom domain once configured. |
| `ADMIN_PASSWORD` | `app` | Railway-generated secret | Used only on first boot. |
| `DB_HOST` | `app` | `${{mariadb.RAILWAY_PRIVATE_DOMAIN}}` | Railway's private networking. |
| `DB_PORT` | `app` | `3306` | |
| `DB_ROOT_PASSWORD` | `app` + `mariadb` (as `MYSQL_ROOT_PASSWORD`) | shared secret | Same value in both places. |
| `REDIS_CACHE_URL` | `app` | `redis://${{redis.RAILWAY_PRIVATE_DOMAIN}}:6379/0` | |
| `REDIS_QUEUE_URL` | `app` | `redis://${{redis.RAILWAY_PRIVATE_DOMAIN}}:6379/1` | |
| `REDIS_SOCKETIO_URL` | `app` | `redis://${{redis.RAILWAY_PRIVATE_DOMAIN}}:6379/2` | |
| `PORT` | `app` | auto-injected by Railway | Consumed by nginx template. |

### `railway.json` at repo root

Minimal — declares only the `app` service, since MariaDB and Redis are added via Railway UI.

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "/entrypoint.sh",
    "healthcheckPath": "/api/method/ping",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

`healthcheckTimeout: 300` accommodates the first-boot `bench new-site` + `install-app` delay (~2–3 min). Steady-state health checks return in <1s.

## Files to add

```
/Dockerfile
/railway.json
/.dockerignore
/deploy/railway/supervisord.conf
/deploy/railway/nginx.conf.template
/deploy/railway/entrypoint.sh
/deploy/railway/README.md           # operator runbook (how to set up services in Railway UI)
```

`.dockerignore` should exclude `frontend/node_modules`, `.git`, `docs/`, `*.md` except `README.md`, `frappe-bench/` (if locally present), to keep build context small.

## Files to modify

None. The existing repo layout (`mrvtools/`, `frappe_side_menu/`, `frontend/`) is already compatible. The Docker build copies in what it needs.

## Operator runbook (documented in `deploy/railway/README.md`)

1. Create a new Railway project.
2. Add three services:
   - **From this repo** (the `app` service) — Railway auto-detects `railway.json` and builds the Dockerfile.
   - **From Docker image** `mariadb:10.6` — attach volume at `/var/lib/mysql`, set `MYSQL_ROOT_PASSWORD`.
   - **Redis plugin** from Railway marketplace.
3. On the `app` service, attach a volume at `/home/frappe/frappe-bench/sites`.
4. Set environment variables per the table above.
5. Trigger a deploy. First build: ~8–10 min. First boot: ~3 min (site creation + seed). Subsequent deploys: ~2 min build, <30s boot.
6. Visit the Railway-generated domain. Log in with `Administrator` / `$ADMIN_PASSWORD`.

## Non-goals and accepted risks

- **No automated backups.** `mysqldump` can be run manually via `railway run` or an ad-hoc cron. Staging scope accepts data loss on catastrophic DB volume failure.
- **No custom domain in v1.** Use `*.up.railway.app`. Adding a custom domain later requires: set Railway domain, update `SITE_NAME` env var, run `bench set-config host_name https://<domain>`, redeploy.
- **No horizontal scaling.** Single `app` container holds all processes. For higher load, future work is to split web/socketio/workers into separate Railway services.
- **`bench init` runs at image build time** (not at deploy time) — slow first build, but reproducible and cache-friendly.
- **Single Redis** — three DB numbers share one instance. Cache churn could theoretically evict queue state if memory-pressured. Staging-acceptable.
- **MariaDB as a Railway custom service** — no managed backup tooling, no failover. User accepts this per the brainstorming decision (option B: staging/demo).

## Open questions

None. All branching decisions were resolved during brainstorming:

- Scope: full Frappe stack (not SPA-only) — **confirmed**.
- Reliability tier: staging/demo (not production) — **confirmed**.
- Architecture: single-container monolith (not multi-service, not install.sh-in-container) — **confirmed**.

## Success criteria

1. `railway up` (or a push to the connected branch) produces a running `app` service.
2. The Railway-generated domain returns the SPA at `/frontend/home` and the Frappe desk at `/app`.
3. Administrator can log in, create a Project (or other mrvtools doctype), log out, redeploy, and the Project still exists.
4. Seed data from `after_install.py` is present after first deploy (master data lookups, default files, single docs).
5. The frontend SPA can call Frappe API endpoints (e.g. `/api/method/mrvtools.api.get_approvers`) and receive JSON without CSRF errors.
