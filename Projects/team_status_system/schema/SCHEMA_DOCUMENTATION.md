# Team Status Career Progression - Schema Documentation

**Version:** 1.0.0  
**Date:** 2025-10-30  
**Worker:** W1 (Schema)  
**Database:** productivity_tracker.db

---

## Overview

This schema extension adds career progression tracking on top of V's existing RPI/productivity system. Models an Arsenal FC-style team status hierarchy where V progresses from **Transfer List** → **Reserves** → **Squad Member** → **First Team** → **Invincible** → **Legend** based on sustained performance.

**Design Philosophy:**
- Simple, normalized structure
- Historical audit trail for all status changes
- Anti-spam email tracking
- Single-row aggregate stats for dashboard efficiency

---

## Table Definitions

### 1. `team_status_history`

**Purpose:** Daily snapshot of V's current team status  
**Growth Rate:** 1 row/day (~365 rows/year)  
**Primary Use:** Current status lookups, 7-day rolling windows, trend analysis

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto-increment primary key |
| `date` | TEXT UNIQUE | YYYY-MM-DD, daily record |
| `status` | TEXT | Current status (see Status Values below) |
| `days_in_status` | INTEGER | Consecutive days at this level (resets on change) |
| `previous_status` | TEXT | Status before current one (NULL if starting) |
| `top5_avg` | REAL | Top 5 of 7 RPI average that determined status |
| `grace_days_used` | INTEGER | How many of 2 worst days excluded (0-2) |
| `promotion_eligible` | INTEGER | 1 if eligible for promotion, 0 otherwise |
| `probation_days_remaining` | INTEGER | Days left in probation period (0 if not in probation) |
| `created_at` | TIMESTAMP | Record creation time |

**Status Values:**
- `transfer_list` - Performance below 80%
- `reserves` - Performance 80-89%
- `squad_member` - Performance 90-99%
- `first_team` - Performance 100%+
- `invincible` - Elite tier (unlock condition TBD by W2)
- `legend` - Elite tier (unlock condition TBD by W2)

**Indexes:**
- `idx_team_status_date` - Fast date lookups
- `idx_team_status_status` - Status distribution queries
- `idx_team_status_promotion_eligible` - Find promotion candidates

**Example Query (Get last 7 days):**
```sql
SELECT date, status, top5_avg, days_in_status 
FROM team_status_history 
WHERE date >= date('now', '-7 days') 
ORDER BY date DESC;
```

---

### 2. `status_transitions`

**Purpose:** Audit log of every status change  
**Growth Rate:** Variable (depends on performance volatility)  
**Primary Use:** Career history, transition analysis, debugging rules

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto-increment primary key |
| `date` | TEXT | Date transition occurred |
| `from_status` | TEXT | Status moving from |
| `to_status` | TEXT | Status moving to |
| `reason` | TEXT | Why transition happened (see Transition Reasons) |
| `top5_avg` | REAL | Performance metric at transition time |
| `notes` | TEXT | Optional context (manual overrides, special cases) |
| `created_at` | TIMESTAMP | Record creation time |

**Transition Reasons:**
- `performance` - Met/failed performance thresholds
- `unlock_elite` - Unlocked Invincible/Legend tier
- `probation_end` - Probation period completed
- `manual_override` - Admin/testing adjustment

**Indexes:**
- `idx_transitions_date` - Chronological lookups
- `idx_transitions_to_status` - "When did I reach First Team?"
- `idx_transitions_reason` - Filter by transition type

**Example Query (Find all promotions):**
```sql
SELECT date, from_status, to_status, top5_avg 
FROM status_transitions 
WHERE to_status > from_status 
  AND reason = 'performance'
ORDER BY date DESC;
```

---

### 3. `coaching_emails`

**Purpose:** Track sent coaching alerts to avoid spam  
**Growth Rate:** ~2-5 emails/week  
**Primary Use:** Deduplication, email history, engagement tracking

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto-increment primary key |
| `date` | TEXT | Date email was sent |
| `email_type` | TEXT | Type of coaching message (see Email Types) |
| `status_at_time` | TEXT | V's status when email sent |
| `trigger_context` | TEXT | What triggered this email (human-readable) |
| `sent_via` | TEXT | Delivery method: `gmail`, `dry_run`, `manual` |
| `created_at` | TIMESTAMP | Record creation time |

**Email Types:**
- `demotion` - Status dropped (e.g., First Team → Squad Member)
- `promotion` - Status improved (e.g., Reserves → Squad Member)
- `warning` - Performance trending down but not yet demoted
- `grace_alert` - Using grace days (approaching threshold)
- `achievement` - Milestone reached (e.g., 30 days First Team)

**Indexes:**
- `idx_coaching_date` - Chronological lookups
- `idx_coaching_type` - Filter by email type
- `idx_coaching_status` - Emails per status level

**Example Query (Last 7 days of emails):**
```sql
SELECT date, email_type, status_at_time, trigger_context 
FROM coaching_emails 
WHERE date >= date('now', '-7 days') 
ORDER BY date DESC;
```

---

### 4. `career_stats`

**Purpose:** Single-row aggregate statistics (cache table)  
**Growth Rate:** 1 row only, updated in place  
**Primary Use:** Dashboard summary, career overview

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Always 1 (enforced by CHECK constraint) |
| `total_game_days` | INTEGER | Total days in career system |
| `days_transfer_list` | INTEGER | Days spent on Transfer List |
| `days_reserves` | INTEGER | Days spent in Reserves |
| `days_squad_member` | INTEGER | Days spent as Squad Member |
| `days_first_team` | INTEGER | Days spent in First Team |
| `days_invincible` | INTEGER | Days spent as Invincible |
| `days_legend` | INTEGER | Days spent as Legend |
| `total_promotions` | INTEGER | Total upward movements |
| `total_demotions` | INTEGER | Total downward movements |
| `elite_unlocks` | INTEGER | Times reached Invincible/Legend |
| `longest_streak_first_team` | INTEGER | Longest consecutive First Team days |
| `longest_streak_invincible` | INTEGER | Longest consecutive Invincible days |
| `last_updated` | TEXT | Last update date (for cache invalidation) |
| `created_at` | TIMESTAMP | Record creation time |

