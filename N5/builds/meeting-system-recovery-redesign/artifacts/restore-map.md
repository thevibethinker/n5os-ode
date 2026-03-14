---
created: 2026-03-10
last_edited: 2026-03-10
version: 1.0
provenance: con_2SbqZ8FwPcUBk4VX
---

# Restore Map

## Scope

This report inventories the approved recovery source `file '/home/.z/chat-uploads/Zo Meetings copy-e49d20a9b948.zip'` and maps what should be restored, normalized, quarantined, or ignored during a later execution phase.

This is a planning-only artifact. No files were restored into `file 'Personal/Meetings/'` and no sqlite state was mutated.

## Inputs Reviewed

- `file '/home/.z/chat-uploads/Zo Meetings copy-e49d20a9b948.zip'`
- `file 'N5/builds/meeting-system-recovery-redesign/PLAN.md'`
- `file 'N5/docs/meeting-system-reference.md'`
- zip-internal samples from root `README.md`, week folders, Archive folders, quarantine folders, and `PROCESSING_LOG.jsonl`

## Executive Read

The zip is not a clean snapshot of the current canonical meeting system. It is a mixed historical corpus containing at least four distinct state families:

1. raw-ish `Inbox/` transcript intake
2. processed `Week-of-*` meeting folders
3. archived processed folders under `Archive/2025-Q3` and `Archive/2025-Q4`
4. exceptional/problematic items under `_quarantine/`

It also contains operational reports, transition documents, logs, manifests, and hidden/system files.

## Coverage

### Real-content date coverage

- **Earliest meaningful artifact date:** `2024-09-03`
- **Latest meaningful artifact date:** `2026-01-19`
- **Distinct content dates detected:** `81`
- **Week-folder coverage window:** `2025-08-25` through `2026-01-19`
- **Observed week folders:** `21`

### Important interpretation

The earliest date (`2024-09-03`) appears in `_quarantine/`, not in the main processed weekly corpus. That means the zip contains older evidence, but the stable processed corpus appears to begin in late Q3 2025.

### Coverage boundaries by structure

| Structure | Earliest observed date | Latest observed date | Notes |
|---|---:|---:|---|
| `Inbox/` | 2025-08-26 | 2025-11-03 | Mostly transcript intake files, many pre-normalization names |
| `Week-of-*` | 2025-08-25 | 2026-01-19 | Main processed working corpus |
| `Archive/` | 2025-09-03 | 2025-11-21 | Quarter-bucketed processed/archive state |
| `_quarantine/` | 2024-09-03 | 2025-11-13 | Exception bucket; includes old and malformed items |
| root logs/docs | 2025-10-30 | 2026-01-19 | Operational evidence, not restore targets |

## Structural Inventory

### Top-level artifact families

| Family | Count | What it implies |
|---|---:|---|
| `week-file` | 3535 | Rich processed meeting content lives inside week folders |
| `week-folder` | 240 | Week folders plus per-meeting directories within them |
| `archive` | 718 | Significant processed corpus already moved to archive buckets |
| `quarantine` | 433 | Large exception surface; not safe to bulk-restore blindly |
| `inbox` | 281 | Raw or lightly normalized transcript intake corpus |
| `operational-doc` | 30 | Execution reports, workflow docs, summaries |
| `log` | 2 | Processing evidence only |
| `manifest` | 1 | Root-level manifest list only |
| `hidden` + `ignore` | 19 | Finder/system noise |

### Week-folder corpus characteristics

Representative processed week folders include:

- `Week-of-2025-09-01/2025-09-04_Jacob-bank-relay-Educational/`
- `Week-of-2025-11-24/2025-11-26_Holly-Sanders-And-Vrijen-Attawar/`
- `Week-of-2026-01-12/...`

Common files inside processed meeting folders:

- `transcript.jsonl`
- `manifest.json`
- `metadata.json` on some later-source meetings
- `B01_DETAILED_RECAP.md`
- `B03_DECISIONS.md`
- `B05_ACTION_ITEMS.md`
- `B06_BUSINESS_CONTEXT.md`
- `B07_TONE_AND_CONTEXT.md`
- `B14_BLURBS*.md`
- `B21_KEY_MOMENTS.md`
- `B25_DELIVERABLES.md`
- `B26_MEETING_METADATA*.md`
- `INTRO_*.md` for intro workflows
- `.processed` markers in some folders

