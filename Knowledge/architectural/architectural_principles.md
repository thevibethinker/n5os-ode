---
date: "2025-10-19T00:00:00Z"
version: 2.6
category: core
priority: high
related_files: "['N5/knowledge/ingestion_standards.md']"
---
# N5 Architectural Principles

**Version**: 2.0 (Zero-Doc Integration)
**Last Updated**: 2025-10-24
**Status**: Living document

---

## Purpose

This document serves as the architectural foundation for N5OS—the operating system for AI-enabled knowledge work. These principles guide all system design decisions, workflow implementations, and tooling choices.

**NEW (v2.0)**: Added philosophical foundation layer (Zero-Doc) and derived 8 new architectural principles.

---

## Principle Hierarchy

### Philosophy Layer (Zero-Doc)

Strategic principles that define *why* we build systems this way:

- **ZD1**: Context + State Framework
- **ZD2**: Flow vs. Pools
- **ZD3**: Organization Step Shouldn't Exist  
- **ZD4**: Maintenance > Organization
- **ZD5**: SSOT Always (Single Source of Truth)
- **ZD6**: Gestalt Evaluation
- **ZD7**: AIR Pattern (Assess-Intervene-Review)
- **ZD8**: Minimal Touch
- **ZD9**: Self-Aware Systems
- **ZD10**: Platform Orchestration

**See**: `file 'Knowledge/architectural/principles/philosophy.md'`

---

## Principles Index

### Design Principles (1-10)

### Core Principles → `file 'Knowledge/architectural/principles/core.md'`
**Load for:** All operations, foundational rules

- **Principle 2:** Single Source of Truth (SSOT)

**Key concept:** Eliminate duplication

---

### Safety Principles (11-15)  

### Safety Principles → `file 'Knowledge/architectural/principles/safety.md'`
**Load for:** File operations, automation, destructive actions

- **Principle 5:** Safety, Determinism, and Anti-Overwrite
- **Principle 7:** Idempotence and Dry-Run by Default
- **Principle 11:** Failure Modes and Recovery
- **Principle 19:** Error Handling is Not Optional

**Key concept:** Prevent data loss, enable recovery, handle errors gracefully

---

### Quality Principles → `file 'Knowledge/architectural/principles/quality.md'`
**Load for:** Implementations, documentation, verification

- **Principle 1:** Human-Readable First
- **Principle 15:** Complete Before Claiming Complete
- **Principle 16:** Accuracy Over Sophistication
- **Principle 18:** State Verification is Mandatory
- **Principle 21:** Document All Assumptions, Placeholders, and Stubs

**Key concept:** Accurate, complete, verifiable outputs

---

### Design Principles → `file 'Knowledge/architectural/principles/design.md'`
**Load for:** System architecture, information design, voice application

- **Principle 3:** Voice Integration Policy  
- **Principle 4:** Ontology-Weighted Analysis
- **Principle 8:** Minimal Context, Maximal Clarity
- **Principle 20:** Modular Design for Context Efficiency
- **Principle 22:** Language Selection for Purpose (Shell, Python, Node.js, Go trade-offs)

**Key concept:** Efficient design, appropriate tooling

---

### Operations Principles → `file 'Knowledge/architectural/principles/operations.md'`
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

### Zero-Doc Integration Principles (23-30) **NEW**

**P23: State Management Philosophy** (Design, High)
- Every component must maintain and expose queryable, auditable state
- `file 'Knowledge/architectural/principles/state_management.md'`
- *Derived from: ZD1 (Context + State Framework)*

**P24: Information Flow Design** (Design, Critical)
- Design for flow, not storage; pools are system failures
- `file 'Knowledge/architectural/principles/information_flow.md'`
- *Derived from: ZD2 (Flow vs. Pools)*

