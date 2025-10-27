---
description: 'Command: transcript-ingest'
tags:
- data
- transcripts
- gdrive
- processing
---
# `transcript-ingest`

Version: 1.0.0

Summary: Ingest and process transcripts from files or Google Drive folders

Workflow: data

Tags: data, transcripts, gdrive, processing

## Inputs
- transcript_source : string (required) — Path to transcript file or Google Drive folder ID
- --gdrive : flag (optional) — Indicates the source is a Google Drive folder ID
- --format : string (optional) — Expected transcript format (txt, vtt, srt, json). Auto-detected if not specified
- --output-dir : string (optional) — Directory to save processed transcripts (default: Records/Temporary/)

## Outputs
- processed_files : list — List of processed transcript files with metadata
- summary : text — Processing summary and statistics

## Side Effects
- writes:file (processed transcripts to Records/Temporary/)
- external:api (Google Drive API if --gdrive flag is used)

## Permissions Required
- external_api (for Google Drive access)
- file:write (for saving processed transcripts)

## Process Flow
1. **Source Validation**: Verify transcript source exists and is accessible
2. **Format Detection**: Auto-detect transcript format if not specified
3. **Content Extraction**: Extract text content from transcripts
4. **Metadata Capture**: Extract timestamps, speakers, and other metadata
5. **Processing**: Clean and structure transcript content
6. **Storage**: Save to Records/Temporary/ with appropriate naming
7. **Optional**: Move to permanent location in Knowledge/ or Records/

## Examples
- Process local transcript: `python N5/scripts/transcript_ingest.py /path/to/transcript.txt`
- Process from Google Drive folder: `python N5/scripts/transcript_ingest.py folder_id_123 --gdrive`
- Specify format: `python N5/scripts/transcript_ingest.py /path/to/file.vtt --format vtt`
- Custom output directory: `python N5/scripts/transcript_ingest.py /path/to/transcript.txt --output-dir Careerspan/Meetings/`

## Supported Formats
- Plain text (.txt)
- WebVTT (.vtt)
- SubRip (.srt)
- JSON transcripts (.json)
- Auto-detection from file extension or content

## Related Components

**Related Commands**: [`direct-knowledge-ingest`](../commands/direct-knowledge-ingest.md), [`knowledge-ingest`](../commands/knowledge-ingest.md)

**Scripts**: `N5/scripts/transcript_ingest.py` (to be created), `N5/scripts/transcript_processor.py` (to be created)

**Knowledge Areas**: [Data Ingestion](../knowledge/data-ingestion.md), [Records Management](../Records/README.md)

**Examples**: See [Examples Library](../examples/) for usage patterns

## Implementation Notes
- Google Drive integration requires connected Google Drive app
- Supports batch processing of multiple transcripts from folders
- Automatic cleanup of temporary files after 7 days (per Records/Temporary/ policy)
- Preserves original timestamps and speaker information when available
- Can be used as part of meeting processing workflow

## Future Enhancements
- [ ] Integration with meeting note templates
- [ ] Automatic speaker identification and labeling
- [ ] Direct ingestion into Knowledge reservoirs
- [ ] Support for audio/video file transcription
- [ ] Batch processing with parallel execution
