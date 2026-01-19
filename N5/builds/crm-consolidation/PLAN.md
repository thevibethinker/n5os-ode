---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
type: build_plan
status: draft
provenance: con_1xhFJwHkZOZPZ38m
---

# Plan: CRM/Deals Database Consolidation

**Objective:** Consolidate three fragmented databases (deals.db, crm_v3.db, Personal/Knowledge/CRM/crm.db) into a single unified database, update all 42+ scripts that reference these databases, and ensure all integration points (blurbs, follow-ups, meeting intel, semantic memory) work with the unified system.

**Trigger:** Audit revealed deal_contacts and CRM individuals tables are completely disconnected, causing duplicate data, missing cross-references, and orphaned tracking files (intro-leads.jsonl).

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

- [x] Should we keep markdown profiles as source of truth or DB? → **DB is authoritative, markdown is human-readable layer**
- [x] Which physical database file to use? → **N5/data/n5_core.db (new unified location)**
- [x] How to handle deal_contacts → people migration? → **Create person_id FK, migrate existing contacts to people table**
- [ ] What to do with crm_v3.db calendar_events table? → **Migrate to n5_core.db, it's valuable**
- [ ] Should organizations be shared between deals and CRM? → **Yes, single organizations table**

---

## Alternatives Considered (Nemawashi)

### Option A: Single Unified Database (SELECTED ✓)
- **Pros:** No sync issues, foreign keys work, simpler queries, one backup
- **Cons:** Larger migration effort upfront
- **Decision:** Selected — sync complexity is already causing bugs

### Option B: Two Databases with Sync Layer
- **Pros:** Conceptual separation, independent evolution
- **Cons:** Sync failures (current problem), duplicate data, complex queries
- **Decision:** Rejected — this is the current broken state

### Option C: Soft Consolidation (Views Only)
- **Pros:** Minimal migration, backward compatible
- **Cons:** Still two sources of truth, queries still complex
- **Decision:** Rejected — doesn't solve the root problem

---

## Trap Doors (Irreversible Decisions)

| Decision | Reversibility | Mitigation |
|----------|--------------|------------|
| Deprecate crm_v3.db | ⚠️ Medium | Keep backup, migration script can reverse |
| Deprecate Personal/Knowledge/CRM/crm.db | ⚠️ Medium | Keep backup, data preserved in n5_core.db |
| Change deal_contacts to use person FK | 🔴 Hard | Extensive testing before cutover |
| Rename DB path constants | ⚠️ Medium | Backward compat aliases during transition |

---

## Checklist

### Phase 1: Schema Design & Database Creation
- ☐ Design unified schema (people, organizations, deals, deal_roles, interactions)
- ☐ Create N5/data/n5_core.db with new schema
- ☐ Create migration scripts for each source database
- ☐ Test: Schema validates, all tables created

### Phase 2: Data Migration
- ☐ Migrate Personal/Knowledge/CRM/crm.db → n5_core.db (people, organizations)
- ☐ Migrate N5/data/crm_v3.db → n5_core.db (profiles → people, calendar_events)
- ☐ Migrate N5/data/deals.db → n5_core.db (deals, deal_contacts → deal_roles)
- ☐ Deduplicate people across sources (email-based matching)
- ☐ Test: Record counts match, no orphaned FKs

### Phase 3: Path Constants & Import Updates
- ☐ Update N5/lib/paths.py with N5_CORE_DB constant
- ☐ Update N5/scripts/crm_paths.py to use unified DB
- ☐ Create backward-compat aliases for transition
- ☐ Test: All imports resolve, paths correct

### Phase 4: Script Updates (CRM Scripts)
- ☐ Update crm_cli.py, crm_lookup.py, crm_query_helper.py
- ☐ Update crm_enrichment_worker.py, crm_gmail_enrichment.py
- ☐ Update meeting_crm_linker.py, meeting_crm_sync.py
- ☐ Update stakeholder scripts (stakeholder_intel.py, auto_create_stakeholder_profiles.py)
- ☐ Test: CRM queries return correct data

### Phase 5: Script Updates (Deal Scripts)
- ☐ Update deal_cli.py, deal_query.py, deal_signal_router.py
- ☐ Update deal_proactive_sensor.py (use people table for contacts)
- ☐ Update broker_detector.py, email_deal_scanner.py
- ☐ Update notion_deal_sync.py, sms_deal_handler.py
- ☐ Test: Deal queries work, Notion sync functional

### Phase 6: Integration Points
- ☐ Update blurb generation (uses CRM profiles)
- ☐ Update follow-up email generator
- ☐ Update warm_intro_generator.py
- ☐ Update morning_digest.py
- ☐ Test: End-to-end flows work

