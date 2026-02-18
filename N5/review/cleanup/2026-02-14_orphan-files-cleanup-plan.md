---
created: 2026-02-14
last_edited: 2026-02-14
version: 1.0
provenance: con_oSMgpCG0LKXFengK
---

# Orphan Files & Outdated Archives Cleanup Plan

**Scan date:** 2026-02-14
**Scope:** All files outside canonical folder structures — root-level orphans, outdated archives, temp files, misplaced paths, duplicate files

---

## Summary

| Category | Items | Reclaimable |
|----------|------:|------------:|
| Top-level orphan directories | 8 | ~293 MB |
| Top-level orphan files | 7 | ~0.1 MB |
| Outdated archives (deletable) | 8 | ~90 MB |
| Duplicate files | 2 pairs | ~15 MB |
| Misplaced paths | 2 | ~2 MB |
| Stale large files | 5 | ~9 MB |
| Project backups | 2 dirs | ~0.8 MB |
| **Total reclaimable** | | **~410 MB** |

---

## Tier 1: DELETE (zero/low risk)

### 1A. Top-level orphan files at workspace root

These are scratch artifacts from past conversations — no canonical home.

| File | Size | Date | Action |
|------|------|------|--------|
| `gdrive_folder_files_list.txt` | 91 KB | Feb 12 | DELETE — one-off GDrive listing |
| `productivity_tracker.db` | 0 KB | Feb 12 | DELETE — empty database |
| `README.md` (root) | 1 KB | Dec 26 | DELETE — generic readme, not meaningful |
| `bridge-test-from-zoputer.md` | 0.1 KB | Feb 12 | DELETE — test artifact |
| `entity_extraction.json` | 3 KB | Feb 11 | DELETE — one-off extraction output |
| `entity_extraction_teamwork.json` | 3 KB | Feb 11 | DELETE — one-off extraction output |
| `N5_BOOTSTRAP_MONITOR.log` | 0 KB | Feb 14 | DELETE — empty log |

### 1B. Duplicate files in Images/

Confirmed identical by md5sum:

| Original | Duplicate | Size | Action |
|----------|-----------|------|--------|
| `Images/Xnip2025-09-20_06-08-37.jpg` | `Images/Xnip2025-09-20_06-08-37 (1).jpg` | 1.83 MB | DELETE duplicate |
| `Images/20251202-093206_Zo_Pinned Folder Glitch.gif` | `Images/20251202-093206_Zo_Pinned Folder Glitch (1).gif` | 13.2 MB | DELETE duplicate |

### 1C. Misplaced paths

| Path | Issue | Action |
|------|-------|--------|
| `Personal/home/workspace/Datasets/linkedin-full-pre-jan-10/` | Full absolute path accidentally nested | DELETE — canonical copy exists at `Datasets/linkedin-full-pre-jan-10/` |
| `Personal/home/workspace/linkedin-profile-articles-pre-jan-9/` | Same issue | DELETE — canonical copy at `Datasets/linkedin-profile-articles-pre-jan-9/` |

### 1D. Project backup dirs

| Path | Size | Action |
|------|------|--------|
| `Projects/zo-meeting-ingestion.backup.20260205_210630/` | 479 KB | DELETE — canonical is in `Skills/` or `Projects/zo-meeting-ingestion/` |
| `Projects/zo-meeting-ingestion.backup.20260205_210921/` | 334 KB | DELETE — same |

### 1E. Outdated archives

| Archive | Size | Date | Action |
|---------|------|------|--------|
| `Backups/Meetings/pre-v3-migration-20260209-101434/personal-meetings-backup.tar.gz` | 17.7 MB | Feb 9 | DELETE — v3 migration complete, `Personal/Meetings/` is canonical |
| `Inbox/meeting-ingestion-zo.zip` | 0.2 MB | Feb 5 | DELETE — old ingestion artifact |
| `Inbox/downloaded_file_con_GTWiYRhnrQ1nUKZO.zip` | 0.05 MB | Dec 21 | DELETE — orphaned conversation download |
| `Inbox/20251029-132500_n5_artifacts.tar.gz` | 0.02 MB | Oct 28 | DELETE — old N5 artifact snapshot |
| `Documents/Deliverables/ConversationalAPI_Package.tar.gz` | 0.004 MB | Oct 21 | DELETE — ancient, superseded |
| `Documents/Deliverables/Vibe_Personas_Package.zip` | 0.02 MB | Dec 11 | DELETE — superseded by v3 |
| `Documents/Deliverables/Vibe_Personas_Package_v3.zip` | 0.01 MB | Dec 11 | DELETE — old export |
| `Documents/Vibe_Personas_for_Zo_Discover.zip` | 0.01 MB | Dec 28 | DELETE — old export |

---

## Tier 2: REVIEW-THEN-DELETE or RELOCATE

### 2A. Top-level orphan directories

