# Export Spec 001: List System

**System:** Dynamic Action Lists with JSONL Storage  
**Version:** 3.1 (Battle-tested)  
**Maturity:** Production, 6+ months active use  
**Last Updated:** 2025-10-28

---

## 1. System Overview

### Purpose
Structured, queryable action tracking system. Lists are "living databases" - JSONL backends + auto-generated markdown views. Think: lightweight database tables without database overhead.

### Core Concept
**Lists = Programs, not files.** Each list is a bounded context with its own operations. Items flow through states (open → pinned → done → archived). Schema-validated, append-only by default.

### Key Capabilities
- Add/update/find/move/pin/promote operations
- Automatic markdown view generation
- Schema validation per list type
- Duplicate detection
- Health monitoring
- Export to various formats

---

## 2. Architecture

### File Structure
```
N5/lists/
├── index.jsonl              # Registry of all lists
├── POLICY.md                # Operational rules
├── README.md                # Generated documentation
├── {list-name}.jsonl        # Data (append-only)
├── {list-name}.md           # Auto-generated view
└── {list-name}.jsonl.template  # Optional schema template
```

### Data Model

**Registry Entry** (index.jsonl):
```json
{
  "slug": "ideas",
  "title": "Ideas",
  "path_jsonl": "N5/lists/ideas.jsonl",
  "path_md": "N5/lists/ideas.md",
  "tags": ["ideation", "backlog"],
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-10-28T12:00:00Z"
}
```

**List Item** (universal schema):
```json
{
  "id": "uuid-v4",
  "created_at": "2025-10-28T12:00:00Z",
  "updated_at": "2025-10-28T14:00:00Z",
  "title": "Item title (max 200 chars)",
  "body": "Optional detailed description",
  "tags": ["tag1", "tag2"],
  "status": "open|pinned|done|archived|planned",
  "priority": "L|M|H" or 1-5,
  "links": [
    {"type": "file", "value": "path/to/file"},
    {"type": "url", "value": "https://..."},
    {"type": "ref", "value": "another-item-id"}
  ],
  "source": "conversation_id or manual",
  "project": "optional project grouping",
  "due": "2025-11-01T00:00:00Z",
  "notes": "additional context"
}
```

### Core Operations

**lists-add**: Append new item
```bash
python3 n5_lists_add.py ideas --title "Build X" --tags feature,priority
```

**lists-set**: Update existing (finds by ID or fuzzy match)
```bash
python3 n5_lists_set.py ideas "Build X" --status done --priority H
```

**lists-find**: Query with filters
```bash
python3 n5_lists_find.py ideas --status open --tags priority --limit 10
```

**lists-move**: Transfer item between lists
```bash
python3 n5_lists_move.py ideas "item-title" system-upgrades
```

**lists-pin**: Promote to pinned status
```bash
python3 n5_lists_pin.py ideas "important-item"
```

**lists-promote**: Graduate item to knowledge base
```bash
python3 n5_lists_promote.py ideas "item-id" --target Knowledge/concepts/
```

**lists-create**: Initialize new list
```bash
python3 n5_lists_create.py new-list "Display Name" --tags tracking,automation
```

**lists-health-check**: Validate integrity
```bash
python3 n5_lists_health_check.py --all --fix
```

---

## 3. Design Decisions & Rationale

### Why JSONL?
- **Append-friendly**: No need to parse entire file to add item
- **Merge-friendly**: Git can resolve conflicts line-by-line
- **Grep-friendly**: Standard text search works
- **Stream-friendly**: Process one line at a time for large lists
- **Simple**: No database setup, just text files

### Why Dual Format (JSONL + MD)?
- **JSONL = Source of truth**: Machine-readable, validated
- **MD = Human view**: Quick scanning, readable in file browser
- **Auto-sync**: MD regenerated on every write operation
- **Best of both**: Structured data + browsable docs

### Status Flow
```
open → pinned → done → archived
       ↓
    planned (future work)
```

**pinned**: "Do this next" signal  
**planned**: "Someday/maybe" parking lot  
**archived**: Preserve history without clutter

### Duplicate Detection
Uses fuzzy matching (Levenshtein distance) on titles. Threshold: 85% similarity = probable duplicate. Warns but doesn't block (user decides).

---

## 4. Integration Points

### With Commands System
Lists integrate with command registry - operations become invokable commands. Example: `N5: add to ideas "Build feature X"`

### With Docgen
`docgen --lists` regenerates all markdown views. Runs on-demand or via scheduled task.

