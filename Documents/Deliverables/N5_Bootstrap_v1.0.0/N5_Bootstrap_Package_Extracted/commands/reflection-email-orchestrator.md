---
category: content
priority: high
description: One-off orchestrator to fetch reflection audio from Gmail and stage it for processing.
---
# Reflection Email Orchestrator (Manual)

Use this when V emails an audio reflection.

## Gmail Filters
- Label: `AI_Reflections` (optional)
- Query: `in:inbox has:attachment filename:(mp3 OR m4a OR wav OR opus) newer_than:14d`

## Steps
1) Find message:
   - tool gmail-find-email with the query above (add `label:AI_Reflections` when used)
2) Download each attachment:
   - tool gmail-download-attachment → `/tmp/<filename>`
3) Move into staging:
   - `/home/workspace/N5/records/reflections/incoming/`
4) Reply to the original thread (only on error or questions):
   - tool gmail-send-email with `inReplyTo` set to the message-id.

## Handoff to Worker
- For each saved audio file, run worker: `reflection-worker` (below).

## Outputs
- Staged files in `N5/records/reflections/incoming/`
- Registry entry appended with status `received`
