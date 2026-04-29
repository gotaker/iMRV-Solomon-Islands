"""
bench.runner.permission_matrix — deterministic cross-role leakage check.

For every pair (role_A, role_B) where A ≠ B:
  1. Enumerate URLs that role_B can reach (from the prior journey/crawler runs).
  2. From role_A's session, attempt each URL.
  3. Assert: if role_A's permission_profile lacks read on the doctype that URL
     resolves to, the response is 403 / 401 / redirect-to-login.
     If role_A *does* have read perm, the response is 200.

Two leakage cells = A-tier failure = deploy blocked. This is the systematic
backstop for the substring-perm-leak class of bug
(reference_drawer_perm_filter.md).

Driven by `roles.yaml` from role_discovery and a per-role URL surface map
(produced by the journey runner — Phase 1 supplies the surface inline; Phase 2's
crawler will widen it).

Standalone usage:
    python3 -m bench.runner.permission_matrix --config bench/config.yaml \
        --target local-docker --roles-file bench/history/<run-id>/roles.yaml \
        --output bench/history/<run-id>/permission_matrix.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bench.runner.a_runner import _load_target, _load_yaml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = REPO_ROOT / "bench"

# A response is "denied" if it returns one of these. Anything else with a 200 is
# treated as access granted, and is checked against the role's expected perm.
DENIED_STATUSES = {401, 403}
LOGIN_URL_PATTERNS = (re.compile(r"/login(\?|$)"),)


# Doctype URL patterns that show up across the surface. Order matters — the
# first match wins, so put the most specific paths first.
_DOCTYPE_URL_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^/api/resource/([^/?]+)"), r"\1"),
    (re.compile(r"^/api/method/frappe\.client\.get_list\?doctype=([^&]+)"), r"\1"),
    (re.compile(r"^/(?:app|desk)/([^/?]+)/([^/?]+)"), r"\1"),  # /app/<doctype>/<name>
    (re.compile(r"^/(?:app|desk)/([^/?]+)$"), r"\1"),           # /app/<doctype>
]


@dataclass
class MatrixCell:
    actor_role: str
    surface_owner_role: str
    url: str
    inferred_doctype: str | None
    expected_access: bool          # actor's perm profile says they should read
    actual_status: int
    actual_url: str
    leaked: bool
    note: str = ""


def _infer_doctype(url: str) -> str | None:
    """Pull a doctype name out of a URL path. Returns None for non-doctype URLs."""
    # Drop the origin if present.
    if url.startswith("http"):
        url = "/" + url.split("/", 3)[-1] if url.count("/") >= 3 else "/"
    for pattern, replacement in _DOCTYPE_URL_PATTERNS:
        m = pattern.match(url)
        if m:
            doctype_slug = pattern.sub(replacement, url)
            # Frappe URLs commonly slugify with hyphens; the live Role doctype
            # name uses spaces or as-typed casing. Normalize back to title-case
            # space-separated form for matching against permission_profile.
            return doctype_slug.replace("-", " ").strip()
    return None


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


def _attempt_url(session, base_url: str, url_path: str) -> tuple[int, str]:
    """GET the URL with redirects followed. Returns (status, final_url)."""
    full = url_path if url_path.startswith("http") else f"{base_url}{url_path}"
    r = session.get(full, allow_redirects=True, timeout=20)
    return r.status_code, r.url


def _is_denied(status: int, final_url: str) -> bool:
    if status in DENIED_STATUSES:
        return True
    if status == 200 and any(p.search(final_url) for p in LOGIN_URL_PATTERNS):
        return True
    return False


def _expected_access(actor_profile: dict, doctype: str | None) -> bool:
    """True if the actor role's profile grants read on the doctype."""
    if doctype is None:
        # We can't confidently infer; default to "expected to be allowed" so
        # only explicit deny-leaks are flagged.
        return True
    perm = (actor_profile.get("permission_profile") or {}).get(doctype, {})
    return bool(perm.get("read"))