**Update Strategy:** W2 (Calculator) updates this daily after processing

**Example Query (Career overview):**
```sql
SELECT 
    total_game_days,
    days_first_team || ' (' || ROUND(100.0 * days_first_team / total_game_days, 1) || '%)' as first_team_pct,
    total_promotions,
    total_demotions,
    longest_streak_first_team
FROM career_stats 
WHERE id = 1;
```

---

## Schema Integration

### Relationships with Existing Tables

**Joins `daily_stats` for RPI data:**
```sql
SELECT 
    h.date,
    h.status,
    h.top5_avg,
    d.rpi_score,
    d.email_count
FROM team_status_history h
JOIN daily_stats d ON h.date = d.date
WHERE h.date >= date('now', '-7 days')
ORDER BY h.date DESC;
```

**No foreign key constraints** - Uses date-based joins for flexibility

---

## Migration and Testing

### Apply Migration
```bash
sqlite3 /home/workspace/productivity_tracker.db < migration_001_team_status.sql
```

### Load Test Data
```bash
sqlite3 /home/workspace/productivity_tracker.db < test_data_team_status.sql
```

### Verify Schema
```bash
sqlite3 /home/workspace/productivity_tracker.db ".schema team_status_history"
sqlite3 /home/workspace/productivity_tracker.db "SELECT COUNT(*) FROM team_status_history;"
```

### Expected Test Data Results
- 14 rows in `team_status_history` (Oct 16-29, 2025)
- 3 rows in `status_transitions` (3 promotions)
- 5 rows in `coaching_emails` (3 promotions, 1 warning)
- 1 row in `career_stats` (14-day summary)

---

## Worker Handoffs

### For W2 (Calculator)
**Your job:** Implement calculation logic using this schema

**Key queries you'll need:**
1. Get last 7 days RPI scores from `daily_stats`
2. Calculate top 5 average (exclude 2 worst days)
3. Determine status based on thresholds
4. Insert/update `team_status_history` daily
5. Log transitions in `status_transitions`
6. Update `career_stats` aggregates

**Status thresholds (from spec):**
- Transfer List: < 0.80
- Reserves: 0.80 - 0.89
- Squad Member: 0.90 - 0.99
- First Team: ≥ 1.00
- Invincible: Special unlock (define condition)
- Legend: Special unlock (define condition)

### For W4 (Email Composer)
**Your job:** Send coaching emails using this schema

**Key queries you'll need:**
1. Check `coaching_emails` for recent sends (avoid spam)
2. Get current status from `team_status_history`
3. Get transition info from `status_transitions`
4. Log sent emails to `coaching_emails`

**Deduplication rules (suggested):**
- Max 1 promotion email per status change
- Max 1 warning per 3 days
- Achievement emails: once per milestone

### For W5 (Dashboard)
**Your job:** Display status and stats using this schema

**Key queries you'll need:**
1. Current status: `SELECT * FROM team_status_history WHERE date = date('now')`
2. Career overview: `SELECT * FROM career_stats WHERE id = 1`
3. Recent transitions: `SELECT * FROM status_transitions ORDER BY date DESC LIMIT 5`
4. 7-day trend: `SELECT date, status, top5_avg FROM team_status_history WHERE date >= date('now', '-7 days')`

---

## Schema Maintenance

### Daily Operations (W2's Responsibility)
1. Insert new `team_status_history` row for today
2. If status changed: insert `status_transitions` row
3. Update `career_stats` aggregates
4. (Optional) Trigger W4 email check

### Backup Considerations
- `team_status_history` - Critical historical data, backup daily
- `status_transitions` - Audit trail, backup daily
- `coaching_emails` - Reference data, backup weekly
- `career_stats` - Derived data, can be recalculated

### Schema Evolution
Future additions should:
- Add columns (not remove) for backward compatibility
- Use migrations with version numbers (002, 003, etc.)
- Document changes in this file with date stamps

---

## Performance Notes

**Expected Table Sizes (1 year):**
- `team_status_history`: ~365 rows (~50KB)
- `status_transitions`: ~50-100 rows (~10KB)
- `coaching_emails`: ~100-200 rows (~15KB)
- `career_stats`: 1 row (~1KB)

**Total overhead:** <100KB/year - negligible

**Index overhead:** ~20KB - negligible

**Query performance:** Sub-millisecond for all expected queries

---

## Questions for W2 (Calculator)

1. **Elite tier unlock conditions?** How does V unlock Invincible/Legend?
2. **Probation period enforcement?** During probation, can V be demoted or only frozen?
3. **Grace day reset timing?** Do grace days reset daily, weekly, or on status change?
4. **Tie-breaker rules?** If exactly 3 promotable candidates at different status levels?

---

## Completion Checklist

- [x] Migration script created (`migration_001_team_status.sql`)
- [x] Test data script created (`test_data_team_status.sql`)
- [x] Schema documentation created (`SCHEMA_DOCUMENTATION.md`)
- [ ] Migration applied to production DB (W2's call)
- [ ] Test data validated (W2's call)
- [ ] Calculator logic implemented (W2)
- [ ] Email composer integrated (W4)
- [ ] Dashboard displaying data (W5)

---

**W1 (Schema) deliverable complete. Awaiting W2 (Calculator) to proceed.**

*Generated: 2025-10-30T02:28 ET*
