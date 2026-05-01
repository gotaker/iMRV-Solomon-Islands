# mrvtools — primary Frappe app

Frappe app for Solomon Islands MRV (Measurement, Reporting, Verification) tooling: projects, adaptation, mitigation, GHG inventory, climate finance, and the public-facing reports portal.

## Modules

This app ships two Frappe modules (see [`modules.txt`](modules.txt)):

- `Mrvtools` — under [`mrvtools/`](mrvtools/) — the main MRV doctypes, dashboards, and reports.
- `GHG Inventory` — under [`ghg_inventory/`](ghg_inventory/) — sector-specific emissions tracking and reporting.

## Install

From your bench root:

```bash
bench get-app mrvtools <path-or-url>
bench --site <site> install-app mrvtools
bench --site <site> migrate
```

## Key entry points

- [`api.py`](api.py) — whitelisted endpoints: `get_approvers`, `route_user`, `get_data` (allowlist-narrowed; never bypass), `replace_email_domain` (System Manager only).
- [`hooks.py`](hooks.py) — Frappe wiring: `website_route_rules` (SPA routing handoff), `after_install` (seed master data + default files + Single docs), `permission_query_conditions` for `My Approval` and `Approved User`.
- [`mrvtools/after_install.py`](mrvtools/after_install.py) — three loaders run on install: `load_master_data` (~35 doctypes from JSON in `master_data/`), `load_default_files` (unzips `public/mrv_default_files.zip`), `load_single_doc` (Website Settings, Navbar Settings, Side Menu Settings, MrvFrontend).
- [`mrvtools/doctype/mrvfrontend/mrvfrontend.py`](mrvtools/doctype/mrvfrontend/mrvfrontend.py) — `get_all()`: SPA home-page payload loader.

## Doctype conventions

- `*_childtable` — Frappe child tables; not independently listable.
- `*_master_list` — reference/lookup tables seeded by `load_master_data`.
- `edited_*` — revision/draft variants of base doctypes; treat as paired.

## More

See the root [`CLAUDE.md`](../CLAUDE.md) for full architecture, the SPA build pipeline ([`frontend/`](../frontend/)), Railway deployment, and the test harness ([`tests/`](../tests/)).
