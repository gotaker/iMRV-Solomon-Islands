# iMRV — Consolidated UX Audit Report (with Architect Review)

**Auditor:** Independent UX consultant, design-agency perspective
**Architect review:** internal (sequencing, dependencies, scope, bench-assertion quality)
**Date:** 2026-04-30
**Target:** `https://demo.imrv.netzerolabs.io` (live Railway demo)
**Authentication:** Administrator/catch22 + 3 audit-only test users (disabled at end)
**Viewports:** desktop 1470×900, mobile 390×844
**Method:** Browser walkthrough (Playwright MCP) + parallel curl probe of 33 surfaces + design-token reference extracted from source + role walkthrough as Observer

---

## Headline

The Forest-and-Sage editorial system **lands cleanly** on the live demo for visual identity, typography (Anton + Inter), drawer composition, list/badge styling, and SPA editorial composition. All 33 probed surfaces returned 2xx. **However**, the deeper data + role audit surfaced 6 additional findings that didn't show in the visual pass — the most serious being a **drawer-permission leak** (Observer with zero roles still sees `USERS` parent → 403 on click), **chart tooltips rendering "undefined"**, **truncated chart axis labels and legends**, and **role assignment via the JSON API silently dropping roles** that aren't in `tabHas Role` for this site's role registry.

Total findings: **17** (1 critical, 5 high, 5 medium, 5 low, 1 informational). Findings prefixed `F` are from the visual pass; `R` are from the role/data deep dive; `D` are drawer-specific.

---

## What's working — design philosophy adherence

| Area | Verified on live |
|---|---|
| Editorial palette tokens | `--ed-forest #01472e`, `--ed-cream #fefae0`, `--ed-sage #ccd5ae`, `--ed-olive #e9edc9`, `--ed-moss #a3b18a`, plus opacity variants — all present, used consistently |
| Anton (display) | Loaded; dashboard h1 ("GOOD EVENING, ADMINISTRATOR"), list page-titles ("MITIGATIONS", "MITIGATION REPORT"), SPA masthead "IMRV", section headlines ("PROGRAMS", "WE MEASURE WHAT WE MEAN TO PROTECT") |
| Inter (body) | 400/500/700 loaded; body copy, buttons, sub-menu items, breadcrumbs |
| Frosted-glass drawer | Translucent surface + 20 px backdrop-blur + cream sticky header band with SI flag |
| Lucide-style rail icons | Top-level drawer items use mask-image SVG; consistent stroke weight |
| Contextual flyout submenu | Pops at clicked-row level with cream header, group-head sub-titles, scroll-anchored on overflow |
| Status badges in lists | Sage/forest tints (Approved green, Draft muted) — readable, on-brand |
| Pill CTAs | Forest fill, cream text, uppercase Inter |
| SPA editorial composition | Torn-edge photo cards, oversized Anton, "FIELD DISPATCH / SLOW NEWS" footer, real partner logos (UNDP, Australian Aid, GGGI) |
| Mobile responsive (390 px) | Clean stack; no horizontal scroll |
| HTTP surface | All 33 URLs 2xx; correct cache directives |

---

## Findings (priority-ranked)

### R1 — Drawer permission leak: Observer sees `USERS` parent, click → 403  `[Critical]`

