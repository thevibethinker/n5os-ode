---
created: 2026-02-14
last_edited: 2026-02-14
version: "1.1"
provenance: con_oSMgpCG0LKXFengK
---

# Stale Folder Cleanup Plan

**Cutoff:** No files modified since Nov 1, 2025
**Scan date:** 2026-02-14
**Total reclaimable (estimated):** ~300 MB (mostly Inbox snapshots)

---

## Legend

| Action | Meaning |
|--------|---------|
| **DELETE** | Remove entirely — no valuable content |
| **ARCHIVE** | Move to `Documents/Archive/` for cold storage |
| **REVIEW-THEN-DELETE** | Spot-check contents, then delete |
| **RELOCATE** | Move contents to their canonical home |
| **KEEP** | Leave as-is (structural or still relevant) |

---

## TIER 1 — High-Confidence Deletes (empty dirs, duplicates, junk)

### Empty directories — DELETE all

| Path | Notes |
|------|-------|
| `Documents/Meetings` + `_staging` | Empty. Meetings live in `Personal/Meetings/` |
| `Research/archive` | Empty scaffolding |
| `Research/builds` | Empty scaffolding |
| `Research/intel` | Empty scaffolding |
| `Research/topics` | Empty scaffolding |
| `Records/Company/emails` | Empty |
| `Careerspan/meta-resumes/outputs` | Empty |
| `Careerspan/meta-resumes/quarantine` | Empty |
| `Build Exports/n5os-ode/Records` | Empty inside export |
| `Build Exports/n5os-ode/scripts` | Empty inside export |
| `Build Exports/n5os-ode-backup-pre-merge/Records` | Empty inside export |
| `Build Exports/n5os-ode-backup-pre-merge/scripts` | Empty inside export |
| `Research/general/reliance-hc-research` | Empty |
| `Research/health/merisenda-alatorre-ace-fitness` | Empty |

**Command:** `find <path> -type d -empty -delete` (after confirming)

---

## TIER 2 — Stale Content Folders (per-folder action)

### `Records/stakeholder_discovery/` — DELETE
- **440 files, 0.28 MB** — all tiny JSON/JSONL run summaries from Oct 2025
- Batch-generated artifacts from a deprecated stakeholder discovery process
- No unique content — all machine-generated run logs
- **Action:** Delete entire folder

### `Records/Archive/` — DELETE
- **5 files, 0.04 MB** — Hamoon email drafts from Oct 2025
- Multiple iterations of the same email, all superseded
- **Action:** Delete entire folder

### `Records/Reflections/` — REVIEW-THEN-DELETE
- **14 files, 0.07 MB** — Proposal drafts and system specs from Oct 2025
- Mix of proposal stubs (0.2 KB placeholders) and integration specs
- Likely all superseded by later work
- **Action:** Glance at `integration-onboarding.md` and `product-spec.md` — if no unique value, delete all

### `Records/Company/Proposals/` — DELETE
- **2 files, ~0 KB** — auto-generated proposal stubs from Oct 2025
- **Action:** Delete

### `Records/Company/Technology/` — ARCHIVE
- **2 files, 0.34 MB** — "Careerspan's Technological Foundation" and "How ATS Systems Work" PDFs
- These have reference value → move to `Knowledge/content-library/personal/`
- **Action:** Relocate to Knowledge, then delete folder

### `Records/Company/voice-memos/` — REVIEW-THEN-DELETE
- **2 files, 0.77 MB** — One .ogg voice memo + transcript from Oct 2025
- **Action:** Listen/read transcript. If captured elsewhere, delete.

### `Records/Personal/drafts/` — DELETE
- **2 files, ~0 KB** — README + one intro draft from Oct 2025
- **Action:** Delete

### `Records/Personal/notes/` — DELETE
- **2 files, 0.01 MB** — One voice memo transcript, one processed note from Sep 2025
- **Action:** Delete

### `Documents/Resumes/` — RELOCATE then DELETE
- **14 files, 1.85 MB** — Mix of V's resume + candidate resumes from Oct 2025
- V's resume (`v_mostrecentresume-FCH.pdf`, `Vrijen_Attawar_Tech_Resume_2024-10.docx`) → `Personal/Career/`
- Candidate resumes → `Careerspan/resumes/` (if not already there)
- Sample resumes subfolder (3 files) → delete (generic samples)
- **Action:** Relocate V's files, check Careerspan for dupes, delete rest

