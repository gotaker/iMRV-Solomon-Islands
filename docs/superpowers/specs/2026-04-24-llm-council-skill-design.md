# LLM Council Skill — Design

**Date:** 2026-04-24
**Status:** Approved (pending user review of this spec)
**Author:** Claude (with @utahjazz)

## Goal

Add a user-global Claude Code skill named `llm-council` that runs a user-provided question through five sub-agent "advisors" with distinct thinking lenses, has them peer-review each other anonymously, then has a chairman synthesise a final verdict. Output: a self-contained HTML report and a Markdown transcript saved into `.council/` in the current working directory.

Adapted from Andrej Karpathy's LLM Council methodology. We do not call multiple model vendors — diversity comes from advisor *prompts*, not from different providers.

## Non-goals

- No shell scripts, no external CLIs, no vendor APIs beyond Anthropic — this skill works inside Claude Code with sub-agents only.
- No replacement of the existing global `agent-council` skill at `~/.claude/skills/agent-council/`. Both coexist; trigger phrases differ.
- No interactive UI, no per-advisor configuration knobs in v1. Five fixed advisors, fixed model assignment.
- No automatic re-running of past councils, no transcript indexing.

## Architecture

The skill is a single self-contained markdown file: `~/.claude/skills/llm-council/SKILL.md`. No companion scripts, no config files.

When loaded, the SKILL.md instructs the main Claude session to orchestrate the council. All sub-agents are spawned via the `Agent` tool. Parallelism is achieved by emitting multiple `Agent` tool calls inside a single assistant message.

### Workflow

```
user: "council this: <question>"
   │
   ▼
[main Claude] frame the question
   │  - scan CLAUDE.md, memory/, recent .council/ transcripts (≤30s)
   │  - rewrite as neutral framed question with embedded context
   ▼
[main Claude] spawn 5 advisor sub-agents IN PARALLEL (one message, 5 Agent calls)
   │  Contrarian │ First Principles │ Expansionist │ Outsider │ Executor
   │  model: sonnet  •  no tools  •  150–300 words each
   ▼
[main Claude] anonymize: random A→E mapping
   │
   ▼
[main Claude] spawn 5 reviewer sub-agents IN PARALLEL (one message, 5 Agent calls)
   │  Each sees all 5 anonymized responses + 3 review questions
   │  model: sonnet  •  ≤200 words each
   ▼
[main Claude] spawn 1 chairman sub-agent
   │  Sees: framed question, de-anonymized responses, all 5 reviews
   │  model: opus  •  produces structured verdict
   ▼
[main Claude] persist artifacts
   │  - .council/council-transcript-<ts>.md
   │  - .council/council-report-<ts>.html
   │  - .council/.gitignore  (containing "*", on first run only)
   ▼
[main Claude] open report
   │  open .council/council-report-<ts>.html  (darwin)
   │  xdg-open .council/council-report-<ts>.html  (linux fallback)
   ▼
[main Claude] reply with one-paragraph summary + path to report
```

## Components

### 1. The SKILL.md frontmatter

```yaml
---
name: llm-council
description: "Run any question, idea, or decision through a council of 5 AI advisors who independently analyze it, peer-review each other anonymously, and synthesize a final verdict. Based on Karpathy's LLM Council methodology. MANDATORY TRIGGERS: 'council this', 'run the council', 'war room this', 'pressure-test this', 'stress-test this', 'debate this'. STRONG TRIGGERS (use when combined with a real decision or tradeoff): 'should I X or Y', 'which option', 'what would you do', 'is this the right move', 'validate this', 'get multiple perspectives', 'I can't decide', 'I'm torn between'. Do NOT trigger on simple yes/no questions, factual lookups, or casual 'should I' without a meaningful tradeoff (e.g. 'should I use markdown' is not a council question). DO trigger when the user presents a genuine decision with stakes, multiple options, and context that suggests they want it pressure-tested from multiple angles."
---
```

The trigger discipline lives entirely in the description string; there is no runtime gate. If Claude misclassifies, the user can correct ("just answer it, don't council").

### 2. Five advisor identities

