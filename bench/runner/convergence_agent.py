"""
bench.runner.convergence_agent — diff-aware candidate generator.

After Wave 1+2 + judge run, ask Sonnet:
  "Given the deploy diff and the failures we just saw, what could still be
   broken that the corpus didn't cover?"

Inputs: scorecard.json (A-tier), judge.json (B-tier), git diff stat for the
deploy range. Outputs: 0-5 candidate scenario YAMLs in
bench/candidates/convergence/.

This is the "stress test convergence" loop the user has trained on. Runs
every deploy, not just on demand.

Standalone usage:
    python3 -m bench.runner.convergence_agent --config bench/config.yaml \
        --scorecard bench/history/<run-id>/scorecard.json \
        --judge bench/history/<run-id>/judge.json \
        --diff-since <prev-sha> \
        --output bench/candidates/convergence/
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

from bench.runner.a_runner import _load_yaml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = REPO_ROOT / "bench"
DEFAULT_MODEL = "claude-sonnet-4-6"


def _git_diff_summary(since_ref: str | None) -> str:
    if not since_ref:
        return "(no diff range provided)"
    try:
        return subprocess.check_output(
            ["git", "log", "--stat", f"{since_ref}..HEAD"],
            cwd=REPO_ROOT, text=True, stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        return f"(git log failed: {exc.output[:200]})"


def _system_instruction() -> str:
    return (
        "You are an adversarial QA reviewer for the iMRV codebase. Given the deploy diff "
        "and the most recent test-bench results, your job is to predict 0-5 NEW scenarios "
        "that the existing test corpus probably missed. Focus on the code paths the diff "
        "actually touched.\n\n"
        "Return STRICT JSON: a list of candidate scenario stubs. Each stub has:\n"
        "  - id: snake_case identifier\n"
        "  - title: human description\n"
        "  - perspective: { role, persona, environment }\n"
        "  - reasoning: why this scenario could catch a real regression in this diff\n"
        "  - suggested_steps: list of step dicts (navigate, click, fill, etc.)\n"
        "  - suggested_assertions: list of assertion dicts\n\n"
        "Be SPECIFIC. 'Test the form better' is a useless suggestion. 'Test that the "
        "edited_project_details revision flow correctly persists field X after the "
        "schema change in commit abc' is useful.\n\n"
        "If you cannot identify any plausible gaps, return an empty list. Do NOT pad."
    )


def _build_user_message(scorecard: dict, judge: dict, diff_summary: str) -> str:
    a_tier = scorecard.get("a_tier", {})
    failures = a_tier.get("failures", [])
    judgments = judge.get("judgments", [])
    low_scores = []
    for j in judgments:
        scores = j.get("scores") or {}
        for k, v in scores.items():
            if isinstance(v, int) and v < 7:
                low_scores.append({
                    "scenario_id": j.get("scenario_id"),
                    "rubric": j.get("rubric"),
                    "dimension": k, "score": v,
                })

    return (
        f"## Deploy diff (last 100 lines):\n```\n{diff_summary[-3000:]}\n```\n\n"
        f"## A-tier failures: {len(failures)}\n"
        f"```json\n{json.dumps(failures[:10], indent=2)}\n```\n\n"
        f"## B-tier rubric scores below 7: {len(low_scores)}\n"
        f"```json\n{json.dumps(low_scores[:20], indent=2)}\n```\n\n"
        f"Return up to 5 candidate scenarios as a JSON array. No prose outside the array."
    )


def _write_candidate(stub: dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "_", stub.get("id", "candidate")).strip("_")[:80]
    path = output_dir / f"{slug}.yaml"
    yaml_stub = {
        "id": stub.get("id", slug),
        "title": stub.get("title", "(no title)"),
        "perspective": stub.get("perspective", {"role": "guest", "persona": "standard", "environment": "any"}),
        "preconditions": {"sample_db": "required", "session": "anonymous", "cache": "warm"},
        "steps": stub.get("suggested_steps", []),
        "assertions": stub.get("suggested_assertions", []),
        "tags": ["candidate", "convergence", "needs-triage"],
        "sources": [{"convergence_agent": stub.get("reasoning", "")}],
    }
    path.write_text(yaml.safe_dump(yaml_stub, sort_keys=False))
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diff-aware convergence agent")
    parser.add_argument("--config", required=True)
    parser.add_argument("--scorecard", required=True)
    parser.add_argument("--judge", required=True)
    parser.add_argument("--diff-since", default=None)
    parser.add_argument("--output", required=True, help="directory")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args(argv)

    config = _load_yaml(Path(args.config))
    if not (config.get("b_tier") or {}).get("enabled"):
        print("[convergence] b_tier disabled; skipping.", file=sys.stderr)
        return 0
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[convergence] ANTHROPIC_API_KEY not set; skipping.", file=sys.stderr)
        return 0

    try:
        from anthropic import Anthropic
    except ImportError:
        print("[convergence] anthropic SDK not installed; pip install anthropic", file=sys.stderr)
        return 2

    scorecard = json.loads(Path(args.scorecard).read_text())
    judge = json.loads(Path(args.judge).read_text()) if Path(args.judge).exists() else {"judgments": []}
    diff_summary = _git_diff_summary(args.diff_since)

    client = Anthropic()
    response = client.messages.create(
        model=args.model,
        max_tokens=4096,
        system=[{
            "type": "text",
            "text": _system_instruction(),
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{
            "role": "user",
            "content": [{"type": "text", "text": _build_user_message(scorecard, judge, diff_summary)}],
        }],
    )

    text = "".join(b.text for b in response.content if getattr(b, "type", None) == "text")
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
    try:
        candidates = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        print(f"[convergence] could not parse JSON: {exc}\n--- raw ---\n{text[:500]}", file=sys.stderr)
        return 1

    if not isinstance(candidates, list):
        candidates = []
    candidates = candidates[:5]

    output_dir = Path(args.output)
    written = [_write_candidate(c, output_dir) for c in candidates]
    print(f"[convergence] wrote {len(written)} candidate(s) → {output_dir.relative_to(REPO_ROOT)}")
    for p in written:
        print(f"  {p.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
