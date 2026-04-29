"""
bench.runner.permission_escalation_agent — Wave 2 cross-role attack.

Thin wrapper over `permission_matrix.py`. The matrix module already does the
right thing for *known* surfaces; this agent expands the attack to crawler-
discovered URLs and explicitly tests the "leak" direction more aggressively:

  - takes the crawler's coverage.json as input
  - for every (actor_role, surface_owner_role) pair, tries every URL the
    owner reached, with the actor's session
  - re-uses permission_matrix's verdict logic + leakage definition

Standalone usage:
    python3 -m bench.runner.permission_escalation_agent --config bench/config.yaml \
        --target local-docker \
        --roles-file bench/history/<run-id>/roles.yaml \
        --coverage-file bench/history/<run-id>/coverage.json \
        --output bench/history/<run-id>/permission_escalation.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bench.runner.a_runner import _load_target, _load_yaml  # noqa: E402
from bench.runner.permission_matrix import _summarize, evaluate_matrix  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = REPO_ROOT / "bench"


def _surface_from_coverage(coverage: dict) -> dict[str, list[str]]:
    """coverage.json -> {role: [url, ...]} mapping."""
    surface: dict[str, list[str]] = {}
    for role, urls in coverage.items():
        if not isinstance(urls, dict):
            continue
        clean: list[str] = []
        for url, data in urls.items():
            if isinstance(data, dict) and data.get("status", 0) >= 400:
                continue
            # Strip origin to a path the matrix can reuse.
            if url.startswith("http"):
                idx = url.find("/", url.index("//") + 2)
                clean.append(url[idx:] if idx > 0 else "/")
            else:
                clean.append(url)
        surface[role] = sorted(set(clean))
    return surface


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Wave 2 cross-role escalation agent")
    parser.add_argument("--config", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--roles-file", required=True)
    parser.add_argument("--coverage-file", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    config = _load_yaml(Path(args.config))
    target = _load_target(config, args.target)
    if not target.get("safe_for_adversarial"):
        print(
            f"[esc] target '{args.target}' is not safe for adversarial. Refusing.",
            file=sys.stderr,
        )
        return 2

    roles_snapshot = _load_yaml(Path(args.roles_file))
    coverage = json.loads(Path(args.coverage_file).read_text())
    surface = _surface_from_coverage(coverage)
    credentials = _load_yaml(BENCH_ROOT / "fixtures" / "role_credentials.yaml") or {}

    cells = evaluate_matrix(target, roles_snapshot, surface, credentials)
    summary = _summarize(cells)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2))
    print(json.dumps({
        "total_cells": summary["total_cells"],
        "leaked_cells": summary["leaked_cells"],
        "passed": summary["passed"],
    }, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