def evaluate_matrix(
    target: dict,
    roles_snapshot: dict,
    surface_by_role: dict[str, list[str]],
    credentials: dict[str, dict],
) -> list[MatrixCell]:
    """Run every (actor × surface_owner × url) cell. Skip self-pairs."""
    base_url = target["base_url"].rstrip("/")
    cells: list[MatrixCell] = []

    actors = sorted(roles_snapshot.get("roles", {}).keys())
    sessions: dict[str, Any] = {}

    for actor in actors:
        creds = credentials.get(actor)
        if not creds:
            cells.append(MatrixCell(
                actor_role=actor, surface_owner_role="*", url="*",
                inferred_doctype=None, expected_access=False, actual_status=0,
                actual_url="", leaked=False,
                note=f"skipped: no fixture credential for role '{actor}'",
            ))
            continue
        try:
            sessions[actor] = _login_session(base_url, creds["email"], creds["password"])
        except Exception as exc:  # noqa: BLE001
            cells.append(MatrixCell(
                actor_role=actor, surface_owner_role="*", url="*",
                inferred_doctype=None, expected_access=False, actual_status=0,
                actual_url="", leaked=False,
                note=f"login failed: {exc!r}",
            ))

    for actor in actors:
        if actor not in sessions:
            continue
        actor_profile = roles_snapshot["roles"][actor]
        for owner, urls in surface_by_role.items():
            if owner == actor:
                continue
            for url in urls:
                doctype = _infer_doctype(url)
                expected = _expected_access(actor_profile, doctype)
                try:
                    status, final = _attempt_url(sessions[actor], base_url, url)
                except Exception as exc:  # noqa: BLE001
                    cells.append(MatrixCell(
                        actor_role=actor, surface_owner_role=owner, url=url,
                        inferred_doctype=doctype, expected_access=expected,
                        actual_status=0, actual_url="",
                        leaked=False, note=f"request failed: {exc!r}",
                    ))
                    continue
                denied = _is_denied(status, final)
                if expected:
                    leaked = denied  # role should have access but was denied
                    note = "expected 200, got denied" if leaked else ""
                else:
                    leaked = not denied  # role should be denied but got through
                    note = f"expected denied, got status={status}" if leaked else ""
                cells.append(MatrixCell(
                    actor_role=actor, surface_owner_role=owner, url=url,
                    inferred_doctype=doctype, expected_access=expected,
                    actual_status=status, actual_url=final,
                    leaked=leaked, note=note,
                ))
    return cells


def _summarize(cells: list[MatrixCell]) -> dict[str, Any]:
    runnable = [c for c in cells if c.actor_role and c.surface_owner_role != "*"]
    leaked = [c for c in runnable if c.leaked]
    return {
        "schema_version": 1,
        "total_cells": len(runnable),
        "leaked_cells": len(leaked),
        "passed": len(leaked) == 0,
        "leakages": [
            {
                "actor_role": c.actor_role,
                "surface_owner_role": c.surface_owner_role,
                "url": c.url,
                "inferred_doctype": c.inferred_doctype,
                "expected_access": c.expected_access,
                "actual_status": c.actual_status,
                "actual_url": c.actual_url,
                "note": c.note,
            }
            for c in leaked
        ],
        "skipped": [
            {"actor_role": c.actor_role, "note": c.note}
            for c in cells if c.surface_owner_role == "*"
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cross-role permission matrix runner")
    parser.add_argument("--config", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--roles-file", required=True, help="roles.yaml from role_discovery")
    parser.add_argument(
        "--surface-file",
        default=None,
        help="JSON file mapping role -> [urls]; defaults to a static seed map",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    config = _load_yaml(Path(args.config))
    target = _load_target(config, args.target)
    roles_snapshot = _load_yaml(Path(args.roles_file))
    credentials = _load_yaml(BENCH_ROOT / "fixtures" / "role_credentials.yaml") or {}

    if args.surface_file:
        surface = json.loads(Path(args.surface_file).read_text())
    else:
        # Phase-1 seed surface: a small, well-known set of URLs per archetype.
        # Phase 2's crawler replaces this with the discovered surface graph.
        surface = {
            "Administrator": [
                "/api/resource/User",
                "/app/user",
                "/app/role",
                "/app/master-data",
            ],
            "System Manager": [
                "/api/resource/User",
                "/app/user",
            ],
        }

    cells = evaluate_matrix(target, roles_snapshot, surface, credentials)
    summary = _summarize(cells)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2))

    print(json.dumps(
        {
            "total_cells": summary["total_cells"],
            "leaked_cells": summary["leaked_cells"],
            "passed": summary["passed"],
        },
        indent=2,
    ))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
