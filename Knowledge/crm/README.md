# CRM System - Quick Reference

**Last Updated:** 2025-10-14  
**Status:** Active & Unified

---

## Directory Structure

```
Knowledge/crm/
├── individuals/           # ✅ ACTIVE - All CRM profiles
├── crm.db                # ✅ ACTIVE - SQLite database
├── .archived_profiles_*/ # 📦 BACKUP - Historical archives
└── README.md            # 📖 This file
```

---

## Quick Start

### Adding a New Profile

1. **Create markdown file:**
   ```bash
   touch Knowledge/crm/individuals/firstname-lastname.md
   ```

2. **Use standard template structure:**
   ```markdown
   # Full Name
   
   **Organization:** Company Name
   **Role/Title:** Job Title
   **Location:** City, State/Country
   **Primary Email:** email@domain.com
   **LinkedIn:** https://linkedin.com/in/username
   
   ---
   
   ## Profile Summary
   [Brief description]
   
   ---
   
   ## Interaction History
   ### 2025-10-14
   - [Details]
   ```

3. **Add to database:**
   ```python
   import sqlite3
   conn = sqlite3.connect('Knowledge/crm/crm.db')
   cursor = conn.cursor()
   cursor.execute("""
       INSERT INTO individuals 
       (full_name, email, linkedin_url, company, title, category, status, priority, markdown_path)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
   """, (
       'Full Name',
       'email@domain.com',
       'https://linkedin.com/in/username',
       'Company Name',
       'Job Title',
       'COMMUNITY',  # or FOUNDER, INVESTOR, CUSTOMER, NETWORKING, ADVISOR, PARTNER, OTHER
       'active',     # or prospect, dormant, archived
       'medium',     # or high, low
       'Knowledge/crm/individuals/firstname-lastname.md'
   ))
   conn.commit()
   conn.close()
   ```

### Finding a Profile

**By name:**
```bash
sqlite3 Knowledge/crm/crm.db "SELECT full_name, markdown_path FROM individuals WHERE full_name LIKE '%search%';"
```

**By company:**
```bash
sqlite3 Knowledge/crm/crm.db "SELECT full_name, company, markdown_path FROM individuals WHERE company LIKE '%search%';"
```

**By category:**
```bash
sqlite3 Knowledge/crm/crm.db "SELECT full_name, company, markdown_path FROM individuals WHERE category='INVESTOR';"
```

### Updating a Profile

1. Edit markdown file directly
2. Update database if core fields changed:
   ```bash
   sqlite3 Knowledge/crm/crm.db "UPDATE individuals SET email='new@email.com' WHERE full_name='Full Name';"
   ```

---

## Database Schema

### Table: `individuals`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key (auto-increment) |
| `full_name` | TEXT | Full name (required) |
| `email` | TEXT | Primary email address |
| `linkedin_url` | TEXT | LinkedIn profile URL |
| `company` | TEXT | Current company/organization |
| `title` | TEXT | Job title/role |
| `category` | TEXT | FOUNDER, INVESTOR, CUSTOMER, COMMUNITY, NETWORKING, ADVISOR, PARTNER, OTHER |
| `status` | TEXT | active, prospect, dormant, archived |
| `priority` | TEXT | high, medium, low |
| `tags` | TEXT | JSON array of tags |
| `first_contact_date` | TEXT | ISO date of first contact |
| `last_contact_date` | TEXT | ISO date of last contact |
| `markdown_path` | TEXT | Path to markdown file (UNIQUE, SSOT) |
| `created_at` | TIMESTAMP | Auto-generated |
| `updated_at` | TIMESTAMP | Auto-updated on changes |

### Indexes

- `idx_individuals_name` on `full_name`
- `idx_individuals_company` on `company`
- `idx_individuals_category` on `category`
- `idx_individuals_status` on `status`
- `idx_individuals_priority` on `priority`
- `idx_individuals_last_contact` on `last_contact_date`

---

## Categories

