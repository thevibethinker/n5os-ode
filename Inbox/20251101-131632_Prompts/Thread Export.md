---
description: 'Command: thread-export'
tags:
- aar
- threads
- export
- documentation
tool: true
---
# `thread-export`

Version: 2.2.0

Summary: Generate After-Action Report (AAR) and export conversation thread with artifacts in modular format

**Alias:** `thread-checkpoint` — Use this command to create a conversation checkpoint (non-destructive state save). For full conversation closure with file organization and cleanup, use `conversation-end` (which calls this command as Phase 0).

Workflow: threads

Tags: aar, threads, export, documentation

## Inputs

- thread_id : string (optional) — Thread ID (auto-detected if not provided)
- title : string (optional) — Descriptive title for archive directory
- dry-run : boolean (optional) — Preview without writing files
- format : string (optional) — Export format: 'modular' (default) or 'single' (v2.0 legacy)

## Outputs

- aar_json : path — AAR data (JSON source of truth)
- modular_exports : paths — 6 markdown files (INDEX, RESUME, DESIGN, IMPLEMENTATION, VALIDATION, CONTEXT) \[v2.2\]
- aar_md : path — Single markdown file (only when --format single) \[v2.0\]
- archive_dir : path — Thread archive directory with artifacts

## Side Effects

- writes:file — Creates AAR files and archive directory
- reads:conversation_workspace — Reads artifacts from conversation workspace

## Examples

- N5: run thread-export --auto
- N5: run thread-export con_abc123 --title "System Implementation"
- N5: run thread-export --auto --dry-run
- N5: run thread-export --auto --format single  # v2.0 legacy format

## Related Components

**Related Commands**: `conversation-end`

**Knowledge Areas**: [Thread Management](../knowledge/thread-management.md), [Documentation](../knowledge/documentation.md)

**Scripts**: `file N5/scripts/n5_thread_export.py` 

**Schemas**: `file N5/schemas/aar.schema.json` 

## Usage Notes

This command implements the AAR v2.2 protocol for thread closure and continuation:

### Export Formats

**v2.2 Modular (default):** 6 separate markdown files

- `file INDEX.md`  - Navigation hub and file directory
- `file RESUME.md`  - Quick 10-minute resume entry point
- `file DESIGN.md`  - Key decisions and rationale
- `file IMPLEMENTATION.md`  - Technical details and code patterns
- `file VALIDATION.md`  - Testing status and troubleshooting
- `file CONTEXT.md`  - Thread lineage and metadata

**Benefits:**

- Faster navigation (read only relevant sections)
- Clearer purpose separation
- Better for resumption (start with INDEX → RESUME)
- Modular updates (edit one file without affecting others)

**v2.0 Single File (legacy):** One comprehensive markdown file

- Available via `--format single` for backward compatibility
- Maintained for existing workflows

### Generation Modes

1. **Interactive Mode**: Prompts user with questions to build AAR
2. **Smart Extraction Mode** (--non-interactive): Auto-extracts from artifacts and patterns
3. **Dual-Write Pattern**: JSON is source of truth, Markdown is generated view
4. **Schema Validation**: All AARs validated against `file aar.schema.json` 

### Phase 6: System Timeline Update (NEW)

After archive creation, thread-export automatically:

1. Analyzes AAR data for timeline-worthy significance
2. Detects high-impact work (new commands, infrastructure, features)
3. Generates suggested timeline entry with category, impact, and components
4. Prompts user to review and approve entry
5. Writes to system-timeline.jsonl if approved

**Skip Criteria:**

- Low-impact conversational threads
- Threads with minimal artifacts
- General work sessions

**Signals for Timeline Update:**

- Impact keywords (implement, create, fix, critical, system)
- Multiple artifacts created (≥3)
- Key decisions documented
- New scripts or commands created

**User can:**

- Accept suggestion as-is (Y)
- Edit before accepting (e)
- Skip timeline update (n)

### Phase 7: Thread Title Generation (NEW)

After export completion, automatically generate thread titles:

**Instructions:**
1. Load `file 'N5/prefs/operations/thread-titling.md'` for format rules
2. Load `file 'N5/config/emoji-legend.json'` for emoji selection
3. Analyze thread content, AAR data, and artifacts
4. Generate TWO titles:
   - **Current thread title**: For the thread just exported
   - **Next thread title**: For continuation (increment #N or add #2 if current has #1 or no number)
   - Using 🔗 chain emoji for linked threads
5. Display both titles prominently for copy/paste

**Title Format (REQUIRED):**
```
MMM DD | {emoji} {Title} {optional: #N}
```

**Examples:**
```
Current Thread:  Oct 16 | ✅ Thread Titling System
Next Thread:     Oct 16 | 🔗 Thread Titling System #2
```

**Display Format:**
```
======================================================================
📋 THREAD TITLES GENERATED
======================================================================

Current Thread:
  Oct 16 | ✅ Thread Titling System

Next Thread (for continuation):
  Oct 16 | 🔗 Thread Titling System #2

💡 Copy these titles when naming threads in the Zo interface.
======================================================================
```

**Rules:**
- Always generate both titles (current + next)
- Use centralized emoji legend for consistency
- Follow noun-first principle
- Respect UI constraints (collapsed sidebar shows ~24 chars)
- Include sequence numbers for linked work
- Display prominently for easy copy/paste

### The AAR System Enables

- Efficient thread closure with context preservation
- Thread continuation across conversations
- Progressive documentation during long conversations
- Packed context window optimization
- Modular knowledge navigation
- **Automatic system timeline updates**

## Command Relationship (clarification)

- thread-export focuses on AAR generation and modular exports for a thread.
- When closing a thread, prefer `conversation-end` — it will run Phase -1 (lessons extraction) and then call `thread-export` as Phase 0.
- Use `thread-export` standalone for mid-thread checkpoints, interim AARs, or when you explicitly do not want the full end-step workflow.
- Lessons extraction is orchestrated by `conversation-end` (Phase -1) via `N5/scripts/n5_lessons_extract.py` and is not triggered by thread-export itself.