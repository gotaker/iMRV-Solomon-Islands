# Install Manual Deltas — Plan Addendum

> Addendum to [2026-04-19-unified-setup-script.md](2026-04-19-unified-setup-script.md). Applies after the base 12-task plan has landed (branch `feat/unified-install`, HEAD at fix commit `ff2ec10`).

**Goal:** bring `install.sh` into alignment with the load-bearing steps in `Insatllation Manual-SI-iMRV Tool-V1.pdf` that the initial plan missed.

**Repo-owner decisions (locked):**

- PDF export is a **critical** requirement → install the patched-Qt `wkhtmltopdf` on Ubuntu, not the distro package.
- Keep `MRVTOOLS_SRC` / `SIDE_MENU_SRC` defaulting to the local repo path for now. No new URL-override env vars.
- DNS multitenant is **always on** in prod.
- `github.com/rajeshscs/MRV-Solomon-Islands` is the canonical origin of record after this branch lands.
- Production domain is `demo.imrv.netzerolabs.com` — hardcoded as the default value of `PROD_DOMAIN`, overridable via env var.
- TLS path uses `bench setup lets-encrypt` (Frappe-blessed one-liner), not the manual's raw snap+certbot flow. Remains opt-in (`PROD_ENABLE_TLS=1`).

**What's deliberately out of scope:** `MRVTOOLS_SOURCE` / `FRAPPE_SIDE_MENU_SOURCE` URL overrides; updating the manual PDF itself; wkhtmltopdf on macOS (brew ships the patched build).

---

## Task 13: Add `git` + `cron` to system deps

**Files:** `install.sh` — extend both OS branches in `install_system_deps`.

- [ ] **Step 1: Extend macOS brew package list**

In [install.sh](../../../install.sh), find:

```bash
  local pkgs=(python@3.11 node@18 yarn mariadb redis wkhtmltopdf pipx)
```

Replace with:

```bash
  local pkgs=(git python@3.11 node@18 yarn mariadb redis wkhtmltopdf pipx)
```

- [ ] **Step 2: Extend Ubuntu apt package list**

Find:

```bash
  local pkgs=(python3.11 python3.11-venv python3-dev mariadb-server redis-server
              wkhtmltopdf build-essential libssl-dev libffi-dev xvfb libfontconfig pipx)
```

Replace with:

```bash
  local pkgs=(git cron python3.11 python3.11-venv python3-dev mariadb-server redis-server
              build-essential libssl-dev libffi-dev xvfb libfontconfig pipx)
```

(Note: `wkhtmltopdf` is removed from the apt list because Task 14 installs a patched build from the wkhtmltopdf GitHub release instead.)

- [ ] **Step 3: Verify**

```bash
bash -n install.sh && shellcheck install.sh
```

Expected: both clean.

- [ ] **Step 4: Commit**

```bash
git add install.sh
git commit -m "feat(install.sh): add git and cron to system deps"
```

---

## Task 14: Install patched `wkhtmltopdf` on Ubuntu/WSL

**Files:** `install.sh` — add a helper invoked at the end of the Ubuntu branch of `install_system_deps`.

**Rationale:** stock Ubuntu `wkhtmltopdf` is built against unpatched Qt and fails on Frappe's PDF templates. The patched `.deb` at `github.com/wkhtmltopdf/packaging` fixes this. macOS `brew install wkhtmltopdf` already ships the patched build, so no change there.

- [ ] **Step 1: Add helper function**

