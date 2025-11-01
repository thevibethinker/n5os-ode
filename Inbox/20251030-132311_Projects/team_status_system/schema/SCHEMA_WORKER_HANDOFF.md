# W1: Schema Worker Handoff
**Worker ID:** W1-SCHEMA  
**Spawned From:** con_MuvXIR7jXZjZxlND (Build Orchestrator)  
**Priority:** 🔴 BLOCKING (All other workers depend on this)  
**Estimated Time:** 40 minutes

---

## Your Mission

Design and implement the database schema extensions needed to track **team status career progression** on top of the existing productivity tracking system.

You are building the **data foundation** for a career simulator where V's daily performance determines their squad status in an Arsenal FC-themed team hierarchy.

---

## Context: What's the Bigger Picture?

V uses a productivity tracker that calculates a daily "RPI" (Response Productivity Index) based on emails sent vs. expected workload. Currently it tracks:
- Daily RPI scores
- Email counts
- XP/Level/Streak (gamification)

**The Enhancement:** Add a career progression layer where 7-day performance windows determine V's "team status" (Transfer List → Legend). This status changes based on sustained performance, with coaching emails sent at key moments.

**Your role:** Create the database tables to store:
1. Team status history (what status on what date)
2. Career statistics (days in each status, transitions)
3. Email tracking (what alerts sent when)

---

## Current Database State

**File:** `/home/workspace/productivity_tracker.db` (SQLite)

### Existing Tables

**daily_stats** (main performance table)
```sql
CREATE TABLE daily_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT UNIQUE NOT NULL,
    rpi_score REAL,
    email_count INTEGER,
    total_words INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    emails_sent INTEGER DEFAULT 0,
    emails_new INTEGER DEFAULT 0,
    emails_followup INTEGER DEFAULT 0,
    emails_response INTEGER DEFAULT 0,
    expected_emails INTEGER DEFAULT 0,
    rpi REAL DEFAULT 0,
    xp_earned REAL DEFAULT 0,
    xp_multiplier REAL DEFAULT 1,
    level INTEGER DEFAULT 1,
    streak_days INTEGER DEFAULT 0
);
```

