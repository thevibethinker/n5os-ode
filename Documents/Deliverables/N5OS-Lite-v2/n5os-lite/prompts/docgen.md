---
tool: true
description: Generate documentation from structured data (lists, commands, schemas)
tags: [automation, documentation, generation, maintenance]
version: 1.0
created: 2025-11-03
---

# Documentation Generation (Docgen)

Automatically generate human-readable documentation from structured data sources.

**Philosophy:** Data is single source of truth → Generate docs from data → Never manually sync

---

## What It Does

**Generates:**
1. **List views** - Markdown from JSONL lists
2. **Command catalogs** - Reference docs from command registry
3. **Schema documentation** - Human-readable schema guides
4. **Index files** - Navigation and discovery

**Input:** Structured data (JSONL, YAML, JSON)  
**Output:** Markdown documentation  
**When:** On data change, scheduled, or manual trigger

---

## Use Cases

### 1. List Documentation

**Data:** `Lists/tools.jsonl` (structured entries)  
**Generated:** `Lists/tools.md` (human-readable table)

```jsonl
{"name": "Planning Prompt", "type": "prompt", "tags": ["planning"]}
{"name": "Query List", "type": "prompt", "tags": ["lists", "search"]}
```

**Becomes:**

```markdown
# Tools List

## Prompts (2 entries)

| Name | Type | Tags |
|------|------|------|
| Planning Prompt | prompt | planning |
| Query List | prompt | lists, search |
```

### 2. Command Catalog

**Data:** Command registry with metadata  
**Generated:** Command reference documentation

### 3. Schemas

**Data:** JSON Schema files  
**Generated:** Readable field documentation

---

## Usage

**Manual generation:**
```
Tell AI: "Generate documentation from my lists"
or: "Run docgen"
```

**Automated:**
- After adding to list → regenerate that list's docs
- Scheduled (daily/weekly) → keep all docs current
- On git commit → ensure docs match data

---

## Configuration

**What to generate:**
```yaml
# config/docgen.yaml
enabled: true
sources:
  - lists/*.jsonl
  - schemas/*.json
  - config/*.yaml

outputs:
  lists: Lists/*.md
  schemas: system/schema_docs/*.md

schedule: daily
```

---

## Integration Points

**Triggered by:**
- `add-to-list.md` → regenerates list docs
- `query-list.md` → ensures fresh view
- Scheduled tasks → keeps everything current

**Uses:**
- List schemas → validates structure
- Templates → consistent formatting
- Metadata → enriches documentation

---

## Example: Tools List

**Before (JSONL only):**
```jsonl
{"name": "Planning Prompt", "slug": "planning-prompt", "type": "prompt", "description": "Think→Plan→Execute framework", "tags": ["planning", "architecture"], "created": "2025-11-03"}
```

**After (JSONL + Generated MD):**
```markdown
# Tools

**Last Updated:** 2025-11-03  
**Total Entries:** 1

## By Type

### Prompts (1)
- **Planning Prompt** - Think→Plan→Execute framework
  - Tags: planning, architecture
  - Location: Prompts/planning_prompt.md
```

**Benefit:** Humans read MD, machines use JSONL, stays in sync automatically.

---

## Quality Checks

**Docgen validates:**
- JSONL structure (schema compliance)
- Required fields present
- No duplicate entries
- Valid tags (lowercase, no spaces)
- File references exist

**Reports:**
- Warnings for missing optional fields
- Errors for schema violations
- Summary of what was generated

---

## Best Practices

**Do:**
- Keep JSONL as source of truth
- Generate docs, don't manually edit generated files
- Include "auto-generated, do not edit" header
- Schedule regeneration

**Don't:**
- Edit generated markdown directly (gets overwritten)
- Forget to regenerate after data changes
- Skip validation step

---

## Troubleshooting

**Docs out of sync:**
```
Run: "regenerate documentation"
Check: Was JSONL updated but doc not regenerated?
Fix: Run docgen manually or check scheduler
```

**Generation fails:**
```
Check: JSONL valid? (run validator)
Check: Schema matches data structure?
Check: File permissions for output directory?
```

**Missing entries in generated doc:**
```
Check: Entry in JSONL? (might be archived/hidden)
Check: Filter criteria? (status=active only?)
Check: Valid schema? (invalid entries skipped)
```

---

## Related

- Prompts: `add-to-list.md` - Triggers docgen after add
- Prompts: `query-list.md` - Uses generated docs for search
- Scripts: `validate_list.py` - Validates before generation
- System: `list_maintenance_protocol.md` - List management

---

*Data is truth. Docs are views. Generate, don't duplicate.*
