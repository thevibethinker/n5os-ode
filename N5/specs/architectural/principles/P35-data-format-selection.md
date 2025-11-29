# P35: Data Format Selection

**Category:** Architecture  
**Priority:** High  
**Related:** P1 (Human-Readable), P22 (Language Selection), P32 (Simple Over Easy)

---

## Principle

**Choose data formats based on usage pattern, not familiarity. Human-authored text → YAML. Machine-generated streams → JSONL. Queryable data → SQLite.**

Match format to access pattern:
- **YAML**: Multi-line text, human-edited, configuration
- **JSONL**: Append-only logs, streaming, atomic writes
- **SQLite**: Transactional, queryable, relational
- **JSON**: Avoid for human-authored content (use YAML instead)

---

## The Problem

**JSON for everything** seems universal but creates pain:



**Problems:**
- Escaped newlines () break readability
- No native multi-line support
- Editing prose with JSON syntax is hostile
- Humans must manage quotes, escapes, commas

---

## Simple Solution

**Match format to who/what writes it:**

### YAML for Human-Authored Content



**Why:**
- Native multi-line (no escaping)
- Comments supported
- More readable for prose-heavy content
- Easier to edit, diff, review

### JSONL for Machine-Generated Streams



**Why:**
- Stream processing (line-by-line)
- Atomic appends (no file locks)
- Fast parsing
- Append-only architecture

### SQLite for Queryable Data



**Why:**
- Transactions (ACID)
- Complex queries
- Indexing
- Schema enforcement

---

## Decision Matrix

| Use Case | Format | Reason |
|----------|--------|--------|
| Persona prompts | YAML | Human-authored, multi-line, edited frequently |
| System prompts | YAML | Prose-heavy, human-maintained |
| Lists | JSONL → SQLite | Append-only migrating to queryable |
| Logs | JSONL | Streaming, append-only |
| Schemas | JSON | Machine-consumed structures |
| Config | YAML | Human-edited, multi-line |
| API interchange | JSON | Universal, language-agnostic |

---


## Workflows

### Editing Personas

**Files:** Documents/System/personas/*.yaml

**Process:**
1. Edit YAML file directly (native multi-line, clean syntax)
2. Copy entire YAML content
3. Update persona in Zo system via edit_persona tool with YAML as prompt field

**Why YAML:** Personas are prose-heavy, human-edited frequently. YAML provides clean multi-line handling without escape characters.

**Note:** Zo prompt field accepts any text format. YAML goes in directly - no conversion needed.


---

## Anti-Patterns

**❌ JSON for prose:** Requires escaping, hostile to humans  
**✅ YAML for prose:** Natural multi-line

**❌ YAML for logs:** Can't stream, can't append safely  
**✅ JSONL for logs:** Stream-friendly, atomic

---

## Trade-offs

**YAML strengths:**
- Human readability for multi-line text
- Comments supported
- Cleaner diffs

**YAML weaknesses:**
- Whitespace-sensitive
- Multiple representations (need conventions)
- Slightly slower parsing

**Decision:** For human-authored, text-heavy content, readability wins.

---

## References

- P1 (Human-Readable): "Optimize for human comprehension"
- P22 (Language Selection): Match tool to task
- P32 (Simple Over Easy): One format per use case

---

**Status:** Active  
**Updated:** 2025-10-31  
**Version:** 1.0
