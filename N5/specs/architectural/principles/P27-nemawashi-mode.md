# P27: Nemawashi Mode

**Category:** Strategy  
**Priority:** High  
**Related:** P23 (Trap Doors), P24 (Simulation), P32 (Simple Over Easy)

---

## Principle

**Explore 2-3 alternatives before committing to any approach. Build consensus with yourself through deliberate option evaluation.**

Nemawashi (根回し) is a Japanese decision-making process: circulate proposals, gather input, build consensus before formal decisions. Applied to system design: explore multiple viable approaches, evaluate trade-offs, choose consciously rather than defaulting to the first idea.

---

## The Problem

**First-idea trap:**
- Think of approach
- Seems reasonable
- Implement immediately
- Discover better option later
- Sunk cost prevents switching

**Cost:** Suboptimal architecture, missed opportunities, regret.

**Nemawashi approach:**
- Think of approach A
- Force yourself to consider B and C
- Evaluate trade-offs explicitly
- Choose best option
- Implement with confidence

**Benefit:** Better decisions, fewer regrets, optimal solutions.

---

## Recognition

**When to use Nemawashi mode:**
- Making trap door decisions
- Choosing core abstractions
- Selecting data formats
- Picking external dependencies
- Designing module interfaces

**Nemawashi is NOT needed for:**
- Easily reversible choices
- Implementation details
- Variable names
- Cosmetic decisions

**Key indicator:** If it's hard to reverse, explore alternatives first.

---

## Application

### Nemawashi Template

```markdown
## Decision: [What you're choosing]

### Option A: [First idea]
**Pros:**
- [Advantage 1]
- [Advantage 2]

**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]

**Trade-offs:**
- [What you gain vs. lose]

---

### Option B: [Alternative approach]
**Pros:**
- [Advantage 1]
- [Advantage 2]

**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]

**Trade-offs:**
- [What you gain vs. lose]

---

### Option C: [Third approach]
**Pros:**
- [Advantage 1]
- [Advantage 2]

**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]

**Trade-offs:**
- [What you gain vs. lose]

---

### Decision: [Chosen option]
**Rationale:** [Why this one?]
**Rejected because:** [Why not the others?]
**Reversibility cost:** [Low/Medium/High - effort to change]
```

---

### Example: N5 Command Storage

```markdown
## Decision: How to store N5 commands

### Option A: JSONL File
**Pros:**
- Human-readable (P1)
- Simple append for adds
- Grep-friendly lookups
- No external dependencies (P8)

**Cons:**
- Updates require full file rewrite
- No built-in validation
- Manual indexing

**Trade-offs:**
- Simplicity + portability vs. query power

---

### Option B: SQLite Database
**Pros:**
- Powerful queries
- Built-in indexing
- Transactional updates
- Schema validation

**Cons:**
- Binary format (not P1)
- Requires schema migration
- Adds complexity
- Harder to backup/version

**Trade-offs:**
- Query power vs. simplicity + portability

---

### Option C: Directory of JSON Files
**Pros:**
- Maximum flexibility
- Easy per-command editing
- Natural organization
- Git-friendly

**Cons:**
- Harder to query all commands
- Coordination overhead
- More files to manage

**Trade-offs:**
- Flexibility vs. cohesion

---

### Decision: JSONL (Option A)
**Rationale:**
- Aligns with P1 (human-readable), P8 (minimal dependencies)
- Expected scale <100 commands (SQLite overkill)
- Updates are rare (rewrites acceptable)
- Grep satisfies query needs

**Rejected B because:**
- Too complex for current scale
- Binary format violates P1
- Migration risk for small benefit

**Rejected C because:**
- Over-flexible for simple use case
- Coordination complexity unnecessary

**Reversibility cost:** Medium (~4 hours to migrate to SQLite if needed)
```

---

### Nemawashi in the Think Phase

**Think → Plan → Execute framework:**

**Think phase (40%):**
1. **Identify the decision** (what am I choosing?)
2. **Generate 2-3 alternatives** (force divergent thinking)
3. **Evaluate trade-offs** (explicit pros/cons)
4. **Choose consciously** (not by default)
5. **Document rationale** (for future reference)

This process takes 15-30 minutes. It prevents hours/days of regret.

---

## Integration with Other Principles

**With P23 (Trap Doors):**
- Nemawashi is HOW you handle trap door decisions
- Identify trap door → Nemawashi mode → Choose wisely

**With P24 (Simulation):**
- Nemawashi explores options in prose
- Simulation tests options in prototype
- Together: thorough evaluation before commitment

**With P32 (Simple Over Easy):**
- Nemawashi often reveals that "easy" option has hidden complexity
- Forces evaluation of "simple" alternatives

---

## Anti-Patterns

❌ **Forcing three options:** Sometimes two is enough  
❌ **Analysis paralysis:** Diminishing returns after 30 minutes  
❌ **Fake alternatives:** Option A, Option A-but-worse, Option A-but-different-name  
❌ **Post-hoc rationalization:** Deciding first, then "exploring alternatives"  

---

## Tools

**Prose evaluation:**
- Markdown decision documents
- Trade-off matrices
- Architecture diagrams showing alternatives

**Code evaluation:**
- Throwaway prototypes (P25: Code Is Free)
- Spike implementations of each option
- Benchmark comparisons

**Mental evaluation:**
- Scenario walkthroughs
- "What if this scales 10x?" testing
- Failure mode analysis per option

---

## Cultural Context

**Nemawashi in Japanese business:**
- Informal circulation of proposals before meetings
- Building consensus gradually
- Avoiding surprises in formal decisions
- Collective wisdom over individual judgment

**Nemawashi in solo design:**
- "Consensus with yourself"
- Evaluating options deliberately
- Documenting reasoning
- Future-self consensus (will you agree with this choice in 6 months?)

---

## Verification

**Before committing to a decision:**
- [ ] Generated 2-3 genuine alternatives
- [ ] Evaluated pros/cons explicitly
- [ ] Identified trade-offs clearly
- [ ] Chose consciously (not by default)
- [ ] Documented rationale
- [ ] Estimated reversibility cost

**Quality check:**
- Can you articulate why you DIDN'T choose the alternatives?
- If not, you haven't done Nemawashi yet.

---

## Practical Workflow

```markdown
## When facing a trap door decision:

1. Stop before implementing anything
2. Open decision document
3. List 2-3 alternatives (force divergent thinking)
4. Evaluate each with Nemawashi template
5. Choose one with explicit rationale
6. Document reversibility cost
7. NOW implement with confidence

Time cost: 15-30 minutes
Value: Optimal decision, no regrets, faster execution
```

---

## Source

From Ben Guo's velocity coding talk: "Nemawashi mode—exploring alternatives before committing. It's part of the thinking phase."

Referenced in Zo's planning prompt as core thinking mode.

---

**Created:** 2025-10-26  
**Version:** 1.0
