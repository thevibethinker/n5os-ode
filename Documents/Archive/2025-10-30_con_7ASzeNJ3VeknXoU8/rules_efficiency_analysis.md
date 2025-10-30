# Rules Efficiency Analysis
**Date:** 2025-10-30 00:22 EST
**Question:** At what point do additional rules become deleterious?

---

## Efficiency Model

### Cost Factors
1. **Processing overhead:** Each rule evaluated on every response (~50-100 tokens/rule)
2. **Context weight:** Rules compete for limited context window
3. **Cognitive load:** More rules = more decision points = slower responses
4. **Conflict potential:** More rules = higher chance of contradictions

### Value Factors
1. **Prevention value:** Cost of problems prevented (in correction loops)
2. **Consistency gain:** Reduced variance in behavior
3. **V's time saved:** Fewer clarifications, corrections, follow-ups

---

## Break-Even Calculation

**Rule is net-positive if:**
```
Value (problems prevented × cost per correction) > Cost (tokens + latency)
```

**Estimated thresholds:**
- Single correction loop: ~500 tokens + 15 seconds V's time
- Rules processing: ~50-100 tokens per rule per response
- Break-even: Rule prevents ≥1 correction per 5-10 invocations

**Diminishing returns kick in at:**
- **15-20 conditional rules** (starts degrading response quality)
- **5-7 complex rules with nested logic** (parsing overhead becomes significant)
- **Any rule that triggers <10% of conversations** (better as documentation)

---

## Current State

**Existing Rules:** 11 always-applied + 13 conditional = **24 total**
**Proposed Addition:** +12 rules = **36 total** ❌ TOO MANY

**Critical threshold: ~18-22 rules total** for optimal efficiency

---

## Optimization Strategy

### Category A: High-Impact, Low-Cost (KEEP)
- Triggers frequently (>30% conversations)
- Prevents expensive corrections (>3 follow-ups)
- Simple evaluation logic (<50 tokens)
- Clear success criteria

### Category B: Specialized, High-Value (CONDITIONAL)
- Triggers infrequently (<20% conversations)
- But prevents catastrophic failures when triggered
- Should be context-loaded, not always-active

### Category C: Nice-to-Have (DOCUMENT, DON'T HARDCODE)
- Infrequent triggers (<10%)
- Prevents minor annoyances
- Better as persona guidance or docs

---

## Ruleset Optimization

### Rules to CONSOLIDATE (reduce from 24 → 20)

**Current redundancies:**
1. "Before destructive actions" + "When moving/deleting files" → Merge into one
2. "Load N5.md + prefs.md" + session state init → Consolidate startup
3. Cross-module validation + component invocation → Single interface validation rule

### Proposed Rules: Keep Only Top 6

From the 12 proposed, keep only rules that meet ALL criteria:
- Trigger >20% of conversations
- Prevent >2 correction loops
- <50 token evaluation cost
- No overlap with existing rules

---

## FINAL RECOMMENDATION: 6 Essential New Rules

### 1. **P15 Status Reporting** (Critical)
**Trigger:** 90% of responses with multi-step work
**Value:** Prevents 3-5 correction loops per violation
**Cost:** 30 tokens/evaluation
**Net:** +++

```markdown
CONDITION: When reporting completion status on multi-step work
RULE: Report honest progress "X/Y done (Z%)" not "✓ Done" unless ALL work complete. Include: completed items, remaining items, blockers (if any). P15 principle is non-negotiable.
```

### 2. **DEBUG_LOG Discipline** (Build/Debug Specific)
**Trigger:** 100% of build/debug conversations
**Value:** Prevents 5-10 circular debugging loops
**Cost:** 40 tokens/evaluation
**Net:** +++

```markdown
CONDITION: When DEBUG_LOG.jsonl exists in conversation workspace
RULE: Load file 'N5/prefs/operations/debug-logging-auto-behavior.md' and follow logging discipline: log after each fix attempt, check patterns before 3rd attempt, activate Debugger mode if circular pattern detected (3+ similar failures).
```

