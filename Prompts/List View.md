---
description: 'Enforces Single Source of Truth (SSOT) principle for lists by:'
tags:
- lists
- view
- docgen
- ssot
---
# `list-view`

**Version:** 1.0.0

**Summary:** View any list by generating an on-demand markdown view from the JSONL source

**Workflow:** lists

**Tags:** lists, view, ssot, docgen

---

## Purpose

Enforces Single Source of Truth (SSOT) principle for lists by:
- Keeping `.jsonl` as the only source of truth
- Generating `.md` views on-demand when needed
- Eliminating dual-write sync complexity

---

## Inputs

- `list` : string — List slug (e.g., "system-upgrades", "ideas")
- `format` : string — Output format: "markdown" (default), "json", "table"
- `filter` : string — Optional filter expression (e.g., "status=planned", "priority=H")

---

## Outputs

- Formatted view of the list contents
- Temporary `.md` file in conversation workspace (if markdown format)

---

## Usage

```bash
# View system upgrades
n5 list-view system-upgrades

# View with filter
n5 list-view system-upgrades filter="priority=H"

# View as table
n5 list-view ideas format=table
```

---

## Implementation Strategy

**Phase 1 (Current):** Manual invocation via Zo
- User: "Show me system upgrades"
- Zo: Reads `.jsonl`, formats response

**Phase 2 (Scripted):** Python script wrapper
```python
#!/usr/bin/env python3
# /home/workspace/N5/scripts/n5_list_view.py
import json, sys
from pathlib import Path

list_slug = sys.argv[1]
jsonl_path = Path(f"/home/workspace/Lists/{list_slug}.jsonl")

for line in jsonl_path.read_text().strip().split('\n'):
    item = json.loads(line)
    print(f"## {item.get('title', item.get('summary', 'Untitled'))}")
    print(f"**Status:** {item.get('status', 'unknown')}")
    print(f"**Priority:** {item.get('priority', 'medium')}")
    print()
```

**Phase 3 (Full):** Integrated with `lists-docgen` command
- Wrap existing `lists-docgen` functionality
- Add filtering and formatting options
- Output to conversation workspace or display

---

## Related Commands

- `lists-docgen` — Regenerate all MD views (batch operation)
- `lists-find` — Search/filter list items
- `lists-export` — Export to MD or CSV

---

## Architectural Principles

- **P2 (SSOT):** `.jsonl` is single source of truth
- **P8 (Minimal Context):** Generate views on-demand, not stored
- **P20 (Modular):** View generation separate from data storage

---

## Migration Notes

**Before SSOT enforcement:**
- Lists had both `.md` and `.jsonl` files
- Required dual-write sync
- Frequent divergence

**After SSOT enforcement:**
- Only `.jsonl` files maintained
- `.md` generated on-demand via this command
- No sync complexity

---

## Examples

### Example 1: View high-priority system upgrades
```bash
n5 list-view system-upgrades filter="priority=H"
```

### Example 2: Export ideas as markdown to conversation workspace
```bash
n5 list-view ideas format=markdown > /tmp/ideas-view.md
```

### Example 3: Quick table view
```bash
n5 list-view must-contact format=table
```

---

**Status:** Active  
**Last Updated:** 2025-10-15
