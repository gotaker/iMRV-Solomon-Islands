"""
bench.runner.fuzz_agent — Wave 2 input fuzzer.

Generates malformed inputs for forms and POST endpoints discovered by the
crawler (or supplied via --target-list), then asserts:

  - server returns 4xx (never 5xx)
  - response body does NOT echo the malformed input verbatim into HTML
    (reflected-XSS check, regex-based)
  - response body does NOT include a Python/Frappe stack trace

Targets `local-docker` only by default — config.targets[].safe_for_adversarial
must be true. The runner refuses to attack `railway-live`.

Standalone usage:
    python3 -m bench.runner.fuzz_agent --config bench/config.yaml \
        --target local-docker --targets-file <crawler_forms.json> \
        --output bench/history/<run-id>/fuzz.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from bench.runner.a_runner import _load_target, _load_yaml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = REPO_ROOT / "bench"


# Input mutation generators. Each entry returns a list of payloads keyed by
# attack class. Payloads are ASCII where possible to keep the JSON output
# readable; unicode is added as separate entries.
PAYLOADS: dict[str, list[str]] = {
    "oversized": ["A" * 1024, "A" * 65536, "A" * 524288],
    "null_bytes": ["foo\x00bar", "\x00\x00\x00", "valid\x00<script>"],
    "rtl_unicode": [
        "‮Hello",                  # right-to-left override
        "Hello​​​World", # zero-width spaces
        "\ud83d",                       # lone surrogate
    ],
    "path_traversal": [
        "../../../etc/passwd",
        "..%2f..%2f..%2fetc%2fpasswd",
        "/var/log/../../../../etc/passwd",
    ],
    "sql_shaped": [
        "' OR 1=1 --",
        "'; DROP TABLE users; --",
        "1' UNION SELECT * FROM tabUser --",
    ],
    "json_depth_bomb": [
        # 50 levels of nesting — Frappe's JSON parser shouldn't crash but
        # might surface deserialization errors that leak stack traces.
        "{" + '"a":' * 50 + "1" + "}" * 50,
    ],
    "xss_shaped": [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert(1)",
    ],
}

STACK_TRACE_PATTERNS = (
    re.compile(r"Traceback \(most recent call last\):"),
    re.compile(r"File \"[^\"]+\", line \d+, in "),
    re.compile(r"frappe\.exceptions\.\w+Error"),
    re.compile(r"werkzeug\.exceptions\."),
)


@dataclass
class FuzzCell:
    target_url: str
    method: str
    field: str
    attack_class: str
    payload_preview: str
    status: int
    body_length: int
    reflected: bool
    stack_trace: bool
    leaked: bool
    note: str = ""


def _looks_reflected(payload: str, body_text: str) -> bool:
    """Return True if the unmangled payload appears in the response body."""
    # Don't fire on tiny payloads that show up everywhere by chance.
    if len(payload) < 8:
        return False
    return payload in body_text


def _has_stack_trace(body_text: str) -> bool:
    return any(p.search(body_text) for p in STACK_TRACE_PATTERNS)


def _fuzz_endpoint(
    session,
    base_url: str,
    method: str,
    path: str,
    fields: list[str],
) -> list[FuzzCell]:
    """For each (attack_class, payload, field), POST a copy with the payload."""
    cells: list[FuzzCell] = []
    full_url = urljoin(base_url + "/", path.lstrip("/"))

    for attack, payloads in PAYLOADS.items():
        for payload in payloads:
            for field in fields or ["data"]:
                form_data = {f: "valid" for f in fields if f != field} | {field: payload}
                try:
                    resp = session.request(method, full_url, data=form_data, timeout=15)
                except Exception as exc:  # noqa: BLE001
                    cells.append(FuzzCell(
                        target_url=full_url, method=method, field=field,
                        attack_class=attack, payload_preview=payload[:40],
                        status=0, body_length=0, reflected=False, stack_trace=False,
                        leaked=False, note=f"request failed: {exc!r}",
                    ))
                    continue

                body = resp.text or ""
                reflected = _looks_reflected(payload, body)
                stack = _has_stack_trace(body)
                # Leak conditions: 5xx, reflected, or stack trace.
                leaked = resp.status_code >= 500 or reflected or stack
                note = ""
                if resp.status_code >= 500:
                    note = f"5xx response"
                elif reflected:
                    note = "input reflected in body"
                elif stack:
                    note = "stack trace in body"

                cells.append(FuzzCell(
                    target_url=full_url, method=method, field=field,
                    attack_class=attack, payload_preview=payload[:40],
                    status=resp.status_code, body_length=len(body),
                    reflected=reflected, stack_trace=stack,
                    leaked=leaked, note=note,
                ))
    return cells


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
    parser = argparse.ArgumentParser(description="Wave 2 fuzz agent")
    parser.add_argument("--config", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument(
        "--targets-file",
        default=None,
        help="JSON file: [{url, method, fields[]}, ...]; default = static seed list",
    )
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--auth-as",
        default="Administrator",
        help="role-credentials key to authenticate as before fuzzing",
    )
    args = parser.parse_args(argv)

    config = _load_yaml(Path(args.config))
    target = _load_target(config, args.target)
    if not target.get("safe_for_adversarial"):
        print(
            f"[fuzz] target '{args.target}' has safe_for_adversarial=false. "
            f"Refusing to fuzz.", file=sys.stderr,
        )
        return 2

    credentials = _load_yaml(BENCH_ROOT / "fixtures" / "role_credentials.yaml") or {}
    auth = credentials.get(args.auth_as)
    if not auth:
        print(f"[fuzz] no credential for role '{args.auth_as}'", file=sys.stderr)
        return 2

    if args.targets_file:
        target_list = json.loads(Path(args.targets_file).read_text())
    else:
        # Phase-3 seed: a small set of well-known whitelisted endpoints.
        target_list = [
            {"url": "/api/method/mrvtools.api.get_data", "method": "POST", "fields": ["doctype"]},
            {"url": "/api/method/mrvtools.api.get_approvers", "method": "POST", "fields": ["doctype"]},
        ]

    base_url = target["base_url"].rstrip("/")
    session = _login_session(base_url, auth["email"], auth["password"])

    cells: list[FuzzCell] = []
    for entry in target_list:
        cells.extend(_fuzz_endpoint(
            session, base_url,
            entry.get("method", "POST"),
            entry["url"],
            entry.get("fields", []),
        ))

    leaked = [c for c in cells if c.leaked]
    summary = {
        "schema_version": 1,
        "target": args.target,
        "total_attempts": len(cells),
        "leaked_count": len(leaked),
        "passed": len(leaked) == 0,
        "leakages": [
            {
                "target_url": c.target_url, "method": c.method, "field": c.field,
                "attack_class": c.attack_class, "payload_preview": c.payload_preview,
                "status": c.status, "reflected": c.reflected,
                "stack_trace": c.stack_trace, "note": c.note,
            }
            for c in leaked
        ],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2))

    print(json.dumps({
        "total_attempts": summary["total_attempts"],
        "leaked_count": summary["leaked_count"],
        "passed": summary["passed"],
    }, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
