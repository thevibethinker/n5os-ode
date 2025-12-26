---
created: 2025-12-15
last_edited: 2025-12-15
version: 1.0
---

# Meeting Weekly Organization System Build

**Conversation:** con_8TAAyMxOGTcp9IZm  
**Date:** 2025-12-15  
**Duration:** ~3 hours  
**Status:** Completed

## Summary

Overhauled the meeting organization system from a messy state-based `[M] → [P] → Archive` pipeline to a clean weekly folder structure (`Week-of-YYYY-MM-DD`). Eliminated manual steps, created automation, and built the `.n5ignored` marker system.

## What Was Built

### 1. Weekly Folder Organization
- Reorganized 80+ meetings from flat Inbox into 17 weekly folders
- Format: `Personal/Meetings/Week-of-2025-12-01/`
- Clean naming: removed ugly `[M]/[P]` suffixes, truncated email concatenations

### 2. Scheduled Agent for Auto-Organization
- Runs 4x/day (3:30am, 9:30am, 3:30pm, 9:30pm)
- Moves `[M]` meetings from Inbox → appropriate weekly folder
- Skips raw meetings (awaits MG-1 processing first)

### 3. `.n5ignored` Marker System
- New script: `N5/scripts/n5_ignore.py`
- Directories with `.n5ignored` are excluded from indexes
- Commands: mark, check, list, unmark, patterns

### 4. Pipeline Fixes
- MG-1: Kept scanning Inbox only (where webhooks deposit)
- MG-2/MG-4: Updated to scan recursively (Inbox + Week-of-*)
- Weekly organizer: Only moves `[M]/[P]` folders, skips raw

### 5. Obsolete System Removal
- Deleted 3 scheduled agents: MG-6, MG-7, Archive Completed Follow-Ups
- Archived 6 obsolete prompts to `Prompts/Archive/meetings_legacy/`

## Key Files

| File | Purpose |
|------|---------|
| `N5/scripts/meeting_weekly_organizer.py` | Main reorganization script |
| `N5/scripts/n5_ignore.py` | .n5ignored marker system |
| `Prompts/Meeting Manifest Generation.prompt.md` | Updated MG-1 (Inbox only) |
| `Prompts/Meeting Intelligence Generator.prompt.md` | Updated MG-2 (recursive) |
| `Prompts/Warm Intro Generator.prompt.md` | Updated MG-4 (recursive) |

## Archived Files

Working scripts from conversation workspace:
- `analyze_meetings.py` - Initial analysis script
- `reorganize_meetings.py` - Development version of organizer

