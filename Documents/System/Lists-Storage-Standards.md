---
created: 2025-12-24
last_edited: 2025-12-24
version: 1
provenance: con_tD6dy87hIIevo1Zw
---
# Lists Storage Standards

## Overview

This document establishes standards for storing information in the N5 Lists system, defining when to use JSONL-only entries versus hybrid JSONL+markdown references.

**Core Principle:** The `.jsonl` file remains the **Single Source of Truth (SSOT)**. Markdown files are optional extensions for complex content.

---

## Content Classification Matrix

All list entries should be classified into one of three types:

| Type | Definition | JSONL Structure | External File? | Examples |
|------|------------|-----------------|----------------|----------|
| **Atomic** | Self-contained data that lives fully in JSONL fields | `title`, `notes`, `tags`, `status` | ❌ No | Quick reminders, URLs, brief ideas |
| **Reference (Internal)** | Complex content requiring rich formatting, length > 800 chars, or structured layout | Minimal JSONL + `links: [{type: "file", value: "..."}]` | ✅ Yes, markdown | Recipes, procedures, frameworks, research summaries |
| **External** | Third-party content where the original URL should remain canonical | `links: [{type: "url", value: "https://..."}]` | ❌ No (point to external) | Articles, documentation, videos |

---

## Decision Criteria

### Use **Atomic** (JSONL-only) when:
- Content fits within a single `notes` field (~800 characters max)
- No structured formatting is needed (headers, lists, tables, code blocks)
- Entry is a brief reference, status update, or quick capture
- Content is temporary or will be frequently reorganized
- Example: "Remember to call Sarah about the contract on Monday"

### Use **Reference (Internal)** (JSONL + Markdown) when:
- Content exceeds ~800 characters
- Requires structured formatting (headers, lists, tables, code blocks, images)
- Has multiple sections or needs clear organization
- Contains structured data that benefits from markdown syntax
- Entry represents a **durable artifact** (recipe, procedure, framework, summary)
- Entry will be read by humans directly
- Example: Full recipe with ingredients, instructions, notes; procedure guide; research summary

### Use **External** (URL reference) when:
- Content lives on a third-party platform
- The original URL should remain canonical
- You don't control or want to mirror the content
- Link may change or is maintained by external source
- Example: Link to a Notion doc, external article, video

---

## File Location Conventions

### Internal Reference Markdown Files

Markdown files referenced by `links: [{type: "file"}]` should be stored in:

```
Lists/content/<list-slug>/<item-id>-<semantic-name>.md
```

**Components:**
- `<list-slug>`: The list name (e.g., `recipes`, `procedures`)
- `<item-id>`: The JSONL item's UUID for traceability
- `<semantic-name>`: A human-readable, hyphenated name (max 40 chars)

**Examples:**
- `Lists/content/recipes/58bf7a0f-spaghetti-carbonara.md`
- `Lists/content/procedures/a1b2c3d4-onboarding-checklist.md`

### Templates

Template files for specific list types should be stored in:

```
Lists/templates/<list-slug>-template.md
```

**Example:**
- `Lists/templates/recipe-template.md`

---

## YAML Frontmatter Standards

All markdown files referenced by Lists must include YAML frontmatter:

```yaml
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: X.Y
provenance: <conversation-id> or <agent-id>
list_id: <list-slug>
item_id: <item-uuid>
---
```

**Fields:**
- `created`: Creation date (YYYY-MM-DD)
- `last_edited`: Last modification date (YYYY-MM-DD)
- `version`: Version number (starting at 1.0)
- `provenance`: Source (conversation ID or agent ID)
- `list_id`: The parent list slug (e.g., `recipes`)
- `item_id`: The JSONL item's UUID

---

## JSONL Entry Format

### Atomic Entry (No external file)

```json
{
  "id": "58bf7a0f-526f-49cd-a151-95c18e0e75f7",
  "created_at": "2025-12-24T19:30:00Z",
  "updated_at": "2025-12-24T19:30:00Z",
  "title": "Call Sarah about contract",
  "status": "open",
  "tags": ["work", "contracts"],
  "notes": "Remember to call Sarah about the contract on Monday"
}
```

### Reference Entry (Internal markdown)

