# N5 Jobs Subsystem Policy

## Purpose
Canonical store for all job-ingestion artefacts: scraped listings, private placements, review state. Follows LADDER principle:
- Light-weight
- Atomic writes (.tmp → rename)
- Dry-run first
- Deduplicate by URL
- Easy-review (PENDING → OK)
- Reject-silently (no junk list)

## Scope
`/N5/jobs/lists/*.jsonl` – medium-protection; manual edits allowed.
`/N5/jobs/modules/` – code; auto-gen OK.
`/N5/jobs/commands/` – thin wrappers; auto-gen from commands.jsonl.
`/N5/jobs/knowledge/` – prompts, detector rules; Git-tracked.

## Rules
1. Every ingest command must offer `--dry-run` (sticky safety).
2. GPT-4 minimum for filter/enrichment (threshold 0.8 hard-floor).
3. UID = URL primary key; no duplicates across lists.
4. Review state: PENDING → OK only via `zo jobs review`.
5. Logs → `/dev/shm/jobs.log`; no sensitive data in logs.