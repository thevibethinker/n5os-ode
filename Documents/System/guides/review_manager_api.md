# review_manager.py API Documentation

**Module:** `N5/scripts/review_manager.py`  
**Created:** 2025-10-19  
**Worker:** W2-CORE-MANAGER

## Overview

Core CRUD module for Output Review Tracker. Handles all JSONL operations for managing review entries and comments with full validation and error handling.

## Class: ReviewManager

### Constructor

```python
ReviewManager(dry_run: bool = False)
```

**Parameters:**
- `dry_run`: If True, simulates operations without writing to disk

### Core Operations

#### add_review()

Add a new output review entry.

```python
add_review(
    title: str,
    output_type: str,  # "file" | "message" | "url"
    reference: str,
    conversation_id: Optional[str] = None,  # Auto-detected if not provided
    thread_id: Optional[str] = None,
    script_path: Optional[str] = None,
    command_name: Optional[str] = None,
    pipeline_run_id: Optional[str] = None,
    parent_output_id: Optional[str] = None,
    tags: Optional[List[str]] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]
```

**Returns:** Complete review entry with generated ID

**Auto-Detection:**
- Conversation ID from `N5_CONVERSATION_ID` env var or CWD
- Content hash for file types

**Validation:**
- Type must be in `VALID_TYPES`
- Conversation ID required (auto-detected or explicit)
- Schema validation against `output-review.schema.json`

#### update_status()

Update review status and related fields.

```python
update_status(
    output_id: str,
    status: str,  # "pending" | "in_review" | "needs_work" | "approved" | "training" | "archived"
    sentiment: Optional[str] = None,  # "excellent" | "good" | "neutral" | "issue" | "critical"
    reviewed_by: Optional[str] = None,
    quality_dimensions: Optional[Dict[str, int]] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]
```

**Returns:** Updated review entry

**Behavior:**
- Sets `reviewed_at` when `reviewed_by` provided
- Sets `archived_at` when status is "archived"
- Validates status and sentiment against enums
- Schema validation on update

#### list_reviews()

List and filter reviews.

```python
list_reviews(
    status: Optional[str] = None,
    sentiment: Optional[str] = None,
    output_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    conversation_id: Optional[str] = None
) -> List[Dict[str, Any]]
```

**Returns:** Filtered list of review entries

**Filters:**
- All filters are optional and combinable
- Tags filter uses ANY match (not ALL)

#### get_review()

Get single review by ID.

```python
get_review(output_id: str) -> Optional[Dict[str, Any]]
```

**Returns:** Review entry or None if not found

#### add_comment()

Add comment to a review.

```python
add_comment(
    output_id: str,
    body: str,
    author: str,
    context: Optional[str] = None,
    parent_comment_id: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]
```

**Returns:** Complete comment entry with generated ID

**Threading:**
- Calculates thread depth automatically
- Enforces max depth of 3 levels
- Validates parent comment exists

**Side Effects:**
- Increments `comment_count` on parent review
- Updates `latest_comment_at` on parent review

#### get_comments()

Get all comments for a review.

```python
get_comments(output_id: str) -> List[Dict[str, Any]]
```

**Returns:** List of comment entries for the output

#### get_comment()

Get single comment by ID.

```python
get_comment(comment_id: str) -> Optional[Dict[str, Any]]
```

**Returns:** Comment entry or None if not found

#### resolve_comment()

Mark a comment thread as resolved.

```python
resolve_comment(
    comment_id: str,
    resolved_by: str
) -> Dict[str, Any]
```

**Returns:** Updated comment entry

**Behavior:**
- Sets `resolved` to True
- Records `resolved_at` timestamp
- Records `resolved_by` author

#### export_reviews()

Export reviews as JSON.

```python
export_reviews(
    status: Optional[str] = None,
    sentiment: Optional[str] = None,
    include_comments: bool = True
) -> str
```

**Returns:** JSON string with filtered reviews

**Options:**
- Filters same as `list_reviews()`
- Optionally includes comments nested in each review

#### verify_state()

Verify data integrity.

```python
verify_state() -> Dict[str, Any]
```

**Returns:**
```python
{
    "reviews_count": int,
    "comments_count": int,
    "issues": List[str],
    "valid": bool
}
```

