# Rubric: perf

Judge perceived performance — does the page feel fast, settled, and responsive in the captured state?

You will receive timing data alongside the screenshot:
  - `navigation_duration_ms` — time from goto() to networkidle
  - `console_error_count`, `network_4xx_count`
  - `dom_size_estimate` — rough DOM node count

## Dimensions

- **time_to_settled** (1–10): based on `navigation_duration_ms`. <2000 = 10, <5000 = 8, <10000 = 6, <15000 = 4, slower = lower.
- **dom_size_reasonable** (1–10): based on `dom_size_estimate`. <2000 = 10, <5000 = 8, <10000 = 6, more = lower.
- **network_health** (1–10): if `network_4xx_count` is 0, score 10. Each 4xx subtracts 1.
- **visual_stability** (1–10): from the screenshot, judge whether the page looks "settled" (content placed, fonts loaded) or mid-render (placeholders, FOUT, layout-shift artifacts).

## Output schema

```json
{
  "time_to_settled": <1-10>,
  "dom_size_reasonable": <1-10>,
  "network_health": <1-10>,
  "visual_stability": <1-10>,
  "reasoning": "<2-4 sentences>",
  "lowest_dimension": "<key>",
  "would_generate_candidate": <true if any < 7 else false>
}
```
