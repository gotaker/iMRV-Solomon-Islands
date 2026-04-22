# Railway Deployment Runbook

Staging/demo deployment of the full MRV stack (Frappe + SPA + MariaDB + Redis) to Railway. Design spec: [docs/superpowers/specs/2026-04-19-railway-deployment-design.md](../../docs/superpowers/specs/2026-04-19-railway-deployment-design.md).

## Contents

- [One-time Railway project setup](#one-time-railway-project-setup)
- [Environment variables](#environment-variables)
- [What to expect on first deploy](#what-to-expect-on-first-deploy)
- [Post-deploy verification checklist](#post-deploy-verification-checklist)
- [Accessing the container shell](#accessing-the-container-shell)
- [Troubleshooting](#troubleshooting)
- [Operations](#operations)
- [Local integration test](#local-integration-test)

## One-time Railway project setup

1. **Create a new Railway project.** Connect it to this GitHub repo. Railway auto-detects [railway.json](../../railway.json) at the repo root and builds the app service from the Dockerfile.

2. **Add MariaDB as a second service:**
   - *New → Empty Service → Deploy from Docker Image*
   - Image: **`mariadb:10.6`** — pin this exactly. `mariadb:latest` now resolves to 12.x, which breaks Frappe's `install_app` with subtle SQL/caching failures. Frappe is tested against 10.6.
   - *Settings → Service Name* → rename to lowercase **`mariadb`** so `${{mariadb.RAILWAY_PRIVATE_DOMAIN}}` resolves from the app service.
   - Variables: `MYSQL_ROOT_PASSWORD` = *(strong random — save it; the app's `DB_ROOT_PASSWORD` must match)*
   - *Settings → Volumes* — mount `/var/lib/mysql`, size 5 GB.
   - Deploy.

3. **Add Redis as a third service:**
   - *New → Database → Redis* (Railway's managed plugin).
   - *Settings → Service Name* → rename to lowercase **`redis`** if Railway gave it a different default.
   - No variables to set — Railway provisions `REDIS_URL` / `REDIS_PASSWORD` automatically. You'll read those from the app side.

4. **Attach a volume to the app service:**
   - App service → Settings → Volumes → Add Volume.
   - Mount path: `/home/frappe/frappe-bench/sites`, size 5 GB.
   - **Required, not optional.** Without it, `sites/` is ephemeral — the site gets recreated from scratch on every redeploy and every user edit is lost.
   - The image bakes a seed template at `/home/frappe/sites-template/`. [entrypoint.sh:33-40](entrypoint.sh#L33-L40) copies it into the volume on first mount so `apps.txt` / `assets/` / etc. aren't shadowed by the empty mount.

5. **Set environment variables on the app service** (see [Environment variables](#environment-variables) below). Read the formatting notes — several non-obvious gotchas.

6. **Set the custom-domain target port to 8080** if you add one. App service → Settings → Networking → ✏️ on the domain row → **Target Port: 8080** (matches `$PORT` injected by Railway, which nginx binds to in [nginx.conf.template](nginx.conf.template)). The default often comes up as 8000 and has to be changed by hand.

7. **Trigger a deploy.** Push to the tracked branch or click Deploy.

## Environment variables

Set these on the **app** service. `PORT` is auto-injected by Railway — do not set it manually.

| Variable | Value | Notes |
| --- | --- | --- |
| `SITE_NAME` | `${{RAILWAY_PUBLIC_DOMAIN}}` | Railway reference. Expands to the auto-generated `.up.railway.app` domain. If you add a custom domain later, see [Custom domain](#custom-domain). |
| `ADMIN_PASSWORD` | *strong random string* | **Save this immediately.** Used only on first boot to create the `Administrator` account. Changing it in Railway after first boot does **not** rotate the DB password — use `bench … set-admin-password` (see [Troubleshooting](#cant-log-in-as-administrator)). |
| `DB_HOST` | `${{mariadb.RAILWAY_PRIVATE_DOMAIN}}` | Railway reference to the MariaDB service's private hostname. Requires the MariaDB service to be named exactly `mariadb`. |
| `DB_PORT` | `3306` | |
| `DB_ROOT_PASSWORD` | *same value as MariaDB's `MYSQL_ROOT_PASSWORD`* | |
| `REDIS_CACHE_URL` | `redis://default:<REDIS_PASSWORD>@${{redis.RAILWAY_PRIVATE_DOMAIN}}:6379/0` | **Must include the password** — Railway's managed Redis requires AUTH. Grab `REDIS_PASSWORD` from the redis service's Variables tab. Unauthenticated connects fail with `redis.exceptions.ResponseError: Protocol error: unauthenticated bulk length`. |
| `REDIS_QUEUE_URL` | `redis://default:<REDIS_PASSWORD>@${{redis.RAILWAY_PRIVATE_DOMAIN}}:6379/1` | Same password as above. |
| `REDIS_SOCKETIO_URL` | `redis://default:<REDIS_PASSWORD>@${{redis.RAILWAY_PRIVATE_DOMAIN}}:6379/2` | Same password as above. |

The [entrypoint.sh](entrypoint.sh) aborts immediately with a clear error if any of these are missing (`: "${VAR:?…}"` checks).

### Optional: seed the site with a sample DB

If you want the Railway deploy to come up pre-populated (instead of the empty default from `bench new-site` + `after_install`), set one of these on the app service:

| Variable | Value | Notes |
| --- | --- | --- |
| `SAMPLE_DB_URL` | `https://…/dump.sql.gz` | URL the container fetches with `curl -fsSL` on first boot. Must be reachable from Railway. Use a GitHub Release artifact, S3 signed URL, Railway volume URL, etc. **Private GitHub repos:** the standard `/releases/download/…` URL returns 404 without auth — either use `SAMPLE_DB_AUTH_HEADER` below (combined with a token-prefixed URL) or a different host. |
| `SAMPLE_DB_AUTH_HEADER` | `Authorization: Bearer ghp_…` | Optional raw header appended to the `curl` call. For a private GitHub repo, generate a fine-scoped PAT with `contents:read` on the repo and point `SAMPLE_DB_URL` at `https://api.github.com/repos/<owner>/<repo>/releases/assets/<asset_id>` (the entrypoint auto-adds `Accept: application/octet-stream` when it sees `api.github.com`). Find the asset id with `gh api repos/<owner>/<repo>/releases -q '.[].assets[] \| {id,name}'`. |
| `SAMPLE_DB_PATH` | `/path/in/container.sql.gz` | Alternative to URL — path inside the container. Useful if you pre-upload via `railway ssh` (`cat dump.sql.gz \| railway ssh … "cat > /tmp/dump.sql.gz"`). |
| `SAMPLE_DB_FORCE_RESTORE` | `1` (default `0`) | Re-run the restore on the next boot even if a previous boot already did it. Leave unset in normal operation; set only to deliberately re-seed, then unset and redeploy. |
| `ADMIN_PASSWORD_FORCE_SYNC` | `1` (default `0`) | Rotate the Administrator password to `$ADMIN_PASSWORD` on boot, independent of the restore pipeline. Use this when a previous restore left the wrong password and you don't want to re-run the full restore. Toggle-off after the next successful boot — every boot with this on logs users out (set-admin-password invalidates sessions). |

**Third option — bake the dump into the image** (no env var needed): commit a `*.sql.gz` into [.Sample DB/](../../.Sample%20DB/) (temporarily un-ignore it by adding `!.Sample DB/your-file.sql.gz` to [.gitignore](../../.gitignore)), and the Dockerfile `COPY` step at [Dockerfile:179-182](../../Dockerfile#L179-L182) will bundle it at `/home/frappe/sample-db/`. The entrypoint's auto-detect picks the first `*.sql.gz` there when neither env var is set. Pros: zero external hosting, self-contained image. Cons: adds dump size (~3 MB per file) to every image layer + git history.

Restore flow ([entrypoint.sh:117-165](entrypoint.sh#L117-L165)):

1. On each boot, after the first-boot `bench new-site` or routine `bench migrate` step, the entrypoint checks for `SAMPLE_DB_URL` / `SAMPLE_DB_PATH`.
2. If set AND a marker file at `sites/<site>/.sample_db_restored` is absent (or `SAMPLE_DB_FORCE_RESTORE=1`), it fetches/copies the dump to `/tmp/sample-db.sql.gz`, runs `bench --force restore` + `bench migrate` + `bench clear-cache`, then writes the marker.
3. On subsequent boots the marker short-circuits the restore (so normal redeploys don't wipe accumulated changes).

**This is destructive** — `bench --force restore` drops the current site DB and recreates it from the dump. The entrypoint auto-rotates the Administrator password back to `$ADMIN_PASSWORD` immediately after restore, so existing login credentials keep working. If you bypass the entrypoint (e.g. manual `bench restore` inside the container), you must also run `bench --site $SITE_NAME set-admin-password "$ADMIN_PASSWORD"` yourself.

### Raw Editor gotchas

The Variables tab's Raw Editor is fussier than it looks. Every one of these has silently broken a deploy for us:

- **No whitespace between the key and `=`.** `ADMIN_PASSWORD ="catch22"` (with a stray tab before `=`) stores the variable under key `ADMIN_PASSWORD\t` and the container sees it as unset. Type the line by hand if you pasted from elsewhere.
- **Avoid wrapping references in quotes.** `DB_HOST="${{mariadb.RAILWAY_PRIVATE_DOMAIN}}"` sometimes stores the literal string and breaks expansion. Prefer unquoted: `DB_HOST=${{mariadb.RAILWAY_PRIVATE_DOMAIN}}`.
- **References fail silently.** If the referenced service doesn't exist with that exact (case-sensitive) name, the reference expands to empty — and the entrypoint's `:?` check reports the var as "must be set" even though Railway's UI shows a value. Double-check the service name on the project canvas.
- **Hardcoded alternative:** Railway's private DNS is always `<service-name>.railway.internal`. If a reference won't resolve, substitute the literal string — e.g. `DB_HOST=mariadb.railway.internal`. Bypasses reference-resolution bugs entirely.
- **Stale deploys:** changing a variable doesn't always trigger a redeploy. If you just added/fixed a variable and logs still show the old value, manually click Deployments → ⋮ → Redeploy.

## What to expect on first deploy

- **Build:** 15–20 minutes. `bench init` clones Frappe, compiles Python deps, `yarn build` produces the SPA bundle.
- **First boot:** 2–3 minutes inside the container. The entrypoint runs `bench new-site`, installs `mrvtools` + `frappe_side_menu`, and `after_install` unzips [mrv_default_files.zip](../../mrvtools/public/mrv_default_files.zip) into `sites/<site>/public/files/` and populates seed doctypes.
- During first boot, Railway healthchecks **will fail** — expected. `healthcheckTimeout` in [railway.json](../../railway.json) is set to 300 s to cover this.
- Subsequent deploys: build 1–3 min (Docker cache), boot <30 s (entrypoint sees existing `site_config.json` → runs `bench migrate` instead of `new-site`).

## Post-deploy verification checklist

Run through this after every first-deploy. Each of these has bitten us at least once.

```bash
# 1. App is up
curl -s https://<your-app>.up.railway.app/api/method/ping
# → {"message":"pong"}

# 2. SPA data API returns content (not an HTML error page)
curl -s https://<your-app>.up.railway.app/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all \
  | head -c 500
# → JSON with "parent_data", "child_table_data", "CCDImages" keys

# 3. Public files serve with 200 (NOT 404)
curl -sI https://<your-app>.up.railway.app/files/iMRV2.jpg | head -2
# → HTTP/1.1 200 OK
# → Content-Type: image/jpeg
```

In the browser:

- [ ] `https://<your-app>.up.railway.app/frontend/home` — public SPA loads with images (Solomon Islands banner, charts, policy thumbnails all render).
- [ ] `https://<your-app>.up.railway.app/login` — custom login page.
- [ ] Log in as `Administrator` / `$ADMIN_PASSWORD` — expect redirect to `/app` (Frappe desk); this is intentional, see [Login redirects to /app instead of /frontend](#login-redirects-to-app-instead-of-frontend).
- [ ] Create a Project from the desk, log out, redeploy, and verify the Project still exists (volume persistence check).

If any checklist item fails, see [Troubleshooting](#troubleshooting).

## Accessing the container shell

Railway's CLI has two similar-sounding commands — **use `railway ssh` for a shell in the running container**; `railway shell` only opens a *local* subshell with Railway env vars injected and is often confused for the remote shell.

```bash
# Install CLI once
brew install railway           # or: npm i -g @railway/cli

railway login
railway link                   # pick the iMRV project

# Service name is case-sensitive and must match what Railway shows:
railway ssh --service "iMRV-Solomon-Islands"

# If your CLI version doesn't have ssh, update:
brew upgrade railway
```

You land as `root` (PID 1 is Supervisor). Switch to the frappe user for bench commands:

```bash
gosu frappe bash
cd /home/frappe/frappe-bench
```

**Fallback if CLI ssh isn't available:** Railway dashboard → project → app service → latest deployment → `⋯` menu → **SSH** / **Shell** opens a browser terminal.

**One-off command without an interactive session:**

```bash
railway run --service "iMRV-Solomon-Islands" bash -c 'cd /home/frappe/frappe-bench && bench --site "$SITE_NAME" migrate'
```

`railway run` attaches the same volume, so file changes persist.

## Troubleshooting

### Can't log in as Administrator

Usually one of:

1. **Password isn't `admin`.** `ADMIN_PASSWORD` env var sets it on first boot. Check Railway Variables for the app service.
2. **Account locked from failed attempts.** Wait a minute or reset from inside the container:

   ```bash
   cd /home/frappe/frappe-bench
   bench --site "$SITE_NAME" set-admin-password "<new-password>"
   ```

3. **Changed `ADMIN_PASSWORD` in Railway after first boot.** That env var is only read by [entrypoint.sh:87](entrypoint.sh#L87) during initial site creation. To rotate later, use `bench set-admin-password` as above.

### Images 404 on /frontend/home

We hit this one on first deploy. Two distinct causes — check both.

**Cause A: Default seed files never landed on disk.** `after_install` in [mrvtools/mrvtools/after_install.py:16](../../mrvtools/mrvtools/after_install.py#L16) unzips `mrv_default_files.zip` into `sites/<site>/public/files/` but wraps failures into Frappe's Error Log silently. The loader also has a skip guard that won't re-extract if `File` DB records exist — even if the physical files are missing.

Verify and recover:

```bash
# Inside the container as frappe:
ls /home/frappe/frappe-bench/sites/$SITE_NAME/public/files | wc -l
# → If near zero, files didn't extract.

cd /home/frappe/frappe-bench/sites/$SITE_NAME/public/files
# The container image doesn't include `unzip`; use Python instead:
python3 -c "
import zipfile, os
z = zipfile.ZipFile('/home/frappe/frappe-bench/apps/mrvtools/mrvtools/public/mrv_default_files.zip')
for info in z.infolist():
    if info.is_dir() or info.filename.startswith('__MACOSX/'): continue
    name = os.path.basename(info.filename)
    if not name or name.startswith('.'): continue
    dest = os.path.join('.', name)
    if os.path.exists(dest): continue
    with z.open(info) as src, open(dest, 'wb') as dst: dst.write(src.read())
    print('wrote', name)
"
chown -R frappe:frappe .
```

Also re-run the seed loaders (safe/idempotent) to repopulate DB records if those are the bit that's missing:

```bash
bench --site "$SITE_NAME" execute mrvtools.mrvtools.after_install.load_master_data
bench --site "$SITE_NAME" execute mrvtools.mrvtools.after_install.load_default_files
bench --site "$SITE_NAME" execute mrvtools.mrvtools.after_install.load_single_doc
bench --site "$SITE_NAME" clear-cache
```

**Cause B: nginx wasn't serving `/files/` as static.** Fixed in commit `00b45ab` — nginx now aliases `/files/` directly to disk instead of proxying to gunicorn. If you're running an older image, redeploy from `master` to pick up the fix. Verify with:

```bash
curl -sI http://127.0.0.1:$PORT/files/iMRV2.jpg | head -2
# → HTTP/1.1 200 OK
```

### Login redirects to /app instead of /frontend

**Not a bug.** The `on_session_creation` handler in [frappe_side_menu/frappe_side_menu/api.py:181](../../frappe_side_menu/frappe_side_menu/api.py#L181) sets the post-login landing to `/app/<route>` (the Frappe desk), which is where System Users like `Administrator` are expected to land.

To reach the public SPA, navigate directly to `https://<your-app>.up.railway.app/frontend/home` — login isn't required. Session cookies carry through if you do want authenticated API calls.

To redirect all users to the SPA instead of desk, edit [api.py:184](../../frappe_side_menu/frappe_side_menu/api.py#L184) to `frappe.local.response['home_page'] = "/frontend/" + (route or "home")`, but that'll break admin access to the desk.

### SPA crashes with `s.value.message.parent_data` undefined

The `get_all` API on MrvFrontend returned an error, usually because the `MrvFrontend` single doc isn't populated. Run the seed loader:

```bash
bench --site "$SITE_NAME" execute mrvtools.mrvtools.after_install.load_single_doc
```

### App service keeps restarting

Railway dashboard → app → Deployments → latest → View Logs. Most common cause is a missing env var — the entrypoint's `: "${VAR:?}"` checks print exactly which one. If the variable actually *is* set in the UI but the container reports it missing, see [Raw Editor gotchas](#raw-editor-gotchas) — it's almost always whitespace in the key, a failing reference expansion, or a stale deploy.

### `DB_HOST must be set` even though it's set in the UI

The reference `${{mariadb.RAILWAY_PRIVATE_DOMAIN}}` expanded to empty. Either:

- The MariaDB service isn't named exactly `mariadb` (case-sensitive). Rename it, or update the reference to match.
- MariaDB and app are in different Railway environments. References don't cross environments — check the environment selector at the top of the UI.
- Private networking isn't enabled on the MariaDB service. Settings → Networking → toggle on.

**Unblock immediately:** hardcode `DB_HOST=mariadb.railway.internal` (substitute the actual service name if different). Railway's private DNS is always `<service>.railway.internal`.

### Redis `unauthenticated bulk length` / `Protocol error`

Your Redis URLs don't include the password. Railway's managed Redis requires AUTH. Grab `REDIS_PASSWORD` from the redis service's Variables tab and use `redis://default:<password>@redis.railway.internal:6379/<db>` format. See the Environment variables table above.

### `Exception: Database _xxx already exists` (first boot)

A previous boot got partway through `bench new-site` — created the DB but crashed before writing `site_config.json`. On the next boot the entrypoint sees no config and takes the "first boot" path again, which tries `CREATE DATABASE` on a name that's already there.

**Fix — wipe both volumes simultaneously:**

1. `mariadb` service → Settings → Volumes → detach & delete. Re-add fresh at `/var/lib/mysql`.
2. `app` service → Settings → Volumes → detach & delete. Re-add fresh at `/home/frappe/frappe-bench/sites`.
3. Redeploy `mariadb`, wait Active, then redeploy `app`.

Wiping just one leaves the other with orphan state and the loop continues.

### `OSError: b'./apps.txt' Not Found`

A persistent volume mounted at `/home/frappe/frappe-bench/sites` shadowed the `apps.txt` that `bench init` wrote during image build. [entrypoint.sh:33-40](entrypoint.sh#L33-L40) seeds the volume from `/home/frappe/sites-template/` if `apps.txt` is missing — if you see this error, either you're on an image predating commit `b968be2`, or the seed copy itself failed.

Check `ls /home/frappe/sites-template/` inside the container — it should contain `apps.txt`, `common_site_config.json`, and `assets/`. If empty or missing, rebuild the image.

### First boot takes >5 min

Check MariaDB is healthy (green Active badge) and the app can resolve `${{mariadb.RAILWAY_PRIVATE_DOMAIN}}` — if MariaDB was added after the app service, redeploy the app so Railway re-injects the reference.

### "The train has not arrived at the station" when hitting the domain

Railway's default 404 page, served when:

- The custom domain isn't registered on any service. App service → Settings → Domains → + Custom Domain → enter the domain exactly.
- The domain is registered but the **Target Port** is wrong (often defaults to 8000). Edit the domain row → set **Target Port to 8080** (matches `$PORT` in [nginx.conf.template](nginx.conf.template)).
- DNS points somewhere other than Railway (verify with `dig <your-domain>` — the CNAME should resolve to a `.up.railway.app` target).

### Cloudflare in front of Railway

Railway supports Cloudflare proxying (orange cloud), but the default "Flexible" SSL mode causes redirect loops.

**Easiest setup:** set the CNAME to **DNS only (grey cloud)**. Railway provisions TLS itself; Cloudflare just forwards DNS.

**If you want Cloudflare CDN/WAF (orange cloud):**

1. Cloudflare → SSL/TLS → Overview → mode **Full (strict)** (NOT Flexible).
2. Don't use Cloudflare's "Custom Hostnames" / "SSL for SaaS" feature — that's for multi-tenant SaaS setups and doesn't apply here. Just the normal DNS CNAME.
3. Add the domain in Railway's app service → Settings → Domains before expecting traffic to route.
4. **Keep the hostname one level deep from the zone apex.** Cloudflare's free Universal SSL cert covers only `<zone>` + `*.<zone>` — so inside zone `example.com`, `demo.example.com` works but `demo.foo.example.com` does not. See the handshake-failure entry below.

### Cloudflare TLS `handshake_failure` on a deep subdomain

Symptom: `curl` to the proxied hostname fails before any HTTP response, with something like:

```text
LibreSSL/3.3.6: error:1404B410:SSL routines:ST_CONNECT:sslv3 alert handshake failure
curl: (35) ... sslv3 alert handshake failure
```

Cause: Cloudflare's free Universal SSL certificate on a zone `<zone>` covers `<zone>` and `*.<zone>` **only — a single level of wildcard.** A hostname like `demo.imrv.netzerolabs.io` inside zone `netzerolabs.io` is two levels deep and is not on the cert, so Cloudflare's edge has nothing to present for that SNI and aborts the handshake with alert 40.

Confirm with SNI probes against the same IP (swap in your hostname / zone):

```bash
# Zone apex — presents the Cloudflare Universal cert
echo | openssl s_client -connect demo.imrv.netzerolabs.io:443 \
  -servername netzerolabs.io 2>&1 | grep -E "subject=|issuer="
# → subject=CN=netzerolabs.io   issuer=... Let's Encrypt ...

# Deep subdomain — alert 40, no cert
echo | openssl s_client -connect demo.imrv.netzerolabs.io:443 \
  -servername demo.imrv.netzerolabs.io 2>&1 | grep -E "alert|Cipher is"
# → SSL alert number 40   Cipher is (NONE)
```

Also check `dig NS <parent-of-deep-subdomain>` — if it returns no records, there is no dedicated Cloudflare zone for that parent, which is the usual trigger.

Fix (easiest first):

1. **Switch the record to DNS-only (grey cloud).** Railway's own Let's Encrypt cert takes over and Cloudflare is no longer in the TLS path. Matches "Easiest setup" above.
2. **Use a single-level host** (`demo.<zone>` instead of `demo.sub.<zone>`). Covered by the existing wildcard. Update Railway's custom domain and the `SITE_NAME` env var to match — see [Custom domain](#custom-domain).
3. **Delegate the intermediate parent as its own Cloudflare zone** (e.g. add `imrv.netzerolabs.io` as a zone, then point the parent zone's `NS` records at the new zone's nameservers). Universal SSL on the new zone then covers `*.imrv.netzerolabs.io`. Keeps orange cloud, no paid plan.
4. **Cloudflare Advanced Certificate Manager** (~$10/mo per zone). Lets you issue a cert that covers deeper wildcards on the existing zone.

### SPA routes 404 (anything under `/frontend/`)

`yarn build` didn't run during the image build, or [mrvtools/www/frontend.html](../../mrvtools/www/frontend.html) isn't in the shipped image. Check build logs for the `--from=frontend-build` COPY step in the Dockerfile.

### Desk CSS/JS bundle 404s (e.g. `desk.bundle.<hash>.css` not found)

`sites/assets/` is build output, not user data, but lives inside the persistent volume. If you're on an image from before this was fixed, the asset manifest (`sites/assets/assets.json`) is frozen at first-boot state while the bench code is newer — hashes in the HTML reference CSS/JS that no longer exist on disk.

Current [entrypoint.sh:46](entrypoint.sh#L46) refreshes `sites/assets/` from the image template on every boot, so a redeploy fixes it. If you need to force it in a running container:

```bash
rm -rf /home/frappe/frappe-bench/sites/assets
cp -a /home/frappe/sites-template/assets /home/frappe/frappe-bench/sites/assets
chown -R frappe:frappe /home/frappe/frappe-bench/sites/assets
supervisorctl restart frappe-gunicorn frappe-socketio
```

### `CSRFTokenError` on API calls from the SPA

`ignore_csrf` should be `0` in prod. Only set it to `1` for local Vite dev on :8080.

### Socket.io "Invalid origin" / `WebSocket connection … failed`

The realtime server checks the browser's `Origin` header against `host_name` in `site_config.json`. [entrypoint.sh:116](entrypoint.sh#L116) sets `host_name` to `https://$SITE_NAME` on every boot, so as long as `SITE_NAME` matches the domain the browser is hitting, this works.

If `SITE_NAME` and the public domain differ (e.g. Railway auto-generated domain still set, but users visit a custom CNAME), update `SITE_NAME` to the domain the browser actually uses, then redeploy.

For non-TLS local testing, set `SITE_PROTOCOL=http` to override the https default.

## Operations

### Custom domain

1. Add the domain in Railway UI (app service → Settings → Domains). Follow Railway's DNS instructions.
2. Update `SITE_NAME` env var to the new domain. This triggers a redeploy.
3. Re-run the verification checklist — in particular the `/files/iMRV2.jpg` curl — because the nginx `alias` path is derived from `SITE_NAME`.

The entrypoint sets `host_name` (Frappe's canonical site URL, used for socket.io origin checks) to `https://$SITE_NAME` on every boot, so no manual `bench set-config` step is needed. If you need a non-https scheme (e.g. local testing), set `SITE_PROTOCOL=http` in Railway variables.

### Manual backups

Staging has no automated backups. Ad-hoc dump via the MariaDB service's one-off runner:

```bash
railway run --service mariadb mysqldump \
  -u root -p"$MYSQL_ROOT_PASSWORD" \
  --all-databases --single-transaction --quick \
  > backup-$(date +%F).sql
```

Store the resulting file somewhere durable (S3, 1Password, etc.).

### Cost (April 2026)

- App service (Docker): ~$5–10/mo depending on memory footprint
- MariaDB custom service: ~$5/mo
- Redis plugin: free tier available, ~$5/mo beyond
- Total typical staging: ~$10–20/mo

## Local integration test

Before pushing to Railway, bring the full stack up locally to validate image changes:

```bash
docker compose -f deploy/railway/docker-compose.local.yml up --build
```

Open <http://localhost:8080>. Default credentials: `Administrator` / `admin`. Tear down (wipes local volumes):

```bash
docker compose -f deploy/railway/docker-compose.local.yml down -v
```

This uses the exact same [Dockerfile](../../Dockerfile) + [entrypoint.sh](entrypoint.sh) + [nginx.conf.template](nginx.conf.template) that Railway does, so issues reproduce here before they bite in production.
