# Worker 2: Migration Scripts

**Orchestrator:** con_RxzhtBdWYFsbQueb  
**Task ID:** W2-MIGRATION  
**Estimated Time:** 45 minutes  
**Dependencies:** Worker 1 ✅ Complete

---

## Mission

Create migration scripts to consolidate 3 existing CRM systems into the unified CRM V3 database with entity deduplication, conflict resolution, and rollback capability.

---

## Context

**Worker 1 Status:** ✅ Complete - Database validated with all tables, indexes, and foreign keys working correctly.

**Source Systems to Migrate:**
1. **Knowledge/crm/** (57 profiles) - Primary CRM with SQLite + markdown
2. **N5/stakeholders/** (10 profiles) - Enriched stakeholder profiles
3. **N5/data/profiles.db** (44 records) - Meeting-centric profiles

**Migration Challenges:**
- **Entity deduplication:** Same person may exist in multiple systems
- **Data quality variance:** Different enrichment levels across systems
- **Conflict resolution:** Contradictory data between sources
- **Relationship preservation:** Must maintain connections

---

## Validation Evidence from Worker 1

✅ **Database exists:** `/home/workspace/N5/data/crm_v3.db`  
✅ **All 5 tables created:** profiles, enrichment_queue, calendar_events, event_attendees, intelligence_sources  
✅ **19 indexes created:** All performance optimization indexes in place  
✅ **Foreign keys working:** CASCADE deletes tested successfully  
✅ **Insert/query operations:** Sample data validated

---

## Deliverables

### 1. Main Migration Script
**File:** `/home/workspace/N5/scripts/crm_migrate_to_v3.py`

**Requirements:**
- Read from all 3 source systems
- Deduplicate by email (canonical identifier)
- Merge intelligence from multiple sources
- Create YAML profiles in correct location
- Insert database records with proper metadata
- Dry-run mode (no actual writes)
- Rollback capability
- Progress logging

**CLI Interface:**
```bash
python3 /home/workspace/N5/scripts/crm_migrate_to_v3.py --dry-run
python3 /home/workspace/N5/scripts/crm_migrate_to_v3.py --execute
python3 /home/workspace/N5/scripts/crm_migrate_to_v3.py --validate
python3 /home/workspace/N5/scripts/crm_migrate_to_v3.py --rollback
```

### 2. Entity Deduplication Logic
**File:** `/home/workspace/N5/scripts/utils/crm_deduplicator.py`

**Algorithm:**
1. **Primary key:** Email (normalized to lowercase)
2. **Secondary match:** Name similarity (fuzzy match >80%)
3. **Conflict resolution:**
   - Most enriched profile wins base data
   - Intelligence sources merged (all kept)
   - Meeting counts summed
   - Latest contact date used
   - Highest category/relationship_strength preserved

**Example:**
```python
# Source 1: Knowledge/crm/individuals/alex-caveny.md
# Source 2: N5/stakeholders/Alex_Caveny_alex.caveny.md
# Result: Single profile with merged intelligence
```

### 3. YAML Profile Generator
**File:** `/home/workspace/N5/scripts/utils/yaml_profile_generator.py`

**Template Structure:**
```yaml
---
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
source: migration_v3
email: alex.caveny@gmail.com
category: ADVISOR
relationship_strength: strong
---

# Alex Caveny

## Contact Information
- **Email:** alex.caveny@gmail.com
- **LinkedIn:** [Profile URL if available]
- **Organization:** Wisdom Partners

## Professional Context
[Merged data from all sources]

## Relationship Notes
[Merged strategic intelligence]

## Meeting History
[Consolidated from profiles.db + crm.db]
```

**Location Rules:**
- **Path:** `/home/workspace/N5/crm_v3/profiles/{firstname}_{lastname}_{email_prefix}.yaml`
- **Example:** `/home/workspace/N5/crm_v3/profiles/Alex_Caveny_alex.caveny.yaml`
- **Naming:** `{Name}_{Email_Prefix}.yaml` (consistent with existing N5/stakeholders pattern)

### 4. Migration Report
**File:** `/home/workspace/N5/orchestration/crm-v3-unified/MIGRATION_REPORT.md`

**Contents:**
- Total records migrated
- Deduplication statistics (X records → Y unique profiles)
- Conflict resolution decisions
- Data quality breakdown
- Missing/incomplete data warnings
- Validation test results

---

## Source System Schemas

### Source 1: Knowledge/crm/crm.db
```sql
-- individuals table
CREATE TABLE individuals (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    category TEXT,
    linkedin_url TEXT,
    organization TEXT,
    notes TEXT,
    created_at TEXT,
    updated_at TEXT
)

-- Count: 57 records
```

### Source 2: N5/stakeholders/*.md
```
# Markdown files with YAML frontmatter
# Count: 10 files
# Format: Enriched profiles with meeting intelligence
```

### Source 3: N5/data/profiles.db
```sql
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY,
    email TEXT,
    name TEXT,
    category TEXT,
    profile_path TEXT,
    created_at TEXT,
    last_updated TEXT,
    meeting_count INTEGER
)

-- Count: 44 records
```

---

## Migration Logic Flowchart

```
1. Read Source 1 (crm.db individuals) → Extract 57 records
2. Read Source 2 (stakeholders/*.md) → Extract 10 profiles
3. Read Source 3 (profiles.db) → Extract 44 records
   ↓
4. Normalize emails (lowercase, trim)
   ↓
5. Deduplicate by email → Identify unique entities
   ↓
6. For each unique entity:
   a. Merge data from all sources
   b. Resolve conflicts (most enriched wins)
   c. Generate YAML profile
   d. Write to /home/workspace/N5/crm_v3/profiles/
   e. Insert database record
   ↓
7. Validate:
   - Profile count matches unique entity count
   - All YAML files created
   - Database records match files
   - No orphaned data
```

---

## Conflict Resolution Rules

### Rule 1: Name Conflicts
**Scenario:** Different name spellings  
**Resolution:** Longest/most complete name wins  
**Example:** "Alex" vs "Alex Caveny" → "Alex Caveny"

### Rule 2: Category Conflicts
**Scenario:** Different categories assigned  
**Resolution:** Hierarchy: ADVISOR > INVESTOR > COMMUNITY > NETWORKING > OTHER  
**Example:** "COMMUNITY" vs "ADVISOR" → "ADVISOR"

### Rule 3: Missing Data
**Scenario:** Field exists in one source, missing in others  
**Resolution:** Use non-null value  
**Example:** Source 1 has LinkedIn, Source 2 doesn't → Keep LinkedIn

### Rule 4: Intelligence Merging
**Scenario:** Multiple intelligence sources  
**Resolution:** Keep ALL sources, append chronologically  
**Example:** B08 blocks + CRM notes + stakeholder intelligence → All preserved

---

## Dry-Run Mode

**Purpose:** Preview migration without making changes

**Output:**
```
=== CRM V3 Migration Dry-Run ===
Source 1 (crm.db): 57 records
Source 2 (stakeholders): 10 profiles
Source 3 (profiles.db): 44 records
Total: 111 records

Deduplication Analysis:
- Unique emails: 73
- Duplicates found: 38
- Final unique profiles: 73

Conflicts Detected:
- Name conflicts: 5 (auto-resolved)
- Category conflicts: 3 (auto-resolved)
- Missing data: 12 profiles (LinkedIn missing)

Would Create:
- 73 YAML profiles in /home/workspace/N5/crm_v3/profiles/
- 73 database records in crm_v3.db

No changes made (dry-run mode).
Run with --execute to perform migration.
```

---

## Rollback Procedure

**If migration fails or needs reversal:**

1. **Backup exists:** Worker 1 created backups before starting
2. **Delete new data:**
   ```bash
   rm -rf /home/workspace/N5/crm_v3/profiles/
   sqlite3 /home/workspace/N5/data/crm_v3.db "DELETE FROM profiles;"
   ```
3. **Old systems intact:** Knowledge/crm, N5/stakeholders, N5/data/profiles.db untouched
4. **Retry:** Fix issues, re-run migration

---

## Testing Requirements

### Test 1: Deduplication Accuracy
```python
# Given: Same person in 2 sources with different emails
# When: Migration runs
# Then: Single profile created, both emails noted
```

### Test 2: Conflict Resolution
```python
# Given: Source 1 says "COMMUNITY", Source 2 says "ADVISOR"
# When: Migration runs
# Then: Profile has category="ADVISOR" (higher priority)
```

### Test 3: Intelligence Preservation
```python
# Given: Source 1 has CRM notes, Source 2 has B08 blocks
# When: Migration runs
# Then: YAML profile contains both sources
```

### Test 4: Database Integrity
```python
# Given: 73 unique profiles created
# When: Query database
# Then: 73 records in profiles table, all yaml_paths valid
```

### Test 5: Idempotency
```python
# Given: Migration runs twice
# When: Second run executes
# Then: No duplicates created, same 73 profiles
```

---

## Success Criteria

✅ **Dry-run completes** without errors  
✅ **Deduplication logic** tested with known duplicates  
✅ **73 unique profiles** identified (estimated based on 111 total - ~35% overlap)  
✅ **YAML profiles created** in correct format and location  
✅ **Database records inserted** with proper metadata  
✅ **Migration report generated** with statistics  
✅ **Rollback tested** (delete + restore works)  
✅ **Validation passes** (file count == DB count)

---

## Output Files

After completion:
```
/home/workspace/N5/scripts/crm_migrate_to_v3.py
/home/workspace/N5/scripts/utils/crm_deduplicator.py
/home/workspace/N5/scripts/utils/yaml_profile_generator.py
/home/workspace/N5/crm_v3/profiles/*.yaml (73 files)
/home/workspace/N5/orchestration/crm-v3-unified/MIGRATION_REPORT.md
/home/workspace/N5/data/crm_v3.db (populated)
```

---

## Handoff to Orchestrator

**Report:**
1. Migration script created and tested
2. Dry-run output (statistics)
3. Actual migration results (if --execute used)
4. Validation test results
5. Any issues/warnings encountered

**Next Worker:** Worker 3 (Enrichment Worker) can begin after validation passes

---

**Orchestrator Contact:** con_RxzhtBdWYFsbQueb  
**Created:** 2025-11-17 22:30 ET  
**Status:** Ready to Execute  
**Worker 1 Validation:** ✅ Complete

