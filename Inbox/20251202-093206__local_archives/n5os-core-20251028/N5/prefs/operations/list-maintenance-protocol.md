---
date: '2025-10-15T21:26:00Z'
category: operations
priority: high
tags: [lists, ssot, maintenance, workflow]
---

# List Maintenance Protocol

**Purpose:** Enforce Single Source of Truth (SSOT) for all list files in the system

**Version:** 1.0.0

**Last Updated:** 2025-10-15

---

## Core Principle

**JSONL is the ONLY source of truth for lists.**

Markdown files (`.md`) are **ephemeral views** generated on-demand, never maintained as dual-write.

---

## File Structure

```
/home/workspace/Lists/
├── {list-name}.jsonl          # SSOT - always maintained
├── index.jsonl                 # Registry of all lists
└── README.md                   # Documentation only
```

**Do NOT maintain:**
- `{list-name}.md` files (generate on-demand only)
- Any dual-write sync mechanisms

---

## List Operations

### Creating a New List

```bash
# Use the lists-create command
n5 lists-create {list-name}

# This creates:
# - Lists/{list-name}.jsonl (empty)
# - Entry in Lists/index.jsonl
```

**Do NOT:** Create `.md` files manually

---

### Adding Items to a List

```bash
# Use lists-add command
n5 lists-add {list-name} "Item description"

# Or append directly to JSONL
echo '{"id": "...", "title": "...", ...}' >> Lists/{list-name}.jsonl
```

**Do NOT:** Add items to `.md` files

---

### Viewing a List

```bash
# Option 1: Ask Zo
"Show me {list-name}"

# Option 2: Use list-view command (when implemented)
n5 list-view {list-name}

# Option 3: Read JSONL directly
jq '.' Lists/{list-name}.jsonl
```

**Do NOT:** Maintain `.md` files for viewing

---

### Updating List Items

```bash
# Use lists-set command
n5 lists-set {list-name} {item-id} field=value

# Or use jq for batch updates
jq 'select(.id=="...") | .status="complete"' Lists/{list-name}.jsonl
```

---

### Searching Lists

```bash
# Use lists-find command
n5 lists-find {list-name} query="search term"

# Or use jq/grep
jq 'select(.status=="planned")' Lists/{list-name}.jsonl
```

---

## Migration from Dual-Write

### Detection

```bash
# Find lists with both .md and .jsonl
cd /home/workspace/Lists
for base in $(ls *.md *.jsonl 2>/dev/null | sed 's/\.\(md\|jsonl\)$//' | sort | uniq -d); do
  echo "DUAL: $base"
done
```

### Consolidation Process

For each dual-write list:

1. **Verify JSONL is complete**
   ```bash
   # Check entry count
   wc -l Lists/{list-name}.jsonl
   
   # Validate JSON
   jq '.' Lists/{list-name}.jsonl > /dev/null
   ```

2. **Compare content**
   ```python
   # Extract unique ideas from both files
   # Ensure all .md content is in .jsonl
   ```

3. **Delete .md file**
   ```bash
   rm Lists/{list-name}.md
   ```

4. **Document decision**
   ```bash
   git commit -m "Consolidate {list-name} to SSOT (.jsonl only)"
   ```

---

## JSONL Schema Standards

All list items should follow this base schema:

```json
{
  "id": "20251015-unique-identifier",
  "title": "Item title",
  "summary": "Detailed description",
  "status": "planned|active|complete|declined",
  "created_at": "2025-10-15T21:26:00Z",
  "updated_at": "2025-10-15T21:26:00Z",
  "priority": "H|M|L",
  "tags": ["tag1", "tag2"],
  "category": "category-name"
}
```

**List-specific schemas** may extend this base with additional fields.

---

## Anti-Patterns

❌ **Creating .md files for lists**
- Generate on-demand only

❌ **Dual-write sync scripts**
- Violates P2 (SSOT)
- Adds complexity
- Creates divergence risk

❌ **Editing .md files**
- Changes will be lost
- Not tracked in SSOT

❌ **Assuming .md is up-to-date**
- Only JSONL is authoritative

---

## When to Generate .md Views

**Valid scenarios:**
1. **On-demand viewing** via `list-view` command
2. **Export for external sharing** via `lists-export`
3. **Snapshot for documentation** (save to conversation workspace)

**Invalid scenarios:**
1. ❌ Maintaining .md alongside .jsonl
2. ❌ Editing .md and syncing back
3. ❌ Using .md as source of truth

---

## Architectural Principles Applied

- **P2 (SSOT):** JSONL is single source of truth
- **P5 (Anti-Overwrite):** Safe append-only JSONL operations
- **P8 (Minimal Context):** Generate views only when needed
- **P11 (Failure Modes):** No sync failures possible
- **P20 (Modular):** View generation separate from storage

---

## Command Reference

| Operation | Command | Output |
|-----------|---------|--------|
| Create list | `lists-create` | JSONL file |
| Add item | `lists-add` | Appends to JSONL |
| View list | `list-view` | Temp MD in conversation workspace |
| Find items | `lists-find` | Filtered results |
| Export | `lists-export` | MD or CSV file |
| Update item | `lists-set` | Modifies JSONL entry |
| Move item | `lists-move` | Atomic transfer between lists |

---

## Enforcement

**Pre-commit hook:**
```bash
# Warn if .md files exist for lists with .jsonl
git diff --cached --name-only | grep 'Lists/.*\.md$' && \
  echo "WARNING: Do not commit .md files for lists. Use JSONL only."
```

**Code review checklist:**
- [ ] No new `.md` files in Lists/
- [ ] All list operations target `.jsonl`
- [ ] No dual-write logic introduced

---

## Related Documents

- `file 'N5/commands/list-view.md'` — On-demand view generation
- `file 'N5/commands/lists-docgen.md'` — Batch view generation (legacy)
- `file 'Knowledge/architectural/architectural_principles.md'` — P2 (SSOT)
- `file 'N5/commands/system-design-workflow.md'` — Design process

---

**Status:** Active  
**Applies to:** All lists in `/home/workspace/Lists/`
