# CRM Find Command

**Category:** crm  
**Workflow:** automation  
**Script:** `/home/workspace/N5/scripts/crm_query_helper.py`

---

## Purpose

Fast CRM database queries to find people, connections, and relationships.

Database acts as quick index pointing to markdown profiles for full details.

---

## Usage

```bash
python3 N5/scripts/crm_query_helper.py [OPTIONS]
```

---

## Options

### Search by Identity
- `--name NAME` - Find by name (partial match, case-insensitive)
- `--company COMPANY` - Find by organization
- `--email EMAIL` - Find by email address

### Filter by Type
- `--category CATEGORY` - Filter by contact type
  - INVESTOR
  - ADVISOR
  - COMMUNITY
  - NETWORKING
  - OTHER

- `--priority PRIORITY` - Filter by priority level
  - high
  - medium
  - low

### Relationship Queries
- `--touchpoints NAME` - Show interaction history for a person
- `--priority-followups` - Show high-priority contacts needing follow-up
- `--network` - Show contacts grouped by organization
- `--recent` - Show activity in last 30 days

### System Queries
- `--stats` - Get CRM statistics (counts, categories, activity)
- `--limit N` - Limit results to N items (default: 10)

---

## Examples

### Find Someone
```bash
# By name
python3 N5/scripts/crm_query_helper.py --name "Graham"

# By company
python3 N5/scripts/crm_query_helper.py --company "YCB"
```

### Filter by Category
```bash
# All investors
python3 N5/scripts/crm_query_helper.py --category INVESTOR

# High-priority investors
python3 N5/scripts/crm_query_helper.py --category INVESTOR --priority high

# Recent networking contacts
python3 N5/scripts/crm_query_helper.py --category NETWORKING --recent
```

### Network Intelligence
```bash
# Who needs follow-up?
python3 N5/scripts/crm_query_helper.py --priority-followups

# Show network map
python3 N5/scripts/crm_query_helper.py --network

# Interaction history
python3 N5/scripts/crm_query_helper.py --touchpoints "Alex Caveny"
```

### System Info
```bash
# Get statistics
python3 N5/scripts/crm_query_helper.py --stats

# Limited results
python3 N5/scripts/crm_query_helper.py --category ADVISOR --limit 5
```

---

## Output Format

Returns JSON with:
- `full_name` - Person's name
- `company` - Organization
- `title` - Role
- `category` - Contact type
- `priority` - Priority level
- `last_contact_date` - Most recent interaction
- `markdown_path` - **Path to full profile** (source of truth)

---

## Workflow

1. **Query database** (fast index search)
2. **Get markdown path** from results
3. **Open markdown file** for full details

Database provides quick lookup; markdown has complete information.

---

## Data Sources

- **Database:** `file 'Knowledge/crm/crm.db'` (57 profiles indexed)
- **Profiles:** `file 'Knowledge/crm/individuals/'` (57 markdown files)
- **Schema:** `file 'N5/schemas/crm_schema.sql'`

---

## Current Statistics

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

## See Also

- `file 'N5/prefs/operations/crm-usage.md'` - Full CRM usage guide
- `file 'Documents/System/CRM_QUICK_START.md'` - Quick reference
- `file 'Documents/System/CRM_HYBRID_IMPLEMENTATION.md'` - Implementation details

---

*Version 1.0.0 | Created: 2025-10-14*
