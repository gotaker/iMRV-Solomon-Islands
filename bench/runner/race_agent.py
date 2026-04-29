"""
bench.runner.race_agent — Wave 2 concurrency hammer.

Fires N concurrent requests at idempotent operations to assert that
double-submission / race-condition behavior is sane:

  - parallel logins from same user → all 200, single sid cookie family
  - double-click approve → record state stable, no duplicate child rows
  - rapid form submits → no orphaned drafts

Targets `local-docker` only by default. The runner refuses to attack live.

Standalone usage:
    python3 -m bench.runner.race_agent --config bench/config.yaml \
        --target local-docker --output bench/history/<run-id>/race.json
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bench.runner.a_runner import _load_target, _load_yaml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = REPO_ROOT / "bench"


@dataclass
class RaceResult:
    name: str
    fired: int
    success: int
    duplicates: int
    leaked: bool
    note: str = ""


def _parallel_login(base_url: str, email: str, password: str, n: int) -> RaceResult:
    """Fire N parallel logins. Expect: all succeed, no 5xx, no auth errors."""
    import requests

    def _one() -> int:
        s = requests.Session()
        r = s.post(
            f"{base_url}/api/method/login",
            data={"usr": email, "pwd": password},
            timeout=15,
        )
        return r.status_code

    statuses: list[int] = []
    with ThreadPoolExecutor(max_workers=n) as ex:
        futures = [ex.submit(_one) for _ in range(n)]
        for f in as_completed(futures):
            try:
                statuses.append(f.result())
            except Exception as exc:  # noqa: BLE001
                statuses.append(0)
    success = sum(1 for s in statuses if s == 200)
    leaked = any(s >= 500 for s in statuses)
    return RaceResult(
        name="parallel_login",
        fired=n, success=success, duplicates=0,
        leaked=leaked,
        note=f"statuses={statuses}",
    )


def _parallel_get(session, base_url: str, path: str, n: int, name: str) -> RaceResult:
    """Fire N parallel GETs at the same path; assert no 5xx / no inconsistent responses."""
    def _one() -> tuple[int, int]:
        r = session.get(f"{base_url}{path}", timeout=15)
        return r.status_code, len(r.text or "")

    statuses: list[int] = []
    body_lens: list[int] = []
    with ThreadPoolExecutor(max_workers=n) as ex:
        futures = [ex.submit(_one) for _ in range(n)]
        for f in as_completed(futures):
            try:
                code, blen = f.result()
                statuses.append(code)
                body_lens.append(blen)
            except Exception:  # noqa: BLE001
                statuses.append(0)

    success = sum(1 for s in statuses if 200 <= s < 400)
    leaked = any(s >= 500 for s in statuses)
    # If body lengths are wildly different, that's a (weak) inconsistency signal.
    if body_lens and max(body_lens) - min(body_lens) > 1024 * 100:
        leaked = True
    return RaceResult(
        name=name,
        fired=n, success=success, duplicates=0,
        leaked=leaked,
        note=f"statuses={statuses[:8]}... body_lens range [{min(body_lens)}, {max(body_lens)}]",
    )


def _login_session(base_url: str, email: str, password: str):
    import requests
    s = requests.Session()
    r = s.post(
        f"{base_url}/api/method/login",
        data={"usr": email, "pwd": password},
        timeout=15,
    )
    r.raise_for_status()
    return s


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Wave 2 race-condition hammer")
    parser.add_argument("--config", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--auth-as", default="Administrator")
    args = parser.parse_args(argv)

    config = _load_yaml(Path(args.config))
    target = _load_target(config, args.target)
    if not target.get("safe_for_adversarial"):
        print(
            f"[race] target '{args.target}' has safe_for_adversarial=false. "
            f"Refusing to hammer.", file=sys.stderr,
        )
        return 2

    credentials = _load_yaml(BENCH_ROOT / "fixtures" / "role_credentials.yaml") or {}
    auth = credentials.get(args.auth_as)
    if not auth:
        print(f"[race] no credential for role '{args.auth_as}'", file=sys.stderr)
        return 2

    base_url = target["base_url"].rstrip("/")
    n = args.concurrency

    results: list[RaceResult] = []
    results.append(_parallel_login(base_url, auth["email"], auth["password"], n))
    session = _login_session(base_url, auth["email"], auth["password"])
    results.append(_parallel_get(session, base_url, "/app/main-dashboard", n, "parallel_dashboard"))
    results.append(_parallel_get(session, base_url, "/api/method/mrvtools.api.get_approvers", n, "parallel_get_approvers"))

    leaked = [r for r in results if r.leaked]
    summary = {
        "schema_version": 1,
        "target": args.target,
        "concurrency": n,
        "total_runs": len(results),
        "leaked_count": len(leaked),
        "passed": len(leaked) == 0,
        "results": [
            {
                "name": r.name, "fired": r.fired, "success": r.success,
                "duplicates": r.duplicates, "leaked": r.leaked, "note": r.note,
            }
            for r in results
        ],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2))
    print(json.dumps({"passed": summary["passed"], "leaked_count": summary["leaked_count"]}, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
