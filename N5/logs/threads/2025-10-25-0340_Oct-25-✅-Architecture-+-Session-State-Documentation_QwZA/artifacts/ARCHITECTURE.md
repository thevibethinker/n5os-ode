# Productivity Benchmarking System Architecture
**Project:** Arsenal FC-Themed Gamified Email Productivity Tracker  
**Version:** 1.0  
**Date:** 2025-10-24  
**Status:** Design Phase

---

## Objective

Build comprehensive productivity benchmarking system to quantify Zo's impact on email output, with gamification mechanics to drive daily engagement and continuous improvement.

---

## Success Criteria

- [ ] Historical email baseline established (Pre-Superhuman, Post-Superhuman/Pre-Zo, Post-Zo)
- [ ] Arsenal FC-themed XP/scoring system implemented
- [ ] SQLite database for multi-metric tracking architecture
- [ ] Gmail scanning script running every 30 minutes
- [ ] Lo-fi web dashboard showing daily progress and Arsenal-themed stats
- [ ] Tracks: total emails, new vs follow-up vs response, completion rate, avg response time
- [ ] Manual refresh capability for on-demand deep-dives
- [ ] Extensible architecture for future metrics (meetings by stakeholder type)

---

## System Components

### 1. Data Layer (SQLite)

**Database:** `/home/workspace/productivity_tracker.db`

**Schema Design:**

```sql
-- Core metrics table (extensible for future metrics)
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type TEXT NOT NULL,  -- 'email', 'meeting', 'document', etc.
    timestamp DATETIME NOT NULL,
    value INTEGER NOT NULL,
    metadata JSON,  -- Flexible for metric-specific data
    era TEXT,  -- 'pre_superhuman', 'post_superhuman_pre_zo', 'post_zo'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Email-specific tracking
CREATE TABLE emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gmail_message_id TEXT UNIQUE NOT NULL,
    gmail_thread_id TEXT,
    sent_date DATETIME NOT NULL,
    subject TEXT,
    email_type TEXT,  -- 'new', 'follow_up', 'response'
    subject_tag TEXT,  -- Extracted from [TAG] in subject
    to_recipients TEXT,  -- JSON array
    word_count INTEGER,
    is_substantial BOOLEAN DEFAULT 1,  -- Filters out automated/short/internal
    response_time_hours REAL,  -- Time from previous email in thread
    era TEXT,
    raw_metadata JSON,  -- Full Gmail API response
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- XP and leveling system
CREATE TABLE xp_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,  -- 'email_sent', 'streak_bonus', 'milestone_reached'
    xp_awarded INTEGER NOT NULL,
    description TEXT,
    arsenal_reference TEXT,  -- Fun Arsenal FC-themed message
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE player_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    total_xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    emails_sent INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    daily_target_met BOOLEAN DEFAULT 0,
    metadata JSON,  -- Daily stats snapshot
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Eras definition
CREATE TABLE eras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    era_name TEXT UNIQUE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,  -- NULL for current era
    description TEXT
);

-- Future: stakeholder meetings
CREATE TABLE stakeholder_time (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_date DATE NOT NULL,
    stakeholder_type TEXT NOT NULL,  -- 'customer', 'partner', 'coach', 'job_seeker'
    stakeholder_name TEXT,
    duration_minutes INTEGER,
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Principles Applied:**
- P2 (SSOT): Single database, no duplication
- P22 (Language Selection): SQLite for local-first, portable storage
- Extensible schema for multi-metric tracking
- JSON fields for flexibility without schema changes

---

### 2. Email Scanner (Python)

**Script:** `/home/workspace/N5/scripts/productivity_email_scanner.py`

**Responsibilities:**
- Query Gmail API for sent emails (handles pagination, no artificial limits per P16)
- Classify emails: new/follow-up/response
- Extract subject tags `[TAG]`
- Calculate word count and response time
- Filter out automated/short/internal emails (substantial only)
- Insert/update database
- Award XP based on activity

**Key Features:**
- Dry-run mode (P7)
- Error handling and logging (P19)
- State verification after writes (P18)
- Idempotent (can re-run without duplicates)
- Exit codes: 0 (success), 1 (errors), 2 (fatal)

**Gmail API Query Strategy:**
- Use `from:me` to get sent emails
- Date filters: `after:YYYY/MM/DD before:YYYY/MM/DD`
- Pagination with `pageToken` (no 3-msg limit per P16!)
- Progressive queries: today, this week, this month, historical

**Classification Logic:**
```python
def classify_email(message, thread_history):
    subject = message['subject']
    thread_id = message['threadId']
    
    # Extract tag from subject
    tag = extract_tag(subject)  # [TAG] -> 'TAG'
    
    # Classify by thread participation
    if len(thread_history) == 1:
        return 'new'
    elif is_user_initiated_thread(thread_history):
        return 'follow_up'
    else:
        return 'response'
