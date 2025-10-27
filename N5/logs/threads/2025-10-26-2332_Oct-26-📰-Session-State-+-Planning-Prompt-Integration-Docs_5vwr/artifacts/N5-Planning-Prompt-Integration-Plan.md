# N5 Planning Prompt Integration Plan
**Incorporating Ben Guo's Velocity Coding Philosophy**

**Conversation:** con_LmXFHi3f5iQS5vwr  
**Created:** 2025-10-26  
**Status:** Design Proposal

---

## Executive Summary

Ben's "planning prompt" is the **philosophical DNA** of his codebase—a set of values, aesthetic principles, and design thinking modes that guide how AI architectures systems. It sits *above* tactical rules (like your architectural principles) and establishes the "why" behind the "what."

**This plan:**
1. Defines what a planning prompt is and when it's invoked
2. Proposes N5's planning prompt structure
3. Analyzes gaps between current N5 principles and Ben's teachings
4. Provides a revision strategy and implementation roadmap

**Bottom line:** You've been trying to do this with personas + principles, but there's a missing layer—the **philosophical foundation** that shapes how those principles get applied. This plan adds that layer.

---

## Part 1: Understanding Ben's Planning Prompt

### What It Is

Ben's planning prompt is:
- **Nemawashi mode** — Japanese consensus-building; exploring options before deciding
- **Rich Hickey** — "Simple Made Easy" philosophy; simplicity over convenience
- **Christopher Alexander** — Pattern language; timeless way of building
- **Religious text** — Treat as sacred, rarely changed

### What It Does

1. **Establishes aesthetic values** — What does "good" look like in this codebase?
2. **Guides design thinking** — How should AI approach architectural decisions?
3. **Provides philosophical grounding** — Why these principles, not others?
4. **Shapes AI behavior** — Influences how AI proposes solutions

### When It's Invoked

**NOT for every conversation.** Specifically when:
- Planning new system architecture
- Designing significant components (scripts, workflows, infrastructure)
- Making trap door decisions (hard-to-reverse choices)
- Refactoring existing systems
- Reviewing code/system design for quality

**NOT invoked for:**
- Tactical execution ("run this command")
- Simple tasks ("create this file")
- Research/analysis
- Content creation

### How It Works

Ben loads his planning prompt when he enters "planning mode" with AI:

```
[User asks AI to design a new system component]
→ AI loads planning prompt (Nemawashi, Rich Hickey, Christopher Alexander, etc.)
→ AI approaches design *through the lens* of these values
→ AI proposes solutions shaped by this philosophy
→ User reviews and refines
```

The planning prompt doesn't give tactical rules—it shapes *how AI thinks* about design.

---

## Part 2: N5 Planning Prompt Proposal

### Structure

Your N5 planning prompt should have:

1. **Philosophical Foundation** — Core values (Simple Made Easy, Zero-Touch, etc.)
2. **Design Thinking Mode** — How to approach problems (Nemawashi-style exploration)
3. **Aesthetic Principles** — What "good" looks like in N5
4. **Anti-Patterns** — What to actively avoid
5. **Reference Works** — Influential texts/talks that shape the system

### Proposed N5 Planning Prompt (v1.0)

