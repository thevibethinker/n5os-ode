# Worker 5: Integration Testing & Documentation

**Orchestrator:** con_YSy4ld4J113LZQ9A  
**Task ID:** W5-INTEGRATION  
**Estimated Time:** 30 minutes  
**Dependencies:** Workers 1-4 complete

---

## Mission

Run comprehensive integration tests across the entire Output Review Tracker system, verify all components work together, and create user documentation.

---

## Context

This is the final validation before deployment. Must verify end-to-end workflows, error handling, edge cases, and ensure fresh conversations can use the system (P12).

---

## Deliverables

### 1. Integration Test Script

**File:** `N5/scripts/test_review_system.py`

```python
#!/usr/bin/env python3
"""
Integration tests for Output Review Tracker system.

Tests end-to-end workflows, validation, persistence, and CLI.
"""

import json
import sys
import tempfile
import subprocess
from pathlib import Path

WORKSPACE = Path("/home/workspace")
REVIEWS_JSONL = WORKSPACE / "Lists/output_reviews.jsonl"
COMMENTS_JSONL = WORKSPACE / "Lists/output_reviews_comments.jsonl"


def run_cmd(cmd):
    """Run CLI command and return result."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def test_add_output():
    """Test adding an output."""
    print("TEST: Add output...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("Test content")
        test_file = f.name
    
    code, stdout, stderr = run_cmd(
        f'python3 N5/scripts/review_cli.py add {test_file} '
        f'--title "Test output" --type file --tags test,integration --json'
    )
    
    assert code == 0, f"Failed to add output: {stderr}"
    
    entry = json.loads(stdout)
    assert entry['title'] == "Test output"
    assert entry['type'] == "file"
    assert 'test' in entry['tags']
    
    print(f"  ✓ Added: {entry['id']}")
    return entry['id']


def test_list_outputs(output_id):
    """Test listing with filters."""
    print("TEST: List outputs...")
    
    code, stdout, stderr = run_cmd(
        'python3 N5/scripts/review_cli.py list --tags test --json'
    )
    
    assert code == 0, f"Failed to list: {stderr}"
    
    results = json.loads(stdout)
    assert len(results) > 0, "No results found"
    assert any(r['id'] == output_id for r in results), "Test output not in list"
    
    print(f"  ✓ Found {len(results)} entries")


def test_show_output(output_id):
    """Test showing details."""
    print("TEST: Show output...")
    
    code, stdout, stderr = run_cmd(
        f'python3 N5/scripts/review_cli.py show {output_id} --json'
    )
    
    assert code == 0, f"Failed to show: {stderr}"
    
    data = json.loads(stdout)
    assert data['output']['id'] == output_id
    assert 'comments' in data
    
    print(f"  ✓ Retrieved details")


def test_update_status(output_id):
    """Test status workflow."""
    print("TEST: Update status...")
    
    # pending → in_review
    code, stdout, stderr = run_cmd(
        f'python3 N5/scripts/review_cli.py status {output_id} in_review --reviewer V --json'
    )
    assert code == 0, f"Failed to update status: {stderr}"
    
    entry = json.loads(stdout)
    assert entry['review']['status'] == "in_review"
    assert entry['review']['reviewed_by'] == "V"
    
    # in_review → approved
    code, stdout, stderr = run_cmd(
        f'python3 N5/scripts/review_cli.py status {output_id} approved --json'
    )
    assert code == 0, f"Failed to approve: {stderr}"
    
    print(f"  ✓ Status transitions work")


def test_sentiment(output_id):
    """Test sentiment and quality scores."""
    print("TEST: Update sentiment...")
    
    code, stdout, stderr = run_cmd(
        f'python3 N5/scripts/review_cli.py sentiment {output_id} excellent '
        f'--score adherence_to_instructions=9 --score tone=10 --json'
    )
    
    assert code == 0, f"Failed to update sentiment: {stderr}"
    
    entry = json.loads(stdout)
    assert entry['review']['sentiment'] == "excellent"
    assert entry['review']['quality_dimensions']['tone'] == 10
    
    print(f"  ✓ Sentiment and scores updated")


def test_comments(output_id):
    """Test adding comments with threading."""
    print("TEST: Add comments...")
    
    # Top-level comment
    code, stdout, stderr = run_cmd(
        f'python3 N5/scripts/review_cli.py comment {output_id} '
        f'"Top-level comment" --author V --json'
    )
    assert code == 0, f"Failed to add comment: {stderr}"
    
    comment1 = json.loads(stdout)
    assert comment1['thread_depth'] == 0
    
    # Reply (depth 1)
    code, stdout, stderr = run_cmd(
        f'python3 N5/scripts/review_cli.py comment {output_id} '
        f'"Reply to top" --reply-to {comment1["id"]} --json'
    )
    assert code == 0, f"Failed to add reply: {stderr}"
    
    comment2 = json.loads(stdout)
    assert comment2['thread_depth'] == 1
    
    # Nested reply (depth 2)
    code, stdout, stderr = run_cmd(
        f'python3 N5/scripts/review_cli.py comment {output_id} '
        f'"Nested reply" --reply-to {comment2["id"]} --json'
    )
    assert code == 0, f"Failed to add nested reply: {stderr}"
    
    comment3 = json.loads(stdout)
    assert comment3['thread_depth'] == 2
    
    # Verify comment count updated
    code, stdout, stderr = run_cmd(
        f'python3 N5/scripts/review_cli.py show {output_id} --json'
    )
    data = json.loads(stdout)
    assert data['output']['comment_count'] == 3
    
    print(f"  ✓ Comments and threading work")


def test_export():
    """Test export for training."""
    print("TEST: Export...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        export_file = f.name
    
    code, stdout, stderr = run_cmd(
        f'python3 N5/scripts/review_cli.py export --sentiment excellent --output {export_file}'
    )
    
    assert code == 0, f"Failed to export: {stderr}"
    
    with open(export_file, 'r') as f:
        data = json.load(f)
    
    assert len(data) > 0, "Export is empty"
    assert all(r['review']['sentiment'] == 'excellent' for r in data)
    
    print(f"  ✓ Exported {len(data)} entries")


def test_spreadsheet_sync():
    """Test spreadsheet sync."""
    print("TEST: Spreadsheet sync...")
    
    sheet = json.loads((WORKSPACE / "Lists/output_reviews.sheet.json").read_text())
    rows = sheet['worksheets'][0]['data']
    
    # Check test entry is in spreadsheet
    test_rows = [r for r in rows if 'test' in str(r[5])]  # tags column
    assert len(test_rows) > 0, "Test entries not synced to spreadsheet"
    
    print(f"  ✓ Spreadsheet has {len(rows)} rows")


def test_dry_run():
    """Test dry-run mode."""
    print("TEST: Dry-run mode...")
    
    # Count current entries
    entries_before = len(REVIEWS_JSONL.read_text().strip().split('\n')) - 4  # minus header
    
    # Dry-run add
    code, stdout, stderr = run_cmd(
        'python3 N5/scripts/review_cli.py add /tmp/dryrun.md '
        '--title "Dry run test" --type file --dry-run'
    )
    
    assert code == 0, f"Dry-run failed: {stderr}"
    
    # Verify no new entry
    entries_after = len(REVIEWS_JSONL.read_text().strip().split('\n')) - 4
    assert entries_after == entries_before, "Dry-run wrote to file!"
    
    print(f"  ✓ Dry-run does not persist")


def test_schema_validation():
    """Test schema validation rejects invalid entries."""
    print("TEST: Schema validation...")
    
    # Try invalid status
    code, stdout, stderr = run_cmd(
        'python3 N5/scripts/review_cli.py status fake_id invalid_status'
    )
    
    assert code != 0, "Should reject invalid status"
    
    print(f"  ✓ Validation rejects invalid data")


def main():
    print("\n=== Output Review Tracker Integration Tests ===\n")
    
    try:
        output_id = test_add_output()
        test_list_outputs(output_id)
        test_show_output(output_id)
        test_update_status(output_id)
        test_sentiment(output_id)
        test_comments(output_id)
        test_export()
        test_spreadsheet_sync()
        test_dry_run()
        test_schema_validation()
        
        print("\n✅ ALL TESTS PASSED\n")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    exit(main())
```