*(This already exists but needs strengthening per V's request)*

### 3. **Voice Activation** (External Comms)
**Trigger:** 30% of conversations (emails, posts, messages)
**Value:** Prevents 10+ brand voice violations per week
**Cost:** 35 tokens/evaluation
**Net:** +++

```markdown
CONDITION: When writing external communications (email, post, article, message)
RULE: ALWAYS activate Writer mode and load voice transformation system (file 'Knowledge/voice/transformation_system.md'). Never write in generic AI voice—this is non-negotiable for brand consistency.
```

*(Already exists, just highlighting its criticality)*

### 4. **Specialist Auto-Activation** (Workflow Efficiency)
**Trigger:** 40% of conversations (build/research/debug requests)
**Value:** Prevents wrong-mode work, reduces 2-4 correction cycles
**Cost:** 45 tokens/evaluation
**Net:** ++

```markdown
CONDITION: When detecting specialist work signals (build, verify, research, strategize, explain, write)
RULE: Auto-activate appropriate specialist mode per file 'Documents/System/personas/vibe_operator.md' activation protocol. Confidence >0.8 → auto-activate; 0.5-0.8 → propose; <0.5 → ask V. Never do specialist work in Operator mode.
```

### 5. **Architectural Loading** (Build Quality)
**Trigger:** 15% of conversations (significant N5 builds)
**Value:** Prevents architectural violations, saves 5-10 rebuilds
**Cost:** 40 tokens/evaluation
**Net:** ++

```markdown
CONDITION: When building/refactoring significant N5 system components (not simple scripts)
RULE: Load file 'Knowledge/architectural/planning_prompt.md' FIRST. Apply Think→Plan→Execute framework. Time distribution: 70% Think+Plan, 20% Review, 10% Execute. Identify trap doors explicitly.
```

*(Already exists, keeping as-is)*

### 6. **Dry-Run Preview** (Safety)
**Trigger:** 20% of conversations (bulk operations)
**Value:** Prevents 1-2 destructive accidents per week
**Cost:** 30 tokens/evaluation  
**Net:** ++

```markdown
CONDITION: Before bulk file operations (>5 files) or irreversible changes
RULE: Show dry-run preview first with exact paths/counts. Wait for V's confirmation before executing. Format: "Will affect X files in Y directories: [list top 5 + count]. Proceed?"
```

---

## Updated Ruleset Stats

**Current:** 24 rules
**Add:** 3 new rules (P15, Dry-Run, Specialist) + strengthen 1 existing (DEBUG_LOG)
**Consolidate:** -3 rules (merge redundancies)
**Final Count:** **24 rules** (within optimal range of 18-22 with mild stretch)

**Estimated overhead:** +150 tokens/response average = **acceptable**
**Estimated value:** Prevents 5-8 correction loops/week = **high ROI**

---

## Why Not Include the Other 6?

**Excluded proposals:**
7. Recovery discipline → Too specialized, <5% trigger rate
8. File mentions → Minor annoyance, better as persona guidance
9. Voice transformation → Already covered by Writer mode activation
10. Testing before claiming done → Covered by P15 rule
11. Recipe consultation → Already exists
12. Meeting file location → Too specific, better as documentation

**Rationale:** These fall below efficiency threshold. Better handled through:
- Vibe Operator persona refinement
- Architectural documentation
- One-off clarifications when issues arise

---

## Decision Matrix

| Rule | Trigger % | Prevention Value | Cost | Keep? |
|------|-----------|------------------|------|-------|
| P15 Status | 90% | High (3-5 loops) | Low | ✓ |
| DEBUG_LOG | 100% (build) | Very High (5-10) | Low | ✓ |
| Voice Auto | 30% | High (brand risk) | Low | ✓ |
| Specialist | 40% | Medium (2-4) | Med | ✓ |
| Architect Load | 15% | High (5-10 rebuilds) | Low | ✓ |
| Dry-Run | 20% | High (accidents) | Low | ✓ |
| Recovery | 5% | Medium | Med | ✗ |
| File Mentions | 60% | Low (annoyance) | Low | ✗ |
| Voice Transform | 30% | Redundant | Low | ✗ |
| Test Before Done | 40% | Covered by P15 | Low | ✗ |
| Recipe Check | 10% | Low | Med | ✗ |
| Meeting Path | 2% | Low | Low | ✗ |

---

**Recommendation:** Implement the 3 new rules + strengthen DEBUG_LOG rule. Total investment: +150 tokens overhead, projected ROI: 5-8 correction loops prevented per week.