**sent_emails** (email records)
```sql
CREATE TABLE sent_emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gmail_id TEXT UNIQUE NOT NULL,
    thread_id TEXT,
    date TEXT,
    subject TEXT,
    word_count INTEGER DEFAULT 0,
    subject_category TEXT,
    era TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**expected_load** (calendar meetings)
```sql
CREATE TABLE expected_load (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    source TEXT NOT NULL,
    type TEXT,
    hours REAL DEFAULT 0,
    title TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, source, type)
);
```

**xp_ledger** (XP transactions)
```sql
CREATE TABLE xp_ledger (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    xp_value REAL NOT NULL,
    source TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Your Task: Schema Extensions

### New Tables to Create

#### 1. **team_status_history**
Tracks V's team status on each date.

**Required Fields:**
- `id` - Primary key
- `date` - Date (YYYY-MM-DD), unique
- `status` - Text enum: 'transfer_list', 'reserves', 'squad_member', 'first_team', 'invincible', 'legend'
- `days_in_status` - Integer (consecutive days at current status)
- `previous_status` - Text (what they moved from, NULL if first entry)
- `top5_avg` - Real (the calculated top 5 of 7 average that determined this status)
- `grace_days_used` - Integer (0-2, how many of the 2 worst days were excluded)
- `promotion_eligible` - Boolean/Integer (1 if has been at level long enough to promote)
- `probation_days_remaining` - Integer (days left in probation period after promotion, 0 if not in probation)
- `created_at` - Timestamp

**Indexes:**
- `date` (for fast lookups)
- `status` (for career stats queries)

#### 2. **status_transitions**
Logs every time V changes status (for career history).

**Required Fields:**
- `id` - Primary key
- `date` - Date of transition
- `from_status` - Text
- `to_status` - Text
- `reason` - Text ('performance', 'unlock_elite', 'probation_end', 'manual_override')
- `top5_avg` - Real (performance metric at time of transition)
- `notes` - Text (optional, for manual overrides)
- `created_at` - Timestamp

**Indexes:**
- `date`
- `to_status` (for counting promotions/demotions)

#### 3. **coaching_emails**
Tracks what alerts have been sent to avoid spam.

**Required Fields:**
- `id` - Primary key
- `date` - Date email was sent
- `email_type` - Text enum: 'demotion', 'promotion', 'warning', 'grace_alert', 'achievement'
- `status_at_time` - Text (V's status when email sent)
- `trigger_context` - Text (what caused the email, e.g., "3 days <90%")
- `sent_via` - Text ('gmail', 'dry_run', 'manual')
- `created_at` - Timestamp

**Indexes:**
- `date`
- `email_type` (for rate limiting queries)

#### 4. **career_stats**
Single-row table tracking lifetime statistics (updated daily).

**Required Fields:**
- `id` - Primary key (always 1, single row)
- `total_game_days` - Integer
- `days_transfer_list` - Integer
- `days_reserves` - Integer
- `days_squad_member` - Integer
- `days_first_team` - Integer
- `days_invincible` - Integer
- `days_legend` - Integer
- `total_promotions` - Integer
- `total_demotions` - Integer
- `elite_unlocks` - Integer (how many times reached Invincible/Legend)
- `longest_streak_first_team` - Integer (consecutive days)
- `longest_streak_invincible` - Integer
- `last_updated` - Date
- `created_at` - Timestamp

---

## Team Status Rules (For Reference)

You don't implement the logic (that's W2's job), but knowing the rules helps design the schema:

### Status Hierarchy
1. 🚫 **Transfer List** - Bottom tier
2. 🟠 **Reserves** - Needs improvement
3. 🟡 **Squad Member** - Probation after promotion
4. 🟢 **First Team Starter** - Expectations met
5. 🌟 **Invincible** - Elite tier (unlock: 6/8 weeks >125% RPI)
6. 🏆 **Legend** - Top tier (sustained Invincible)

### Movement Rules
- **Top 5 of 7:** Take best 5 days out of last 7, average them
- **90% threshold:** Must average ≥90% to maintain/promote
- **Asymmetric:** Easier to climb (3 days above threshold) than fall (5 days below)
- **Probation:** 7-day buffer after promotion before demotion possible
- **Elite unlock:** Requires sustained excellence (6/8 weeks >125%)

---

## Deliverables

### 1. Migration Script
**File:** `/home/.z/workspaces/con_MuvXIR7jXZjZxlND/migration_001_team_status.sql`

Create a complete SQL migration that:
- Creates all 4 new tables
- Creates all indexes
- Includes comments explaining each field
- Is idempotent (can be run multiple times safely)

**Format:**
```sql
-- Migration: Team Status Career Progression
-- Date: 2025-10-30
-- Description: Adds tables for tracking team status, transitions, coaching emails, career stats

-- Drop existing if re-running (for development)
DROP TABLE IF EXISTS team_status_history;
DROP TABLE IF EXISTS status_transitions;
DROP TABLE IF EXISTS coaching_emails;
DROP TABLE IF EXISTS career_stats;

-- Create tables...
CREATE TABLE team_status_history (
    ...
);

-- Create indexes...
CREATE INDEX idx_team_status_date ON team_status_history(date);
...
```

### 2. Test Data Script
**File:** `/home/.z/workspaces/con_MuvXIR7jXZjZxlND/test_data_team_status.sql`

Insert sample data for testing:
- 14 days of status history (showing status changes)
- 3-4 status transitions
- 2-3 coaching emails
- 1 career_stats row with realistic numbers

This allows other workers to test their code immediately.

### 3. Schema Documentation
**File:** `/home/.z/workspaces/con_MuvXIR7jXZjZxlND/SCHEMA_DOCUMENTATION.md`

Document:
- ERD or table relationship diagram (text/ASCII is fine)
- Purpose of each table
- Field descriptions
- Query patterns (how other workers should use these tables)
- Example queries for common operations

**Example sections:**
```markdown
## team_status_history

**Purpose:** Daily record of V's team status

**Key Queries:**
- Get current status: `SELECT * FROM team_status_history ORDER BY date DESC LIMIT 1`
- Get 7-day window: `SELECT * FROM team_status_history WHERE date >= date('now', '-7 days')`
...
```

---

## Success Criteria

- [ ] All 4 tables created with correct schemas
- [ ] All indexes created for performance
- [ ] Migration script runs without errors
- [ ] Migration script is idempotent (safe to re-run)
- [ ] Test data inserted successfully
- [ ] Schema documentation complete
- [ ] No foreign key constraints that would block future extensions
- [ ] Compatible with SQLite 3 (V's current database)

---

## Design Constraints

### Database Extensibility
**Future-proof:** V wants to track LinkedIn messages, other platforms later. Your schema should:
- NOT over-engineer for hypothetical features
- Focus on team status needs NOW
- Use clean, modular design that allows adding parallel tables later

**Good:** Separate `team_status_history` table (one concern)  
**Bad:** Creating `outbound_messages` super-table we don't need yet

### Performance Considerations
- Table will grow by 1 row per day per user (slow growth)
- Queries will be mostly `WHERE date >= X` range scans
- Index on `date` is critical for performance

### SQLite-Specific
- Use `TEXT` for dates (YYYY-MM-DD format)
- Use `INTEGER` for booleans (0/1)
- Use `REAL` for percentages/decimals
- `AUTOINCREMENT` for primary keys

---

## Dependencies

**Requires:**
- Access to `/home/workspace/productivity_tracker.db`
- SQLite 3 command-line tool (already installed)

**Blocks:**
- W2 (Calculator) - needs schema to store results
- W3 (Integration) - needs schema to update daily
- W4 (Email) - needs coaching_emails table
- W5 (UI) - needs schema to query for dashboard
- W6 (QA) - needs schema to validate

---

## Testing Instructions

After creating the migration:

```bash
# Backup current database
cp /home/workspace/productivity_tracker.db /home/workspace/productivity_tracker.db.backup

# Run migration
sqlite3 /home/workspace/productivity_tracker.db < migration_001_team_status.sql

# Verify tables created
sqlite3 /home/workspace/productivity_tracker.db ".tables"

# Insert test data
sqlite3 /home/workspace/productivity_tracker.db < test_data_team_status.sql

# Verify test data
sqlite3 /home/workspace/productivity_tracker.db "SELECT * FROM team_status_history;"
```

---

## Return Format

When complete, return to orchestrator thread with:

**Subject:** W1 (Schema) - COMPLETE

**Body:**
```
Status: ✅ COMPLETE

Deliverables:
- migration_001_team_status.sql
- test_data_team_status.sql
- SCHEMA_DOCUMENTATION.md

Files Changed:
- /home/workspace/productivity_tracker.db (4 new tables, 8 new indexes)

Test Results:
- [x] Migration runs without errors
- [x] Migration is idempotent
- [x] Test data inserted successfully
- [x] All tables queryable

Notes:
[Any design decisions, trade-offs, or blockers discovered]

Ready for W2 (Calculator Worker) to proceed.
```

---

## Questions/Clarifications

If you discover ambiguity or need decisions:
1. Document the question
2. Propose 2-3 options with trade-offs
3. Return to orchestrator for V's decision
4. DO NOT block on uncertainties - make reasonable assumptions and document them

---

**Orchestrator:** con_MuvXIR7jXZjZxlND  
**Your Mission:** Build the data foundation. Make it clean, focused, extensible.  
**Priority:** BLOCKING - Other workers are waiting on you.

Good luck! 🏗️

---
**Created:** 2025-10-30 01:33 ET
