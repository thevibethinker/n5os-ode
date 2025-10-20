# Output Review Tracker - System Design

**Version:** 1.0  
**Date:** 2025-10-17  
**Status:** Design Phase

---

## Purpose

Centralized tracking system for generated outputs (markdown files, messages, images, transcripts, external URLs) with full provenance for quality review and training refinement. Enables flagging outputs for review without copy-pasting content, preserving exact lineage back to conversation/script/pipeline that produced them.

---

## Core Requirements

1. **Track local files** (markdown, images, transcripts) and external URLs (Google Docs/Drive)
2. **Full provenance**: conversation ID, thread, script path, command name, pipeline/run ID
3. **Review workflow**: statuses (flagged → under_review → resolved → archived)
4. **Quality assessment**: sentiment (good/bad/excellent/issue), tags, threaded comments
5. **Hybrid storage**: JSONL (SSOT) + companion spreadsheet (quick scanning)
6. **CLI interface**: `n5 review add`, `n5 review comment`, `n5 review status`, etc.
7. **Threaded comments** with author, timestamp, and context

---

## Architecture

### Storage

```
Lists/
├── output_reviews.jsonl           # SSOT - one entry per output
├── output_reviews.sheet.json      # Companion spreadsheet for scanning
└── output_reviews_comments.jsonl  # Threaded comments registry
```

### Data Model

#### Output Review Entry (output_reviews.jsonl)

```json
{
  "id": "or_20251017_abc123",
  "created_at": "2025-10-17T20:44:12Z",
  "updated_at": "2025-10-17T20:44:12Z",
  "title": "Career transition guide output",
  "type": "file",
  "reference": "Documents/career-guide.md",
  "content_hash": "sha256:abc123...",
  "provenance": {
    "conversation_id": "con_XYZ",
    "thread_id": "thread_ABC",
    "thread_title": "Career guide generation",
    "script_path": "N5/scripts/generate_guide.py",
    "command_name": "generate-career-guide",
    "pipeline_run_id": "run_20251017_001",
    "parent_output_id": null,
    "timestamp": "2025-10-17T20:30:00Z"
  },
  "review": {
    "status": "flagged",
    "sentiment": "issue",
    "flagged_by": "V",
    "flagged_reason": "Tone too formal, length exceeded target",
    "reviewer": null,
    "resolution_note": null
  },
  "quality_dimensions": {
    "instruction_adherence": null,
    "format_compliance": null,
    "length_target": "800-1000 words",
    "length_actual": "1450 words",
    "style": "conversational",
    "tone": "empathetic"
  },
  "tags": ["training", "career-guide", "tone-issue", "length-issue"],
  "comment_count": 0,
  "latest_comment_at": null
}
```

#### Comment Entry (output_reviews_comments.jsonl)

```json
{
  "id": "cmt_20251017_xyz789",
  "output_review_id": "or_20251017_abc123",
  "parent_comment_id": null,
  "created_at": "2025-10-17T21:00:00Z",
  "author": "V",
  "comment": "Paragraph 3 is particularly problematic - sounds like corporate speak rather than coaching voice.",
  "context": {
    "line_numbers": "45-52",
    "excerpt": "It is imperative that one leverages..."
  },
  "tags": ["tone", "paragraph-3"]
}
```

---

## CLI Commands

### n5 review add

```bash
n5 review add <file_or_url> \
  --title "Brief description" \
  --sentiment [excellent|good|issue|bad] \
  --reason "Why flagged" \
  --tags "tag1,tag2" \
  --conversation-id "con_XYZ" \
  --script "path/to/script.py" \
  --command "command-name" \
  --pipeline-run "run_id" \
  --quality key=value \
  --dry-run
```

**Auto-detection:**
- Conversation ID from workspace context
- Script path from `N5_SCRIPT_PATH` env var
- Pipeline run from `N5_PIPELINE_RUN` env var
- Content hash computed automatically for files

**Examples:**

```bash
# Flag problematic output
n5 review add Documents/career-guide.md \
  --title "Career transition guide" \
  --sentiment issue \
  --reason "Tone too formal, length exceeded"

# Flag excellent output for training
n5 review add Documents/perfect-email.md \
  --sentiment excellent \
  --tags "training,email,voice"

# Flag external URL
n5 review add "https://docs.google.com/document/d/abc123" \
  --title "Client proposal draft" \
  --sentiment good
```

### n5 review list

```bash
n5 review list \
  --status [flagged|under_review|resolved|archived] \
  --sentiment [excellent|good|issue|bad] \
  --tags "tag1,tag2" \
  --from "2025-10-01" \
  --to "2025-10-31" \
  --conversation "con_XYZ" \
  --format [table|json|sheet]
```

### n5 review show

```bash
n5 review show <output_id> \
  --with-comments \
  --with-content  # Show first 50 lines of referenced file
```

### n5 review status

