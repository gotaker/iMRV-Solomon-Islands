# CI Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add GitHub Actions CI that runs fast checks (frontend build, Prettier, ruff) on every push and the full Frappe doctype test suite on PRs targeting `master` + nightly, per [docs/superpowers/specs/2026-04-19-ci-pipeline-design.md](../specs/2026-04-19-ci-pipeline-design.md).

**Architecture:** Two workflow files — `ci-fast.yml` (parallel lightweight jobs on `ubuntu-latest`) and `ci-frappe-tests.yml` (MariaDB + Redis service containers, `bench init`, `bench run-tests` on `ubuntu-22.04`). Versions pinned to match [install.sh](../../../install.sh): Python 3.11, Node 18, Frappe `version-15`, MariaDB 10.6, Redis 7.

**Tech Stack:** GitHub Actions, ruff, Prettier, frappe-bench, MariaDB 10.6, Redis 7.

---

## Repository orientation (read before starting)

- Two Frappe apps live at repo root: `mrvtools/` and `frappe_side_menu/`.
- Frontend Vue SPA lives in `frontend/`; scripts defined in [frontend/package.json](../../../frontend/package.json). `frontend/yarn.lock` exists. Prettier config is [frontend/.prettierrc.json](../../../frontend/.prettierrc.json): `{"semi": false, "singleQuote": true}`.
- [install.sh](../../../install.sh) bootstraps the full stack; CI mirrors its version pins but reimplements steps (install.sh does host-level setup CI doesn't need).
- No CI currently exists. No `.github/` directory yet — you will create it.
- Commits do NOT include a `Co-Authored-By` trailer (project convention).

---

## File Structure

**New files:**
- `ruff.toml` — minimal ruff config (E, F, I rules) at repo root.
- `.github/workflows/ci-fast.yml` — fast checks workflow.
- `.github/workflows/ci-frappe-tests.yml` — Frappe doctype tests workflow.

**Modified files (one-time Prettier reformat):**
- Files under `frontend/src/` matching `*.{js,vue,css}` (26 files at time of planning).

**Documentation touch-up:**
- `CLAUDE.md` — one short paragraph describing the CI workflows and linking to the spec.

---

## Task 1: Add ruff config and verify it passes locally

**Files:**
- Create: `ruff.toml`

- [ ] **Step 1: Install ruff locally**

Run:
```bash
pipx install ruff || pip install --user ruff
ruff --version
```
Expected: prints a version (any recent version is fine — CI will pin in Task 3).

- [ ] **Step 2: Create `ruff.toml` at repo root**

Write this exact content to `ruff.toml`:

```toml
# Minimal ruff config for CI. Deliberately conservative so the first
# CI run passes without requiring reformatting. Add rules incrementally.

target-version = "py311"
line-length = 110

[lint]
select = [
    "E",  # pycodestyle errors
    "F",  # pyflakes (undefined names, unused imports)
    "I",  # import sorting
]

ignore = [
    "E501",  # line too long — not enforced yet; revisit when codebase is cleaner
]

[lint.per-file-ignores]
# Frappe test files import * from a controller module by convention
"**/test_*.py" = ["F403", "F405"]
# __init__.py re-exports
"**/__init__.py" = ["F401"]
```

- [ ] **Step 3: Run ruff against both apps to confirm it passes on current code**

Run:
```bash
ruff check mrvtools/ frappe_side_menu/
```

Expected: `All checks passed!` or a small number of trivially-fixable findings.

If findings appear: inspect them. If they are real bugs (undefined names, shadowed builtins) fix the code. If they are stylistic noise, add to `ignore` in `ruff.toml`. **Do not add blanket ignores** — each added rule should be justified with a one-line comment.

- [ ] **Step 4: Run ruff with a deliberately-broken file to confirm it fails**

Create a scratch file `mrvtools/_ruff_smoketest.py`:
```python
import os
import sys
x = undefined_name
```

Run:
```bash
ruff check mrvtools/_ruff_smoketest.py
```
Expected: non-zero exit, errors include `F821 Undefined name` and `F401 imported but unused`.

Delete the scratch file:
```bash
rm mrvtools/_ruff_smoketest.py
```

- [ ] **Step 5: Commit**

```bash
git add ruff.toml
git commit -m "chore(lint): add ruff config for CI (E, F, I rule set)"
```

---

## Task 2: One-time Prettier format sweep of `frontend/src/`

This is a prerequisite for the `frontend-format` CI job — without it the first CI run would fail on legacy formatting.

**Files:**
- Modify: all files under `frontend/src/` matching `*.{js,vue,css}` (26 files).

- [ ] **Step 1: Install frontend deps if not already present**

Run:
```bash
yarn --cwd frontend install --frozen-lockfile
```
Expected: completes without errors.

- [ ] **Step 2: Run Prettier in check mode and observe failures**

Run:
```bash
yarn --cwd frontend exec prettier --check "src/**/*.{js,vue,css}"
```
Expected: non-zero exit, lists files that need formatting. This confirms the check is working.

- [ ] **Step 3: Apply Prettier formatting**

Run:
```bash
yarn --cwd frontend exec prettier --write "src/**/*.{js,vue,css}"
```
Expected: lists the files it reformatted.

- [ ] **Step 4: Verify check now passes**

Run:
```bash
yarn --cwd frontend exec prettier --check "src/**/*.{js,vue,css}"
```
Expected: `All matched files use Prettier code style!` with exit 0.

- [ ] **Step 5: Verify the frontend still builds after reformatting**

Run:
```bash
yarn --cwd frontend build
```
Expected: build succeeds, writes to `mrvtools/public/frontend/` and `mrvtools/www/frontend.html`. Critical — if the build breaks, Prettier introduced a syntax change (rare, but possible with Vue SFC quirks).

- [ ] **Step 6: Spot-check the diff is cosmetic only**

Run:
```bash
git diff --stat frontend/src
git diff frontend/src | head -80
```

Confirm the diff is whitespace/quotes/semicolons only. No logic changes, no identifier renames.

- [ ] **Step 7: Commit**

```bash
git add frontend/src
git commit -m "style(frontend): apply Prettier formatting to src/

One-time reformat to bring existing sources in line with
.prettierrc.json (semi: false, singleQuote: true). Prerequisite
for the frontend-format CI check."
```

---

## Task 3: Create `ci-fast.yml` workflow

**Files:**
- Create: `.github/workflows/ci-fast.yml`

- [ ] **Step 1: Create the `.github/workflows/` directory**

Run:
```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Install `actionlint` locally for workflow YAML validation**

Run (macOS):
```bash
brew install actionlint
```
Or (Linux):
```bash
bash <(curl -sSL https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
```

Verify:
```bash
actionlint --version
```
Expected: prints a version.

- [ ] **Step 3: Write `.github/workflows/ci-fast.yml`**

Exact content:

```yaml
name: CI (fast checks)

on:
  push:
  pull_request:

jobs:
  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: yarn
          cache-dependency-path: frontend/yarn.lock
      - name: Install frontend deps
        run: yarn --cwd frontend install --frozen-lockfile
      - name: Build frontend
        run: yarn --cwd frontend build

  frontend-format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: yarn
          cache-dependency-path: frontend/yarn.lock
      - name: Install frontend deps
        run: yarn --cwd frontend install --frozen-lockfile
      - name: Check Prettier formatting
        run: yarn --cwd frontend exec prettier --check "src/**/*.{js,vue,css}"

  python-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip
      - name: Install ruff
        run: pip install ruff==0.6.9
      - name: Run ruff
        run: ruff check mrvtools/ frappe_side_menu/
```

Notes on choices embedded above:
- `fail-fast: false` is only valid inside a matrix; these are separate jobs so they run in parallel and fail independently by default. No matrix needed.
- Ruff version pinned to `0.6.9` (recent stable at time of writing). Update the pin deliberately, not automatically.

- [ ] **Step 4: Validate the workflow YAML**

Run:
```bash
actionlint .github/workflows/ci-fast.yml
```
Expected: no output, exit 0.

- [ ] **Step 5: Dry-run each job's command locally to confirm they pass**

Run each of these and confirm exit 0:
```bash
yarn --cwd frontend install --frozen-lockfile
yarn --cwd frontend build
yarn --cwd frontend exec prettier --check "src/**/*.{js,vue,css}"
pip install ruff==0.6.9
ruff check mrvtools/ frappe_side_menu/
```
Expected: every command succeeds. This confirms CI will pass on the current tree once the workflow lands.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/ci-fast.yml
git commit -m "feat(ci): add fast checks workflow (frontend build, prettier, ruff)

Runs on every push and PR. Three parallel jobs catch broken Vite
builds, formatting drift, and basic Python errors in <2 min."
```

---

## Task 4: Create `ci-frappe-tests.yml` workflow

**Files:**
- Create: `.github/workflows/ci-frappe-tests.yml`

- [ ] **Step 1: Read install.sh's apt package list for Ubuntu**

Run:
```bash
sed -n '165,190p' install.sh
```

Confirm the pkgs list in `_install_system_deps_ubuntu` matches what's used in Step 2 below. If install.sh has been updated since this plan was written, use its current list (minus `mariadb-server`, `redis-server`, `cron` — the service containers and the ephemeral runner cover those). **Flag any mismatch to the planner before proceeding.**

- [ ] **Step 2: Write `.github/workflows/ci-frappe-tests.yml`**

Exact content:

```yaml
name: CI (Frappe tests)

on:
  pull_request:
    branches: [master]
  schedule:
    - cron: '0 2 * * *'

# To require this check on master, configure branch protection manually
# via repo Settings -> Branches. This cannot be encoded in the workflow.

jobs:
  frappe-tests:
    runs-on: ubuntu-22.04

    services:
      mariadb:
        image: mariadb:10.6
        env:
          MARIADB_ROOT_PASSWORD: ${{ secrets.MARIADB_ROOT_PASSWORD }}
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mariadb-admin ping -uroot -p${{ secrets.MARIADB_ROOT_PASSWORD }}"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=10
      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd="redis-cli ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=10

    steps:
      - name: Checkout repo at apps/mrvtools
        uses: actions/checkout@v4
        with:
          path: apps/mrvtools

      - name: Cache apt packages
        uses: actions/cache@v4
        with:
          path: /var/cache/apt/archives
          key: apt-${{ runner.os }}-frappe-v1

      - name: Install system apt deps
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            git \
            python3.11 python3.11-venv python3-dev \
            build-essential libssl-dev libffi-dev \
            xvfb libfontconfig

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip

      - uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install frappe-bench
        run: pip install frappe-bench

      - name: Configure MariaDB for Frappe
        run: |
          mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" -h 127.0.0.1 <<SQL
          SET GLOBAL innodb_read_only_compressed = OFF;
          SQL
        env:
          MARIADB_ROOT_PASSWORD: ${{ secrets.MARIADB_ROOT_PASSWORD }}

      - name: Initialize bench
        run: |
          bench init \
            --skip-redis-config-generation \
            --frappe-branch version-15 \
            --python python3.11 \
            frappe-bench
        env:
          # bench init shells out to yarn; ensure it finds Node 18
          PATH: ${{ env.PATH }}

      - name: Symlink apps into bench
        working-directory: frappe-bench
        run: |
          ln -s "$GITHUB_WORKSPACE/apps/mrvtools/frappe_side_menu" apps/frappe_side_menu
          # apps/mrvtools is already inside the checkout path; symlink it in
          ln -s "$GITHUB_WORKSPACE/apps/mrvtools" apps/mrvtools_src
          # The checkout contains both apps at its root; use a second layout
          # check to make sure bench sees both as independent apps.
          ls -la apps/

      - name: Point bench redis at the service containers
        working-directory: frappe-bench
        run: |
          # bench init with --skip-redis-config-generation leaves redis URLs
          # in common_site_config.json pointing at bench-managed ports.
          # Rewrite them to the service container (port 6379).
          python3 - <<'PY'
          import json, pathlib
          cfg_path = pathlib.Path("sites/common_site_config.json")
          cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
          cfg.update({
              "redis_cache": "redis://127.0.0.1:6379",
              "redis_queue": "redis://127.0.0.1:6379",
              "redis_socketio": "redis://127.0.0.1:6379",
          })
          cfg_path.write_text(json.dumps(cfg, indent=1))
          PY

      - name: Create site
        working-directory: frappe-bench
        run: |
          bench new-site test_site \
            --mariadb-root-password "$MARIADB_ROOT_PASSWORD" \
            --admin-password admin \
            --no-mariadb-socket \
            --db-host 127.0.0.1
        env:
          MARIADB_ROOT_PASSWORD: ${{ secrets.MARIADB_ROOT_PASSWORD }}

      - name: Install mrvtools
        working-directory: frappe-bench
        run: bench --site test_site install-app mrvtools

      - name: Install frappe_side_menu
        working-directory: frappe-bench
        run: bench --site test_site install-app frappe_side_menu

      - name: Migrate
        working-directory: frappe-bench
        run: bench --site test_site migrate

      - name: Run mrvtools tests
        working-directory: frappe-bench
        run: bench --site test_site run-tests --app mrvtools

      - name: Run frappe_side_menu tests
        working-directory: frappe-bench
        run: bench --site test_site run-tests --app frappe_side_menu

      - name: Upload bench logs on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: frappe-bench-logs
          path: frappe-bench/logs/
          retention-days: 7

      - name: Open issue on nightly failure
        if: failure() && github.event_name == 'schedule'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh issue create \
            --title "Nightly CI failure: $(date -u +%Y-%m-%d)" \
            --label "ci-nightly-failure" \
            --body "Nightly Frappe-tests run failed. See [workflow run](${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}). Logs artifact: \`frappe-bench-logs\`."
```

**Known rough edges in the above — flag and fix as you go, don't assume it works first try:**

1. **App-symlink layout.** The repo contains both `mrvtools/` and `frappe_side_menu/` at its root, but each needs to appear as an independent app directory inside `frappe-bench/apps/`. The symlink block above is a first cut; test it by running `bench --site test_site install-app ...` and seeing if bench discovers both apps. If it doesn't, the fix is probably two separate checkouts (one to `apps/mrvtools/`, another to `apps/frappe_side_menu/`) using `sparse-checkout`.
2. **MariaDB `innodb_read_only_compressed`.** The `mariadb:10.6` official image defaults may cause Frappe's `create database` to fail with a row-format error on some versions. The SQL pre-step works around this. If you see `Table compressed row format requires...`, that step is the fix.
3. **`bench new-site` may need `--db-password`.** If the root-password flag isn't enough (depends on bench version), add `--db-password "$MARIADB_ROOT_PASSWORD"` too.
4. **`nightly-failure` label:** The label doesn't need to pre-exist; `gh issue create --label` will fail if it doesn't. Either create the label manually in the repo once, or change to `--label "bug"` which always exists.

- [ ] **Step 3: Validate the workflow YAML**

Run:
```bash
actionlint .github/workflows/ci-frappe-tests.yml
```
Expected: no output, exit 0. If actionlint warns about `${{ secrets.MARIADB_ROOT_PASSWORD }}` interpolation inside the `options:` shell string, that warning is informational — secrets interpolation is supported there, but quote carefully.

- [ ] **Step 4: Commit (workflow not yet tested end-to-end)**

```bash
git add .github/workflows/ci-frappe-tests.yml
git commit -m "feat(ci): add Frappe doctype tests workflow

PRs to master and nightly cron run bench init + install-app +
migrate + run-tests for both mrvtools and frappe_side_menu. Opens
a GitHub issue on nightly failure."
```

- [ ] **Step 5: Create the `MARIADB_ROOT_PASSWORD` GitHub repository secret**

This step requires repo-admin access and is **manual** — cannot be done from the CLI during plan execution unless the runner has `gh` authed:

```bash
# With gh CLI authed as a repo admin:
gh secret set MARIADB_ROOT_PASSWORD -b "$(openssl rand -base64 24)"
```

Or via repo Settings → Secrets and variables → Actions → New repository secret. Name: `MARIADB_ROOT_PASSWORD`. Value: any strong password (CI picks it and uses it only inside the ephemeral MariaDB container).

- [ ] **Step 6: Create the `ci-nightly-failure` label (one-time)**

```bash
gh label create ci-nightly-failure \
  --description "Auto-opened by nightly CI on failure" \
  --color B60205
```

Expected: label is created. If `gh` isn't authed, do this via Issues → Labels in the GitHub UI.

- [ ] **Step 7: Push branch and open a draft PR to trigger the workflow end-to-end**

The Frappe-tests workflow only runs on PRs to `master` or the nightly cron, so verification happens in-PR:

```bash
git push -u origin HEAD
gh pr create --draft --title "ci: add GitHub Actions workflows" \
  --body "Implements docs/superpowers/specs/2026-04-19-ci-pipeline-design.md"
```

Watch the run:
```bash
gh run watch
```

- [ ] **Step 8: Iterate on workflow failures**

If the `ci-frappe-tests` job fails: download logs, identify the failing step, fix inline, amend the workflow, push. Common failures and fixes are documented in Step 2's "Known rough edges" section above.

Do not mark the task complete until both `ci-fast` and `ci-frappe-tests` have passed at least once on the PR branch.

---

## Task 5: Document CI and branch protection in `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md` — append a short section after "Build and run".

- [ ] **Step 1: Read the current CLAUDE.md to find insertion point**

Run:
```bash
grep -n '^## ' CLAUDE.md
```

Identify the line number of the `## Architecture notes worth knowing before editing` heading — insert a new `## Continuous integration` section *before* it.

- [ ] **Step 2: Add the CI section**

Insert this block before the "Architecture notes" heading:

```markdown
## Continuous integration

CI runs via GitHub Actions. Two workflows:

- [.github/workflows/ci-fast.yml](.github/workflows/ci-fast.yml) — runs on every push and PR. Three parallel jobs: `frontend-build` (Vite build), `frontend-format` (Prettier `--check`), `python-lint` (ruff on both apps). Target <2 min.
- [.github/workflows/ci-frappe-tests.yml](.github/workflows/ci-frappe-tests.yml) — runs on PRs targeting `master` and nightly at 02:00 UTC. Spins up MariaDB 10.6 + Redis 7 service containers, runs `bench init`, installs both apps into a fresh `test_site`, then `bench run-tests --app mrvtools` and `--app frappe_side_menu`. Nightly failures auto-open a GitHub issue labelled `ci-nightly-failure`.

Design spec: [docs/superpowers/specs/2026-04-19-ci-pipeline-design.md](docs/superpowers/specs/2026-04-19-ci-pipeline-design.md).

Version pins live in both workflow files and in [install.sh](install.sh) — keep them in sync. Bumping Python, Node, or the Frappe branch in install.sh requires a matching edit to `ci-frappe-tests.yml` in the same PR.

Branch protection on `master` requires these status checks (configure manually via repo Settings → Branches): `frontend-build`, `frontend-format`, `python-lint`, `frappe-tests`.
```

- [ ] **Step 3: Verify the section renders sensibly**

Run:
```bash
grep -A 2 '^## Continuous integration' CLAUDE.md
```
Expected: the heading and first line of the new section print.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(claude-md): document CI workflows and branch protection"
```

---

## Task 6: Post-merge: configure branch protection (manual, coordinated with repo admin)

**This task runs AFTER the PR from Task 4 is merged to `master`** — required status checks can't be added until they've run at least once on the default branch.

- [ ] **Step 1: Confirm the four status checks have run on master**

Visit repo → Actions tab → verify `frontend-build`, `frontend-format`, `python-lint`, and `frappe-tests` have each completed at least one run on the `master` branch.

- [ ] **Step 2: Configure branch protection via CLI or UI**

CLI (requires admin token):
```bash
gh api --method PUT repos/:owner/:repo/branches/master/protection \
  -f required_status_checks[strict]=true \
  -f 'required_status_checks[contexts][]=frontend-build' \
  -f 'required_status_checks[contexts][]=frontend-format' \
  -f 'required_status_checks[contexts][]=python-lint' \
  -f 'required_status_checks[contexts][]=frappe-tests' \
  -f enforce_admins=false \
  -f required_pull_request_reviews=null \
  -f restrictions=null
```

Or via UI: Settings → Branches → Add branch protection rule → Branch name pattern `master` → tick "Require status checks to pass before merging" → add the four check names.

- [ ] **Step 3: Verify by opening a trivial PR and confirming merge is blocked until checks pass**

No commit for this task — it's repo configuration, not code.

---

## Self-review checklist (run before handing off)

- [ ] **Spec coverage:** every section in [2026-04-19-ci-pipeline-design.md](../specs/2026-04-19-ci-pipeline-design.md) maps to a task above:
  - Workflow layout → Tasks 3 and 4
  - `ci-fast.yml` jobs → Task 3
  - `ci-frappe-tests.yml` (triggers, services, steps, secrets) → Task 4
  - Caching → embedded in Tasks 3 and 4
  - Failure handling (artifact upload, issue on nightly failure) → Task 4 Steps 2 + 6
  - Branch protection → Task 6
  - Files changed — ruff.toml (Task 1), prettier reformat (Task 2), two workflow files (Tasks 3+4), CLAUDE.md (Task 5) — all accounted for
- [ ] **No placeholders** — all code blocks contain real content, all commands are runnable as written.
- [ ] **Type/name consistency** — job names `frontend-build`, `frontend-format`, `python-lint`, `frappe-tests` are identical in workflows, in CLAUDE.md prose, and in the branch-protection step.
- [ ] **Secrets and labels** — `MARIADB_ROOT_PASSWORD` is the single secret name used everywhere; `ci-nightly-failure` is the single label name used everywhere.