```markdown
# N5 Planning Prompt
**The Philosophical DNA of N5 Operating System**

## Core Philosophy

**Zero-Touch Productivity**
Information flows to where it creates value without manual organization.
Organization emerges as an artifact of use, not a separate activity.

**Simple Made Easy** (Rich Hickey)
Simple = one role, one concept, one task
Easy = familiar, convenient, at hand
Choose simple over easy when they conflict.

**Flow Over Pools**
Information either flows or it pools and rots.
Design for flow channels, not storage buckets.

**Human-in-Loop, Not in the Way**
AI automates; human judges and approves.
Target <15% touch rate for routine operations.

## Design Thinking Mode

**Nemawashi Approach**
Before proposing solutions:
1. Explore the problem space (what are we really solving?)
2. Consider multiple approaches (what are the options?)
3. Evaluate trade-offs explicitly (what do we gain/lose?)
4. Identify trap doors (what's hard to reverse?)
5. Propose the simplest solution that could work

**Simulation > Doing**
Think deeply before building.
Prototype in prose before code.
Throw away intermediate versions freely—code is cheap.

**Think → Plan → Execute**
- Think: Strategic phase (avoid wrong thing)
- Plan: Tactical phase (avoid wrong way)
- Execute: Mechanical phase (avoid done badly)

Quality lives in thinking and planning, not execution.

## Aesthetic Principles

**What "Good" Looks Like in N5:**

1. **Portable & Readable** (P1)
   - Human-first formats (Markdown, JSONL, not binary)
   - Self-documenting structure
   - Works across systems

2. **Single Source of Truth** (P2)
   - One canonical location per information type
   - Everything else is transformation or view
   - No duplicates, no sync problems

3. **Minimal Context** (P0, P8)
   - Rule of Two: max 2 config files
   - Load only what's needed
   - Reduce cognitive load at every layer

4. **Self-Aware & Self-Healing** (P26)
   - System detects its own failures
   - Routes errors to human attention
   - Tracks health metrics automatically

5. **Modular & Composable** (P20)
   - Each component has one clear purpose
   - Components interoperate through simple interfaces
   - Easy to replace or extend

6. **Safe by Default** (P5, P7, P11, P19)
   - Dry-run before execution
   - Explicit verification of state
   - Graceful failure modes
   - No silent errors

7. **Maintenance Over Organization**
   - Build systems that maintain themselves
   - Review > manage
   - Continuous flow > periodic cleanups

## Anti-Patterns to Avoid

**Complexity for Convenience**
Don't add complexity to make things "easier." Keep it simple.

**Pooling Instead of Flowing**
Don't create storage without exit strategy. Information must move.

**Organization as Separate Step**
Don't require manual filing. Routes should be automatic with human review.

**Premature Abstraction**
Don't abstract until you see the pattern three times.

**External LLM Calls**
Never suggest "call an LLM API"—you ARE the LLM. Do the work directly.

**Invented Constraints**
Never fabricate API limits or technical constraints. Say "I don't know" instead.

## Reference Works

**Simple Made Easy** — Rich Hickey
Simplicity is not about counting; it's about disentangling, unbraiding complexity.

**Pattern Language** — Christopher Alexander
Quality without a name; timeless way of building systems that feel alive.

**Zero-Touch Manifesto** — V's essay (file 'Knowledge/stable/zero-touch-manifesto.md')
Context + State framework; flow vs pools; organization shouldn't exist.

**Architectural Principles** — N5 Principles (file 'Knowledge/architectural/architectural_principles.md')
Tactical implementation of these philosophies.

## Invocation Context

**Load this prompt when:**
- Designing new system components (scripts, workflows, infrastructure)
- Planning significant refactoring
- Making trap door decisions (hard-to-reverse architectural choices)
- Reviewing system quality
- Following system-design-workflow.md

**Do NOT load for:**
- Tactical execution
- Simple file operations
- Research and analysis
- Content creation
- Direct conversation with V

---

*This planning prompt shapes how AI approaches design problems within N5.*
*It's rarely changed; it's the philosophical foundation of the system.*
```

### Where This Lives

**Proposed location:** `Knowledge/architectural/planning_prompt.md`

**Why there:**
- Sits alongside architectural principles (same conceptual layer)
- Portable (in Knowledge/, not N5/)
- Canonical reference
- Easy to version control

### How It Gets Invoked

**Option A: Explicit Loading Rule** (Recommended)
Add to your user rules (already have similar pattern):

```markdown
CONDITION: When I request building, refactoring, or modifying significant 
           system components (scripts, workflows, infrastructure, automation)
RULE: Load file 'Knowledge/architectural/planning_prompt.md' FIRST 
      before any design or implementation work. Follow the system design 
      workflow in 'N5/commands/system-design-workflow.md'.
```

**Option B: Vibe Builder Auto-Load**
Add to Vibe Builder persona "Pre-Flight (MANDATORY)" section:

