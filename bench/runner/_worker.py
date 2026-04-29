"""
bench.runner._worker — single-process worker invoked by parallel runs.

Reads its assignment from a JSON file on disk, runs the assigned scenarios,
writes results to another JSON file. Avoids cross-process IPC entirely —
parent and worker communicate through the filesystem, which is robust,
debuggable, and platform-agnostic.

Not invoked directly by users; bench/runner/a_runner.py spawns this via
subprocess when --parallel > 1.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bench.runner.a_runner import _run_scenario, _load_yaml, _load_target

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = REPO_ROOT / "bench"


def main() -> int:
    parser = argparse.ArgumentParser(description="bench parallel worker (internal)")
    parser.add_argument("--assignment", required=True,
                        help="JSON file with batch info: scenario paths + target + run-id")
    parser.add_argument("--output", required=True,
                        help="JSON file path for results")
    args = parser.parse_args()

    assignment = json.loads(Path(args.assignment).read_text())
    config = _load_yaml(Path(assignment["config_path"]))
    target = _load_target(config, assignment["target"])
    run_dir = Path(assignment["run_dir"])

    creds_path = Path(assignment["credentials_path"])
    credentials = _load_yaml(creds_path) if creds_path.exists() else {}

    from playwright.sync_api import sync_playwright

    out: list[dict] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for scenario_path_str in assignment["scenario_paths"]:
                scenario_path = Path(scenario_path_str)
                result = _run_scenario(
                    scenario_path, target, credentials, run_dir, config, browser,
                    assignment.get("dry_run", False),
                )
                out.append({
                    "scenario_id": result.scenario_id,
                    "role": result.role,
                    "persona": result.persona,
                    "journey_path": result.journey_path,
                    "duration_ms": result.duration_ms,
                    "passed": result.passed,
                    "error": result.error,
                    "screenshot_path": result.screenshot_path,
                    "assertions": [
                        {"name": a.name, "passed": a.passed, "detail": a.detail}
                        for a in result.assertions
                    ],
                })
        finally:
            browser.close()

    Path(args.output).write_text(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
