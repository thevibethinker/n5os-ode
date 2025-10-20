---
category: content
priority: high
description: End-to-end reflection ingestion and output generation from Google Drive folder with dynamic classification and voice-aware templates.
---
# Reflection Pipeline

Purpose: Ingest reflections from Google Drive, classify, and generate outputs (LinkedIn post, executive memo, blog snippet) using correct voice routing.

## Inputs
- Google Drive folder (provided by V)
- Reflection files (txt, md, docx, gdoc export)

## Flow
1. Pull new files from Google Drive folder into `N5/records/reflections/incoming/`
2. Classify reflection type (multi-label): product_strategy, dilemma, pitch_narrative, announcement, hiring, founder_journal
3. Select voice profile:
   - Social outputs → `file 'N5/prefs/communication/social-media-voice.md'`
   - Executive memo → `file 'N5/prefs/communication/voice.md'`
4. Generate outputs via `script 'N5/scripts/reflection_pipeline.py'`
5. Save artifacts under `N5/records/reflections/outputs/{YYYY-MM-DD}/{slug}/`
6. Stage extracted insights to `N5/sessions/strategic-partner/pending-updates/` for approval

## Safety
- Read-only from Drive; writes are local
- Idempotent: tracks processed file IDs in `.state.json`
- No external sends

## Usage
```
python3 /home/workspace/N5/scripts/reflection_pipeline.py --pull --process --folder-id <FOLDER_ID> [--dry-run]
```

## References
- file 'N5/scripts/reflection_pipeline.py'
- file 'N5/scripts/reflection_synthesizer.py'
- file 'N5/prefs/communication/social-media-voice.md'
- file 'N5/prefs/communication/voice.md'