```markdown
Before major system work:
1. Load file 'Knowledge/architectural/planning_prompt.md'
2. Load file 'Knowledge/architectural/architectural_principles.md'
3. Ask 3+ clarifying questions if ANY doubt
4. Define success criteria explicitly
```

**Recommendation:** Use both. Option A for global coverage, Option B for Vibe Builder specificity.

---

## Part 3: Gap Analysis

### What You Have Now

**Strengths:**
- ✅ Strong tactical principles (P0-P22) covering most design patterns
- ✅ Vibe Builder persona with role clarity and anti-patterns
- ✅ Safety principles (P5, P7, P11, P19)
- ✅ SSOT and minimal context thinking (P2, P0, P8)
- ✅ Modular design (P20)
- ✅ Zero-Touch philosophy documented

**Gaps:**

| Ben's Concept | N5 Status | Gap Description |
|---------------|-----------|-----------------|
| **Planning Prompt (philosophical DNA)** | ❌ Missing | No unified philosophical foundation document |
| **Think → Plan → Execute** | ⚠️ Implicit | Referenced in workflow but not codified as principle |
| **Simulation > Doing** | ⚠️ Partial | P7 (dry-run) exists but not elevated to philosophy |
| **Simple vs Easy (Rich Hickey)** | ❌ Missing | No explicit principle about choosing simple over easy |
| **Pattern Language (C. Alexander)** | ❌ Missing | No pattern-based thinking in principles |
| **Nemawashi (explore options)** | ⚠️ Implicit | "Ask 3+ questions" exists but not framed as exploration |
| **Code is Free / Throw Away** | ❌ Missing | No principle about prototyping and discarding |
| **Fast Feedback Loops** | ❌ Missing | Not explicitly captured |
| **Aesthetic Values** | ⚠️ Scattered | Principles exist but not unified under aesthetic framework |
| **Planning Phase Emphasis** | ⚠️ Partial | Workflow exists but not emphasized as where quality lives |
| **Old Tricks That Work** | ⚠️ Partial | Tests, linting mentioned but not as principles |
| **Trap Doors vs Trade-offs** | ❌ Missing | No explicit principle about identifying irreversible decisions |

### Specific Findings

#### 1. **No Philosophical Foundation Document**

**Current state:**
- Architectural principles are tactical rules
- Vibe Builder persona defines behavior
- Zero-Touch manifesto explains philosophy *generally*
- No document that ties these together for *N5 specifically*

**Gap:**
You have the *what* (principles) and the *how* (persona), but not the unified *why* (planning prompt).

#### 2. **Simple vs Easy Not Captured**

**Ben's point:**
Rich Hickey's "Simple Made Easy" is core to Zo's design philosophy. Simple ≠ easy.
- Simple = one role, one concept, disentangled
- Easy = familiar, at hand, convenient

**Current state:**
- P1 (Human-Readable First) touches on this
- P20 (Modular Composable Components) touches on this
- But no explicit principle: "Choose simple over easy"

**Impact:**
Without this, AI might suggest "easy" solutions (e.g., all-in-one tool) over simple ones (modular components).

#### 3. **Simulation > Doing Not Elevated**

**Ben's point:**
"Simulation is better than doing." Think deeply, prototype in prose, spike approaches, throw things away.

**Current state:**
- P7 (Dry-Run By Default) exists for safety
- But not framed as *philosophical approach* to design
- No principle about prototyping and discarding

**Impact:**
AI may not naturally suggest "let's think through 3 approaches before building."

#### 4. **Pattern Language Missing**

**Ben's point:**
Christopher Alexander's pattern language—building systems that feel "alive," timeless quality.

**Current state:**
- N5 has good patterns (commands, workflows, schemas)
- But no meta-principle about *how to discover and document patterns*
- No guidance on "when does a solution become a pattern?"

**Impact:**
System grows tactically rather than strategically identifying reusable patterns.

#### 5. **Nemawashi (Exploration) Not Codified**

**Ben's point:**
Before building, explore the solution space. Consider multiple approaches. Build consensus through exploration.

