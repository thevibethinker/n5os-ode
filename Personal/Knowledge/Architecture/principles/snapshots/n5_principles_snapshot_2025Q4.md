---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
grade: knowledge
domain: systems
stability: time_bound
form: aggregator
---

# N5 Architectural Principles

**Version**: 2.0 (Zero-Touch Integration)\
**Last Updated**: 2025-10-24\
**Status**: Living document

---

## Purpose

This document serves as the architectural foundation for N5OS—the operating system for AI-enabled knowledge work. These principles guide all system design decisions, workflow implementations, and tooling choices.

**NEW (v2.0)**: Added philosophical foundation layer (Zero-Touch) and derived 8 new architectural principles.

---

## Principle Hierarchy

### Philosophy Layer (Zero-Touch)

Strategic principles that define *why* we build systems this way:

- **ZT1**: Context + State Framework
- **ZT2**: Flow vs. Pools
- **ZT3**: Organization Step Shouldn't Exist
- **ZT4**: Maintenance &gt; Organization
- **ZT5**: SSOT Always (Single Source of Truth)
- **ZT6**: Gestalt Evaluation
- **ZT7**: AIR Pattern (Assess-Intervene-Review)
- **ZT8**: Minimal Touch
- **ZT9**: Self-Aware Systems
- **ZT10**: Platform Orchestration

**See**: `file Knowledge/architectural/principles/philosophy.md`

---

## Principles Index

### Design Principles (1-10)

### Core Principles → `file Knowledge/architectural/principles/core.md`

**Load for:** All operations, foundational rules

- **Principle 2:** Single Source of Truth (SSOT)

**Key concept:** Eliminate duplication

---

### Safety Principles (11-15)

### Safety Principles → `file Knowledge/architectural/principles/safety.md`

**Load for:** File operations, automation, destructive actions

- **Principle 5:** Safety, Determinism, and Anti-Overwrite
- **Principle 7:** Idempotence and Dry-Run by Default
- **Principle 11:** Failure Modes and Recovery
- **Principle 19:** Error Handling is Not Optional

**Key concept:** Prevent data loss, enable recovery, handle errors gracefully

---

### Quality Principles → `file Knowledge/architectural/principles/quality.md`

**Load for:** Implementations, documentation, verification

- **Principle 1:** Human-Readable First
- **Principle 15:** Complete Before Claiming Complete
- **Principle 16:** Accuracy Over Sophistication
- **Principle 18:** State Verification is Mandatory
- **Principle 21:** Document All Assumptions, Placeholders, and Stubs

**Key concept:** Accurate, complete, verifiable outputs

---

### Design Principles → `file Knowledge/architectural/principles/design.md`

**Load for:** System architecture, information design, voice application

- **Principle 3:** Voice Integration Policy
- **Principle 4:** Ontology-Weighted Analysis
- **Principle 8:** Minimal Context, Maximal Clarity
- **Principle 20:** Modular Design for Context Efficiency
- **Principle 22:** Language Selection for Purpose (Shell, Python, Node.js, Go trade-offs)

**Key concept:** Efficient design, appropriate tooling

---

### Operations Principles → `file Knowledge/architectural/principles/operations.md`

**Load for:** Day-to-day ops, testing, maintenance

- **Principle 6:** Mirror Sync Hygiene
- **Principle 9:** Copyable Blocks Philosophy
- **Principle 10:** Calendar & Time Semantics
- **Principle 12:** Testing in Fresh Threads
- **Principle 13:** Naming and Placement
- **Principle 14:** Change Tracking
- **Principle 17:** Test with Production Configuration

**Key concept:** Operational excellence, consistent processes

---

### Velocity Coding Principles (P23-P33) **NEW**

**From Ben Guo's Velocity Coding philosophy—think, plan, execute framework**

**P23: Identify Trap Doors** (Design, Critical)

- Explicitly identify and document irreversible decisions before making them
- `file Knowledge/architectural/principles/P23-identify-trap-doors.md`
- *Core to Think phase: flag hard-to-reverse decisions, explore alternatives*

**P24: Simulation Over Doing** (Strategy, High)

- Model, prototype, and test ideas before building production systems
- `file Knowledge/architectural/principles/P24-simulation-over-doing.md`
- *Simulation is faster than doing; write specs, prototype, then implement*

**P25: Code Is Free** (Strategy, Medium)

- Generate, test, and discard code freely; architecture cost is what matters
- `file Knowledge/architectural/principles/P25-code-is-free.md`
- *With AI, code generation is cheap—leverage for prototyping and refactoring*

