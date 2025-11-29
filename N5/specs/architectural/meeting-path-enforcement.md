# Meeting Path Enforcement

**Version:** 1.0  
**Created:** 2025-10-29  
**Status:** Active  
**Related:** P5 (Anti-Overwrite), P11 (Failure Modes)

---

## Canonical Path

**ONLY location for meeting output:**



---

## System Enforcement Points

### 1. Configuration Files
- file 'N5/config/meeting_monitor_config.json' → "meetings": "Personal/Meetings"
- file 'N5/config/anchors.json' → meetings_personal path

### 2. Documentation
- file 'N5/prefs/operations/meetings-folder-structure.md'
- file 'N5/docs/meeting-system-reference.md'

### 3. Scheduled Tasks
- GTM Meetings Market Intelligence (c34187f7...)
- Meeting Action Items Extraction (fe975bf7...)

### 4. System Rules
- Rule ID: 4a39aa2b-3b25-454a-b09a-aa39faa261cb
- Enforces Personal/Meetings as ONLY location

---

## Migration: 2025-10-29

Recovered 73 meetings from:
- Inbox/20251028-132902_Meetings/ (6)
- Inbox/20251029-132500_Meetings/ (66)
- Records/meetings/ (1)

Root cause: Meeting processing wrote to Inbox instead of final location.

Fix: Multi-layer enforcement (config + docs + tasks + rules).

---

**Principle:** Personal data → Personal/. Meetings are personal records.
