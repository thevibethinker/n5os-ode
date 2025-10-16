---
date: "2025-10-12T00:00:00Z"
version: 2.2
category: core
priority: high
related_files: "['N5/knowledge/ingestion_standards.md']"
---
# N5 Architectural Principles Index

**Version 2.2 - Modular Structure**

This index provides quick reference to all architectural principles. Load specific modules based on task context to minimize token usage and maintain focus.

---

## How to Use This Index

**For most operations:** Load this index file only for quick reference.

**For specific tasks:** Load the relevant module(s) alongside this index:
- **System changes/scripts**: Load `core.md`, `safety.md`, `quality.md`
- **Design reviews**: Load `core.md`, `design.md`
- **Operations/deployments**: Load `operations.md`, `safety.md`
- **Troubleshooting**: Load `safety.md`, `quality.md`

---

## Principle Modules

### Core Principles → `file 'Knowledge/architectural/principles/core.md'`
**Load for:** All operations, foundational rules

- **Principle 2:** Single Source of Truth (SSOT)

**Key concept:** Eliminate duplication

---

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
**Load for:** Architecture, system design, content structure

- **Principle 3:** Voice Integration Policy (Tiered + Tags)
- **Principle 4:** Ontology-Weighted Analysis
- **Principle 8:** Minimal Context, Maximal Clarity
- **Principle 20:** Modular Design for Context Efficiency

**Key concept:** Efficient, selective, purpose-driven design

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

## Change Log

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