```

**Substantial Email Filter:**
```python
def is_substantial(message):
    """Exclude automated, short, internal"""
    # Exclude automated
    if has_auto_reply_headers(message):
        return False
    
    # Exclude very short (< 50 words)
    if word_count(message) < 50:
        return False
    
    # Exclude internal-only (optional: based on domain)
    # Can refine this based on V's preferences
    
    return True
```

---

### 3. XP & Leveling System (Arsenal FC Theme)

**Design:** Arsenal FC progression system inspired by player development

**XP Awards:**
- New email: 10 XP ("Assist") 
- Follow-up email: 8 XP ("Pass Completion")
- Response email: 5 XP ("Defensive Header")
- Daily target met (e.g., 10 emails): 50 XP bonus ("Clean Sheet")
- Weekly streak (7 days): 100 XP ("Week of Excellence")
- Milestone bonuses:
  - First 50 emails: 200 XP ("Arsenal Academy Graduate")
  - First 100 emails: 500 XP ("First Team Debut")
  - First 250 emails: 1000 XP ("Club Legend Status")

**Leveling Curve:**
```python
def xp_for_level(level):
    """Arsenal-themed exponential curve"""
    # Level 1: 100 XP (Easy start)
    # Level 10: ~5000 XP
    # Level 20: ~25000 XP
    return int(100 * (level ** 1.8))

def get_arsenal_rank(level):
    """Arsenal progression titles"""
    if level < 5: return "Youth Academy"
    elif level < 10: return "Reserve Team"
    elif level < 15: return "First Team Squad"
    elif level < 20: return "Regular Starter"
    elif level < 25: return "Club Captain"
    elif level < 30: return "Arsenal Legend"
    else: return "Invincible"  # Reference to the 2003-04 undefeated season
```

**Daily Stats:**
- Emails sent today
- XP earned today
- Current streak (consecutive days meeting target)
- Progress to next level (XP bar)
- Arsenal-themed motivational messages

---

### 4. Web Dashboard (Lo-Fi Site)

**Location:** `/home/workspace/sites/productivity-dashboard/`

**Tech Stack:**
- Hono (Bun) server
- SQLite queries via better-sqlite3
- Lo-fi HTML/CSS (no heavy frameworks)
- Simple charts (Chart.js or D2 diagrams)
- Auto-refresh every 30 seconds

**Pages:**

**Home (`/`):**
- Big daily counter (emails sent today)
- Current XP / Level / Arsenal Rank
- Progress bar to next level
- Today's streak status
- Arsenal-themed motivational quote

**Dashboard (`/dashboard`):**
- Week-over-week comparison
- Historical trend chart (emails per week)
- Era comparison (Pre-SH / Post-SH-Pre-Zo / Post-Zo)
- XP timeline graph
- Achievements unlocked

**Stats (`/stats`):**
- Email type breakdown (new/follow-up/response)
- Average response time
- Tags frequency (from [TAG] subjects)
- Completion rate of follow-ups
- Time-to-send histogram

**Leaderboard (`/leaderboard`):**
- Best days (most emails)
- Best weeks
- Longest streaks
- Milestone achievements

**API Endpoints:**
- `GET /api/today` - Current day stats
- `GET /api/week` - This week stats
- `GET /api/historical` - Historical data by era
- `POST /api/refresh` - Manual trigger for email scan

**Design:**
- Lo-fi aesthetic: monospace fonts, simple colors (Arsenal red/white)
- ASCII art Arsenal cannon logo
- Minimal CSS, fast load times
- Mobile-friendly responsive design

---

### 5. Automation & Scheduling

**Scheduled Task:**
```bash
# Every 30 minutes
python3 /home/workspace/N5/scripts/productivity_email_scanner.py --scan-recent

# Daily summary (06:00 AM ET)
python3 /home/workspace/N5/scripts/productivity_daily_summary.py
```

**Manual Triggers:**
- `productivity-scan-all` - Full historical scan
- `productivity-refresh` - Refresh last 24 hours
- `productivity-stats` - Generate deep-dive report
- `productivity-reset` - Clear data (with confirmation)

---

## Data Flow

```
Gmail API
  ↓
[Scanner Script]
  ↓ 
SQLite Database ← [XP System]
  ↓
[Web Dashboard]
  ↓
