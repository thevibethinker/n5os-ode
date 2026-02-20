---
created: 2026-02-19
last_edited: 2026-02-19
version: 1.0
type: build_plan
status: complete
provenance: con_adqlbbwFE3aw6RHS
---
# Plan: Socratic Information Sufficiency Gate (ISG)

**Objective:** Ensure Zo asks proportionally deep clarifying questions before executing important tasks, with mandatory multi-round questioning for high-stakes work — eliminating the current "opt-in" pattern where AI self-assesses whether it needs to ask.

**Trigger:** V audit revealed 6 separate touchpoints that all say "ask if in doubt" but none enforce mandatory questioning. The AI can always rationalize "I'm confident enough" and skip. Most important builds and decisions suffer from insufficient information gathering.

**Design Principle:** Simple > Easy. Prefer one strong rule over many weak rules. Leverage the proven hybrid switching model (mechanical triggers > AI discretion) to enforce questioning behavior.

---

## Open Questions

- [x] Path selection: Full tier system vs. hybrid vs. lazy solution? → **Path C (Hybrid)** selected per Level Upper analysis. One rule rewrite + one new conditional rule + minor persona tweaks. Best ratio of enforcement to complexity.
- [ ] Should the ISG gate for scheduled agents be in-scope? → **No.** Agents can't ask questions. Separate concern for a future build.
- [ ] Should the confidence framework be updated? → **Optional enhancement.** Noted in Phase 2 but not blocking.

---

## Nemawashi: Alternatives Considered

### Path A: Lazy Solution (One Rule Rewrite)
- Rewrite global rule 32ace0a3 to force assumption-surfacing + mandatory questioning for "major work"
- **Pros:** Minimal change, low context tax
- **Cons:** Still relies on AI to classify what's "major." No mechanical trigger.
- **Verdict:** Too weak as standalone. The current rule already says "ask if in doubt" — rewording it differently won't change the incentive structure.

### Path B: Full 4-Tier ISG Classification System
- T1 (Mechanical): No questions. T2 (Standard): 1-2 questions. T3 (Strategic): 3-5 questions + multi-round. T4 (Critical): Full Socratic deep-dive.
- **Pros:** Elegant, proportional, comprehensive
- **Cons:** Self-classification vulnerability (AI picks the tier), context tax (another classification step per conversation), over-engineering for the problem
- **Verdict:** Too complex. Adds a classification layer that has the same opt-in problem at a different level.

