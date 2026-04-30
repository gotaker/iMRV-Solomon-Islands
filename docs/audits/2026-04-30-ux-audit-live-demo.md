# iMRV — External UX Audit Report

**Auditor:** Independent UX consultant, design-agency perspective
**Date:** 2026-04-30
**Target:** `https://demo.imrv.netzerolabs.io` (live Railway demo)
**Authentication:** Administrator / catch22
**Viewports:** desktop 1470×900, mobile 390×844
**Method:** Browser walkthrough (Playwright MCP) + parallel HTTP probe of 33 surfaces (curl) + design-token reference extracted from source

---

## 1. Headline

The Forest-and-Sage editorial system **lands cleanly** on the live demo: tokens, fonts (Anton + Inter, both loaded), drawer (frosted-glass, Lucide-style rail icons, contextual flyout), pill CTAs, status badges, list views, and the SPA's torn-paper photographic composition all render as intended at desktop and mobile widths. All 33 probed URLs returned 2xx with correct cache headers (`no-cache, must-revalidate` on `/assets/`, `max-age=3600` on `/files/`).

The audit surfaced **9 findings** — 1 high, 4 medium, 3 low, 1 informational. The two most user-visible items are scroll-reveal content stuck at `opacity:0` on the public SPA home page and "undefined" tokens leaking into the GHG Inventory Report.

Role-based testing (Approver / Observer / basic User) and the bench's adversarial Wave 2 (fuzz / race / chaos / permission-escalation) are **not yet run** — both require explicit user authorisation per the project's `safe_for_adversarial` policy.

---

## 2. What's working

| Area | Verified on live |
|---|---|
| Editorial palette tokens | `--ed-forest #01472e`, `--ed-cream #fefae0`, `--ed-sage #ccd5ae`, `--ed-olive #e9edc9`, `--ed-moss #a3b18a`, plus opacity variants — all present in `:root`, used consistently |
| Typography — Anton (display) | Loaded; applied to dashboard h1, list page-titles, SPA masthead "IMRV", section headlines |
| Typography — Inter (body) | Multiple weights (400/500/700) loaded; body copy, buttons, sub-menu items, breadcrumbs |
| Frosted-glass drawer | `var(--ed-frost-bg)` translucent surface + 20px blur; cream sticky header band with SI flag |
| Lucide-style rail icons | Top-level drawer items use mask-image SVG; consistent stroke weight, single visual family |
| Contextual flyout submenu | Pops at clicked-row level with cream header, group-head sub-titles, scroll-anchored when row is near viewport bottom |
| Status badges in lists | Sage/forest tints, readable, on-brand |
| Pill CTAs | Forest fill, cream text, uppercase Inter (login button, "+ ADD MITIGATIONS", drawer trigger) |
| SPA editorial composition | Torn-edge photo cards, oversized Anton headlines, "FIELD DISPATCH / SLOW NEWS" footer, real partner logos (UNDP, Australian Aid, GGGI) |
| Mobile responsive (390 px) | Clean vertical stack; header → IMRV mark → body copy → metadata; no horizontal scroll |
| HTTP surface | All 33 URLs 2xx; correct cache directives; no tracebacks; `/files/` 1h cache; `/assets/` revalidating |

---

## 3. Findings (priority-ranked)

### F1 — SPA reveal-stuck-on-load `[High]`

**Where:** `/frontend/home` (and likely every SPA route using `useReveal()`).
**What I saw:** 11 of 14 `[data-reveal]` elements stuck at `opacity:0` on initial render. Affected content includes the entire "PROGRAMS" section, three program photo cards ("Coastal Adaptation 14 Sites", "Forest Mitigation 9 Provinces", "Reef Inventory 226 Reports"), the "WE MEASURE WHAT WE MEAN TO PROTECT" statement, and the stats row (42+ verified projects, 9/9 provinces reporting, SBD 84.6M, −12% YoY).
**When it happens:** anyone whose viewport doesn't reach the element on initial paint AND who doesn't scroll. Includes:
- fullPage screenshot tools (caught this audit)
- non-scrolling assistive tech / screen-readers
- SEO crawlers
- users on tall displays where the element is *almost* in view but no scroll occurs
**Self-heals:** yes, on scroll. All 14 reveal once the user scrolls past them.
**Root cause hypothesis:** `useReveal` composable's synchronous prime-walk (per memory `feedback_io_threshold_pitfall.md`) either regressed or wasn't applied to this composable instance. Memory entry documents the prior fix.
**Action:** in `frontend/src/composables/useReveal.js`, run a synchronous prime-walk on mount adding `is-revealed` to every element above `1.5 × viewport.height`, before the IntersectionObserver wires up. Validate with the bench `data-reveal` health assertion.

### F2 — GHG Inventory Report renders `undefined` tokens `[Medium]`

**Where:** `/desk/ghg-inventory-report`.
**What I saw:** rendered text contains `undefined tCO₂e GgCO₂e undefined`. Likely a chart-series label or unit-dropdown option with a missing-name fallback.
**Action:** trace the unit/series source; supply a default label or filter `undefined` entries before rendering. Add a regression assertion: page text never contains the literal `undefined`.

### F3 — Sector pie chart degenerates when one sector is 100 % `[Medium]`

**Where:** `/desk/ghg-inventory-report` → "Total National Emission of all Gases - Sector Wise".
**What I saw:** sample data shows Energy 100 %, all other sectors 0 %. Pie chart renders as a single solid forest-green disk, no labels, indistinguishable from "no data".
**Action:** swap to a centerstone callout when one segment ≥ 95 %, or render as a stacked bar so single-sector cases are still legible.