**P25: Automated Organization Philosophy** (Design, High)
- Organization emerges from use; categorization should be automatic
- `file 'Knowledge/architectural/principles/automated_organization.md'`
- *Derived from: ZD3 (Organization Step Shouldn't Exist)*

**P26: Maintenance-First Design** (Design, High)
- Design for continuous maintenance with review rhythms and health checks
- `file 'Knowledge/architectural/principles/maintenance_first.md'`
- *Derived from: ZD4 (Maintenance > Organization)*

**P27: System Integration Patterns** (Design, High)
- Optimize for system-wide effectiveness, not individual component excellence
- `file 'Knowledge/architectural/principles/system_integration.md'`
- *Derived from: ZD6 (Gestalt Evaluation)*

**P28: AIR Pattern** (Operations, Critical)
- Assess-Intervene-Review: AI automates first two, humans review
- `file 'Knowledge/architectural/principles/air_pattern.md'`
- *Derived from: ZD7 (AIR Pattern)*

**P29: Human-in-Loop Design** (Operations, Critical)
- Humans as approvers of what matters, not operators of routine processes
- `file 'Knowledge/architectural/principles/human_in_loop.md'`
- *Derived from: ZD8 (Minimal Touch)*

**P30: Minimal Touch Philosophy** (Operations, High)
- Reduce human intervention to strategic decisions and exceptions only
- `file 'Knowledge/architectural/principles/minimal_touch.md'`
- *Derived from: ZD8 (Minimal Touch)*

---

## Quick Reference: When to Load What

| Task Type | Load Modules |
|-----------|-------------|
| System implementation | `core.md`, `safety.md`, `quality.md` |
| Design review | `core.md`, `design.md` |
| Automation workflow | `safety.md`, `operations.md` |
| File operations | `safety.md`, `quality.md` |
| Documentation | `quality.md`, `design.md` |
| Troubleshooting | `safety.md`, `quality.md` |
| Quick check | This index only |

---

## Execution Checklist (Major System Changes)

Before implementing scripts, workflows, or infrastructure:

### Pre-Implementation
- [ ] Load `file 'Knowledge/architectural/principles/core.md'`
- [ ] Load `file 'Knowledge/architectural/principles/safety.md'`
- [ ] Load `file 'Knowledge/architectural/principles/quality.md'`
- [ ] Review relevant principles (especially 5, 7, 11, 15-20)
- [ ] Define "complete" explicitly before starting

### During Implementation
- [ ] Ensure dry-run mode supported (Principle 7)
- [ ] Add error handling and recovery paths (Principle 19)
- [ ] Apply Minimal Context for context loading (Principle 8)
- [ ] Generate human-readable first (Principle 1)
- [ ] Use anti-overwrite protection (Principle 5)

### Post-Implementation
- [ ] Test with production configuration (Principle 17)
- [ ] Verify state writes succeeded (Principle 18)
- [ ] Confirm all objectives met (Principle 15)
- [ ] Test in fresh thread (Principle 12)
- [ ] Update change logs (Principle 14)

---

## Organization

Principles are organized into these directories:
- `Knowledge/architectural/principles/philosophy.md` - Zero-Doc philosophical foundation
- `Knowledge/architectural/principles/[principle_name].md` - Individual principle files

---

## Change Log

### 2025-10-19 (v2.6)
- **Batch 3:** Integrated 11 final acceptable lessons (all remaining except speculative #13)
- **Total integrated today:** 25 lessons (6 approved + 8 batch 2 + 11 batch 3)
- **Coverage:** 96% of valid lessons (25/26) now integrated into principles
- **Updated modules:**
  - safety.md: Added protected file patterns (P5)
  - quality.md: Added exit codes (P18/P19), multi-phase resume (P18/P15), automated cleanup execution (P15), automated mode (P15/P18), running scripts before manual phases (P21)
  - core.md: Added centralized configuration pattern (P2)
  - design.md: Added noun-first title structure (P1)
- All lessons include concrete examples, implementation patterns, key insights, and applications

### 2025-10-19 (v2.5)
- Integrated 8 additional lessons from batch review (total 14 lessons integrated today)
- **Safety principles** (safety.md):
  - P7: Automated cleanup pattern, multi-phase cleanup operations
  - P11: Graceful degradation for enhancements, post-archive timeline integration
- **Quality principles** (quality.md):
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
- Created `Knowledge/architectural/principles/language_selection.md`
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
