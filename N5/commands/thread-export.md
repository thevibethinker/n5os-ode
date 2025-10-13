---
date: '2025-10-12T04:06:11Z'
last-tested: '2025-10-12T04:06:11Z'
generated_date: '2025-10-12T04:06:11Z'
checksum: auto
tags: [aar, threads, export, documentation]
category: threads
priority: high
related_files: [N5/scripts/n5_thread_export.py, N5/schemas/aar.schema.json]
anchors:
  input: null
  output: /home/workspace/N5/logs/threads/
---
# `thread-export`

Version: 2.2.0

Summary: Generate After-Action Report (AAR) and export conversation thread with artifacts in modular format

Workflow: threads

Tags: aar, threads, export, documentation

## Inputs
- thread_id : string (optional) — Thread ID (auto-detected if not provided)
- title : string (optional) — Descriptive title for archive directory
- dry-run : boolean (optional) — Preview without writing files
- format : string (optional) — Export format: 'modular' (default) or 'single' (v2.0 legacy)

## Outputs
- aar_json : path — AAR data (JSON source of truth)
- modular_exports : paths — 6 markdown files (INDEX, RESUME, DESIGN, IMPLEMENTATION, VALIDATION, CONTEXT) [v2.2]
- aar_md : path — Single markdown file (only when --format single) [v2.0]
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

**Related Commands**: [`conversation-end`](../commands/conversation-end.md)

**Knowledge Areas**: [Thread Management](../knowledge/thread-management.md), [Documentation](../knowledge/documentation.md)

**Scripts**: `file 'N5/scripts/n5_thread_export.py'`

**Schemas**: `file 'N5/schemas/aar.schema.json'`

## Usage Notes

This command implements the AAR v2.2 protocol for thread closure and continuation:

### Export Formats

**v2.2 Modular (default):** 6 separate markdown files
- `INDEX.md` - Navigation hub and file directory
- `RESUME.md` - Quick 10-minute resume entry point
- `DESIGN.md` - Key decisions and rationale
- `IMPLEMENTATION.md` - Technical details and code patterns
- `VALIDATION.md` - Testing status and troubleshooting
- `CONTEXT.md` - Thread lineage and metadata

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
4. **Schema Validation**: All AARs validated against `aar.schema.json`

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

### The AAR System Enables
- Efficient thread closure with context preservation
- Thread continuation across conversations
- Progressive documentation during long conversations
- Packed context window optimization
- Modular knowledge navigation
- **Automatic system timeline updates**
