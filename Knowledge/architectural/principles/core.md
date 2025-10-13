---
date: "2025-10-12T00:00:00Z"
version: 2.0
category: core
priority: critical
---
# Core Principles

These are foundational principles that apply across all N5 operations.

## 0) LLM Sourcing Directive (Rule-of-Two)

**Purpose:** Minimize context bloat and enforce clarity

**Rules:**
- Always load at most two preference/config files in context:
  1. `file 'N5/knowledge/ingestion_standards.md'`
  2. `file 'Knowledge/architectural/principles/[module].md'` (relevant module)
- Do not load additional prefs/voice files. If a third is needed, stop and ask.
- Order of precedence for conflicts: Architectural Principles > Ingestion Standards > ephemeral instructions.

**When to apply:** Every operation, always


**Example from lesson extraction (2025-10-12):**
- Thread: con_JB5UD88QWtAkoaXF
- Issue: Split 400-line monolithic architectural principles document into 5 focused modules: core.md (principles 0,2), safety.md (5,7,11,19), quality.md (1,15,16,18,21), design.md (3,4,8,20), operations.md (6,9,10,12,13,14,17). Created lightweight index for navigation.
- Context: Monolithic principles document was loaded entirely every time, wasting tokens and context window. Different tasks need different subsets of principles. User wanted Rule-of-Two compliance with selective loading.
- Resolution: Achieved ~70% context reduction for typical operations. Can now load index + 1-2 relevant modules instead of entire document. Follows Principle 20 (Modular Design) and Principle 8 (Minimal Context).


**Example from lesson extraction (2025-10-12):**
- Thread: con_JB5UD88QWtAkoaXF
- Issue: Instead of updating architectural principles ad-hoc during conversations, capture lessons to pending storage for weekly batch review. Review session allows approve/edit/reject with principle updates only for approved lessons. Archive approved, discard rejected, keep pending for next time.
- Context: Making same mistakes repeatedly because lessons weren't formally captured and integrated into principles. Needed systematic way to learn from experience and update decision-making frameworks.
- Resolution: Built complete workflow: auto-extract on conversation-end → pending/ storage → Sunday evening review → update principles → archive. Scheduled task reminds weekly. Takes 15-30 min/week. Enables continuous improvement without disrupting conversations.

---

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
