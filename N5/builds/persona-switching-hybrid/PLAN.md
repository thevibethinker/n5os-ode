---
created: 2026-02-08
last_edited: 2026-02-08
version: 1.0
provenance: con_ZEHFBcGBGSVDzqZR
---

# PLAN: Hybrid Persona Switching System

## Open Questions

1. ~~**Which personas get hard-switch rules vs. methodology injection?**~~ — **Resolved:** Debugger, Writer, Strategist, Builder for hard-switch. Researcher, Teacher for injection. V confirmed and added Builder.
2. ~~**Should the return-to-Operator rule (091bcb5c) be updated?**~~ — **Resolved:** No change needed; it already uses the correct Operator ID.
3. ~~**What's the canonical Operator persona ID?**~~ — **Resolved:** `3700edcc-9785-4dee-9530-ad4a440293d9`. Fixed stale ID in both router scripts.

## Context

V has observed that persona switching almost never happens in practice despite extensive infrastructure (routing contract, router script, persona prompts with handoff sections). The core diagnosis: LLMs don't naturally self-interrupt to call `set_active_persona()` before responding. The system relies on semantic judgment that consistently loses to conversational momentum.

V and Aaron Mak independently concluded (2025-11-13): "explicit routing >> implicit semantic routing." This build implements that insight.

### Design Decision: Pathway 3 (Hybrid)

**Hard-switch** (mechanical rules) for personas where cognitive stance genuinely differs:
- **Debugger** — Skeptic stance, 5-phase methodology, principle compliance
- **Writer** — Voice protocol, audience awareness, tone shift
- **Strategist** — Multi-path thinking, options generation, tradeoff framing

**Methodology injection** (load file as context) for personas where frameworks are useful but stance doesn't need to change:
- **Researcher** — Search methodology, source synthesis
- **Teacher** — Explanation frameworks, analogy generation

**Untouched** (routing stays as-is):
- **Builder** — Already has Architect gating as a forcing function
- **Architect** — Already has plan-gating rule enforcement
- **Level Upper** — Meta-persona, invoked explicitly

## Alternatives Considered (Nemawashi)

### A. Pure Hard Rules (All personas get mechanical switch rules)
- **Pro:** Simple, consistent mechanism
- **Con:** Over-switching. "Fix this typo" triggers Debugger 5-phase methodology. High friction for lightweight tasks.
- **Rejected:** Too blunt. Would create switching fatigue.

### B. Pure Methodology Injection (No switching at all — Aaron's pattern)
- **Pro:** Zero switching friction. Methodologies always available.
- **Con:** Operator becomes god-persona. Loses the cognitive "mode shift" that genuine persona switching creates. System prompt bloat from loading full methodology files.
- **Rejected:** Loses real value of personas (stance change, not just technique access).

### C. Hybrid (Selected — Pathway 3)
- **Pro:** Hard switches where stance matters, injection where technique matters. Minimal rules (3 hard-switch + 2 injection). Testable incrementally.
- **Con:** More complex mental model (two mechanisms). Need to get the boundary right.
- **Selected:** Best balance of reliability and value.

## Trap Doors

1. **⚠️ Rule creation is reversible** — Rules can be edited/deleted. Low risk.
2. **⚠️ Persona prompt edits are reversible** — Can revert via edit_persona. Low risk.
3. **⚠️ Router script changes are reversible** — Can revert file. Low risk.
4. **✅ No trap doors identified** — All changes are easily reversible.

## Checklist

### Phase 1: Hard-Switch Rules (Core)
- ☑ Create conditional rule: Debugger hard-switch (`866b1ec2`)
- ☑ Create conditional rule: Writer hard-switch (`c498e973`)
- ☑ Create conditional rule: Strategist hard-switch (`77b48c04`)
- ☑ Create conditional rule: Builder hard-switch (`f145a902`)
- ☑ Verify Operator ID consistency across all references
- ☐ Test each rule with representative messages

### Phase 2: Methodology Injection Rules
- ☑ Create conditional rule: Researcher methodology injection (`8d17445b`)
- ☑ Create conditional rule: Teacher methodology injection (`f39f560d`)
- ☑ Verify methodology files exist and are loadable at referenced paths

### Phase 3: Cleanup & Documentation
- ☑ Update routing contract to reflect hybrid model (Section 11)
- ☑ Fix stale Operator ID in router scripts (v1 + v2)
- ☑ Update Operator persona doc to describe new routing behavior
- ☑ Remove/deprecate conflicting guidance (no conflicts found; Writer rule reinforces existing voice protocol)

---

## Phase 1: Hard-Switch Rules

### Affected Files
- Zo Rules (3 new conditional rules via `create_rule`)
- No file system changes

### Changes

**Rule 1: Debugger Hard-Switch**
```
CONDITION: When the task involves debugging, troubleshooting, diagnosing errors, or fixing broken functionality — AND the work is substantive (not a quick typo fix)

RULE: MUST call set_active_persona("17def82c-ca82-4c03-9c98-4994e79f785a") before ANY substantive response.

Trigger signals:
- V says "debug", "troubleshoot", "figure out why X isn't working"
- An error has occurred and V asks to fix/investigate it
- V says "what's broken", "why is this failing"
- Repeated failures on the same issue (3+ attempts)

NOT a trigger:
- Simple typo fixes or one-line corrections
- "Fix the spacing here"
- Quick config changes

After switching, Debugger must load its methodology from the persona prompt and follow the 5-phase approach.
```

