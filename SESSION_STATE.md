# Session State
Auto-generated | Scheduled Task

## Metadata
- Conversation ID: con_scRaOffQWfIgY7zc
- Status: active
- Type: discussion

## Focus
Execute command-first: run meeting-transcript-scan, enforcing strict dedup by gdrive_id across inbox/processed/records before any processing; only create requests for truly new transcripts; apply internal/external naming convention.

## Objective
- Load all existing gdrive_ids from:
  - N5/inbox/meeting_requests/*.json
  - N5/inbox/meeting_requests/completed/*.json
  - N5/inbox/meeting_requests/processed/*.json
  - N5/records/meetings/*/_metadata.json
- Skip any transcript whose gdrive_id is present
- For new items: generate name as YYYY-MM-DD_internal-team or YYYY-MM-DD_external-{name}
- Queue standardized meeting_requests only for new transcripts

## Tags
#scheduled #meetings #transcripts #dedup #naming #command-first #google-drive