**P26: Fast Feedback Loops** (Operations, High)

- Design systems for immediate feedback; faster iteration enables flow
- `file Knowledge/architectural/principles/P26-fast-feedback-loops.md`
- *Optimize action-to-outcome time; &lt;10s ideal, &gt;60s requires progress bars*

**P27: Nemawashi Mode** (Strategy, High)

- Explore 2-3 alternatives before committing; build consensus with yourself
- `file Knowledge/architectural/principles/P27-nemawashi-mode.md`
- *Japanese consensus-building applied to design: evaluate options explicitly*

**P28: Plans As Code DNA** (Strategy, Critical)

- Code quality determined upstream in plans, not downstream in implementation
- `file Knowledge/architectural/principles/P28-plans-as-code-dna.md`
- *Most important principle: plans generate code; care about plan quality*

**P29: Focus Plus Parallel** (Operations, Medium)

- One primary focus + one auxiliary parallel task; not zero, not five
- `file Knowledge/architectural/principles/P29-focus-plus-parallel.md`
- *Strategic parallelism: you focus, AI works in background*

**P30: Maintain Feel For Code** (Quality, High)

- Stay connected to shape, quality, and craft of generated code
- `file Knowledge/architectural/principles/P30-maintain-feel-for-code.md`
- *Read generated code, understand architecture; should feel mentally tired*

**P31: Own The Planning Process** (Strategy, Critical)

- YOU write plans, AI executes plans; never delegate planning to AI
- `file Knowledge/architectural/principles/P31-own-the-planning-process.md`
- *Planning is strategic judgment; AI handles mechanical execution*

**P32: Simple Over Easy** (Design Philosophy, Critical)

- Choose simple (few braids) over easy (familiar); from Rich Hickey
- `file Knowledge/architectural/principles/P32-simple-over-easy.md`
- *Simple Made Easy: disentangled concepts beat convenient frameworks*

**P33: Old Tricks Still Work** (Quality, Medium)

- Tests, types, linting, refactoring remain essential with AI coding
- `file Knowledge/architectural/principles/P33-old-tricks-still-work.md`
- *Quality practices more important than ever; AI changes speed, not fundamentals*

**P34: Centralized Secrets Management** (Security, Critical)

- All API keys, tokens, and credentials stored in encrypted secrets manager
- `file Knowledge/architectural/principles/P34-secrets-management.md`
- *Single source of truth with audit logging, rotation tracking, encryption at rest*

---

## Quick Reference: When to Load What

| Task Type | Load Modules |
| --- | --- |
| System implementation | `file core.md`, `file safety.md`, `file quality.md` |
| Design review | `file core.md`, `file design.md` |
| Automation workflow | `file safety.md`, `file operations.md` |
| File operations | `file safety.md`, `file quality.md` |
| Documentation | `file quality.md`, `file design.md` |
| Troubleshooting | `file safety.md`, `file quality.md` |
| Quick check | This index only |

---

## Execution Checklist (Major System Changes)

Before implementing scripts, workflows, or infrastructure:

### Pre-Implementation

- [ ]  Load `file Knowledge/architectural/principles/core.md`

- [ ]  Load `file Knowledge/architectural/principles/safety.md`

- [ ]  Load `file Knowledge/architectural/principles/quality.md`

- [ ]  Review relevant principles (especially 5, 7, 11, 15-20)

- [ ]  Define "complete" explicitly before starting

### During Implementation

- [ ]  Ensure dry-run mode supported (Principle 7)

- [ ]  Add error handling and recovery paths (Principle 19)

- [ ]  Apply Minimal Context for context loading (Principle 8)

- [ ]  Generate human-readable first (Principle 1)

- [ ]  Use anti-overwrite protection (Principle 5)

### Post-Implementation

- [ ]  Test with production configuration (Principle 17)

- [ ]  Verify state writes succeeded (Principle 18)

- [ ]  Confirm all objectives met (Principle 15)

- [ ]  Test in fresh thread (Principle 12)

- [ ]  Update change logs (Principle 14)

---

## Organization

Principles are organized into these directories:

- `file Knowledge/architectural/principles/philosophy.md` - Zero-Touch philosophical foundation
- `file Knowledge/architectural/principles/[principle_name].md` - Individual principle files

---

## Change Log

### 2025-10-26 (v2.7) **VELOCITY CODING INTEGRATION**