### 2. User Documentation

**File:** `Documents/output-review-tracker.md`

```markdown
# Output Review Tracker

**Version:** 1.0  
**Date:** 2025-10-17

---

## Overview

The Output Review Tracker is a centralized system for flagging generated outputs (markdown files, messages, images, transcripts, etc.) for quality review. It preserves full provenance so you can trace every output back to the conversation, script, or pipeline that created it.

**Use Cases:**
- Flag problematic outputs for improvement
- Track excellent outputs for training data
- Review multi-step pipeline outputs
- Audit output quality over time
- Build curated training datasets

---

## Quick Start

```bash
# Flag a file for review
n5 review add Documents/meeting-notes.md --title "Weekly sync notes" --type file

# List pending reviews
n5 review list --status pending

# Show details
n5 review show out_x7k9m2n4p8q1

# Update status
n5 review status out_x7k9m2n4p8q1 approved --reviewer V

# Add comment
n5 review comment out_x7k9m2n4p8q1 "Excellent tone in intro section"

# Export excellent outputs for training
n5 review export --sentiment excellent --output /tmp/training.json
```

---

## Data Structure

**Location:** `Lists/output_reviews.jsonl` (SSOT)  
**Companion:** `Lists/output_reviews.sheet.json` (quick scanning)  
**Comments:** `Lists/output_reviews_comments.jsonl`

**Each entry tracks:**
- Reference (file path, URL, identifier)
- Type (file, message, image, video, transcript, url)
- Provenance (conversation, thread, script, pipeline/run)
- Review status (pending → in_review → approved/issue → training/archived)
- Sentiment (excellent, good, acceptable, issue)
- Quality dimensions (scores 0-10 for adherence, formatting, length, style, tone, accuracy, completeness)
- Tags, notes, comments

---

## Workflow States

```
pending → in_review → approved → training
                    ↘ issue → archived
                    