**Checks:**
- Orphaned comments (reference non-existent outputs)
- Comment count mismatches

### Utility Methods

#### generate_id()

Generate unique ID.

```python
generate_id(prefix: str = "out") -> str
```

**Returns:** ID in format `{prefix}_{12_hex_chars}`

#### compute_hash()

Compute SHA256 hash of file.

```python
compute_hash(file_path: str) -> Optional[str]
```

**Returns:** Hex digest or None if file not found/readable

#### detect_conversation_id()

Auto-detect conversation ID.

```python
detect_conversation_id() -> Optional[str]
```

**Sources (in order):**
1. `N5_CONVERSATION_ID` environment variable
2. Parse from CWD if in `/.z/workspaces/`

**Returns:** Conversation ID or None

## Constants

```python
VALID_STATUSES = ["pending", "in_review", "needs_work", "approved", "training", "archived"]
VALID_SENTIMENTS = ["excellent", "good", "neutral", "issue", "critical", None]
VALID_TYPES = ["file", "message", "url"]

REVIEWS_JSONL = Path("/home/workspace/Lists/output_reviews.jsonl")
COMMENTS_JSONL = Path("/home/workspace/Lists/output_reviews_comments.jsonl")
REVIEW_SCHEMA = Path("/home/workspace/N5/schemas/output-review.schema.json")
COMMENT_SCHEMA = Path("/home/workspace/N5/schemas/output-review-comment.schema.json")
```

## CLI Usage

### Test Suite

```bash
# Dry run test
python3 N5/scripts/review_manager.py --test --dry-run

# Full test (writes to JSONL)
python3 N5/scripts/review_manager.py --test
```

### Verify Integrity

```bash
python3 N5/scripts/review_manager.py --verify
```

## Python Usage Examples

### Basic CRUD

```python
from N5.scripts.review_manager import ReviewManager

manager = ReviewManager()

# Add review
review = manager.add_review(
    title="API documentation",
    output_type="file",
    reference="/home/workspace/Documents/api.md",
    tags=["docs", "api"],
    notes="First draft"
)

# Update status
manager.update_status(
    output_id=review["id"],
    status="approved",
    sentiment="good",
    reviewed_by="V"
)

# Add comment
manager.add_comment(
    output_id=review["id"],
    body="Looks great!",
    author="V"
)
```

### Filtering & Export

```python
# List pending reviews
pending = manager.list_reviews(status="pending")

# Filter by conversation
conv_reviews = manager.list_reviews(
    conversation_id="con_abc123"
)

# Export approved with comments
export_json = manager.export_reviews(
    status="approved",
    include_comments=True
)
```

### Threading Comments

```python
# Add top-level comment
comment = manager.add_comment(
    output_id="out_abc123",
    body="Consider adding examples",
    author="V"
)

# Reply to comment
reply = manager.add_comment(
    output_id="out_abc123",
    body="Good idea, will add",
    author="Zo",
    parent_comment_id=comment["id"]
)

# Resolve thread
manager.resolve_comment(
    comment_id=comment["id"],
    resolved_by="V"
)
```

## Error Handling

All methods raise `ValueError` for:
- Invalid enum values (status, sentiment, type)
- Missing required IDs
- Schema validation failures
- Max thread depth exceeded

All errors are logged with context before raising.

## Schema Validation

Uses `jsonschema` library if installed:
- Validates on every write operation
- Enforces ID patterns (`^out_[a-zA-Z0-9]{12}$`)
- Type checking and enum validation
- Logs detailed error messages

If `jsonschema` not installed, validation is skipped with warning.

## Safety Features

- **Dry-run mode:** Preview operations without writes
- **Header preservation:** Maintains JSONL comment headers
- **Atomic writes:** Read-modify-write pattern
- **Schema validation:** Enforces data integrity
- **Error logging:** Comprehensive error context
- **State verification:** Built-in integrity checks

## Performance Notes

- All operations read full JSONL (acceptable for 1000s of entries)
- Comments filtered in-memory (no indexing)
- For large datasets (10k+ entries), consider pagination

## Integration Points

- Worker 3 (CLI) wraps these operations
- Worker 4 (TUI) uses for display
- Session state manager calls for provenance

---

**Next:** CLI wrapper (Worker 3)  
**Status:** ✅ Complete and tested