### `Documents/_ARCHIVE_2025-10/` — KEEP (already archived)
- **17 files, 0.41 MB** — Meeting transcripts + orchestrator migration docs from Oct 2025
- This IS the archive — it's doing its job
- **Action:** Keep as-is

### `Documents/Contracts/` — KEEP
- **1 file, 0.12 MB** — Laura Close advisor proposal (unsigned)
- Legal document with potential future relevance
- **Action:** Keep

### `Documents/Imported/` — DELETE
- **1 file, 0.11 MB** — `sofia_meeting.txt` from Oct 2025
- One-off import, likely processed elsewhere
- **Action:** Delete

### `Documents/Social/` — ARCHIVE
- **7 files, 0.02 MB** — GTM post drafts and panel drafts from Oct 2025
- Some may have reusable angles for future content
- **Action:** Move to `Documents/Archive/2025-10-social-drafts/`

### `Documents/ZoDrops/` — DELETE
- **2 files, 0.02 MB** — Streaming player setup doc + README from Oct 2025
- Likely obsolete feature exploration
- **Action:** Delete

### `Documents/Legal/` — KEEP
- **2 files, 0.01 MB** — Commercial license + NDA template
- Templates have ongoing utility
- **Action:** Keep

### `Documents/N5-Development/` — DELETE
- **1 file, 0.01 MB** — Networking event processor spec from Oct 2025
- **Action:** Delete

### `Documents/Proposals/` — REVIEW-THEN-DELETE
- **1 file, 0.01 MB** — Marvin Ventures partnership proposal
- **Action:** Check if this relationship is still active. Delete if dead.

### `Documents/Backups/` — DELETE
- **1 file + 1 subfolder, ~0 KB** — index.jsonl registry fix backup from Oct 2025
- **Action:** Delete (registry has moved on)

### `Documents/Pricing/` — REVIEW-THEN-DELETE
- **1 file, ~0 KB** — `founder-os-pricing.md`
- **Action:** Check if pricing is captured elsewhere. If so, delete.

### `Documents/Runbooks/` — KEEP or RELOCATE
- **2 files, ~0 KB** — Zo bridge MVP checklist + clone kit checklist
- May still be operationally relevant
- **Action:** If still used, keep. If obsolete, delete.

### `Documents/System/evaluations/` — DELETE
- **1 file, 0.01 MB** — Just a README
- **Action:** Delete empty scaffolding

### `Documents/System/migration-reports/` — KEEP
- **1 file** — N5 realignment report from Oct 2025
- Historical record of system migration
- **Action:** Keep

### `Documents/Deliverables/ConversationalAPI_Package/` — DELETE
- **3 files, 0.01 MB** — Install script + README for a demo package
- Old deliverable, likely shipped
- **Action:** Delete

### `Documents/Deliverables/proposals_pricing/` — DELETE
- **1 file, ~0 KB** — Oct 2025 pricing proposal
- **Action:** Delete

---

## TIER 3 — Inbox Snapshots (biggest space savings)

The `Inbox/` contains **~340 MB** across 60+ dated snapshot directories. Most are system migration artifacts from Oct-Dec 2025.

### Massive duplicates — DELETE (reclaims ~290 MB)

| Path | Size | Files | Notes |
|------|------|-------|-------|
| `Inbox/20251031-131643_Sites` | 138 MB | 1,610 | Duplicate site snapshot |
| `Inbox/20251031-131638_n5-waitlist-backup` | 138 MB | 1,610 | Duplicate waitlist backup |
| `Inbox/20251030-132306_Sites` | 7.9 MB | 1,033 | Older site snapshot |
| `Inbox/20251103-041837_Sites` | 7.9 MB | 1,035 | Another site snapshot |

### Trash snapshots — DELETE (reclaims ~5 MB)

All `*_Trash` folders are point-in-time trash captures during migrations. No reason to keep trash-of-trash.