Any state → archived
```

**Transitions:**
- **pending**: Just added, awaiting review
- **in_review**: Actively being reviewed
- **approved**: Passed review, ready for use
- **issue**: Has problems, needs fixing
- **training**: Marked for training data
- **archived**: No longer active

---

## Commands

### n5 review add

Flag an output for review.

```bash
n5 review add <reference> --title "Description" --type <type> [options]
```

**Options:**
- `--conversation-id con_XXX` - Override auto-detected conversation
- `--script-path path/to/script.py` - Script that generated this
- `--pipeline-run run-123` - Pipeline/run identifier
- `--tags tag1,tag2` - Categorization tags
- `--notes "..."` - Additional context

**Examples:**
```bash
n5 review add Documents/strategy.md --title "Q1 Strategy Doc" --type file --tags strategy,planning
n5 review add https://docs.google.com/doc/123 --title "External doc" --type url
```

### n5 review list

List outputs with filters.

```bash
n5 review list [--status ...] [--sentiment ...] [--tags ...] [--type ...] [--json]
```

**Filters:**
- `--status`: pending, in_review, approved, issue, training, archived
- `--sentiment`: excellent, good, acceptable, issue
- `--tags`: Comma-separated tag list
- `--type`: file, message, image, video, transcript, url
- `--conversation-id`: Filter by conversation

**Examples:**
```bash
n5 review list --status pending
n5 review list --sentiment issue --tags documentation
n5 review list --json
```

### n5 review show

Show full details with comments.

```bash
n5 review show <output_id> [--with-content] [--json]
```

**Options:**
- `--with-content` - Show first 50 lines of file content
- `--json` - Machine-readable output

### n5 review status

Update workflow status.

```bash
n5 review status <output_id> <new_status> [--reviewer "Name"] [--note "..."] [--dry-run]
```

**Examples:**
```bash
n5 review status out_x7k9m2n4p8q1 in_review --reviewer V
n5 review status out_x7k9m2n4p8q1 approved --note "Ready for training"
n5 review status out_x7k9m2n4p8q1 archived --dry-run
```

### n5 review sentiment

Rate quality with sentiment and dimension scores.

```bash
n5 review sentiment <output_id> <sentiment> [--score dimension=value]
```

**Dimensions:** adherence_to_instructions, formatting, length, style, tone, accuracy, completeness  
**Scale:** 0-10

**Examples:**
```bash
n5 review sentiment out_x7k9m2n4p8q1 excellent
n5 review sentiment out_x7k9m2n4p8q1 issue --score adherence_to_instructions=3 --score tone=4
n5 review sentiment out_x7k9m2n4p8q1 good --score formatting=8 --score completeness=9
```

### n5 review comment

Add threaded comments (max 3 levels).

```bash
n5 review comment <output_id> "comment text" [options]
```

**Options:**
- `--author "Name"` - Default: V
- `--context "..."` - Specific section/line reference
- `--reply-to cmt_XXX` - Parent comment for threading
- `--tags tag1,tag2` - Comment categorization

**Examples:**
```bash
n5 review comment out_x7k9m2n4p8q1 "Excellent tone in the introduction"
n5 review comment out_x7k9m2n4p8q1 "Consider shortening" --context "lines 45-67" --tags structure
n5 review comment out_x7k9m2n4p8q1 "Agreed, will revise" --reply-to cmt_abc123456789
```

### n5 review export

Export outputs to JSON for training.

```bash
n5 review export [--sentiment excellent] [--output /path/to/file.json]
```

**Example:**
```bash
n5 review export --sentiment excellent --output /tmp/training-excellent.json
```

---

## Provenance Tracking

Every entry automatically captures:
- **Conversation ID**: Where it was created
- **Thread name**: If from an archived thread
- **Script path**: What script generated it
- **Pipeline/run**: Multi-step process identifier
- **Parent output**: Derived from another output
- **Content hash**: SHA256 (for files, detects changes)

This allows you to trace any output back to its source and understand what parameters/prompts/settings produced it.

---

## Spreadsheet View

Open `Lists/output_reviews.sheet.json` for quick scanning.

**Editable columns:**
- Status
- Sentiment
- Tags

All other fields are read-only (maintained by JSONL). Changes to editable fields will sync on next CLI operation.

---

## Best Practices

1. **Flag immediately**: Add outputs right after generation while context is fresh
2. **Use tags**: Categorize by domain, project, output type
3. **Comment specifics**: Reference exact sections that need improvement
4. **Track excellent outputs**: Not just problems—capture what works well
5. **Export regularly**: Build training datasets from approved/excellent outputs
6. **Review in batches**: Process pending reviews weekly

---

## Schema Files

- `N5/schemas/output-review.schema.json` - Output entry schema
- `N5/schemas/output-review-comment.schema.json` - Comment schema

---

## Scripts

- `N5/scripts/review_manager.py` - Core CRUD operations
- `N5/scripts/review_cli.py` - CLI interface
- `N5/scripts/test_review_system.py` - Integration tests

---

## Troubleshooting

**"Output not found"**
- Check output ID is correct (starts with `out_`)
- Use `n5 review list` to find the ID

**"Invalid status transition"**
- Follow workflow: pending → in_review → approved/issue
- Can always transition to archived from any state

**"Max thread depth exceeded"**
- Comments support max 3 levels of nesting
- Reply to a higher-level comment instead

**Spreadsheet out of sync**
- Run any CLI command to trigger sync
- Or manually run: `python3 N5/scripts/review_manager.py --sync`

---

**Created:** 2025-10-17  
**Maintained by:** N5 Output Review System
```

---

## Success Criteria

- ✅ Integration test script runs all tests
- ✅ All test cases pass
- ✅ User documentation complete and accurate
- ✅ Fresh conversation can use system (test in new thread)
- ✅ Principles compliance verified (P12, P15, P18, P19)

---

## Testing Checklist

```bash
# Run integration tests
python3 N5/scripts/test_review_system.py

# Verify docs render correctly
cat Documents/output-review-tracker.md

# Test in fresh conversation (P12)
# Start new conversation, run:
n5 review add /tmp/test.md --title "Fresh thread test" --type file
n5 review list

# Verify all files
ls -lh Lists/output_reviews.jsonl Lists/output_reviews_comments.jsonl Lists/output_reviews.sheet.json
ls -lh N5/schemas/output-review*.json
ls -lh N5/scripts/review_*.py
```

---

## Report Back

1. Integration tests pass (all green)
2. Documentation created
3. Fresh conversation test passed
4. System ready for production

---

**Orchestrator:** con_YSy4ld4J113LZQ9A  
**Created:** 2025-10-17 21:03 ET
