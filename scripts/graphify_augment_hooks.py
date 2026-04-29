#!/usr/bin/env python3
"""Augment graphify-out/graph.json with edges for Frappe hooks.py string dispatches.

Frappe wires `permission_query_conditions`, `doc_events`, `scheduler_events`,
`on_session_creation`, `after_install`, etc. via string references like
"mrvtools.mrvtools.doctype.approved_user.approved_user.get_query_conditions".
The graphify AST extractor can't follow these strings, so the resulting graph
is missing the most architecturally important edges in any Frappe codebase.

This script reads each hooks.py (AST-parsed, comments ignored), resolves the
string references to existing nodes in graph.json, and appends edges marked
EXTRACTED with `augmented: true` so the script is re-runnable without stacking
duplicates.

Usage:
    python3 scripts/graphify_augment_hooks.py
"""
import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GRAPH_PATH = REPO_ROOT / "graphify-out" / "graph.json"

# Hook keys whose values are Python dotted-path strings we can resolve.
# Each tuple is (key, shape, edge-relation-template).
# shape: 'str' | 'dict_str' | 'dict_dict_str_or_list' | 'dict_list' | 'list'
HOOK_KEYS = [
    ("after_install",               "str",                  "wires_after_install"),
    ("on_session_creation",         "str",                  "wires_session_creation"),
    ("before_install",              "str",                  "wires_before_install"),
    ("permission_query_conditions", "dict_str",             "wires_permission_query"),
    ("has_permission",              "dict_str",             "wires_has_permission"),
    ("override_doctype_class",      "dict_str",             "wires_override_class"),
    ("doc_events",                  "dict_dict_str_or_list","wires_doc_event"),
    ("scheduler_events",            "dict_list",            "wires_scheduler"),
    ("auth_hooks",                  "list",                 "wires_auth_hook"),
    ("override_whitelisted_methods","dict_str",             "wires_override_whitelist"),
]


def parse_hooks_file(path: Path) -> dict:
    """Return module-level name -> ast.AST node value for every assignment."""
    tree = ast.parse(path.read_text())
    out = {}
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            for tgt in stmt.targets:
                if isinstance(tgt, ast.Name):
                    out[tgt.id] = stmt.value
    return out


def as_str(node) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def as_dict_items(node):
    if not isinstance(node, ast.Dict):
        return None
    out = []
    for k, v in zip(node.keys, node.values):
        ks = as_str(k)
        if ks is not None:
            out.append((ks, v))
    return out


def as_list_items(node):
    if not isinstance(node, ast.List):
        return None
    return list(node.elts)


def extract_dispatches(assignments: dict, hooks_src: str) -> list[dict]:
    """Pull every (relation, context, target_dotted_path) from hook assignments."""
    out = []
    for key, shape, rel in HOOK_KEYS:
        node = assignments.get(key)
        if node is None:
            continue

        if shape == "str":
            s = as_str(node)
            if s:
                out.append({"relation": rel, "context": None, "target": s})

        elif shape == "dict_str":
            for k, v in as_dict_items(node) or []:
                s = as_str(v)
                if s:
                    out.append({"relation": rel, "context": k, "target": s})

        elif shape == "dict_dict_str_or_list":
            for doctype, inner in as_dict_items(node) or []:
                for event, target_node in as_dict_items(inner) or []:
                    targets = as_list_items(target_node) or [target_node]
                    for tn in targets:
                        s = as_str(tn)
                        if s:
                            out.append({"relation": f"{rel}_{event}",
                                        "context": doctype, "target": s})

        elif shape == "dict_list":
            for schedule, inner in as_dict_items(node) or []:
                for tn in as_list_items(inner) or []:
                    s = as_str(tn)
                    if s:
                        out.append({"relation": f"{rel}_{schedule}",
                                    "context": None, "target": s})

        elif shape == "list":
            for tn in as_list_items(node) or []:
                s = as_str(tn)
                if s:
                    out.append({"relation": rel, "context": None, "target": s})

    for d in out:
        d["hooks_src"] = hooks_src
    return out


def find_node(nodes_by_src_label: dict, target_path: str) -> str | None:
    """Resolve "mrvtools.mrvtools.doctype.x.x.fn_name" to a node id.

    Strategy: split into module + function name. Look up nodes whose
    source_file ends with the module-path-as-file and whose label is the bare
    function name (graphify writes both "fn_name()" and ".fn_name()" depending
    on whether it's top-level or a method).
    """
    parts = target_path.split(".")
    if len(parts) < 2:
        return None
    fn_name = parts[-1]
    expected_file_suffix = "/".join(parts[:-1]) + ".py"

    for (src, label), nid in nodes_by_src_label.items():
        if not src.endswith(expected_file_suffix):
            continue
        bare = label.rstrip("()").lstrip(".")
        if bare == fn_name:
            return nid
    return None


def main():
    if not GRAPH_PATH.exists():
        sys.exit(f"ERROR: {GRAPH_PATH} not found. Run /graphify first.")

    graph = json.loads(GRAPH_PATH.read_text())

    # Strip prior augmented edges (idempotency)
    before = len(graph.get("links", []))
    graph["links"] = [e for e in graph.get("links", []) if not e.get("augmented")]
    stripped = before - len(graph["links"])

    nodes_by_src_label = {(n.get("source_file", ""), n.get("label", "")): n["id"]
                          for n in graph.get("nodes", [])}
    hooks_node_by_src = {n.get("source_file"): n["id"]
                         for n in graph.get("nodes", [])
                         if n.get("source_file", "").endswith("hooks.py")}

    hook_files = sorted(REPO_ROOT.glob("*/hooks.py"))
    if not hook_files:
        sys.exit("ERROR: no hooks.py files found at depth 1.")

    added = 0
    unresolved: list[tuple[str, str]] = []
    by_app: dict[str, int] = {}

    for hooks_file in hook_files:
        rel = hooks_file.relative_to(REPO_ROOT).as_posix()
        hooks_node_id = hooks_node_by_src.get(rel)
        if not hooks_node_id:
            print(f"  warn: {rel} has no node in graph (graphify didn't see it)")
            continue

        assignments = parse_hooks_file(hooks_file)
        for disp in extract_dispatches(assignments, rel):
            target_id = find_node(nodes_by_src_label, disp["target"])
            if not target_id:
                unresolved.append((rel, disp["target"]))
                continue
            edge = {
                "source": hooks_node_id,
                "target": target_id,
                "relation": disp["relation"],
                "confidence": "EXTRACTED",
                "confidence_score": 1.0,
                "source_file": rel,
                "weight": 1.0,
                "augmented": True,
            }
            if disp["context"]:
                edge["context"] = disp["context"]
            graph["links"].append(edge)
            added += 1
            by_app[rel] = by_app.get(rel, 0) + 1

    GRAPH_PATH.write_text(json.dumps(graph, indent=2))

    print(f"Stripped {stripped} prior augmented edges.")
    print(f"Added {added} hook-dispatch edges:")
    for app, n in by_app.items():
        print(f"  {n:3d}  {app}")
    if unresolved:
        print(f"\nUnresolved targets ({len(unresolved)}):")
        for src, t in unresolved:
            print(f"  {src} -> {t}")


if __name__ == "__main__":
    main()