| Path | Files |
|------|-------|
| `Inbox/20251028-131721_Trash` | 9 |
| `Inbox/20251029-131651_Trash` | 3 |
| `Inbox/20251031-131646_Trash` | 5 |
| `Inbox/20251101-131632_Trash` | 23 |
| `Inbox/20251102-141647_Trash` | 3 |
| `Inbox/20251103-041844_Trash` | 2 |
| `Inbox/20251103-093347_Trash` | 3 |
| `Inbox/20251105-095006_Trash` | 199 |
| `Inbox/20251106-093637_Trash` | 14 |
| `Inbox/20251108-093530_Trash` | 15 |
| `Inbox/20251109-093358_Trash` | 1 |
| `Inbox/20251110-093321_Trash` | 117 |
| `Inbox/20251117-093332_Trash` | 91 |
| `Inbox/20251124-093245_Trash` | 1 |
| `Inbox/20251126-093220_Trash` | 6 |
| `Inbox/20251127-093158_Trash` | 2 |
| `Inbox/20251203-093412_Trash` | 26 |

### Duplicate/obsolete system snapshots — DELETE

| Path | Size | Files | Notes |
|------|------|-------|-------|
| `Inbox/20251117-093331_webhook-receiver` | 2.6 MB | 628 | Duplicated by `20251213` version |
| `Inbox/20251213-093159_webhook-receiver` | 2.6 MB | 628 | Both can go — webhook-receiver lives in canonical location |
| `Inbox/20251130-093826__local_archives` | 1 MB | 159 | Duplicated |
| `Inbox/20251202-093206__local_archives` | 1 MB | 159 | Duplicated |
| `Inbox/20251028-131721_logs` | ~0 | 1 | Stale log |
| `Inbox/20251030-132311_marvin_jobs_data` | ~0 | 3 | Duplicated by `20251031` |
| `Inbox/20251031-131646_marvin_jobs_data` | ~0 | 4 | Both can go |
| `Inbox/20251031-131638_Deliverables` | ~0 | 1 | Single debug report |
| `Inbox/20251027-132323_n5-waitlist` | ~0 | 1 | Single file |
| `Inbox/20251031-131638_n5-waitlist-backup` | 138 MB | 1,610 | Full backup, redundant |

### Phase transfer artifacts — REVIEW-THEN-DELETE

These are N5 OS migration phase exports. They've been consumed. Spot-check one, then delete all:

- `Inbox/20251028-132904_phase0.5_transfer` (15 files)
- `Inbox/20251028-132904_phase1_transfer` (10 files)
- `Inbox/20251028-132904_phase2_transfer` (10 files)
- `Inbox/20251028-131721_phase3_transfer` (11 files)
- `Inbox/20251028-131721_phase4_transfer` (9 files)
- `Inbox/20251028-132859_phase5_transfer` (12 files)
- `Inbox/20251028-132904_N5_OS_Core_Artifacts` (10 files)
- `Inbox/20251029-131651_N5_OS_Core_Artifacts` (7 files)
- `Inbox/20251029-132500_N5_Artifacts_For_Download` (7 files)

### Other Inbox stale dirs — REVIEW-THEN-DELETE

| Path | Files | Notes |
|------|-------|-------|
| `Inbox/20251030-132311_Projects` | 14 | Old project snapshot |
| `Inbox/20251101-131632_Archive` | 14 | Archive snapshot |
| `Inbox/20251103-093347_Intelligence` | 87 | Intelligence snapshot |
| `Inbox/20251105-095007_Intelligence` | 135 | Intelligence snapshot |
| `Inbox/20251105-095006_Reports` | 2 | Old reports |
| `Inbox/20251116-095237_Archives` | 12 | Archive snapshot |
| `Inbox/20251118-093542_Integrations` | 12 | Old integration snapshot |
| `Inbox/20251120-093554_Integrations` | 28 | Old integration snapshot |
| `Inbox/20251202-093206_Integrations` | 4 | Old integration snapshot |
| `Inbox/20251211-093323_Integrations` | 0 | Empty |
| `Inbox/20251213-093159_Integrations` | 14 | Old integration snapshot |
| `Inbox/20251202-093206_Exports` | 7 | Old export |
| `Inbox/20251202-093206_TutorSandboxes` | 2 | Old sandbox |
| `Inbox/20251202-093206_Logs` | 4 | Old logs |
| `Inbox/20251029-132500_Meetings` | 684 | Old meetings snapshot — canonical is `Personal/Meetings/` |
| `Inbox/meetings_cleanup_20251112_051310` | varies | Cleanup staging artifact |
| `Inbox/con_GTWiYRhnrQ1nUKZO_extracted` | varies | Conversation extraction artifact |
| `Inbox/Zorg_Case_Files` | varies | Old Zorg case files |