Verbatim from the user-provided spec — preserved unchanged in v1. Each is a thinking style, not a job title:

- **The Contrarian** — finds fatal flaws, what's missing, what will fail.
- **The First Principles Thinker** — strips assumptions, asks "are we solving the right problem?"
- **The Expansionist** — looks for upside, hidden adjacent opportunity.
- **The Outsider** — zero context, fresh-eyes test for curse of knowledge.
- **The Executor** — only "what do you do Monday morning?", fastest path.

Three natural tensions: Contrarian↔Expansionist, First Principles↔Executor, Outsider keeps everyone honest.

### 3. Sub-agent prompts (templates baked into SKILL.md)

**Advisor prompt template** — given to each of the 5 in parallel:

```
You are [Advisor Name] on an LLM Council.
Your thinking style: [advisor description]

A user has brought this question to the council:
---
[framed question]
---

Respond from your perspective. Be direct and specific. Don't hedge or try to
be balanced. Lean fully into your assigned angle. The other advisors will
cover the angles you're not covering.

Do not use any tools. Do not search the web, read files, or run code. Reason
purely from the question and your assigned perspective.

Keep your response between 150-300 words. No preamble. Go straight into your
analysis.
```

**Reviewer prompt template** — given to each of the 5 reviewers in parallel, with anonymized A–E responses:

```
You are reviewing the outputs of an LLM Council. Five advisors independently
answered this question:
---
[framed question]
---
Here are their anonymized responses:

**Response A:**
[response]
**Response B:**
[response]
... (C, D, E)

Answer these three questions. Be specific. Reference responses by letter.

1. Which response is the strongest? Why?
2. Which response has the biggest blind spot? What is it missing?
3. What did ALL five responses miss that the council should consider?

Do not use any tools. Keep your review under 200 words. Be direct.
```

**Chairman prompt** — single sub-agent, given everything de-anonymized:

```
You are the Chairman of an LLM Council. Synthesize 5 advisor responses and
their peer reviews into a final verdict.

Question:
---
[framed question]
---

ADVISOR RESPONSES:
**The Contrarian:** [response]
**The First Principles Thinker:** [response]
**The Expansionist:** [response]
**The Outsider:** [response]
**The Executor:** [response]

PEER REVIEWS:
[all 5 peer reviews, with anonymization mapping disclosed]

Produce the council verdict using this exact structure:

## Where the Council Agrees
## Where the Council Clashes
## Blind Spots the Council Caught
## The Recommendation
## The One Thing to Do First

Be direct. Don't hedge. The chairman may disagree with the majority if the
reasoning supports it.
```

### 4. Model assignment

| Role | Model | Reasoning |
|---|---|---|
| 5 advisors | `sonnet` (Sonnet 4.6) | Bulk reasoning; 5 calls per session, cost-sensitive |
| 5 reviewers | `sonnet` (Sonnet 4.6) | Same — bulk |
| 1 chairman | `opus` (Opus 4.7) | Load-bearing synthesis step |

Passed via the `model` parameter on the `Agent` tool. `subagent_type` is `general-purpose` for all 11 calls.

### 5. Output artifacts

Both written to `<cwd>/.council/`:

- **Transcript** (`council-transcript-<ISO8601-no-colons>.md`): original question, framed question, all 5 advisor responses, all 5 peer reviews with anonymization mapping disclosed at the end, chairman synthesis. This is the canonical record.
- **Report** (`council-report-<ISO8601-no-colons>.html`): single self-contained HTML file. Inline CSS only, system font stack, white background, subtle borders. Sections in order:
  1. Question (top, prominent)
  2. Chairman verdict (the focal section — most users read only this). The verdict's "Where the Council Agrees" and "Where the Council Clashes" subsections double as the agreement/divergence view; no separate grid is generated.
  3. Five `<details>` blocks for advisor responses (collapsed by default), one per advisor, labelled with the advisor name.
  4. One `<details>` block holding all 5 peer reviews (collapsed by default).
  5. Footer: timestamp, original (un-framed) question, anonymization mapping that was used.

### 6. `.council/.gitignore` self-exclusion

