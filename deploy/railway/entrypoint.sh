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
envsubst '${PORT} ${SITE_NAME}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
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
# Pass secrets and site name via the child process's environment (gosu -E
# preserves them) so a single quote or other shell metacharacter in any value
# cannot break out of the bash -c string.
SITE_DIR="$SITES/$SITE_NAME"
if [[ ! -f "$SITE_DIR/site_config.json" ]]; then
    echo "[entrypoint] first boot — creating site $SITE_NAME"
    gosu frappe env \
        BENCH="$BENCH" \
        SITE_NAME="$SITE_NAME" \
        ADMIN_PASSWORD="$ADMIN_PASSWORD" \
        DB_ROOT_PASSWORD="$DB_ROOT_PASSWORD" \
        bash -c 'cd "$BENCH" && bench new-site \
            --mariadb-root-password "$DB_ROOT_PASSWORD" \
            --admin-password "$ADMIN_PASSWORD" \
            --no-mariadb-socket \
            --install-app mrvtools \
            --install-app frappe_side_menu \
            "$SITE_NAME"'
    echo "[entrypoint] site created and apps installed"
else
    echo "[entrypoint] existing site — running migrate"
    gosu frappe env \
        BENCH="$BENCH" \
        SITE_NAME="$SITE_NAME" \
        bash -c 'cd "$BENCH" && bench --site "$SITE_NAME" migrate'
fi

# ---- 5. Set current site ----
echo "$SITE_NAME" > "$SITES/currentsite.txt"
chown frappe:frappe "$SITES/currentsite.txt"

# ---- 6. Hand off to supervisor ----
echo "[entrypoint] handing off to supervisord"
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
