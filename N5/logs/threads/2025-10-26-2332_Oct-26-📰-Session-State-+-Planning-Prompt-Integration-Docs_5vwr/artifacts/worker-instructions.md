# Worker Instructions: New Architectural Principles
**Parallel Deployment Plan**

**Orchestrator:** con_LmXFHi3f5iQS5vwr  
**Created:** 2025-10-26  
**Strategy:** Deploy 11 workers in parallel to create new principles

---

## Context for All Workers

You are creating **new architectural principles** for the N5 system based on Ben Guo's velocity coding philosophy. These principles complement existing P0-P22.

**Requirements:**
- **Format:** Individual .md files per principle
- **Location:** `Knowledge/architectural/principles/`
- **Naming:** `P[NUMBER]-[slug].md` (e.g., `P23-trap-doors.md`)
- **Length:** Concise (1-2 pages max)
- **Style:** Direct, principle-driven, actionable
- **Structure:** Title | Summary | Why It Matters | How To Apply | Anti-Patterns | Examples

**Sacred Text Protocol:**
- These files are V-only modification
- Clear, authoritative language
- No speculation—only established patterns
- Must reference Ben's talk concepts where applicable

---

## Worker 1: P23 - Trap Doors

**Principle:** Identify and document irreversible decisions before making them.

**Create:** `Knowledge/architectural/principles/P23-trap-doors.md`

**Content Guidance:**
- Definition: Trap doors = irreversible architectural decisions
- Examples: Database choice, file format, public API contracts
- vs. Trade-offs (reversible choices with pros/cons)
- How to identify trap doors early
- Documentation protocol when encountering one
- Ben's concept: Think phase must surface these

**Key Quote from Ben:** "Some decisions are trap doors—you fall through and can't come back."

---

## Worker 2: P24 - Simulation Over Doing

**Principle:** Model and prototype in prose before generating code.

**Create:** `Knowledge/architectural/principles/P24-simulation-over-doing.md`

**Content Guidance:**
- Simulation = mental modeling, spiking, prototyping
- Why simulation is faster than doing (in AI era)
- Prose plans as simulation
- Spike-and-discard as simulation
- Code is free, thinking is expensive
- Connection to Ben's "leverage" concept

**Key Quote from Ben:** "Simulation is better than doing."

---

## Worker 3: P25 - Fast Feedback Loops

**Principle:** Design for immediate feedback to maintain flow state.

**Create:** `Knowledge/architectural/principles/P25-fast-feedback-loops.md`

**Content Guidance:**
- Flow state requires <1s feedback
- How to structure work for fast feedback
- Hot reload, watch modes, incremental testing
- Breaking work into testable chunks
- Ben's hierarchy of slowdowns
- Psychological importance of immediacy

**Key Quote from Ben:** "The delay between thought and result determines your flow state."

---

## Worker 4: P26 - Pattern Language

**Principle:** Build reusable, composable patterns (Christopher Alexander).

**Create:** `Knowledge/architectural/principles/P26-pattern-language.md`

**Content Guidance:**
- Christopher Alexander's pattern language concept
- Patterns in N5 context (commands, workflows, scripts)
- How to identify reusable patterns
- Documentation as pattern capture
- Composition over repetition
- Ben's reference to "patterns that combine"

**Key Quote from Ben:** "Build a pattern language that composes."

---

## Worker 5: P27 - Nemawashi (Consensus Building)

**Principle:** Explore 2-3 alternatives before committing to approach.

**Create:** `Knowledge/architectural/principles/P27-nemawashi.md`

**Content Guidance:**
- Nemawashi = Japanese consensus-building process
- In N5: exploring alternatives before deciding
- Minimum 2-3 approaches considered
- Document why chosen, why alternatives rejected
- Prevents premature optimization
- Part of Think phase

**Key Quote from Ben:** "Nemawashi mode—explore alternatives before committing."

---

## Worker 6: P28 - Plans As Code DNA

**Principle:** Plans generate code; quality lives in plans, not code.

**Create:** `Knowledge/architectural/principles/P28-plans-as-code-dna.md`

**Content Guidance:**
- All code inherits from plans
- Plan quality determines code quality
- Review plans, not just code
- Plans as specification for generation
- Sacred text approach to planning prompt
- Ben's insight: "Code is generated from your plans"

**Key Quote from Ben:** "If you care about quality, care about it at the plan level."

---

## Worker 7: P29 - Focus Plus Parallel

**Principle:** One primary focus + one background task maximum.

**Create:** `Knowledge/architectural/principles/P29-focus-plus-parallel.md`

**Content Guidance:**
- Strategic parallelism: 1 main + 1 auxiliary
- Not 5 things in parallel (chaos)
- How to structure work for focused parallelism
- Background tasks must be non-blocking
- Context-switching costs
- Ben's "one weird trick"

**Key Quote from Ben:** "Do one thing with focus, plus one thing in parallel."

---

## Worker 8: P30 - Maintain Feel For Code

**Principle:** Stay connected to code quality even when AI generates it.

**Create:** `Knowledge/architectural/principles/P30-maintain-feel-for-code.md`

**Content Guidance:**
- What "feel" means (quality intuition)
- How to lose feel (generating without reading)
- How to maintain feel (reading, reviewing, understanding)
- You should feel tired if you're learning
- Craft vs. speed tension
- Ben's warning about disconnect

**Key Quote from Ben:** "You can lose your feel for the code if you're not careful."

---

## Worker 9: P31 - Own The Planning Process

**Principle:** Never outsource strategic thinking to AI.

**Create:** `Knowledge/architectural/principles/P31-own-the-planning-process.md`

**Content Guidance:**
- You own Think + Plan phases
- AI owns Execute phase
- Why AI can't plan for you (lacks context/values)
- Strategy is human, tactics are machine
- Mental exhaustion as signal you're doing it right
- 70% of time in thinking+planning

**Key Quote from Ben:** "You have to own the planning. AI can't do that for you."

---

## Worker 10: P32 - Simple Over Easy (Rich Hickey)

**Principle:** Choose disentangled over convenient (existing P13 enhancement).

**Create:** `Knowledge/architectural/principles/P32-simple-over-easy.md`

**Content Guidance:**
- Rich Hickey's "Simple Made Easy" talk
- Simple = disentangled, few concepts
- Easy = familiar, convenient, intertwined
- Simple is better long-term (even if harder short-term)
- How to identify simplicity vs. easiness
- Connection to N5's modularity principles
- Ben's #1 design value

**Key Quote from Ben:** "Rich Hickey—Simple Made Easy. Read it if you haven't."

---

## Worker 11: P33 - Old Tricks Still Work

**Principle:** Tests, types, linting, refactoring, simplicity never go out of style.

**Create:** `Knowledge/architectural/principles/P33-old-tricks-still-work.md`

**Content Guidance:**
- Traditional software engineering practices remain valuable
- Tests verify behavior
- Types prevent errors
- Linting enforces consistency
- Refactoring reduces complexity
- Simplicity compounds
- AI doesn't obsolete fundamentals
- Ben's slide: "Tests, Types, Linting, Refactoring, Simplicity"

**Key Quote from Ben:** "The old tricks still work. Don't forget them."

---

## Orchestrator's Role (This Thread)

**I will:**
1. Deploy these 11 workers in parallel
2. Monitor completion
3. Integrate results into principles index
4. Update system-design-workflow.md to reference planning prompt
5. Final verification and report

**Timeline:** ~60-90 minutes for parallel completion

---

**Ready to deploy workers on V's signal.**