In `install.sh`, immediately **after** the `_ensure_mariadb_root_password` function (end of file's system-deps block), add:

```bash
_install_wkhtmltopdf_patched() {
  # Only Ubuntu/WSL. macOS brew already ships the patched Qt build.
  if [[ "$OS" != "ubuntu" ]]; then
    return
  fi
  if command -v wkhtmltopdf &>/dev/null && \
     wkhtmltopdf --version 2>&1 | grep -qi 'with patched qt'; then
    skip "wkhtmltopdf (patched Qt build already installed)"
    return
  fi
  local codename arch version='0.12.6.1-2'
  # shellcheck disable=SC1091
  codename="$(. /etc/os-release && echo "$VERSION_CODENAME")"
  arch="$(dpkg --print-architecture)"
  if [[ -z "$codename" || -z "$arch" ]]; then
    err "could not determine Ubuntu codename or architecture for wkhtmltopdf download"
    exit 1
  fi
  local deb_name="wkhtmltox_${version}.${codename}_${arch}.deb"
  local url="https://github.com/wkhtmltopdf/packaging/releases/download/${version}/${deb_name}"
  local tmp="/tmp/${deb_name}"
  info "downloading patched wkhtmltopdf: $url"
  run_sh "curl -fsSL -o '$tmp' '$url'"
  # Stock wkhtmltopdf (if present) conflicts with wkhtmltox; remove it quietly.
  if dpkg -s wkhtmltopdf &>/dev/null; then
    run sudo apt-get remove -y wkhtmltopdf
  fi
  run_sh "sudo dpkg -i '$tmp' || sudo apt-get install -f -y"
  run rm -f "$tmp"
}
```

- [ ] **Step 2: Call the helper from the Ubuntu branch**

Find the end of `_install_system_deps_ubuntu()` — specifically the last line before the closing `}`:

```bash
  if [[ "$IS_WSL" == "1" ]]; then
    run sudo service mariadb start
    run sudo service redis-server start
  else
    run sudo systemctl start mariadb
    run sudo systemctl start redis-server
  fi
}
```

Insert a call to the new helper immediately after the `fi` closing the WSL/systemctl branch, before the closing brace:

```bash
  if [[ "$IS_WSL" == "1" ]]; then
    run sudo service mariadb start
    run sudo service redis-server start
  else
    run sudo systemctl start mariadb
    run sudo systemctl start redis-server
  fi
  _install_wkhtmltopdf_patched
}
```

- [ ] **Step 3: Verify static checks**

```bash
bash -n install.sh && shellcheck install.sh
```

Expected: both clean.

- [ ] **Step 4: Verify DRY_RUN on macOS is a no-op for this helper**

```bash
DRY_RUN=1 MYSQL_ROOT_PASSWORD=test ./install.sh --dev 2>&1 | grep -c 'wkhtmltox'
```

Expected (on macOS): `0` (helper returns early because `$OS != ubuntu`).

- [ ] **Step 5: Commit**

```bash
git add install.sh
git commit -m "feat(install.sh): install patched wkhtmltopdf on Ubuntu for PDF export"
```

---

## Task 15: Always-on `dns_multitenant` + optional `PROD_DOMAIN` add-domain + optional TLS

**Files:** `install.sh` — extend config block, usage, and `configure_prod`.

- [ ] **Step 1: Add two new env vars to the config block**

In `install.sh`, find:

```bash
PROD_USER="${PROD_USER:-${USER:-root}}"
DRY_RUN="${DRY_RUN:-0}"
```

Replace with:

```bash
PROD_USER="${PROD_USER:-${USER:-root}}"
PROD_DOMAIN="${PROD_DOMAIN:-demo.imrv.netzerolabs.com}"
PROD_ENABLE_TLS="${PROD_ENABLE_TLS:-0}"
DRY_RUN="${DRY_RUN:-0}"
```

- [ ] **Step 2: Document the new env vars in the usage block**

Find the line (inside `usage()`'s heredoc):

```text
  PROD_USER               ($USER)               User for bench setup production
```

Insert two new lines immediately after it:

```text
  PROD_USER               ($USER)                       User for bench setup production
  PROD_DOMAIN             (demo.imrv.netzerolabs.com)    In --prod, the FQDN attached via bench setup add-domain
  PROD_ENABLE_TLS         (0)                            If 1 in --prod, run bench setup lets-encrypt (Ubuntu only)
```

- [ ] **Step 3: Replace `configure_prod`**

Find (exact):

```bash
configure_prod() {
  step "configure_prod"
  run sudo bench setup production "$PROD_USER"
  (
    [[ "$DRY_RUN" == "1" ]] || cd "$BENCH_DIR"
    run bench --site "$SITE_NAME" set-config developer_mode 0
    run bench --site "$SITE_NAME" set-config ignore_csrf 0
  )
}
```

Replace with:

```bash
configure_prod() {
  step "configure_prod"
  (
    [[ "$DRY_RUN" == "1" ]] || cd "$BENCH_DIR"
    run bench config dns_multitenant on
  )
  run sudo bench setup production "$PROD_USER"
  (
    [[ "$DRY_RUN" == "1" ]] || cd "$BENCH_DIR"
    run bench --site "$SITE_NAME" set-config developer_mode 0
    run bench --site "$SITE_NAME" set-config ignore_csrf 0
  )
  if [[ -n "$PROD_DOMAIN" ]]; then
    info "attaching domain $PROD_DOMAIN to $SITE_NAME"
    (
      [[ "$DRY_RUN" == "1" ]] || cd "$BENCH_DIR"
      run bench setup add-domain "$PROD_DOMAIN" --site "$SITE_NAME"
    )
  fi
  if [[ "$PROD_ENABLE_TLS" == "1" ]]; then
    if [[ -z "$PROD_DOMAIN" ]]; then
      err "PROD_ENABLE_TLS=1 requires PROD_DOMAIN to be set"
      exit 1
    fi
    if [[ "$OS" != "ubuntu" ]]; then
      warn "TLS setup skipped: Let's Encrypt path is Ubuntu-only (current OS: $OS)"
    else
      info "provisioning Let's Encrypt certificate for $PROD_DOMAIN"
      (
        [[ "$DRY_RUN" == "1" ]] || cd "$BENCH_DIR"
        run sudo -H bench setup lets-encrypt "$SITE_NAME" --custom-domain "$PROD_DOMAIN"
      )
    fi
  fi
}
```

- [ ] **Step 4: Verify static checks**

```bash
bash -n install.sh && shellcheck install.sh
```

Expected: both clean.

- [ ] **Step 5: DRY_RUN verify — default prod (domain defaults to demo.imrv.netzerolabs.com, TLS off)**

```bash
DRY_RUN=1 MYSQL_ROOT_PASSWORD=test PROD_USER=ubuntu ./install.sh --prod 2>&1 \
  | sed -n '/==> configure_prod/,/install.sh finished/p'
```

Expected output includes `DRY_RUN: bench config dns_multitenant on` before `DRY_RUN: sudo bench setup production ubuntu`, then `DRY_RUN: bench setup add-domain demo.imrv.netzerolabs.com --site mrv.localhost`, and NO `lets-encrypt` line (PROD_ENABLE_TLS defaults to 0).

- [ ] **Step 6: DRY_RUN verify — prod with domain + TLS**

```bash
DRY_RUN=1 MYSQL_ROOT_PASSWORD=test PROD_USER=ubuntu \
  PROD_DOMAIN=mrv.gov.sb PROD_ENABLE_TLS=1 \
  ./install.sh --prod 2>&1 | sed -n '/==> configure_prod/,/install.sh finished/p'
```

Expected on macOS (the current host): all of `dns_multitenant`, `setup production`, `set-config`, `add-domain`, and a `WARN: TLS setup skipped: Let's Encrypt path is Ubuntu-only (current OS: macos)` line.

On Ubuntu: the final block includes `DRY_RUN: sudo -H bench setup lets-encrypt mrv.localhost --custom-domain mrv.gov.sb`.

- [ ] **Step 7: DRY_RUN verify — explicit empty PROD_DOMAIN + TLS errors out**

```bash
DRY_RUN=1 MYSQL_ROOT_PASSWORD=test PROD_DOMAIN= PROD_ENABLE_TLS=1 ./install.sh --prod; echo exit=$?
```

Expected: prints `ERR:  PROD_ENABLE_TLS=1 requires PROD_DOMAIN to be set`, then `exit=1`. (Passing an empty string explicitly overrides the `demo.imrv.netzerolabs.com` default.)

- [ ] **Step 8: Commit**

```bash
git add install.sh
git commit -m "feat(install.sh): dns_multitenant + optional PROD_DOMAIN and Let's Encrypt"
```

---

## Task 16: Update `CLAUDE.md` pointer to mention new prod env vars

**Files:** `CLAUDE.md` — extend the install.sh paragraph added in Task 12.

- [ ] **Step 1: Find the sentence listing env vars**

In [CLAUDE.md](../../../CLAUDE.md), find:

```markdown
Env vars (`BENCH_DIR`, `SITE_NAME`, `FRAPPE_BRANCH`, etc.) override defaults; `DRY_RUN=1` prints what would run without executing it.
```

Replace with:

```markdown
Env vars (`BENCH_DIR`, `SITE_NAME`, `FRAPPE_BRANCH`, `PROD_DOMAIN`, `PROD_ENABLE_TLS`, etc.) override defaults; `DRY_RUN=1` prints what would run without executing it. Prod-only: set `PROD_DOMAIN=<fqdn>` to run `bench setup add-domain`, and `PROD_ENABLE_TLS=1` (Ubuntu only) to provision a Let's Encrypt cert via `bench setup lets-encrypt`.
```

- [ ] **Step 2: Verify**

```bash
grep -c PROD_DOMAIN CLAUDE.md
```

Expected: `1` (or higher — one new reference).

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: document PROD_DOMAIN and PROD_ENABLE_TLS in CLAUDE.md"
```

---

## Final verification (after all four tasks)

```bash
bash -n install.sh
shellcheck install.sh
DRY_RUN=1 MYSQL_ROOT_PASSWORD=test ./install.sh --dev 2>&1 | grep -c '^==>'
DRY_RUN=1 MYSQL_ROOT_PASSWORD=test PROD_USER=ubuntu ./install.sh --prod 2>&1 | grep -c '^==>'
```

Expected: shellcheck and bash -n clean; dev=9, prod=8 (unchanged — new logic is inside existing phases, not new phases).

```bash
git log --oneline ff2ec10..HEAD
```

Expected: four commits, one per task, in order.
