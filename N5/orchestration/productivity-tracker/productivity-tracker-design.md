# Productivity Tracker - Technical Design
**Project:** Arsenal FC-Themed Gamified Email Productivity Tracker with RPI  
**Version:** 2.0  
**Date:** 2025-10-24  
**Orchestrator:** con_6NobvGrBPaGJQwZA

---

## Quick Reference

**Superhuman Start Date:** November 12, 2024

**Eras:**
- Pre-Superhuman: Before Nov 12, 2024
- Post-Superhuman/Pre-Zo: Nov 12, 2024 → Oct 24, 2025
- Post-Zo: Oct 25, 2025 onwards

**Database:** `/home/workspace/productivity_tracker.db`

**Workers:** 5 parallel + 2 sequential = 7 total

---

## System Architecture

### Components

1. **SQLite Database** - Single source of truth
2. **Email Scanner** - Gmail API integration with classification
3. **Meeting Scanner** - Google Calendar API integration
4. **RPI Calculator** - Load tracking and productivity index
5. **Arsenal XP System** - Gamification engine
6. **Web Dashboard** - Bun + Hono lo-fi interface
7. **Scheduled Tasks** - 30-min email/meeting scans

### Data Flow

```
Gmail API ──> Email Scanner ──> Database ──> RPI Calculator
                                     ↑            ↓
GCal API ──> Meeting Scanner ────────┘      XP System
                                              ↓
                                        Web Dashboard
```

---

## Database Schema

### Tables

1. **emails** - All sent emails with classification
2. **load_events** - Expected output (meetings, incoming, manual)
3. **daily_stats** - Aggregated RPI, XP per day
4. **xp_ledger** - XP transactions log
5. **achievements** - Unlocked achievements
6. **eras** - Historical baseline by era

### Key Indexes

- `emails(sent_at)` - Time range queries
- `emails(era)` - Era comparisons
- `load_events(event_date)` - Daily load calculation
- `daily_stats(date)` - Dashboard queries

---

## RPI Formula

```python
expected_daily = (
    meetings_count * 1.0 +
    incoming_substantial_emails * 0.5 +
    manual_load_additions
)

rpi = (actual_emails_sent / expected_daily) * 100 if expected_daily > 0 else 100
```

### XP Multipliers

- RPI ≥ 150%: 1.5× ("Invincible Form")
- RPI ≥ 125%: 1.25× ("Top Performance")
- RPI 100-124%: 1.0× (standard)
- RPI 75-99%: 0.9× ("Catch Up Needed")
- RPI < 75%: 0.75× ("Behind Schedule")

---

## Arsenal FC XP System

### Base XP Values

- New email: 10 XP
- Follow-up: 8 XP
- Response: 5 XP

### Bonuses

- Speed bonus: +5 XP (response < 24h)
- Clean Sheet: +50 XP (RPI ≥ 100%)
- Hat Trick: +20 XP (3+ new emails)
- Weekly streak: +10 XP per day

### Leveling

```python
level = floor(sqrt(total_xp / 100))
```

**Ranks:**
1. Youth Academy (L1-4)
2. Reserve Team (L5-9)
3. First Team Squad (L10-14)
4. Regular Starter (L15-19)
5. Club Captain (L20-24)
6. Arsenal Legend (L25+)

---

## Worker Breakdown

### Parallel Phase 1 (4 workers, ~1.5 hours)

1. **W1: Database Setup** - Schema, indexes, seed data
2. **W2: Email Scanner Core** - Gmail API, classification logic
3. **W3: Meeting Scanner** - GCal API, load tracking
4. **W4: XP System** - Leveling, achievements, bonuses

### Sequential Phase 2 (1 worker, ~30 min)

5. **W5: RPI Calculator** - Integration, daily aggregation (depends on W1-W4)

### Parallel Phase 3 (2 workers, ~2 hours)

6. **W6: Web Dashboard** - Bun/Hono site, Arsenal theme (depends on W5)
7. **W7: Scheduled Tasks** - Automation, cron setup (depends on W5)

---

## File Locations

### Scripts
- `/home/workspace/N5/scripts/productivity/email_scanner.py`
- `/home/workspace/N5/scripts/productivity/meeting_scanner.py`
- `/home/workspace/N5/scripts/productivity/rpi_calculator.py`
- `/home/workspace/N5/scripts/productivity/xp_system.py`

### Dashboard
- `/home/workspace/Sites/productivity-dashboard/` (Bun site)

### Database
- `/home/workspace/productivity_tracker.db`

### Docs
- `/home/workspace/Documents/Systems/productivity-tracker-guide.md`

---

## Success Criteria

- [ ] Historical baseline established across 3 eras
- [ ] RPI calculation working with auto + manual load
- [ ] Arsenal XP system with levels and achievements
- [ ] Web dashboard showing real-time stats
- [ ] Scheduled tasks running every 30 min
- [ ] Manual refresh capability
- [ ] All tests passing
- [ ] Fresh conversation test (P12)

---

## Architectural Principles Applied

- P0 (Rule-of-Two): Max 2 config files per component
- P2 (SSOT): Single SQLite database
- P7 (Dry-run): All scripts support `--dry-run`
- P15 (Complete Before Claiming): Explicit deliverable tracking
- P16 (No Invented Limits): Proper Gmail/GCal API usage
- P18 (State Verification): Verify all database writes
- P19 (Error Handling): Try/except with logging
- P21 (Document Assumptions): Track all TODOs
- P22 (Language Selection): Python for scripts, Node.js for dashboard

---

**Ready for worker deployment!** 🚀⚽