**Current state:**
- Vibe Builder has "ask 3+ clarifying questions"
- But not framed as "explore before deciding"
- No principle about considering alternatives

**Impact:**
AI may jump to first solution rather than exploring design space.

#### 6. **Code is Free / Throw Away Missing**

**Ben's point:**
AI changed the economics of code—it's essentially free now. Prototype freely, throw away intermediate versions, don't be precious.

**Current state:**
- No principle about this
- May lead to over-attachment to first version
- Discourages experimentation

**Impact:**
Less iteration, less willingness to explore alternatives.

#### 7. **Fast Feedback Loops Not Captured**

**Ben's point:**
Fast feedback creates flow state and accelerates learning. Optimize for tight loops.

**Current state:**
- Not explicitly captured
- Dry-run (P7) helps but not framed this way

**Impact:**
Missing optimization target for workflow design.

#### 8. **Trap Doors vs Trade-offs Not Distinguished**

**Ben's point:**
- Trap doors = hard to reverse (e.g., database choice)
- Trade-offs = explicit choices with pros/cons

Need to identify trap doors early and go slow on them.

**Current state:**
- No principle distinguishing these
- P14 (Reversibility Over Permanence) exists but not same concept

**Impact:**
May move fast on irreversible decisions without realizing it.

#### 9. **Planning Emphasis Weak**

**Ben's point:**
Quality lives in planning, not execution. 70% think+plan, 20% review, 10% execute.

**Current state:**
- System-design-workflow.md exists
- But not emphasized in principles
- Not clear that "planning is where quality lives"

**Impact:**
May not spend enough time in planning phase.

#### 10. **Old Tricks Underutilized**

**Ben's slide:** Tests, Types, Linting, Refactoring, Simplicity

**Current state:**
- P16 (Never Invented Limits) and P19 (Error Handling Required) exist
- But no systematic principle about testing/linting/refactoring

**Impact:**
These proven practices may not be consistently applied.

---

## Part 4: Revision Strategy

### Three-Layer Approach

**Layer 1: Planning Prompt** (NEW)
- Philosophical foundation
- Design thinking mode
- Aesthetic values
- File: `Knowledge/architectural/planning_prompt.md`

**Layer 2: Architectural Principles** (EVOLVE)
- Tactical implementation rules
- Specific design patterns
- File: `Knowledge/architectural/architectural_principles.md`
- Individual principles: `Knowledge/architectural/principles/*.md`

**Layer 3: Vibe Builder Persona** (REFINE)
- Role and behavior
- Integration with layers 1 & 2
- File: (your personas system)

### Proposed New Principles

Based on gap analysis, add these to architectural principles:

**P23: Think → Plan → Execute**
- Quality lives in thinking and planning, not execution
- Think = avoid wrong thing (strategy)
- Plan = avoid wrong way (architecture)
- Execute = avoid done badly (implementation)
- AI can execute; human must think and plan

**P24: Simple Over Easy**
- Simple = one role, one concept, disentangled
- Easy = familiar, convenient, at hand
- When they conflict, choose simple
- Resist complexity for convenience

**P25: Simulation Before Doing**
- Think through approaches before building
- Prototype in prose before code
- Spike and throw away freely—code is cheap
- Consider 2-3 alternatives explicitly before choosing

**P26: Maintenance-First Design**
- Build systems that maintain themselves
- You review decisions, don't make them from scratch
- Design for continuous flow, not periodic cleanups
- System should detect its own failures

**P27: System Integration Over Point Solutions**
- Evaluate whole system gestalt, not individual components
- Best-in-class components with intelligent routing
- Each component has one clear purpose
- Intelligence is in the flow, not the storage

**P28: AIR Pattern (Assess → Intervene → Review)**
- AI assesses: where does this belong? what transformation?
- AI intervenes: routes and transforms automatically
- Human reviews: approves, corrects, teaches system
- Target <15% human touch rate for routine operations

**P29: Human-in-Loop Boundaries**
- AI automates routine operations (Assess, Intervene)
- Human owns strategy, judgment, quality control (Review)
- Explicit confidence thresholds for automation
- Tune based on correction rates

