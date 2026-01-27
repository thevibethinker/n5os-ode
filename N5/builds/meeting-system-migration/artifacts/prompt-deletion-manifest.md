---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_jET6XAvuruJlsxOH
---

# Prompt Deletion Manifest - Meeting System Migration

## Executive Summary

This document catalogs all meeting-related prompts and their disposition as part of the migration to the unified `meeting-ingestion` skill.

**Total Prompts Audited:** 17
**DELETE (Safe Now):** 2
**DELETE_AFTER_MIGRATION:** 4
**KEEP (Active/Reference):** 5
**ARCHIVE (Historical):** 6

---

## DELETE (Safe to Delete Now)

These prompts are no longer used and have been fully replaced by the `meeting-ingestion` skill.

| Path | Reason | Replacement |
|------|---------|-------------|
| `Prompts/Meeting Blurb Generation.prompt.md` | Replaced by Zo Take Heed system (2026-01-19) | `Skills/meeting-ingestion/` |
| `Prompts/Meeting_Block_Selector.prompt.md` | Replaced by meeting-ingestion skill's manifest generation | `Skills/meeting-ingestion/scripts/processor.py` |

---

## DELETE_AFTER_MIGRATION (Agent-Dependent)

These prompts are still used by active scheduled agents (MG-1, MG-2, MG-4, MG-6). They can only be deleted **after** the agents are migrated to use the skill.

| Path | Reason | Blocked By | Agent |
|------|---------|-------------|--------|
| `Prompts/Meeting Manifest Generation.prompt.md` | Used by MG-1 agent to generate manifests | Agent `0c53b7ba` (Meeting Manifest Generation Workflow Execution) | MG-1 |
| `Prompts/Meeting Block Generation.prompt.md` | Used by MG-2 agent to generate intelligence blocks | Agent `0a08e6a8` (Meeting Intelligence Generation Report) | MG-2 |
| `Prompts/Meeting Warm Intro Generation.prompt.md` | Used by MG-4 agent to generate warm intro emails | Agent `ce6995b8` (Meeting Warm Intro Email Drafts) | MG-4 |
| `Prompts/Meeting State Transition.prompt.md` | Used by MG-6 agent to transition meeting states | Agent `f339ca26` (Meeting State Transition: intelligence_generated to processed) | MG-6 |

**Note:** `Prompts/Meeting Follow-Up Generation.prompt.md` (MG-5) is also still active but the associated agent (`5579f899`) is deprecated. Status: pending review during D3.1.

---

## KEEP (Active or Reference)

These prompts are either still actively used or serve as reference documentation.

| Path | Reason | Notes |
|------|---------|-------|
| `Prompts/Internal Meeting Process.prompt.md` | Reference document for MECEM principles and B40-B48 blocks | Referenced by `Skills/meeting-ingestion/references/legacy_prompts.md` |
| `Prompts/Meeting Prep Digest.prompt.md` | Active command: `meeting-prep-digest` | Still used for daily meeting prep with calendar integration |
| `Prompts/Blocks/Generate_B*.prompt.md` (B00-B48) | Block generators used by `processor.py` | Required by meeting-ingestion skill |
| `N5/workflows/meeting_pipeline_registry.md` | Historical reference for MG-1 → MG-7 pipeline | Keep for documentation of legacy system |

---

## ARCHIVE (Historical Value)

These prompts are already in the `Prompts/Archive/meetings_legacy/` folder and have historical value.

| Path | Reason |
|------|---------|
| `Prompts/Archive/meetings_legacy/Meeting Auto Process.prompt.md` | Legacy auto-process workflow |
| `Prompts/Archive/meetings_legacy/Meeting State Transition.prompt.md` | Duplicate legacy version |
| `Prompts/Archive/meetings_legacy/Meeting Auto Processor.prompt.md` | Legacy processor |
| `Prompts/Archive/meetings_legacy/Meeting Mark C-State.prompt.md` | Legacy state marking |
| `Prompts/Archive/meetings_legacy/Meeting Archive.prompt.md` | Legacy archiver (deprecated as mover, now read-only reference) |
| `Prompts/Archive/meetings_legacy/meeting-placement-cleanup.prompt.md` | Legacy cleanup |
| `N5/workflows/meeting-to-akiflow.md` | Future workflow design (never implemented) |

---

## Block Prompt Inventory (B00-B48)

All block generator prompts in `Prompts/Blocks/` are **REQUIRED** by the meeting-ingestion skill's `processor.py`:

| Block | Path | Status |
|--------|--------|--------|
| B00 | `Prompts/Blocks/Generate_B00.prompt.md` | KEEP |
| B01 | `Prompts/Blocks/Generate_B01.prompt.md` | KEEP |
| B02 | `Prompts/Blocks/Generate_B02.prompt.md` | KEEP |
| B03 | `Prompts/Blocks/Generate_B03.prompt.md` | KEEP |
| B04 | `Prompts/Blocks/Generate_B04.prompt.md` | KEEP |
| B05 | `Prompts/Blocks/Generate_B05.prompt.md` | KEEP |
| B06 | `Prompts/Blocks/Generate_B06.prompt.md` | KEEP |
| B07 | `Prompts/Blocks/Generate_B07.prompt.md` | KEEP |
| B08 | `Prompts/Blocks/Generate_B08.prompt.md` | KEEP |
| B09 | `Prompts/Blocks/Generate_B09.prompt.md` | KEEP |
| B10 | `Prompts/Blocks/Generate_B10.prompt.md` | KEEP |
| B11 | `Prompts/Blocks/Generate_B11.prompt.md` | KEEP |
| B12 | `Prompts/Blocks/Generate_B12.prompt.md` | KEEP |
| B13 | `Prompts/Blocks/Generate_B13.prompt.md` | KEEP |
| B14 | `Prompts/Blocks/Generate_B14.prompt.md` | KEEP |
| B15 | `Prompts/Blocks/Generate_B15.prompt.md` | KEEP |
| B16 | `Prompts/Blocks/Generate_B16.prompt.md` | KEEP |
| B17 | `Prompts/Blocks/Generate_B17.prompt.md` | KEEP |
| B20 | `Prompts/Blocks/Generate_B20.prompt.md` | KEEP |
| B21 | `Prompts/Blocks/Generate_B21.prompt.md` | KEEP |
| B22 | `Prompts/Blocks/Generate_B22.prompt.md` | KEEP |
| B23 | `Prompts/Blocks/Generate_B23.prompt.md` | KEEP |
| B24 | `Prompts/Blocks/Generate_B24.prompt.md` | KEEP |
| B25 | `Prompts/Blocks/Generate_B25.prompt.md` | KEEP |
| B26 | `Prompts/Blocks/Generate_B26.prompt.md` | KEEP |
| B27 | `Prompts/Blocks/Generate_B27.prompt.md` | KEEP |
| B28 | `Prompts/Blocks/Generate_B28.prompt.md` | KEEP |
| B31 | `Prompts/Blocks/Generate_B31.prompt.md` | KEEP |
| B32 | `Prompts/Blocks/Generate_B32.prompt.md` | KEEP |
| B33 | `Prompts/Blocks/Generate_B33.prompt.md` | KEEP |
| B35 | `Prompts/Blocks/Generate_B35.prompt.md` | KEEP |
| B40 | `Prompts/Blocks/Generate_B40.prompt.md` | KEEP |
| B41 | `Prompts/Blocks/Generate_B41.prompt.md` | KEEP |
| B42 | `Prompts/Blocks/Generate_B42.prompt.md` | KEEP |
| B43 | `Prompts/Blocks/Generate_B43.prompt.md` | KEEP |
| B44 | `Prompts/Blocks/Generate_B44.prompt.md` | KEEP |
| B45 | `Prompts/Blocks/Generate_B45.prompt.md` | KEEP |
| B46 | `Prompts/Blocks/Generate_B46.prompt.md` | KEEP |
| B47 | `Prompts/Blocks/Generate_B47.prompt.md` | KEEP |
| B48 | `Prompts/Blocks/Generate_B48.prompt.md` | KEEP |

---

## Migration Path

### Phase 1: Delete Safe Now (D2.1)
- Delete `Prompts/Meeting Blurb Generation.prompt.md`
- Delete `Prompts/Meeting_Block_Selector.prompt.md`

### Phase 2: Migrate Agents (D3.1)
Migrate agents to use `meeting-ingestion` skill CLI:
- MG-1 agent `0c53b7ba` → Use `meeting-ingestion pull` instead of prompt
- MG-2 agent `0a08e6a8` → Use `meeting-ingestion process` instead of prompt
- MG-4 agent `ce6995b8` → Use `meeting-ingestion process` + warm intro generation
- MG-6 agent `f339ca26` → Use `meeting-ingestion process` handles state transitions

### Phase 3: Delete After Migration (Post D3.1)
- Delete `Prompts/Meeting Manifest Generation.prompt.md`
- Delete `Prompts/Meeting Block Generation.prompt.md`
- Delete `Prompts/Meeting Warm Intro Generation.prompt.md`
- Delete `Prompts/Meeting State Transition.prompt.md`
- Review `Prompts/Meeting Follow-Up Generation.prompt.md` (agent status unclear)

---

## Already Deleted (Per legacy_prompts.md)

The following prompts were already deleted as part of the skill consolidation:
- `Prompts/drive_meeting_ingestion.prompt.md`
- `Prompts/Analyze Meeting.prompt.md`
- `Prompts/Auto Process Meetings.prompt.md`
- `Prompts/Meeting Process.prompt.md`
- `Prompts/Meeting Transcript Process.prompt.md`
- `Prompts/Meeting Transcript Scan.prompt.md`
- `Prompts/meeting-block-selector.prompt.md`
- `Prompts/meeting-block-generator.prompt.md`
- `Prompts/standardize_meeting_folder.prompt.md`
- `Prompts/deduplicate-meetings.prompt.md`
- `Prompts/Meeting Detect.prompt.md`
- `Prompts/worker-meeting-cleanup.prompt.md`
- `Prompts/Meeting Metadata Extractor.prompt.md`