**Rule 2: Writer Hard-Switch**
```
CONDITION: When generating substantial text (>2 sentences) that will represent V externally — emails, posts, blurbs, articles, proposals, outreach

RULE: MUST call set_active_persona("5cbe0dd8-9bfb-4cff-b2da-23112572a6b8") before drafting.

Note: This strengthens the existing voice protocol rule (47b9abb9) which already says "Route to Writer persona for any substantial drafting (>2 sentences)" but is advisory. This makes it mechanical.
```

**Rule 3: Strategist Hard-Switch**
```
CONDITION: When V is making a decision between options, evaluating tradeoffs, planning a roadmap, or needs multi-path thinking — AND the decision is consequential (not "should I name this file X or Y")

RULE: MUST call set_active_persona("39309f92-3f9e-448e-81e2-f23eef5c873c") before substantive analysis.

Trigger signals:
- V says "help me think through", "what are my options", "should we X or Y"
- V is weighing a business/career/architecture decision
- V asks for a framework or structured analysis
- Multiple viable paths exist and the choice matters

NOT a trigger:
- Simple preference questions
- Binary yes/no decisions with obvious answers
- Implementation choices within an already-decided direction
```

**Operator ID Verification:**
- Canonical ID from routing contract + return-to-Operator rule: `3700edcc-9785-4dee-9530-ad4a440293d9`
- Router script has stale ID: `90a7486f-46f9-41c9-a98c-21931fa5c5f6` — needs fix in Phase 3

### Unit Tests
- Test: Say "debug why this script is failing" → Verify Debugger activates
- Test: Say "draft an email to X about Y" → Verify Writer activates
- Test: Say "should we go with approach A or B" → Verify Strategist activates
- Test: Say "fix this typo" → Verify NO switch happens (stays Operator)
- Test: Say "rename this file" → Verify NO switch happens

---

## Phase 2: Methodology Injection Rules

### Affected Files
- Zo Rules (2 new conditional rules via `create_rule`)
- No file system changes

### Changes

**Rule 4: Researcher Methodology Injection**
```
CONDITION: When V asks to research a topic, find information, investigate, scan sources, or gather intelligence — AND the work requires systematic multi-source research (not a quick lookup)

RULE: Before proceeding, load the Researcher methodology:
1. Read: file 'Documents/System/personas/vibe_researcher_persona.md' (or equivalent live reference)
2. Apply the systematic search methodology, source evaluation, and synthesis framework
3. Stay as current persona (do NOT switch) — use the methodology as technique, not stance

NOT a trigger:
- Quick "what is X" questions answerable from training data
- Single-source lookups
- Checking a specific fact
```

**Rule 5: Teacher Methodology Injection**
```
CONDITION: When V asks for a deep explanation of a concept, wants to understand how something works, or explicitly asks to learn — AND the explanation requires substantial depth (not a one-liner)

RULE: Before proceeding, load the Teacher methodology:
1. Read: file 'Documents/System/personas/vibe_teacher_persona.md' (or equivalent)
2. Apply scaffolded explanation approach, analogy generation, and knowledge-level calibration
3. Stay as current persona (do NOT switch) — use the methodology as technique, not stance

Note: V's existing always-on rule about non-technical explanations (905df1e4) already covers light teaching. This rule activates the FULL teaching framework for deep dives.
```

### Unit Tests
- Test: "Research the top 5 competitors in X space" → Verify methodology loads but persona doesn't switch
- Test: "Explain how vector databases work in depth" → Verify teaching framework loads but persona doesn't switch
- Test: "What is a Dockerfile?" → Verify NO methodology injection (too simple)

---

## Phase 3: Cleanup & Documentation

### Affected Files
- `N5/prefs/system/persona_routing_contract.md` (update)
- `N5/scripts/persona_router_v2.py` (fix Operator ID)
- `Documents/System/personas/vibe_operator_persona.md` (update)

### Changes

1. **Update routing contract** — Add new Section 11: "Hybrid Switching Model" documenting:
   - Which personas use hard-switch rules (Debugger, Writer, Strategist)
   - Which use methodology injection (Researcher, Teacher)
   - Which retain current routing (Builder, Architect, Level Upper)
   - The design rationale (Aaron Mak meeting insight)

2. **Fix router script** — Update Operator ID from `90a7486f` to `3700edcc` to match canonical SSOT

3. **Update Operator persona doc** — Add section describing how hard-switch rules change Operator's routing behavior (Operator no longer needs to "decide" for 3 personas — rules force the switch)

### Unit Tests
- Verify router script Operator ID matches routing contract
- Verify routing contract has hybrid model section
- Verify no conflicting guidance between old and new sections

---

## Success Criteria

1. **Debugger activates** when V says "debug" in a substantive context — measurable by checking active persona in subsequent response
2. **Writer activates** when V asks to draft external-facing text >2 sentences
3. **Strategist activates** when V asks to weigh options or make consequential decisions
4. **No false switches** on lightweight tasks (typo fixes, simple questions, quick lookups)
5. **Methodology injection loads** for Researcher/Teacher without switching personas
6. **All persona IDs consistent** across rules, routing contract, and router script

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-switching on ambiguous messages | Medium — friction, interrupts flow | Explicit "NOT a trigger" exclusions in each rule; V can always say "stay as Operator" |
| Rules conflict with existing voice protocol rule | Low — redundancy | Writer rule reinforces existing rule 47b9abb9; no conflict, just stronger enforcement |
| LLM still ignores mechanical rules | High — entire build fails | Monitor for 2 weeks; if rules don't fire, escalate to fundamentally different approach |
| Methodology injection bloats context | Low — files are ~2-3K tokens each | Only load when triggered, not always-on |