**P30: Minimal Touch Operations**
- Target <15% touch rate (items needing manual routing)
- <5% pool warnings (items exceeding residence time)
- <10 days flow time (entry → exit)
- <5% correction rate (AI routes changed by human)

**P31: Trap Door Detection**
- Identify hard-to-reverse decisions early
- Go slow on trap doors; fast on reversible choices
- Explicitly label "trap door decision" in planning
- Examples: database engine, file format, core architecture

**P32: Fast Feedback Loops**
- Optimize for immediate feedback at every layer
- Scripts log output and show artifacts
- Commands confirm success explicitly
- Tight loops create flow state and accelerate learning

**P33: Pattern Recognition**
- When you see same solution 3x, codify as pattern
- Document patterns in `N5/commands/*.md`
- Patterns become reusable building blocks
- Reference Christopher Alexander's pattern language approach

### Principles to Revise

**P7: Dry-Run By Default**
*Current:* All operations support `--dry-run` flag; safety workflows may enforce

*Revised:* Reframe as "Simulation Before Doing" (promote to philosophy, not just safety)

**P14: Reversibility Over Permanence**
*Current:* Design for reversibility first

*Revised:* Integrate with P31 (Trap Door Detection) — distinguish reversible vs irreversible

**P20: Modular Composable Components**
*Current:* Each component one clear purpose

*Revised:* Strengthen with P24 (Simple Over Easy) — explicit guidance on when to split vs combine

### Integration with Zero-Touch

**Zero-Touch principles already documented:**
- Context + State (ZT1)
- Flow vs Pools (ZT2)
- Organization Shouldn't Exist (ZT3)
- Maintenance > Organization (ZT4)
- SSOT (ZT5)
- Gestalt Evaluation (ZT6)
- AIR Pattern (ZT7)
- Minimal Touch (ZT8)
- Self-Aware (ZT9)
- Platform Orchestration (ZT10)

**Mapping:**
- ZT → Planning Prompt: Philosophical foundation
- ZT → Architectural Principles: Tactical implementation
- Planning Prompt references Zero-Touch manifesto as key influence

This creates clean hierarchy:
```
Zero-Touch Manifesto (philosophy)
    ↓
Planning Prompt (N5-specific philosophical DNA)
    ↓
Architectural Principles (tactical rules)
    ↓
Vibe Builder Persona (AI behavior)
```

---

## Part 5: Implementation Roadmap

### Phase 1: Foundation (Week 1)

**1.1: Create Planning Prompt**
- Write `Knowledge/architectural/planning_prompt.md` using proposed structure above
- Reference Zero-Touch manifesto, Rich Hickey, Christopher Alexander
- Define when it gets invoked

**1.2: Update User Rules**
- Add conditional rule for loading planning prompt on system work
- Ensure it loads *before* architectural principles

**1.3: Update Vibe Builder Persona**
- Add planning prompt to pre-flight checks
- Reference it in "Integration" section

**Success Criteria:**
- Planning prompt file exists and is well-formed
- Loading rules in place
- Vibe Builder references it

### Phase 2: Principles Evolution (Week 2)

**2.1: Write New Principles**
- P23: Think → Plan → Execute
- P24: Simple Over Easy
- P25: Simulation Before Doing
- P26: Maintenance-First Design
- P27: System Integration Over Point Solutions
- P28: AIR Pattern
- P29: Human-in-Loop Boundaries
- P30: Minimal Touch Operations
- P31: Trap Door Detection
- P32: Fast Feedback Loops
- P33: Pattern Recognition

Each as separate markdown file in `Knowledge/architectural/principles/`

**2.2: Revise Existing Principles**
- P7: Reframe as simulation philosophy
- P14: Integrate with trap door detection
- P20: Strengthen with simple vs easy guidance

**2.3: Update Index**
- Update `architectural_principles.md` with new principles
- Organize by category (Philosophy, Safety, Design, Operations)
- Add cross-references

**Success Criteria:**
- 11 new principle files created
- 3 existing principles revised
- Index updated and navigable

