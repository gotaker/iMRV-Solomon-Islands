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
   - Image: `mariadb:10.6`
   - Variables: `MYSQL_ROOT_PASSWORD` = *(strong random — save it; the app needs the same value)*
   - *Settings → Volumes* — mount `/var/lib/mysql`, size 5 GB.
   - Deploy.

3. **Add Redis as a third service:**
   - *New → Database → Redis* (Railway's managed plugin).
   - No configuration needed.

4. **Attach a volume to the app service:**
   - App service → Settings → Volumes → Add Volume.
   - Mount path: `/home/frappe/frappe-bench/sites`, size 5 GB.
   - This is where the site config, DB seeds, and uploaded files persist across deploys.

5. **Set environment variables on the app service** (see table below).

6. **Trigger a deploy.** Push to the tracked branch or click Deploy.

## Environment variables

Set these on the **app** service. `PORT` is auto-injected by Railway — do not set it manually.

| Variable | Value | Notes |
| --- | --- | --- |
| `SITE_NAME` | `${{RAILWAY_PUBLIC_DOMAIN}}` | Railway reference. Expands to the auto-generated `.up.railway.app` domain. If you add a custom domain later, see [Custom domain](#custom-domain). |
| `ADMIN_PASSWORD` | *strong random string* | **Save this immediately.** Used only on first boot to create the `Administrator` account. Changing it in Railway after first boot does **not** rotate the DB password — use `bench … set-admin-password` (see [Troubleshooting](#cant-log-in-as-administrator)). |
| `DB_HOST` | `${{mariadb.RAILWAY_PRIVATE_DOMAIN}}` | Railway reference to the MariaDB service's private hostname. |
| `DB_PORT` | `3306` | |
| `DB_ROOT_PASSWORD` | *same value as MariaDB's `MYSQL_ROOT_PASSWORD`* | |
| `REDIS_CACHE_URL` | `redis://${{redis.RAILWAY_PRIVATE_DOMAIN}}:6379/0` | |
| `REDIS_QUEUE_URL` | `redis://${{redis.RAILWAY_PRIVATE_DOMAIN}}:6379/1` | |
| `REDIS_SOCKETIO_URL` | `redis://${{redis.RAILWAY_PRIVATE_DOMAIN}}:6379/2` | |

The [entrypoint.sh](entrypoint.sh) aborts immediately with a clear error if any of these are missing (`: "${VAR:?…}"` checks).

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

Railway dashboard → app → Deployments → latest → View Logs. Most common cause is a missing env var — the entrypoint's `: "${VAR:?}"` checks print exactly which one.

### First boot takes >5 min

Check MariaDB is healthy (green Active badge) and the app can resolve `${{mariadb.RAILWAY_PRIVATE_DOMAIN}}` — if MariaDB was added after the app service, redeploy the app so Railway re-injects the reference.

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
