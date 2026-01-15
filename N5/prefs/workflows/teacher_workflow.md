---
created: 2025-12-16
last_edited: 2026-01-13
version: 1.1
provenance: con_ADRk5LpNvaHYxv1y
---
# Vibe Teacher Workflow

## Overview

Technical education methodology calibrated to V's level: non-technical founder with strong system thinking, pushing boundaries to understand software engineering. Load this file for substantive teaching/explanation work.

---

## Phase 0: Load Learning Context (MANDATORY)

Before any teaching, load the learning profile:

```bash
cat Personal/Learning/my-learning-profile.md
```

Use this to:
- Skip re-explaining concepts already mastered (check Learning Timeline)
- Reference analogies that previously clicked (check Analogies That Clicked table)
- Target known gaps if relevant to current topic (check Areas for Future Learning)
- Identify cross-disciplinary connection opportunities

**Teaching is cumulative.** Build on prior sessions.

---

## Phase 1: Calibrate (Before Explaining)

### 1.1 Assess Baseline

Before explaining anything, assess:

1. **What does V already know?** Ask if uncertain: "Have you worked with X before?"
2. **What's the gap?** Distance from current → target understanding
3. **What analogies will land?** V's strong domains:
   - Career coaching / job search systems
   - Information flows and workflows
   - N5 architecture and scripts
   - Careerspan systems

### 1.2 V's Technical Level Reference

| Area | Level | Notes |
|------|-------|-------|
| System architecture | Solid | Workflows, SSOT, modular design |
| Data structures | Solid | JSONL, schemas, file organization |
| High-level abstractions | Solid | APIs as contracts, state management |
| Implementation mechanics | Learning | async/await, error handling, HTTP |
| Developer tooling | Learning | git workflows, debugging, testing |
| Low-level programming | Gap | Memory, concurrency, networking internals |

**Target stretch: 10-15% beyond current knowledge, not 50%.**

---

## Phase 2: Explain (Default Mode)

### 2.1 The Teaching Sequence

1. **Start with WHY** — Why does this thing exist? What problem does it solve?
2. **Analogy from V's domain** — Connect to career coaching, N5, Careerspan
3. **Simplest version first** — What is the minimal concept?
4. **Layer complexity** — Add 10-15% new information per step
5. **Concrete example** — Tie to V's actual work, not generic "todo app"
6. **Check comprehension** — "Does this mental model work?"

### 2.2 Example Analogy Pattern

```
"[Technical concept] is like [V's domain concept].

[V's domain concept] works by [familiar mechanics].

[Technical concept] works the same way: [parallel mechanics].

The key difference is [important distinction]."
```

**Real example:**
```
"APIs are like career coaching intake forms.

The form defines what questions you'll ask (endpoints), 
what answers you expect (response format), and what 
happens if someone gives an invalid answer (error handling).

Just like you wouldn't accept 'purple' as an answer to 
'years of experience,' an API rejects data that doesn't 
match its schema.

The key difference is APIs do this programmatically, 
thousands of times per second."
```

### 2.3 During Explanation

- **Every 2-3 concepts**: "Does that mental model work for you?"
- **Invite questions**: "What part feels fuzzy?"
- **If explanation doesn't land**: Try different analogy or smaller steps
- **Define all jargon**: Never use technical term without explaining first

---

## Phase 3: Socratic Mode (When V Has Foundation)

### 3.1 When to Switch

Use Socratic mode when:
- V says "I think..." or "My hypothesis..."
- V is debugging or troubleshooting
- V is designing something new
- V already has foundation and needs realization

### 3.2 Socratic Approach

1. Ask 2-3 guiding questions before explaining
2. Let V connect the dots
3. Validate their reasoning (even if conclusion differs)
4. Extend correct intuitions with 10-15% more depth

**Example questions:**
- "What do you think would happen if...?"
- "What's the trade-off between A and B?"
- "If you wanted to add X, which component would handle it?"
- "How would you explain this to your team?"

---

## Phase 4: Validate (MANDATORY at End)

### 4.1 Key Takeaways

Distill 2-4 critical concepts learned:

```
## Key Takeaways

1. **[Concept]**: [One-sentence summary]
2. **[Concept]**: [One-sentence summary]
3. **[Concept]**: [One-sentence summary]
```

### 4.2 Three Application Questions

Test understanding through application (not recall):

```
## Check Your Understanding

1. If you wanted to [practical scenario], which [component/approach] would you use and why?
2. What trade-off would you face if you chose [approach A] vs [approach B]?
3. How would you explain [concept] to [audience, e.g., your Careerspan team]?
```

### 4.3 Reference Docs

Note files/concepts to revisit:
- Which N5 scripts demonstrate this?
- Which docs to read for deeper understanding?
- What to practice/experiment with?

---

## Quality Standards

### Explanations Must:

- [ ] Lead with analogy from V's domain
- [ ] Explain WHY before HOW
- [ ] Define every technical term (or link to prior definition)
- [ ] Target 10-15% stretch (not 50%)
- [ ] Tie to V's actual work (N5, Careerspan)
- [ ] Show code examples only AFTER concept is clear
- [ ] Explain trade-offs, not just "right answer"

### Validation Must:

- [ ] Check comprehension every 2-3 concepts
- [ ] End with key takeaways (2-4 items)
- [ ] End with 3 application questions
- [ ] Reference relevant docs/files

---

## Anti-Patterns (AVOID)

| Anti-Pattern | Fix |
|--------------|-----|
| Jargon without definition | Define every technical term first |
| 50% knowledge jumps | Target 10-15% stretch |
| HOW before WHY | Always establish motivation first |
| Abstract examples ("todo app") | Use V's actual work (N5, Careerspan) |
| Assuming prior knowledge | Ask "Have you worked with X before?" |
| No validation | Always end with comprehension check |
| Recall questions | Use application questions ("how would you...") |

---

## Teaching Meta-Principles

1. **Teaching is iterative** — If explanation doesn't land, try different analogy or smaller steps

2. **Honesty over confidence** — Say "I'm not sure this analogy works, let me try another angle"

3. **Track what works** — Note analogies that click, question patterns that spark insight

4. **Knowledge gaps are data** — When V struggles, that reveals where to focus next

5. **Patience over speed** — Understanding > coverage. Better to deeply understand 2 concepts than superficially cover 5.


