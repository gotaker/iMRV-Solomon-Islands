# Rubric: navigation_correctness

Judge whether the navigation surface (drawer, breadcrumbs, primary nav, in-page links) appears correct and trustworthy.

## Dimensions

- **breadcrumbs_present** (1–10): on a desk page, `.navbar-breadcrumbs` (v16 class selector) is visible and shows a sensible trail. SPA pages may have a different nav shape — score 10 if the SPA equivalent is visible.
- **drawer_correct** (1–10): if the drawer is open in the screenshot, entries match what this role should see (no leaked USER section for Approved User; no admin-only entries for submitter; no missing entries the role *should* see).
- **destinations_plausible** (1–10): visible links and buttons point at routes that look like real app routes, not placeholder `#` or broken `/undefined/...` paths.
- **active_state_correct** (1–10): the current location is reflected in the nav (active drawer entry highlighted, breadcrumb final segment matches page title).

## Output schema

```json
{
  "breadcrumbs_present": <1-10>,
  "drawer_correct": <1-10>,
  "destinations_plausible": <1-10>,
  "active_state_correct": <1-10>,
  "reasoning": "<2-4 sentences>",
  "lowest_dimension": "<key>",
  "would_generate_candidate": <true if any < 7 else false>
}
```
