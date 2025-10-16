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
