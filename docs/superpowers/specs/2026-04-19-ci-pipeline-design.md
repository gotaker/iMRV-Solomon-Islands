# CI Pipeline Design

**Date:** 2026-04-19
**Platform:** GitHub Actions
**Scope:** Automated checks for the iMRV Solomon Islands monorepo (mrvtools + frappe_side_menu Frappe apps, plus the Vue 3 SPA under `frontend/`).

## Goals

- Catch broken builds, lint regressions, and failing Frappe doctype tests before they reach `master`.
- Give contributors fast feedback (<2 min) on every push.
- Gate `master` merges with the full Frappe test suite.
- Detect silent regressions via a nightly run against `master`.

## Non-goals

- Smoke-testing `install.sh` end-to-end (deferred — slow, warrants its own spec).
- Security scanning / dependency auditing (deferred).
- Deploy or release automation (deferred).
- Python/Node version matrix testing (single-deployment app; not warranted).

## Version pins

Pinned to match [install.sh](../../../install.sh):

- Python **3.11**
- Node **18**
- Frappe branch **version-15**
- MariaDB **10.6**, Redis **7** (CI service containers)

Drift between CI and install.sh is a real risk — these values live in one place in each workflow file and must be updated together when install.sh's defaults change.

## Workflow layout

Two workflow files under `.github/workflows/`:

| File | Triggers | Jobs | Target runtime |
|---|---|---|---|
| `ci-fast.yml` | `push`, `pull_request` | `frontend-build`, `frontend-format`, `python-lint` | <2 min |
| `ci-frappe-tests.yml` | `pull_request` targeting `master`, `schedule: '0 2 * * *'` | `frappe-tests` | ~8–12 min |

Rationale for the split: fast feedback on typos and build breaks without waiting for MariaDB/Redis/bench to boot. Master merges are still gated by real tests.

## `ci-fast.yml` — fast checks

Runs on `ubuntu-latest`. `fail-fast: false` so contributors see all three results, not just the first failure.

### Job: `frontend-build`

- `actions/setup-node@v4` with Node 18, `cache: yarn`, `cache-dependency-path: frontend/yarn.lock`
- `yarn --cwd frontend install --frozen-lockfile`
- `yarn --cwd frontend build`

Catches broken imports, Vite misconfig, missing deps, and drift between the `--base=/assets/mrvtools/frontend/` flag and the `website_route_rules` / `app_include_*` entries in [mrvtools/hooks.py](../../../mrvtools/hooks.py).

### Job: `frontend-format`

- Same Node 18 setup
- `yarn --cwd frontend install --frozen-lockfile`
- `npx prettier --check "frontend/src/**/*.{js,vue,css}"`

**Pre-landing chore:** before this check is enabled, run `prettier --write` across `frontend/src/` once and commit the result. Without that one-time pass the first CI run would fail on legacy formatting.

### Job: `python-lint`

- `actions/setup-python@v5` with Python 3.11, `cache: pip`
- `pip install ruff`
- `ruff check mrvtools/ frappe_side_menu/`

Ruff config at repo root as `ruff.toml` with a minimal rule set: `E` (pycodestyle errors), `F` (pyflakes — undefined names, unused imports), `I` (import sorting). Deliberately conservative so the first run passes without reformatting — stricter rules can be added later as follow-ups.

## `ci-frappe-tests.yml` — Frappe doctype tests

Runs on `ubuntu-22.04` to match install.sh's apt-based path.

### Triggers

```yaml
on:
  pull_request:
    branches: [master]
  schedule:
    - cron: '0 2 * * *'
```

### Services

```yaml
services:
  mariadb:
    image: mariadb:10.6
    env:
      MARIADB_ROOT_PASSWORD: ${{ secrets.MARIADB_ROOT_PASSWORD }}
    ports: [3306:3306]
    options: >-
      --health-cmd "mariadb-admin ping --password=$MARIADB_ROOT_PASSWORD"
      --health-interval 10s --health-timeout 5s --health-retries 10
  redis:
    image: redis:7
    ports: [6379:6379]
```

