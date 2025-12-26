---
created: 2025-12-17
last_edited: 2025-12-17
version: 1.0
provenance: con_D6vBftjjgAMTW64F
worker_id: WORKER_xawq_20251217_220317_707535
---

# DD System v1.1: CRM + Meeting Prep Integration — Design Memo

## Executive Summary

This memo proposes four interconnected enhancements to the DD (Due Diligence) system to close the loop between DD artifacts, CRM profiles, and meeting prep surfacing. The goal: when V has a meeting, relevant DD intel surfaces automatically; when DD is created, CRM stays synchronized.

---

## 1. Legacy DD Migration Plan

### Current State
- **2 legacy DDs** exist in `Documents/`:
  - `DD_Adam_Alpert_Pangea.md` (6.8KB, Dec 16)
  - `DD_Eric_Rubin_Consonant_VC.md` (10KB, Dec 5)
- **New DD location:** `Knowledge/market and competitor intel/due-diligence/<slug>/`
- Legacy files lack the structured frontmatter the new system expects

### Migration Strategy

**Phase A: Inventory & Validate (Non-Destructive)**
```bash
# Proposed script: N5/scripts/maintenance/migrate_legacy_dd.py --dry-run
```
1. Scan `Documents/DD_*.md` for legacy files
2. Parse existing content, extract: subject name, org, interaction type
3. Generate migration manifest showing: source → target path

**Phase B: Migrate (With Confirmation)**
1. For each legacy DD:
   - Create target directory under `Knowledge/market and competitor intel/due-diligence/<slug>/`
   - Inject standardized frontmatter (preserving `created` date from file mtime)
   - Copy content (no deletion yet)
   - Update any CRM profile that references the old path
2. Leave symlink at old location pointing to new location (backwards compat)
3. After 7 days, delete symlinks (optional cleanup phase)

### Proposed File Changes

| Action | Path | Notes |
|--------|------|-------|
| CREATE | `N5/scripts/maintenance/migrate_legacy_dd.py` | Migration script with --dry-run |
| MOVE | `Documents/DD_Adam_Alpert_Pangea.md` → `Knowledge/.../adam-alpert/DD_Adam_Alpert_20251216.md` | After frontmatter injection |
| MOVE | `Documents/DD_Eric_Rubin_Consonant_VC.md` → `Knowledge/.../eric-rubin/DD_Eric_Rubin_20251205.md` | After frontmatter injection |
| UPDATE | `N5/crm_v3/profiles/Adam_Alpert_pangea.yaml` | Fix DD link path |
| UPDATE | `N5/crm_v3/profiles/Eric_Rubin_eric.yaml` | Add DD link section |

---

## 2. Meeting-Prep Surfacing Design

### Objective
When `Meeting Prep Digest.prompt.md` runs, it should automatically surface relevant DD intel for attendees.

### Current State
- `Meeting Prep Digest` calls `morning_digest.py` and retrieves calendar events
- No linkage to DD system exists
- CRM profiles have `## Due Diligence` section (when linked)

### Proposed Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Google Cal     │────▶│  CRM Lookup     │────▶│  DD Retrieval   │
│  (attendees)    │     │  (by email)     │     │  (from CRM link)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Inject into    │
                                               │  Meeting Prep   │
                                               └─────────────────┘
```

### Implementation

**Option A: Enhance `morning_digest.py`** (Minimal)
- Add `get_dd_intel_for_attendees(attendee_emails: list)` function
- For each email → lookup CRM profile → check `## Due Diligence` section → return DD paths
- Append "### DD Intel Available" section to digest

**Option B: Create `n5_meeting_dd_linker.py`** (Modular)
- Standalone script: `python3 n5_meeting_dd_linker.py --date 2025-12-18`
- Returns structured JSON: `{meeting_id: [{attendee, crm_profile, dd_paths, dd_summaries}]}`
- `Meeting Prep Digest` calls this as a module

**Recommendation:** Option B (modular) — keeps DD logic isolated, testable, reusable.

### Proposed File Changes

| Action | Path | Notes |
|--------|------|-------|
| CREATE | `N5/scripts/n5_meeting_dd_linker.py` | DD ↔ Meeting linker |
| UPDATE | `Prompts/Meeting Prep Digest.prompt.md` | Add instruction to call linker |
| UPDATE | `N5/scripts/morning_digest.py` | Import and call linker (optional) |

---

## 3. CRM DD Link Section Standard

### Current State
The `n5_dd.py link` command appends DD links to CRM profiles, but the format is inconsistent.

**Current format (ad-hoc):**
```markdown
## Due Diligence
- 2025-12-17: [DD_Adam_Alpert_20251217.md](Knowledge/market and competitor intel/due-diligence/adam-alpert/DD_Adam_Alpert_20251217.md) - acquisition
```

