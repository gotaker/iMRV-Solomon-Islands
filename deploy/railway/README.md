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

```
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

```
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

## Local integration test

Before deploying to Railway, you can run the full stack locally to verify the image:

```
docker compose -f deploy/railway/docker-compose.local.yml up --build
```

Then open http://localhost:8080. Default credentials: `Administrator` / `admin`. Bring down with `docker compose -f deploy/railway/docker-compose.local.yml down -v` (the `-v` removes the local volumes).
