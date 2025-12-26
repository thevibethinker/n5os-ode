# N5OS Lite Assumptions & Dependencies

**Version:** 1.2.2  
**Purpose:** Document all assumptions, dependencies, and requirements  
**Principle:** P21 (Document All Assumptions)

---

## Directory Structure Assumptions

### Required Directories

**System expects these to exist:**
```
workspace/
├── .n5os/lists/          # Canonical list storage
├── Prompts/              # User prompts
├── Knowledge/            # Knowledge base
├── Documents/            # Active work
└── Inbox/                # Temporary staging
```

**Fallback Behavior:**
- Scripts check `.n5os/lists/` first
- If not found, try `Lists/` (root level)
- Create `.n5os/lists/` if neither exists

### File Locations

| Component | Canonical Location | Legacy Location | Behavior |
|-----------|-------------------|-----------------|----------|
| Lists | `.n5os/lists/` | `Lists/` | Check both |
| Personas | `.n5os/personas/` | None | Create if missing |
| Config | `.n5os/config/` | None | Use defaults |
| Knowledge | `Knowledge/` | None | Create if missing |

---

## Schema Assumptions

### List Entry Format

**All list entries MUST have:**
```json
{
  "name": "string (required)",
  "slug": "lowercase-hyphenated (required)",
  "description": "string",
  "tags": ["array", "of", "strings"],
  "created": "YYYY-MM-DD (required)",
  "updated": "YYYY-MM-DD (required)",
  "status": "active|archived|deprecated"
}
```

**Field Validation:**
- `name`: Non-empty string
- `slug`: Lowercase, hyphens only, no spaces
- `tags`: Lowercase, hyphens for multi-word
- `status`: Must be "active", "archived", or "deprecated" (NOT "open"/"closed")
- Dates: ISO format YYYY-MM-DD

---

## Python Dependencies

### Standard Library (Always Available)
- pathlib, json, sys, argparse, logging, datetime, hashlib

### Bundled Modules (Included in Package)
- n5_safety.py
- executable_manager.py
- direct_ingestion_mechanism.py
- file_guard.py
- validate_list.py
- session_state_manager.py

### Optional External (Not Required)
None - N5OS Lite is self-contained

---

## Script Dependencies

| Script | Depends On | Purpose |
|--------|-----------|---------|
| n5_lists_add.py | n5_safety | Validation |
| n5_docgen.py | executable_manager, n5_safety | Doc generation |
| n5_knowledge_ingest.py | direct_ingestion_mechanism | Knowledge storage |
| file_guard.py | None | Protection system |
| n5_protect.py | file_guard | Wrapper |
| spawn_worker.py | session_state_manager | Worker context |

---

## Workspace Assumptions

### File Permissions
- Scripts assume read/write access to workspace
- `.n5os/` directory is user-owned
- No special privileges required

### Path Resolution
- Workspace root: `$HOME/workspace` or `/home/workspace`
- Conversation workspace: `/home/.z/workspaces/{id}`
- Scripts use `Path.home() / "workspace"`

### File Formats
- Lists: JSONL (one JSON object per line)
- Knowledge: Markdown with YAML frontmatter
- Config: YAML
- Schemas: JSON Schema draft 2020-12

---

## Behavioral Assumptions

### Default Values

```python
# When not specified:
status = "active"           # Not "open" or "new"
created = today()           # ISO format
updated = today()           # ISO format
tags = []                   # Empty array, not null
slug = auto_generated       # From name if missing
```

### Error Handling

- **File not found:** Create with defaults
- **Invalid JSON:** Skip line, log warning
- **Missing required field:** Reject entry
- **Permission denied:** Fail with clear error

---

## Known Limitations

### Stub Implementations

**executable_manager.py:**
- Reads from JSONL only (no database)
- No caching
- No validation
- Simple list implementation

**direct_ingestion_mechanism.py:**
- No LLM extraction
- Basic file creation only
- No entity recognition
- No relationship mapping

### Future Enhancements

When moving from stub to full implementation:
1. Add database backend for executable_manager
2. Integrate LLM for knowledge extraction
3. Add entity/relationship extraction
4. Implement caching layer

---

## Integration Assumptions

### AI Assistant Integration

**Scripts assume AI can:**
- Execute Python scripts via `run_bash_command`
- Read/write files in workspace
- Parse JSONL format
- Follow prompts that reference scripts

**Scripts do NOT assume:**
- Direct database access
- External API access
- Network connectivity
- Root/admin privileges

---

## Testing Assumptions

### Validation

Scripts validate:
- ✅ Required fields present
- ✅ Field types correct
- ✅ Slug format valid
- ✅ Status values valid

Scripts do NOT validate:
- ❌ Business logic constraints
- ❌ Cross-list references
- ❌ Semantic correctness

---

## Change Log

| Date | Version | Change | Reason |
|------|---------|--------|--------|
| 2025-11-03 | 1.2.2 | Created ASSUMPTIONS.md | P21 compliance |
| 2025-11-03 | 1.2.2 | Documented dependencies | Fix import errors |
| 2025-11-03 | 1.2.2 | Standardized directory structure | P2 compliance |
| 2025-11-03 | 1.2.2 | Schema-script alignment | Fix field mismatch |

---

**When in doubt, check this document. When assumptions change, update this document.**

*P21: Explicit > Implicit. Document everything.*