- **Added 11 new principles (P23-P33):** Velocity Coding philosophy from Ben Guo
- **Created Planning Prompt:** `file Knowledge/architectural/planning_prompt.md` - philosophical DNA for system design
- **Replaced previous P23-P30:** Zero-Touch integration principles superseded by velocity coding framework
- **Key additions:**
  - P23: Identify Trap Doors (irreversible decisions)
  - P24: Simulation Over Doing (prototype first)
  - P25: Code Is Free (leverage AI generation)
  - P26: Fast Feedback Loops (&lt;10s ideal)
  - P27: Nemawashi Mode (explore alternatives)
  - P28: Plans As Code DNA (MOST CRITICAL - quality is upstream)
  - P29: Focus Plus Parallel (one + one optimal)
  - P30: Maintain Feel For Code (understand what you generate)
  - P31: Own The Planning Process (you plan, AI executes)
  - P32: Simple Over Easy (Rich Hickey's principle)
  - P33: Old Tricks Still Work (tests, types, linting)
- **Framework:** Think (40%) → Plan (30%) → Execute (10%) → Review (20%)
- **Integration complete:** Planning prompt auto-loads for system design work
- **Updated:** Vibe Builder persona v1.2 with planning prompt integration

### 2025-10-19 (v2.6)

- **Batch 3:** Integrated 11 final acceptable lessons (all remaining except speculative #13)
- **Total integrated today:** 25 lessons (6 approved + 8 batch 2 + 11 batch 3)
- **Coverage:** 96% of valid lessons (25/26) now integrated into principles
- **Updated modules:**
  - [safety.md](http://safety.md): Added protected file patterns (P5)
  - [quality.md](http://quality.md): Added exit codes (P18/P19), multi-phase resume (P18/P15), automated cleanup execution (P15), automated mode (P15/P18), running scripts before manual phases (P21)
  - [core.md](http://core.md): Added centralized configuration pattern (P2)
  - [design.md](http://design.md): Added noun-first title structure (P1)
- All lessons include concrete examples, implementation patterns, key insights, and applications

### 2025-10-19 (v2.5)

- Integrated 8 additional lessons from batch review (total 14 lessons integrated today)
- **Safety principles** ([safety.md](http://safety.md)): 
  - P7: Automated cleanup pattern, multi-phase cleanup operations
  - P11: Graceful degradation for enhancements, post-archive timeline integration
- **Quality principles** ([quality.md](http://quality.md)): 
  - P15: Dry-run early return ordering, dual title generation, mock data in production, no glazing feedback
  - P16: Quantitative thresholds over boolean checks
  - P18: State verification cross-references
  - P21: Ask clarifying questions pattern, document assumptions explicitly
- All lessons include context, implementation patterns, and key insights for reuse

### 2025-10-19 (v2.4)

- Integrated 6 approved lessons from lessons review system
- Added comprehensive case study to P20 (Modular Design) documenting architectural principles modularization
- Enhanced P14 (Change Tracking) and P17 (Test with Production) with lessons learned examples
- Quality principles (P15, P16, P21) already contained integrated lessons from Oct 12

### 2025-10-16 (v2.3)

- **Added Principle 22:** Language Selection for Purpose
- Created `file Knowledge/architectural/principles/language_selection.md`
- Covers: Shell vs Python vs Node.js vs Go trade-offs
- Includes: SQLite vs server databases, SDK considerations, vibe-coding factors
- Lesson from: Scripting language selection discussion

### 2025-10-12 (v2.2)

- **Added Principle 21:** Document All Assumptions, Placeholders, and Stubs
- **Enhanced Principle 16:** Added critical anti-pattern about false API limitations (Gmail API example)
- Both lessons from recurring mistakes in implementation work

### 2025-10-12 (v2.1)

- **BREAKING:** Modularized monolithic document into 5 focused modules
- Created `Knowledge/architectural/principles/` directory
- Split principles into: core, safety, quality, design, operations
- Converted main file to lightweight index
- Enabled selective loading for context efficiency
- Updated execution checklist with module references

### 2025-10-12 (v2.0)

- Added Principles 15-20 based on thread export refactoring and meeting digest lessons
- **Principle 15:** Complete before claiming complete
- **Principle 16:** Accuracy over sophistication
- **Principle 17:** Test with production configuration
- **Principle 18:** State verification is mandatory
- **Principle 19:** Error handling is not optional
- **Principle 20:** Modular design for context efficiency
- Added "For Major System Changes" checklist to execution section

### 2025-09-21 (v1.0)

- Initial principles document
- Established core principles
- Defined core principles 1-14
- Created execution checklist
