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

SITE_DIR="$SITES/$SITE_NAME"

# ---- 3a. Optional: one-shot DB user force-sync ----
# Recover from a DB-was-wiped-but-sites-volume-survived state: read
# db_name/db_password from sites/<site>/site_config.json (the values bench
# new-site generated on original first boot) and re-assert the MariaDB user
# + database + grants so the migrate step below can connect. Idempotent —
# set DB_USER_FORCE_SYNC=1 on Railway, redeploy, then unset. No-op on first
# boot (site_config.json doesn't exist yet). This fixes user/password drift,
# NOT a full DB wipe — if the site's tables are also gone you still need to
# wipe sites/<site>/ and let first-boot recreate (or pair with SAMPLE_DB_*).
if [[ "${DB_USER_FORCE_SYNC:-0}" == "1" && -f "$SITE_DIR/site_config.json" ]]; then
    echo "[entrypoint] DB_USER_FORCE_SYNC=1 — reconciling MariaDB user/db/grants with site_config.json"
    python3 - "$SITE_DIR/site_config.json" <<'PY'
import json, os, re, subprocess, sys
with open(sys.argv[1]) as f:
    cfg = json.load(f)
db_name = cfg.get("db_name")
db_pw = cfg.get("db_password")
if not db_name or not db_pw:
    sys.exit("site_config.json missing db_name or db_password — cannot sync")
if not re.fullmatch(r"_[A-Za-z0-9_]+", db_name):
    sys.exit(f"refusing to use unsafe db_name identifier: {db_name!r}")
def qstr(s):
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"
sql = "\n".join([
    f"CREATE USER IF NOT EXISTS {qstr(db_name)}@'%' IDENTIFIED BY {qstr(db_pw)};",
    f"ALTER USER {qstr(db_name)}@'%' IDENTIFIED BY {qstr(db_pw)};",
    f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
    f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO {qstr(db_name)}@'%';",
    "FLUSH PRIVILEGES;",
])
p = subprocess.run(
    ["mysql",
     f"-h{os.environ['DB_HOST']}",
     f"-P{os.environ['DB_PORT']}",
     "--protocol=TCP",
     "-uroot",
     f"-p{os.environ['DB_ROOT_PASSWORD']}"],
    input=sql, text=True, capture_output=True,
)
# Drop the "Using a password on the command line" warning; surface everything else.
leaks = [ln for ln in p.stderr.splitlines() if "Using a password on the command line" not in ln]
if leaks:
    sys.stderr.write("\n".join(leaks) + "\n")
if p.returncode != 0:
    sys.exit(p.returncode)
print(f"[entrypoint] synced user {db_name}@% and database {db_name}")
PY
    echo "[entrypoint] DB_USER_FORCE_SYNC complete (unset DB_USER_FORCE_SYNC for future boots)"
fi

# ---- 4. First-boot site creation OR routine migrate ----
# Pass secrets and site name via the child process's environment (gosu -E
# preserves them) so a single quote or other shell metacharacter in any value
# cannot break out of the bash -c string.
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

    # A sample DB can land with NULL values for singles the app seeds on
    # install (Side Menu Settings.application_logo is the common casualty —
    # it makes the sidebar flag 404). load_single_doc() re-upserts the four
    # seeded singles from master_data/*.json and is idempotent.
    echo "[entrypoint] re-seeding singles from master_data (post-restore)"
    gosu frappe env BENCH="$BENCH" SITE_NAME="$SITE_NAME" \
        bash -c 'cd "$BENCH" && bench --site "$SITE_NAME" execute mrvtools.mrvtools.after_install.load_single_doc'

    # Re-extract any seed files the singles above point at but whose physical
    # file is missing from the volume. A Railway volume remount can drop
    # sites/<site>/public/files/ while leaving File DB records intact; the
    # patched load_default_files() decouples the disk and DB checks so
    # missing files are always re-extracted from mrv_default_files.zip.
    echo "[entrypoint] re-extracting seed files from zip (post-restore)"
    gosu frappe env BENCH="$BENCH" SITE_NAME="$SITE_NAME" \
        bash -c 'cd "$BENCH" && bench --site "$SITE_NAME" execute mrvtools.mrvtools.after_install.load_default_files'

    # bench --force restore overwrites the Administrator password hash with
    # whatever was in the dump (typically a dev-laptop password). Re-apply the
    # env var so ADMIN_PASSWORD remains the source of truth and login works
    # with the same credential users already have.
    echo "[entrypoint] rotating Administrator password to \$ADMIN_PASSWORD"
    gosu frappe env BENCH="$BENCH" SITE_NAME="$SITE_NAME" ADMIN_PASSWORD="$ADMIN_PASSWORD" \
        bash -c 'cd "$BENCH" && bench --site "$SITE_NAME" set-admin-password "$ADMIN_PASSWORD"'

    rm -f "$dump"
    gosu frappe touch "$marker"
    echo "[entrypoint] sample DB restore complete"
}
maybe_restore_sample_db

