# Worker 5: Commands Registration

**Orchestrator:** con_YSy4ld4J113LZQ9A\
**Task ID:** W5-COMMANDS\
**Estimated Time:** 25 minutes\
**Dependencies:** Worker 3 (review_cli.py must exist)

---

## Mission

Register all Output Review Tracker commands in `file N5/config/commands.jsonl`     so they're discoverable via the N5 command system and accessible through the `/` slash command interface.

---

## Context

The N5 command system allows users to invoke commands via slash commands in Zo. Need to register all 7 `n5 review` commands with proper metadata, examples, and tags for discoverability.

---

## Prerequisites

Ensure these exist (created by Worker 3):

- `file N5/scripts/review_cli.py`     with all 6 commands working

---

## Deliverable

Add 7 command entries to: `file N5/config/commands.jsonl` 

### Commands to Register

1. `n5 review add` - Add output for review
2. `n5 review list` - List reviews with filters
3. `n5 review show` - Show full review details
4. `n5 review status` - Update status/sentiment
5. `n5 review comment` - Add threaded comment
6. `n5 review export` - Export to JSON for training
7. `n5 review` - Show help (parent command)

---

## Command Entry Template

Each command entry in `file commands.jsonl`     should follow this structure:

```json
{
  "name": "n5 review add",
  "description": "Add an output (file, message, image, etc.) for quality review and tracking. Automatically detects type and captures provenance including conversation ID, thread, and script context.",
  "entrypoint": "python3 /home/workspace/N5/scripts/review_cli.py add",
  "category": "quality",
  "tags": ["review", "quality", "tracking", "training"],
  "examples": [
    "n5 review add Documents/meeting-notes.md --title \"Q4 Planning Notes\"",
    "n5 review add /tmp/output.txt --tags \"generated,test\" --sentiment good",
    "n5 review add https://docs.google.com/document/d/xyz --type url"
  ],
  "schema": {
    "reference": {"type": "string", "required": true, "description": "File path, URL, or message to review"},
    "title": {"type": "string", "description": "Title (auto-detected from filename if not provided)"},
    "type": {"type": "string", "enum": ["file", "message", "image", "video", "transcript", "url"]},
    "conversation_id": {"type": "string", "description": "Conversation ID (auto-detected)"},
    "tags": {"type": "string", "description": "Comma-separated tags"},
    "notes": {"type": "string", "description": "Additional notes"}
  }
}
```

---

## Full Commands to Add

### 1. n5 review (parent command)

```json
{
  "name": "n5 review",
  "description": "Output Review Tracker - Centralized system for tracking generated outputs (files, messages, images) for quality review and training data collection. Maintains full provenance and supports workflow states, comments, and export.",
  "entrypoint": "python3 /home/workspace/N5/scripts/review_cli.py --help",
  "category": "quality",
  "tags": ["review", "quality", "tracking", "training", "help"],
  "examples": [
    "n5 review --help",
    "n5 review add --help",
    "n5 review list --help"
  ]
}
```

### 2. n5 review add

```json
{
  "name": "n5 review add",
  "description": "Add an output for quality review. Auto-detects type (file/message/url) and captures full provenance (conversation, thread, script). Supports custom tags and notes.",
  "entrypoint": "python3 /home/workspace/N5/scripts/review_cli.py add",
  "category": "quality",
  "tags": ["review", "quality", "add", "tracking"],
  "examples": [
    "n5 review add Documents/article.md --title \"Blog Post Draft\"",
    "n5 review add /tmp/generated-image.png --tags \"dalle,landscape\"",
    "n5 review add https://example.com/doc --type url --notes \"External reference\""
  ]
}
```

### 3. n5 review list

```json
{
  "name": "n5 review list",
  "description": "List all reviews with optional filters by status, sentiment, type, or tags. Shows formatted table with ID, title, status, sentiment, and comment count.",
  "entrypoint": "python3 /home/workspace/N5/scripts/review_cli.py list",
  "category": "quality",
  "tags": ["review", "quality", "list", "filter"],
  "examples": [
    "n5 review list",
    "n5 review list --status pending",
    "n5 review list --sentiment excellent --tags training"
  ]
}
```

### 4. n5 review show

```json
{
  "name": "n5 review show",
  "description": "Show full details for a specific review including provenance, quality scores, status history, and all threaded comments.",
  "entrypoint": "python3 /home/workspace/N5/scripts/review_cli.py show",
  "category": "quality",
  "tags": ["review", "quality", "details"],
  "examples": [
    "n5 review show out_x7k9m2n4p8q1",
    "n5 review show out_abc123def456"
  ]
}
```

### 5. n5 review status

```json
{
  "name": "n5 review status",
  "description": "Update review status, sentiment, and quality scores. Supports workflow transitions: pending → in_review → approved/issue → training/archived.",
  "entrypoint": "python3 /home/workspace/N5/scripts/review_cli.py status",
  "category": "quality",
  "tags": ["review", "quality", "status", "workflow"],
  "examples": [
    "n5 review status out_x7k9m2n4p8q1 in_review --sentiment good",
    "n5 review status out_abc123 approved --reviewer V --score tone=9 --score clarity=8",
    "n5 review status out_xyz789 archived --note \"Superseded by v2\""
  ]
}
```

### 6. n5 review comment