### With Knowledge Base
`lists-promote` graduates validated items from lists → permanent docs in Knowledge/. Creates bidirectional links.

### With Timeline
List operations can auto-log to system timeline for audit trail.

---

## 5. Schemas

**See attached:**
- `lists.item.schema.json` - Universal item structure
- `lists.registry.schema.json` - Index entry format

**Validation:**
```python
from jsonschema import Draft202012Validator
validator = Draft202012Validator(schema)
validator.validate(item)  # Raises if invalid
```

---

## 6. Testing Strategy

### Validation Tests
- Schema compliance for all items
- Registry consistency (paths exist, no duplicates)
- Status values within allowed enum
- ISO8601 timestamp format

### Integration Tests
- Add item → verify appears in JSONL and MD
- Update item → verify changes reflected, updated_at bumps
- Move item → verify removed from source, added to target
- Health check → verify catches and fixes common issues

### Example Test Scenarios
```python
# Add duplicate detection test
items = [
    {"title": "Build API endpoint"},
    {"title": "Build API endpont"}  # Typo
]
# Should warn: 95% similarity
```

---

## 7. Operational Considerations

### Performance
- **Add**: O(1) append
- **Find**: O(n) scan (acceptable for <10k items per list)
- **Update**: O(n) read + rewrite (use sparingly on huge lists)
- **Health check**: O(n*m) for duplicate detection (run nightly)

### Scaling
- Works well up to ~5k items per list
- Beyond 10k: consider splitting or moving to SQLite
- Current largest list: system-upgrades (~200 items)

### Backup Strategy
- JSONL files committed to git
- Auto-backup on destructive operations (move, mass update)
- Recovery: `git revert` or restore from `.backup` files

### Error Handling
- Invalid JSON: Skip line, log warning, continue
- Missing fields: Fill with defaults per schema
- Write failures: Rollback transaction, preserve original

---

## 8. Migration Guide

### For New Implementers

**Minimal Implementation (1-2 hours):**
1. Create `lists/` directory
2. Implement `lists-add` (append to JSONL)
3. Implement `lists-find` (filter + display)
4. Implement basic schema validation

**Full Implementation (1-2 days):**
1. All CRUD operations (add/set/find/move)
2. Markdown view generation
3. Registry management (index.jsonl)
4. Health check tooling
5. Duplicate detection

**Reference Implementations:**
- Python scripts: `/home/workspace/N5/scripts/n5_lists_*.py`
- Safety layer: Import `n5_safety.py` for command validation
- Examples: See N5/lists/ for production data

---

## 9. Known Issues & Gotchas

### Issue: Concurrent Writes
**Problem:** Two processes append simultaneously = race condition  
**Solution:** File locking or atomic rename pattern  
**Current:** Not implemented (low risk, single user)

### Issue: Large List Performance
**Problem:** Reading 10k+ items for each find operation  
**Solution:** Build index or migrate to SQLite  
**Current:** Acceptable for current scale

### Issue: Schema Evolution
**Problem:** Adding new fields breaks old items  
**Solution:** Schema versioning + migration scripts  
**Current:** `additionalProperties: true` allows graceful growth

---

## 10. Success Metrics

**System is working well when:**
- 95%+ of list operations succeed without manual intervention
- Health checks pass daily
- No data loss incidents
- Users prefer lists over ad-hoc text files
- Average time-to-add: <30 seconds

**Current Stats (N5 OS):**
- 15 active lists
- ~500 total items
- 0 data loss incidents in 6 months
- Daily usage: 5-20 operations

---

## 11. Related Systems

**Dependencies:**
- Schema validation library (jsonschema)
- Command safety layer (optional but recommended)

**Synergies:**
- Works well with docgen for documentation
- Pairs with timeline for audit trail
- Integrates with command authoring for workflow automation

---

## Philosophy Notes

This system embodies **"Flow Over Pools"** - items flow through states rather than sitting in static buckets. It's **"Simple Over Easy"** - JSONL is simple (just text files), even if not the easiest (no GUI, must learn commands).

The dual format (JSONL + MD) respects both machine and human needs - neither is sacrificed for the other.

---

**Implementation Checklist:**
- [ ] Create lists/ directory structure
- [ ] Implement lists-add (core operation)
- [ ] Implement lists-find (query interface)
- [ ] Add schema validation
- [ ] Build markdown view generator
- [ ] Create registry management (index.jsonl)
- [ ] Add health check tooling
- [ ] Write tests for CRUD operations
- [ ] Document custom list types (if any)
- [ ] Set up automated backup strategy

---

*Export specification format v1.0*
