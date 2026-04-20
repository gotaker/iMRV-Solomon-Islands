# iMRV Solomon Islands

Measurement, Reporting and Verification (MRV) tooling for Solomon Islands — climate adaptation, mitigation tracking, GHG inventory, climate finance, and reporting.

## Stack

Three layers in one repo:

- **`mrvtools/`** — the main [Frappe](https://frappeframework.com/) app (projects, adaptation, mitigation, GHG inventory, climate finance, reports).
- **`frappe_side_menu/`** — a separate Frappe app providing a custom sidebar/workspace UI.
- **`frontend/`** — a Vue 3 + Vite + Tailwind + Frappe UI SPA served by Frappe at `/frontend/*`.

See [CLAUDE.md](CLAUDE.md) for a deeper architectural tour (routing handoff, seed data, permission query conditions, server-side entry points).

## Quick start (local dev)

One-command bootstrap on a fresh macOS, Ubuntu, or WSL2 laptop:

```bash
MYSQL_ROOT_PASSWORD=<pw> ./install.sh --dev
```

The script installs OS deps, runs `bench init`, creates a site, installs both apps, builds the SPA, and flips dev flags (`ignore_csrf`, `developer_mode`). See [install.sh](install.sh) for env-var overrides (`BENCH_DIR`, `SITE_NAME`, `FRAPPE_BRANCH`, etc.) or run with `DRY_RUN=1` to preview.

For production installs: `./install.sh --prod` (with `PROD_DOMAIN=<fqdn>` and optionally `PROD_ENABLE_TLS=1` on Ubuntu).

## Development

```bash
yarn --cwd frontend install
yarn dev        # Vite on :8080, proxies to bench on :8000
yarn build      # Vite build → mrvtools/public/frontend/
```

Vite dev mode requires `"ignore_csrf": 1` in `site_config.json` — `install.sh --dev` sets this.

## Deployment

### Railway (staging/demo)

Single-container Frappe + MariaDB + Redis deployment via multi-stage Dockerfile. See [deploy/railway/README.md](deploy/railway/README.md) for the operator runbook (3 Railway services, env-var table, first-deploy expectations, troubleshooting).

Local integration test of the Railway image:

```bash
docker compose -f deploy/railway/docker-compose.local.yml up --build
```

### Manual VPS / bare metal

Use `install.sh --prod` on a fresh Ubuntu host. The script runs the same `bench get-app` / `install-app` / `migrate` / `yarn build` sequence and optionally provisions a Let's Encrypt cert.

## Tests & CI

Frappe's test runner (requires a bench + site):

```bash
bench --site <site> run-tests --app mrvtools
bench --site <site> run-tests --app frappe_side_menu
```

CI runs on every PR via GitHub Actions — fast lint/build checks plus a full bench-tests job against ephemeral MariaDB + Redis. See [.github/workflows/](.github/workflows/) and the design spec at [docs/superpowers/specs/2026-04-19-ci-pipeline-design.md](docs/superpowers/specs/2026-04-19-ci-pipeline-design.md).

## License

MIT
