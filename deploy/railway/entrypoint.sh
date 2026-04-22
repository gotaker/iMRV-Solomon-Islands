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

# ---- 1a. Seed sites/ skeleton on first mount ----
# A fresh Railway volume mount shadows the sites/ directory baked into the
# image (apps.txt, assets/, etc.), so bench can't find its app list. Copy the
# template in if the volume is empty.
if [[ ! -f "$SITES/apps.txt" ]]; then
    echo "[entrypoint] seeding empty sites volume from /home/frappe/sites-template"
    gosu frappe cp -an /home/frappe/sites-template/. "$SITES/"
fi

# ---- 1b. Refresh sites/assets/ from image template on every boot ----
# sites/assets/ is build output (produced by `bench build` in the image),
# not user data. Leaving the first-boot copy on the persistent volume causes
# the asset manifest (assets.json) to drift out of sync with the bench code
# baked into each new image, producing 404s on CSS/JS bundles.
if [[ -d /home/frappe/sites-template/assets ]]; then
    echo "[entrypoint] refreshing sites/assets/ from image template"
    rm -rf "$SITES/assets"
    gosu frappe cp -a /home/frappe/sites-template/assets "$SITES/assets"
fi

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

# ---- 4b. Optional: restore a sample DB ----
# Runs iff SAMPLE_DB_URL or SAMPLE_DB_PATH is set. A marker file in the site
# dir (.sample_db_restored) keeps this to once-per-site-lifetime unless
# SAMPLE_DB_FORCE_RESTORE=1 is explicitly set — otherwise every redeploy
# would wipe demo state. Mirrors install.sh :: load_sample_data() semantics.
maybe_restore_sample_db() {
    local src_url="${SAMPLE_DB_URL:-}"
    local src_path="${SAMPLE_DB_PATH:-}"

    # Fall back to a dump baked into the image at /home/frappe/sample-db/.
    # Only used when neither env var is set. See Dockerfile "bake in a sample
    # DB dump" step for how to include one.
    if [[ -z "$src_url" && -z "$src_path" ]]; then
        shopt -s nullglob
        local baked=(/home/frappe/sample-db/*.sql.gz)
        shopt -u nullglob
        if [[ ${#baked[@]} -gt 0 ]]; then
            src_path="${baked[0]}"
            echo "[entrypoint] auto-using baked-in sample DB: $src_path"
        fi
    fi

    if [[ -z "$src_url" && -z "$src_path" ]]; then
        return 0
    fi

    local marker="$SITE_DIR/.sample_db_restored"
    local force="${SAMPLE_DB_FORCE_RESTORE:-0}"
    if [[ -f "$marker" && "$force" != "1" ]]; then
        echo "[entrypoint] sample DB already restored (marker: $marker) — skipping"
        echo "[entrypoint]   set SAMPLE_DB_FORCE_RESTORE=1 to re-run on next boot"
        return 0
    fi

    local dump=/tmp/sample-db.sql.gz
    if [[ -n "$src_url" ]]; then
        echo "[entrypoint] fetching sample DB from \$SAMPLE_DB_URL"
        # Private-repo GitHub Release assets need a PAT; any other bespoke
        # auth scheme can also be threaded through via SAMPLE_DB_AUTH_HEADER
        # (full header line, e.g. "Authorization: Bearer ghp_xxx"). For
        # GitHub Releases specifically, the asset returns octet-stream only
        # when Accept is set — otherwise you get an HTML redirect that
        # bench restore can't read.
        local curl_args=(-fsSL --output "$dump")
        if [[ -n "${SAMPLE_DB_AUTH_HEADER:-}" ]]; then
            curl_args+=(-H "$SAMPLE_DB_AUTH_HEADER")
        fi
        if [[ "$src_url" == *"api.github.com"* ]]; then
            curl_args+=(-H "Accept: application/octet-stream")
        fi
        curl "${curl_args[@]}" "$src_url"
    else
        echo "[entrypoint] copying sample DB from \$SAMPLE_DB_PATH=$src_path"
        if [[ ! -f "$src_path" ]]; then
            echo "[entrypoint] FATAL: SAMPLE_DB_PATH file does not exist" >&2
            exit 1
        fi
        cp "$src_path" "$dump"
    fi
    chown frappe:frappe "$dump"

    echo "[entrypoint] restoring sample DB into $SITE_NAME (drops current DB)"
    gosu frappe env BENCH="$BENCH" SITE_NAME="$SITE_NAME" \
        DB_ROOT_PASSWORD="$DB_ROOT_PASSWORD" DUMP="$dump" \
        bash -c 'cd "$BENCH" && bench --site "$SITE_NAME" --force restore "$DUMP" \
            --mariadb-root-password "$DB_ROOT_PASSWORD"'
    gosu frappe env BENCH="$BENCH" SITE_NAME="$SITE_NAME" \
        bash -c 'cd "$BENCH" && bench --site "$SITE_NAME" migrate && bench --site "$SITE_NAME" clear-cache'

    rm -f "$dump"
    gosu frappe touch "$marker"
    echo "[entrypoint] sample DB restore complete"
}
maybe_restore_sample_db

# ---- 4a. Set host_name so Frappe's realtime server accepts the public URL ----
# Without this, socket.io rejects websocket connections from any domain other
# than the bare SITE_NAME with "Invalid origin". Safe to run every boot — it
# re-writes site_config.json idempotently. Protocol defaults to https (Railway
# always serves TLS); override SITE_PROTOCOL=http for local/non-TLS setups.
SITE_PROTOCOL="${SITE_PROTOCOL:-https}"
HOST_NAME_URL="${SITE_PROTOCOL}://${SITE_NAME}"
gosu frappe env BENCH="$BENCH" SITE_NAME="$SITE_NAME" HOST_NAME_URL="$HOST_NAME_URL" \
    bash -c 'cd "$BENCH" && bench --site "$SITE_NAME" set-config host_name "$HOST_NAME_URL"'
echo "[entrypoint] host_name set to $HOST_NAME_URL"

# ---- 5. Set current site ----
echo "$SITE_NAME" > "$SITES/currentsite.txt"
chown frappe:frappe "$SITES/currentsite.txt"

# ---- 6. Hand off to supervisor ----
echo "[entrypoint] handing off to supervisord"
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