On first run, if `.council/.gitignore` does not exist, write a single-line file containing `*`. This prevents the report and transcript from being committed without requiring the user to edit the project's root `.gitignore`. Subsequent runs do not touch this file.

## Data flow

```
user message
    │
    ▼
framed_question  (built from message + workspace context)
    │
    ├──▶ 5 advisor calls (parallel)  ──▶ {responses[5]}
    │
    ▼
anonymized_responses  (random A–E permutation)
    │
    ├──▶ 5 reviewer calls (parallel)  ──▶ {reviews[5]}
    │
    ▼
{framed_question, deanon_responses, reviews}
    │
    └──▶ 1 chairman call  ──▶ verdict
                                 │
                                 ▼
                          transcript.md + report.html  →  open
```

The main Claude session is the only stateful actor. Sub-agents are stateless: each invocation gets full context as a prompt.

## Failure modes

| Mode | Handling |
|---|---|
| One advisor sub-agent fails or returns empty | Retry that one slot once. If it fails again, proceed with 4 advisors and disclose the gap in the transcript and report. Do not abort the session. |
| Reviewer fails | Same — retry once, then proceed. The chairman is told how many reviews are present. |
| Chairman fails | Retry once with the same inputs. If it fails again, write the transcript anyway (advisor responses + reviews are still valuable) and tell the user the synthesis step failed. |
| `.council/` not writable (read-only fs, etc.) | Fall back to `$TMPDIR/council-<ts>/`, tell the user the path. |
| `open` / `xdg-open` not available | Skip the open step, print the absolute path. Do not error. |
| Question clearly trivial despite trigger match | The skill description handles this at trigger time. If the user explicitly invokes ("council this: should I use markdown"), proceed anyway — the user asked for it. |
| User on Windows | Out of scope for v1. Document `open` is darwin/linux only; Windows users get the path printed. |

## Testing

Skills don't have a unit-test harness in this repo. Verification is manual:

1. **Smoke test in a scratch repo:**
   ```bash
   mkdir /tmp/council-smoke && cd /tmp/council-smoke
   # in a fresh Claude Code session:
   # > council this: should I use Postgres or SQLite for a 100-user internal tool?
   ```
   Expected: `.council/council-report-*.html` opens in browser, transcript saved alongside, `.council/.gitignore` contains `*`.

2. **Trigger discrimination check:** ask a trivial factual question ("council this: what's the capital of France?"). Expected: Claude should *not* run the council. If it does, tighten the description.

3. **Parallelism check:** in the transcript, the advisor responses should not show evidence of seeing each other (e.g., no "as the Contrarian noted…"). If they do, the parallel dispatch broke.

4. **Anonymization check:** the peer reviews should reference responses by letter (A–E) only. If a review says "the Contrarian's response," anonymization broke.

5. **Cost ceiling check:** one council session should cost on the order of a few cents (5×Sonnet + 5×Sonnet + 1×Opus, modest token counts). If it spikes much higher, something is wrong with prompt sizes.

## Out of scope (deferred)

- Configurable advisors / advisor count
- Cross-vendor council (OpenAI + Gemini + Anthropic)
- Council on a *codebase* (advisors with file-read tools)
- Council history index / past-decision search
- Windows `start` support for auto-opening reports
- Streaming output (sub-agents return as a batch; user waits for the synthesis)

## Open decisions resolved during brainstorm

| Decision | Choice |
|---|---|
| Diversity mechanism | Sub-agents with distinct prompts (option D), not multi-vendor |
| Install location | `~/.claude/skills/llm-council/` (global) |
| Output location | `<cwd>/.council/` with self-excluding `.gitignore` |
| Model assignment | Sonnet for advisors+reviewers, Opus for chairman |
| Skill packaging | Single SKILL.md, no scripts |

## References

- Andrej Karpathy's LLM Council post (the methodology this adapts).
- Existing global skill: `~/.claude/skills/agent-council/SKILL.md` — different mechanism (shells out to vendor CLIs), kept side-by-side. Different trigger phrases.
- Claude Code `Agent` tool: parallel sub-agent dispatch via multiple tool calls in one assistant message; supports `model` and `subagent_type` parameters.
