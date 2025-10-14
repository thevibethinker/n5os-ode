# CRM Usage Preferences

**Version:** 1.0.0  
**Last Updated:** 2025-10-14  
**Purpose:** Define how AI should use CRM when finding people or stakeholders

---

## When to Use CRM

**ALWAYS use CRM database first** when user asks to:
- Find a specific person ("Do I know someone named...")
- Search by company ("Who do I know at...")
- Search by role/category ("Show me investors I've met")
- Find connections ("Who introduced me to...")
- Check contact status ("When did I last talk to...")
- Map network ("Show my connections grouped by...")

---

## CRM Query Priority

### Step 1: Query Database First
```bash
python3 N5/scripts/crm_query_helper.py [options]
```

**Available queries:**
- `--name "Name"` - Find by name (partial match)
- `--company "Company"` - Find by organization
- `--category CATEGORY` - Filter by type (INVESTOR, ADVISOR, COMMUNITY, NETWORKING, OTHER)
- `--priority PRIORITY` - Filter by priority (high, medium, low)
- `--touchpoints "Name"` - Show interaction history
- `--priority-followups` - Show high-priority contacts needing follow-up
- `--network` - Group contacts by organization
- `--recent` - Show activity in last 30 days
- `--stats` - Get CRM statistics

### Step 2: Get Full Details from Markdown
Database returns `markdown_path` → Open that file for complete profile

---

## Query Patterns

### Finding a Specific Person
```bash
# Quick lookup
python3 N5/scripts/crm_query_helper.py --name "Graham"

# Returns markdown path → open for full details
```

### Finding People by Category
```bash
# All investors
python3 N5/scripts/crm_query_helper.py --category INVESTOR

# High-priority investors
python3 N5/scripts/crm_query_helper.py --category INVESTOR --priority high
```

### Finding People by Company
```bash
python3 N5/scripts/crm_query_helper.py --company "YCB"
```

### Network Mapping
```bash
# See connections grouped by organization
python3 N5/scripts/crm_query_helper.py --network

# See who needs follow-up
python3 N5/scripts/crm_query_helper.py --priority-followups
```

### Interaction History
```bash
python3 N5/scripts/crm_query_helper.py --touchpoints "Alex Caveny"
```

---

## Natural Language Queries

When user asks in natural language, translate to CRM queries:

**"Do I know anyone at Cornell?"**
→ `--company "Cornell"` or search markdown content

**"Show me all the investors I met in September"**
→ `--category INVESTOR` + filter by `last_contact_date`

**"Who haven't I contacted recently?"**
→ `--priority-followups` or custom query by date

**"Find that person from the AI meetup"**
→ `--name` search + check `--category NETWORKING`

**"Who introduced me to Graham?"**
→ Check Graham's profile markdown for "source" or "introduced by"

---

## Database Structure

### Individuals Table
- Core contact info (name, email, company, title)
- Category (INVESTOR, ADVISOR, COMMUNITY, NETWORKING, OTHER)
- Priority (high, medium, low)
- Last contact date
- **Markdown path** (source of truth)

### Interactions Table
- Linked to individual
- Type (meeting, email, event, introduction)
- Date, context
- Notes

### Organizations Table
- Company name
- Industry, stage
- Linked individuals

### Relationships Table
- Person-to-person connections
- Relationship type (introduced_by, colleague, etc.)

---

## CRM Statistics (Current)

- **Total Profiles:** 57
- **By Category:**
  - COMMUNITY: 18 (32%)
  - INVESTOR: 15 (26%)
  - ADVISOR: 11 (19%)
  - NETWORKING: 8 (14%)
  - OTHER: 5 (9%)
- **By Priority:**
  - High: 24 (42%)
  - Medium: 33 (58%)
- **Contacted Last 30 Days:** 28 (49%)

---

## Data Sources

**Profiles:** `file 'Knowledge/crm/individuals/'` (57 markdown files)  
**Database:** `file 'Knowledge/crm/crm.db'` (SQLite index)  
**Query Helper:** `file 'N5/scripts/crm_query_helper.py'`  
**Schema:** `file 'N5/schemas/crm_schema.sql'`

---

## Key Principles

1. **Database is index, markdown is source** - Always return markdown path for full details
2. **Query performance** - Database queries are <10ms vs scanning 57 files
3. **Network intelligence** - Database enables relationship mapping that markdown can't do efficiently
4. **Always current** - Dual-write keeps database in sync (Phase 2 implementation pending)

---

## Commands

### Current
- `command 'N5/commands/crm-query.md'` - Legacy query command (needs update)

### Planned (Phase 3)
- `command crm-find` - Smart people finder
- `command crm-connections` - Network mapper
- `command crm-touchpoints` - Interaction history
- `command crm-followup` - Priority follow-ups

---

## See Also

- `file 'Documents/System/CRM_HYBRID_IMPLEMENTATION.md'` - Full implementation details
- `file 'Documents/System/CRM_QUICK_START.md'` - Quick reference guide
- `file 'N5/prefs/prefs.md'` - Main preferences index

---

*Version 1.0.0 | Created: 2025-10-14*