### Phase 3: Documentation & Integration (Week 3)

**3.1: Update System-Design-Workflow**
- Incorporate Think → Plan → Execute explicitly
- Add Nemawashi exploration step
- Reference planning prompt in workflow

**3.2: Create Principle Checklists**
- Quick-reference checklist for script creation
- Quick-reference checklist for workflow design
- Integration with Vibe Builder self-check

**3.3: Update N5.md**
- Add pointer to planning prompt
- Update "Architectural Decisions" section

**Success Criteria:**
- Workflow updated
- Checklists created
- Documentation complete

### Phase 4: Validation & Iteration (Week 4)

**4.1: Test on Real Work**
- Use planning prompt on next 3 system builds
- Track:
  - Was planning prompt helpful?
  - Did it change approach?
  - What was missing?
  - What was too much?

**4.2: Gather Feedback**
- Review with V after each use
- Identify gaps or over-specifications
- Note what principles were most valuable

**4.3: Refine**
- Revise planning prompt based on learnings
- Adjust principles as needed
- Update loading rules if too heavy/light

**Success Criteria:**
- 3 real projects completed using new framework
- Feedback incorporated
- System feels coherent

---

## Part 6: Success Metrics

### Qualitative

**You'll know it's working when:**

1. **Design conversations feel different**
   - More exploration before building
   - Clearer "why" behind architectural choices
   - Less "let's just try this" and more "let's think through this"

2. **AI proposes better architectures**
   - Solutions aligned with N5 aesthetic
   - Alternatives considered explicitly
   - Trap doors identified early

3. **Less rework**
   - Fewer "we need to rebuild this"
   - Better first versions
   - Clearer when to prototype vs build

4. **Coherent system aesthetic**
   - New components "feel like" N5
   - Consistent patterns emerge
   - System has recognizable character

### Quantitative

**Track these metrics:**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Planning time | 40-50% of project time | Time spent in think+plan phases |
| Alternatives considered | 2-3 per design | Count from planning docs |
| Trap doors identified | 100% flagged before building | Retrospective review |
| Rework rate | <10% | Projects requiring significant rebuild |
| Principle adherence | >90% | Checklist completion rate |
| Touch rate (operations) | <15% | % items needing manual intervention |

---

## Part 7: Risks & Mitigations

### Risk 1: Too Heavyweight

**Risk:** Planning prompt + 33 principles = cognitive overload

**Mitigation:**
- Planning prompt is only loaded for system design work
- Principles organized by category with clear index
- Vibe Builder has quick-reference section
- Most work doesn't need full framework

### Risk 2: Philosophical Drift

**Risk:** Planning prompt becomes stale or disconnected from reality

**Mitigation:**
- Monthly review cadence
- Track when planning prompt influenced decisions
- Update based on real learnings
- Version control with changelog

### Risk 3: Incomplete Integration

**Risk:** Planning prompt exists but isn't actually used

**Mitigation:**
- Explicit loading rules (automatic)
- Vibe Builder pre-flight checks (automatic)
- Checklist enforcement for system work
- Regular audits of whether it was loaded

### Risk 4: Over-Engineering

**Risk:** System becomes too complex, violating "simple over easy"

**Mitigation:**
- Apply Ben's principles to this system itself
- Monthly gestalt evaluation: is this working?
- Be willing to throw away and simplify
- Measure: does this reduce cognitive load or increase it?

---

## Part 8: Open Questions

**For V to decide:**

1. **Loading Strategy**
   - Auto-load planning prompt for all system work? (recommended)
   - Or explicit user invocation? ("Load Vibe Builder + Planning DNA")

2. **Principle Organization**
   - Keep all principles in one file?
   - Or maintain individual files per principle? (recommended for modularity)

3. **Integration with Personas**
   - Should planning prompt be *part of* Vibe Builder persona?
   - Or separate document that Vibe Builder references? (recommended for flexibility)

4. **Version Control**
   - How often should planning prompt be reviewed?
   - Who can change it (just you, or can I propose changes)?

