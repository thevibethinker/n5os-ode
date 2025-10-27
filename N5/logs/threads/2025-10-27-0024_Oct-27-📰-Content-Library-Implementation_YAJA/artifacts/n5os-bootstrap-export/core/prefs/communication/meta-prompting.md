# Prompt Engineering & Meta-Prompting

**Module:** Communication  
**Version:** 2.0.0  
**Date:** 2025-10-09

---

## Outcome-First Interrogatories

Start every complex task with these questions:

### 1. Job of the Text
**"What decision should this drive, and for whom?"**

- Identify the primary audience
- Identify the decision they need to make
- Identify the action they need to take

### 2. Define Success
Specify clearly:
- **Metric:** How will success be measured?
- **Audience:** Who is the primary consumer?
- **Time horizon:** When is this needed? When does it expire?
- **Constraints:** What are the boundaries? (scope, length, tone, format)

### 3. Deliverable Spec
- **Format:** YAML, Markdown, JSON, PDF, etc.
- **Length cap:** Maximum words/pages
- **Voice:** Which tone profile? (see `file 'N5/prefs/communication/voice.md'`)
- **Citations:** Are sources required?

### 4. Steps Most Often Refined

**Constraints (Step 2):**
- Clarifying scope boundaries
- Defining guardrails
- Specifying what to explicitly exclude

**Deliverable (Step 3/4):**
- Tightening format requirements (YAML/Markdown)
- Adding version tags
- Ensuring line-edit readiness

---

## Clarifiers & Inference Helpers

### Socratic Clarifiers

**Use when:** Ambiguity would cause churn

**Limit:** 3 crisp questions maximum

**Example questions:**
1. "Who is the primary decision-maker for this?"
2. "What's the OMTM (one metric to move) here?"
3. "What should we explicitly exclude from scope?"

### Auto-Inference

**Apply liberally for obvious defaults:**
- Absolute dates (never relative like "tomorrow")
- Source citations for recent facts
- Structured sections (headers, bullets)
- Version tags for iterative documents

### Relevance Scoring

**Mid-high preference (3-5 / 5)** for clarifiers on:
- High-stakes outputs
- External-facing content
- Strategic decisions
- New/unfamiliar territory

**Low preference (1-2 / 5)** for clarifiers on:
- Routine tasks
- Clear patterns from history
- Low-stakes internal docs

---

## Enhancement Passes

### Red-Team Critique Pass

**Purpose:** Strengthen reasoning and catch weaknesses

**What to check:**
- Weak claims without evidence
- Missing disconfirmers or counter-examples
- Hand-wavy steps that skip complexity
- Overconfident predictions

**Output:** List of vulnerabilities with suggested fixes

---

### Tighten & Compress Pass

**Purpose:** Remove filler, maximize signal

**What to cut:**
- Throat-clearing intros ("It's important to note that...")
- Redundant phrasing
- Vague qualifiers ("somewhat," "generally")
- Unnecessary hedging

**Keep:**
- Concrete claims
- Specific examples
- Actionable steps

---

### Options with Pros/Cons + Risks

**Purpose:** Improve decision-readiness

**Format:**
```markdown
## Option A: [Name]
**Pros:**
- Benefit 1
- Benefit 2

**Cons:**
- Drawback 1
- Drawback 2

**Risks:**
- Risk 1 (mitigation: [how to reduce])
- Risk 2 (mitigation: [how to reduce])
```

---

### /diff Mindset

**Purpose:** Make iteration transparent

**Format:**
```markdown
## Changes from v1.2 to v1.3

**Added:**
- Section on X
- Clarified Y

**Removed:**
- Redundant intro
- Outdated reference to Z

**Modified:**
- Updated timeline (was Q3, now Q4)
- Strengthened CTA (added owner + date)
```

---

### /breakdown Mindset

**Purpose:** Decompose vague asks

**Process:**
1. Identify the high-level request
2. Break into 3-5 concrete sub-tasks
3. For each sub-task:
   - Owner (who)
   - Due date (when)
   - Success criteria (what "done" looks like)
   - Risks/blockers

---

## Nuances Toggle Reference

### Most-Used Toggles

**ON by default:**
- `ClarityOverVerbosity` — Bias toward concise
- `Tool-Aware` — Use search/citations when facts are fresh
- `Evidence-First, Primary-Source Bias` — For research
- `Reversible-First Decisions` — Prefer low-risk, reversible options
- `Candidate-First` — Careerspan lens (see `file 'Knowledge/stable/company/principles.md'`)
- `Memory Granularity` — Prefer small, named modules over blobs

### Nuance Harvests Added

Patterns to remember:
- **rails-not-rules** — Guidelines over strict enforcement
- **bad-first-version** — Ship to learn, iterate
- **24-hour shortlist** — Fast turnaround for candidate lists
- **community-validated talent** — Peer validation for quality
- **avoid ATS integrations early** — Focus on human value first
- **absolute dates** — Never "tomorrow" without date
- **two-step CTAs** — Primary ask + fallback option

---

## Adaptive Interrogatory Behaviors

### Probes That Clarify Fast

Ask these to resolve ambiguity quickly:
1. **Audience:** Who is this for?
2. **Decision owner:** Who makes the call?
3. **OMTM:** What's the one metric to move?
4. **Time horizon:** When is this needed? When does it expire?
5. **Privacy/compliance constraints:** Any sensitive data?
6. **Explicitly exclude:** What should we NOT include?

### Decision Hygiene

When recommending options:
- Include disconfirmers (reasons it might not work)
- Provide counter-examples
- State assumptions explicitly
- Note confidence level (high / medium / low)

---

## User-Value Features

### Applied Features & Impact

**Web search + citations:**
- Higher accuracy on news/policy
- Reduces back-and-forth clarifications
- Builds trust with sourced claims

**Output polish:**
- Readability boost (Flesch-Kincaid 10-12)
- Fewer long sentences
- Clearer headers and structure

**Diagrams (when helpful):**
- Turn messy plans into visual flows
- Clarify complex relationships
- Aid understanding for non-technical audiences

**Task suggestions (lightweight):**
- Convert outputs into 1-3 next actions
- Specify owner + date
- Provide fallback options

---

## Meta-Enhancements

### Observed Patterns

User (V) prefers:
- YAML/Markdown scaffolds for structured content
- Explicit version tags (v1.2, v2.0)
- Owner + date on all action items
- Reversible-first decision recommendations

### Suggested Refinements

To build out:
1. **Smaller, reusable CTA snippets** (library in `file 'N5/prefs/communication/templates.md'`)
2. **Centralized style guide** for external vs. internal comms
3. **Stable lexicon list** with allowed/avoid examples (see `file 'N5/prefs/communication/voice.md'`)

---

## Related Files

- **Voice & Style:** `file 'N5/prefs/communication/voice.md'`
- **Templates:** `file 'N5/prefs/communication/templates.md'`
- **Company Principles:** `file 'Knowledge/stable/company/principles.md'`
- **Operational Principles:** `file 'Knowledge/architectural/operational_principles.md'`

---

## Change Log

### v2.0.0 — 2025-10-09
- Extracted from monolithic prefs.md
- Organized into clear workflow sections
- Added decision hygiene section
- Expanded enhancement passes with examples
- Added /diff and /breakdown mindsets
- Cross-referenced related knowledge files
- Preserved all nuance toggles and preferences
