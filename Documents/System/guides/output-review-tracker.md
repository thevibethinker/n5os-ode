# Output Review Tracker

**Status:** Production  
**Version:** 1.0  
**Created:** 2025-10-19  
**Orchestrator:** con_YSy4ld4J113LZQ9A

---

## Overview

The Output Review Tracker is a quality management system for tracking, reviewing, and rating AI outputs within the N5 ecosystem. It provides structured workflows for flagging outputs, adding comments, tracking quality dimensions, and exporting training data.

## Architecture

### Components

1. **Schemas** (`N5/schemas/`)
   - `output-review.schema.json` - Main review entry schema
   - `output-review-comment.schema.json` - Comment schema with threading

2. **Core Library** (`N5/scripts/`)
   - `review_manager.py` - Core ReviewManager class with all operations
   - `review_cli.py` - Command-line interface wrapping ReviewManager

3. **Data Storage** (`Lists/`)
   - `output_reviews.jsonl` - Main review entries
   - `output_reviews_comments.jsonl` - Threaded comments

4. **Commands** (`Recipes/recipes.jsonl`)
   - 6 registered commands: `review-add`, `review-list`, `review-show`, `review-status`, `review-comment`, `review-export`

---

## Commands

### `n5 review add`
Flag an output for review with full provenance tracking.

```bash
n5 review add <reference> \
  [--title "Title"] \
  [--type file|message|url] \
  [--conversation-id con_XXX] \
  [--tags tag1,tag2] \
  [--notes "Context"] \
  [--dry-run]
```

**Examples:**
```bash
# Add a file for review
n5 review add Documents/meeting-notes.md --title "Weekly sync notes" --tags meeting,notes

# Add URL with context
n5 review add https://docs.google.com/doc/123 --title "Strategy doc" --type url --notes "Draft v2"
```

---

### `n5 review list`
List tracked outputs with optional filters.

```bash
n5 review list \
  [--status pending|in_review|approved|issue|training|archived] \
  [--sentiment excellent|good|acceptable|issue] \
  [--tags tag1,tag2] \
  [--type file|message|url]
```

**Examples:**
```bash
# List all pending reviews
n5 review list --status pending

# Find problematic outputs
n5 review list --sentiment issue --tags documentation

# Show all reviews
n5 review list
```

---

### `n5 review show`
Show full details for a tracked output including provenance, quality scores, and comments.

```bash
n5 review show <output_id>
```

**Example:**
```bash
n5 review show out_2fa3949708b2
```

**Output includes:**
- Title, type, reference, status, sentiment
- Creation/update timestamps
- Provenance (conversation, thread, script, pipeline)
- Quality dimension scores (0-10 scale)
- Threaded comments with indentation

---

### `n5 review status`
Update review status with optional sentiment and quality scores.

```bash
n5 review status <output_id> <new_status> \
  [--sentiment excellent|good|acceptable|issue] \
  [--reviewer "Name"] \
  [--score dimension=value] \
  [--note "Details"] \
  [--dry-run]
```

**Valid statuses:** `pending`, `in_review`, `approved`, `issue`, `training`, `archived`

**Examples:**
```bash
# Start review
n5 review status out_2fa3949708b2 in_review --sentiment good --reviewer V

# Approve with quality scores
n5 review status out_2fa3949708b2 approved \
  --score tone=9 \
  --score clarity=8 \
  --score completeness=10

# Archive with dry-run
n5 review status out_2fa3949708b2 archived --dry-run
```

---

### `n5 review comment`
Add threaded comments to an output (max 3 thread levels).

```bash
n5 review comment <output_id> \
  --body "<comment_text>" \
  [--author "Name"] \
  [--context "Section reference"] \
  [--parent cmt_XXX] \
  [--tags tag1,tag2] \
  [--dry-run]
```

**Examples:**
```bash
# Add top-level comment
n5 review comment out_2fa3949708b2 --body "Excellent documentation!" --author V

# Comment on specific section
n5 review comment out_2fa3949708b2 \
  --body "Consider shortening this section" \
  --context "lines 45-67" \
  --tags structure

# Reply to comment
n5 review comment out_2fa3949708b2 \
  --body "Agreed, will revise" \
  --parent cmt_abc123456789
```

---

### `n5 review export`
Export filtered reviews to JSON for training data preparation.

```bash
n5 review export \
  [--status <status>] \
  [--sentiment <sentiment>] \
  [--output /path/to/file.json] \
  [--dry-run]
```

**Examples:**
```bash
# Export excellent outputs
n5 review export --sentiment excellent --output /tmp/training-excellent.json

# Export all approved
n5 review export --status approved

# Preview export
n5 review export --sentiment good --dry-run
```

---

## Typical Workflows

### 1. Flag → Review → Approve
```bash
# Flag output
OUTPUT_ID=$(n5 review add Documents/analysis.md --title "Market Analysis" --tags analysis | grep "out_" | awk '{print $3}')

# Start review
n5 review status $OUTPUT_ID in_review --reviewer V

# Add feedback
n5 review comment $OUTPUT_ID --body "Strong data analysis, consider adding more visuals"

# Approve
n5 review status $OUTPUT_ID approved --sentiment excellent --score clarity=9 --score completeness=10
```

### 2. Identify Issues → Fix → Re-review
```bash
# Flag problematic output
n5 review status out_XXX issue --sentiment issue --score adherence=3 --note "Missed key requirements"

# Add detailed feedback
n5 review comment out_XXX --body "Missing sections 2-4 from the brief" --context "requirements doc"

# After fixes, re-review
n5 review status out_XXX in_review --sentiment good
n5 review status out_XXX approved
```

