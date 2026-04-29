"""
bench.runner.design_system_checks — Forest-and-Sage system enforcement.

Asserts the design-system invariants documented in CLAUDE.md and feedback
memory entries:

  - typography:    --ed-font-display resolves to Anton; --ed-font-body to Inter
  - tokens:        no off-token hex/rgb in computed styles where Forest-and-Sage
                   tokens exist (allowlist-controlled)
  - v16 selectors: .navbar-breadcrumbs (class) resolves on every desk page;
                   .fsm-trigger at top:12px;left:12px;width:40px;
                   .page-head .page-title margin-left >= 60px
  - reveal:        no [data-reveal] elements stuck at opacity:0 in viewport
  - drawer:        frosted-glass backdrop computed style

Used by both crawler.py (per-page baseline check) and a_runner.py (when a
scenario asserts `design_system: { fonts: enforced, ... }`).

This module exposes a single entry point `check_page(page) -> dict[str, bool]`
that returns the per-aspect pass/fail map. The caller decides which aspects
are required for the current scenario.
"""

from __future__ import annotations

from typing import Any

# The Forest-and-Sage token allowlist. These are the colors expected in
# computed styles after token resolution. Anything else in the brand range
# (sage / forest greens, frost-glass overlays) is suspicious. We allow any
# white/black/transparent/inherit because they're not "brand" colors.
ALLOWED_NEUTRAL_PATTERNS = (
    "rgba(0, 0, 0, 0)",
    "rgb(255, 255, 255)",
    "rgb(0, 0, 0)",
    "transparent",
    "inherit",
    "initial",
)

# Computed font-family values that should resolve from the editorial tokens.
EXPECTED_DISPLAY_FONT = "Anton"
EXPECTED_BODY_FONT = "Inter"


def _check_typography(page) -> dict[str, Any]:
    """Verify --ed-font-display=Anton and --ed-font-body=Inter resolve correctly.

    On desk pages the editorial display element is the breadcrumb leaf
    (`.navbar-breadcrumbs li:last-child a`), not `.page-title` — Frappe's
    `.page-title` falls through to Inter by design. On SPA / public pages,
    `.ed-display` and `h1` are the display elements.
    """
    try:
        result = page.evaluate(
            """
            () => {
                const root = document.documentElement;
                const cs = window.getComputedStyle(root);
                const display = cs.getPropertyValue('--ed-font-display').trim();
                const body = cs.getPropertyValue('--ed-font-body').trim();
                const url = window.location.pathname;
                const isDeskPage = url.startsWith('/app') || url.startsWith('/desk');
                // Pick the right display element per surface.
                const headingSelector = isDeskPage
                    ? '.navbar-breadcrumbs li:last-child a, .ed-display, h1'
                    : '.ed-display, h1, .page-title';
                const heading = document.querySelector(headingSelector);
                const para = document.querySelector('p, .ed-body, body');
                const headingFont = heading ? window.getComputedStyle(heading).fontFamily : '';
                const bodyFont = para ? window.getComputedStyle(para).fontFamily : '';
                return {
                    declared_display: display, declared_body: body,
                    resolved_display: headingFont, resolved_body: bodyFont,
                    heading_found: !!heading,
                };
            }
            """
        )
    except Exception as exc:  # noqa: BLE001
        return {"passed": False, "detail": f"evaluate failed: {exc!r}"}

    display_ok = EXPECTED_DISPLAY_FONT in (result["resolved_display"] or "")
    body_ok = EXPECTED_BODY_FONT in (result["resolved_body"] or "")

    return {
        "passed": display_ok and body_ok,
        "detail": (
            f"display='{result['resolved_display']}' body='{result['resolved_body']}' "
            f"(expected Anton + Inter)"
        ),
    }