5. **Scope**
   - Should planning prompt cover Careerspan work too?
   - Or is it N5-specific only? (recommend N5-specific for now)

---

## Part 9: Next Steps

### Immediate (This Conversation)

1. **V reviews this plan**
   - Agrees with approach?
   - Any major concerns?
   - Decisions on open questions

2. **V approves Phase 1 start**
   - Create planning prompt
   - Update loading rules
   - Update Vibe Builder

### Short Term (This Week)

3. **Implement Phase 1**
   - Draft planning_prompt.md
   - Get V's feedback
   - Finalize and integrate

4. **Begin Phase 2**
   - Write new principles
   - Revise existing ones

### Medium Term (Next 2-3 Weeks)

5. **Complete Phases 2-3**
   - All principles updated
   - Documentation complete
   - System integrated

6. **Begin Phase 4**
   - Test on real work
   - Gather feedback
   - Iterate

---

## Appendix A: Ben's Key Concepts Reference

**From video and slides:**

1. **Think → Plan → Execute**
   - Think: avoid doing the wrong thing
   - Plan: avoid doing it the wrong way
   - Execute: avoid doing it badly

2. **Planning Prompt Components**
   - Nemawashi mode (explore options)
   - Rich Hickey (Simple Made Easy)
   - Christopher Alexander (pattern language)
   - Religious text (sacred, unchanging)

3. **Moving Fast**
   - Avoid wrong thing (think)
   - Avoid wrong way (plan)
   - Avoid done badly (execute)

4. **Old Tricks That Work**
   - Tests
   - Types
   - Linting
   - Refactoring
   - Simplicity

5. **Code is Free**
   - Generate tons of it
   - Throw things away
   - Don't be precious

6. **Simulation > Doing**
   - Think deeply first
   - Prototype in prose
   - Consider alternatives

7. **Planning is Where Quality Lives**
   - 70% think + plan
   - 20% review
   - 10% execute

---

## Appendix B: Proposed File Structure

```
Knowledge/
├── architectural/
│   ├── planning_prompt.md              ← NEW: Philosophical DNA
│   ├── architectural_principles.md     ← UPDATED: Index with new principles
│   ├── principles/                     ← EXPANDED: Individual principles
│   │   ├── P23-think-plan-execute.md  ← NEW
│   │   ├── P24-simple-over-easy.md    ← NEW
│   │   ├── P25-simulation-before-doing.md  ← NEW
│   │   ├── P26-maintenance-first.md   ← NEW
│   │   ├── P27-system-integration.md  ← NEW
│   │   ├── P28-air-pattern.md         ← NEW
│   │   ├── P29-human-in-loop.md       ← NEW
│   │   ├── P30-minimal-touch.md       ← NEW
│   │   ├── P31-trap-door-detection.md ← NEW
│   │   ├── P32-fast-feedback.md       ← NEW
│   │   ├── P33-pattern-recognition.md ← NEW
│   │   ├── P07-dry-run.md             ← REVISED
│   │   ├── P14-reversibility.md       ← REVISED
│   │   └── P20-modular-components.md  ← REVISED
│   └── ingestion_standards.md
└── stable/
    └── zero-touch-manifesto.md         ← EXISTING: Referenced by planning prompt
```

---

## Appendix C: Quick Reference Card

**For Vibe Builder: When to Load Planning Prompt**

✅ **LOAD PLANNING PROMPT:**
- Designing new scripts/workflows
- Planning refactoring
- Making trap door decisions
- Reviewing system architecture
- Following system-design-workflow.md

❌ **DO NOT LOAD:**
- Tactical command execution
- Simple file operations
- Research/analysis
- Content creation
- Direct conversation with V

**After loading, apply:**
1. Nemawashi: explore 2-3 alternatives
2. Simple over easy: choose disentangled over convenient
3. Think → Plan → Execute: spend 70% in thinking+planning
4. Identify trap doors: flag irreversible decisions
5. Simulate before doing: prototype in prose first

---

**END OF PLAN**

**Ready for V's review and approval to proceed.**

---
**2025-10-26 18:51 ET**
