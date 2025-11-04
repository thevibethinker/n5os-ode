---
description: Convert Records → Knowledge with classification and tagging
tool: true
tags:
  - knowledge
  - classification
  - processing
---

# Process to Knowledge

Convert raw records to structured knowledge.

**Workflow:**

1. Identify source file(s) in `file Records/` 
2. Review and classify content type (guide, reference, analysis, decision)
3. Extract key insights and structure
4. Tag appropriately using `file N5/config/emoji-legend.json`
5. Move to appropriate Knowledge subdirectory
6. Update `file Knowledge/index.md` if significant
7. Archive original in `file Records/Archive/`

**Principles:**
- P1: Human-readable paths and filenames
- P2: Single Source of Truth (avoid duplication)
- Modular separation by domain
