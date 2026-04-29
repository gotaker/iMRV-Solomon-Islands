"""
bench.runner.score — composite scoring + 5-run rolling delta.

Reads the most recent N scorecards from bench/history/<run-id>/scorecard.json
(plus optional judge.json), computes:

  - A-tier composite: pass/total across curated + crawled + adversarial
  - B-tier composite: mean of rubric averages
  - Per-rubric Δ vs prior 5 runs (flagged if Δ ≤ -0.5)

Writes:
  - bench/history/INDEX.json — small rolling index of last 50 runs (committed)
  - bench/history/<run-id>/score_summary.json — combined view

Standalone usage:
    python3 -m bench.runner.score --history bench/history \
        --window 5 --output bench/history/<run-id>/score_summary.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = REPO_ROOT / "bench"
HISTORY_DIR = BENCH_ROOT / "history"
INDEX_PATH = HISTORY_DIR / "INDEX.json"


def _list_runs(history_dir: Path) -> list[Path]:
    """Sorted oldest-first list of run directories with scorecard.json."""
    runs = [p for p in sorted(history_dir.iterdir()) if p.is_dir() and (p / "scorecard.json").exists()]
    return runs


def _aggregate_b_tier(judge_path: Path) -> dict[str, float]:
    """Mean score per rubric × dimension. Returns {rubric: avg}."""
    if not judge_path.exists():
        return {}
    data = json.loads(judge_path.read_text())
    by_rubric: dict[str, list[float]] = {}
    for j in data.get("judgments", []):
        scores = j.get("scores") or {}
        rubric = j.get("rubric")
        if not rubric:
            continue
        nums = [v for v in scores.values() if isinstance(v, (int, float))]
        if not nums:
            continue
        by_rubric.setdefault(rubric, []).extend(nums)
    return {k: statistics.fmean(v) for k, v in by_rubric.items() if v}


def _compute_deltas(history: list[dict], current: dict, window: int) -> dict[str, float]:
    """For each rubric in `current`, Δ = current - mean(prior `window` runs)."""
    deltas: dict[str, float] = {}
    for rubric, current_score in current.items():
        prior = [
            r["b_tier_rubrics"].get(rubric)
            for r in history[-window:]
            if r.get("b_tier_rubrics", {}).get(rubric) is not None
        ]
        if not prior:
            deltas[rubric] = 0.0
        else:
            deltas[rubric] = round(current_score - statistics.fmean(prior), 3)
    return deltas


def _update_index(run_id: str, summary: dict, max_entries: int = 50) -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    if INDEX_PATH.exists():
        index = json.loads(INDEX_PATH.read_text())
    else:
        index = {"schema_version": 1, "runs": []}
    index["runs"].append({
        "run_id": run_id,
        "a_tier_rate": summary["a_tier"]["rate"],
        "b_tier_composite": summary["b_tier"].get("composite"),
        "b_tier_rubrics": summary["b_tier"].get("rubrics", {}),
    })
    index["runs"] = index["runs"][-max_entries:]
    INDEX_PATH.write_text(json.dumps(index, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Composite scoring + rolling delta")
    parser.add_argument("--history", default=str(HISTORY_DIR))
    parser.add_argument("--window", type=int, default=5)
    parser.add_argument(
        "--run-id",
        default=None,
        help="run-id to summarize (default = most recent)",
    )
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    history_dir = Path(args.history)
    runs = _list_runs(history_dir)
    if not runs:
        print("[score] no runs in history", file=sys.stderr)
        return 2

    target_run = (
        history_dir / args.run_id if args.run_id else runs[-1]
    )
    if not target_run.exists():
        print(f"[score] run not found: {target_run}", file=sys.stderr)
        return 2

    scorecard = json.loads((target_run / "scorecard.json").read_text())
    b_rubrics = _aggregate_b_tier(target_run / "judge.json")
    composite = round(statistics.fmean(b_rubrics.values()), 3) if b_rubrics else None

    # Pull priors from INDEX.json (cheap) — falls back to history scan.
    history = []
    if INDEX_PATH.exists():
        history = json.loads(INDEX_PATH.read_text()).get("runs", [])
    deltas = _compute_deltas(history, b_rubrics, args.window)
    flagged = {k: v for k, v in deltas.items() if v <= -0.5}

    summary = {
        "schema_version": 1,
        "run_id": target_run.name,
        "a_tier": {
            "rate": scorecard.get("a_tier", {}).get("rate", 0),
            "passed": scorecard.get("a_tier", {}).get("passed", 0),
            "total": scorecard.get("a_tier", {}).get("total", 0),
        },
        "b_tier": {
            "rubrics": b_rubrics,
            "composite": composite,
            "deltas_vs_prior_window": deltas,
            "flagged_drops": flagged,
        },
    }

    output_path = Path(args.output) if args.output else target_run / "score_summary.json"
    output_path.write_text(json.dumps(summary, indent=2))
    _update_index(target_run.name, summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
