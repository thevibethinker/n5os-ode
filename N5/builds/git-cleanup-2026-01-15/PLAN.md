---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: con_c1ID1RsYieCNzQpm
---

# Plan: Atomic GitHub Commit Cleanup

Goal: Commit all uncommitted changes in logical, atomic chunks.

## Checklist

- [ ] Group 1: System Infrastructure & Build Protection
- [ ] Group 2: Core Scripts & Data Processing Utilities
- [ ] Group 3: CRM & Stakeholder Intelligence
- [ ] Group 4: Meeting Intelligence (Manifests & Blocks)
- [ ] Group 5: Records, AARs & Context Packs
- [ ] Group 6: Health & Wellness Tracking
- [ ] Group 7: Integrations & Sites Staging
- [ ] Group 8: General Cleanup & Deletions

## Affected Files
(Too many to list individually, but grouped by directory patterns below)

### Group 1: System Infrastructure
- `N5/builds/**/*.n5protected`
- `N5/systems/health/.n5protected`
- `Lists/system-upgrades.jsonl`
- `N5/prefs/workflows/teacher_workflow.md`

### Group 2: Core Scripts
- `N5/scripts/*.py`

### Group 3: CRM
- `N5/crm_v3/profiles/*.yaml`
- `Personal/Knowledge/CRM/`
- `Knowledge/linkedin/`

### Group 4: Meetings
- `Personal/Meetings/`
- `N5/data/` (Meeting candidates)

### Group 5: Records & AARs
- `Records/AARs/`
- `Records/Temporary/`
- `Knowledge/positions/`
- Root level markdown files (`Tope_Awotona_Framework.md`, etc.)

### Group 6: Health
- `Personal/Health/WorkoutTracker/`

### Group 7: Integrations & Sites
- `Integrations/google_flights/`
- `Personal/Integrations/fillout/`
- `Sites/vrijenattawar-staging/`

### Group 8: Cleanup
- `Inbox/` (Deletions)
- `Trash/` (Deletions)
- `Prompts/` additions

## Unit Tests
- `git status` should be empty (or only containing ignored files) after completion.
- `git log` should show atomic commits with clear messages.

