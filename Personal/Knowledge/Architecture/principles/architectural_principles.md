# N5 Architectural Principles

**Purpose:** Core design principles guiding N5 system development  
**Version:** 2.0  
**Updated:** 2025-10-26

---

## Overview

These principles represent distilled wisdom from building and maintaining N5 systems. They're not abstract theory—they're battle-tested patterns that prevent common mistakes.

**How to use:** Before making architectural decisions, review relevant principles. When stuck, check which principles you might be violating.

---

## Core Principles (P0-P22)

See individual principle files in `principles/` directory for details:

- **P0:** Rule-of-Two (max 2 context files)
- **P1:** Human-Readable Formats (text over binary)
- **P2:** Single Source of Truth (SSOT)
- **P5:** Anti-Overwrite (preview before destroy)
- **P7:** Dry-Run (simulate before execute)
- **P8:** Minimal Context (less is more)
- **P11:** Failure Modes (plan for breakage)
- **P15:** Complete Before Claiming (verify done)
- **P16:** No Invented Limits (cite or admit)
- **P17:** Test Production Config (not toy data)
- **P18:** Verify State (check it worked)
- **P19:** Error Handling (explicit, never silent)
- **P20:** Modular Components (composable, independent)
- **P21:** Document Assumptions (no hidden magic)
- **P22:** Language Selection (right tool for job)

---

## New Principles (P23-P39)

### Design Philosophy
- **P24:** Simulation Over Doing - Dry-run everything before execution
- **P25:** Code Is Free, Thinking Is Expensive - Optimize for understanding
- **P27:** Nemawashi Mode - Explore 2-3 alternatives before committing
- **P32:** Simple Over Easy - Few concepts > familiar patterns
- **P33:** Old Tricks Still Work - Boring technology solves most problems

### Development Practice
- **P26:** Fast Feedback Loops - Minimize action → result time
- **P28:** Plans as Code DNA - Specifications generate code
- **P29:** Focus Plus Parallel - Deep work on critical path
- **P30:** Maintain Feel for Code - Keep intuition calibrated
- **P31:** Own the Planning Process - Don't outsource thinking

### Security
- **P34:** Centralized Secrets Management - Encrypted, audited, rotated

### Building Fundamentals (NEW - Jan 2026)
- **P35:** Version, Don't Overwrite - Create new versions, never mutate inputs
- **P36:** Make State Visible - Hidden state causes bugs; declare and validate
- **P37:** Design as Pipelines - Input → Transform → Output with recoverable stages
- **P38:** Isolate by Default, Parallelize Proactively - Workers don't share state; bias toward Pulse
- **P39:** Audit Everything - Every change traceable to cause, trigger, and timestamp

See `file 'Personal/Knowledge/Architecture/principles/P35-P39_building_fundamentals.md'` for full details.

### Validation & Quality (NEW - Feb 2026)
- **P40:** Specify Behaviorally - Define acceptance as observable scenarios (Given/When/Then/Verify), not implementation checklists. Specs must be complete enough that output quality can be assessed without reading the output's implementation.

See `file 'Personal/Knowledge/Architecture/principles/P40_specify_behaviorally.md'` for full details.

---

## Principle Categories

### Safety & Reliability
P5, P7, P11, P15, P18, P19, P35, P36

### Design & Architecture
P1, P2, P8, P20, P24, P25, P27, P32, P33, P37

### Development Practice
P0, P16, P17, P21, P22, P26, P28, P29, P30, P31

### Concurrency & Orchestration
P38

### Auditability & Trust
P39

### Validation & Quality
P40

### Security
P34

---

## When to Apply

**Planning Phase:** P27 (Nemawashi), P31 (Own Planning), P32 (Simple Over Easy), P40 (Behavioral Specs)
**Implementation:** P25 (Code Is Free), P26 (Fast Feedback), P28 (Plans as Code)
**Testing:** P7 (Dry-Run), P17 (Production Config), P18 (Verify State), P40 (Scenario Validation)
**Deployment:** P5 (Anti-Overwrite), P15 (Complete First), P24 (Simulation)
**Maintenance:** P2 (SSOT), P8 (Minimal Context), P30 (Feel for Code)
**Security:** P34 (Secrets Management)

---

## Principle Conflicts

Sometimes principles conflict. When they do, use judgment:

**Example:** P8 (Minimal Context) vs P21 (Document Assumptions)
- **Resolution:** Document assumptions, but keep docs minimal
- **Pattern:** Inline comments for "why", not "what"

**Example:** P25 (Code Is Free) vs P8 (Minimal Context)
- **Resolution:** More lines is fine if it reduces concepts
- **Pattern:** Explicit > implicit, even if verbose

---

## Evolution

These principles evolve as we learn. When you encounter a pattern that works, document it. When a principle consistently causes problems, revise it.

**Contributing:** When adding principles:
1. Number sequentially (P35, P36, ...)
2. Use template: Principle → Pattern → Examples → Benefits
3. Update this index
4. Link related principles

---

## Related Documents

- file 'Knowledge/architectural/starter_planning_prompt.md' - Framework for system design
- file 'Knowledge/architectural/principles/' - Individual principle details

---

**Remember:** Principles are guidelines, not laws. Use judgment. Break them when you have good reason, but know why you're breaking them.