```bash
n5 review status <output_id> <new_status> \
  --note "Resolution explanation" \
  --reviewer "V"
```

**Valid transitions:**
- `flagged` → `under_review` → `resolved` → `archived`
- `flagged` → `archived` (skip review)

### n5 review comment

```bash
# Add comment
n5 review comment <output_id> \
  --text "This paragraph needs work" \
  --lines "45-52" \
  --excerpt "First few words..." \
  --tags "tone,paragraph-3"

# Reply to comment (threaded)
n5 review comment <output_id> \
  --reply-to <comment_id> \
  --text "Agreed, let's rephrase"
```

### n5 review export

```bash
n5 review export \
  --sentiment excellent \
  --format jsonl \
  --output training/positive-examples.jsonl \
  --include-content
```

---

## Workflow States

```
flagged ──────────────────┐
   │                       │
   ├──> under_review       │
   │         │              │
   │         └──> resolved ─┤
   │                        │
   └────────────────────────┴──> archived
```

**State descriptions:**
- `flagged`: New entry, waiting for review
- `under_review`: Reviewer assigned, analysis in progress
- `resolved`: Issue addressed or pattern documented
- `archived`: No longer active, historical record

---

## Implementation Plan

### Phase 1: Core Infrastructure (60 min)

1. **Schemas** (15 min)
   - `N5/schemas/output-review.schema.json`
   - `N5/schemas/output-review-comment.schema.json`

2. **Review Manager** (30 min)
   - `N5/scripts/review_manager.py`
   - CRUD operations (add, get, update, list)
   - State machine validation
   - Content hash computation
   - Provenance auto-detection

3. **Tests** (15 min)
   - Basic CRUD operations
   - State transitions
   - Schema validation

### Phase 2: CLI Interface (45 min)

4. **CLI Script** (30 min)
   - `N5/scripts/review_cli.py`
   - Argument parsing
   - Output formatting (table, JSON)
   - Error handling

5. **Command Registration** (15 min)
   - Add to `N5/config/commands.jsonl`
   - Create `N5/commands/review.md`

### Phase 3: Spreadsheet Sync (30 min)

6. **Sync Script** (20 min)
   - `N5/scripts/review_sync.py`
   - JSONL → sheet conversion
   - Rebuild from source

7. **Integration Tests** (10 min)
   - End-to-end workflow
   - Multi-user scenarios

### Phase 4: Comments System (30 min)

8. **Comment Manager** (20 min)
   - Add comment functionality
   - Threaded replies
   - Context tracking

9. **Tests** (10 min)
   - Comment threads
   - Orphan detection

**Total estimated time: 2.75 hours**

---

## Testing Checklist

- [ ] Add file review with full provenance
- [ ] Add URL review (external)
- [ ] Add review with auto-detected conversation_id
- [ ] List reviews with filters (status, sentiment, tags, date)
- [ ] Update review status (valid transitions)
- [ ] Reject invalid state transition
- [ ] Add comment with context (lines, excerpt)
- [ ] Add threaded reply to comment
- [ ] Sync JSONL to spreadsheet
- [ ] Validate content hash on file modification
- [ ] Export outputs for training
- [ ] Dry-run operations
- [ ] Schema validation
- [ ] Fresh thread test

---

## Principles Applied

- **P0 (Rule-of-Two)**: Design doc + 2 schemas for review
- **P1 (Human-Readable)**: JSONL + companion sheet
- **P2 (SSOT)**: JSONL source, sheet derived
- **P5 (Anti-Overwrite)**: Append-only JSONL
- **P7 (Dry-Run)**: All commands support `--dry-run`
- **P11 (Failure Modes)**: Error handling documented
- **P18 (Verify State)**: Content hash validation
- **P19 (Error Handling)**: Schema + state machine enforcement
- **P20 (Modular)**: Separate scripts for CLI, core, sync
- **P21 (Document Assumptions)**: Auto-detection documented
- **P22 (Language)**: Python for data processing + CLI

---

## Open Questions for V

1. Should sentiment be required at creation time, or can it be added later?
2. Do you want automatic weekly/monthly review summary reports?
3. Should we support batch import (scan directory for existing outputs)?
4. Do you need separate "reviewed_at" timestamp from "updated_at"?
5. Should we track who archived an item (separate from resolver)?

---

## Next Steps

1. ✅ Design complete - review with V
2. ⏳ Get approval on schema and CLI interface
3. ⏳ Clarify open questions
4. ⏳ Implement Phase 1 (core infrastructure)
5. ⏳ Implement Phase 2 (CLI)
6. ⏳ Implement Phase 3 (spreadsheet sync)
7. ⏳ Implement Phase 4 (comments)
8. ⏳ Run full test checklist
9. ⏳ Update N5 documentation

---

**Status:** Design ready for review  
**Estimated Implementation:** 2-3 hours  
**Priority:** Medium (training infrastructure)
