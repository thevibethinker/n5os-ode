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

Version: 2.0.0

Summary: Generate After-Action Report (AAR) and export conversation thread with artifacts

Workflow: threads

Tags: aar, threads, export, documentation

## Inputs
- thread_id : string (optional) — Thread ID (auto-detected if not provided)
- title : string (optional) — Descriptive title for archive directory
- dry-run : boolean (optional) — Preview without writing files

## Outputs
- aar_json : path — AAR data (JSON source of truth)
- aar_md : path — AAR markdown view (generated)
- archive_dir : path — Thread archive directory with artifacts

## Side Effects
- writes:file — Creates AAR files and archive directory
- reads:conversation_workspace — Reads artifacts from conversation workspace

## Examples
- N5: run thread-export --auto
- N5: run thread-export con_abc123 --title "System Implementation"
- N5: run thread-export --auto --dry-run

## Related Components

**Related Commands**: [`conversation-end`](../commands/conversation-end.md)

**Knowledge Areas**: [Thread Management](../knowledge/thread-management.md), [Documentation](../knowledge/documentation.md)

**Scripts**: `file 'N5/scripts/n5_thread_export.py'`

**Schemas**: `file 'N5/schemas/aar.schema.json'`

## Usage Notes

This command implements the AAR v2.0 protocol for thread closure and continuation:

1. **Interactive Mode** (current MVP): Prompts user with questions to build AAR
2. **Automatic Mode** (future): Extracts data from conversation context
3. **Dual-Write Pattern**: JSON is source of truth, Markdown is generated view
4. **Schema Validation**: All AARs validated against `aar.schema.json`

The AAR system enables:
- Efficient thread closure with context preservation
- Thread continuation across conversations
- Progressive documentation during long conversations
- Packed context window optimization