Browser (Auto-refresh)
```

---

## Eras & Baseline

**Era Definitions:**

1. **Pre-Superhuman**: [START_DATE] to [SUPERHUMAN_START_DATE]
2. **Post-Superhuman/Pre-Zo**: [SUPERHUMAN_START_DATE] to 2025-10-24
3. **Post-Zo**: 2025-10-25 onwards

**Historical Scan Process:**
1. Define era dates in `eras` table
2. Run scanner with date ranges for each era
3. Classify all historical emails with era tags
4. Compute baseline stats (avg emails/week per era)
5. Generate baseline report

---

## Implementation Phases

### Phase 1: Database Setup
- [ ] Create SQLite schema
- [ ] Seed eras table
- [ ] Create indexes for performance

### Phase 2: Email Scanner
- [ ] Gmail API integration
- [ ] Classification logic
- [ ] Substantial email filter
- [ ] Database writes with verification (P18)
- [ ] Dry-run mode (P7)
- [ ] Error handling (P19)

### Phase 3: XP System
- [ ] XP calculation logic
- [ ] Leveling curve
- [ ] Arsenal-themed rank names
- [ ] Daily stats updates
- [ ] Milestone detection

### Phase 4: Historical Baseline
- [ ] Scan Pre-Superhuman era
- [ ] Scan Post-Superhuman/Pre-Zo era
- [ ] Generate comparison report
- [ ] Validate data quality

### Phase 5: Web Dashboard
- [ ] Create site structure
- [ ] Home page with daily counter
- [ ] Dashboard with charts
- [ ] Stats page
- [ ] API endpoints
- [ ] Lo-fi styling (Arsenal theme)

### Phase 6: Automation
- [ ] Scheduled task (30-min scanning)
- [ ] Daily summary email
- [ ] Manual commands registered
- [ ] Testing in production mode (P17)

### Phase 7: Polish & Extension
- [ ] Arsenal-themed achievements
- [ ] Streak bonuses
- [ ] Mobile optimization
- [ ] Performance tuning
- [ ] Documentation

---

## Testing Checklist

- [ ] Historical scan retrieves all eras correctly
- [ ] Email classification accuracy verified manually
- [ ] Substantial filter excludes automated/short/internal
- [ ] XP awards correctly for all event types
- [ ] Level progression matches curve
- [ ] Dashboard displays real-time data
- [ ] Scheduled task runs non-interactively (P15)
- [ ] Manual refresh works on-demand
- [ ] Dry-run preview accurate (P7)
- [ ] State verification after all writes (P18)
- [ ] No placeholder code in production (P21)
- [ ] Fresh thread test (P12)

---

## Open Questions

1. **Superhuman Start Date**: When did V start using Superhuman? (Awaiting answer)
2. **Daily Target**: What's the daily email target for "Clean Sheet" bonus? (Suggest: 10 emails)
3. **Substantial Filter Tuning**: Should internal Careerspan emails be excluded? Or only specific domains?
4. **Subject Tag Nomenclature**: Confirm current format (e.g., `[Follow-up]`, `[Outreach]`)
5. **Dashboard Location**: Deploy on registered user service or just local dev server for now?

---

## Arsenal FC Theme Examples

**Level Up Messages:**
- "Goal! You've reached Level 5: Reserve Team. Keep pressing forward!"
- "What a strike! Level 10: First Team Squad. You're wearing the famous red and white now!"
- "Unbelievable! Level 20: Arsenal Legend status. Bergkamp would be proud!"

**Daily Achievements:**
- "Clean Sheet! 🥅 10 emails sent today - solid defensive performance"
- "Hat Trick! 🎩 3 new threads initiated today"
- "Assist King! 👑 5 follow-ups completed"

**Streak Bonuses:**
- "7-day streak: Week of Excellence! This is the Arsenal way!"
- "30-day streak: Invincible Form! 🔥"

---

## Future Extensions

**Planned Metrics (Phase 8+):**
- Meetings booked by stakeholder type
- Time spent per stakeholder category
- Documents created/edited
- GitHub commits (if applicable)
- Voice notes transcribed

**Advanced Gamification:**
- Team challenges (compare with other Zo users?)
- Seasonal goals (quarterly targets)
- Trophy cabinet (achievements showcase)
- Historical comparison vs. industry benchmarks

---

**Principles Applied:**
- P2: SSOT (single database)
- P7: Dry-run support
- P15: Complete before claiming (explicit progress tracking)
- P16: No invented API limits
- P18: State verification
- P19: Error handling
- P21: Document assumptions
- P22: Python for data processing, Node.js for web dashboard with APIs

**Next Step:** Receive Superhuman start date, then proceed to implementation.
