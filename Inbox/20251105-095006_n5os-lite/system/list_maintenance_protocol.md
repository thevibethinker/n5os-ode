# List Maintenance Protocol
**Category:** Operations  
**Priority:** High  
**Version:** 1.0  
**Created:** 2025-11-03

---

## Purpose

Lists are structured knowledge collections using JSONL format as single source of truth. This protocol ensures consistency, quality, and maintainability across all lists.

## List Structure

### Storage Format: JSONL (JSON Lines)

Each entry is a single-line JSON object. One entry per line.

```jsonl
{"id": "unique-id", "title": "Entry Title", "category": "category-name", "tags": ["tag1", "tag2"], "created": "2025-11-03", "updated": "2025-11-03"}
{"id": "another-id", "title": "Another Entry", "category": "different-category", "tags": ["tag3"], "created": "2025-11-03", "updated": "2025-11-03"}
```

### Required Fields

- `id` (string): Unique identifier, typically slug format
- `title` (string): Human-readable name
- `created` (string): ISO 8601 date
- `updated` (string): ISO 8601 date

### Optional Fields

- `category` (string): Classification grouping
- `tags` (array): List of relevant tags
- `description` (string): Detailed explanation
- `status` (string): active, archived, deprecated
- Custom fields as needed per list type

## File Organization

```
Lists/
├── resources.jsonl          # Tools, services, references
├── concepts.jsonl           # Ideas, patterns, frameworks
├── contacts.jsonl           # People and organizations
└── projects.jsonl           # Active work initiatives
```

### Naming Conventions

- Lowercase with hyphens: `my-list.jsonl`
- Descriptive, plural names: `resources.jsonl`, not `res.jsonl`
- One list per file
- JSONL extension required

## Operations

### Adding Entries

**Manual:**
```jsonl
{"id": "new-entry", "title": "New Entry", "category": "general", "tags": ["new"], "created": "2025-11-03", "updated": "2025-11-03"}
```

**Via Script:**
```bash
python3 scripts/list_manager.py add --list resources --id "new-tool" --title "New Tool" --category "tools"
```

### Updating Entries

1. Find entry by `id`
2. Modify fields (preserve `id` and `created`)
3. Update `updated` timestamp
4. Replace line in file

### Removing Entries

**Soft Delete (Preferred):**
```jsonl
{"id": "old-entry", "title": "Old Entry", "status": "archived", "archived_date": "2025-11-03", ...}
```

**Hard Delete:**
Remove line from file entirely. Only for duplicate/erroneous entries.

### Querying Lists

**By ID:**
```bash
grep '"id": "specific-id"' Lists/resources.jsonl
```

**By Category:**
```bash
grep '"category": "tools"' Lists/resources.jsonl
```

**By Tag:**
```bash
grep '"tag1"' Lists/resources.jsonl
```

## Quality Standards

### Consistency

- **Field naming:** Consistent across all lists
- **Date format:** ISO 8601 (YYYY-MM-DD)
- **ID format:** Lowercase with hyphens (slug)
- **Tags:** Lowercase, no spaces

### Validation

Before committing changes:
1. **Valid JSON:** Each line parses as JSON object
2. **Required fields:** All entries have id, title, created, updated
3. **Unique IDs:** No duplicate ids within list
4. **Sorted:** Optional but helpful - sort by id or created date

### Validation Script

```bash
python3 scripts/validate_list.py Lists/resources.jsonl
```

Checks:
- JSON validity
- Required fields present
- Unique IDs
- Date format correctness

## Maintenance Workflows

### Weekly Review

1. Check for duplicates
2. Update stale entries
3. Archive completed/obsolete entries
4. Add missing tags for discoverability

### Monthly Audit

1. Validate all lists
2. Consolidate related entries
3. Remove truly obsolete entries (hard delete)
4. Update documentation if structure changed

## Anti-Patterns

### ❌ Markdown Lists as SSOT

**Problem:** Markdown lists alongside JSONL create sync issues  
**Fix:** JSONL only. Generate markdown views from JSONL if needed

### ❌ Manual Duplicates

**Problem:** Same entry in multiple lists  
**Fix:** Choose canonical list, reference by ID from others

### ❌ Untracked Changes

**Problem:** Editing lists without updating timestamps  
**Fix:** Always update `updated` field when modifying

### ❌ Inconsistent Formats

**Problem:** Different field names across lists (e.g., `cat` vs `category`)  
**Fix:** Standardize field names across all lists

## Migration

### From Markdown to JSONL

```bash
# Extract entries from markdown
# Convert to JSONL format
# Validate output
python3 scripts/md_to_jsonl.py input.md output.jsonl --validate
```

### From CSV to JSONL

```bash
# Convert CSV to JSONL
python3 scripts/csv_to_jsonl.py input.csv output.jsonl
```

## Examples

### Resources List Entry

```jsonl
{"id": "example-tool", "title": "Example Tool", "category": "development", "tags": ["cli", "productivity"], "url": "https://example.com", "description": "Command-line tool for X", "created": "2025-11-03", "updated": "2025-11-03", "status": "active"}
```

### Concepts List Entry

```jsonl
{"id": "think-plan-execute", "title": "Think → Plan → Execute", "category": "workflow", "tags": ["planning", "methodology"], "description": "Framework for systematic project execution", "source": "planning_prompt.md", "created": "2025-11-03", "updated": "2025-11-03"}
```

### Projects List Entry

```jsonl
{"id": "n5os-lite", "title": "N5OS Lite", "category": "infrastructure", "tags": ["ai", "automation", "open-source"], "status": "active", "start_date": "2025-11-03", "repo": "github.com/user/n5os-lite", "created": "2025-11-03", "updated": "2025-11-03"}
```

## Related Documents

- Principles: P2 (Single Source of Truth)
- Principles: P1 (Human-Readable First)
- Directory Structure: `system/directory_structure.md`

---

**Status:** Active  
**Applies to:** All lists in `/workspace/Lists/`  
**Last Updated:** 2025-11-03
