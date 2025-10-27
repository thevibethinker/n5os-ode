---
category: content
priority: high
description: One-off orchestrator to fetch reflection audio from Gmail and stage it for processing.
---
# Reflection Email Orchestrator (Subject Trigger)

Pulls audio attachments from the last 10 minutes whose subject contains `[Reflect]`.

## Query Rules
- Time window: last 10 minutes
- Must have attachment
- Filenames: mp3, m4a, wav, opus
- Subject must include literal token: `[Reflect]`

## Steps
1) Find emails: tool gmail-find-email with query
   ```
   newer_than:10m has:attachment subject:"[Reflect]" filename:(mp3 OR m4a OR wav OR opus)
   ```
2) For each match:
   - Download attachment(s) to `N5/records/reflections/incoming/`
   - Extract email body text and save as `<message-id>_context.md` (used as processing instructions)
3) Record message IDs to `N5/records/reflections/.state.json` under `processed_message_ids`
4) Reply to the original email only on error/questions

## Email Body Handling
- **Body text** = context/instructions for how to process the audio
- Saved alongside audio as `<filename>_context.md`
- Loaded automatically by reflection worker during processing

## Next
- Run worker: `reflection-worker --file <staged-file>`
