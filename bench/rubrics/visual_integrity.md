# Rubric: visual_integrity

Judge whether the screenshot shows a structurally intact rendered page — no broken images, no console-error overlays, no half-loaded states.

## Dimensions

- **layout_complete** (1–10): page sections present and properly arranged; no empty regions where content should be; no overflowing/clipped containers. 10 = looks production-ready; 1 = dev-mode broken.
- **assets_loaded** (1–10): images render with content (not broken-image icons or blank rectangles); fonts have rendered (not fallback default-system-font); icons present. 10 = every asset loaded; 1 = obvious missing-image / missing-font failures.
- **no_error_overlays** (1–10): no Frappe error toasts, no browser alert dialogs, no red 4xx/5xx error pages. 10 = clean; 1 = error UI dominates the screenshot.
- **interactive_state_visible** (1–10): if the page has expected interactive affordances (buttons, links, forms), they look usable — not greyed-out, not stuck in a loading spinner forever. 10 = ready for input; 1 = blocked or stuck loading.

## Output schema

```json
{
  "layout_complete": <1-10>,
  "assets_loaded": <1-10>,
  "no_error_overlays": <1-10>,
  "interactive_state_visible": <1-10>,
  "reasoning": "<2-4 sentences>",
  "lowest_dimension": "<key>",
  "would_generate_candidate": <true if any < 7 else false>
}
```
