# LLM Council Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a user-global Claude Code skill at `~/.claude/skills/llm-council/SKILL.md` that orchestrates 5 sub-agent advisors + anonymous peer review + chairman synthesis, persisting an HTML report and Markdown transcript to `<cwd>/.council/`.

**Architecture:** Single self-contained markdown file. The skill is content, not code: when invoked, the main Claude session reads the SKILL.md and follows its instructions, dispatching sub-agents via the `Agent` tool (multiple calls in one message for parallelism) with explicit `model` overrides. Output is persisted via `Write` and `Bash` tools.

**Tech Stack:** Markdown, YAML frontmatter, Claude Code's `Agent` / `Write` / `Bash` / `Glob` / `Read` tools. No external dependencies, no scripts, no git in the deliverable directory.

---

## Pre-implementation notes

**Deliverable lives outside any git repo** (`~/.claude/skills/llm-council/`), so this plan does NOT include per-task git commits for the skill file. The iMRV repo gets its own commit for the spec + plan separately (out of scope for this plan — user-initiated).

**No automated test harness exists for skills.** Verification is the final smoke-test task. Each authoring task ends with a "verify the file parses as valid YAML+Markdown" check, which catches frontmatter typos.

**Source of truth for content:** the spec at `docs/superpowers/specs/2026-04-24-llm-council-skill-design.md`. When in doubt during implementation, the spec wins. Tasks below quote the spec verbatim where prompt templates are involved — do not paraphrase.

**Reference, not duplication:** Each task shows the exact content to write. Tasks are append-only (no editing earlier sections), so an engineer reading them out of order should still get a working file by following them in numeric order.

---

## File structure

Single file:

| File | Responsibility |
| --- | --- |
| `~/.claude/skills/llm-council/SKILL.md` | Skill definition: frontmatter + workflow instructions + prompt templates + output format spec. Read by Claude Code at skill-invocation time. |

The file is built up section by section. Each section maps to one task below.

---

## Task 1: Create skill directory and frontmatter

**Files:**
- Create: `~/.claude/skills/llm-council/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p ~/.claude/skills/llm-council
```

Expected: directory created, no output. Verify: `ls -ld ~/.claude/skills/llm-council` shows it exists.

- [ ] **Step 2: Write the frontmatter and title (use `Write` tool, not echo/heredoc)**

Write the file with exactly this content (description string is verbatim from the spec — do NOT paraphrase or shorten the trigger taxonomy, the trigger discipline lives in this string):

````markdown
---
name: llm-council
description: "Run any question, idea, or decision through a council of 5 AI advisors who independently analyze it, peer-review each other anonymously, and synthesize a final verdict. Based on Karpathy's LLM Council methodology. MANDATORY TRIGGERS: 'council this', 'run the council', 'war room this', 'pressure-test this', 'stress-test this', 'debate this'. STRONG TRIGGERS (use when combined with a real decision or tradeoff): 'should I X or Y', 'which option', 'what would you do', 'is this the right move', 'validate this', 'get multiple perspectives', 'I can't decide', 'I'm torn between'. Do NOT trigger on simple yes/no questions, factual lookups, or casual 'should I' without a meaningful tradeoff (e.g. 'should I use markdown' is not a council question). DO trigger when the user presents a genuine decision with stakes, multiple options, and context that suggests they want it pressure-tested from multiple angles."
---

# LLM Council

You ask one AI a question, you get one answer. That answer might be great. It might be mid. You have no way to tell because you only saw one perspective.

The council fixes this. It runs the user's question through 5 independent advisors, each thinking from a fundamentally different angle. Then they review each other's work. Then a chairman synthesizes everything into a final recommendation that says where the advisors agree, where they clash, and what the user should actually do.

Adapted from Andrej Karpathy's LLM Council. We do this inside Claude using sub-agents with different thinking lenses (not different vendors).

## When to run the council

Council questions are decisions where being wrong is expensive: real tradeoffs, real stakes, multiple plausible options.

**Good council questions:**
- "Should I launch a $97 workshop or a $497 course?"
- "Which of these 3 positioning angles is strongest?"
- "I'm thinking of pivoting from X to Y. Am I crazy?"
- "Here's my landing page copy. What's weak?"