**Where:** floating drawer, every authenticated session for users without explicit USERS-domain perms.
**What I saw:** logged in as `audit_observer_test@imrv.local` (effectively zero roles after API role-assignment failure described in R3). Drawer rendered 5 items: HOME, PROJECT, REPORTS (with submenu), **USERS (with submenu)**, DOCUMENT RESOURCE TOOL. Expanding USERS revealed leaf "Approved Users" → `/app/approved-user`. `GET /api/method/frappe.client.get_count?doctype=Approved User` returned **HTTP 403** with `User <strong>audit_observer_test@imrv.local</strong> does not have doctype access permissions`.
**Memory match:** exact pattern documented in `reference_drawer_perm_filter.md`: *"the drawer shows top-level entries (USERS) whose target page then 403s on click — the substring SQL match was the root cause"*. The fix described there (narrow with `frappe.has_permission(d, "read", user=user)` + use Python sets, not substring on the SQL string) is either not deployed to live, has a gap, or regressed.
**Action:**
1. Inspect `frappe_side_menu/frappe_side_menu/api.py:get_menulist()` deployed to live vs repo. If they differ, the live deploy is stale.
2. If they match, the fix has a gap — most likely scenario: a parent's `has_sub_menu=1` row gets included if any leaf passes `permitted_docs_set`, but for this user `Approved User` IS in the user's DocPerm rows even though `frappe.has_permission` returns False. Check whether `permitted_docs_set` is filtered with `has_permission` at the leaf level too, or only at the top level.
3. Add bench scenario: log in as a zero-role user, open drawer, assert exactly the "everyone-allowed" subset is visible (Home, the always-public direct links).

### F1 — SPA reveal-stuck-on-load `[High]`

**Where:** `/frontend/home` (and likely every SPA route using `useReveal()`).
**What I saw:** 11 of 14 `[data-reveal]` elements stuck at `opacity:0` on initial render. Self-heals on scroll.
**Architect note:** The `prime()` walk *exists* in `frontend/src/composables/useReveal.js`. This is most likely a **deploy/cache issue, not a code regression**. Verify: hash the deployed `index-*.js` and `grep -c "is-revealed" $(curl -sL https://demo.imrv.netzerolabs.io/frontend/home | grep -o 'index-[a-z0-9]*\.js' | head -1)` against a local `yarn build`. If hashes differ, redeploy and re-test before opening any code PR.
**Action:** Verify deploy first. Open code change only if local + deployed bundles agree.

### R2 — GHG report chart tooltips render `undefined`  `[High]`

**Where:** `/desk/mitigation-report` (and likely all 8 reports under the REPORTS submenu — 4 instances detected on this single page).
**What I saw:** all 4 occurrences of literal `\bundefined\b` are inside `<span class="tooltip-content">` — chart hover tooltips. So when a user hovers a data point on the bar/pie charts, the tooltip shows "undefined" instead of the data label/value.
**Action:** Trace the chart-config tooltip formatter in `mrvtools/mrvtools/page/{mitigation_report,adaptation_report,...}/`. Most likely a chart-series field reference is `undefined` because the data row's expected key is missing or renamed.
**Architect note:** the proposed bench assertion (no literal `undefined` in body text) needs **`\bundefined\b`** word boundary or it'll false-positive on legitimate strings; also exclude `<input placeholder>` and `aria-*` attribute values from the scan.

### R3 — Mitigation Report bar chart: title-data mismatch + Y-axis label clipping `[High]`

