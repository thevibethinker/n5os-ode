# Export Spec 003: Documentation Generation System

**System:** Automated Documentation from Structured Data  
**Version:** 3.0 (Production)  
**Maturity:** Battle-tested, 8+ months active use  
**Last Updated:** 2025-10-28

---

## 1. System Overview

### Purpose
Auto-generate human-readable documentation from structured data files (JSONL, schemas). Keep docs synchronized with reality - no manual drift.

### Core Concept
**Single source of truth → multiple views.**  
Data lives in structured files (JSONL). Documentation is a generated artifact, regenerated on demand.

### Key Innovation
Multi-mode generator: recipes catalog, lists markdown views, command documentation - all from one tool.

---

## 2. Architecture

### Data Flow
```
Structured Data (JSONL/JSON)
  ↓
Schema Validation
  ↓
Template Processing
  ↓
Markdown Generation
  ↓
File Write (with validation)
```

### Components

**1. Schema Validator**
- Validates input data against JSON Schema (Draft 2020-12)
- Blocks generation if schema violations detected
- Reports specific validation errors

**2. Data Reader**
- JSONL parser (one JSON object per line)
- JSON file loader for schemas/configs
- Handles missing files gracefully

**3. Template Engine**
- Markdown template system
- Variable interpolation
- Section builders (tables, lists, code blocks)
- Cross-reference link generation

**4. Output Manager**
- Atomic writes (temp file → move)
- Backup existing docs before overwrite
- File permission management
- Output validation

---

## 3. Core Operations

### Mode: Recipes Catalog
**Input:** `Recipes/recipes.jsonl`  
**Output:** Unified recipes catalog markdown

**Transforms:**
- Recipe metadata → searchable catalog
- Tags → browsable categories
- File references → clickable links
- Descriptions → formatted sections

### Mode: Lists Views
**Input:** `N5/lists/*.jsonl`  
**Output:** Per-list markdown views (`.md` companion files)

**Transforms:**
- JSONL items → formatted tables
- Status icons (✓ done, ○ open, ⊙ pinned)
- Priority indicators
- Linked references
- Auto-sorted by status/priority

### Mode: Commands Documentation
**Input:** Command registry JSONL  
**Output:** Unified commands.md reference

**Transforms:**
- Command specs → API documentation
- Input/output schemas → parameter tables
- Examples → code blocks
- Related commands → cross-links

---

## 4. Data Schema

### Recipe Entry Schema
```json
{
  "name": "string (required)",
  "description": "string (multiline)",
  "tags": ["array", "of", "strings"],
  "created_at": "ISO-8601 timestamp",
  "updated_at": "ISO-8601 timestamp",
  "version": "semantic version string"
}
```

### List Item Schema
```json
{
  "id": "unique-id",
  "created_at": "ISO-8601",
  "title": "string",
  "status": "open|pinned|done|archived",
  "priority": "L|M|H or 1-5",
  "tags": ["strings"],
  "body": "optional markdown text",
  "links": [{"type": "file|url|ref", "value": "string"}]
}
```

### Command Entry Schema
```json
{
  "name": "command-name",
  "summary": "one-line description",
  "workflow": "category",
  "inputs": {"param": "type description"},
  "outputs": {"result": "type description"},
  "examples": ["usage examples"],
  "related": ["other-commands"]
}
```

---

## 5. Implementation Patterns

### Validation First
```python
# ALWAYS validate before generating
schema = load_schema("lists.item.schema.json")
validator = Draft202012Validator(schema)

for item in data:
    errors = list(validator.iter_errors(item))
    if errors:
        report_and_block(errors)
```

### Atomic Writes
```python
# Never corrupt existing docs
temp_file = output_path.with_suffix('.tmp')
write(temp_file, content)
backup(output_path, output_path.with_suffix('.bak'))
temp_file.rename(output_path)
```

### Idempotency
Running docgen multiple times with same input = identical output.  
No timestamps in generated docs. Deterministic sorting.

---

## 6. Extension Points

### Custom Formatters
Add new output formats (HTML, PDF) by implementing formatter interface:
```python
class Formatter:
    def format_section(self, title, items): pass
    def format_table(self, headers, rows): pass
    def format_link(self, text, target): pass
```