**Bad council questions:**
- "What's the capital of France?" (one right answer)
- "Write me a tweet" (creation, not decision)
- "Summarize this article" (processing, not judgment)

If the user invokes the council on a trivial question, proceed anyway — they explicitly asked.
````

- [ ] **Step 3: Verify the frontmatter parses**

Run:

```bash
python3 -c "import yaml,sys; doc=open('$HOME/.claude/skills/llm-council/SKILL.md').read(); fm=doc.split('---',2)[1]; print(yaml.safe_load(fm))"
```

Expected: a dict with `name: llm-council` and a non-empty `description`. No traceback. If YAML parsing errors, the most likely cause is an unescaped quote in the description — re-read Step 2 and re-write.

---

## Task 2: Add the five advisor identities

**Files:**
- Modify: `~/.claude/skills/llm-council/SKILL.md` (append section)

- [ ] **Step 1: Append the advisors section**

Append this section to the file:

````markdown

## The five advisors

Each advisor is a thinking *style*, not a job title. Together they create three natural tensions: Contrarian↔Expansionist, First Principles↔Executor, with the Outsider keeping everyone honest.

### 1. The Contrarian

Actively looks for what's wrong, what's missing, what will fail. Assumes the idea has a fatal flaw and tries to find it. Not a pessimist — the friend who saves you from a bad deal by asking the questions you're avoiding.

### 2. The First Principles Thinker

Ignores the surface-level question and asks "what are we actually trying to solve here?" Strips away assumptions. Rebuilds from the ground up. May say "you're asking the wrong question entirely."

### 3. The Expansionist

Looks for upside everyone else is missing. What could be bigger? What adjacent opportunity is hiding? Doesn't care about risk (Contrarian's job). Cares about what happens if this works even better than expected.

### 4. The Outsider

Has zero context about the user, their field, or their history. Responds purely to what's in front of them. Catches the curse of knowledge — things that are obvious to the user but confusing to everyone else.

### 5. The Executor

Only cares about one thing: can this actually be done, and what's the fastest path? Ignores theory. Looks at every idea through "OK but what do you do Monday morning?"
````

- [ ] **Step 2: Verify the file is still well-formed**

Run:

```bash
wc -l ~/.claude/skills/llm-council/SKILL.md
grep -c "^## " ~/.claude/skills/llm-council/SKILL.md
```

Expected: line count grew, and `^## ` matches show 2 sections (`When to run the council`, `The five advisors`). If less, the append didn't take.

---

## Task 3: Add the framing/context-enrichment step

**Files:**
- Modify: `~/.claude/skills/llm-council/SKILL.md` (append)

- [ ] **Step 1: Append the framing section**

````markdown

## Step 1: Frame the question (with context enrichment)

When the user invokes the council, do two things before dispatching advisors:

**A. Scan the workspace for context.** Spend at most 30 seconds. Use `Glob` and `Read` to locate the 2–3 files that would let advisors give specific, grounded answers instead of generic takes. Look for:

- `CLAUDE.md` / `claude.md` in the project root or workspace
- A `memory/` folder (audience profiles, voice docs, past decisions, business context)
- Any files the user explicitly referenced or attached
- Recent transcripts in `<cwd>/.council/` (to avoid re-counciling the same ground)
- Topic-specific files: if the question is about pricing, look for revenue/launch data; if about positioning, look for past messaging.

Stop scanning as soon as you have enough; do not enumerate the whole repo.

**B. Frame the question.** Rewrite the user's raw message + the workspace context as a clear, neutral prompt that all five advisors will receive. Include:

1. The core decision or question
2. Key context from the user's message
3. Key context from workspace files (business stage, audience, constraints, past results, relevant numbers)
4. What's at stake — why this decision matters

Don't add your own opinion. Don't steer it. Do make sure each advisor has enough context to give a specific answer.

If the question is too vague (e.g. "council this: my business"), ask **exactly one** clarifying question, then proceed.

Save the framed question — it goes into the transcript, every advisor prompt, and every reviewer prompt.
````

- [ ] **Step 2: Verify**

```bash
grep -c "^## Step " ~/.claude/skills/llm-council/SKILL.md
```

Expected: `1` (only Step 1 so far).

---

## Task 4: Add the convene-the-council step (parallel advisor dispatch)