**Where:** `/desk/mitigation-report` → "No of Projects based on Categories" bar chart.
**What I saw:**
1. Title says "**No of Projects** based on Categories" but Y-axis goes 0 → 400,000+ (project counts can't be 100,000s).
2. Y-axis tick labels are clipped on the **left edge** — visible labels read `00000`, `100000`, `200000` (truncated to `00000`, `00000`, `00000` because the leading digit is cut off by container clipping).
3. Single bar floating in the chart with no x-axis category label (just `Till Date` axis label).
4. Legend reads "Expected Annual..." (truncated) and "Actual Annual GHG".
**Diagnosis:** the chart appears to be plotting GHG-emission values but is labelled as a project-count chart — either the wrong series is bound, or the title is wrong.
**Action:** Reconcile chart title with bound series. Add left padding to chart container to prevent Y-axis label clip. Truncate legend labels with ellipsis and provide full text on hover (or widen legend container).

### R4 — Pie chart legends truncated, single-segment pies render as solid disks `[High]`

**Where:** `/desk/mitigation-report` and `/desk/ghg-inventory-report`.
**What I saw:**
1. Pie chart "GHG emissions reductions actual sector wise" — single solid pink circle = 100% one sector ("346980"), no labels, looks like "no data".
2. Legend labels truncated with no tooltip: "Energy Utilisat...", "Energy Generati...", "Others - Cross-...", "Indigenous Peop..."
3. Same on `/desk/ghg-inventory-report` — Energy 100%, all other sectors 0%, indistinguishable from broken.
**Action:** swap to a stacked-bar / centerstone callout when one segment ≥ 95 %; full legend text on hover; widen legend container or wrap legend onto multiple lines.
**Architect note:** the original bench assertion shape (`pie_segment_legibility` keyed on `≥ 95%`) is **flaky** because real-world data legitimately has dominant segments. Better assertion: pie chart must always emit `<text>` data labels regardless of segment ratio.

### R5 — Report data-table column headers + cell values truncated; data quality issues  `[High]`

**Where:** every Tracking Report's data table.
**What I saw:** Frappe DataTable renders 20 columns (Action, Programme, Project ID, Project Name, Objective, Key Sector, Key Sub-Sector, Cost (USD), Location, Start Date, Lifetime, Included In, Implementing Entity, Other Agency, Status, Expected Annual GHG, Actual Annual GHG, Till Date Expected GHG, Till Date Actual GHG, plus row-#) — all visible, some truncated mid-word ("Acti...", "Program...", "Lifeti...", "Locati..."). Real data also flagged inconsistencies — e.g. `Cost (USD): 2.6` for SPIRES PROJECT (clearly an entry error vs. another row showing `240,480,000`).
**Action:** Allow horizontal scroll for the data table or shrink the most-truncated cols; flag obviously-malformed Cost values via doctype-level validation (e.g. < $1,000 likely an entry error for a project of this scale).

### R6 — Role assignment via `frappe.client.insert` silently drops roles  `[High]`

**Where:** API path used by automation / fixtures.
**What I saw:** `POST /api/method/frappe.client.insert` with a `User` doc containing `roles: [{role: "Observer GHG Inventory Report"}, {role: "Observer Mitigation Report"}]` returned 200, but `frappe.client.get` of the new user shows `roles: []`. The roles aren't being persisted on insert.
**Hypothesis:** the role names exist in `tabRole` but Frappe's User-doc validator filters them out on insert because they're missing `desk_access=1` or aren't in some allowlist, AND the validator does so silently.
**Action:** Reproduce on local-docker, trace `User.before_save` / `User.validate_user_roles`. Either fix the silent drop or surface a validation error. Important for CI/scripted seed flows.

### F2 — Default chart tooltip "undefined" — *folded into R2*

### R7 — Pages show "Good evening, Administrator" as H1 after SPA navigation  `[Medium]`

**Where:** observed on hard-navigation to several `/desk/*-report` pages.
**What I saw:** my `h1, .page-title .title-text` selector returned "Good evening, Administrator" on `/desk/mitigation-report`, `/desk/adaptation-report`, `/desk/sdg-report`, etc.
**Likely cause:** these custom report pages have no `<h1>` of their own, so my heading-detection landed on a leftover `<h1>` from main-dashboard mount that wasn't unmounted on SPA route change. Frappe v16 desk SPA-navigation issue — the dashboard widget DOM persists in the document.
**Action:** Verify with a hard reload that no leftover `<h1>` exists on report pages. If it does, fix the dashboard page's teardown. If it doesn't, the report pages need their own `<h1>` for accessibility (current `.page-title` is a `DIV.page-title` in Inter 14px — not a real heading).
**Architect note:** this overlaps with the "list rows accumulating" suspicion — `listRowCount` rose from 20 → 284 across 33 SPA route changes in my probe. Strong indicator of DOM leakage between routes.

### F3 — Sector pie chart degenerates when one sector is 100% — *folded into R4*

### F4 — GHG gas-wise bar chart has no value labels — *folded into R3*

### F5 — Drawer flyouts use Font-Awesome icons (inconsistent with Lucide rail) `[Medium]`

**Where:** every parent submenu's leaf items.
**What I saw:** 27 `i.fa.fa-bar-chart` instances inside the drawer's flyouts. The rail uses Lucide-style mask SVGs; the flyout falls through to FA glyphs. Visible inconsistency.
**Architect note:** split into:
- **F5a** (rendering fallback): map FA classes to Lucide-style mask SVGs in `frappe_side_menu.css` — same pattern as the rail. **Land before role audit closes.**
- **F5b** (seed JSON authoring): assign per-item `sub_menu_icon` / `sub_menu_image_icon` in `Sub Menu` seed JSON. **Land after a 1-week soak of `e3c1b2e`** (the contextual-flyout commit) to avoid touching the same seed surface twice.

### F6 — `+ ADD MITIGATIONS` button copy reads grammatically odd `[Low]`

Same as before. Architect flagged the proposed "force singular doctype" bench assertion as flaky (some doctypes legitimately plural — "Settings", "Permissions") — needs an allowlist.

### F7 — Login layout has tight vertical rhythm `[Low]`

Same as before.

### F8 — Recent Activity heading is very small (11 px / 3.3 px tracked) `[Low]`

Same as before.

### D1 — Drawer flag-band shading vertically asymmetric (flag pinned to bottom-left of an oversized cream block)  `[Low — FIXED]`

**Where:** drawer header `<li class="app-logo">` band.
**What I saw:** band 320×137 px, flag 72×36 px sitting at x=26, y=120 — 80 px of empty cream above the flag, 21 px below. The cream rectangle's vertical centre (y=109) sat 29 px above the flag's centre (y=138). Visually read as a lopsided header.
**Root cause:** padding `80px 4.5rem 20px 1.5rem` was tuned to clear the floating burger button, but ~68 px of that top padding was unnecessary — the cream band sits below the close button (y=40+) and the burger only overlaps the band by 12 px vertically.
**Fix shipped:** padding tightened to `24px 4.5rem 24px 1.5rem` and the LI made `display:flex; align-items:center;` so the flag is vertically centred regardless of band height. Result: band height 137 → 85 px, top/bottom gaps both 24 px, flag now visually centred. Synced into local container; needs Railway redeploy for live.

### D2 — Flag link routes to `/desk/frontend/home` (404-ish) instead of `/frontend/home`  `[Critical — FIXED]`

**Where:** drawer header flag click.
**What I saw:** clicking the SI flag in the drawer landed on `https://demo.imrv.netzerolabs.io/desk/frontend/home` — broken route, shows desk dashboard layout but not the public SPA homepage.
**Root cause:** `frappe_side_menu.js`'s drawer click delegate intercepts every anchor with a non-`#` href and routes it through `frappe.set_route(href)`. `frappe.set_route` is desk-only — calling it with `/frontend/home` re-prefixes with `/desk/` and strands users at the broken `/desk/frontend/home`. The delegate didn't have an exclusion for non-desk routes.
**Fix shipped:** added an early-return in the delegate for href matching `^(https?:|mailto:|tel:|/(frontend|files|api|method|website|private)/)` — those navigate natively. Verified: clicking the flag now lands on `http://localhost:8080/frontend/home` correctly. Needs Railway redeploy for live.

### F9 — Console errors on every desk page  `[Medium]` *(re-classified per architect review)*

**Architect rationale:** "≥ 1 console error per desk page" smells like a missing `frappe.boot.user.can_read.includes(...)` guard somewhere (the same pattern that was fixed for `main_dashboard.js`). Per memory, that pattern blocks 403s for users without read perm. If another doctype is missing the guard, the error count = number of doctypes calling unguarded queries. Treat as **permission-leakage scent, not noise**.
**Action:** grep the actual error string, decide whether it's the deferred CSRF retry interceptor (intentionally not fixed per `reference_csrf_retry_interceptor.md`) or a new guard gap.

---

## Suggested execution order (revised per architect)

1. **Verify deploy hash for F1** — bundle on live vs `yarn build`. May resolve F1 with no code change.
2. **Fix R1 drawer-permission leak** — the actual security/UX risk in this audit.
3. **R2 + R3 + R4 (chart fixes)** — single sweep on the report pages: tooltip formatter, axis padding, legend overflow, pie-chart degenerate handling.
4. **F9 grep** — figure out whether console errors are the deferred CSRF or a new gap; reclassify accordingly.
5. **Run adversarial Wave 2 on local-docker** — `./bench/bench.sh --target=local-docker --include-adversarial`.
6. **R5 (data-table truncation + validation)** — UI-side and data-side together.
7. **R6 (silent role-drop on insert)** — reproduce on local-docker first; touches Frappe core behaviour.
8. **R7 (heading hierarchy on report pages)** — accessibility + DOM-leak together.
9. **F5a (FA → Lucide in flyouts)** — visible polish, low risk.
10. **F6 / F7 / F8** — copy + spacing sweep, single PR.
11. **F5b (seed JSON icons)** — after 1-week soak of `e3c1b2e`.

---

## Bench scenarios to add (revised per architect)

| # | Assertion | Stability notes |
|---|---|---|
| R1 | `drawer_perm_no_leak_zero_role_user` — log in as a fixture-created zero-role user; drawer must render only the public/All-Role subset. | Stable — uses fixed fixture user, deterministic role inventory. |
| R2 | `no_undefined_in_visible_text` — every desk + SPA route's body text must not match `\bundefined\b`. **Exclusions:** `<input placeholder>`, `aria-*` attributes, scripts. | Tightened per architect — word boundary + exclusion list. |
| R3 | `chart_axis_label_not_clipped` — for every visible chart, every axis tick text must have its full bounding box inside the chart's clip-rect. | Stable. |
| R4 | `chart_text_labels_emitted` — every chart must emit at least one `<text>` element representing data labels (regardless of segment ratio). | Tightened per architect — drops the "≥95%" gate. |
| R5 | `report_table_columns_not_mid_word_truncated` — column header full text reachable via title attr or full content fits, OR scroll is offered. | Stable. |
| R6 | `user_role_assignment_persists_on_insert` — `frappe.client.insert` of a User doc with N roles must result in N entries in `tabHas Role` for that user (or surface validation error). | Stable. |
| F1 | `data_reveal_health` — `[data-reveal]` with `opacity < 0.99` (per architect — CSS transition rounding) and `getBoundingClientRect` clipped to viewport. | Tightened threshold. |
| F5a | `drawer_flyout_no_fa_icon` — count of `.fsm-flyout-anchored i.fa-` elements; assert 0 (or document the design choice). | Stable. |

---

## Permanence checklist

- [x] Test users created on live demo (3 succeeded, 1 failed on missing role) — **all 3 disabled (not deleted) at audit end**, audit trail preserved.
- [x] Architect-reviewed audit landed at `/docs/audits/2026-04-30-ux-audit-live-demo-CONSOLIDATED.md` (this file).
- [x] R1 drawer-leak fixed in code + DB (commit 8da8a49) + bench scenario `drawer_perm_no_leak_zero_role_user.yaml`.
- [x] R2/R3 chart fixes shipped + bench scenarios `tracking_reports_chart_health.yaml`, `pie_chart_data_labels_emitted.yaml`.
- [x] F5a / F7 / F8 / D1 / D2 fixes shipped + bench scenarios.
- [x] R4 / R5 / R6 / R7 / F1 / F6 / F9 covered as bench scenarios (will fail until corresponding code fix lands).
- [x] Existing `intersection_observer_threshold.yaml` tightened to `opacity < 0.99` per architect review.
- [ ] F1 deploy verification before any composable change.

## Carry-overs to next audit

- Role-specific UX testing was effectively a **zero-role-user audit** because the API role-assignment silently dropped the assigned roles (R6). To truly audit Approver / Observer / MRV Admin perspectives, fix R6 first — or assign roles via the Frappe desk UI (which uses a different code path that doesn't silent-drop).
- Adversarial Wave 2 on local-docker — not yet run.
- Print/export of GHG report (PDF download via top-right `DOWNLOAD` button) — not exercised.
- Empty-state coverage on list views with zero records — not exercised.
- Lighthouse / axe accessibility — not run.

---

*End of consolidated audit*
