# CRM SQLite Database Setup

## Overview

The CRM database provides structured, queryable storage for individual contacts while maintaining rich context in markdown files. This hybrid approach gives you:

- **SQL queries** for filtering, aggregation, and reporting
- **Markdown files** for detailed notes, meeting transcripts, and context
- **Bidirectional links** between database records and markdown files

## Architecture

```
Knowledge/crm/
├── crm.db                      # SQLite database
├── individuals/                # Markdown files (one per person)
│   ├── jane-smith.md
│   └── alex-caveny.md
├── events/                     # Event logs (existing)
└── follow-ups/                 # Follow-up templates (existing)
```

## Database Schema

### Tables

**individuals** - Core contact information
- Basic info: name, title, company
- Contact details: email, phone, LinkedIn, Twitter
- Classification: category, status, tags
- Relationships: referrer_id, source_type
- Links: markdown_file_path
- Timestamps: created_at, updated_at, last_interaction_date

**interactions** - Interaction history
- Links to individual
- Type: meeting, email, call, linkedin, event
- Date, subject, summary
- Optional link to detailed notes (markdown)

**relationships** - Person-to-person connections
- Bidirectional relationships (mutual acquaintances, referrals, colleagues)
- Notes on relationship context

### Views

**active_prospects** - Quick view of active prospects with last contact date

**stale_contacts** - Contacts with no interaction in 90+ days

## Setup

### 1. Run Migration Script

```bash
cd /home/workspace
python N5/scripts/migrate_crm_to_sqlite.py
```

Options:
1. Migrate existing markdown files
2. Create sample data for testing  
3. Both (recommended for first run)
4. Skip (empty database)

### 2. Verify Database

```bash
sqlite3 Knowledge/crm/crm.db

# List tables
.tables

# View schema
.schema individuals

# Sample query
SELECT full_name, company, primary_category FROM individuals;

# Exit
.quit
```

### 3. Use Query Helper

```bash
# List all active prospects
python N5/scripts/crm_query.py list --category=prospect --status=active

# Search by name/company
python N5/scripts/crm_query.py search "Alex"

# Show stale contacts
python N5/scripts/crm_query.py stale --days=90

# Add new individual
python N5/scripts/crm_query.py add "John Doe" \\
    --company="Acme" \\
    --title="CTO" \\
    --email="john@acme.com" \\
    --category=prospect \\
    --tags="saas,enterprise" \\
    --create-markdown
```

## Data Flow

### Adding New Contact

1. **Script creates DB record** with core data
2. **Script creates/updates markdown** with rich context
3. **Both stay in sync** via markdown_file_path field

### Example Workflow

```python
import sqlite3

conn = sqlite3.connect('Knowledge/crm/crm.db')
cursor = conn.cursor()

# Add individual
cursor.execute("""
    INSERT INTO individuals (full_name, title, company, primary_category, status)
    VALUES (?, ?, ?, ?, ?)
""", ('Jane Smith', 'VP Engineering', 'TechCorp', 'prospect', 'active'))

individual_id = cursor.lastrowid

# Add interaction
cursor.execute("""
    INSERT INTO interactions (individual_id, interaction_type, interaction_date, summary)
    VALUES (?, ?, ?, ?)
""", (individual_id, 'meeting', '2024-01-15', 'Initial discovery call'))

conn.commit()
conn.close()
```

## Categories & Status Values

### Primary Categories
- `prospect` - Potential customer/partner
- `customer` - Active customer
- `channel_partner` - Distribution/partnership
- `investor` - Funding source
- `advisor` - Provides guidance
- `referral_source` - Introduces others  
- `community` - Network/ecosystem
- `other`

### Status Values
- `active` - Currently engaged
- `prospect` - In pipeline
- `dormant` - Temporarily inactive
- `archived` - No longer relevant

## Migration Strategy: Merge vs. Transfer

### Option A: Merge (Recommended Initially)
- Keep both SQLite DB and markdown files
- DB for queries, markdown for rich context
- Update both when data changes
- Gradual transition

**Pros:** No data loss, gradual adoption, best of both worlds
**Cons:** Need to maintain sync

### Option B: Full Transfer
- Migrate all markdown to SQLite
- Archive markdown files
- Use DB as single source of truth
- Generate markdown from DB when needed

**Pros:** Single source of truth, simpler
**Cons:** Lose rich context unless stored in `notes` field

## Recommendation: Merge Strategy

Start with **merge** approach:
1. SQLite stores queryable fields
2. Markdown stores rich context, notes, transcripts
3. Link them via `markdown_file_path` field
4. Update both when creating/editing contacts

After 2-3 months, evaluate whether to consolidate.

## Sample Queries

```sql
-- Active prospects at Series A companies
SELECT full_name, company, title
FROM individuals
WHERE primary_category = 'prospect'
  AND status = 'active'
  AND tags LIKE '%series_a%';

-- Advisors who are also referral sources
SELECT full_name, company, tags
FROM individuals  
WHERE primary_category IN ('advisor', 'referral_source')
  AND status = 'active';

-- Contacts with no interactions in 90 days
SELECT * FROM stale_contacts;

-- Interaction history for specific person
SELECT int.interaction_date, int.interaction_type, int.summary
FROM interactions int
JOIN individuals i ON int.individual_id = i.id
WHERE i.full_name = 'Jane Smith'
ORDER BY int.interaction_date DESC;

-- Referral network
SELECT 
    i1.full_name as person,
    i2.full_name as referred_by
FROM individuals i1
LEFT JOIN individuals i2 ON i1.referrer_id = i2.id
WHERE i1.referrer_id IS NOT NULL;
```

## Integration with Existing Scripts

Update `n5_networking_event_process.py` to:
1. Create/update DB records when processing events
2. Still create markdown files for detailed notes
3. Cross-reference DB ID in markdown frontmatter

## Future Enhancements

- Organizations table (when ready)
- Deal tracking
- Email integration (auto-log interactions)
- Calendar integration
- Export to external CRM (HubSpot, Salesforce)

## Questions to Resolve

1. **Sync strategy:** Update both DB and markdown, or DB-first with markdown generation?
2. **Primary key:** Auto-increment ID or use email/LinkedIn as natural key?
3. **Tags:** Comma-separated in text field or separate tags table?
4. **Existing data:** Migrate all existing markdown or start fresh?

---

**Status:** Experimental — test with sample data before full migration
**Next:** Run migration script, test queries, update Python scripts