### Proposed Standard Format

```markdown
## Due Diligence

| Date | Type | Status | Path |
|------|------|--------|------|
| 2025-12-17 | acquisition | in_progress | [DD_Adam_Alpert_20251217.md](Knowledge/...) |
| 2025-12-05 | networking | complete | [DD_Adam_Alpert_20251205.md](Knowledge/...) |

**Latest:** [Quick summary or recommendation from most recent DD]
```

### Benefits
- **Machine-parseable:** Table format enables programmatic extraction
- **Status visible:** At-a-glance view of DD completion state
- **Summary line:** LLM can surface the "Latest" line in meeting prep

### Proposed File Changes

| Action | Path | Notes |
|--------|------|-------|
| UPDATE | `N5/scripts/n5_dd.py` | Modify `link_dd_to_crm()` to use table format |
| CREATE | `N5/prefs/crm/dd_link_standard.md` | Document the standard |
| UPDATE | `N5/crm_v3/profiles/Adam_Alpert_pangea.yaml` | Migrate to new format |

---

## 4. DD Lifecycle/Status Markers

### Current State
DD files have `status: in_progress` in frontmatter, but no lifecycle tracking.

### Proposed Lifecycle

```
[created] → [in_progress] → [ready_for_review] → [complete]
                  │                                    │
                  └──────────[stale]◀──────────────────┘
                         (no update in 30 days)
```

### Frontmatter Extension

```yaml
---
status: in_progress          # created | in_progress | ready_for_review | complete | stale
status_updated: 2025-12-17
decision_deadline: 2025-12-25  # Optional: when must V decide?
stale_after_days: 30           # Auto-mark stale if untouched
---
```

### n5_dd.py Extensions

```bash
# Mark DD ready for review
python3 n5_dd.py ready --subject "Adam Alpert"

# Mark DD complete with summary
python3 n5_dd.py complete --subject "Adam Alpert" --summary "Recommend proceeding"

# Check for stale DDs
python3 n5_dd.py stale --list

# Refresh status across all DDs (for scheduled task)
python3 n5_dd.py refresh-status
```

### Proposed File Changes

| Action | Path | Notes |
|--------|------|-------|
| UPDATE | `N5/scripts/n5_dd.py` | Add `ready`, `complete`, `stale`, `refresh-status` commands |
| UPDATE | `N5/docs/DD_SYSTEM_QUICKREF.md` | Document lifecycle states |
| UPDATE | DD skeleton templates in n5_dd.py | Add new frontmatter fields |

---

## Implementation Priority

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| P0 | CRM DD Link Standard | Low | High — fixes data consistency |
| P1 | Meeting-Prep Surfacing | Medium | High — closes the loop |
| P2 | DD Lifecycle Markers | Low | Medium — improves hygiene |
| P3 | Legacy DD Migration | Low | Medium — cleans up debt |

---

## Files to Create/Modify Summary

### CREATE
1. `N5/scripts/n5_meeting_dd_linker.py` — DD ↔ Meeting linker
2. `N5/scripts/maintenance/migrate_legacy_dd.py` — Legacy migration
3. `N5/prefs/crm/dd_link_standard.md` — Standard documentation

### UPDATE
1. `N5/scripts/n5_dd.py` — Lifecycle commands + table format
2. `N5/docs/DD_SYSTEM_QUICKREF.md` — Document lifecycle
3. `Prompts/Meeting Prep Digest.prompt.md` — Integrate linker
4. `N5/crm_v3/profiles/*.yaml` — Migrate to table format (2 profiles)

---

## Next Steps

1. **V to review this memo** — confirm priorities, approve approach
2. **Implement P0** (CRM DD Link Standard) — 15 min
3. **Implement P1** (Meeting-Prep Surfacing) — 45 min
4. **Implement P2** (Lifecycle Markers) — 20 min
5. **Run P3** (Legacy Migration) — 10 min with --dry-run first

---

## Appendix: Current System State

### DD Base Path
`Knowledge/market and competitor intel/due-diligence/`

### Existing DDs (New Location)
- `adam-alpert/DD_Adam_Alpert_20251217.md` (skeleton, in_progress)
- `teamworkonline/teamworkonline__partnership-acquisition-dossier.md` (complete)

### Legacy DDs (Documents/)
- `DD_Adam_Alpert_Pangea.md` — needs migration
- `DD_Eric_Rubin_Consonant_VC.md` — needs migration

### CRM Profiles with DD Links
- `Adam_Alpert_pangea.yaml` — has link (needs format upgrade)
- `Eric_Rubin_eric.yaml` — missing DD link

