---
description: 'Command: reflection-pipeline'
tags: []
tool: true
---
# Reflection Pipeline

Purpose: Ingest reflections from Google Drive, classify, and generate outputs (LinkedIn post, executive memo, blog snippet) using correct voice routing.

## Inputs

- **Google Drive folder** (primary, regular use)
- **Email with `[Reflect]` tag** (occasional, ad-hoc)
- Reflection files: txt, md, docx, gdoc export, audio (mp3, m4a, wav, opus)
- Email body text: used as context/instructions when audio attachment present

## Flow

1. Pull new files from Drive/Email into `N5/records/reflections/incoming/`
2. Transcribe audio files automatically
3. Classify reflection type (multi-label): product_strategy, dilemma, pitch_narrative, announcement, hiring, founder_journal
4. Select voice profile: 
   - Social outputs → `file N5/prefs/communication/social-media-voice.md` 
   - Executive memo → `file N5/prefs/communication/voice.md` 
5. Generate outputs via `script 'N5/scripts/reflection_pipeline.py'`
6. Save artifacts under `N5/records/reflections/outputs/{YYYY-MM-DD}/{slug}/`
7. Stage extracted insights to `N5/sessions/strategic-partner/pending-updates/` for approval

## Safety

- Read-only from Drive; writes are local
- Idempotent: tracks processed file IDs in `file .state.json` 
- No external sends

## Usage

```
# Unified ingestion (recommended)
command 'N5/commands/reflection-ingest.md'

# Or directly:
python3 /home/workspace/N5/scripts/reflection_ingest.py [--source email|drive|both] [--dry-run]

# Legacy Drive-only:
python3 /home/workspace/N5/scripts/reflection_pipeline.py --pull --process --folder-id <FOLDER_ID> [--dry-run]
```

## References

- file 'N5/scripts/reflection_pipeline.py'
- file 'N5/scripts/reflection_synthesizer.py'
- file 'N5/prefs/communication/social-media-voice.md'
- file 'N5/prefs/communication/voice.md'