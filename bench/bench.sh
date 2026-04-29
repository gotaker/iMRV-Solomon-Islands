#!/usr/bin/env bash
# bench.sh — single entry point for the iMRV test bench.
#
# Usage:
#   ./bench/bench.sh --target=<local-docker|local-bench|railway-live> [flags]
#
# Common flags:
#   --tier=<a|b|all>            which tiers to run (default: a)
#   --scenarios=<glob>          subset by scenario glob (relative to bench/)
#   --roles=<csv>               filter to these roles only
#   --include-discovery         run role_discovery before A-tier
#   --include-permission-matrix run cross-role permission matrix
#   --include-crawler           run per-role exhaustive crawler
#   --include-design-system     stricter design-system enforcement (Phase 2)
#   --include-adversarial       run Wave 2 (fuzz/race/chaos/escalation) — local-docker only
#   --include-judge             run B-tier LLM judge (requires ANTHROPIC_API_KEY)
#   --include-convergence       run convergence-agent (requires --diff-since)
#   --diff-since=<sha>          base ref for convergence-agent diff context
#   --update-golden             regenerate golden screenshot baselines
#   --dry-run                   discover only; don't launch a browser
#
# Exit codes:
#   0   all A-tier checks passed (B-tier is observability-only, never blocks)
#   1   one or more A-tier checks failed (deploy blocked)
#   2   misconfiguration / fixture missing / target unreachable
#
# See bench/README.md for the full schema reference.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TARGET="local-docker"
TIER="a"
SCENARIOS_GLOB=""
ROLES_FILTER=""
UPDATE_GOLDEN=0
DRY_RUN=0
PARALLEL=1
INCLUDE_DISCOVERY=0
INCLUDE_PERM_MATRIX=0
INCLUDE_CRAWLER=0
INCLUDE_ADVERSARIAL=0
INCLUDE_JUDGE=0
INCLUDE_CONVERGENCE=0
DIFF_SINCE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target=*)              TARGET="${1#*=}"; shift ;;
    --target)                TARGET="$2"; shift 2 ;;
    --tier=*)                TIER="${1#*=}"; shift ;;
    --tier)                  TIER="$2"; shift 2 ;;
    --scenarios=*)           SCENARIOS_GLOB="${1#*=}"; shift ;;
    --roles=*)               ROLES_FILTER="${1#*=}"; shift ;;
    --include-discovery)        INCLUDE_DISCOVERY=1; shift ;;
    --include-permission-matrix) INCLUDE_PERM_MATRIX=1; shift ;;
    --include-crawler)          INCLUDE_CRAWLER=1; shift ;;
    --include-adversarial)      INCLUDE_ADVERSARIAL=1; shift ;;
    --include-judge)            INCLUDE_JUDGE=1; shift ;;
    --include-convergence)      INCLUDE_CONVERGENCE=1; shift ;;
    --diff-since=*)             DIFF_SINCE="${1#*=}"; shift ;;
    --update-golden)            UPDATE_GOLDEN=1; shift ;;
    --dry-run)                  DRY_RUN=1; shift ;;
    --parallel=*)               PARALLEL="${1#*=}"; shift ;;
    --parallel)                 PARALLEL="$2"; shift 2 ;;
    -h|--help)
      sed -n '3,28p' "$0"
      exit 0
      ;;
    *) echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
done

case "$TIER" in
  a|b|all) ;;
  *) echo "Invalid --tier: $TIER (expected: a, b, all)" >&2; exit 2 ;;
esac

# Each bench session writes to a single run-id directory, computed up front so
# every component agrees on the location.
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
RUN_DIR="$REPO_ROOT/bench/history/$RUN_ID"
mkdir -p "$RUN_DIR"

CONFIG="$REPO_ROOT/bench/config.yaml"

# --- Step 1: role discovery (optional) ---
if [[ $INCLUDE_DISCOVERY -eq 1 && $DRY_RUN -eq 0 ]]; then
  python3 -m bench.runner.role_discovery \
    --config "$CONFIG" --target "$TARGET" \
    --output "$RUN_DIR/roles.yaml" || exit $?
fi

# --- Step 2: A-tier (always, unless tier=b) ---
A_RUNNER_ARGS=(
  --config "$CONFIG"
  --target "$TARGET"
  --tier "$TIER"
  --run-id "$RUN_ID"
)
[[ -n "$SCENARIOS_GLOB" ]] && A_RUNNER_ARGS+=(--scenarios "$SCENARIOS_GLOB")
[[ -n "$ROLES_FILTER"   ]] && A_RUNNER_ARGS+=(--roles "$ROLES_FILTER")
[[ $UPDATE_GOLDEN -eq 1 ]] && A_RUNNER_ARGS+=(--update-golden)
[[ $DRY_RUN -eq 1 ]]       && A_RUNNER_ARGS+=(--dry-run)
[[ $PARALLEL -gt 1 ]]      && A_RUNNER_ARGS+=(--parallel "$PARALLEL")