The week-folder corpus is therefore the clearest evidence of the mature processed-meeting state model.

### Archive corpus characteristics

Archive content lives under quarter buckets:

- `Archive/2025-Q3/`
- `Archive/2025-Q4/`

Representative archive folder names include processed-state suffixes like `_[P]`, for example:

- `2025-09-03_Strategy_Meeting_Signal_Intelligence_[P]/`
- `2025-11-14_Vrijen_Attawar_Kai_Song_[P]/`
- `2025-11-13_Aaron-Mak-Hoffman_Vrijen-Attawar_[P]/`

This suggests the historical system used filesystem state suffixes as execution markers, while the newer canonical reference now points to `Personal/Meetings/` without requiring the old week/archive structure as the future target layout.

### Inbox corpus characteristics

`Inbox/` contains pre-normalized transcript files such as:

- `Alex_x_Vrijen_Wisdom_Partners_Coaching-...transcript.md`
- `Daily team stand-up-...transcript.md`
- `Plaud Note_10-31 ...transcript.md`

Interpretation:

- `Inbox/` is evidence of source intake history
- it is not the best source for restoring already-processed meetings when a fuller processed version exists elsewhere
- it may be useful for gap-filling when processed folders are missing or incomplete

### Quarantine corpus characteristics

- **Quarantine folder count:** `45`
- contents include mostly markdown block outputs (`.md`), plus a few `.json`, one `.docx`, and one `.pre-backfill`
- representative folders include:
  - `2024-09-03_HealthTech-SurgicalIntelligence_external/`
  - `2025-11-03_Plaud-VrijenaAI-Workflow_technical/`
  - `2025-11-04_Vrijen-SecondShift_Networking/`

Interpretation:

- quarantine contains substantive meeting evidence
- but it is explicitly a failure/exception lane
- it should not be merged into canonical live state without per-item adjudication

### Operational evidence artifacts

Root-level docs and logs include:

- `PROCESSING_LOG.jsonl`
- `rename_log.jsonl`
- `meetings_m_manifests.txt`
- `MG*_EXECUTION_REPORT*.md`
- transition and analysis docs
- root `README.md` describing the historical MG pipeline and filesystem state machine

These are useful for system archaeology, but not restore targets.

## Restore class matrix

### Restore class definitions

| Restore class | Meaning |
|---|---|
| **restore** | eligible to become canonical recovered meeting content |
| **normalize** | keep content, but transform layout/state markers before restore |
| **quarantine** | preserve outside canonical corpus pending review |
| **ignore** | do not restore; retain only as audit evidence |

### Restore class by artifact family

| Artifact family | Restore class | Rationale | Proposed target in later execution |
|---|---|---|---|
| Processed week-folder meeting directories | **restore + normalize** | richest source of meeting content and block outputs | normalize into canonical `Personal/Meetings/<meeting-id>/` layout with provenance |
| Archive processed meeting directories with `_[P]` | **restore + normalize** | valid processed history, but stateful/historical path model should not be copied verbatim | restore content, strip/archive-state suffixes, preserve prior state in metadata |
| `Inbox/` raw transcript files with no richer processed counterpart | **normalize** | valuable source material, but not canonical processed state | convert into canonical intake-ready structure or staged recovery inbox |
| `_quarantine/` meeting folders | **quarantine** | explicit exception lane; mixed quality and naming hygiene | restore to separate recovery quarantine area only, not canonical corpus |
| Root processing logs and rename logs | **ignore** | evidence for audit and debugging only | keep external to restored corpus |
| Root operational reports / transition docs / summaries | **ignore** | describe system operation, not meeting records | retain as build evidence only |
| Hidden files (`.DS_Store`, `.stfolder`) | **ignore** | system noise | none |
| Protection marker `.n5protected` | **ignore** for corpus restore, **retain** as provenance evidence | not meeting content | note in provenance, do not copy as meeting data |

## DP-1: Week-folder structure — source truth or evidence?

**Recommendation:** treat historical `Week-of-*` structure as **evidence, not future source truth**.

### Why

- the canonical reference points to `Personal/Meetings/` as the long-term home
- the zip shows multiple historical storage models coexisting at once: Inbox, Week-of, Archive, quarantine, and filesystem suffix states
- copying week-folder layout directly would preserve historical operational scaffolding, not a cleaned canonical meeting corpus