**Files:**
- Modify: `~/.claude/skills/llm-council/SKILL.md` (append)

- [ ] **Step 1: Append the dispatch section**

The advisor prompt template below is verbatim from the spec — copy it exactly. The closing-fence dance (using a 4-backtick outer fence so the inner 3-backtick code block survives) matters; if the file ends up with a broken code block, look here first.

`````markdown

## Step 2: Convene the council (5 advisors in parallel)

Dispatch all 5 advisor sub-agents **in a single assistant message** with 5 `Agent` tool calls. Sequential dispatch wastes time and risks earlier responses bleeding into later ones via your conversation context.

For each `Agent` call:

- `subagent_type`: `general-purpose`
- `model`: `sonnet` (Sonnet 4.6 — bulk reasoning, cost-sensitive)
- `description`: a short label (e.g. `"Council: Contrarian"`)
- `prompt`: the template below, with `[Advisor Name]`, `[advisor description]`, and `[framed question]` filled in.

**Advisor prompt template:**

````
You are [Advisor Name] on an LLM Council.
Your thinking style: [advisor description from the SKILL.md "five advisors" section]

A user has brought this question to the council:
---
[framed question]
---

Respond from your perspective. Be direct and specific. Don't hedge or try to be balanced. Lean fully into your assigned angle. The other advisors will cover the angles you're not covering.

Do not use any tools. Do not search the web, read files, or run code. Reason purely from the question and your assigned perspective.

Keep your response between 150-300 words. No preamble. Go straight into your analysis.
````

After all 5 return, store each response in memory keyed by advisor name. If any advisor returns empty or errors, retry that one slot once. If it fails again, proceed with 4 advisors and record the gap in the transcript.
`````

- [ ] **Step 2: Verify the inner code fence survived the append**

```bash
grep -c '^```' ~/.claude/skills/llm-council/SKILL.md
```

Expected: an even number (every fence has a closing partner). If odd, a fence got swallowed — re-read the file and fix.

---

## Task 5: Add the peer-review step

**Files:**
- Modify: `~/.claude/skills/llm-council/SKILL.md` (append)

- [ ] **Step 1: Append the peer-review section**

`````markdown

## Step 3: Peer review (5 reviewers in parallel)

This is the step that makes the council more than "ask 5 times."

**Anonymize first.** Generate a random permutation of `[A, B, C, D, E]` and map each advisor's response to one letter. Keep the mapping in memory; do NOT include it in the reviewer prompts. If reviewers know which advisor said what, they'll defer to certain thinking styles instead of evaluating on merit.

**Dispatch 5 reviewer sub-agents in a single message.** Each reviewer is a separate `Agent` call:

- `subagent_type`: `general-purpose`
- `model`: `sonnet`
- `description`: `"Council review N"` (N = 1..5)
- `prompt`: the template below, with all 5 anonymized responses inlined.

All 5 reviewers see the same 5 anonymized responses — they review independently.

**Reviewer prompt template:**

````
You are reviewing the outputs of an LLM Council. Five advisors independently answered this question:
---
[framed question]
---

Here are their anonymized responses:

**Response A:**
[response]

**Response B:**
[response]

**Response C:**
[response]

**Response D:**
[response]

**Response E:**
[response]

Answer these three questions. Be specific. Reference responses by letter only.

1. Which response is the strongest? Why?
2. Which response has the biggest blind spot? What is it missing?
3. What did ALL five responses miss that the council should consider?

Do not use any tools. Keep your review under 200 words. Be direct.
````

If a reviewer fails, retry once, then proceed with whatever reviews returned. Tell the chairman how many reviews are present.
`````

- [ ] **Step 2: Verify**

```bash
grep -c "^## Step " ~/.claude/skills/llm-council/SKILL.md
grep -c '^```' ~/.claude/skills/llm-council/SKILL.md
```

Expected: 3 step-sections so far; even fence count.

---

## Task 6: Add the chairman synthesis step

**Files:**
- Modify: `~/.claude/skills/llm-council/SKILL.md` (append)

- [ ] **Step 1: Append the chairman section**

`````markdown

## Step 4: Chairman synthesis

One final sub-agent. The chairman gets everything de-anonymized.

