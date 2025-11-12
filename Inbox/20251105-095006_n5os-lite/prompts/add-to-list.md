---
tool: true
description: Add structured entries to JSONL lists with validation and deduplication
tags: [lists, workflow, data-management]
version: 1.0
created: 2025-11-03
---

# Add to List

Add structured entries to JSONL lists with proper validation, deduplication, and Single Source of Truth maintenance.

## Instructions

**You are adding entries to a structured list. Follow this protocol:**

### 1. Identify Target List

**Ask if ambiguous:**
- Which list? (e.g., `Lists/tools.jsonl`, `Lists/people.jsonl`)
- What category/domain?

**Common lists:**
- `tools.jsonl` - Software tools and utilities
- `resources.jsonl` - Learning resources, articles, references
- `contacts.jsonl` - People and organizations
- `ideas.jsonl` - Ideas, concepts, opportunities
- `projects.jsonl` - Projects and initiatives

### 2. Validate Entry Structure

**Required fields (all lists):**
- `name` - Primary identifier (string)
- `created` - ISO date (YYYY-MM-DD)
- `updated` - ISO date (YYYY-MM-DD)

**Optional common fields:**
- `description` - Brief explanation
- `tags` - Array of strings (lowercase, no spaces)
- `url` - Reference link if applicable
- `status` - Current state (active, archived, etc.)
- `category` - Organizational grouping

**List-specific fields:**
Add fields relevant to the list type (e.g., `email` for contacts, `priority` for projects)

### 3. Check for Duplicates

**Before adding:**
1. Search existing list for similar entries
2. Check by name, URL, or key identifiers
3. If duplicate found:
   - **Update existing** entry instead of creating new
   - Merge new information with existing
   - Update `updated` field to current date

### 4. Format Entry

**JSONL format (one line per entry):**
```jsonl
{"name": "Example Tool", "description": "Does X", "tags": ["automation", "cli"], "url": "https://example.com", "created": "2025-11-03", "updated": "2025-11-03"}
```

**Validation rules:**
- Valid JSON on single line
- All strings properly escaped
- No trailing commas
- ISO dates (YYYY-MM-DD)
- Lowercase tags with hyphens, no spaces

### 5. Add to List

**Process:**
1. Read existing list file
2. Append new entry on new line
3. Sort by name (optional, depends on list)
4. Verify valid JSONL format
5. Report success with entry count

### 6. Report

**Format:**
```
✅ Added to Lists/{filename}

Entry: {name}
- Description: {description}
- Tags: {tags}
- [Other key fields]

Total entries: {count}
```

## Examples

### Example 1: Adding a Tool

**Input:**
> Add ripgrep to my tools list. It's a fast grep alternative written in Rust.

**Output:**
```jsonl
{"name": "ripgrep", "description": "Fast grep alternative written in Rust, optimized for code searching", "tags": ["cli", "search", "rust"], "url": "https://github.com/BurntSushi/ripgrep", "created": "2025-11-03", "updated": "2025-11-03", "category": "development"}
```

**Report:**
```
✅ Added to Lists/tools.jsonl

Entry: ripgrep
- Description: Fast grep alternative written in Rust, optimized for code searching
- Tags: cli, search, rust
- URL: https://github.com/BurntSushi/ripgrep

Total entries: 47
```

### Example 2: Duplicate Detection

**Input:**
> Add Docker to my tools list.

**Process:**
1. Search `tools.jsonl` for "docker"
2. Found existing entry from 2024-10-15
3. Merge any new information
4. Update `updated` field

**Report:**
```
ℹ️ Entry already exists in Lists/tools.jsonl

Updated: Docker
- Last updated: 2024-10-15 → 2025-11-03
- No new information to merge

Total entries: 47 (unchanged)
```

## Anti-Patterns

**❌ Skip duplicate check**
Creates redundant entries, violates P2 (SSOT)

**❌ Add with invalid JSON**
Breaks list parsing

**❌ Inconsistent field names**
Use `description` not `desc`, `url` not `link`

**❌ Malformed tags**
Tags should be lowercase, hyphenated: `machine-learning` not `Machine Learning`

**❌ Missing timestamps**
Always include `created` and `updated`

## Quality Checks

Before completing:
- [ ] Entry is valid JSON
- [ ] No duplicates exist
- [ ] Required fields present
- [ ] Tags formatted correctly
- [ ] Timestamps are ISO dates
- [ ] List file still valid JSONL after addition

## Related

- System: `list_maintenance_protocol.md`
- Principles: P2 (Single Source of Truth)
- Principles: P1 (Human-Readable First)
- Prompt: `query-list.md`

---

**Maintain lists as canonical knowledge sources.**
