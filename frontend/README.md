# frontend — Vue 3 SPA

The public-facing Solomon Islands MRV portal. Vue 3 + Vite + TailwindCSS + [Frappe UI](https://github.com/frappe/frappe-ui), built into [`mrvtools/public/frontend/`](../mrvtools/public/frontend/) and served by Frappe at `/frontend/*`.

## Build and run

```bash
yarn install        # first time
yarn dev            # Vite dev server on :8080, proxies to bench on :8000
yarn build          # production build → mrvtools/public/frontend/
                    # also copies index.html → mrvtools/www/frontend.html
```

Dev server proxies `/api`, `/method`, `/assets`, `/files`, `/private`, `/app`, `/login`, `/logout`, `/socket.io` to the adjacent Frappe bench. Host-aware: visit `http://mrv.localhost:8080` to proxy to `http://mrv.localhost:8000`.

## Verifying a production build

Don't use `vite preview` — it serves from `frontend/dist` with the dev base URL. Instead:

```bash
yarn build
python3 -m http.server -d ../mrvtools/public/frontend 8090
# load http://localhost:8090/
```

## Build pipeline

[`vite.config.mjs`](vite.config.mjs) drives the build via `frappe-ui/vite`'s plugin with `buildConfig: { outDir, baseUrl, indexHtmlPath }`. The `.mjs` extension is load-bearing (`frappe-ui/vite` is ESM-only). Output paths and the `website_route_rules` / `app_include_*` entries in [`mrvtools/hooks.py`](../mrvtools/hooks.py) must stay in sync.

## More

See the root [`CLAUDE.md`](../CLAUDE.md) for architecture notes, the routing handoff (`/frontend/<path:app_path>` → Frappe → Vue router with `createWebHistory('/frontend')`), the `useReveal()` composable for scroll animations, and the `createResource(...).data` unwrap idiom.