- `subagent_type`: `general-purpose`
- `model`: `opus` (Opus 4.7 — load-bearing synthesis, the bigger model goes here)
- `description`: `"Council chairman synthesis"`
- `prompt`: the template below.

**Chairman prompt:**

````
You are the Chairman of an LLM Council. Synthesize 5 advisor responses and their peer reviews into a final verdict.

Question:
---
[framed question]
---

ADVISOR RESPONSES:

**The Contrarian:**
[response]

**The First Principles Thinker:**
[response]

**The Expansionist:**
[response]

**The Outsider:**
[response]

**The Executor:**
[response]

PEER REVIEWS (5 total, anonymized A–E mapping disclosed):
[anonymization mapping in plain text, e.g. "A=Contrarian, B=Outsider, C=Executor, D=Expansionist, E=First Principles"]

[review 1 full text]
[review 2 full text]
[review 3 full text]
[review 4 full text]
[review 5 full text]

Produce the council verdict using this exact structure:

## Where the Council Agrees
Points multiple advisors converged on independently. High-confidence signals.

## Where the Council Clashes
Genuine disagreements. Present both sides. Explain why reasonable advisors disagree. Do not smooth this over.

## Blind Spots the Council Caught
Things that only emerged through peer review — that individual advisors missed but others flagged.

## The Recommendation
A clear, direct recommendation. Not "it depends." Not "consider both sides." A real answer with reasoning. You may disagree with the majority of advisors if the reasoning of a dissenter is stronger.

## The One Thing to Do First
A single concrete next step. Not a list. One thing.

Be direct. Don't hedge. The whole point of the council is to give the user clarity they couldn't get from one perspective.
````

If the chairman call fails, retry once. If it fails again, write the transcript with advisor responses + reviews and tell the user the synthesis step failed (the raw inputs are still valuable).
`````

- [ ] **Step 2: Verify**

```bash
grep -c '^```' ~/.claude/skills/llm-council/SKILL.md
```

Expected: even count.

---

## Task 7: Add the persistence step (transcript + HTML report + .gitignore)

**Files:**
- Modify: `~/.claude/skills/llm-council/SKILL.md` (append)

- [ ] **Step 1: Append the persistence section**

`````markdown

## Step 5: Persist artifacts

Both files go to `<cwd>/.council/`. Use the local timezone for the timestamp; format `YYYYMMDD-HHMMSS` (no colons — safe in filenames on every OS).

**Bootstrap the output directory** on first use only:

```bash
mkdir -p .council
[ -f .council/.gitignore ] || echo '*' > .council/.gitignore
```

The `.gitignore` containing `*` makes the directory self-excluding so reports don't accidentally land in commits without touching the project's root `.gitignore`.

**Write the transcript** as `.council/council-transcript-<ts>.md`. Use the `Write` tool. Structure:

````
# Council Transcript — <ISO timestamp>

