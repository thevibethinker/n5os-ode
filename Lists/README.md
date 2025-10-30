# Lists: Cognitive Tracking System

**Purpose**: Track everything V needs to stay on top of—from fleeting ideas to investor contacts.

---

## Overview

The Lists system is V's extended memory, capturing and organizing information across multiple tracking categories. Each list is a JSONL file (JSON Lines) that stores structured items with rich metadata, tags, and relationships.

### Core Philosophy

- **Single Source of Truth (SSOT)**: JSONL files are the only source of truth; markdown views generated on-demand
- **Intelligent Classification**: Items auto-assign to appropriate lists via URL/content analysis
- **Dynamic Creation**: New lists created on-demand with barebones schema
- **Schema Validation**: Every item validated against schema on write
- **Extensibility**: Custom fields via `additionalProperties: true`
- **Health Monitoring**: Continuous checks for duplicates, corruption, schema violations

---

## Directory Structure

```
Lists/
├── schemas/                    # Schema definitions (portable with data)
│   ├── lists.item.schema.json        # Base item schema
│   ├── lists.registry.schema.json    # List registry schema
│   └── system-upgrades.schema.json   # Custom schema for system tracking
├── POLICY.md                   # List governance rules
├── README.md                   # This file
├── index.jsonl                 # List registry
└── *.jsonl                     # Individual list files (SSOT)

NOTE: .md files are NOT maintained. Use `n5 list-view {list-name}` to generate views on-demand.
```

---

## Active Lists

| List | Purpose | Items | Status |
|------|---------|-------|--------|
| `ideas.jsonl` | General ideas and thoughts | Variable | Active |
| `must-contact.jsonl` | People to reach out to | Variable | Active |
| `system-upgrades.jsonl` | N5 OS improvements | 43+ | Active |
| `fundraising-opportunity-tracker.jsonl` | Investors, rounds, stages | Variable | Active |
| `areas-for-exploration.jsonl` | Topics to explore | Variable | Active |
| `social-media-ideas.jsonl` | Content ideas for social | Variable | Active |
| `opportunity-calendar.jsonl` | Time-sensitive opportunities | Variable | Active |
| `pending-knowledge-updates.jsonl` | Knowledge base updates queue | Variable | Active |
| `[Custom Lists]` | User-defined trackers | Variable | Extensible |

---

## Schema Structure

All list items follow the base schema in `schemas/lists.item.schema.json`:

### Required Fields
- `id` (string, UUID): Unique identifier
- `created_at` (string, ISO 8601): Creation timestamp
- `title` (string, max 200 chars): Item title
- `status` (enum): One of `open`, `pinned`, `done`, `archived`, `planned`

### Optional Fields
- `updated_at` (string, ISO 8601): Last modification timestamp
- `body` (string): Detailed description or notes
- `tags` (array of strings): Categorization tags
- `priority` (string): `H` (High), `M` (Medium), `L` (Low)
- `links` (array of URLs): Related web resources
- `project` (string): Associated project name
- `due` (string, date): Due date (YYYY-MM-DD)
- `notes` (string): Additional context

### Custom Fields
Lists support `additionalProperties: true`, allowing custom fields per list:
- `must-contact.jsonl` might add: `company`, `role`, `met_at`
- `fundraising-opportunity-tracker.jsonl` might add: `stage`, `amount`, `lead_investor`

---

## Usage

### Viewing Lists

**SSOT Enforcement**: Lists are stored as JSONL (single source of truth). Generate markdown views on-demand.

**Command**: `n5 list-view {list-name}`

**Examples**:
```bash
# View system upgrades
n5 list-view system-upgrades

# View with specific format
n5 list-view ideas format=table

# Export to file
n5 list-view must-contact format=markdown > contacts-view.md
```

**Natural Language** (via Incantum):
- "Show me my system upgrades"
- "What's on my must-contact list?"
- "Display my social media ideas"

### Adding Items

**Command**: `lists-add`

**Natural Language** (via Incantum):
```
"Add Lynnette Scott to my must-contact list—we met at Civana, 
she's HR at CMC looking for AI talent"
```

**Direct Script**:
```bash
python3 /home/workspace/N5/scripts/n5_lists_add.py \
  --list must-contact \
  --title "Lynnette Scott" \
  --body "Met at Civana, HR at CMC, looking for AI talent" \
  --tags "recruiting,hr,ai"
```

### Finding Items

**Command**: `lists-find`

**Examples**:
- Find by tag: `lists-find --tag recruiting`
- Find by status: `lists-find --status open`
- Find by text: `lists-find --query "investor"`

### Exporting Lists

**Command**: `lists-export`

**Export to Markdown**:
```bash
python3 /home/workspace/N5/scripts/n5_lists_export.py \
  --list ideas \
  --format markdown \
  --output /home/workspace/Documents/ideas_export.md
```