| Category | Use For |
|----------|---------|
| **FOUNDER** | Company founders, entrepreneurs |
| **INVESTOR** | VCs, angels, investment professionals |
| **CUSTOMER** | Current or potential customers |
| **COMMUNITY** | Community members, ecosystem participants |
| **NETWORKING** | General networking contacts |
| **ADVISOR** | Advisors, mentors, consultants |
| **PARTNER** | Business partners, strategic alliances |
| **OTHER** | Miscellaneous contacts |

---

## Common Queries

### Active high-priority contacts
```sql
SELECT full_name, company, category, last_contact_date 
FROM individuals 
WHERE status='active' AND priority='high'
ORDER BY last_contact_date DESC;
```

### Investors by recent contact
```sql
SELECT full_name, company, last_contact_date 
FROM individuals 
WHERE category='INVESTOR' AND status='active'
ORDER BY last_contact_date DESC;
```

### Contacts needing follow-up (no contact in 30+ days)
```sql
SELECT full_name, company, category, last_contact_date,
       CAST((julianday('now') - julianday(last_contact_date)) AS INTEGER) as days_since_contact
FROM individuals 
WHERE status='active' 
  AND last_contact_date IS NOT NULL
  AND julianday('now') - julianday(last_contact_date) > 30
ORDER BY last_contact_date ASC;
```

### Category distribution
```sql
SELECT category, COUNT(*) as count 
FROM individuals 
GROUP BY category 
ORDER BY count DESC;
```

---

## File Naming Convention

Use kebab-case for filenames:
- ✅ `firstname-lastname.md`
- ✅ `firstname-middlename-lastname.md`
- ❌ `FirstName_LastName.md`
- ❌ `first name last name.md`

---

## Integration Points

### Meeting Prep Digests
- `N5/digests/daily-meeting-prep-*.md` references profiles
- Path pattern: `file 'Knowledge/crm/individuals/name.md'`

### Stakeholder Discovery
- `Records/stakeholder_discovery/*.jsonl` feeds into CRM
- Use for initial capture, then promote to CRM

### Tags & Categorization
- See: `file N5/config/tag_mapping.json`
- Lead type tags (LD-*) map to categories

---

## Maintenance

### Backup Strategy
- Automated backups via consolidation scripts
- Archives stored in `.archived_profiles_YYYYMMDD/`
- Keep for 30 days, then archive

### Data Quality Checks
Run periodically:
```bash
# Check for orphaned database records (no file)
python3 -c "
import sqlite3
from pathlib import Path
conn = sqlite3.connect('Knowledge/crm/crm.db')
cursor = conn.cursor()
cursor.execute('SELECT full_name, markdown_path FROM individuals')
for name, path in cursor.fetchall():
    if not Path(path).exists():
        print(f'MISSING: {name} -> {path}')
conn.close()
"

# Check for orphaned files (no database record)
python3 -c "
import sqlite3
from pathlib import Path
conn = sqlite3.connect('Knowledge/crm/crm.db')
cursor = conn.cursor()
cursor.execute('SELECT markdown_path FROM individuals')
db_paths = {p for (p,) in cursor.fetchall()}
file_paths = {f'Knowledge/crm/individuals/{f.name}' for f in Path('Knowledge/crm/individuals').glob('*.md')}
orphans = file_paths - db_paths
for o in orphans:
    print(f'ORPHAN: {o}')
conn.close()
"
```

---

## Historical Notes

### 2025-10-14: Consolidation Complete
- Unified from `profiles/` → `individuals/`
- 57 records migrated successfully
- Full documentation: `file N5/logs/CRM_CONSOLIDATION_FINAL_SUMMARY.md`

---

## Support

**For Issues:**
- Report: Bottom of left sidebar → "Report an issue"
- Discord: https://discord.gg/zocomputer

**Related Documentation:**
- Status Report: `file Documents/CRM_Consolidation_Status_Report.md`
- Final Summary: `file N5/logs/CRM_CONSOLIDATION_FINAL_SUMMARY.md`
- Thread Archive: `file N5/logs/threads/2025-10-14-1143_Meeting-Prep-Digest-V2-Phase-3-Complete_OIVq/`

---

*Quick Reference v1.0 | 2025-10-14*