## Original question
[user's raw message]

## Framed question
[the framed question that all advisors saw]

## Advisor responses

### The Contrarian
[response]

### The First Principles Thinker
[response]

### The Expansionist
[response]

### The Outsider
[response]

### The Executor
[response]

## Anonymization mapping
- A = [advisor]
- B = [advisor]
- C = [advisor]
- D = [advisor]
- E = [advisor]

## Peer reviews

### Review 1
[review]

### Review 2
[review]

### Review 3
[review]

### Review 4
[review]

### Review 5
[review]

## Chairman synthesis
[full chairman output]
````

**Write the HTML report** as `.council/council-report-<ts>.html`. Single self-contained file. Inline CSS only — no external assets. Use a system font stack and a clean, document-looking layout (white background, subtle borders, generous whitespace, a soft accent color for section headers). Sections in order:

1. **Header:** the title "Council Verdict" and the original (un-framed) user question.
2. **Chairman verdict:** prominent. The five subsections (Agrees, Clashes, Blind Spots, Recommendation, One Thing to Do First) rendered as HTML headings + paragraphs. This is what most users will read; do not collapse it.
3. **Five `<details>` blocks** for advisor responses. Each `<summary>` is the advisor name. `open` attribute absent (collapsed by default).
4. **One `<details>` block** titled "Peer reviews" containing all 5 reviews concatenated with `<h3>` separators. Collapsed by default.
5. **Footer:** small text — timestamp, original question, anonymization mapping (so the user can audit which letter was which advisor).

When generating the HTML, escape user content with HTML entities (`&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`, `"` → `&quot;`). Convert markdown in advisor responses to HTML by handling at minimum: paragraph breaks (blank line → `<p>`), bold (`**x**` → `<strong>`), italic (`*x*` → `<em>`), and bullet lists (lines starting with `- ` → `<ul><li>`). Code blocks are not expected in advisor output and don't need handling.

**Open the report:**

```bash
if command -v open >/dev/null 2>&1; then
  open .council/council-report-<ts>.html
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open .council/council-report-<ts>.html
else
  echo "Report saved to .council/council-report-<ts>.html"
fi
```

If `.council/` is not writable (read-only filesystem, etc.), fall back to `$TMPDIR/council-<ts>/` and tell the user where it went.
`````

- [ ] **Step 2: Verify**

```bash
grep -c '^## Step ' ~/.claude/skills/llm-council/SKILL.md
grep -c '^```' ~/.claude/skills/llm-council/SKILL.md
```

Expected: 5 step-sections; even fence count.

---

## Task 8: Add the failure-modes summary

**Files:**
- Modify: `~/.claude/skills/llm-council/SKILL.md` (append)

- [ ] **Step 1: Append**

````markdown

## Failure modes

| Mode | Handling |
| --- | --- |
| One advisor returns empty / errors | Retry that slot once. If it still fails, proceed with 4 advisors and disclose the gap in the transcript and report. Do not abort. |
| One reviewer returns empty / errors | Retry once, then proceed with the reviews that returned. Tell the chairman how many reviews are present. |
| Chairman fails | Retry once. If it still fails, write the transcript anyway and tell the user the synthesis step failed. |
| `.council/` not writable | Fall back to `$TMPDIR/council-<ts>/`. Tell the user the path. |
| Neither `open` nor `xdg-open` available | Skip the auto-open step and print the absolute path to the report. |
| User invokes the council on a trivial question | Proceed — they explicitly asked. The trigger description discriminates at invocation time, not at runtime. |

## Operating notes

- **Always dispatch the 5 advisors in parallel** — one assistant message with 5 `Agent` tool calls.
- **Always dispatch the 5 reviewers in parallel** — same pattern.
- **Always anonymize before peer review.** Reviewer prompts must reference responses by letter only.
- **The chairman may disagree with the majority.** If 4 advisors say "do it" but the dissenter's reasoning is strongest, side with the dissenter and explain why.
- **The HTML report is the user-facing artifact.** Most users will not read the transcript. Make the verdict scannable.
- **Don't council trivial questions yourself.** The trigger description handles that; respect it.
````

- [ ] **Step 2: Verify the file is structurally sound**

```bash
python3 -c "import yaml; doc=open('$HOME/.claude/skills/llm-council/SKILL.md').read(); fm=doc.split('---',2)[1]; assert yaml.safe_load(fm)['name']=='llm-council'; print('OK frontmatter')"
grep -c '^```' ~/.claude/skills/llm-council/SKILL.md
grep -c '^## ' ~/.claude/skills/llm-council/SKILL.md
```

Expected: `OK frontmatter`; even fence count; `^## ` count of 8 (When-to / Five-advisors / Step1–5 / Failure modes — that's 8).

---

## Task 9: Smoke test the skill end-to-end

**Files:**
- No file modifications — this is a manual verification task.

- [ ] **Step 1: Set up a scratch directory**

```bash
mkdir -p /tmp/council-smoke && cd /tmp/council-smoke && rm -rf .council
ls -la
```

Expected: empty directory, no `.council/`.

- [ ] **Step 2: Reload the skill in a fresh Claude Code session**

The current session loaded the skills list at startup, so `llm-council` won't be visible until reload.

- Open a new Claude Code session in `/tmp/council-smoke`.
- Confirm in the system reminder that `llm-council` appears in the available-skills list.

- [ ] **Step 3: Run a real council question**

In the new session, send:

```
council this: should I use Postgres or SQLite as the backend for a 100-user internal expense-tracking tool with audit-log requirements?
```

Expected sequence:

1. Claude reads `~/.claude/skills/llm-council/SKILL.md` (no `CLAUDE.md` in `/tmp/council-smoke`, so the framing skips workspace context).
2. Claude frames the question and dispatches **5 `Agent` calls in one message** with `model: sonnet`.
3. After all 5 return, Claude dispatches **5 reviewer `Agent` calls in one message** with `model: sonnet` and anonymized responses.
4. Claude dispatches **1 chairman `Agent` call** with `model: opus`.
5. Claude writes `.council/council-transcript-<ts>.md` and `.council/council-report-<ts>.html`.
6. Claude creates `.council/.gitignore` containing `*`.
7. Claude runs `open .council/council-report-<ts>.html` (the report opens in the default browser).

- [ ] **Step 4: Verify output structure**

```bash
ls -la /tmp/council-smoke/.council/
cat /tmp/council-smoke/.council/.gitignore
```

Expected:
- exactly one `council-transcript-*.md` and one `council-report-*.html`
- `.gitignore` contents = `*`

- [ ] **Step 5: Inspect the transcript for parallelism + anonymization integrity**

Open the transcript. Check:

- All 5 advisor responses are present and distinct (different angles, no copying).
- No advisor response references another advisor by name or position. (E.g. no "as the Contrarian noted…" — that would mean parallel dispatch broke and one advisor saw another's output.)
- Peer reviews reference responses by letter (A–E) only, never by advisor name. (If reviews say "the Contrarian's response", anonymization broke.)
- The "Anonymization mapping" section is present and the letters do map to all 5 distinct advisors.
- Chairman synthesis has all 5 required subsections (Agrees, Clashes, Blind Spots, Recommendation, One Thing to Do First).

- [ ] **Step 6: Inspect the HTML report**

Open the report (already opened in browser by step 3, step 7). Check:

- Title + question visible at the top.
- Chairman verdict prominent, fully expanded — not collapsed.
- 5 collapsed `<details>` blocks for advisor responses, each labelled with the advisor name.
- 1 collapsed `<details>` block for peer reviews.
- Footer shows timestamp + original question + anonymization mapping.
- HTML escaping intact — no raw `<` or `&` from user content rendered as broken markup.
- The report renders without external network requests (no broken image icons, no spinning fonts).

- [ ] **Step 7: Trigger discrimination check**

In the same scratch session, send a question that should NOT trigger the council:

```
council this: what's the capital of France?
```

Expected: Claude either answers directly without convening the council, or asks a clarifying question. If Claude does spawn 5 advisors for this, the trigger description is too loose — re-read the spec's description string and tighten the "Do NOT trigger on…" guidance.

- [ ] **Step 8: Run a second council question to verify `.gitignore` is not overwritten**

```
council this: should I refactor before or after shipping the next feature?
```

Then:

```bash
ls /tmp/council-smoke/.council/*.html | wc -l
cat /tmp/council-smoke/.council/.gitignore
```

Expected: 2 HTML files now; `.gitignore` still contains exactly `*` (not duplicated, not changed).

- [ ] **Step 9: Cleanup**

```bash
rm -rf /tmp/council-smoke
```

If all the above passed, the skill is verified working.

---

## Self-review

**Spec coverage** — every section of the spec maps to a task:

| Spec section | Implementing task |
| --- | --- |
| Frontmatter / triggers | Task 1 |
| Five advisor identities | Task 2 |
| Step 1 framing + context enrichment | Task 3 |
| Step 2 advisor dispatch + advisor prompt template | Task 4 |
| Step 3 anonymization + peer review + reviewer prompt template | Task 5 |
| Step 4 chairman + chairman prompt template | Task 6 |
| Step 5 persistence (transcript + HTML + `.gitignore`) | Task 7 |
| Failure modes table | Task 8 |
| Manual verification | Task 9 |

**Placeholder scan** — no "TBD", "TODO", "implement later", or "similar to Task N". Bracketed placeholders inside prompt templates (`[framed question]`, `[response]`) are intentional template slots that the runtime Claude fills in.

**Type/name consistency** — file path is `~/.claude/skills/llm-council/SKILL.md` everywhere. Output dir is `.council/` everywhere. Models are `sonnet` (advisors + reviewers) and `opus` (chairman) consistently. Step section headings (`## Step 1` … `## Step 5`) match the workflow numbering in the spec.
