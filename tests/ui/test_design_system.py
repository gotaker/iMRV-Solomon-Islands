"""Layer 3 — design-system compliance (WCAG, touch targets, alt text, no emojis, responsive)."""

from __future__ import annotations

import re

import pytest

from tests.ui._axe import axe_scan, violations_of

pytestmark = pytest.mark.ui


# Emoji codepoint ranges — rough cut, catches the common offenders (😀 🚀 ⚙️ 🎨 ✅ 🔥).
_EMOJI_RE = re.compile(
    r"["
    r"\U0001F300-\U0001F6FF"
    r"\U0001F900-\U0001F9FF"
    r"☀-➿"
    r"]"
)


def _login(page, base_url: str) -> None:
    page.goto(f"{base_url}/login")
    page.fill('input[name="login_email"], input#login_email', "Administrator")
    page.fill('input[name="login_password"], input#login_password', "admin")
    page.click('button[type="submit"], button:has-text("Login")')
    page.wait_for_url("**/app/**", timeout=15_000)


def test_ds_color_contrast(browser, bench_server):
    """axe-core scan: zero color-contrast violations on the SPA home and desk main dashboard."""
    ctx = browser.new_context()
    page = ctx.new_page()
    try:
        for path in ("/frontend/home",):
            page.goto(f"{bench_server}{path}")
            page.wait_for_load_state("networkidle", timeout=15_000)
            result = axe_scan(page, rules=["color-contrast"])
            violations = violations_of(result, "color-contrast")
            assert violations == [], (
                f"{len(violations)} color-contrast violations on {path}: "
                f"{[v['nodes'][0]['html'][:80] for v in violations[:3]]}"
            )

        # Authed view
        _login(page, bench_server)
        page.goto(f"{bench_server}/app/main-dashboard")
        page.wait_for_load_state("networkidle", timeout=15_000)
        result = axe_scan(page, rules=["color-contrast"])
        violations = violations_of(result, "color-contrast")
        assert violations == [], f"{len(violations)} violations on /app/main-dashboard"
    finally:
        ctx.close()


def test_ds_touch_targets(browser, bench_server):
    """At 375px viewport, every <a> / <button> / [role=button] on /frontend/home has bounding box >= 44x44."""
    ctx = browser.new_context(viewport={"width": 375, "height": 812})
    page = ctx.new_page()
    try:
        page.goto(f"{bench_server}/frontend/home")
        page.wait_for_load_state("networkidle", timeout=15_000)
        small = page.evaluate("""
            () => {
              const els = document.querySelectorAll('a, button, [role="button"]');
              return Array.from(els).flatMap(el => {
                const r = el.getBoundingClientRect();
                // ignore hidden/zero-size elements
                if (r.width === 0 && r.height === 0) return [];
                return (r.width < 44 || r.height < 44) ? [{tag: el.tagName, w: r.width, h: r.height, html: el.outerHTML.slice(0, 120)}] : [];
              });
            }
        """)
        assert small == [], f"{len(small)} interactive elements under 44x44: {small[:3]}"
    finally:
        ctx.close()


def test_ds_alt_text(browser, bench_server):
    """All <img> on 4 key SPA routes have non-empty alt OR explicit role=presentation."""
    ctx = browser.new_context()
    page = ctx.new_page()
    missing = []
    try:
        for path in ("/frontend/home", "/frontend/about", "/frontend/projects", "/frontend/reports"):
            page.goto(f"{bench_server}{path}")
            page.wait_for_load_state("networkidle", timeout=15_000)
            bad = page.evaluate("""
                () => Array.from(document.querySelectorAll('img'))
                  .filter(img => !img.getAttribute('role') || img.getAttribute('role') !== 'presentation')
                  .filter(img => !img.alt || img.alt.trim() === '')
                  .map(img => img.outerHTML.slice(0, 120))
            """)
            missing.extend([(path, b) for b in bad])
        assert missing == [], f"{len(missing)} images lack alt text: {missing[:3]}"
    finally:
        ctx.close()


def test_ds_no_emoji_icons(browser, bench_server):
    """No emoji codepoints inside <button>, <a>, or [role=menuitem]."""
    ctx = browser.new_context()
    page = ctx.new_page()
    try:
        page.goto(f"{bench_server}/frontend/home")
        page.wait_for_load_state("networkidle", timeout=15_000)
        texts = page.evaluate("""
            () => Array.from(document.querySelectorAll('button, a, [role="menuitem"]'))
              .map(el => el.innerText || '')
        """)
        offenders = [t for t in texts if _EMOJI_RE.search(t)]
        assert offenders == [], f"emoji used as icon text: {offenders[:3]}"
    finally:
        ctx.close()


def test_ds_responsive_no_overflow(browser, bench_server):
    """Viewport at 375/768/1440px — /frontend/home has no horizontal scroll."""
    for width in (375, 768, 1440):
        ctx = browser.new_context(viewport={"width": width, "height": 900})
        page = ctx.new_page()
        try:
            page.goto(f"{bench_server}/frontend/home")
            page.wait_for_load_state("networkidle", timeout=15_000)
            scroll, inner = page.evaluate("() => [document.documentElement.scrollWidth, window.innerWidth]")
            assert scroll <= inner + 1, f"horizontal scroll at {width}px: scrollWidth={scroll}, innerWidth={inner}"
        finally:
            ctx.close()
