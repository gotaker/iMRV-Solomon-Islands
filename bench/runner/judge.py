"""
bench.runner.judge — B-tier LLM-as-judge.

For each scenario whose YAML has a `rubric:` block, sends the captured
screenshot + collected runtime metadata (console errors, network 4xx, timing)
to Claude Sonnet, scored against the rubric files in bench/rubrics/.

Uses prompt caching: rubric content + system instructions are stable across
scenarios, so they ride the cache. Only the per-scenario screenshot + metadata
varies. Per the claude-api skill, we structure messages so the cache breakpoint
falls between the cached preamble and the per-call user content.

Output: bench/history/<run-id>/judge.json — per-scenario rubric scores plus
rolling-window deltas.

Standalone usage:
    python3 -m bench.runner.judge --config bench/config.yaml \
        --target local-docker --scorecard bench/history/<run-id>/scorecard.json \
        --output bench/history/<run-id>/judge.json
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from typing import Any

from bench.runner.a_runner import _load_target, _load_yaml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = REPO_ROOT / "bench"
RUBRICS_DIR = BENCH_ROOT / "rubrics"

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 1024


def _load_rubrics() -> dict[str, str]:
    """Load every rubric file as {dimension_name: full_markdown}."""
    out: dict[str, str] = {}
    for f in sorted(RUBRICS_DIR.glob("*.md")):
        if f.name.startswith("_") or f.name.lower() == "readme.md":
            continue
        out[f.stem] = f.read_text(encoding="utf-8")
    return out


def _system_instruction() -> str:
    return (
        "You are an expert UI/UX evaluator scoring screenshots of an iMRV "
        "(Measurement, Reporting & Verification) web application built on Frappe v16 "
        "with a Vue 3 SPA frontend. The design system is 'Forest-and-Sage editorial' — "
        "Anton display + Inter body, sage/forest greens, frosted-glass overlays, "
        "magazine-grade whitespace.\n\n"
        "Score each rubric dimension 1-10 (whole numbers). Return STRICT JSON matching "
        "the rubric's output schema exactly — no surrounding prose, no markdown fences, "
        "no extra keys.\n\n"
        "Be concrete and actionable in `reasoning`. Avoid generic praise."
    )


def _encode_screenshot(path: Path) -> dict[str, Any] | None:
    """Return an Anthropic image content block for the screenshot, or None if missing."""
    if not path.exists():
        return None
    data = path.read_bytes()
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": base64.standard_b64encode(data).decode("ascii"),
        },
    }


def _build_messages(
    scenario: dict[str, Any],
    rubric_name: str,
    rubric_content: str,
    screenshot_block: dict | None,
    metadata: dict[str, Any],
) -> list[dict[str, Any]]:
    """Compose the messages for one scenario × one rubric judgment.

    Cache breakpoint: the rubric content goes in a cached system block; the
    per-scenario user content (screenshot + metadata) is the only thing that
    varies between calls.
    """
    user_blocks: list[dict[str, Any]] = []
    if screenshot_block:
        user_blocks.append(screenshot_block)
    user_blocks.append({
        "type": "text",
        "text": (
            f"## Scenario\n\n"
            f"- id: {scenario.get('scenario_id', '?')}\n"
            f"- role: {scenario.get('role', '?')}\n"
            f"- persona: {scenario.get('persona', '?')}\n"
            f"- duration_ms: {metadata.get('duration_ms', '?')}\n"
            f"- console_error_count: {metadata.get('console_error_count', 0)}\n"
            f"- network_4xx_count: {metadata.get('network_4xx_count', 0)}\n"
            f"- dom_size_estimate: {metadata.get('dom_size_estimate', '?')}\n\n"
            f"Score against the **{rubric_name}** rubric. Return ONLY the JSON object."
        ),
    })
    return [{"role": "user", "content": user_blocks}]


def _judge_one(
    client,
    scenario: dict[str, Any],
    rubric_name: str,
    rubric_content: str,
    screenshot_path: Path | None,
    metadata: dict[str, Any],
    model: str,
) -> dict[str, Any]:
    screenshot_block = _encode_screenshot(screenshot_path) if screenshot_path else None
    if screenshot_block is None:
        return {
            "rubric": rubric_name,
            "scenario_id": scenario.get("scenario_id"),
            "skipped": "no screenshot available",
        }

    response = client.messages.create(
        model=model,
        max_tokens=DEFAULT_MAX_TOKENS,
        system=[
            {
                "type": "text",
                "text": _system_instruction(),
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": f"## Active rubric: {rubric_name}\n\n{rubric_content}",
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=_build_messages(scenario, rubric_name, rubric_content, screenshot_block, metadata),
    )

    text = "".join(b.text for b in response.content if getattr(b, "type", None) == "text")
    try:
        # Strip optional markdown fences before json.loads.
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
        scores = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        return {
            "rubric": rubric_name,
            "scenario_id": scenario.get("scenario_id"),
            "raw_text": text[:500],
            "parse_error": str(exc),
        }

    return {
        "rubric": rubric_name,
        "scenario_id": scenario.get("scenario_id"),
        "scores": scores,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "cache_creation_input_tokens": getattr(response.usage, "cache_creation_input_tokens", 0),
            "cache_read_input_tokens": getattr(response.usage, "cache_read_input_tokens", 0),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="B-tier LLM judge")
    parser.add_argument("--config", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--scorecard", required=True, help="A-tier scorecard.json from this run")
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--rubrics",
        default=None,
        help="csv: only run these rubrics (default = all)",
    )
    parser.add_argument(
        "--max-scenarios",
        type=int,
        default=None,
        help="cap the number of scenarios judged (cost guard)",
    )
    args = parser.parse_args(argv)

    config = _load_yaml(Path(args.config))
    if not (config.get("b_tier") or {}).get("enabled"):
        print("[judge] b_tier.enabled is false in config; skipping (Phase 4 toggle).", file=sys.stderr)
        return 0

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "[judge] ANTHROPIC_API_KEY not set; skipping B-tier rather than failing the run.",
            file=sys.stderr,
        )
        return 0

    try:
        from anthropic import Anthropic
    except ImportError:
        print(
            "[judge] anthropic SDK not installed; pip install anthropic",
            file=sys.stderr,
        )
        return 2

    rubrics = _load_rubrics()
    if args.rubrics:
        wanted = {r.strip() for r in args.rubrics.split(",")}
        rubrics = {k: v for k, v in rubrics.items() if k in wanted}

    scorecard = json.loads(Path(args.scorecard).read_text())
    scenarios = scorecard.get("scenarios", [])
    if args.max_scenarios:
        scenarios = scenarios[: args.max_scenarios]

    client = Anthropic()

    # Build the (scenario, rubric) work plan, then sort by rubric for KV-cache
    # locality. Each cached-system block is (system_instruction + rubric); when
    # consecutive calls share the same rubric, the second cached block hits.
    # Loop order matters: rubric-outer keeps the rubric stable across scenarios,
    # invalidating the rubric cache only `len(rubrics)` times per run instead of
    # `len(scenarios)` × `len(rubrics)` times.
    plan: list[tuple[dict, str]] = []
    for scenario in scenarios:
        spec_path = REPO_ROOT / scenario["journey_path"]
        spec = _load_yaml(spec_path) if spec_path.exists() else {}
        rubric_flags = spec.get("rubric") or {}
        for rname in rubrics:
            if rubric_flags.get(rname):
                plan.append((scenario, rname))

    # Stable, cache-friendly ordering: group by rubric, then by scenario_id.
    plan.sort(key=lambda pair: (pair[1], pair[0].get("scenario_id", "")))

    judgments: list[dict[str, Any]] = []
    for scenario, rname in plan:
        screenshot_rel = scenario.get("screenshot_path")
        screenshot_path = REPO_ROOT / screenshot_rel if screenshot_rel else None
        metadata = {
            "duration_ms": scenario.get("duration_ms"),
            "console_error_count": 0,  # TODO: thread from a_runner output
            "network_4xx_count": 0,
            "dom_size_estimate": None,
        }
        judgments.append(_judge_one(
            client, scenario, rname, rubrics[rname], screenshot_path, metadata, args.model,
        ))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({
        "schema_version": 1,
        "model": args.model,
        "rubrics_used": sorted(rubrics),
        "judgments": judgments,
    }, indent=2))
    print(f"[judge] wrote {len(judgments)} judgments → {output.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