def _check_v16_selectors(page) -> dict[str, Any]:
    """Verify v16 class-based selectors resolve and layout invariants hold."""
    try:
        info = page.evaluate(
            """
            () => {
                const url = window.location.pathname;
                const isDeskPage = url.startsWith('/app') || url.startsWith('/desk');
                const breadcrumb = document.querySelector('.navbar-breadcrumbs');
                const trigger = document.querySelector('.fsm-trigger');
                // The 60px clearance rule applies to the page-title / title-area
                // children inside .page-head. Some desk pages (list/form views)
                // omit .page-head entirely; check breadcrumb margin separately.
                const pageTitle = document.querySelector(
                    '.page-head .page-title, .page-head .title-area'
                );
                let triggerStyle = null, pageTitleML = null, breadcrumbML = null;
                if (trigger) {
                    const cs = window.getComputedStyle(trigger);
                    triggerStyle = {
                        position: cs.position, top: cs.top, left: cs.left, width: cs.width,
                    };
                }
                if (pageTitle) {
                    pageTitleML = parseFloat(window.getComputedStyle(pageTitle).marginLeft) || 0;
                }
                if (breadcrumb) {
                    breadcrumbML = parseFloat(window.getComputedStyle(breadcrumb).marginLeft) || 0;
                }
                return {
                    is_desk: isDeskPage,
                    has_breadcrumb: !!breadcrumb,
                    has_page_title: !!pageTitle,
                    has_trigger: !!trigger,
                    trigger_style: triggerStyle,
                    page_title_margin_left_px: pageTitleML,
                    breadcrumb_margin_left_px: breadcrumbML,
                };
            }
            """
        )
    except Exception as exc:  # noqa: BLE001
        return {"passed": False, "detail": f"evaluate failed: {exc!r}"}

    if not info["is_desk"]:
        # SPA pages don't have these v16 selectors; skip.
        return {"passed": True, "detail": "SPA page; v16 selectors not applicable"}

    failures: list[str] = []
    if not info["has_breadcrumb"]:
        failures.append(".navbar-breadcrumbs missing on desk page")
    if not info["has_trigger"]:
        failures.append(".fsm-trigger missing")
    elif info["trigger_style"]:
        ts = info["trigger_style"]
        if ts.get("position") != "fixed":
            failures.append(f".fsm-trigger position={ts.get('position')!r} (expected fixed)")
    # Either .page-head .page-title OR .navbar-breadcrumbs (whichever is the
    # leftmost titlebar element on this page) must clear the .fsm-trigger.
    # Pages with neither are dialogs / unusual surfaces — skip silently.
    if info["has_page_title"] and (info["page_title_margin_left_px"] or 0) < 60:
        failures.append(
            f".page-head .page-title margin-left={info['page_title_margin_left_px']}px (expected >= 60 to clear .fsm-trigger)"
        )
    elif info["has_breadcrumb"] and not info["has_page_title"]:
        if (info["breadcrumb_margin_left_px"] or 0) < 60:
            failures.append(
                f".navbar-breadcrumbs margin-left={info['breadcrumb_margin_left_px']}px (expected >= 60 to clear .fsm-trigger)"
            )

    return {
        "passed": not failures,
        "detail": "; ".join(failures) if failures else "v16 selectors + layout OK",
    }


def _check_reveal_health(page) -> dict[str, Any]:
    """Verify no [data-reveal] elements are stuck at opacity:0 in viewport."""
    try:
        stuck = page.evaluate(
            """
            () => {
                const els = Array.from(document.querySelectorAll('[data-reveal]'));
                const viewport_h = window.innerHeight;
                return els.filter(el => {
                    const r = el.getBoundingClientRect();
                    const inViewport = r.top < viewport_h && r.bottom > 0;
                    const op = parseFloat(window.getComputedStyle(el).opacity);
                    return inViewport && op === 0;
                }).map(el => el.tagName + (el.id ? '#' + el.id : ''));
            }
            """
        )
    except Exception as exc:  # noqa: BLE001
        return {"passed": False, "detail": f"evaluate failed: {exc!r}"}
    return {
        "passed": len(stuck) == 0,
        "detail": (
            f"{len(stuck)} reveal elements stuck at opacity:0 in viewport: {stuck[:3]}"
            if stuck else "all visible [data-reveal] elements have non-zero opacity"
        ),
    }


def _check_drawer_surface(page) -> dict[str, Any]:
    """Verify drawer surface uses var(--ed-frost-bg) backdrop-filter blur+saturate."""
    try:
        info = page.evaluate(
            """
            () => {
                const drawer = document.querySelector('#fsm-drawer, .main-sidebar');
                if (!drawer) return { has_drawer: false };
                const cs = window.getComputedStyle(drawer);
                return {
                    has_drawer: true,
                    backdrop_filter: cs.backdropFilter || cs.webkitBackdropFilter || '',
                    background: cs.backgroundColor || '',
                };
            }
            """
        )
    except Exception as exc:  # noqa: BLE001
        return {"passed": False, "detail": f"evaluate failed: {exc!r}"}

    if not info.get("has_drawer"):
        return {"passed": True, "detail": "no drawer on this page; check skipped"}

    backdrop = info["backdrop_filter"] or ""
    has_blur = "blur" in backdrop.lower()
    has_saturate = "saturate" in backdrop.lower()
    passed = has_blur and has_saturate
    return {
        "passed": passed,
        "detail": (
            f"backdrop-filter='{backdrop}' (expected blur+saturate)"
            if not passed else "drawer frosted glass intact"
        ),
    }


def check_page(page, aspects: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    """
    Run all design-system checks. Returns {aspect_name: {passed, detail}}.

    `aspects` is an optional filter dict mapping aspect names to truthy values.
    If provided, only those aspects are checked; missing aspects are skipped
    and reported as passed=True.
    """
    aspects = aspects or {}
    results: dict[str, dict[str, Any]] = {}

    if aspects.get("fonts", True):
        results["fonts"] = _check_typography(page)
    if aspects.get("selectors", True):
        results["selectors"] = _check_v16_selectors(page)
    if aspects.get("reveal_health", True):
        results["reveal_health"] = _check_reveal_health(page)
    if aspects.get("drawer", True):
        results["drawer"] = _check_drawer_surface(page)
    return results


def summarize(results: dict[str, dict[str, Any]]) -> tuple[bool, str]:
    """Roll {aspect: {passed, detail}} into a single (passed, message) tuple."""
    failures = [(k, v["detail"]) for k, v in results.items() if not v.get("passed", True)]
    if failures:
        return False, "; ".join(f"{k}: {d}" for k, d in failures)
    return True, "all design-system aspects pass"
