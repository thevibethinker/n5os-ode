---
tool: true
description: Generate documentation from lists, schemas, and system data
tags: [automation, documentation, maintenance]
version: 1.0
created: 2025-11-03
---

# Generate Documentation

**Auto-generate documentation from structured data**

Keeps documentation in sync with system data. Converts JSONL lists, schemas, and other structured formats into human-readable markdown.

---

## What It Does

### From Lists → Markdown
Converts JSONL lists into readable markdown:

```jsonl
{"name": "Planning Prompt", "slug": "planning-prompt", "type": "prompt"}
{"name": "Query List", "slug": "query-list", "type": "prompt"}
```

↓

```markdown
# Prompts

## Planning Prompt
**Slug:** planning-prompt  
**Type:** prompt

## Query List  
**Slug:** query-list
**Type:** prompt
```

### From Schemas → Docs
Generates documentation from JSON schemas showing:
- Required fields
- Field types
- Validation rules
- Examples

---

## Usage

### Generate All Documentation

**Tell your AI:**
```
"Generate documentation for all lists"
"Run docgen on my system"
"Update all documentation from data"
```

### Generate Specific List

```
"Generate docs for tools list"
"Update knowledge documentation"
```

### Validate and Generate

```
"Validate and regenerate all docs"
"Check consistency then update docs"
```

---

## What Gets Generated

### List Documentation
- **Input:** `Lists/*.jsonl`
- **Output:** `Lists/*.md`
- **Format:** Readable markdown with metadata

### Schema Documentation
- **Input:** `schemas/*.json`
- **Output:** `system/schema_reference.md`
- **Format:** Field definitions, examples, validation rules

### Index Files
- **Input:** Various system data
- **Output:** `README.md`, indexes, catalogs
- **Format:** Navigable references

---

## Automation

### Manual Generation
Run when you:
- Add items to lists
- Update schemas
- Change system structure

### Scheduled Generation
Set up automated documentation:
```yaml
schedule: Daily at 2 AM
command: generate-docs --all
```

Keeps docs fresh automatically.

---

## Quality Checks

**Before generating:**
1. Validate JSONL format
2. Check required fields
3. Verify no duplicates

**After generating:**
1. Confirm files created
2. Verify content accuracy
3. Check links work

---

## Integration

**Automatically triggered by:**
- `add-to-list` - Regenerates that list's docs
- `query-list` - May refresh index
- System updates - Rebuilds affected docs

**Manually triggered via:**
- "Generate documentation"
- Scheduled tasks
- After bulk data changes

---

## Example Workflow

### After Adding Tools

```
1. Add to lists: "Add this Python tool to my tools list"
2. AI adds entry to Lists/tools.jsonl
3. AI runs: generate-docs for tools
4. Result: Lists/tools.md updated with new entry
```

### After Schema Changes

```
1. Update schemas/prompt.schema.yaml
2. Run: "Generate schema documentation"  
3. Result: system/schema_reference.md includes changes
```

---

## Best Practices

### Keep Data Clean
- Validate before generating
- Fix JSONL errors immediately
- Use consistent formatting

### Generate Often
- After batch updates
- Before committing changes
- During system maintenance

### Review Generated Docs
- Spot check accuracy
- Verify formatting
- Confirm links work

---

## Troubleshooting

**Docs not updating?**
- Check JSONL validity
- Verify file permissions
- Confirm correct list name

**Missing information?**
- Ensure required fields present
- Check schema compliance
- Validate data structure

**Formatting issues?**
- Review JSONL special characters
- Check markdown escaping
- Verify template compatibility

---

## Related

- Prompt: `add-to-list.md` - Triggers doc generation
- Script: `validate_list.py` - Validates before generating
- System: `list_maintenance_protocol.md` - List standards
- Principles: P1 (Human-Readable First)

---

*Structured data → Beautiful docs. Automate documentation.*
