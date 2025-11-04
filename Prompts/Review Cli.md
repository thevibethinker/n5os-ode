---
description: 'Command: review-cli'
tool: true
tags: []
---
# Review CLI (n5 review)

Purpose: manage output reviews (add, list, show, status, comment, export, improve).

## Quickstart

- Add: `python3 N5/scripts/review_cli.py add Documents/N5.md --title "N5 System Documentation" --conversation-id "con_xxx" --tags "docs,n5,system" --improve "Tighten intro" --optimal "Concise 150 words, active voice"`
- List: `python3 N5/scripts/review_cli.py list --status in_review`
- Show: `python3 N5/scripts/review_cli.py show out_XXXXXXXXXXXX`
- Update: `python3 N5/scripts/review_cli.py status out_XXXXXXXXXXXX approved --sentiment excellent --reviewer "V" --improve "Fix tone in section 2" --optimal "Warmer, direct"`
- Comment: `python3 N5/scripts/review_cli.py comment out_XXXXXXXXXXXX --body "Great work" --author "V"`
- Improve: `python3 N5/scripts/review_cli.py improve out_XXXXXXXXXXXX --improve "Trim 20%" --optimal "Same content, fewer words" --priority high`
- Export: `python3 N5/scripts/review_cli.py export --status approved --output /tmp/approved.json`

## Data files

- Lists/output_reviews.jsonl
- Lists/output_reviews_comments.jsonl

## Commands

### add

Add an output (file, message, URL, image, video, transcript) for review.

Flags:

- `--title` Title override
- `--type` file|message|image|video|transcript|url (auto-detected if omitted)
- `--conversation-id` Conversation ID (auto-detected if omitted)
- `--thread`, `--script`, `--pipeline` Provenance metadata
- `--tags` Comma-separated tags
- `--notes` Freeform notes
- `--improve` What to change (improvement notes)
- `--optimal` Optimal state description
- `--priority` low|medium|high

### list

Filterable listing by `--status`, `--sentiment`, `--type`, `--tags`.

### show &lt;output_id&gt;

Detailed view including provenance, quality scores, improvement notes, and threaded comments.

### status &lt;output_id&gt;

Update workflow status; optional `--sentiment`, `--reviewer`, repeated `--score dim=value`, `--note`.\
Also supports inline `--improve`, `--optimal`, `--priority`.

### comment &lt;output_id&gt;

Add threaded comment (`--body` required); optional `--author`, `--context`, `--parent`, `--tags`.

### improve &lt;output_id&gt;

Update structured improvement notes without changing status.

### export

Export filtered reviews as JSON (`--status`, `--sentiment`, `--output`).

## Notes

- Valid statuses: pending, in_review, approved, issue, training, archived
- Valid sentiments: excellent, good, acceptable, issue
- New field: `review.improvement_notes` with `{ what_to_change, optimal_state, priority }`
- Full provenance captured: conversation, thread, script, pipeline