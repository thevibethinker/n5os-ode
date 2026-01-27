---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
type: build_plan
status: complete
provenance: con_Tq9eOqW4T0rTnKvb
supersedes: meeting-skill-migration
---

# Plan: Complete Meeting Ingestion Skill

**Objective:** Fill out the meeting-ingestion skill with working `pull.py` and `processor.py` scripts that wrap existing N5/scripts functionality, plus a `legacy_prompts.md` reference doc.

**Trigger:** V requested completing the skill that was scaffolded but never filled out.

**Key Design Principle:** Thin wrappers around existing N5/scripts. The skill orchestrates; the scripts do the work.

---

## Open Questions

<!-- None - all requirements are clear from existing code and prompts. -->

---

## Checklist

### Phase 1: Skill Scripts & Docs
- ☑ Create `Skills/meeting-ingestion/scripts/pull.py` - GDrive transcript puller using Zo API
- ☑ Create `Skills/meeting-ingestion/scripts/processor.py` - Meeting processing orchestrator
- ☑ Create `Skills/meeting-ingestion/scripts/meeting_cli.py` - Unified CLI entry point
- ☑ Create `Skills/meeting-ingestion/references/legacy_prompts.md` - Captured logic from prompts
- ☑ Update `Skills/meeting-ingestion/SKILL.md` - Full usage documentation
- ☑ Test: `meeting-ingestion pull --dry-run` shows available transcripts
- ☑ Test: `meeting-ingestion status` shows queue state

---

## Phase 1: Skill Scripts & Docs

### Affected Files
- `Skills/meeting-ingestion/scripts/pull.py` - CREATE - GDrive transcript puller
- `Skills/meeting-ingestion/scripts/processor.py` - CREATE - Meeting processing orchestrator
- `Skills/meeting-ingestion/scripts/meeting_cli.py` - CREATE - Unified CLI (`meeting-ingestion` command)
- `Skills/meeting-ingestion/references/legacy_prompts.md` - CREATE - Reference doc for legacy prompt logic
- `Skills/meeting-ingestion/SKILL.md` - UPDATE - Complete usage documentation

### Changes

**1.1 Pull Script (`pull.py`):**
Downloads transcripts from Google Drive to staging area.

Core logic:
1. Read Drive folder ID from `N5/config/drive_locations.yaml` 
2. Use Zo API (`/zo/ask`) to invoke `use_app_google_drive` to list files
3. For each file not already in registry:
   - Download via Zo API 
   - Convert .docx to markdown via pandoc
   - Apply normalization via `N5/scripts/meeting_normalizer.py`
   - Write to `Personal/Meetings/Inbox/`
4. Return list of ingested files

CLI interface:
```
python3 pull.py [--dry-run] [--batch-size N]
```

**1.2 Processor Script (`processor.py`):**
Orchestrates the MG-1 through MG-6 pipeline for meetings in staging.

Core logic:
1. Find meetings in `Personal/Meetings/Inbox/` or specified path
2. For each meeting:
   - Phase 1 (MG-1): Generate manifest using `N5/scripts/meeting_manifest_generator.py`
   - Phase 2 (MG-2): Generate intelligence blocks (B01, B05, B08, etc.)
   - Phase 3 (MG-3): CRM sync using `N5/scripts/meeting_crm_sync.py`
3. Move processed meeting to final location
4. Update registry status

CLI interface:
```
python3 processor.py [meeting_path] [--blocks B01,B05,B08] [--skip-crm]
```

**1.3 Unified CLI (`meeting_cli.py`):**
Single entry point that dispatches to subcommands.

```
python3 meeting_cli.py pull [--dry-run] [--batch-size N]
python3 meeting_cli.py process [meeting_path] [--blocks ...]
python3 meeting_cli.py status
```

**1.4 Legacy Prompts Reference (`legacy_prompts.md`):**
Consolidate and document the logic from:
- `Prompts/drive_meeting_ingestion.prompt.md`
- `Prompts/Analyze Meeting.prompt.md`
- `Prompts/Internal Meeting Process.prompt.md`
- `Prompts/Meeting State Transition.prompt.md`
- `Prompts/standardize_meeting_folder.prompt.md`

This becomes the canonical reference for understanding meeting processing logic.

**1.5 SKILL.md Update:**
- Add complete CLI reference
- Add workflow examples
- Document dependencies on N5/scripts
- Add troubleshooting section

### Unit Tests
- `pull.py --dry-run`: Shows list of available transcripts from Drive without downloading
- `processor.py --help`: Shows help with all options
- `meeting_cli.py status`: Returns JSON with queue stats

---

## MECE Validation

Single-worker build - no MECE validation required.

---

## Success Criteria

1. `meeting-ingestion pull && meeting-ingestion process` replaces legacy 5+ agent chain
2. Scripts successfully wrap existing N5/scripts without duplicating logic
3. `meeting-ingestion status` shows accurate queue state
4. Legacy prompts documented in references/

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Google Drive auth via script | Use Zo API (`/zo/ask`) to delegate auth to Zo's native integrations |
| Breaking changes to N5/scripts | Scripts use imports, not copies - stays in sync automatically |
| Transcript conversion failures | Quarantine failed conversions, continue with next file |

---

## Architectural Decisions

### Why thin wrappers?
The existing N5/scripts (`meeting_registry.py`, `meeting_orchestrator.py`, `meeting_normalizer.py`, `meeting_manifest_generator.py`) are mature, tested, and work well. The skill should **orchestrate** these scripts, not **replace** them.

### Why Zo API for Drive access?
Direct Google Drive API calls require managing OAuth tokens and credentials. Using `/zo/ask` to invoke `use_app_google_drive` leverages Zo's existing authenticated connection.

### MG Block Generation
Intelligence blocks (B01, B05, B08, etc.) require LLM analysis of transcript content. The processor script will use `/zo/ask` to generate blocks, passing the transcript and block definitions.

---

## Level Upper Review

Skipped - straightforward implementation following established patterns.
