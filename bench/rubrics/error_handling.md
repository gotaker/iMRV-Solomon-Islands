# Rubric: error_handling

Judge how the page communicates problems — when something is wrong, does the user see a helpful message?

## Dimensions

- **errors_user_facing** (1–10): if errors occurred (form validation failures, permission denied, server error), they're shown in a clear, user-readable form — not raw stack traces, not silent failures, not generic "something went wrong".
- **stack_traces_absent** (1–10): no Python tracebacks, no `frappe.exceptions.*` strings, no `werkzeug.exceptions.*` rendered to the user.
- **fallback_states_present** (1–10): empty states, loading spinners, and "no results" messages exist where appropriate; no eternal blank panels with no indication of what's happening.
- **recovery_paths_visible** (1–10): when something fails, the user sees what to do next (retry button, back link, contact support). Not "click somewhere or refresh, who knows".

## Output schema

```json
{
  "errors_user_facing": <1-10>,
  "stack_traces_absent": <1-10>,
  "fallback_states_present": <1-10>,
  "recovery_paths_visible": <1-10>,
  "reasoning": "<2-4 sentences>",
  "lowest_dimension": "<key>",
  "would_generate_candidate": <true if any < 7 else false>
}
```
