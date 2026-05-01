# iMRV Solomon Islands

Measurement, Reporting and Verification (MRV) tooling for Solomon Islands — climate adaptation, mitigation tracking, GHG inventory, climate finance, and reporting.

## Stack

Three layers in one repo:

- **`mrvtools/`** — the main [Frappe](https://frappeframework.com/) app (projects, adaptation, mitigation, GHG inventory, climate finance, reports).
- **`frappe_side_menu/`** — a separate Frappe app providing a custom sidebar/workspace UI.
- **`frontend/`** — a Vue 3 + Vite + Tailwind + Frappe UI SPA served by Frappe at `/frontend/*`.

See [CLAUDE.md](CLAUDE.md) for a deeper architectural tour (routing handoff, seed data, permission query conditions, server-side entry points).

## Design philosophy — Forest-and-Sage editorial system

A single editorial design system spans all three layers: the public SPA at `/frontend/*`, the Frappe desk at `/app/*`, and the custom `/login` page. Designed to replace the Bootstrap/AOS/CDN-dependent legacy templates with a continuous, self-hosted, brand-coherent experience.

**Typography.** [Anton](https://fonts.google.com/specimen/Anton) for display (h1/h2, modal titles, large stat numbers, program-card titles); [Inter](https://rsms.me/inter/) for everything else. Both self-hosted under [`mrvtools/public/fonts/`](mrvtools/public/fonts/) and [`frontend/src/assets/Anton/`](frontend/src/assets/Anton/) — **zero CDN calls** (hard requirement for offline / low-bandwidth deployment).

**Palette.** Forest (`#01472e`) + cream (`#fefae0`) + sage tones, with derived alpha scrims (`--ed-forest-08/-12/-20/-60`). All tokens declared once at `:root` in [`frappe_side_menu/public/css/frappe_side_menu.css`](frappe_side_menu/public/css/frappe_side_menu.css) and consumed via `var(--ed-*)`. The SPA mirrors them in [`frontend/tailwind.config.js`](frontend/tailwind.config.js); palette changes update **both** files.

**Surface language.**

- **Persistent surfaces** (page bg, navbar, sidebar) — flat `var(--ed-cream)`, never frosted.
- **Ephemeral surfaces** (modals, dropdowns, tooltips, popovers, the floating drawer) — frosted-glass: `backdrop-filter: blur(20px) saturate(140%)`, `var(--ed-frost-bg)`, hairline forest border. Backdrop dim uses `blur(4px)`.
- **Cards** — white, hairline `var(--ed-forest-08)` border, `var(--ed-shadow-forest)`, `var(--ed-radius-card)`.
- **Buttons + pills** — `var(--ed-radius-pill)`, uppercase, `letter-spacing: 0.3em`, 11px / 700 Inter.

**Adherence rules.** Never hardcode hex literals — always `var(--ed-*)`. Never re-override the `:root` Frappe v16 variables that [`mrvtools/public/css/editorial/01-foundation.css`](mrvtools/public/css/editorial/01-foundation.css) owns. Add new desk styles to one of the existing `0X-*.css` layers (or a new `08-*.css` wired into [`mrvtools/hooks.py`](mrvtools/hooks.py) `app_include_css`). Diagnose selector/loading bugs before reaching for token swaps — "fix the font" usually means a CSS specificity issue, not a wrong token.

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
