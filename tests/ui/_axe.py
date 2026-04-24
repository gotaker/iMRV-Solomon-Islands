"""axe-core injection + scan helper for Layer 3 design-system tests."""

from __future__ import annotations

import json
from pathlib import Path

AXE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.2/axe.min.js"
AXE_VENDOR = Path(__file__).parent / "vendor" / "axe.min.js"


def inject_axe(page) -> None:
    """Inject axe-core into the current page. Prefer vendored copy, fall back to CDN."""
    if AXE_VENDOR.is_file():
        page.add_script_tag(content=AXE_VENDOR.read_text())
    else:
        page.add_script_tag(url=AXE_CDN)


def axe_scan(page, *, rules: list[str] | None = None) -> dict:
    """Run an axe scan and return the raw result dict.

    Raises `RuntimeError` with a clear message if axe-core fails to inject
    (CDN unreachable, CSP blocking, syntax error in the loaded script).
    This prevents tests from silently passing when the accessibility scan
    didn't actually run.
    """
    inject_axe(page)

    # Post-inject guard — confirm `axe` is actually defined on the page.
    loaded = page.evaluate("() => typeof axe !== 'undefined' && typeof axe.run === 'function'")
    if not loaded:
        raise RuntimeError(
            "axe-core failed to inject on the page (CDN unreachable, CSP blocked the "
            "script tag, or the vendored axe.min.js is corrupt). Scan aborted; do NOT "
            "treat this as a pass. Vendor axe-core to tests/ui/vendor/axe.min.js and retry."
        )

    options = {}
    if rules:
        options["runOnly"] = {"type": "rule", "values": rules}

    raw = page.evaluate(
        "async (opts) => JSON.stringify(await axe.run(document, opts))",
        options,
    )
    if raw is None:
        raise RuntimeError("axe.run() returned undefined — axe may have been evicted by navigation. Scan aborted.")
    return json.loads(raw)


def violations_of(result: dict, rule_id: str) -> list[dict]:
    return [v for v in result.get("violations", []) if v["id"] == rule_id]