### Health Checks

**Command**: `lists-health-check`

**Validates**:
- Schema compliance
- Duplicate detection
- Broken references
- File corruption

---

## Intelligent Features

### Auto-Classification

The `listclassifier.py` script automatically assigns items to appropriate lists based on:
- **URL patterns**: LinkedIn → `crm`, GitHub → `tech-resources`
- **Keywords**: "investor", "funding" → `fundraising-opportunity-tracker`
- **Context**: Meeting notes → `must-contact`

### Dynamic List Creation

If a list doesn't exist, the system creates it with:
- Barebones schema (base fields only)
- Empty JSONL file
- Automatic registration
- Schema validation enabled

### Deduplication

The `lists-similarity-scanner` detects potential duplicates via:
- Exact title matches
- Fuzzy string matching (Levenshtein distance)
- URL overlap analysis

---

## Governance

See `POLICY.md` for detailed governance rules:

- **Atomic Operations**: All writes are atomic (no partial updates)
- **Validation**: Every write validates against schema
- **Backups**: Automatic backups before modifications
- **Rollbacks**: Failed operations auto-rollback
- **Protection**: MEDIUM protection tier (validate before edit)

---

## Portability

The Lists system is **fully portable**:

1. **Self-Describing**: Schemas travel with data in `schemas/`
2. **OS-Agnostic**: Standard JSONL format, no N5-specific dependencies
3. **Interpretable**: Any system can read JSONL + apply JSON Schema validation
4. **Documented**: This README explains structure and usage

**Export Procedure**:
```bash
# Package Lists system for export
tar -czf lists_export.tar.gz Lists/
```

The resulting archive contains:
- All list data (`*.jsonl`)
- All schemas (`schemas/*.json`)
- Governance (`POLICY.md`)
- Documentation (`README.md`)

Another system can import and interpret without N5 OS.

---

## Commands Reference

| Command | Purpose | Script |
|---------|---------|--------|
| `lists-add` | Add item to list | `n5_lists_add.py` |
| `lists-find` | Search lists | `n5_lists_find.py` |
| `lists-export` | Export to formats | `n5_lists_export.py` |
| `lists-health-check` | Validate lists | `n5_lists_health_check.py` |
| `lists-similarity-scanner` | Find duplicates | `n5_lists_similarity_scanner.py` |

See `Recipes/recipes.jsonl (index only)` for full command registry.

---

## Technical Details

### File Format

**JSONL** (JSON Lines): One JSON object per line
```jsonl
{"id":"uuid-1","created_at":"2025-10-08T12:00:00Z","title":"Example","status":"open"}
{"id":"uuid-2","created_at":"2025-10-08T13:00:00Z","title":"Another","status":"done"}
```

### Validation

Uses JSON Schema Draft 2020-12 for validation:
```python
import jsonschema
schema = load_schema("Lists/schemas/lists.item.schema.json")
jsonschema.validate(item, schema)
```

### Safety

All list operations go through `n5_safety.py`:
- Dry-run mode available
- Explicit confirmations for destructive actions
- Audit trail logging
- MEDIUM protection enforcement

---

## Examples

### Personal Networking
```jsonl
{
  "id": "uuid-abc",
  "created_at": "2025-10-08T14:30:00Z",
  "title": "Lynnette Scott",
  "status": "open",
  "body": "HR Director at CMC, met at Civana retreat",
  "tags": ["recruiting", "hr", "ai"],
  "priority": "H",
  "company": "CMC",
  "role": "HR Director",
  "met_at": "Civana Retreat, Oct 2025"
}
```

### System Improvements
```jsonl
{
  "id": "uuid-def",
  "created_at": "2025-10-08T15:00:00Z",
  "title": "Distribute schemas for portability",
  "status": "done",
  "body": "Move schemas to Knowledge/schemas/ and Lists/schemas/",
  "tags": ["architecture", "portability", "P2"],
  "priority": "M",
  "component": "schemas",
  "effort": "30min"
}
```

---

## Troubleshooting

**Issue**: Item won't add to list  
**Solution**: Run `lists-health-check` to validate schema

**Issue**: Can't find items  
**Solution**: Check tags and status filters in search

**Issue**: Duplicate items appearing  
**Solution**: Run `lists-similarity-scanner --dedupe`

**Issue**: Schema validation errors  
**Solution**: Verify required fields (id, created_at, title, status)

---

## Future Enhancements

Tracked in `system-upgrades.jsonl`:
- Cross-list relationships (link items across lists)
- Time-series tracking (visualize item lifecycle)
- Smart reminders (due date notifications)
- List templates (pre-configured schemas for common use cases)
- Web interface (UI for list management)

---

*Last Updated: 2025-10-08*  
*Part of N5 OS - V's Cognitive Operating System*