### Practical conclusion

- use week folders as the **best recovery source for content selection and chronology**
- do **not** adopt `Week-of-*` as the future canonical storage contract unless Wave 2 explicitly decides that grouping remains operationally valuable

## DP-2: Which artifact classes should be excluded from restore?

### Exclude from canonical restore

1. hidden/system files
2. operational reports and execution summaries
3. processing logs and rename logs
4. root workflow docs and transition notes
5. quarantine items from automatic restore

### Conditionally exclude from first-pass restore

1. duplicate raw Inbox transcripts when a fuller processed meeting directory exists
2. archive/processed folders with malformed dates or ambiguous IDs until normalization rules are finalized
3. partial or sparse processed folders that fail minimum-content checks

## Historical state model mismatch

The zip clearly implies an older filesystem-driven state machine:

- raw Intake in `Inbox/`
- manifest stage `_[M]`
- processed/archive stage `_[P]`
- quarter archive buckets
- explicit `.processed` sentinels in some meeting folders

The current reference system is simpler and canonicalized under `Personal/Meetings/`. That means restore should be a **migration**, not a byte-for-byte replay.

## Proposed restore targets for later execution

| Source family | Later execution target | Notes |
|---|---|---|
| processed week folders | `Personal/Meetings/<normalized-meeting-id>/` | main recovery path |
| archived `_[P]` folders | `Personal/Meetings/<normalized-meeting-id>/` or `Personal/Meetings/Archive/<...>` depending on final execution plan | preserve prior archive status in metadata |
| raw Inbox-only items | `Personal/Meetings/Inbox/<staged-item>/` | only when no richer processed artifact exists |
| quarantine items | separate recovery quarantine area, not live canonical corpus | likely under build-owned recovery staging, not `Personal/Meetings/` first pass |

## Provenance requirements for recovered items

Recovered items should carry source lineage into normalized state.

### Minimum provenance payload per restored meeting

- `recovery_source`: zip file path/name
- `recovery_drop`: `D1.1`
- `original_zip_path`: exact internal zip path used for restore
- `original_state_family`: `week`, `archive`, `inbox`, or `quarantine`
- `original_state_marker`: e.g. `_[P]`, `_[M]`, `.processed`, or `none`
- `restored_at`: execution timestamp from the later mutation wave
- `restored_by_build`: `meeting-system-recovery-redesign`

### Why this matters

This keeps recovered state auditable and allows later comparison between restored canonical content and the historical layout model inside the zip.

## Risks and trap doors

### Risk 1 — duplicate meetings across families

The same meeting may exist in Inbox, Week-of, Archive, and/or quarantine. Restore must deduplicate by meeting identity, not by filename alone.

### Risk 2 — state suffixes encode workflow history

Folders like `_[P]` and `_[M]` encode pipeline state. Blindly preserving them in canonical names would import historical process mechanics into the future information model.

### Risk 3 — quarantine contains real content

Quarantine is not trash. It contains meaningful meeting outputs, including full block sets. It needs controlled review, not deletion.

### Risk 4 — archive buckets may be better than week folders for some dates

Some Q3/Q4 content may only exist in Archive or may be more complete there. Execution must compare source families before choosing the recovery winner.

### Risk 5 — metadata richness changes over time

Later meetings include `metadata.json` from source systems like Fireflies, while earlier folders may rely more heavily on manifest/block content. Normalization must tolerate both shapes.

## Proposed execution heuristics for later drops

1. Prefer the richest processed artifact available for a meeting.
2. Rank source families roughly as: complete processed week/archive folder > partial processed folder > Inbox transcript-only item.
3. Never auto-promote quarantine into canonical corpus.
4. Preserve all historical source paths in provenance metadata.
5. Normalize names and remove historical execution suffixes before final placement.

## Recommendation summary

- Treat the zip as a **mixed historical evidence corpus**, not a direct filesystem template.
- Use processed week/archive directories as the main restore source.
- Treat `Inbox/` as gap-fill input, not primary canonical restore source.
- Keep `_quarantine/` out of automatic canonical restore.
- Carry explicit provenance on every recovered item.

## Verification notes

- Coverage boundaries identified from real artifact paths, not zip timestamp alone.
- Restore classes are explicit for each major artifact family.
- This drop performed no restore into live meeting paths.