---

## Execution Order

1. **Empty dirs** — delete immediately (zero risk)
2. **Inbox `*_Trash` dirs** — delete immediately (trash-of-trash)
3. **Inbox large duplicates** (Sites, waitlist, webhook-receiver) — delete (reclaims ~290 MB)
4. **Records/stakeholder_discovery** — delete (440 junk files)
5. **Remaining Tier 2 DELETEs** — batch delete
6. **RELOCATEs** (Resumes, Company/Technology) — move then delete source
7. **REVIEW-THEN-DELETEs** — V spot-checks, then we delete
8. **Remaining Inbox snapshots** — batch delete after confirmation

---

## What We're NOT Touching

- `N5/` — system infrastructure (protected)
- `Sites/` — production websites (protected)
- `Personal/` — personal data (protected)
- `Skills/` — deployed skills (protected)
- `Knowledge/` — curated knowledge (protected)
- `Integrations/` — service connections (protected)
- `Zo/` — identity space (protected)
- `Documents/Contracts/` — legal docs (keep)
- `Documents/Legal/` — templates (keep)
- `Documents/_ARCHIVE_2025-10/` — already archived (keep)
- `Careerspan/` — active pipeline (keep, only empty subdirs flagged)

---

## Execution Results (2026-02-14 00:40 ET)

**Status: COMPLETE** — All planned actions executed.

### Space Reclaimed
- **Inbox:** ~340 MB → 14 MB (reclaimed ~326 MB)
- **Records:** partial cleanup (stakeholder_discovery, Archive, Personal, Company subdirs deleted; meetings relocated)
- **Documents:** stale folders deleted/archived; Resumes relocated
- **Empty dirs:** 14 removed across Research/, Documents/, Careerspan/, Build Exports/

### Actions Taken

| Step | Action | Details |
|------|--------|---------|
| 1 | Empty dirs deleted | 14 folders (Documents/Meetings, Research/*, Careerspan empties, Build Exports empties) |
| 2 | Inbox trash snapshots | 17 `*_Trash` folders deleted (~21 MB) |
| 3 | Inbox large duplicates | 4 Site/waitlist snapshots deleted (~292 MB) |
| 4 | Inbox misc duplicates | 9 folders (webhook-receiver, local_archives, marvin, etc.) |
| 5 | Records cleanup | stakeholder_discovery (440 files), Archive, Reflections, Company/Proposals, Personal/drafts, Personal/notes, Company/voice-memos |
| 6 | Documents cleanup | Imported, ZoDrops, N5-Development, Backups, System/evaluations, Deliverables/* |
| 7 | Inbox phase transfers | 9 phase transfer artifact folders deleted |
| 8 | Inbox remaining snapshots | Projects, Intelligence, Archives, Integrations, Meetings, misc — 18 folders deleted |
| 9 | Old Deliverables + duplicate Heather staging | 2 more Inbox folders deleted |

### Relocations

| Source | Destination | Files |
|--------|-------------|-------|
| Documents/Resumes (V's resumes) | Personal/Career/ | 2 |
| Documents/Resumes (candidate resumes) | Careerspan/resumes/inbox/ | 9 |
| Records/Company/Technology/ (PDFs) | Knowledge/content-library/personal/ | 2 |
| Records/meetings/ (9 meeting dirs) | Personal/Meetings/ | 9 dirs |

### Archives Created

| Source | Archive Location |
|--------|-----------------|
| Documents/Social/ | Documents/Archive/2025-10-social-drafts/ |
| Documents/Proposals/ + Documents/Pricing/ | Documents/Archive/2025-10-proposals/ |

### Not Cleaned (out of original scope)

- `Records/AARs/` — 63 files, recent content (Jan 2026)
- `Records/reflections/` — 726 files, recent content
- `Records/Temporary/` — 250 files, recent worker assignments
- `Records/external_sessions/`, `conversations/`, `productivity-philosophy/` — small, recent
- `Inbox/` 4 remaining meeting staging dirs (Mihir, Maria, CK) — not yet canonicalized
- All protected roots unchanged