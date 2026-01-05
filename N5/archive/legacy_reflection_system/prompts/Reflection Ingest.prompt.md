---
description: 'Manually triggered command that:'
tool: true
tags: []
---
# Reflection Ingest (Unified)

Single entry point for ingesting reflections from email and/or Google Drive.

## Purpose

Manually triggered command that:
1. Pulls new reflections from specified source(s)
2. Auto-transcribes audio files
3. Processes each reflection through the pipeline
4. Stages all outputs for approval

## Usage

```bash
# Ingest from both sources (default)
command 'N5/commands/reflection-ingest.md'

# Email only
command 'N5/commands/reflection-ingest.md' --source email

# Drive only
command 'N5/commands/reflection-ingest.md' --source drive
```

## Sources

- **Google Drive folder** (primary, regular use)
- **Email with `[Reflect]` tag** (occasional, ad-hoc)
- Reflection files: txt, md, docx, gdoc export, audio (mp3, m4a, wav, opus)
- Email body text: used as context/instructions when audio attachment present

## Email-Triggered Invocation (For AI)

When V emails Zo with subject containing "reflection-ingest" or "[Reflect]":

### Workflow

1. **Locate attachment**: Check conversation workspace at `/home/.z/workspaces/[CONVO_ID]/email_attachment/` (replace `[CONVO_ID]` with current conversation ID)

2. **Stage file**: Copy to `N5/records/reflections/incoming/` with descriptive, datestamped filename:
   ```bash
   cp "/home/.z/workspaces/[CONVO_ID]/email_attachment/[original_file]" \
      "/home/workspace/N5/records/reflections/incoming/YYYY-MM-DD_descriptive-slug.ext"
   ```

3. **Handle text transcripts**: If file is .txt/.md (already transcribed text), create `.transcript.jsonl` wrapper:
   ```python
   import json
   from pathlib import Path
   
   txt_file = Path("/home/workspace/N5/records/reflections/incoming/2025-10-20_example.txt")
   transcript_file = Path(str(txt_file) + ".transcript.jsonl")
   
   transcript_data = {
       "text": txt_file.read_text(),
       "source_file": str(txt_file),
       "mime_type": "text/plain"
   }
   
   transcript_file.write_text(json.dumps(transcript_data))
   ```

4. **Handle audio files**: Use Zo's `transcribe_audio` tool before running pipeline

5. **Run pipeline**: 
   ```bash
   python3 /home/workspace/N5/scripts/reflection_ingest.py
   ```

6. **Synthesize content**: Don't leave placeholders—create actual summary and analysis from reflection content based on transcript

7. **Follow approval workflow**: System creates registry entry with status `awaiting-approval`. V selects desired outputs from proposal.

### DO NOT

- Create ad-hoc analysis documents in conversation workspace
- Manually add items to lists before approval workflow completes
- Skip the reflection pipeline and improvise alternate processing
- Leave placeholder content ("Generated summary placeholder") in summary/detail files
- Bypass the registry and approval system

### Rationale

The reflection pipeline provides:
- Consistent processing and classification (product_strategy, founder_journal, etc.)
- Registry tracking with approval workflow and audit trail
- Standardized output formats (summary.md, detail.md, proposal.md)
- Integration with knowledge management system
- Voice-aware synthesis (social vs. executive voice profiles)
- Modular outputs V can select from

Improvising alternate approaches loses all these system benefits and violates SSOT principle.

## Flow

1. **Pull** new files from source(s) → `N5/records/reflections/incoming/`
2. **Transcribe** audio files (auto-detect: mp3, m4a, wav, opus)
3. **Process** each file via `script 'N5/scripts/reflection_worker.py'`
   - Classify reflection type
   - Select voice profile
   - Generate summary + detailed recap
   - Create proposal with output options
4. **Register** with status `awaiting-approval`
5. **Notify** V of new reflections ready for approval

## Email Body + Audio Handling

When email contains both body text and audio attachment:
- **Body** = context/instructions for processing the audio
- **Audio** = actual reflection content
- Body saved as `<filename>_context.md` and referenced during processing

## Approval Workflow

All reflections require approval before generating final outputs:
1. Review summary, recap, and classification
2. Select desired outputs (LinkedIn, memo, blog, etc.)
3. Approve → triggers output generation
4. Outputs saved to `N5/records/reflections/outputs/{YYYY-MM-DD}/{slug}/`

## Configuration

Drive folder-id stored in: `file 'N5/config/reflection-sources.json'`

```json
{
  "drive_folder_id": "your-folder-id-here",
  "email_lookback_minutes": 10
}
```

## Safety

- Read-only from external sources
- Idempotent: deduplicates via state tracking
- No automatic sends
- All outputs require explicit approval

## Implementation

Script: `file 'N5/scripts/reflection_ingest.py'`

## References

- file 'N5/commands/reflection-pipeline.md'
- file 'N5/commands/reflection-email-orchestrator.md'
- file 'N5/commands/reflection-worker.md'
- file 'N5/scripts/reflection_ingest.py'
- file 'N5/scripts/reflection_worker.py'
