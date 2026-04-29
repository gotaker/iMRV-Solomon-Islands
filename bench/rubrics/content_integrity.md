# Rubric: content_integrity

Judge the *written content* visible in the screenshot — text quality, terminology consistency, copy that reads like it was reviewed by a human.

The deterministic deny-list at `bench/fixtures/typo_denylist.txt` catches *known* typos. This rubric catches the unknown ones — judgment calls about whether a domain term is used consistently, whether an error message is plain English or developer jargon, whether a label reads like it was reviewed.

## Dimensions

- **spelling_correctness** (1–10): visible text shows no obvious spelling errors. 10 = clean copy throughout; 1 = multiple typos visible. Flag specific examples in `reasoning`.
- **terminology_consistency** (1–10): the same concept uses the same word everywhere — "Mitigation" not interchangeably with "Reduction"; "Approver" not switching to "Reviewer"; sector names are stable. 10 = consistent vocabulary; 1 = three different terms for one concept on one page.
- **copy_voice** (1–10): labels and messages read like natural English. No "field is required errored" half-templated text. No raw stack traces. No leftover `{{placeholder}}` strings. 10 = production-ready voice; 1 = clearly half-finished or developer-internal.
- **localization_readiness** (1–10): if the app is intended for an English-speaking Solomon Islands audience, the copy is appropriate (no US-specific idioms in critical paths). Score 10 if irrelevant to the page.

If you spot a specific likely-typo or jargon string, name it in `reasoning` so the deny-list maintainer can add it.

## Output schema

```json
{
  "spelling_correctness": <1-10>,
  "terminology_consistency": <1-10>,
  "copy_voice": <1-10>,
  "localization_readiness": <1-10>,
  "reasoning": "<2-4 sentences; if any specific typo or inconsistent term, NAME IT here>",
  "lowest_dimension": "<key>",
  "would_generate_candidate": <true if any < 7 else false>,
  "specific_typos": ["<list of suspect strings to add to deny-list>"]
}
```
