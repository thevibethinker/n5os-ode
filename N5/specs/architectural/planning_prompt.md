# N5 Planning Prompt
**Philosophical DNA for System Design**

**Version:** 1.0  
**Created:** 2025-10-26  
**Authority:** V only (sacred text)  
**Auto-Load:** When building/refactoring N5 systems

---

## Purpose

This is the philosophical foundation for N5 system design. It sits **above** tactical principles and establishes the *why* behind the *what*. Load this before planning any significant system work—scripts, workflows, infrastructure, or architecture changes.

---

## Core Philosophy: Zero-Touch

**Information either flows or it pools. When it pools, it rots.**

N5 is a **flow-based cognitive infrastructure** where:
- Organization happens as artifact of use, not separate activity
- AI automates, human reviews exceptions
- Systems maintain themselves, with V as quality control
- Context and state are always queryable
- Best-in-class components with intelligent routing

**Target:** <15% touch rate (V only touches exceptions, not routine operations)

---

## Design Values (In Priority Order)

### 1. Simple Over Easy
**From:** Rich Hickey's "Simple Made Easy"

Choose **disentangled** (simple) over **convenient** (easy).

- Simple = few interwoven concepts, low coupling
- Easy = familiar, quick to start, but complex underneath
- Simple systems adapt well to change and AI generation
- Easy systems accumulate hidden complexity

**Trade-off:** Initial setup time for long-term adaptability.

**Ask:** "Is this simple (few parts) or just easy (feels familiar)?"

### 2. Flow Over Pools
**From:** Zero-Touch Manifesto

Information must move through stages with time limits. Pools = failure state.

- Track residence time for all information
- Auto-alert when items exceed thresholds
- Every entry point has defined exit conditions
- Default: 24hr triage → 7 days processing → permanent archive or deletion

**Trade-off:** Discipline to delete vs. comfort of "maybe I'll need this."

**Ask:** "Where does this flow *to*, and what happens when it gets there?"

### 3. Maintenance Over Organization
**From:** Zero-Touch Manifesto

You can't organize your way to productivity. Build self-maintaining systems.

- Review > manage
- Detect failures automatically
- Route exceptions to human attention
- Evaluate end-to-end flows, not individual components

**Trade-off:** Upfront design work for reduced ongoing cognitive load.

**Ask:** "How will this system tell me when it's broken?"

### 4. Code Is Free, Thinking Is Expensive
**From:** Ben Guo

AI can generate unlimited code. Your strategic thinking is the constraint.

- Spend 70% time in Think+Plan, 20% Review, 10% Execute
- Prototype in prose before coding
- Throw away intermediate versions freely
- All code quality comes from planning quality

**Trade-off:** Patience in planning phase for velocity in execution.

**Ask:** "Have I thought through trap doors and failure modes?"

### 5. Nemawashi: Explore Before Deciding
**From:** Ben Guo (via Japanese consensus-building)

For significant decisions, explore 2-3 alternatives explicitly.

- What are the adjacent possibilities?
- What are the trade-offs?
- What are the trap doors (irreversible decisions)?
- What could we try that we're not considering?

**Trade-off:** Time exploring vs. bias toward first idea.

**Ask:** "What's the second-best way to do this?"

---

## Design Thinking Mode: Think → Plan → Execute

**THINK Phase (70% of time)**
- What am I building and why?
- What are the alternatives? (Nemawashi)
- What are the trap doors? (Irreversible decisions)
- What are the trade-offs?
- What are the failure modes?
- Is this simple (disentangled) or just easy (familiar)?

**PLAN Phase (included in 70%)**
- Write prose specification (the "planning prompt" for this feature)
- Define success criteria explicitly
- Identify verification steps
- Map information flows (entry → transform → destination → exit)
- Specify confidence thresholds for automation
- Document assumptions explicitly

**EXECUTE Phase (10% of time)**
- Generate code from plan
- Move fast, don't break things
- Goal is velocity, not perfection
- Execution is mechanical; quality came from planning

**REVIEW Phase (20% of time)**
- Verify all success criteria met
- Test in production conditions (not just dev)
- Check error paths work
- Validate state after writes
- Fresh thread test (can someone else understand this?)

---

## Trap Doors vs. Trade-offs

**Trap Door** = Irreversible or very-high-cost-to-reverse decision

Examples:
- Choosing database technology (hard to migrate)
- File format that can't be converted
- API that requires rewriting all consumers
- Architectural pattern that touches everything

**When you hit a trap door:** SLOW DOWN. Nemawashi. Explore alternatives. Get V's input if needed.

**Trade-off** = Reversible choice with pros/cons

Examples:
- Script language selection (can rewrite)
- File organization structure (can reorganize)
- Logging verbosity (can adjust)
- Variable naming (can refactor)

**When you hit a trade-off:** Document decision + rationale, move forward, iterate.

---

## Pattern Language (Christopher Alexander)

When you see something 3 times, it's a pattern. Codify it.

**Pattern detection:**
- Similar code across 3+ scripts → Extract to library
- Similar workflow across 3+ processes → Templatize
- Similar error across 3+ modules → Systematic fix

**Pattern application:**
- Use existing patterns before inventing new ones
- Name patterns clearly (human-readable identifiers)
- Document when/why pattern applies
- Link patterns that compose together

**Anti-pattern:** Don't pattern-ize after seeing it twice. Three instances confirm.

---

## Fast Feedback Loops

**Optimize for immediacy:** Faster feedback = more flow state = better work.

Design for:
- Run locally before deploying
- Test individual components in isolation
- Dry-run mode for all destructive operations
- Immediate verification after writes
- Real-time logs (not batch processing)

**Anti-pattern:** "It'll take hours to test, so let's ship and see."

---

## When This Applies

**LOAD PLANNING PROMPT FOR:**
- Building new N5 scripts/workflows
- Refactoring existing systems
- Architectural decisions
- Infrastructure changes
- Workflow design
- System integrations
- Following `N5/commands/system-design-workflow.md`

**DON'T LOAD FOR:**
- Tactical command execution
- Simple file operations
- Research/content creation
- Direct conversations with V

---

## How To Use This

1. **Load** at start of system design work
2. **Think** using the five design values (simple over easy, flow over pools, etc.)
3. **Plan** using Think→Plan→Execute framework
4. **Identify** trap doors early (get V's input if needed)
5. **Execute** fast once planning is solid
6. **Review** thoroughly (production conditions, error paths, fresh thread test)

---

## Integration With Architectural Principles

**Planning Prompt = WHY** (philosophy, values, thinking modes)  
**Architectural Principles = WHAT** (specific rules, patterns, practices)

Load planning prompt → Apply design values → Reference specific principles as needed.

**Don't load all principles.** Use selective loading: index first, then load specific principles relevant to current work.

---

## Sacred Text Protocol

**This document can only be modified by V.**

If you (AI) discover:
- Missing values
- Wrong priority
- Better framing
- New insights from Ben or other sources

→ Propose changes to V explicitly. Document reasoning. Get approval. Then update.

**Never silently change this document.**

---

## Meta: Why This Exists

Ben's insight: **All code is generated from your planning prompt and your plans.**

If you care about quality, care about it at the prompt level, not the code level.

This planning prompt is the DNA. Everything in N5 inherits from it. Get this right, everything downstream gets easier.

---

**END OF PLANNING PROMPT**

*v1.0 | 2025-10-26*