### Custom Modes
Add new doc types by implementing mode handler:
```python
def generate_custom_mode(input_path, output_path, schema_path):
    data = load_jsonl(input_path)
    validate(data, schema_path)
    markdown = transform(data)
    write_atomic(output_path, markdown)
```

---

## 7. Operational Considerations

### Performance
- Sub-second for <1000 items
- Scales linearly with data size
- Schema validation is dominant cost

### Error Handling
**BLOCK on:**
- Schema validation failures
- Missing required fields
- Malformed JSONL

**WARN on:**
- Missing optional fields
- Broken cross-references
- Deprecated fields

### Automation Integration
- Run on schedule (daily docgen)
- Run on data change (git hook, file watcher)
- Run manually (command invocation)

---

## 8. Related Systems

**Depends On:**
- Schema definitions (JSON Schema files)
- Structured data files (JSONL sources)

**Used By:**
- List system (generates .md views)
- Recipe system (generates catalog)
- Command system (generates reference docs)
- Knowledge base (generates indexes)

**Integrates With:**
- Version control (commit generated docs)
- Search systems (index generated markdown)
- UI rendering (display generated docs)

---

## 9. Quality Standards

### Generated Documentation Must:
- Pass markdown linting
- Contain no broken internal links
- Include generation timestamp footer
- Match source data exactly
- Be git-diff friendly (consistent formatting)

### Validation Gates:
1. Input schema validation
2. Template syntax check
3. Output markdown validation
4. Cross-reference resolution
5. File permission check

---

## 10. Example Implementation

### Minimal Docgen (Python)
```python
#!/usr/bin/env python3
import json
from pathlib import Path
from jsonschema import Draft202012Validator

def generate_list_view(list_jsonl, output_md, schema_path):
    # Load and validate
    schema = json.loads(Path(schema_path).read_text())
    validator = Draft202012Validator(schema)
    
    items = []
    for line in Path(list_jsonl).read_text().splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        errors = list(validator.iter_errors(item))
        if errors:
            raise ValueError(f"Schema errors: {errors}")
        items.append(item)
    
    # Sort: pinned → open → done
    status_order = {"pinned": 0, "open": 1, "done": 2}
    items.sort(key=lambda x: status_order.get(x["status"], 99))
    
    # Generate markdown
    md = [f"# {Path(list_jsonl).stem.replace('-', ' ').title()}\n"]
    md.append("| Status | Title | Priority | Tags |")
    md.append("|--------|-------|----------|------|")
    
    for item in items:
        icon = {"open": "○", "pinned": "⊙", "done": "✓"}.get(item["status"], "?")
        tags = ", ".join(item.get("tags", []))
        pri = item.get("priority", "M")
        md.append(f"| {icon} | {item['title']} | {pri} | {tags} |")
    
    # Atomic write
    temp = Path(output_md).with_suffix('.tmp')
    temp.write_text('\n'.join(md))
    temp.rename(output_md)

# Usage
generate_list_view(
    "N5/lists/ideas.jsonl",
    "N5/lists/ideas.md",
    "N5/schemas/lists.item.schema.json"
)
```

---

## 11. Testing Strategy

### Unit Tests
- Schema validation (valid/invalid inputs)
- JSONL parsing (well-formed, malformed)
- Markdown generation (template correctness)
- Atomic write operations

### Integration Tests
- Full pipeline (JSONL → MD)
- Multiple modes (recipes, lists, commands)
- Error recovery (rollback on failure)

### Acceptance Tests
- Generated docs match expected output
- Cross-references resolve correctly
- No broken links
- Consistent formatting

---

## Implementation Checklist

- [ ] Set up JSON Schema validation
- [ ] Implement JSONL reader
- [ ] Build markdown template engine
- [ ] Implement atomic write operations
- [ ] Create recipes catalog mode
- [ ] Create lists view mode
- [ ] Add error handling and reporting
- [ ] Write unit tests
- [ ] Add CLI interface
- [ ] Document custom extension points
- [ ] Create example schemas
- [ ] Set up automation hooks (optional)

---

*Export specification format v1.0*
