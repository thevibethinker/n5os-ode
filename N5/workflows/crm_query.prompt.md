---
title: CRM Query Interface
description: Natural language interface to CRM V3 - your primary way to interact with CRM data
tags: [crm, query, search, interface, tool]
tool: true
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
---

# Mission

Execute natural language CRM queries by routing to appropriate tools (CLI for mechanical, AI for semantic).

**Query:** {{query}}

---

## Decision Tree

**Analyze the query intent and route appropriately:**

### 1. MECHANICAL Operations (Use CLI directly)
- **Stats/Counts:** "How many profiles?", "Show CRM stats"
  - Route: `crm stats`

- **List/Browse:** "Show me investors", "List networking contacts"
  - Route: `crm list --category [CATEGORY] --limit [N]`

- **Exact Search:** Clear email/name provided
  - Route: `crm search --email X` or `crm search --name "X"`

### 2. SEMANTIC Operations (AI Synthesis Required)

- **Relationship Queries:** "Who do I know at Stripe?", "Find people in fintech"
  - **Action:** 
    1. Use `crm search` with company/keywords
    2. Read matching profiles
    3. Synthesize relationship context
    4. Return structured answer

- **Intelligence Synthesis:** "What do I know about John?", "Prep me for call with Sarah"
  - **Action:**
    1. Find profile via `crm search`
    2. Load file `N5/workflows/crm_intel_synthesis.prompt.md`
    3. Execute deep synthesis

- **Complex Filters:** "Show investors I haven't talked to in 30 days"
  - **Action:**
    1. Query database directly with SQL
    2. Read relevant profiles
    3. Apply semantic filters
    4. Return results with context

- **Connection Mapping:** "How am I connected to X?", "Who can intro me to Y?"
  - **Action:**
    1. Find target profile
    2. Analyze mutual connections
    3. Trace intro paths
    4. Suggest warm intro strategy

### 3. CREATION Operations

- **Add Contact:** "Add John from Stripe", "Create profile for sarah@a16z.com"
  - **Action:**
    1. Load file `N5/workflows/crm_add_contact.prompt.md`
    2. Execute structured creation workflow

---

## Execution Protocol

**Step 1: Classify Intent**
- Determine if mechanical (CLI only) or semantic (AI required)
- Identify required data (email, name, company, category, etc.)

**Step 2: Execute**
- **Mechanical:** Call CLI, return formatted output
- **Semantic:** Execute multi-step synthesis, provide context-rich answer

**Step 3: Response Format**
- Be conversational and specific
- Include key facts and actionable intelligence
- Reference profile paths for follow-up
- Suggest next actions when relevant

---

## Examples

**Query:** "Who do I know at Stripe?"

**Action:**
```bash
crm search --company stripe.com
```
Then synthesize: "You have 2 connections at Stripe: [details with relationship context]"

---

**Query:** "Show me investors I met in the last month"

**Action:**
```sql
SELECT * FROM profiles 
WHERE category = 'INVESTOR' 
AND last_contact_at > date('now', '-30 days')
```
Then format with context.

---

**Query:** "What do I know about Alex Caveny?"

**Action:**
```bash
crm search --name "Alex Caveny"
```
Then load file `N5/workflows/crm_intel_synthesis.prompt.md` with profile data.

---

**Query:** "Add Sarah Chen, investor at A16Z, met at TechCrunch"

**Action:**
Load file `N5/workflows/crm_add_contact.prompt.md` with parsed data.

---

## Key Principles

1. **Prefer CLI for speed** - Don't use AI when SQL is faster
2. **Synthesize for context** - Use AI for relationship understanding
3. **Be specific** - Include profile IDs, paths, last contact dates
4. **Suggest actions** - "You should follow up with X" or "Queue enrichment for Y"
5. **Show your work** - Explain what you found and why it matters

---

## Tools Available

- `crm stats` - CRM statistics
- `crm list [--category CAT] [--limit N]` - List profiles
- `crm search --email EMAIL` - Exact email search
- `crm search --name "NAME"` - Name search (fuzzy)
- `crm search --company DOMAIN` - Company search
- `crm intel --email EMAIL` - Intelligence synthesis (calls separate prompt)
- `crm create` - Manual profile creation (via separate prompt)
- Direct SQL queries via `sqlite3 /home/workspace/N5/data/crm_v3.db "QUERY"`
- Profile YAML files at `N5/crm_v3/profiles/`

---

## Output Format

**For simple queries:**
Direct answer with key facts.

**For complex queries:**
```markdown
## [Query Result]

**Summary:** [High-level answer]

**Details:**
- Key fact 1
- Key fact 2
- Key fact 3

**Context:**
[Relationship intelligence]

**Suggested Actions:**
- Action 1
- Action 2

**Profiles:** file 'N5/crm_v3/profiles/...'
```