### Path C: Hybrid — Mechanical Triggers + Assumption Surfacing ✅
- Rewrite global rule to force **assumption surfacing** (what do I know / what don't I know) before acting
- Add **conditional rules** that make questioning mandatory for known high-stakes patterns (the same patterns that already trigger persona switches: builds, strategy, writing)
- The mechanical triggers piggyback on existing hard-switch rules, avoiding a new classification layer
- **Pros:** Uses proven enforcement pattern, minimal new surface area, proportional naturally (heavy personas = heavy questioning)
- **Cons:** Doesn't cover edge cases where a task seems simple but is actually complex
- **Mitigation for cons:** The assumption-surfacing in the global rule catches these — when stated assumptions reveal gaps, questioning kicks in

### Level Upper Divergent Contributions
- ✅ Incorporated: "The laziest solution" insight → hybrid is closer to lazy than to complex
- ✅ Incorporated: "Self-classification is the vulnerability" → avoid new classification layer, use existing mechanical triggers
- ✅ Incorporated: "Post-execution confidence check" → added to Phase 2 as optional enhancement
- ❌ Rejected: "Just change the output side" (no input gating) → V explicitly wants pre-execution questioning, not just post-hoc review
- ❌ Rejected: "More questions ≠ better output" → true in general, but the current failure mode is clearly too few questions, not too many

---

## Trap Doors

1. **Rule edits are reversible** — can always revert. No trap doors.
2. **Persona file edits are reversible** — reference docs, not live prompts. Low risk.
3. **Over-questioning risk** — if rules are too aggressive, V gets annoyed by unnecessary Q&A. Mitigation: explicit exclusion list in the conditional rule for trivial tasks.

---

## Checklist

### Phase 1: Core Rule Changes
- ☑ Rewrite global rule 32ace0a3 (assumption-surfacing before action)
- ☑ Create new conditional rule: mandatory multi-round questioning for build/strategy/writing persona triggers
- ☑ Update critical_reminders.txt item #5 (Ambiguity Detection) to reference the new ISG pattern
- ☑ Test: Verify rules load correctly (list_rules)

### Phase 2: Persona Alignment
- ☑ Update Operator persona reference doc — "Intent & Scope Discovery" section to reference ISG
- ☑ Update Strategist mode doc — make Socratic questioning mandatory (not a switchable style) for the first round
- ☑ Test: Read updated files, verify no contradictions with existing rules

---

## Phase 1: Core Rule Changes

### Affected Files
1. **Rule 32ace0a3** (global, always-on) — `edit_rule`
2. **New conditional rule** — `create_rule`
3. `N5/prefs/system/critical_reminders.txt` — line edit to item #5

### Changes

#### 1a. Rewrite Global Rule 32ace0a3

**Current text:**
> "If you are in any doubt about my objectives, priorities, target persona, intended audience, or any and all details that would materially affect your response, ask a minimum of 3 clarifying questions before proceeding with any action"

**New text:**
> Before acting on any non-trivial request, surface your understanding by stating: (1) what you believe the objective is, (2) what assumptions you're making, and (3) what you DON'T know that could materially affect the output. If you have ≥2 unverified assumptions or knowledge gaps, ask clarifying questions before proceeding. The number of questions should be proportional to the task's stakes and complexity — at minimum 2 for standard tasks, 3-5 for significant tasks.

**Why this is better:**
- Removes the "if in doubt" opt-in. Assumption-surfacing is always required for non-trivial work.
- Naming what you don't know is harder to skip than assessing whether you "feel doubtful."
- Proportionality is explicit: more complex = more questions.
- Still allows zero questions for genuinely trivial tasks (file moves, simple lookups).

#### 1b. New Conditional Rule — Mandatory Deep Questioning for High-Stakes Personas

**Condition:** When operating as or transitioning to Builder, Strategist, Writer, or Architect for substantive work

**Instruction:**
> Questioning is MANDATORY before execution, regardless of confidence level. This is a hard gate — do not begin implementation, strategic analysis, external-facing writing, or system design until at least one round of clarifying questions has been asked AND answered by V. For builds and system design, require a second round if the first round reveals additional unknowns. For strategy, explore V's constraints, values, and non-obvious preferences before recommending. For writing, confirm audience, tone, purpose, and any sensitivities. This gate cannot be self-waived.

**Why a separate rule:** The global rule handles assumption-surfacing. This rule adds the **hard gate** specifically for the personas where insufficient questioning causes the most damage. It piggybacks on the existing hard-switch trigger patterns (same condition signals) so there's no new classification layer.

#### 1c. Critical Reminders Update

Update item #5 from:
```
5. AMBIGUITY DETECTION
   - Ambiguous requests → ask clarifying questions BEFORE acting
   - Examples: "delete meetings" "fix the code" "update everything"
   - Pattern: Scope + Target + Confirmation
```

To:
```
5. INFORMATION SUFFICIENCY GATE (ISG)
   - ALL non-trivial requests → surface assumptions + knowledge gaps BEFORE acting
   - High-stakes personas (Builder, Strategist, Writer, Architect) → MANDATORY questioning gate
   - Pattern: State objective → List assumptions → Identify gaps → Ask proportional questions
   - Examples of mandatory gate: "build me X", "help me decide Y", "write Z for [audience]"
   - Examples of pass-through: "move this file", "what time is it", "read me that doc"
```

### Unit Tests (Phase 1)
- `list_rules` returns updated rule and new rule
- Read `critical_reminders.txt` and verify item #5 updated
- No contradictions with existing rules (manual scan)

---

## Phase 2: Persona Alignment

### Affected Files
1. `Documents/System/personas/vibe_operator_persona.md` — Section "Intent & Scope Discovery"
2. `Documents/System/personas/vibe_strategist_mode.md` — "Dynamic Styles" section

### Changes

#### 2a. Operator Persona — Intent & Scope Discovery

Add after the existing "Asks clarifying questions until the objective, audience, and constraints are clear" bullet:

> **ISG Protocol:** For any non-trivial request, explicitly state your understanding (objective, assumptions, gaps) before asking questions. This surfaces blind spots that pure "do I feel doubtful?" self-assessment misses. For tasks routing to Builder, Strategist, Writer, or Architect, questioning is mandatory — do not route until at least one round of Q&A is complete.

#### 2b. Strategist Mode — Socratic as Default Requirement

Change the "Dynamic Styles" section so Socratic is not a switchable option but a required first pass:

> **Socratic Baseline (REQUIRED for Round 1):** First exchange with V must include 3-5 clarifying questions exploring objectives, constraints, values, and non-obvious preferences. This is mandatory regardless of style selection. Other styles (Aggressive, Hater, etc.) layer ON TOP of the Socratic baseline after Round 1.

### Unit Tests (Phase 2)
- Read each updated file, verify changes are non-contradictory
- Verify no breakage in persona routing (changes are additive, not restructuring)

---

## Deferred (Out of Scope)

- **Confidence framework integration:** Connect LOW confidence → questioning escalation. Nice-to-have but the conditional rule already makes questioning mandatory for high-stakes personas regardless of confidence level. Future enhancement.
- **Scheduled agent ISG:** Agents can't ask questions. Separate concern requiring a different solution (e.g., pause-and-escalate mechanism). Separate build.

---

## Success Criteria

1. **Mechanical enforcement:** Builder, Strategist, Writer, Architect sessions cannot proceed without at least one round of Q&A (enforced by conditional rule, not AI discretion)
2. **Assumption surfacing:** Every non-trivial request gets explicit "here's what I think you want / here's what I don't know" before action
3. **Proportionality:** Quick tasks (file ops, lookups) aren't gated. Major tasks get deep questioning.
4. **No context tax increase:** Total rule count increases by 1. No new scripts, no new classification systems, no new conversation-start overhead.
5. **Backward compatible:** Doesn't break any existing workflow, persona routing, or scheduled agents.

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Over-questioning on tasks V considers obvious | Medium | Annoyance, slower throughput | Explicit pass-through examples in critical reminders; "non-trivial" qualifier in global rule |
| AI still skips questioning by rationalizing tasks as "trivial" | Low-Medium | Defeats the purpose | Conditional rule on persona triggers is mechanical, not discretionary |
| V gets fatigued by mandatory Q&A and disables rules | Low | Loses the system | Proportionality built in; V can always say "just proceed" to override in-conversation |
| Persona files and rules drift out of sync over time | Medium | Inconsistent behavior | Phase 2 changes reference the rule rather than duplicating logic |