| Directory | Size | Files | Last Modified | Recommendation |
|-----------|------|-------|---------------|----------------|
| `Services/umami/` | 2.1 GB (1.7 GB node_modules) | 4762 | Jan 16 | **KEEP** — registered service (port 8764). But consider: do you still use Umami analytics? If not, deregister service + delete = 2.1 GB saved |
| `Backups/` | 67 MB | 6860 | Feb 9 | **DELETE Meetings/ subdir** (17.7 MB, migration done). Check if anything else is useful |
| `Careerspan/` | 48 MB | 227 | Feb 14 | **KEEP** — active pipeline data |
| `Projects/` | 5.8 MB | 213 | Feb 12 | **KEEP active, DELETE backups** — `x-thought-leader` and `zo-meeting-ingestion` are active. Delete the 2 `.backup.*` dirs |
| `string/` | 0.27 MB | 26 | Feb 11 | **REVIEW** — looks like a cloned web app repo with its own `.git`. Registered as service `string` (tcp:8000). Is this active? |
| `Clients/Guickly/` | 0.45 MB | 15 | Feb 3 | **KEEP** — active client work |
| `Lists/` | 0.16 MB | 60 | Jan 27 | **KEEP** — has POLICY.md, actively used by N5 |
| `Scratch/` | 0.09 MB | 18 | Jan 15 | **RELOCATE or DELETE** — Careerspan target lists from Jan. If still needed, move to `Careerspan/research/`. Otherwise delete |
| `Drafts/Social/Jobs/` | 0.07 MB | 20 | Dec 21 | **DELETE** — old Dec 2025 job board drafts, all stale |
| `Travel Wrapped/` | 0.01 MB | 2 | Dec 26 | **DELETE** — one-off Dec 2025 project, likely superseded or abandoned |
| `Temp/` | 0.04 MB | 2 | Feb 13 | **REVIEW** — has recent David Careerspan transcript (Feb 12). Move to `Careerspan/` if needed, then delete `Temp/` |
| `Logs/` | 0.003 MB | 2 | Feb 12 | **DELETE** — zoputer-sanitizer smoke test logs, not canonical log location |

### 2B. Stale large files in Images/

| File | Size | Date | Recommendation |
|------|------|------|----------------|
| `Images/placeholder-fix-architecture.png` | 2.09 MB | Oct 21 | DELETE — old N5 architecture placeholder |
| `Images/n5_os_final_architecture.png` | 1.98 MB | Oct 21 | KEEP — could be useful reference |
| `Images/n5_bootstrap_architecture.png` | 1.74 MB | Oct 21 | DELETE — superseded by final |
| `Images/meeting_monitor_impact_map.png` | 1.47 MB | Oct 21 | DELETE — old meeting system diagram |
| `Images/meeting_system_architecture.png` | 1.45 MB | Oct 21 | DELETE — old meeting system diagram |
| `Images/n5_architecture_relationships.png` | 1.46 MB | Oct 21 | DELETE — old diagram |

### 2C. Build Exports

| Directory | Size | Files | Recommendation |
|-----------|------|-------|----------------|
| `Build Exports/n5os-ode/` | 2.7 MB | ~600 | REVIEW — N5OS export snapshot. Still useful? |
| `Build Exports/n5os-ode-backup-pre-merge/` | 2.4 MB | ~600 | DELETE — pre-merge backup of the above |
| `Build Exports/n5-os-zo-persona-optimization/` | 228 KB | ~40 | DELETE — old build export |
| `Build Exports/Exports/` | 39 KB | ~5 | DELETE — nested empty-ish exports dir |

### 2D. N5/backups/ (inside protected N5/)

| Archive | Size | Date | Recommendation |
|---------|------|------|----------------|
| `N5/backups/threads_archive_oct11-12.tar.gz` | 0.28 MB | Oct 14 | DELETE — ancient thread archive |
| `N5/backups/consolidation_20251226.zip` | 0.24 MB | Dec 26 | DELETE — old consolidation |
| `N5/backups/migration_backups_20251014_051335.tar.gz` | 0.13 MB | Oct 14 | DELETE — old migration |
| `N5/backups/backup-py-2.tar.gz` | 0.004 MB | Oct 2 | DELETE — test backup |
| `N5/backups/backup-py-test.tar.gz` | 0.002 MB | Oct 2 | DELETE — test backup |
| `N5/backups/secrets-migration-20251026/` | tiny | Oct 27 | **CAUTION** — contains a credentials backup. Verify secrets were migrated, then delete |

---

## Tier 3: BIG WINS (require your decision)

### 3A. Services/umami/ — 2.1 GB

Umami is a self-hosted web analytics platform. It's registered as a service on port 8764.
- **If actively used:** Keep, no action
- **If not used anymore:** Deregister service + delete folder = **2.1 GB reclaimed**

### 3B. Backups/ top-level directory (67 MB)

After deleting the Meetings subdir, check what else is in `Backups/`. This is a non-canonical location — N5/backups/ is the system backup location.

---

## NOT TOUCHING

- `Careerspan/` — active pipeline
- `Clients/` — active client work  
- `Lists/` — N5 managed, has POLICY.md
- `Projects/x-thought-leader/` — active project
- `Projects/prediction-markets/` — recent project
- All protected roots (N5/, Sites/, Personal/, Skills/, Knowledge/, Integrations/, Zo/)
- `.config/syncthing/` — system config, actively used
- N5/data/bundles/ — consulting stack bundles, actively used

---

## GitHub Tools for Agentic Cleanup

**Most relevant find:** [taylorwilsdon/reclaimed](https://github.com/taylorwilsdon/reclaimed) — disk space cleanup tool for macOS/Linux/Windows, built with agentic dev tools. Focused on disk utilization and cleanup recommendations.

**Other options considered but less relevant:**
- Most "agentic file cleanup" repos are general AI agent frameworks (Agent Zero, BabyCommandAGI) not purpose-built for filesystem cleanup
- The Reddit thread on r/LocalLLaMA mentions local-first content-aware file organization tools, but they're desktop-focused (Downloads folder sorting)

**Assessment:** For your use case (Zo workspace with semantic meaning in folder structures), the custom scan scripts we're running are actually more appropriate than generic tools. A generic cleanup tool doesn't understand N5OS conventions, protected paths, or canonical locations. The agentic value comes from *us* understanding your system architecture while scanning.