### F4 — GHG gas-wise bar chart has no value labels `[Medium]`

**Where:** same report — "Total National Emission of all Gases (tCO₂e)".
**What I saw:** CO₂ ≈ 300, CH₄ and N₂O at 0. Bars without numeric annotations make proportions look more dramatic than the underlying data.
**Action:** add data labels above each bar; or annotate empty bars explicitly ("0 tCO₂e").

### F5 — Drawer flyouts use Font-Awesome icons (inconsistent with Lucide rail) `[Medium]`

**Where:** every parent submenu in the floating drawer.
**What I saw:** 27 `i.fa.fa-bar-chart` instances inside the drawer's flyouts. The rail (top-level items) uses Lucide-style mask SVGs. The flyout (children) falls through to FA glyphs.
**Action:** map each FA class in flyouts to a Lucide-style mask SVG, mirroring the rail. Or assign `sub_menu_icon`/`sub_menu_image_icon` per item in the `Sub Menu` seed JSON.

### F6 — `+ ADD MITIGATIONS` button copy reads grammatically odd `[Low]`

**Where:** `/desk/mitigations` list view top-right.
**What I saw:** Frappe button uses doctype name (plural "Mitigations"). "Add Mitigations" reads as a bulk-action label, not "create one".
**Action:** rename the doctype label to singular ("Mitigation"), or override the button copy at the doctype-meta level. Same likely applies to "Adaptation" if doctype name is plural.

### F7 — Login layout has tight vertical rhythm `[Low]`

**Where:** `/login`.
**What I saw:** flag → "SIGN IN" → "iMRV TOOL · AUTHORISED ACCESS" sub-line are visually close together. At smaller viewports the composition feels cramped.
**Action:** increase vertical rhythm by ~8 px between flag → heading → tagline. Editorial composition benefits from breathing room.

### F8 — Recent Activity heading is very small `[Low]`

**Where:** `/desk/main-dashboard` Recent Activity section.
**What I saw:** Inter, 11 px, 3.3 px letter-spacing. Small-caps editorial feel intended, but at the edge of readability.
**Action:** bump to 12 px, drop letter-spacing to 0.24 em.

### F9 — Console errors on every desk page `[Informational]`

**Where:** every `/desk/*` page.
**What I saw:** ≥ 1 console error and 5–17 warnings per page (consistent across pages).
**Action:** out of scope for an external UX audit. Engineering should grep for the recurring error string and decide whether it's a known Frappe v16 quirk or actionable.

---

## 4. Not tested (blocked, with suggested next steps)

| Dimension | Why blocked | Recommended next step |
|---|---|---|
| Role-based UX (Approver, Observer, basic User) | Real-user PII in sample DB; no test creds provided | Create 4 obvious test users from the Administrator session with `_test` suffix, audit each, disable (not delete) at end. Or add real test creds via secrets file. |
| Adversarial Wave 2 (fuzz, race, chaos, permission-escalation) | `safe_for_adversarial: false` on live by policy | Run the bench at `--target=local-docker --include-adversarial`. Bench refuses to run these against live by design. |
| End-to-end create flows (new project, new monitoring report, new approval) | Would create real records on a shared demo | Run on `local-docker` against the same data shape. |
| Accessibility audit (axe, keyboard nav, contrast for color-vision-deficient users) | Not run this session | Lighthouse audit + axe via `mcp__chrome-devtools__lighthouse_audit` on each main surface. |
| 4G / slow-network performance | Not run | Lighthouse with throttled-network preset. |

---

## 5. Suggested execution order

1. **Ship F1** (reveal-stuck) — highest visibility impact, smallest fix area (one composable). Add bench assertion.
2. **Ship F2** (`undefined` tokens) — small fix, eliminates "broken" perception.
3. **Run adversarial Wave 2** on `local-docker` — fastest way to surface security/race-condition issues that wouldn't show in this UX audit.
4. **Create 4 test users + role-flow audit on live** — needs your go/no-go on the writes.
5. **Ship F3, F4** (chart degenerate cases) together — both touch the GHG report.
6. **Ship F5** (drawer flyout icons) — visible on every drawer interaction.
7. **F6, F7, F8** — copy / spacing polish, can land in a single sweep.
8. **F9** — engineering deep-dive, not UX.

---

## 6. Permanence — bench scenarios to add

Per project policy "every memory entry describing a runtime invariant must become a bench scenario in the same session" — these findings should each gain a deterministic A-tier check:

| Finding | Bench assertion |
|---|---|
| F1 | `data_reveal_health` — open `/frontend/home`, count `[data-reveal]` with `opacity < 0.5` and visible bounds; threshold 0. |
| F2 | `no_undefined_in_text` — every desk + SPA route's body text must not contain literal `undefined`. |
| F3 | `pie_segment_legibility` — when sector data is single-segment ≥ 95 %, render assertion checks for centerstone callout (not solid disk). |
| F4 | `bar_chart_data_labels` — every value bar in GHG report has a sibling text label with the value. |
| F5 | `drawer_icon_family_consistency` — count of `.main-sidebar i.fa-` vs Lucide mask icons; assert 0 FA in flyouts (or document the design choice). |
| F6 | `singular_doctype_button` — list-view "Add" buttons use singular label. |

---

*End of audit*
