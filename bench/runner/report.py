"""
bench.runner.report — human-readable per-run report.

Reads scorecard.json (+ score_summary.json + judge.json + permission_matrix.json
+ coverage.json + adversarial outputs if present) and writes:

  - bench/history/<run-id>/report.md  (Markdown — viewable in any IDE)
  - bench/history/<run-id>/report.html (optional, with embedded screenshots)

The Markdown report is the primary deliverable; HTML is a convenience for
sharing via Slack/PR comments.

Standalone usage:
    python3 -m bench.runner.report --run-id <run-id>
    python3 -m bench.runner.report --run-dir bench/history/<run-id>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = REPO_ROOT / "bench"
HISTORY_DIR = BENCH_ROOT / "history"


def _safe_load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _format_assertion(a: dict, status_emoji: bool = True) -> str:
    icon = ("✓" if a.get("passed") else "✗") if status_emoji else ""
    detail = (a.get("detail") or "").replace("\n", " ")
    if len(detail) > 240:
        detail = detail[:240] + "…"
    return f"  - {icon} `{a.get('kind')}` — {detail}"


def _format_scenario(s: dict, run_dir_rel: str) -> list[str]:
    lines: list[str] = []
    icon = "✅" if s.get("passed") else "❌"
    lines.append(f"### {icon} `{s['scenario_id']}` ({s['duration_ms']} ms)")
    lines.append(f"- **role**: `{s.get('role')}`")
    lines.append(f"- **persona**: `{s.get('persona')}`")
    lines.append(f"- **journey**: [{s['journey_path']}]({Path('..').as_posix()}/../../{s['journey_path']})")
    if s.get("error"):
        lines.append(f"- **error**: `{s['error']}`")
    if s.get("screenshot_path"):
        # Screenshot lives at e.g. bench/history/<run-id>/screenshots/<file>.png
        # The report itself sits at bench/history/<run-id>/report.md, so use a
        # relative path from the report.
        rel = Path(s["screenshot_path"]).relative_to(Path(run_dir_rel))
        lines.append(f"- **screenshot**: [{rel.name}]({rel.as_posix()})")
    if s.get("assertions"):
        lines.append("")
        lines.append("**Assertions:**")
        for a in s["assertions"]:
            lines.append(_format_assertion(a))
    lines.append("")
    return lines


def _format_section_header(title: str) -> list[str]:
    return ["", f"## {title}", ""]


def _format_a_tier_summary(scorecard: dict) -> list[str]:
    a = scorecard.get("a_tier", {}) or {}
    rate = a.get("rate", 0)
    rate_pct = rate * 100
    verdict = "✅ PASS — deploy proceeds" if rate >= 1.0 else "❌ FAIL — deploy blocked"

    lines = [
        f"**A-tier (deploy gate):** {a.get('passed', 0)} / {a.get('total', 0)} passing  "
        f"({rate_pct:.1f}%) — {verdict}",
        "",
    ]

    by_role = a.get("by_role") or {}
    if by_role:
        lines.append("**Per-role sub-scores:**")
        lines.append("")
        lines.append("| Role | Pass | Total | Rate |")
        lines.append("| --- | --- | --- | --- |")
        for role, slot in sorted(by_role.items()):
            r_rate = (slot["passed"] / slot["total"] * 100) if slot.get("total") else 0
            lines.append(f"| `{role}` | {slot['passed']} | {slot['total']} | {r_rate:.1f}% |")
        lines.append("")

    failures = a.get("failures") or []
    if failures:
        lines.append("**Failures:**")
        lines.append("")
        for f in failures:
            lines.append(f"- `{f['scenario_id']}` ({f['role']})")
            for fa in f.get("failed_assertions", []) or []:
                lines.append(f"    - `{fa['kind']}`: {fa['detail'][:300]}")
            if f.get("error"):
                lines.append(f"    - error: `{f['error']}`")
        lines.append("")

    return lines


def _format_b_tier_summary(score_summary: dict) -> list[str]:
    b = score_summary.get("b_tier") or {}
    if not b.get("rubrics"):
        return ["**B-tier (LLM judge):** not run (set `b_tier.enabled: true` in config + export `ANTHROPIC_API_KEY`)", ""]

    lines = [f"**B-tier composite:** {b.get('composite', 0):.2f} / 10", ""]
    lines.append("**Per-rubric averages:**")
    lines.append("")
    lines.append("| Rubric | Score | Δ vs prior 5 | Flagged |")
    lines.append("| --- | --- | --- | --- |")
    deltas = b.get("deltas_vs_prior_window") or {}
    flagged = b.get("flagged_drops") or {}
    for rubric, score in sorted((b.get("rubrics") or {}).items()):
        delta = deltas.get(rubric, 0)
        delta_s = f"{delta:+.2f}" if delta else "—"
        flag = "⚠ flagged" if rubric in flagged else ""
        lines.append(f"| `{rubric}` | {score:.2f} | {delta_s} | {flag} |")
    lines.append("")
    return lines


def _format_supplementary(run_dir: Path) -> list[str]:
    """Pull in role discovery / permission matrix / adversarial / crawler if present."""
    lines: list[str] = []

    roles_path = run_dir / "roles.yaml"
    if roles_path.exists():
        roles_lines = roles_path.read_text().splitlines()
        n_roles = sum(1 for ln in roles_lines if ln.startswith("  ") and ln.endswith(":"))
        lines.append(f"- Role discovery: `{roles_path.name}` written ({n_roles} roles inventoried)")

    perm = _safe_load(run_dir / "permission_matrix.json")
    if perm:
        lines.append(
            f"- Permission matrix: `{perm.get('total_cells', 0)} cells`, "
            f"`{perm.get('leaked_cells', 0)} leaked` "
            f"({'pass' if perm.get('passed') else 'FAIL'})"
        )

    coverage = _safe_load(run_dir / "coverage.json")
    if coverage:
        n_pages = sum(len(v) for v in coverage.values() if isinstance(v, dict) and "_error" not in v)
        n_passed = sum(
            sum(1 for d in v.values() if isinstance(d, dict) and d.get("passed"))
            for v in coverage.values() if isinstance(v, dict) and "_error" not in v
        )
        lines.append(f"- Crawler coverage: `{n_passed}/{n_pages}` pages passed baseline checks")

    for adv in ("fuzz", "race", "chaos", "permission_escalation"):
        data = _safe_load(run_dir / f"{adv}.json")
        if data:
            lines.append(
                f"- Adversarial `{adv}`: "
                f"`{data.get('leaked_count', '?')}` leaks across "
                f"`{data.get('total_attempts') or data.get('total_cells') or data.get('total_scenarios') or '?'}` cells "
                f"({'pass' if data.get('passed') else 'FAIL'})"
            )

    judge = _safe_load(run_dir / "judge.json")
    if judge:
        lines.append(f"- B-tier judge: `{len(judge.get('judgments') or [])}` judgments rendered")

    candidates_dir = BENCH_ROOT / "candidates"
    if candidates_dir.exists():
        n_candidates = sum(1 for _ in candidates_dir.rglob("*.yaml"))
        if n_candidates:
            lines.append(f"- Candidates queue: `{n_candidates}` awaiting `/bench triage`")

    if not lines:
        return []
    return ["", "## Supplementary outputs", ""] + lines + [""]


def render_markdown(run_dir: Path) -> str:
    scorecard = _safe_load(run_dir / "scorecard.json")
    score_summary = _safe_load(run_dir / "score_summary.json")
    if not scorecard:
        return f"# bench run {run_dir.name}\n\n_no scorecard.json — run incomplete?_\n"

    a = scorecard.get("a_tier", {}) or {}
    overall = "✅ PASS" if a.get("rate", 0) >= 1.0 else "❌ FAIL"

    lines: list[str] = [
        f"# Bench Run Report — `{run_dir.name}`",
        "",
        f"**Verdict:** {overall}  ",
        f"**Target:** `{scorecard.get('target')}` ({scorecard.get('base_url')})  ",
        f"**Started:** {scorecard.get('started_utc')}",
        "",
        "---",
        "",
    ]

    lines.extend(_format_section_header("Summary"))
    lines.extend(_format_a_tier_summary(scorecard))
    lines.extend(_format_b_tier_summary(score_summary))
    lines.extend(_format_supplementary(run_dir))

    lines.extend(_format_section_header("All scenarios"))
    for s in sorted(scorecard.get("scenarios") or [], key=lambda s: (not s["passed"], s["scenario_id"])):
        lines.extend(_format_scenario(s, str(run_dir.relative_to(REPO_ROOT))))

    lines.extend([
        "---",
        "",
        "## Artifacts",
        "",
        f"- Scorecard JSON: [`scorecard.json`](scorecard.json)",
        f"- Score summary: [`score_summary.json`](score_summary.json)",
        f"- Screenshots: [`screenshots/`](screenshots/)",
        f"- Captured page text: [`text/`](text/)",
        "",
        "Run history index: [`../INDEX.json`](../INDEX.json)",
        "",
    ])

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render human-readable bench report")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--run-dir", default=None)
    args = parser.parse_args(argv)

    if args.run_dir:
        run_dir = Path(args.run_dir)
    elif args.run_id:
        run_dir = HISTORY_DIR / args.run_id
    else:
        # Most recent run.
        runs = [p for p in HISTORY_DIR.iterdir() if p.is_dir() and (p / "scorecard.json").exists()]
        if not runs:
            print("[report] no runs in history", file=sys.stderr)
            return 2
        run_dir = sorted(runs)[-1]

    if not run_dir.exists():
        print(f"[report] run-dir not found: {run_dir}", file=sys.stderr)
        return 2

    md = render_markdown(run_dir.resolve())
    out_path = run_dir / "report.md"
    out_path.write_text(md, encoding="utf-8")
    try:
        rel = out_path.resolve().relative_to(REPO_ROOT)
        print(f"[report] {rel}")
    except ValueError:
        print(f"[report] {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
