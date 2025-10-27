---
description: 'Command: gfetch'
tags:
- gdrive
- gmail
- fetch
- retrieval
---
# `gfetch`

Version: 1.0.0

Summary: Fetch and retrieve content from Google Drive or Gmail based on search criteria

Workflow: data

Tags: gdrive, gmail, fetch, retrieval, search

## Inputs
- query : string (required) — Search query or file/email identifier
- --source : string (optional) — Source service: 'drive' or 'gmail' (default: auto-detect)
- --format : string (optional) — Output format: 'raw', 'markdown', 'json' (default: 'markdown')
- --output-dir : string (optional) — Directory to save retrieved content (default: Records/Temporary/)
- --limit : integer (optional) — Maximum number of items to retrieve (default: 10)

## Outputs
- retrieved_items : list — List of retrieved items with metadata
- summary : text — Retrieval summary with item count and locations

## Side Effects
- external:api (Google Drive and Gmail APIs)
- writes:file (retrieved content to specified output directory)

## Permissions Required
- external_api (Google Drive and/or Gmail access)
- file:write

## Process Flow
1. **Parse Query**: Interpret search query and determine source
2. **Authenticate**: Verify Google API access
3. **Search**: Execute search against specified source
4. **Retrieve**: Download matching items
5. **Convert**: Transform to requested format
6. **Save**: Store in output directory with metadata
7. **Report**: Generate summary of retrieved items

## Examples
- Fetch file by name: `/gfetch Q4 budget spreadsheet`
- Fetch from Gmail: `/gfetch subject:invoice from:vendor@example.com --source gmail`
- Fetch multiple files: `/gfetch "meeting notes" --source drive --limit 5`
- Custom output: `/gfetch "project docs" --output-dir Careerspan/Meetings/ --format markdown`

## Search Syntax

### Google Drive
- By name: `filename`
- By type: `type:spreadsheet`, `type:document`, `type:pdf`
- By date: `modified:>2025-01-01`
- By folder: `in:folder_name`

### Gmail
- By subject: `subject:keyword`
- By sender: `from:email@example.com`
- By date: `after:2025/01/01`, `before:2025/12/31`
- Has attachment: `has:attachment`
- Standard Gmail search operators supported

## Related Components

**Related Commands**: [`transcript-ingest`](../commands/transcript-ingest.md), [`direct-knowledge-ingest`](../commands/direct-knowledge-ingest.md), [`knowledge-add`](../commands/knowledge-add.md)

**App Integrations**: Google Drive (`use_app_google_drive`), Gmail (`use_app_gmail`)

**Scripts**: `N5/scripts/gfetch.py` (to be created)

**Examples**: See [Examples Library](../examples/) for usage patterns

## Implementation Notes
- Requires connected Google Drive and/or Gmail apps
- Auto-detects source based on query syntax
- Supports batch retrieval with rate limiting
- Preserves original file metadata (dates, authors, etc.)
- Downloaded files automatically organized by date/source
- Integrates with Records staging system

## Future Enhancements
- [ ] Fuzzy search with AI-powered relevance ranking
- [ ] Direct ingestion into Knowledge reservoirs
- [ ] Automatic file type conversion
- [ ] Scheduled periodic fetches
- [ ] Integration with lists (auto-add fetched items)