### 3. Export Training Data
```bash
# Export high-quality outputs
n5 review export --sentiment excellent --output ~/training-data/excellent.json
n5 review export --sentiment good --output ~/training-data/good.json

# Export issues for fine-tuning
n5 review export --sentiment issue --output ~/training-data/issues.json
```

---

## Quality Dimensions

Common quality dimensions to score (0-10 scale):

- **adherence_to_instructions** - How well output follows the brief
- **tone** - Appropriateness and consistency of voice
- **clarity** - Readability and coherence
- **completeness** - Coverage of required topics
- **formatting** - Structure and presentation
- **accuracy** - Factual correctness
- **efficiency** - Conciseness without loss of meaning

**Example:**
```bash
n5 review status out_XXX approved \
  --score adherence_to_instructions=10 \
  --score tone=9 \
  --score clarity=10 \
  --score completeness=9 \
  --score formatting=8
```

---

## Integration Points

### With Knowledge System
- Review outputs can reference Knowledge articles
- Approved outputs can be promoted to Knowledge

### With Lists System
- Reviews stored in `Lists/output_reviews.jsonl`
- Comments stored in `Lists/output_reviews_comments.jsonl`
- Can be processed by list management commands

### With Scheduled Tasks
```bash
# Weekly review reminder
n5 agent add "FREQ=WEEKLY;BYDAY=FR;BYHOUR=16;BYMINUTE=0" \
  "List all pending reviews and email summary: n5 review list --status pending"
```

### With Training Pipelines
```bash
# Export excellent outputs for fine-tuning
n5 review export --sentiment excellent --output /tmp/training.json
# Process with ML pipeline...
```

---

## Technical Details

### Data Model

**Review Entry:**
```json
{
  "id": "out_XXXXXXXXXXXX",
  "created_at": "2025-10-19T15:35:44.751874+00:00",
  "updated_at": "2025-10-19T15:35:56.330499+00:00",
  "archived_at": null,
  "title": "Output title",
  "type": "file|message|url",
  "reference": "/path/to/file or URL or message excerpt",
  "content_hash": "sha256:...",
  "provenance": {
    "conversation_id": "con_XXX",
    "thread_name": "optional",
    "script_path": "optional",
    "pipeline_run": "optional",
    "parent_output_id": "optional"
  },
  "review": {
    "status": "pending|in_review|approved|issue|training|archived",
    "sentiment": "excellent|good|acceptable|issue",
    "reviewed_by": "V",
    "reviewed_at": "2025-10-19T15:35:56.330499+00:00",
    "quality_dimensions": {
      "clarity": 10.0,
      "completeness": 9.0
    }
  },
  "tags": ["tag1", "tag2"],
  "notes": "Additional context",
  "comment_count": 1,
  "latest_comment_at": "2025-10-19T15:35:56.330499+00:00"
}
```

**Comment Entry:**
```json
{
  "id": "cmt_XXXXXXXXXXXX",
  "output_id": "out_XXXXXXXXXXXX",
  "created_at": "2025-10-19T15:35:56.330499+00:00",
  "updated_at": "2025-10-19T15:35:56.330499+00:00",
  "author": "V",
  "body": "Comment text",
  "context": "Optional reference to specific section",
  "parent_comment_id": null,
  "thread_depth": 0,
  "tags": ["tag1"],
  "resolved": false
}
```

### Schema Validation

All entries are validated against JSON schemas before write:
- `N5/schemas/output-review.schema.json`
- `N5/schemas/output-review-comment.schema.json`

### Safety Features

- **Dry-run mode** - Preview all operations with `--dry-run`
- **Schema validation** - Prevents invalid data from being written
- **Content hashing** - Detects changes to reviewed files
- **Atomic writes** - All JSONL writes are atomic
- **Error handling** - Comprehensive try/except with context logging

---

## Known Issues

1. **Schema Mismatch (P21)** - `notes` field must be string, not nullable. Current workaround: CLI converts None to empty string. **Fix:** Update schema to allow `["string", "null"]`.

2. **No deduplication** - Same output can be added multiple times. Consider adding content_hash check.

3. **No archival workflow** - Archived reviews stay in main JSONL. Consider separate archive file.

---

## Future Enhancements

- **Web UI** - Visual review dashboard
- **Batch operations** - Bulk status updates
- **ML integration** - Auto-sentiment detection
- **Version tracking** - Track changes to reviewed outputs
- **Team features** - Multi-reviewer workflows
- **Stats dashboard** - Review velocity, quality trends

---

## Development History

- **2025-10-17** - Initial spec (Worker 1: Schemas)
- **2025-10-18** - Core implementation (Worker 2: ReviewManager)
- **2025-10-19** - CLI + Commands (Workers 3-4)
- **2025-10-19** - Documentation complete

**Orchestrator:** con_YSy4ld4J113LZQ9A  
**Workers:** 4 (Schemas, Manager, CLI, Commands)  
**Total Time:** ~2 hours

---

## References

- `file N5/schemas/output-review.schema.json`
- `file N5/schemas/output-review-comment.schema.json`
- `file N5/scripts/review_manager.py`
- `file N5/scripts/review_cli.py`
- `file Recipes/recipes.jsonl` (lines 98-103)
- `file Knowledge/architectural/architectural_principles.md` (P5, P7, P11, P19)

---

*System built following N5 architectural principles: P0 (Rule-of-Two), P1 (Human-Readable), P2 (SSOT), P5 (Anti-Overwrite), P7 (Dry-Run), P19 (Error Handling), P20 (Modular)*