A_TIER_EXIT=0
if [[ "$TIER" != "b" ]]; then
  python3 -m bench.runner.a_runner "${A_RUNNER_ARGS[@]}" || A_TIER_EXIT=$?
fi

# --- Step 3: permission matrix (optional, after roles.yaml exists) ---
if [[ $INCLUDE_PERM_MATRIX -eq 1 && $DRY_RUN -eq 0 && -f "$RUN_DIR/roles.yaml" ]]; then
  python3 -m bench.runner.permission_matrix \
    --config "$CONFIG" --target "$TARGET" \
    --roles-file "$RUN_DIR/roles.yaml" \
    --output "$RUN_DIR/permission_matrix.json" || A_TIER_EXIT=$?
fi

# --- Step 4: crawler (optional) ---
if [[ $INCLUDE_CRAWLER -eq 1 && $DRY_RUN -eq 0 ]]; then
  python3 -m bench.runner.crawler \
    --config "$CONFIG" --target "$TARGET" \
    --output "$RUN_DIR/coverage.json" || true
fi

# --- Step 5: adversarial Wave 2 (optional, only if A-tier passed and target safe) ---
if [[ $INCLUDE_ADVERSARIAL -eq 1 && $DRY_RUN -eq 0 && $A_TIER_EXIT -eq 0 ]]; then
  python3 -m bench.runner.fuzz_agent --config "$CONFIG" --target "$TARGET" \
    --output "$RUN_DIR/fuzz.json" || true
  python3 -m bench.runner.race_agent --config "$CONFIG" --target "$TARGET" \
    --output "$RUN_DIR/race.json" || true
  python3 -m bench.runner.chaos_agent --config "$CONFIG" --target "$TARGET" \
    --output "$RUN_DIR/chaos.json" || true
  if [[ -f "$RUN_DIR/coverage.json" && -f "$RUN_DIR/roles.yaml" ]]; then
    python3 -m bench.runner.permission_escalation_agent \
      --config "$CONFIG" --target "$TARGET" \
      --roles-file "$RUN_DIR/roles.yaml" \
      --coverage-file "$RUN_DIR/coverage.json" \
      --output "$RUN_DIR/permission_escalation.json" || true
  fi
fi

# --- Step 6: B-tier judge (optional) ---
if [[ $INCLUDE_JUDGE -eq 1 && $DRY_RUN -eq 0 && -f "$RUN_DIR/scorecard.json" ]]; then
  python3 -m bench.runner.judge \
    --config "$CONFIG" --target "$TARGET" \
    --scorecard "$RUN_DIR/scorecard.json" \
    --output "$RUN_DIR/judge.json" || true
fi

# --- Step 7: convergence (optional) ---
if [[ $INCLUDE_CONVERGENCE -eq 1 && $DRY_RUN -eq 0 && -f "$RUN_DIR/scorecard.json" ]]; then
  CONV_ARGS=(
    --config "$CONFIG"
    --scorecard "$RUN_DIR/scorecard.json"
    --judge "$RUN_DIR/judge.json"
    --output "$REPO_ROOT/bench/candidates/convergence"
  )
  [[ -n "$DIFF_SINCE" ]] && CONV_ARGS+=(--diff-since "$DIFF_SINCE")
  python3 -m bench.runner.convergence_agent "${CONV_ARGS[@]}" || true
fi

# --- Step 8: score summary (always, after all the above) ---
if [[ $DRY_RUN -eq 0 && -f "$RUN_DIR/scorecard.json" ]]; then
  python3 -m bench.runner.score \
    --history "$REPO_ROOT/bench/history" \
    --run-id "$RUN_ID" \
    --output "$RUN_DIR/score_summary.json" >/dev/null || true
fi

# --- Step 9: human-readable report (always) ---
if [[ $DRY_RUN -eq 0 && -f "$RUN_DIR/scorecard.json" ]]; then
  python3 -m bench.runner.report --run-dir "$RUN_DIR" || true
fi

echo "[bench] run_id=$RUN_ID exit=$A_TIER_EXIT"
echo "[bench] report: $RUN_DIR/report.md"
exit "$A_TIER_EXIT"
