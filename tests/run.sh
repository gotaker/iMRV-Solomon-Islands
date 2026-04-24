#!/usr/bin/env bash
# Local entrypoint for the v16 test harness.
# Thin wrapper over pytest — CI invokes pytest directly.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

LAYER=""
FAST=0
UPDATE_GOLDEN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --layer)   LAYER="$2"; shift 2 ;;
    --fast)    FAST=1; shift ;;
    --update-golden) UPDATE_GOLDEN=1; shift ;;
    -h|--help)
      cat <<EOF
Usage: ./tests/run.sh [OPTIONS]

  --layer <data|integration|ui|regression|security>
                        Run only one layer
  --fast                Run layers 1+2+5 only (skip UI), ~45s
  --update-golden       Regenerate Layer 4 snapshot files
  -h, --help            Show this help
EOF
      exit 0
      ;;
    *) echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
done

ARGS=(-c tests/pytest.ini)

if [[ -n "$LAYER" ]]; then
  ARGS+=("tests/$LAYER")
elif [[ $FAST -eq 1 ]]; then
  export TESTS_SKIP_UI=1
  ARGS+=(tests/data tests/integration tests/security)
else
  ARGS+=(tests)
fi

if [[ $UPDATE_GOLDEN -eq 1 ]]; then
  export TESTS_UPDATE_GOLDEN=1
  ARGS+=(tests/regression)
fi

exec python3 -m pytest "${ARGS[@]}"