# ---- 4c. Optional: force-sync Administrator password to $ADMIN_PASSWORD ----
# Use when a sample-DB restore left the site with a dev-laptop password and
# you don't want to re-run the full restore just to rotate credentials.
# Set ADMIN_PASSWORD_FORCE_SYNC=1 on Railway, redeploy, then unset and
# redeploy again so subsequent boots don't keep rewriting (set-admin-password
# invalidates existing sessions, so every boot with this on logs users out).
if [[ "${ADMIN_PASSWORD_FORCE_SYNC:-0}" == "1" ]]; then
    echo "[entrypoint] ADMIN_PASSWORD_FORCE_SYNC=1 — rotating Administrator password"
    gosu frappe env BENCH="$BENCH" SITE_NAME="$SITE_NAME" ADMIN_PASSWORD="$ADMIN_PASSWORD" \
        bash -c 'cd "$BENCH" && bench --site "$SITE_NAME" set-admin-password "$ADMIN_PASSWORD" && bench --site "$SITE_NAME" clear-cache'
    echo "[entrypoint] Administrator password rotated (unset ADMIN_PASSWORD_FORCE_SYNC for future boots)"
fi

# ---- 4d. Optional: force-reseed Frappe singles from master_data ----
# Re-asserts seeded values on the four singles MRV owns (MrvFrontend,
# Side Menu Settings, Website Settings, Navbar Settings) AND re-extracts any
# missing seed files from mrv_default_files.zip (the sidebar flag PNG, NDC
# PDFs, etc.) — a volume remount can drop sites/<site>/public/files/ while
# leaving File DB records intact, producing 404s that neither a restart nor a
# DB reseed alone will fix. Both underlying functions are idempotent.
# Set SINGLES_FORCE_SYNC=1 on Railway, redeploy, then unset and redeploy again.
if [[ "${SINGLES_FORCE_SYNC:-0}" == "1" ]]; then
    echo "[entrypoint] SINGLES_FORCE_SYNC=1 — re-seeding singles from master_data"
    gosu frappe env BENCH="$BENCH" SITE_NAME="$SITE_NAME" \
        bash -c 'cd "$BENCH" && bench --site "$SITE_NAME" execute mrvtools.mrvtools.after_install.load_single_doc'
    echo "[entrypoint] SINGLES_FORCE_SYNC=1 — re-extracting seed files from zip"
    gosu frappe env BENCH="$BENCH" SITE_NAME="$SITE_NAME" \
        bash -c 'cd "$BENCH" && bench --site "$SITE_NAME" execute mrvtools.mrvtools.after_install.load_default_files && bench --site "$SITE_NAME" clear-cache'
    echo "[entrypoint] singles + seed files reseeded (unset SINGLES_FORCE_SYNC for future boots)"
fi

# ---- 4e. Optional: one-shot email-domain rewrite ----
# Set EMAIL_DOMAIN_REWRITE="<old>:<new>" (e.g. "tridotstech.com:netzerolabs.io")
# on Railway and redeploy to rewrite every Contact / Contact Email / User
# whose email or login ID ends in @<old> to use @<new>. Uses frappe.rename_doc
# under the hood so foreign-key references stay consistent. Then DELETE the
# variable from Railway — leaving it set is harmless (idempotent: no-op once
# nothing matches) but spams the boot log.
if [[ -n "${EMAIL_DOMAIN_REWRITE:-}" ]]; then
    rewrite_old="${EMAIL_DOMAIN_REWRITE%%:*}"
    rewrite_new="${EMAIL_DOMAIN_REWRITE##*:}"
    if [[ -z "$rewrite_old" || -z "$rewrite_new" || "$rewrite_old" == "$EMAIL_DOMAIN_REWRITE" ]]; then
        echo "[entrypoint] EMAIL_DOMAIN_REWRITE malformed — expected '<old>:<new>', got '$EMAIL_DOMAIN_REWRITE' (skipping)"
    else
        echo "[entrypoint] EMAIL_DOMAIN_REWRITE — rewriting @$rewrite_old to @$rewrite_new"
        gosu frappe env BENCH="$BENCH" SITE_NAME="$SITE_NAME" \
            REWRITE_OLD="$rewrite_old" REWRITE_NEW="$rewrite_new" \
            bash -c 'cd "$BENCH" && bench --site "$SITE_NAME" execute mrvtools.api.replace_email_domain --kwargs "{\"old_domain\":\"$REWRITE_OLD\",\"new_domain\":\"$REWRITE_NEW\",\"dry_run\":0}" && bench --site "$SITE_NAME" clear-cache'
        echo "[entrypoint] email-domain rewrite complete (delete EMAIL_DOMAIN_REWRITE for future boots)"
    fi
fi

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
