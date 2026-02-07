# Worker 1: Database Schema Creation

**Orchestrator:** con_RxzhtBdWYFsbQueb  
**Task ID:** W1-DB-SCHEMA  
**Estimated Time:** 30 minutes  
**Dependencies:** None

---

## Mission

Create the foundational SQLite database schema for CRM V3 unified system with 5 tables supporting webhook-triggered enrichment, profiles, and intelligence tracking.

---

## Context

This is Worker 1 of 7 in the CRM V3 unified system build. You are creating the foundation database that all other workers depend on.

**Why this matters:**
- 3 legacy CRM systems need migration into a single unified schema
- Database serves as queryable index while YAML files are source of truth
- Must support async enrichment queue, calendar webhooks, email tracking

**Full Architecture:** `file '/home/.z/workspaces/con_RxzhtBdWYFsbQueb/CRM_UNIFIED_ARCHITECTURE_V3_FINAL.md'`

---

## Dependencies

**None** - This is the foundation task.

---

## Deliverables

1. **File:** `/home/workspace/N5/data/crm_v3.db` (SQLite database)
2. **Tables:** 5 tables with proper foreign keys and indexes
3. **Test Results:** Sample data inserts + validation queries
4. **Documentation:** Schema diagram in orchestration folder

---

## Requirements

### Database Location
`/home/workspace/N5/data/crm_v3.db`

### Table Specifications

#### 1. `profiles` Table

```sql
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    yaml_path TEXT NOT NULL UNIQUE,
    
    -- Metadata
    source TEXT NOT NULL,  -- 'calendar', 'email_reply', 'transcript', 'voice_memo', 'manual'
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_enriched_at TEXT,
    last_contact_at TEXT,
    
    -- Classification
    category TEXT,  -- 'ADVISOR', 'INVESTOR', 'COMMUNITY', 'NETWORKING', 'OTHER'
    relationship_strength TEXT,  -- 'strong', 'moderate', 'weak'
    
    -- State
    enrichment_status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'in_progress', 'complete', 'failed'
    profile_quality TEXT NOT NULL DEFAULT 'stub',  -- 'stub', 'basic', 'enriched', 'comprehensive'
    
    -- Stats
    meeting_count INTEGER DEFAULT 0,
    intelligence_block_count INTEGER DEFAULT 0,
    last_intelligence_at TEXT,
    
    -- Search optimization
    search_text TEXT  -- denormalized for FTS, updated by trigger
);

CREATE INDEX idx_profiles_email ON profiles(email);
CREATE INDEX idx_profiles_enrichment_status ON profiles(enrichment_status);
CREATE INDEX idx_profiles_source ON profiles(source);
CREATE INDEX idx_profiles_category ON profiles(category);
```

#### 2. `enrichment_queue` Table

```sql
CREATE TABLE enrichment_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    
    -- Scheduling
    priority INTEGER NOT NULL DEFAULT 50,  -- 0-100, higher = more urgent
    scheduled_for TEXT NOT NULL,  -- ISO8601 datetime
    checkpoint TEXT NOT NULL,  -- 'initial', 'pre_meeting', 'morning_of'
    
    -- State
    status TEXT NOT NULL DEFAULT 'queued',  -- 'queued', 'processing', 'complete', 'failed'
    attempt_count INTEGER DEFAULT 0,
    last_attempt_at TEXT,
    
    -- Context
    trigger_source TEXT NOT NULL,  -- 'calendar_webhook', 'manual', 'email_reply'
    trigger_metadata TEXT,  -- JSON with event_id, meeting_time, etc.
    
    -- Results
    completed_at TEXT,
    error_message TEXT,
    
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_queue_status ON enrichment_queue(status);
CREATE INDEX idx_queue_priority ON enrichment_queue(priority DESC);
CREATE INDEX idx_queue_scheduled ON enrichment_queue(scheduled_for);
CREATE INDEX idx_queue_profile ON enrichment_queue(profile_id);
```

#### 3. `calendar_events` Table

```sql
CREATE TABLE calendar_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,  -- Google Calendar event ID
    
    -- Event details
    summary TEXT NOT NULL,
    start_time TEXT NOT NULL,  -- ISO8601
    end_time TEXT NOT NULL,
    location TEXT,
    
    -- Processing state
    processed_at TEXT,
    attendee_count INTEGER DEFAULT 0,
    
    -- Tracking
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_events_id ON calendar_events(event_id);
CREATE INDEX idx_events_start ON calendar_events(start_time);
```

#### 4. `event_attendees` Table

```sql
CREATE TABLE event_attendees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    profile_id INTEGER NOT NULL,
    
    -- Attendee details
    response_status TEXT,  -- 'accepted', 'declined', 'tentative', 'needsAction'
    is_organizer INTEGER DEFAULT 0,
    
    FOREIGN KEY (event_id) REFERENCES calendar_events(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    
    UNIQUE(event_id, profile_id)
);

CREATE INDEX idx_attendees_event ON event_attendees(event_id);
CREATE INDEX idx_attendees_profile ON event_attendees(profile_id);
```