```json
{
  "id": "58bf7a0f-526f-49cd-a151-95c18e0e75f7",
  "created_at": "2025-12-24T19:30:00Z",
  "updated_at": "2025-12-24T19:30:00Z",
  "title": "Spaghetti Carbonara",
  "status": "active",
  "tags": ["pasta", "italian", "dinner"],
  "notes": "Classic Roman pasta dish with eggs, cheese, and pancetta",
  "links": [
    {
      "type": "file",
      "value": "Lists/content/recipes/58bf7a0f-spaghetti-carbonara.md"
    }
  ]
}
```

### External Entry (URL)

```json
{
  "id": "58bf7a0f-526f-49cd-a151-95c18e0e75f7",
  "created_at": "2025-12-24T19:30:00Z",
  "updated_at": "2025-12-24T19:30:00Z",
  "title": "N5 Lists Policy",
  "status": "reference",
  "tags": ["documentation"],
  "links": [
    {
      "type": "url",
      "value": "https://docs.n5.local/lists/policy"
    }
  ]
}
```

---

## Validation & Orphan Detection

### Validation Script

Run `python3 N5/scripts/n5_lists_validate.py <list-slug>` to:
1. Verify all `links: [{type: "file"}]` entries point to existing files
2. Report orphan markdown files (markdown files with no JSONL reference)
3. Validate JSONL schema compliance

### Preventing Orphans

**When deleting a JSONL entry:**
1. Check if entry has `links: [{type: "file"}]`
2. Delete the referenced markdown file (or move to archive)
3. Then delete the JSONL entry

**When moving a markdown file:**
1. Update the corresponding JSONL entry's `links[*].value`
2. Maintain the `item_id` in the filename for traceability

---

## Interaction with Knowledge System

Lists and Knowledge serve different purposes:

| Aspect | Lists | Knowledge |
|--------|-------|-----------|
| **Purpose** | Tracking, queuing, actionability | Durable wisdom, canon, curated content |
| **Structure** | Flat, status-driven | Hierarchical, thematic |
| **Update Pattern** | Frequent edits, status changes | Rare edits, versioned |
| **Relationship** | Lists may link to Knowledge for deep content | Knowledge may reference Lists for context |

**When to promote from Lists → Knowledge:**
- Entry has proven durable value over time
- Content is canonical (not task-specific)
- Entry has accumulated substantial notes/framework
- You want it surfaced in other contexts (meetings, reflections)

Promote by: copying markdown content to `Personal/Knowledge/` and updating the List entry's `links` to point to the Knowledge file.

---

## Examples

### Example 1: Atomic Task (JSONL-only)
```json
// Lists/ideas.jsonl
{
  "id": "abc123",
  "title": "Test storage hardening",
  "status": "open",
  "notes": "Add encryption at rest for sensitive data"
}
```

### Example 2: Recipe (Hybrid)

**JSONL:**
```json
// Lists/recipes.jsonl
{
  "id": "58bf7a0f-526f-49cd-a151-95c18e0e75f7",
  "title": "Spaghetti Carbonara",
  "status": "active",
  "tags": ["pasta", "italian", "dinner"],
  "notes": "Classic Roman pasta dish",
  "links": [
    {
      "type": "file",
      "value": "Lists/content/recipes/58bf7a0f-spaghetti-carbonara.md"
    }
  ]
}
```

**Markdown:**
```markdown
---
created: 2025-12-24
last_edited: 2025-12-24
version: 1.0
provenance: con_tD6dy87hIIevo1Zw
list_id: recipes
item_id: 58bf7a0f-526f-49cd-a151-95c18e0e75f7
---

# Spaghetti Carbonara

## Ingredients
- 400g spaghetti
- 150g pancetta or guanciale
- 4 egg yolks + 2 whole eggs
- 100g Pecorino Romano, grated
- Black pepper (freshly ground)
- Salt

## Instructions
[...]
```

### Example 3: External Reference

```json
// Lists/ideas.jsonl
{
  "id": "def456",
  "title": "Read about semantic search",
  "status": "backlog",
  "links": [
    {
      "type": "url",
      "value": "https://www.sbert.net/examples/applications/semantic-search.html"
    }
  ]
}
```

---

## Migration Guidance

For existing lists with `links` entries:

1. **Audit:** Run validation script to identify orphans
2. **Classify:** Apply classification matrix to each entry
3. **Standardize:** Rename markdown files to include `item_id`
4. **Frontmatter:** Add YAML frontmatter to all markdown files
5. **Validate:** Run validation script to confirm compliance

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-24 | Initial standards document |