### Steps

1. Checkout repo at `apps/mrvtools` inside a bench directory layout.
2. Install system apt deps: `wkhtmltopdf`, `libcups2-dev`, `xfonts-75dpi`, `xfonts-base`, `software-properties-common`, etc. (the subset of install.sh's apt list that isn't covered by the service containers).
3. `actions/setup-python@v5` Python 3.11 (with pip cache).
4. `actions/setup-node@v4` Node 18 (with yarn cache).
5. `actions/cache@v4` for the apt package list, keyed on the hash of the package list. ~1 min savings per run.
6. `pip install frappe-bench`.
7. `bench init --skip-redis-config-generation --frappe-branch version-15 --python python3.11 frappe-bench`.
8. Symlink the checkout into `frappe-bench/apps/mrvtools`; same for `frappe_side_menu`.
9. `bench new-site test_site --mariadb-root-password <secret> --admin-password admin --no-mariadb-socket`.
10. `bench --site test_site install-app mrvtools`.
11. `bench --site test_site install-app frappe_side_menu`.
12. `bench --site test_site migrate`.
13. `bench --site test_site run-tests --app mrvtools`.
14. `bench --site test_site run-tests --app frappe_side_menu`.

### Approach: reimplement, not reuse

install.sh is not invoked directly from CI. It does significant host-setup work CI doesn't need (Homebrew, `systemctl start`, bench-managed redis daemons on ports 11000/13000, MariaDB root-password provisioning via socket). The CI workflow reimplements the relevant install sequence inline. Drift with install.sh is managed by review discipline — any change to install.sh's Frappe-relevant steps (Python version, Node version, Frappe branch, apt package list) requires a corresponding edit to `ci-frappe-tests.yml` in the same PR.

### Site sharing

Both apps install into the same `test_site`. This is faster (one bench init, one site) and matches production, where both apps are installed together.

### Secrets

- `MARIADB_ROOT_PASSWORD` — GitHub repository secret. No default; the workflow fails fast if unset.

## Caching

- Yarn cache via `actions/setup-node@v4` built-in cache, keyed on `frontend/yarn.lock`.
- Pip cache via `actions/setup-python@v5` built-in cache.
- Apt cache via `actions/cache@v4` keyed on a hash of the package list.
- Bench `frappe-bench/env/` venv: **not cached** (complexity exceeds the benefit for a single workflow).

## Failure handling

- Each job fails independently.
- `ci-fast.yml` uses `fail-fast: false`.
- On Frappe test failure, upload `frappe-bench/logs/` as a workflow artifact with 7-day retention.
- Nightly failures auto-open a GitHub issue labelled `ci-nightly-failure`, using `gh issue create` in an `if: failure() && github.event_name == 'schedule'` step. Issue title includes the workflow run URL; body links to logs. Duplicate issues are acceptable — a human closes them after triage.

## Branch protection (manual, post-merge)

After the workflows land, configure via repo Settings → Branches → `master`:

Required status checks:
- `frontend-build`
- `frontend-format`
- `python-lint`
- `frappe-tests`

This step is manual because it cannot be committed to the repo. Document it in the workflow files as a comment.

## Files changed / added

New:
- `.github/workflows/ci-fast.yml`
- `.github/workflows/ci-frappe-tests.yml`
- `ruff.toml`

Modified (one-time):
- Files under `frontend/src/` reformatted by Prettier.

## Open risks

- **First Prettier run:** legacy files may surface surprising reformats. Run locally first and inspect the diff before committing.
- **Frappe-bench memory:** `bench init` + MariaDB + Redis on the default GitHub Actions runner (7 GB RAM) is close to the edge. If we hit OOM, first mitigation is `bench init --no-backups` and skipping scheduler; second is a larger runner.
- **Drift with install.sh:** the workflow duplicates Python/Node/Frappe pinning. Acceptable cost for CI-specific simplicity, but every install.sh version bump needs a paired CI bump.