```json
{
  "name": "n5 review comment",
  "description": "Add threaded comment to a review. Supports up to 3 levels of threading, context excerpts, and tags. Use for detailed feedback on specific aspects (tone, structure, accuracy, etc.).",
  "entrypoint": "python3 /home/workspace/N5/scripts/review_cli.py comment",
  "category": "quality",
  "tags": ["review", "quality", "comment", "feedback"],
  "examples": [
    "n5 review comment out_x7k9m2n4p8q1 --body \"Great clarity in the introduction\"",
    "n5 review comment out_abc123 --body \"Consider simplifying this section\" --context \"Lines 45-52\" --tags tone",
    "n5 review comment out_xyz789 --body \"Agreed, good point\" --parent cmt_parent123"
  ]
}
```

### 7. n5 review export

```json
{
  "name": "n5 review export",
  "description": "Export reviews to JSON for training data collection. Filter by sentiment (excellent/good) or status. Includes full review data, comments, and provenance.",
  "entrypoint": "python3 /home/workspace/N5/scripts/review_cli.py export",
  "category": "quality",
  "tags": ["review", "quality", "export", "training", "data"],
  "examples": [
    "n5 review export --sentiment excellent",
    "n5 review export --status approved --output /tmp/training-data.json",
    "n5 review export --sentiment good --status training"
  ]
}
```

---

## Implementation Steps

1. **Open commands.jsonl**

   ```bash
   nano /home/workspace/N5/config/commands.jsonl
   ```

2. **Add all 7 command entries** (one JSON object per line)

   - Ensure valid JSONL format (one complete JSON object per line)
   - No trailing commas
   - Preserve existing commands

3. **Validate JSON**

   ```bash
   # Test each line is valid JSON
   while IFS= read -r line; do
     echo "$line" | jq empty || echo "Invalid JSON: $line"
   done < /home/workspace/N5/config/commands.jsonl
   ```

4. **Test command discovery**

   ```bash
   # Check commands are registered
   grep "n5 review" /home/workspace/N5/config/commands.jsonl | wc -l
   # Should output: 7
   
   # Verify specific commands
   grep "n5 review add" /home/workspace/N5/config/commands.jsonl
   grep "n5 review list" /home/workspace/N5/config/commands.jsonl
   ```

---

## Success Criteria

- ✅ All 7 commands added to commands.jsonl
- ✅ Valid JSONL syntax (each line is complete JSON object)
- ✅ No duplicate command names
- ✅ Descriptions clear and complete
- ✅ Examples helpful and realistic
- ✅ Tags appropriate for discoverability

---

## Testing

```markdown
# Verify command count
grep "n5 review" /home/workspace/N5/config/commands.jsonl | wc -l

# Validate JSONL syntax
cat /home/workspace/N5/config/commands.jsonl | while read line; do echo "$line" | jq -c .; done

# Test each command is findable
for cmd in "n5 review" "n5 review add" "n5 review list" "n5 review show" "n5 review status" "n5 review comment" "n5 review export"; do
  echo "Checking: $cmd"
  grep -q "\"name\": \"$cmd\"" /home/workspace/N5/config/commands.jsonl && echo "  ✓ Found" || echo "  ✗ Missing"
done
```

---

## Additional Documentation

Create user-facing documentation:

**File:** `file Documents/output-review-tracker.md` 

```markdown
# Output Review Tracker

**Purpose:** Centralized tracking of generated outputs for quality review and training data collection

---

## Quick Start

### Add output for review
\`\`\`bash
n5 review add path/to/file.md --title "Description"
\`\`\`

### List all reviews
\`\`\`bash
n5 review list
n5 review list --status pending
n5 review list --sentiment excellent
\`\`\`

### Update status
\`\`\`bash
n5 review status <output_id> approved --sentiment good
\`\`\`

### Add comments
\`\`\`bash
n5 review comment <output_id> --body "Great work!"
\`\`\`

### Export for training
\`\`\`bash
n5 review export --sentiment excellent --output training.json
\`\`\`

---

## Workflow States

1. **pending** - Just added, awaiting review
2. **in_review** - Currently being reviewed
3. **approved** - Passed review, good quality
4. **issue** - Has problems, needs revision
5. **training** - Approved for training data
6. **archived** - No longer relevant

---

## Sentiment Levels

- **excellent** - Outstanding quality, exemplar
- **good** - Solid quality, usable
- **acceptable** - Meets minimum bar
- **issue** - Below standard, needs work

---

## Storage

- **JSONL (SSOT):** `Lists/output_reviews.jsonl`
- **Comments:** `Lists/output_reviews_comments.jsonl`
- **Spreadsheet:** `Lists/output_reviews.sheet.json`
- **Schemas:** `N5/schemas/output-review*.schema.json`

---

## Provenance Tracking

Each review automatically captures:
- Conversation ID
- Thread name
- Script path (if generated by script)
- Pipeline/run ID (if part of multi-step process)
- Content hash (detects file changes)
- Timestamps (created, updated, archived)

---

## Commands Reference

See: `n5 review --help`
```

---

## Report Back

When complete, report:

1. All 7 commands registered successfully
2. Validation passed (JSONL syntax correct)
3. Sample grep output showing registered commands
4. Documentation created
5. Ready for integration testing

---

**Orchestrator Contact:** con_YSy4ld4J113LZQ9A\
**Created:** 2025-10-19 15:30 ET