### Phase 7: Cleanup & Deprecation
- ☐ Mark old databases as deprecated
- ☐ Update scheduled agents that reference old DBs
- ☐ Create deprecation notice file in old locations
- ☐ Test: No scripts reference old paths

---

## Phase 1: Schema Design & Database Creation

### Affected Files
- `N5/data/n5_core.db` - CREATE - Unified database
- `N5/scripts/n5_core_schema.py` - CREATE - Schema definition and creation script
- `N5/lib/paths.py` - UPDATE - Add N5_CORE_DB constant

### Changes

**1.1 Unified Schema Design:**

```sql
-- Core People Table (THE source of truth for all humans)
CREATE TABLE people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identity
    full_name TEXT NOT NULL,
    email TEXT UNIQUE,
    linkedin_url TEXT,
    
    -- Professional
    company TEXT,
    title TEXT,
    organization_id INTEGER REFERENCES organizations(id),
    
    -- Categorization
    category TEXT CHECK(category IN (
        'FOUNDER', 'INVESTOR', 'CUSTOMER', 'COMMUNITY',
        'NETWORKING', 'ADVISOR', 'PARTNER', 'OTHER'
    )),
    status TEXT DEFAULT 'active',
    priority TEXT DEFAULT 'medium',
    tags TEXT, -- JSON array
    
    -- Tracking
    first_contact_date TEXT,
    last_contact_date TEXT,
    
    -- Profile linkage
    markdown_path TEXT,
    
    -- Source tracking for migration
    source_db TEXT, -- 'crm', 'crm_v3', 'deals'
    source_id TEXT,
    
    -- Timestamps
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Organizations
CREATE TABLE organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    domain TEXT,
    industry TEXT,
    size TEXT,
    description TEXT,
    linkedin_url TEXT,
    website TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Deals (business opportunities)
CREATE TABLE deals (
    id TEXT PRIMARY KEY,
    deal_type TEXT NOT NULL, -- 'zo_partnership', 'careerspan_acquirer', 'leadership'
    
    -- Entity
    company TEXT NOT NULL,
    organization_id INTEGER REFERENCES organizations(id),
    category TEXT,
    
    -- Pipeline
    pipeline TEXT, -- 'careerspan', 'zo'
    stage TEXT DEFAULT 'identified',
    temperature TEXT DEFAULT 'warm',
    
    -- Key contact (now references people)
    primary_contact_id INTEGER REFERENCES people(id),
    
    -- External sync
    notion_page_id TEXT,
    google_sheet_row INTEGER,
    external_source TEXT,
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Deal Roles (junction: which people are on which deals)
CREATE TABLE deal_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deal_id TEXT NOT NULL REFERENCES deals(id),
    person_id INTEGER NOT NULL REFERENCES people(id),
    
    role TEXT NOT NULL, -- 'primary_contact', 'broker', 'champion', 'decision_maker', 'influencer'
    context TEXT,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(deal_id, person_id, role)
);

-- Interactions (meetings, emails, touchpoints)
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER REFERENCES people(id),
    deal_id TEXT REFERENCES deals(id),
    
    type TEXT NOT NULL, -- 'meeting', 'email', 'call', 'linkedin', 'event'
    direction TEXT, -- 'inbound', 'outbound'
    summary TEXT,
    source_ref TEXT, -- meeting folder path, email message_id, etc.
    
    occurred_at TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Calendar Events (migrated from crm_v3)
CREATE TABLE calendar_events (
    id TEXT PRIMARY KEY,
    google_event_id TEXT UNIQUE,
    title TEXT,
    start_time TEXT,
    end_time TEXT,
    location TEXT,
    description TEXT,
    meeting_folder TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Event Attendees (junction)
CREATE TABLE event_attendees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT REFERENCES calendar_events(id),
    person_id INTEGER REFERENCES people(id),
    email TEXT,
    response_status TEXT,
    is_organizer INTEGER DEFAULT 0,
    UNIQUE(event_id, person_id)
);

-- Pending Approvals (for proactive sensor)
CREATE TABLE pending_approvals (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    name TEXT,
    person_id INTEGER REFERENCES people(id),
    context TEXT,
    source_text TEXT,
    pipeline TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT NOT NULL,
    resolved_at TEXT
);

-- Deal Activities Timeline
CREATE TABLE deal_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deal_id TEXT REFERENCES deals(id),
    activity_type TEXT NOT NULL,
    description TEXT,
    performed_by TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Relationships (person-to-person connections)
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_a_id INTEGER REFERENCES people(id),
    person_b_id INTEGER REFERENCES people(id),
    relationship_type TEXT, -- 'colleague', 'friend', 'former_colleague', 'investor', etc.
    strength TEXT, -- 'strong', 'medium', 'weak'
    notes TEXT,
    discovered_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Sync State (for external sources)
CREATE TABLE sync_state (
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    notion_page_id TEXT,
    last_pull_at TEXT,
    last_push_at TEXT,
    PRIMARY KEY (entity_type, entity_id)
);

-- Indexes
CREATE INDEX idx_people_email ON people(email);
CREATE INDEX idx_people_company ON people(company);
CREATE INDEX idx_people_name ON people(full_name);
CREATE INDEX idx_deals_company ON deals(company);
CREATE INDEX idx_deals_type ON deals(deal_type);
CREATE INDEX idx_deals_stage ON deals(stage);
CREATE INDEX idx_deal_roles_deal ON deal_roles(deal_id);
CREATE INDEX idx_deal_roles_person ON deal_roles(person_id);
CREATE INDEX idx_interactions_person ON interactions(person_id);
CREATE INDEX idx_interactions_deal ON interactions(deal_id);
```

