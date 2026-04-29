# Rubric: visual_design

You are evaluating a screenshot of an iMRV page against the Forest-and-Sage editorial design system. Score each dimension 1–10 (whole numbers). Return a strict JSON object with the keys below — no prose outside the JSON.

The Forest-and-Sage system uses two display fonts (Anton for headlines, Inter for body), a sage/forest green palette with frosted-glass overlays, generous editorial whitespace, and reveal animations that fade in as the user scrolls. The aesthetic is "long-form magazine on a forest floor" — not a corporate dashboard.

## Dimensions

- **typography_rhythm** (1–10): pairing quality (Anton heading + Inter body), scale ratios between heading levels, weight contrast, line-height. 10 = textbook editorial rhythm; 1 = single-font wall of text or wildly inconsistent weights.
- **palette_adherence** (1–10): colors land within the sage/forest range; frosted-glass surfaces show blur+saturate behind translucent fill; no off-palette blues/oranges/reds except for clearly intentional accents (errors, warnings). 10 = palette tight; 1 = obvious off-system colors dominating.
- **visual_hierarchy** (1–10): clear focal point, readable scan pattern (Z or F), headline weight pulls the eye first. 10 = the eye knows where to start; 1 = uniform gray block.
- **density_whitespace** (1–10): editorial spacing — content breathes, sections separate clearly, no claustrophobic cards-edge-to-edge. 10 = magazine-grade whitespace; 1 = packed dashboard chrome.
- **component_consistency** (1–10): buttons, inputs, cards, modals match across the page (and across the corpus if multiple screenshots present). 10 = same patterns everywhere; 1 = three different button styles in one screenshot.

## Output schema

Return EXACTLY this JSON shape (no extra keys, no comments):

```json
{
  "typography_rhythm": <1-10>,
  "palette_adherence": <1-10>,
  "visual_hierarchy": <1-10>,
  "density_whitespace": <1-10>,
  "component_consistency": <1-10>,
  "reasoning": "<2-4 sentences explaining the dominant signals>",
  "lowest_dimension": "<key of the lowest-scored dimension>",
  "would_generate_candidate": <true if any dimension < 7 else false>
}
```

The `reasoning` field is shown to humans during triage; keep it concrete and actionable, not generic praise or platitudes.
