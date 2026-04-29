# bench/ — iMRV Test Bench

A scored, multi-perspective deploy-verification harness. Separate from
[`tests/`](../tests/) — the pytest harness owns code-level integration
against a fresh bench; the test bench owns deploy-verification + quality-trend
against deployed targets (local Docker replica, Railway preview, Railway live).

Design and full rationale: [`~/.claude/plans/despite-diffrent-and-multiple-sharded-frost.md`](file://~/.claude/plans/despite-diffrent-and-multiple-sharded-frost.md).

## What's here today (Phase 1)

- **`bench.sh`** — single entry point.
- **`runner/a_runner.py`** — A-tier YAML executor. Drives Playwright through
  declarative `steps`, evaluates `assertions`, emits a per-run scorecard
  (`history/<run-id>/scorecard.json`).
- **`runner/role_discovery.py`** — introspects the live target's
  `Role` / `DocPerm` / `Custom DocPerm` tables; writes `roles.yaml`.
- **`runner/permission_matrix.py`** — for every pair `(actor_role, surface_owner_role)`,
  attempts surface URLs from the actor's session and asserts denied/allowed
  matches the actor's permission profile. Two leakage cells = A-tier fail.
- **`scenarios/journeys/{guest,user,approver,admin}/*.yaml`** — four user-type
  end-to-end journey templates.
- **`scenarios/regression/*.yaml`** — ten bug-derived regression scenarios
  ported from existing memory entries.
- **`fixtures/role_credentials.example.yaml`** — copy to
  `fixtures/role_credentials.yaml` (gitignored) and fill in.
- **`config.yaml`** — targets, tier defaults, B-tier flag (Phase 4 toggle).

Phase 2-6 deliverables (crawler, design-system-agent, adversarial Wave 2,
LLM judge, deploy integration, self-improvement) are not yet wired.

## Quick start

```bash
# Validate the YAML corpus and discovery loop without running a browser:
./bench/bench.sh --target=local-docker --tier=a --dry-run

# After spinning up the local Docker replica:
docker compose -f deploy/railway/docker-compose.local.yml up -d --build

# Copy the credentials template, fill in real test-user passwords:
cp bench/fixtures/role_credentials.example.yaml bench/fixtures/role_credentials.yaml
$EDITOR bench/fixtures/role_credentials.yaml

# Install Playwright (once):
python3 -m pip install playwright pyyaml requests
python3 -m playwright install chromium

# Run A-tier:
./bench/bench.sh --target=local-docker --tier=a
# Exits 0 if all scenarios pass, 1 on any failure (deploy blocked), 2 on
# misconfig.
```

## Scenario YAML schema

One file describes both the deterministic (A-tier) and judged (B-tier) checks
for one user journey:

```yaml
id: <unique-snake-case>
title: "Human-readable description"
perspective:
  role: <Frappe role name | guest>
  persona: standard | mobile_390 | slow_3g | csrf_expired | screen_reader
  environment: any | cold_container | warm
preconditions:
  sample_db: required | none
  session: anonymous | logged_in_as:<role>
  cache: warm | cold

steps:
  - navigate: /url/path             # absolute path, prepended to base_url
  - wait_for_selector:
      selector: "css selector"
      timeout_ms: 15000
  - capture: name-of-screenshot     # writes history/<run-id>/screenshots/...
  - capture_text: name-of-text      # writes history/<run-id>/text/<name>.txt
  - login_as: <role>                # uses fixtures/role_credentials.yaml
  - fill: { selector: "...", value: "..." }
  - click: "css selector"
  - walk_drawer:                    # opens drawer, clicks every entry, captures
      link_selector: "#fsm-drawer a[href]"
      settle_timeout_ms: 8000
      skip_patterns: [logout, mailto:, tel:]

assertions:                          # A-tier (deterministic, hard gate)
  - selector:
      selector: "img[src^='/files/']"
      count: { min: 8 }
      has_natural_width: true
  - no_console_error_matching: "regex pattern"
  - no_network_4xx_for_path: "/files/*"
  - url_matches: "regex:/(app|desk)/"
  - drawer_destinations_healthy:    # asserts each drawer entry walked is healthy
      min_body_text_length: 100
      require_heading: true
  - no_text_matching:               # typo / banned-string deny-list
      denylist_file: bench/fixtures/typo_denylist.txt
  - design_system: { fonts: enforced, ... }   # Phase 2

rubric:                              # B-tier (LLM-judged, observability)
  visual_integrity: true
  visual_design: true
  navigation_correctness: true
  error_handling: true

tags: [journey, role, day-1, ...]
sources:                             # provenance — bug, memory entry, commit
  - memory: reference_<bug>.md
  - commit: <sha>
```

Schema rules:

- Every step is a single-key dict. Unknown step kinds fail the scenario rather
  than silently no-op.
- Every assertion is also a single-key dict. Each is evaluated independently;
  one failure does not short-circuit the rest.
- `assertions` and `rubric` coexist. A scenario can be A-only, B-only, or both.
- No procedural code in YAML. If custom logic is required, point at a Python
  file via `custom_runner: my_scenario.py` (not implemented in Phase 1).

## Tiering

**A-tier (hard gate, blocks deploy):** every assertion is deterministic.
<100% pass → exit 1 → deploy blocked. Flakes are fixed by tightening selectors
or settle timeouts; **never** by retrying or weighting.

**B-tier (observability, no block):** Phase 4. LLM judge scores 1-10 per rubric
dimension. Sustained drops flag in the scorecard.

## Roles, discovery, and the permission matrix

The four user-type journeys (`journeys/<type>/`) are *templates*. They expand
into per-role concrete runs at execution time, using the role inventory
discovered by `role_discovery.py` and credentials from
`fixtures/role_credentials.yaml`.

`role_discovery.py` walks the live target's REST API as Administrator:

1. Enumerates `Role` rows where `disabled=0`.
2. Pulls `DocPerm` + `Custom DocPerm` per role; takes the max value across rows
   (`Custom DocPerm` overlays `DocPerm` additively).
3. Narrows to "effectively readable" doctypes — rows with `read=0` are dropped,
   matching the bug pattern flagged in
   [`reference_drawer_perm_filter.md`](file://~/.claude/projects/-Users-utahjazz-Library-CloudStorage-OneDrive-Personal-Github-iMRV-Solomon-Islands/memory/reference_drawer_perm_filter.md).
4. Writes `history/<run-id>/roles.yaml`, plus a `diff_vs_prior_run` block
   noting added/removed roles and per-role `gained_read` / `lost_read` deltas.

`permission_matrix.py` consumes that snapshot. For every pair
`(actor_role, surface_owner_role)` where actor ≠ owner, it attempts the
owner's surface URLs from the actor's session and checks the response status
against the actor's permission profile:

| Actor's profile | Response | Verdict |
|---|---|---|
| has read on doctype | 200 | OK |
| has read on doctype | 401/403/redirect-to-login | LEAK (false-deny) |
| no read on doctype  | 401/403/redirect-to-login | OK |
| no read on doctype  | 200 | LEAK (substring/Custom DocPerm leak) |

Two or more leakage cells = A-tier failure = deploy blocked.

## Outputs

Each run writes to `history/<run-id>/`:

- `scorecard.json` — pass/fail rollup, per-role sub-scores, failure detail.
- `screenshots/*.png` — one per `capture:` step.
- `roles.yaml` (when role_discovery runs) — role inventory snapshot.
- `permission_matrix.json` (when permission_matrix runs) — every cell + leakages.

`history/` is gitignored except for `INDEX.json` (a small rolling index of the
last N runs, written by Phase 4's `score.py`).

## Adding a scenario

Manual path:

1. Pick the right directory: `journeys/<role>/` for a primary user flow,
   `regression/` for a bug-derived test, `adversarial/` (Phase 3) for fuzz/
   race/chaos targets.
2. Author the YAML following the schema above. Lift a similar existing
   scenario as a starting point.
3. Run `./bench/bench.sh --target=local-docker --tier=a --scenarios='scenarios/<glob>.yaml' --dry-run`
   to validate parsing, then drop `--dry-run` to actually execute.
4. Add a `sources:` entry pointing at the memory entry or commit that
   motivated the scenario.

LLM-assisted path (Phase 4): `/bench add-scenario <bug-context>`.

Auto-promotion path (Phase 4+): `crawled/`, `judge/`, and `convergence/` directories
under `candidates/` collect findings; `/bench triage` walks them weekly.

## Boundary with `tests/`

| | `tests/` (pytest) | `bench/` |
|---|---|---|
| Target | fresh `bench serve` on port 8001 | deployed (Docker / Railway) |
| Lifecycle | per-test rollback via savepoint | persistent, real DB state |
| Scope | code-level integration (data, integration, ui, regression, security) | deploy-verification + quality-trend |
| Output | pytest pass/fail | scorecard JSON + screenshots + role/perm snapshots |
| Cadence | every PR (CI) | every deploy |
| Gating | required-check on PR | A-tier blocks deploy, B-tier observes |

The two suites are complementary, not competitive. A bug discovered by the
bench against a deployed Railway image becomes a regression test in **both**
places: a `tests/regression/` golden file pinning the code-level invariant,
and a `bench/scenarios/regression/` scenario gating future deploys.

## Troubleshooting

**`pyyaml not found`** — `python3 -m pip install pyyaml`.

**`playwright not installed`** — see Quick start; the runner only needs it for
real runs, not `--dry-run`.

**`no fixture credentials for role 'X'`** — copy `role_credentials.example.yaml`
to `role_credentials.yaml` and fill in. New roles discovered by `role_discovery.py`
without an entry here will fail the bench with a pointer to this file.

**Target unreachable** — confirm the local Docker replica is up
(`docker compose -f deploy/railway/docker-compose.local.yml ps`) and reachable
at `http://localhost:8080`. For `railway-live` targets, ensure
`RAILWAY_LIVE_URL` is exported.

**Flake on `wait_for_selector`** — do **not** add retries or longer timeouts
reflexively. Investigate: is the selector selecting an off-screen element?
Has the v16 selector contract changed (e.g., `.navbar-breadcrumbs` vs
`#navbar-breadcrumbs`)? Tighten the selector, then re-run.