**1.2 Create Schema Script:**
Create `N5/scripts/n5_core_schema.py` that:
- Creates database if not exists
- Applies schema
- Has `--reset` flag for development
- Has `--verify` flag to check schema integrity

### Unit Tests
- `python3 N5/scripts/n5_core_schema.py --verify` returns success
- `sqlite3 N5/data/n5_core.db '.tables'` shows all expected tables
- Foreign key constraints are enforced

---

## Phase 2: Data Migration

### Affected Files
- `N5/scripts/migrate_to_n5_core.py` - CREATE - Migration script
- `N5/data/n5_core.db` - UPDATE - Populated with data

### Changes

**2.1 Migration Script:**
Create comprehensive migration that:

1. **Migrate from Personal/Knowledge/CRM/crm.db:**
   - `individuals` → `people` (192 records)
   - `organizations` → `organizations` (29 records)
   - `relationships` → `relationships`
   - `interactions` → `interactions`

2. **Migrate from N5/data/crm_v3.db:**
   - `profiles` → `people` (dedupe by email, 91 records)
   - `organizations` → `organizations` (dedupe by name, 26 records)
   - `calendar_events` → `calendar_events`
   - `event_attendees` → `event_attendees`

3. **Migrate from N5/data/deals.db:**
   - `deals` → `deals` (99 records)
   - `deal_contacts` → create `people` entries + `deal_roles` junction (33 contacts)
   - `deal_activities` → `deal_activities`
   - `pending_approvals` → `pending_approvals`
   - `sync_state` → `sync_state`

**2.2 Deduplication Strategy:**
- Primary key: email address (case-insensitive)
- Secondary: full_name + company combination
- Merge strategy: keep most complete record, log conflicts

### Unit Tests
- Record counts: people >= max(192, 91) (some dedupe expected)
- All deals have valid primary_contact_id or NULL
- No orphaned deal_roles (all reference valid deal_id and person_id)
- `SELECT COUNT(*) FROM people WHERE source_db IS NULL` = 0

---

## Phase 3: Path Constants & Import Updates

### Affected Files
- `N5/lib/paths.py` - UPDATE - Add N5_CORE_DB, deprecate old paths
- `N5/scripts/crm_paths.py` - UPDATE - Point to unified DB
- `N5/scripts/deal_paths.py` - CREATE - Deal-specific path constants

### Changes

**3.1 Update N5/lib/paths.py:**
```python
# Unified Database (NEW)
N5_CORE_DB = N5_DATA_DIR / "n5_core.db"

# Legacy (DEPRECATED - kept for migration reference)
LEGACY_DEALS_DB = N5_DATA_DIR / "deals.db"
LEGACY_CRM_V3_DB = N5_DATA_DIR / "crm_v3.db"
LEGACY_CRM_DB = WORKSPACE / "Personal/Knowledge/CRM/db/crm.db"
```

**3.2 Update crm_paths.py:**
```python
# Point CRM_DB to unified database
CRM_DB = WORKSPACE / "N5/data/n5_core.db"  # Changed from Personal/Knowledge/CRM/db/crm.db

# Add backward compat
DEALS_DB = CRM_DB  # Same database now
```

### Unit Tests
- `python3 -c "from N5.lib.paths import N5_CORE_DB; print(N5_CORE_DB)"` outputs correct path
- `python3 N5/scripts/crm_paths.py` shows unified paths

---

## Phase 4-6: Script Updates

**See Worker Briefs for detailed per-script changes.**

