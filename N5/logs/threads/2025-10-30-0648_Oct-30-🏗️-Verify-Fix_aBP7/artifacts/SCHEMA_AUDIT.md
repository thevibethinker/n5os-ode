# Schema Audit: W1 vs Handoff Spec

## Critical Misalignments Found

### 1. team_status_history - MISSING FIELDS

**Handoff spec requires:**
```sql
consecutive_poor_days INTEGER  -- Days below 90% in a row
reason TEXT                     -- Why status changed
changed_at TIMESTAMP           -- When status actually changed
```

**W1 actually created:**
```sql
promotion_eligible INTEGER DEFAULT 0  -- NOT in spec
(missing: consecutive_poor_days, reason, changed_at)
```

**Impact:** Calculator (W2) expects to track consecutive_poor_days for demotion logic. This is BLOCKING.

---

### 2. status_transitions - MISSING FIELDS

**Handoff spec requires:**
```sql
grace_days_used INTEGER
consecutive_poor_days INTEGER
probation_triggered INTEGER
```

**W1 actually created:**
```sql
notes TEXT  -- Wrong field!
(missing: grace_days_used, consecutive_poor_days, probation_triggered)
```

**Impact:** Transition audit trail incomplete. Can't debug why demotions happened.

---

### 3. coaching_emails - Wrong table exists

**W1 created:** `coaching_emails` table
**Handoff spec:** Never mentions this table (W4/W5 territory)

**Impact:** Premature implementation. Not blocking but shows W1 went off-spec.

---

### 4. career_stats - Wrong table exists

**W1 created:** `career_stats` table
**Handoff spec:** Never mentions this table

**Impact:** Same as above - outside W1's scope.

---

## Root Cause Analysis

W1 appears to have:
1. ✅ Created correct tables (team_status_history, status_transitions)
2. ❌ Omitted critical fields from handoff spec
3. ❌ Added fields not in spec (promotion_eligible)
4. ❌ Created extra tables not requested (coaching_emails, career_stats)

This suggests W1 either:
- Didn't fully read the handoff spec, OR
- Made independent design decisions without orchestrator approval

---

## Required Corrections

### Migration #1: Fix team_status_history

```sql
ALTER TABLE team_status_history 
ADD COLUMN consecutive_poor_days INTEGER DEFAULT 0;

ALTER TABLE team_status_history 
ADD COLUMN reason TEXT;

ALTER TABLE team_status_history 
ADD COLUMN changed_at TIMESTAMP;

-- Remove non-spec field
-- (Can't drop columns in SQLite easily, but we can ignore it)
```

### Migration #2: Fix status_transitions

```sql
ALTER TABLE status_transitions 
ADD COLUMN grace_days_used INTEGER DEFAULT 0;

ALTER TABLE status_transitions 
ADD COLUMN consecutive_poor_days INTEGER DEFAULT 0;

ALTER TABLE status_transitions 
ADD COLUMN probation_triggered INTEGER DEFAULT 0;

-- notes field stays (can coexist with spec fields)
```

---

## Decision Point

**Option A:** Apply migrations, keep extra tables
- Pros: Minimal disruption, forward-compatible
- Cons: Database has off-spec artifacts

**Option B:** Drop and rebuild entire schema
- Pros: Clean slate, 100% spec-aligned
- Cons: Loses any test data from previous work

**Recommendation:** Option A (migrations) since:
1. Only 2 days of data in daily_stats (minimal loss)
2. Extra tables don't hurt calculator
3. Faster to fix than rebuild

---

## Validation Checklist

After migration:
- [ ] team_status_history has all 12 required fields
- [ ] status_transitions has all 10 required fields
- [ ] Calculator can write to all expected fields
- [ ] No blocking issues for W2 implementation

---

**Audit Date:** 2025-10-30 02:44 ET
**Auditor:** Operator (pre-W2 launch)
