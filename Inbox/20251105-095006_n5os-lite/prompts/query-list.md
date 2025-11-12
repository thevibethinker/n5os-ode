---
tool: true
description: Search and retrieve information from JSONL lists
tags: [lists, workflow, search, data-retrieval]
version: 1.0
created: 2025-11-03
---

# Query List

Search and retrieve structured information from JSONL lists with filtering, sorting, and formatting.

## Instructions

**You are querying a structured list. Follow this protocol:**

### 1. Identify Query Parameters

**Clarify:**
- **Which list?** (e.g., `Lists/tools.jsonl`, `Lists/resources.jsonl`)
- **What to find?** (name, tag, category, any field)
- **How many results?** (all, top N, specific entry)
- **Output format?** (table, list, full JSON, summary)

### 2. Load and Parse List

**Process:**
1. Read JSONL file
2. Parse each line as JSON object
3. Build searchable collection
4. Report total entries loaded

### 3. Apply Filters

**Common filter types:**

**By name:**
```
Find entries where name contains "docker"
Find exact match for name "PostgreSQL"
```

**By tag:**
```
Find all entries tagged "automation"
Find entries with tags ["cli", "rust"]
```

**By field value:**
```
Find entries where status = "active"
Find entries where priority > 7
```

**By date range:**
```
Find entries created after 2025-01-01
Find entries updated in last 30 days
```

**Combined filters:**
```
Find active projects tagged "ai" created this year
```

### 4. Sort Results

**Common sort criteria:**
- Alphabetical by name
- By date (newest/oldest first)
- By priority/rating (if applicable)
- By relevance (if searching)

### 5. Format Output

**Output formats:**

**Table (default for multiple results):**
```
| Name | Description | Tags | Updated |
|------|-------------|------|---------|
| Tool A | Does X | cli, rust | 2025-11-03 |
| Tool B | Does Y | automation | 2025-10-15 |
```

**List (for simple queries):**
```
Found 3 entries:
1. Tool A (cli, rust) - Does X
2. Tool B (automation) - Does Y
3. Tool C (python) - Does Z
```

**Full JSON (for detailed inspection):**
```json
[
  {"name": "Tool A", "description": "Does X", "tags": ["cli", "rust"], "created": "2025-11-03"},
  {"name": "Tool B", "description": "Does Y", "tags": ["automation"], "created": "2025-10-15"}
]
```

**Summary (for counts/stats):**
```
Total: 47 entries
- By category: development (23), productivity (15), other (9)
- By status: active (42), archived (5)
- Most common tags: cli (18), automation (12), python (9)
```

### 6. Report Results

**Format:**
```
🔍 Query: Lists/{filename}
Filter: {filter_description}
Found: {count} results

{formatted_results}
```

## Examples

### Example 1: Find by Tag

**Input:**
> Show me all CLI tools in my tools list

**Output:**
```
🔍 Query: Lists/tools.jsonl
Filter: tag = "cli"
Found: 18 results

| Name | Description | Tags | Updated |
|------|-------------|------|---------|
| fd | Fast find alternative | cli, rust, search | 2025-10-20 |
| fzf | Fuzzy finder | cli, search | 2025-09-15 |
| ripgrep | Fast grep alternative | cli, rust, search | 2025-11-03 |
... (15 more)
```

### Example 2: Find Specific Entry

**Input:**
> Get full details on PostgreSQL from my tools list

**Output:**
```
🔍 Query: Lists/tools.jsonl
Filter: name = "PostgreSQL"
Found: 1 result

Name: PostgreSQL
Description: Open-source relational database with advanced features
Tags: database, sql, backend
URL: https://www.postgresql.org
Category: database
Status: active
Created: 2024-05-12
Updated: 2025-10-01
Notes: Primary database for production systems
```

### Example 3: Recent Updates

**Input:**
> What have I updated in my resources list in the last week?

**Output:**
```
🔍 Query: Lists/resources.jsonl
Filter: updated >= 2025-10-27
Found: 4 results

1. "Building Effective Agents" (2025-11-03)
   - Tags: ai, agents, architecture
   - https://example.com/agents

2. "Simple Made Easy" - Rich Hickey (2025-11-01)
   - Tags: design, philosophy
   - https://www.infoq.com/presentations/Simple-Made-Easy

3. "The Pragmatic Programmer" (2025-10-28)
   - Tags: books, software-engineering
   - Added: Second edition release

4. "Unix Philosophy" (2025-10-27)
   - Tags: design, unix
   - Reference for system design decisions
```

## Anti-Patterns

**❌ Loading entire list when one entry needed**
Be efficient: search for specific entry

**❌ Unclear filter criteria**
Specify exact field and value to match

**❌ Wrong output format**
Use table for many results, full JSON for single entries

**❌ No result count**
Always report how many matches found

## Quality Checks

Before completing:
- [ ] List file found and parsed successfully
- [ ] Filter criteria applied correctly
- [ ] Results sorted appropriately
- [ ] Output format matches request
- [ ] Result count reported

## Related

- System: `list_maintenance_protocol.md`
- Principles: P2 (Single Source of Truth)
- Prompt: `add-to-list.md`

---

**Lists are your external memory. Query them effectively.**
