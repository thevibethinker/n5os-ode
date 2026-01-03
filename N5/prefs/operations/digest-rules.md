# Digest Rules & Principles

**Version:** 1.0.0
**Created:** 2026-01-03
**Purpose:** Standardized rules for creating and maintaining the ONE daily digest

---

## Core Philosophy

**One Digest, Maximum Impact.** V receives exactly ONE daily digest that surfaces the most important information and actionable items. No digest sprawl. No redundant notifications.

### Guiding Principles

1. **Signal over Noise** — Only include items that require attention or action today
2. **Actionable over Informational** — Every section should have a clear "what to do"
3. **Context over Data** — Don't just show numbers; explain what they mean
4. **Three is the Magic Number** — Limit action items to 3 to maintain focus
5. **Fail Gracefully** — Missing data should produce a helpful message, not break the digest

---

## The ONE Daily Digest Structure

### Required Sections (in order)

| Section | Purpose | Data Source | Fallback |
|---------|---------|-------------|----------|
| **Bio-Context** | Sleep quality, resting HR, health advisory | `wellness.db` | "Sleep data not synced" |
| **Today's Workout** | Training plan with coaching | Hardcoded 10K plan | "Check workout plan" |
| **The Landscape** | Today's calendar events | Google Calendar via Zo | "No events scheduled" |
| **Top 3 Today** | Highest-priority action items | Lists/*.jsonl, must-contact | "No priority items today" |
| **Reconnects** | 2-3 people to reach out to with context | `crm_v3.db` profiles | "CRM needs attention" |
| **The Nudge** | CTA to start morning flow | Static link | Always present |

### Removed/Deprecated Sections

These sections are **NOT** included in the unified digest:

- ~~The Loop~~ — Was always placeholder text
- ~~The Pulse~~ — Productivity data inconsistent, not actionable
- ~~The Wedge~~ — Quotes not adding value
- ~~Habit Tracker~~ — Move to separate weekly review
- ~~CRM Review (data quality)~~ — Replaced by actionable Reconnects
- ~~Must-Go Events~~ — Separate notification system

---

## Data Source Rules

### Bio-Context Rules
```
Source: wellness.db → daily_sleep, daily_resting_hr
Fallback: "Sleep data not synced. Check Fitbit sync."
Advisory Thresholds:
  - DEFICIT MODE: <6 hrs sleep
  - LOW SCORE: sleep_score <70 OR efficiency <70%
  - NOMINAL: Everything else
```

### Today's Workout Rules
```
Source: Hardcoded weekly schedule from 10K_Prep_Plan.md
Include: Type, duration, coaching note, days until race
Recent context: Last workout from wellness.db life_logs
Fallback: "Consult your 10K prep plan."
```

### Calendar/Landscape Rules
```
Source: Google Calendar via Zo CLI
Format: Time range (24hr) + Event title + Calendar name
Include: Only events for TODAY
Exclude: All-day events unless tagged important
Fallback: "No events scheduled for today."
```

### Top 3 Today Rules
```
Sources (priority order):
  1. Lists/must-contact.jsonl (status=open, priority=H)
  2. Lists/ideas.jsonl (priority=H, tags contain "today" or "urgent")
  3. Overdue scheduled tasks from scheduled_tasks.db
  4. Calendar events requiring prep (meetings with external stakeholders)

Selection Algorithm:
  - Take up to 3 items total
  - Prefer H priority over M priority
  - Prefer older created_at dates (FIFO for equal priority)

Format per item:
  - Title (bold)
  - One-line context or next step
  - Source reference (e.g., "from must-contact")

Fallback: "No priority items today. Review your lists or enjoy the clarity."
```

### Reconnects Rules
```
Source: crm_v3.db → profiles table
Query:
  - last_contact_at IS NOT NULL
  - last_contact_at < date('now', '-30 days')
  - category IN ('INVESTOR', 'NETWORKING', 'COMMUNITY', 'FOUNDER')
  - ORDER BY last_contact_at ASC
  - LIMIT 3

Format per person:
  - Name (bold)
  - Category + "last contact: X days ago"
  - One-line context from yaml_path if available

Fallback (no contacts >30 days): "Network is healthy. No reconnects needed."
Fallback (no data): "CRM needs profile data. Run enrichment."
```

---

## Technical Requirements

### Script Standards
All digest scripts MUST follow `/home/workspace/N5/prefs/operations/digest-creation-protocol.md`:

1. **`--dry-run` flag** — Preview without saving
2. **`--date` parameter** — Target date in YYYY-MM-DD format
3. **`--json` flag** — Output structured JSON for automation
4. **Logging** — ISO timestamps, INFO level minimum
5. **Verification** — Confirm file exists and is non-zero after write
6. **Exit codes** — 0 for success, 1 for failure

### Output Format
```
Location: /home/workspace/N5/digests/morning-digest-YYYY-MM-DD.md
Naming: morning-digest-{date}.md (NO other daily digest files)
Encoding: UTF-8
Max Size: ~5KB (keep it scannable)
```

### Scheduling
```
Generation: Daily at 07:00 ET (before morning routine)
Delivery: Email at 07:05 ET with subject "🌅 MorningOS: {date}"
Retry: Once at 07:30 ET if first attempt fails
```

---

## Anti-Patterns

**DO NOT:**
- Create additional daily digest types (consolidate everything here)
- Show placeholder text ("initializing...", "coming soon")
- Include sections that consistently show "No data"
- List more than 3 action items
- Show raw data without context (e.g., "252 profiles missing email")
- Include stale/cached content (check timestamps)

**DO:**
- Show actionable items with clear next steps
- Provide fallback messages that guide user action
- Keep sections short and scannable
- Test with `--dry-run` before production
- Verify data freshness before including

---

## Maintenance

### Weekly Review
- Check digest generation success rate in `N5/logs/`
- Review any fallback messages triggered (indicates data issues)
- Verify calendar integration is working

### Monthly Review
- Assess which sections are actually being used
- Consider adding/removing sections based on user feedback
- Update thresholds (e.g., sleep, reconnect days) if needed

---

## Related Files

- **Script:** `N5/scripts/morning_digest.py`
- **Protocol:** `N5/prefs/operations/digest-creation-protocol.md`
- **CRM Data:** `N5/data/crm_v3.db`
- **Health Data:** `N5/data/wellness.db`
- **Lists:** `Lists/*.jsonl`
- **Output:** `N5/digests/morning-digest-*.md`

---

## Change Log

### 1.0.0 — 2026-01-03
- Initial version: ONE digest philosophy established
- Defined 6-section structure: Bio-Context, Workout, Landscape, Top 3 Today, Reconnects, Nudge
- Removed deprecated sections (Loop, Pulse, Wedge, Habit Tracker, CRM data quality)
- Created data source rules with fallbacks
- Established anti-patterns and maintenance schedule
