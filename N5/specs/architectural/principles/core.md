---
date: "2025-10-12T00:00:00Z"
version: 2.0
category: core
priority: critical
---
# Core Principles

These are foundational principles that apply across all N5 operations.

## 2) Single Source of Truth (SSOT)

**Purpose:** Eliminate duplication, prevent drift

**Rules:**
- Each fact lives in exactly one reservoir file, linked everywhere else.
- Prefer updating the canonical location over duplicating content.
- When referencing information, point to source via file mentions or cross-references.

**When to apply:** 
- Adding new information
- Updating existing information
- Designing new data structures

**Anti-patterns:**
- Copying the same fact to multiple files
- Creating summary documents that duplicate source content
- Embedding full context instead of linking to canonical source

**Lessons Learned:**

**Centralized Configuration with Auto-Generated Documentation (2025-10-16):**
- **Pattern:** Store command metadata in single JSONL registry (`commands.jsonl`), auto-generate markdown docs from it
- **Benefits:**
  - Single edit updates both execution layer and documentation
  - Reduces documentation drift
  - Registry becomes programmable (scripts can query available commands)
  - Markdown docs remain human-readable and git-friendly
- **Implementation:** `commands.jsonl` (SSOT) → `generate_command_docs.py` → `command_index.md` (generated)
- **Key insight:** When configuration needs both machine-readable and human-readable forms, store once and generate the other
- **Application:** Any system where you have both config files and documentation (API specs, command registries, workflow definitions)

---

## 8) Minimal Context Loading

**Purpose:** Load only what's needed for the task

**Rules:**
- Package domain knowledge into reusable personas for efficient context loading
- Complete systems require both infrastructure AND execution layer
- Don't claim "complete" if automation trigger is missing

**When to apply:**
- Building new subsystems
- Adding major features
- Refactoring

**Example from Vibe Builder persona (2025-10-13):**
- Consolidated architectural principles, anti-patterns, script templates, troubleshooting patterns into single 5.5KB document
- Loadable reference enables consistent system-building without re-reading 20+ files
- Principle: Package domain knowledge into reusable personas for context efficiency.

**Example from workspace cleanup (2025-10-14):**
- System had robust cleanup infrastructure: reports, dry-run, safety checks
- But no automation trigger - 20+ reports accumulated without execution
- Missing piece: scheduled task with --execute flag
- Principle: Complete system requires both infrastructure AND automation trigger. Don't claim complete if execution layer missing.

---
