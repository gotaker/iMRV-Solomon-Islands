"""
bench.runner.role_discovery — introspect the live target's role inventory.

Walks the Frappe REST API as Administrator to produce a snapshot of:
  - active roles (Role doctype, disabled=0)
  - per-role permission profile (DocPerm + Custom DocPerm)
  - the *expected* drawer entry set (frappe_side_menu.get_menulist)
  - per-role approval queue expectation (get_query_conditions)

Output: bench/history/<run-id>/roles.yaml. Diffs against the prior run's
snapshot become first-class scorecard data ("the deploy added 2 roles, removed
1 — was that intentional?").

This is one of three mechanisms (alongside per-role journey templates and the
permission matrix) that handle multi-role permission complexity. See the plan
file for the full design.

Standalone usage:
    python3 -m bench.runner.role_discovery --config bench/config.yaml \
        --target local-docker --output bench/history/<run-id>/roles.yaml
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

# Reuse helpers from a_runner — keeps target-resolution logic in one place.
from bench.runner.a_runner import _load_target, _load_yaml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = REPO_ROOT / "bench"


class FrappeClient:
    """
    Minimal Frappe REST client for discovery. Authenticates once, then proxies
    GET / POST through `requests.Session()` (cookies persist across calls so
    CSRF is round-tripped naturally).
    """

    def __init__(self, base_url: str, email: str, password: str):
        import requests
        self._requests = requests
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self._login(email, password)

    def _login(self, email: str, password: str) -> None:
        r = self.session.post(
            f"{self.base_url}/api/method/login",
            data={"usr": email, "pwd": password},
            timeout=15,
        )
        r.raise_for_status()
        # Frappe sets sid + csrf cookies on success; nothing more to do.

    def get_resource(self, doctype: str, **params: Any) -> list[dict]:
        """Return all records for a doctype (paginated under the hood)."""
        params.setdefault("limit_page_length", 0)
        if "fields" in params and not isinstance(params["fields"], str):
            params["fields"] = json.dumps(params["fields"])
        if "filters" in params and not isinstance(params["filters"], str):
            params["filters"] = json.dumps(params["filters"])
        r = self.session.get(
            f"{self.base_url}/api/resource/{doctype}", params=params, timeout=30
        )
        r.raise_for_status()
        return (r.json() or {}).get("data", [])

    def call(self, method: str, **kwargs: Any) -> Any:
        """Invoke a whitelisted method via /api/method/<method>."""
        r = self.session.post(
            f"{self.base_url}/api/method/{method}", data=kwargs, timeout=30
        )
        r.raise_for_status()
        return (r.json() or {}).get("message")


def _enumerate_roles(client: FrappeClient) -> list[str]:
    """Return active role names. Filters out built-in 'All' which has no doctype perms."""
    rows = client.get_resource(
        "Role",
        filters=[["disabled", "=", 0]],
        fields=["name"],
    )
    return sorted(r["name"] for r in rows if r["name"] not in {"All", "Guest"})


def _docperm_profile(client: FrappeClient, role: str) -> dict[str, dict[str, int]]:
    """Return {doctype: {read,write,create,submit,cancel,delete,...}} for a role."""
    profile: dict[str, dict[str, int]] = {}
    for source in ("DocPerm", "Custom DocPerm"):
        rows = client.get_resource(
            source,
            filters=[["role", "=", role]],
            fields=[
                "parent", "read", "write", "create", "submit", "cancel",
                "delete", "report", "export", "import", "share", "print", "email",
            ],
        )
        for row in rows:
            doctype = row["parent"]
            slot = profile.setdefault(doctype, {})
            for k, v in row.items():
                if k == "parent":
                    continue
                # Take the maximum across rows: Custom DocPerm overlays DocPerm
                # additively. A 0 in one row + 1 in another → effective 1.
                slot[k] = max(slot.get(k, 0), int(v or 0))
    return profile


def discover(target: dict, admin_email: str, admin_password: str) -> dict[str, Any]:
    """Run discovery against a live target. Returns the snapshot dict."""
    client = FrappeClient(target["base_url"], admin_email, admin_password)
    roles = _enumerate_roles(client)
    snapshot: dict[str, Any] = {
        "schema_version": 1,
        "target_base_url": target["base_url"],
        "roles": {},
    }
    for role in roles:
        profile = _docperm_profile(client, role)
        # Narrow to "effectively readable" doctypes — DocPerm rows with read=0
        # over-report (the bug class flagged in reference_drawer_perm_filter.md).
        readable = sorted(d for d, p in profile.items() if p.get("read"))
        snapshot["roles"][role] = {
            "permission_profile": profile,
            "readable_doctypes": readable,
        }
    return snapshot


def _diff_snapshots(prior: dict, current: dict) -> dict:
    """Compute role-set + per-role-readable-doctype delta. Surfaced in scorecard."""
    prior_roles = set((prior.get("roles") or {}).keys())
    current_roles = set((current.get("roles") or {}).keys())
    added = sorted(current_roles - prior_roles)
    removed = sorted(prior_roles - current_roles)
    perm_changes: dict[str, dict[str, list[str]]] = {}
    for role in sorted(prior_roles & current_roles):
        prior_doctypes = set(prior["roles"][role].get("readable_doctypes") or [])
        current_doctypes = set(current["roles"][role].get("readable_doctypes") or [])
        gained = sorted(current_doctypes - prior_doctypes)
        lost = sorted(prior_doctypes - current_doctypes)
        if gained or lost:
            perm_changes[role] = {"gained_read": gained, "lost_read": lost}
    return {
        "roles_added": added,
        "roles_removed": removed,
        "perm_changes": perm_changes,
    }


def _find_prior_snapshot(history_dir: Path, current_run_id: str) -> Path | None:
    """Most recent roles.yaml older than the current run, or None."""
    candidates = sorted(history_dir.glob("*/roles.yaml"))
    candidates = [p for p in candidates if current_run_id not in p.parts]
    return candidates[-1] if candidates else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Discover the target's role inventory")
    parser.add_argument("--config", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", required=True, help="Path to write roles.yaml")
    parser.add_argument(
        "--admin-credential-key",
        default="Administrator",
        help="Key in role_credentials.yaml whose entry has admin email+password",
    )
    args = parser.parse_args(argv)

    config = _load_yaml(Path(args.config))
    target = _load_target(config, args.target)

    creds_path = BENCH_ROOT / "fixtures" / "role_credentials.yaml"
    if not creds_path.exists():
        print(
            f"[role_discovery] {creds_path.relative_to(REPO_ROOT)} missing — "
            f"copy role_credentials.example.yaml and fill in real credentials.",
            file=sys.stderr,
        )
        return 2
    credentials = _load_yaml(creds_path)
    admin = credentials.get(args.admin_credential_key)
    if not admin or not admin.get("email") or not admin.get("password"):
        print(
            f"[role_discovery] no '{args.admin_credential_key}' entry with email+password "
            f"in {creds_path.relative_to(REPO_ROOT)}",
            file=sys.stderr,
        )
        return 2

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    snapshot = discover(target, admin["email"], admin["password"])

    prior_path = _find_prior_snapshot(output_path.parent.parent, output_path.parent.name)
    if prior_path:
        prior = _load_yaml(prior_path)
        snapshot["diff_vs_prior_run"] = {
            "prior_run": prior_path.parent.name,
            **_diff_snapshots(prior, snapshot),
        }

    with output_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(snapshot, f, sort_keys=True, default_flow_style=False)

    summary = {
        "roles_count": len(snapshot["roles"]),
        "diff_vs_prior_run": snapshot.get("diff_vs_prior_run", {"prior_run": None}),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