#### 5. `intelligence_sources` Table

```sql
CREATE TABLE intelligence_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    
    -- Source details
    source_type TEXT NOT NULL,  -- 'b08_block', 'aviato_enrichment', 'gmail_thread', 'linkedin_profile', 'manual_note'
    source_path TEXT,  -- Path to meeting file, email thread ID, etc.
    source_date TEXT NOT NULL,
    
    -- Content summary
    summary TEXT NOT NULL,  -- One-line summary for quick reference
    
    -- Metadata
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_intel_profile ON intelligence_sources(profile_id);
CREATE INDEX idx_intel_type ON intelligence_sources(source_type);
CREATE INDEX idx_intel_date ON intelligence_sources(source_date DESC);
```

---

## Implementation Guide

### Step 1: Create Database File

```python
import sqlite3
from pathlib import Path

DB_PATH = Path("/home/workspace/N5/data/crm_v3.db")

# Ensure directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Create connection
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Enable foreign keys
cursor.execute("PRAGMA foreign_keys = ON")
```

### Step 2: Create Tables

Execute each CREATE TABLE statement in order:
1. profiles
2. enrichment_queue
3. calendar_events
4. event_attendees
5. intelligence_sources

### Step 3: Verify Schema

```python
# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables created: {tables}")

# Verify foreign keys
cursor.execute("PRAGMA foreign_key_list(enrichment_queue)")
fkeys = cursor.fetchall()
print(f"Foreign keys: {fkeys}")
```

### Step 4: Insert Sample Data

```python
# Sample profile
cursor.execute("""
    INSERT INTO profiles (email, name, yaml_path, source, category)
    VALUES ('test@example.com', 'Test Person', 'Profiles/test-person.yaml', 'manual', 'NETWORKING')
""")

profile_id = cursor.lastrowid

# Sample enrichment queue item
cursor.execute("""
    INSERT INTO enrichment_queue (profile_id, priority, scheduled_for, checkpoint, trigger_source)
    VALUES (?, 100, datetime('now', '+2 days'), 'pre_meeting', 'calendar_webhook')
""", (profile_id,))

# Sample calendar event
cursor.execute("""
    INSERT INTO calendar_events (event_id, summary, start_time, end_time)
    VALUES ('evt_test_123', 'Test Meeting', datetime('now', '+3 days'), datetime('now', '+3 days', '+1 hour'))
""")

event_id = cursor.lastrowid

# Link attendee
cursor.execute("""
    INSERT INTO event_attendees (event_id, profile_id, response_status)
    VALUES (?, ?, 'accepted')
""", (event_id, profile_id))

# Sample intelligence source
cursor.execute("""
    INSERT INTO intelligence_sources (profile_id, source_type, source_path, source_date, summary)
    VALUES (?, 'manual_note', '/dev/null', date('now'), 'Test intelligence entry')
""", (profile_id,))

conn.commit()
```

### Step 5: Validation Queries

```python
# Count records
cursor.execute("SELECT COUNT(*) FROM profiles")
print(f"Profiles: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM enrichment_queue")
print(f"Queue items: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM calendar_events")
print(f"Events: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM event_attendees")
print(f"Attendees: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM intelligence_sources")
print(f"Intelligence: {cursor.fetchone()[0]}")

# Test foreign key cascades
cursor.execute("DELETE FROM profiles WHERE email = 'test@example.com'")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM enrichment_queue")
print(f"Queue after cascade delete: {cursor.fetchone()[0]} (should be 0)")
```

---

## Testing

### Test 1: Schema Creation

```bash
sqlite3 /home/workspace/N5/data/crm_v3.db ".schema" | head -50
```

Expected: All 5 tables with proper CREATE statements

### Test 2: Sample Data Inserts

Run the sample data insertion script above.

Expected: No errors, all foreign key relationships work

### Test 3: Cascade Deletes

Delete a profile, verify enrichment_queue, event_attendees, and intelligence_sources cascade.

Expected: Related records deleted automatically

### Test 4: Index Verification

```sql
SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND tbl_name IN ('profiles', 'enrichment_queue', 'calendar_events', 'event_attendees', 'intelligence_sources');
```

Expected: 11+ indexes created

---

## Report Back

When complete, report to orchestrator (con_RxzhtBdWYFsbQueb):

✅ **Deliverable 1:** `/home/workspace/N5/data/crm_v3.db` created  
✅ **Deliverable 2:** All 5 tables created with foreign keys  
✅ **Deliverable 3:** Sample data tests passed  
✅ **Deliverable 4:** Schema documentation created  

**Validation Commands:**
```bash
ls -lh /home/workspace/N5/data/crm_v3.db
sqlite3 /home/workspace/N5/data/crm_v3.db ".tables"
sqlite3 /home/workspace/N5/data/crm_v3.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
```

**Ready for:** Worker 2 (Migration Scripts) to begin

---

**Orchestrator Contact:** con_RxzhtBdWYFsbQueb  
**Created:** 2025-11-17 21:45 ET  
**Status:** Ready to Execute

