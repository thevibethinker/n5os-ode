# Worker 4: Command Registration

**Orchestrator:** con_YSy4ld4J113LZQ9A  
**Task ID:** W4-COMMANDS  
**Estimated Time:** 20 minutes  
**Dependencies:** Worker 3 (review_cli.py must exist)

---

## Mission

Register all `n5 review` commands in `commands.jsonl` so they're discoverable via the N5 command system and can be invoked with proper wrappers.

---

## Context

N5's command system allows users to invoke scripts via `n5 <command>` syntax. We need to register all review subcommands with proper metadata, descriptions, and examples.

---

## Deliverable

**File:** `N5/config/commands.jsonl`

### Requirements

1. Add entries for each review subcommand
2. Include descriptions, examples, tags
3. Follow existing command patterns in commands.jsonl
4. Validate JSON syntax

---

## Entries to Add

Append these lines to `N5/config/commands.jsonl`:

```json
{"command": "review-add", "script": "N5/scripts/review_cli.py", "args": ["add"], "description": "Flag an output (file, message, image, etc.) for quality review with full provenance tracking", "usage": "n5 review add <reference> --title \"Description\" --type file [--tags tag1,tag2] [--notes \"Additional context\"]", "examples": ["n5 review add Documents/meeting-notes.md --title \"Weekly sync notes\" --type file --tags meeting,notes", "n5 review add https://docs.google.com/doc/123 --title \"Strategy doc\" --type url"], "tags": ["review", "quality", "tracking"], "added": "2025-10-17"}
{"command": "review-list", "script": "N5/scripts/review_cli.py", "args": ["list"], "description": "List tracked outputs with optional filters by status, sentiment, tags, type, or conversation", "usage": "n5 review list [--status pending|in_review|approved|issue|training|archived] [--sentiment excellent|good|acceptable|issue] [--tags tag1,tag2] [--type file|message|image|video|transcript|url] [--conversation-id con_XXX] [--json]", "examples": ["n5 review list --status pending", "n5 review list --sentiment issue --tags documentation", "n5 review list --json"], "tags": ["review", "list", "query"], "added": "2025-10-17"}
{"command": "review-show", "script": "N5/scripts/review_cli.py", "args": ["show"], "description": "Show full details for a tracked output including provenance, quality scores, and threaded comments", "usage": "n5 review show <output_id> [--with-content] [--json]", "examples": ["n5 review show out_x7k9m2n4p8q1", "n5 review show out_x7k9m2n4p8q1 --with-content"], "tags": ["review", "details"], "added": "2025-10-17"}
{"command": "review-status", "script": "N5/scripts/review_cli.py", "args": ["status"], "description": "Update review workflow status with optional reviewer and resolution note", "usage": "n5 review status <output_id> <new_status> [--reviewer \"Name\"] [--note \"Resolution details\"] [--dry-run]", "examples": ["n5 review status out_x7k9m2n4p8q1 in_review --reviewer V", "n5 review status out_x7k9m2n4p8q1 approved --note \"Ready for training\"", "n5 review status out_x7k9m2n4p8q1 archived --dry-run"], "tags": ["review", "workflow", "status"], "added": "2025-10-17"}
{"command": "review-sentiment", "script": "N5/scripts/review_cli.py", "args": ["sentiment"], "description": "Rate output quality with sentiment and optional dimension scores (0-10 scale)", "usage": "n5 review sentiment <output_id> <sentiment> [--score dimension=value] [--json]", "examples": ["n5 review sentiment out_x7k9m2n4p8q1 excellent", "n5 review sentiment out_x7k9m2n4p8q1 issue --score adherence_to_instructions=3 --score tone=4", "n5 review sentiment out_x7k9m2n4p8q1 good --score formatting=8 --score completeness=9"], "tags": ["review", "quality", "rating"], "added": "2025-10-17"}
{"command": "review-comment", "script": "N5/scripts/review_cli.py", "args": ["comment"], "description": "Add threaded comment to an output with optional context and tags (max 3 thread levels)", "usage": "n5 review comment <output_id> \"<comment_text>\" [--author \"Name\"] [--context \"Section reference\"] [--reply-to cmt_XXX] [--tags tag1,tag2] [--json]", "examples": ["n5 review comment out_x7k9m2n4p8q1 \"Excellent tone in the introduction\"", "n5 review comment out_x7k9m2n4p8q1 \"Consider shortening this section\" --context \"lines 45-67\" --tags structure", "n5 review comment out_x7k9m2n4p8q1 \"Agreed, will revise\" --reply-to cmt_abc123456789"], "tags": ["review", "comment", "feedback"], "added": "2025-10-17"}
{"command": "review-export", "script": "N5/scripts/review_cli.py", "args": ["export"], "description": "Export outputs with specified sentiment to JSON for training data preparation", "usage": "n5 review export [--sentiment excellent|good|acceptable|issue] [--output /path/to/file.json]", "examples": ["n5 review export --sentiment excellent --output /tmp/training-excellent.json", "n5 review export --sentiment issue"], "tags": ["review", "export", "training"], "added": "2025-10-17"}
```

---

## Implementation Steps

1. Read current `N5/config/commands.jsonl`
2. Validate it's valid JSONL
3. Append the 7 new entries above
4. Validate updated file is still valid JSONL
5. Verify no duplicate commands exist

---

## Validation Script

```bash
# Check JSON validity
cat N5/config/commands.jsonl | while read line; do echo "$line" | jq . > /dev/null || echo "Invalid JSON: $line"; done

# Check for duplicates
cat N5/config/commands.jsonl | jq -r '.command' | sort | uniq -d

# Count review commands
cat N5/config/commands.jsonl | jq -r 'select(.command | startswith("review-")) | .command' | wc -l
# Should output: 7
```

---

## Success Criteria

- ✅ All 7 commands registered
- ✅ Valid JSONL syntax
- ✅ No duplicate command names
- ✅ Descriptions clear and complete
- ✅ Examples helpful and realistic
- ✅ Tags appropriate

---

## Report Back

1. Commands registered
2. Validation passed
3. Count: 7 review commands added
4. Ready for Worker 5

---

**Orchestrator:** con_YSy4ld4J113LZQ9A  
**Created:** 2025-10-17 21:01 ET