Scripts are divided into MECE worker assignments below.

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| `n5_core_schema.py` | W1.1 | ✓ |
| `migrate_to_n5_core.py` | W1.1 | ✓ |
| `N5/lib/paths.py` | W1.2 | ✓ |
| `crm_paths.py` | W1.2 | ✓ |
| `crm_cli.py` | W2.1 | ✓ |
| `crm_lookup.py` | W2.1 | ✓ |
| `crm_query_helper.py` | W2.1 | ✓ |
| `crm_enrichment_worker.py` | W2.1 | ✓ |
| `deal_cli.py` | W2.2 | ✓ |
| `deal_query.py` | W2.2 | ✓ |
| `deal_proactive_sensor.py` | W2.2 | ✓ |
| `deal_signal_router.py` | W2.2 | ✓ |
| `broker_detector.py` | W2.2 | ✓ |
| `meeting_crm_linker.py` | W2.3 | ✓ |
| `meeting_crm_sync.py` | W2.3 | ✓ |
| `stakeholder_intel.py` | W2.3 | ✓ |
| `auto_create_stakeholder_profiles.py` | W2.3 | ✓ |
| `warm_intro_generator.py` | W3.1 | ✓ |
| `morning_digest.py` | W3.1 | ✓ |
| `follow-up generators` | W3.1 | ✓ |
| `notion_deal_sync.py` | W3.2 | ✓ |
| `sms_deal_handler.py` | W3.2 | ✓ |
| Cleanup & deprecation | W4.1 | ✓ |

### Token Budget Summary

| Worker | Estimated Files | Est. Tokens | Status |
|--------|-----------------|-------------|--------|
| W1.1 | 2 new scripts | ~6,000 | ✓ |
| W1.2 | 2 path files | ~2,000 | ✓ |
| W2.1 | 4 CRM scripts | ~10,000 | ✓ |
| W2.2 | 5 deal scripts | ~12,000 | ✓ |
| W2.3 | 4 meeting/stakeholder | ~10,000 | ✓ |
| W3.1 | 3 integration scripts | ~8,000 | ✓ |
| W3.2 | 2 sync scripts | ~6,000 | ✓ |
| W4.1 | Cleanup tasks | ~2,000 | ✓ |

### MECE Validation Checklist

- [ ] All scope items assigned to exactly ONE worker (no overlaps)
- [ ] All plan deliverables covered (no gaps)
- [ ] All workers within 40% token budget
- [ ] Wave dependencies are valid (no circular, no same-wave deps)
- [ ] `python3 N5/scripts/mece_validator.py crm-consolidation` passes

---

## Worker Briefs

| Wave | Worker | Title | Brief File | Dependencies |
|------|--------|-------|------------|--------------|
| 1 | W1.1 | Schema & Migration | `workers/W1.1-schema-migration.md` | None |
| 1 | W1.2 | Path Constants | `workers/W1.2-path-constants.md` | None |
| 2 | W2.1 | CRM Script Updates | `workers/W2.1-crm-scripts.md` | W1.1, W1.2 |
| 2 | W2.2 | Deal Script Updates | `workers/W2.2-deal-scripts.md` | W1.1, W1.2 |
| 2 | W2.3 | Meeting/Stakeholder Scripts | `workers/W2.3-meeting-scripts.md` | W1.1, W1.2 |
| 3 | W3.1 | Integration Scripts | `workers/W3.1-integration-scripts.md` | W2.1, W2.2 |
| 3 | W3.2 | Sync & External Scripts | `workers/W3.2-sync-scripts.md` | W2.1, W2.2 |
| 4 | W4.1 | Cleanup & Deprecation | `workers/W4.1-cleanup.md` | W3.1, W3.2 |

---

## Success Criteria

1. **Single Database:** All CRM and deal data in `N5/data/n5_core.db`
2. **No Broken Imports:** All 42+ scripts run without import errors
3. **Data Integrity:** All migrated records accessible, no data loss
4. **Cross-References Work:** Query "all deals involving person X" returns correct results
5. **External Sync:** Notion bidirectional sync still functional
6. **Scheduled Agents:** All CRM/deal agents run without errors for 24h

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Data loss during migration | Backup all DBs before migration, verify counts |
| Script breaks in production | Phase rollout, keep backward compat aliases |
| Notion sync breaks | Test sync in isolation before full cutover |
| Email scanner stops working | Test email_deal_scanner.py with live emails |
| Performance regression | Add indexes, benchmark before/after |

---

## Level Upper Review

*To be completed before finalizing plan.*

### Counterintuitive Suggestions to Consider:
1. Should we keep markdown profiles at all, or go DB-only?
2. Is there value in keeping deals as a separate table vs. just "tagged people"?
3. Should calendar_events live here or in a separate calendar.db?

### Incorporated:
- TBD

### Rejected (with rationale):
- TBD
