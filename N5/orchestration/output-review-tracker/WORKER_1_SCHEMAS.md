# Worker 1: Schemas & Data Infrastructure

**Orchestrator:** con_YSy4ld4J113LZQ9A  
**Task ID:** W1-SCHEMAS  
**Estimated Time:** 30 minutes  
**Dependencies:** None

---

## Mission

Create JSON schemas and initialize JSONL/spreadsheet data files for Output Review Tracker system.

---

## Context

Building a centralized system to track generated outputs (markdown files, messages, images, etc.) for quality review with full provenance. This worker creates the data foundation.

---

## Decisions Locked In

1. Archive date: **Separate field from updated_at**
2. Resolver tracking: **No**
3. Comment threading: **Max 3 levels**
4. Export format: **JSON only**
5. Spreadsheet edits: **Status, sentiment, tags only (others read-only)**

---

## Deliverables

### 1. Output Review Schema
**File:** `N5/schemas/output-review.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://n5.local/schemas/output-review.schema.json",
  "title": "N5 Output Review Entry",
  "type": "object",
  "required": ["id", "created_at", "title", "type", "reference", "provenance", "review"],
  "additionalProperties": true,
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^out_[a-zA-Z0-9]{12}$",
      "description": "Unique identifier, e.g., out_x7k9m2n4p8q1"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    },
    "archived_at": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "Timestamp when archived (separate from updated_at)"
    },
    "title": {
      "type": "string",
      "maxLength": 200,
      "description": "Brief description of the output"
    },
    "type": {
      "type": "string",
      "enum": ["file", "message", "image", "video", "transcript", "url"],
      "description": "Type of output being tracked"
    },
    "reference": {
      "type": "string",
      "description": "Path, URL, or identifier for the output"
    },
    "content_hash": {
      "type": ["string", "null"],
      "description": "SHA256 hash of file content (for change detection)"
    },
    "provenance": {
      "type": "object",
      "required": ["conversation_id"],
      "properties": {
        "conversation_id": {
          "type": "string",
          "pattern": "^con_[a-zA-Z0-9]+$"
        },
        "thread_name": {
          "type": ["string", "null"],
          "description": "Human-readable thread name if from archived thread"
        },
        "script_path": {
          "type": ["string", "null"],
          "description": "Path to script that generated this output"
        },
        "pipeline_run": {
          "type": ["string", "null"],
          "description": "Pipeline/run identifier for multi-step processes"
        },
        "parent_output_id": {
          "type": ["string", "null"],
          "description": "ID of output this was derived from"
        }
      }
    },
    "review": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["pending", "in_review", "approved", "issue", "training", "archived"],
          "description": "Current review workflow state"
        },
        "sentiment": {
          "type": ["string", "null"],
          "enum": ["excellent", "good", "acceptable", "issue", null],
          "description": "Quality assessment"
        },
        "reviewed_by": {
          "type": ["string", "null"],
          "description": "Who reviewed this output"
        },
        "reviewed_at": {
          "type": ["string", "null"],
          "format": "date-time"
        },
        "quality_dimensions": {
          "type": ["object", "null"],
          "description": "Granular quality scores (0-10 scale)",
          "properties": {
            "adherence_to_instructions": {"type": ["number", "null"], "minimum": 0, "maximum": 10},
            "formatting": {"type": ["number", "null"], "minimum": 0, "maximum": 10},
            "length": {"type": ["number", "null"], "minimum": 0, "maximum": 10},
            "style": {"type": ["number", "null"], "minimum": 0, "maximum": 10},
            "tone": {"type": ["number", "null"], "minimum": 0, "maximum": 10},
            "accuracy": {"type": ["number", "null"], "minimum": 0, "maximum": 10},
            "completeness": {"type": ["number", "null"], "minimum": 0, "maximum": 10}
          }
        }
      }
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "uniqueItems": true,
      "description": "Categorization tags"
    },
    "notes": {
      "type": ["string", "null"],
      "description": "Free-form notes about this output"
    },
    "comment_count": {
      "type": "integer",
      "minimum": 0,
      "description": "Number of comments on this output"
    },
    "latest_comment_at": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "Timestamp of most recent comment"
    }
  }
}
```

### 2. Comment Schema
**File:** `N5/schemas/output-review-comment.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://n5.local/schemas/output-review-comment.schema.json",
  "title": "N5 Output Review Comment",
  "type": "object",
  "required": ["id", "output_id", "created_at", "author", "body"],
  "additionalProperties": true,
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^cmt_[a-zA-Z0-9]{12}$",
      "description": "Unique comment identifier"
    },
    "output_id": {
      "type": "string",
      "pattern": "^out_[a-zA-Z0-9]{12}$",
      "description": "ID of output being commented on"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "author": {
      "type": "string",
      "description": "Who wrote this comment"
    },
    "body": {
      "type": "string",
      "description": "Comment text content"
    },
    "context": {
      "type": ["string", "null"],
      "description": "Specific section/line being referenced"
    },
    "parent_comment_id": {
      "type": ["string", "null"],
      "pattern": "^(cmt_[a-zA-Z0-9]{12}|null)$",
      "description": "ID of parent comment for threading (max 3 levels)"
    },
    "thread_depth": {
      "type": "integer",
      "minimum": 0,
      "maximum": 3,
      "description": "Depth in comment thread (0=top-level, max 3)"
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "uniqueItems": true,
      "description": "Tags for categorizing comments (tone, structure, etc.)"
    }
  }
}
```

### 3. Initialize JSONL Files

**File:** `Lists/output_reviews.jsonl`
```
# N5 Output Reviews Registry (JSONL)
# Schema: file N5/schemas/output-review.schema.json
# Each line after this header is a JSON object representing one output review entry
# Format: {"id": "out_XXXXXXXXXXXX", "created_at": "...", "title": "...", ...}
# Do not edit manually - use: n5 review add|status|comment commands
```

**File:** `Lists/output_reviews_comments.jsonl`
```
# N5 Output Review Comments (JSONL)
# Schema: file N5/schemas/output-review-comment.schema.json
# Each line after this header is a JSON object representing one comment
# Format: {"id": "cmt_XXXXXXXXXXXX", "output_id": "out_XXXXXXXXXXXX", "body": "...", ...}
# Do not edit manually - use: n5 review comment commands
```

### 4. Initialize Spreadsheet

**File:** `Lists/output_reviews.sheet.json`

```json
{
  "tabs": true,
  "toolbar": true,
  "worksheets": [
    {
      "worksheetName": "Output Reviews",
      "minDimensions": [11, 10],
      "columns": [
        {"type": "text", "title": "ID", "width": 150},
        {"type": "text", "title": "Title", "width": 300},
        {"type": "text", "title": "Type", "width": 80},
        {"type": "text", "title": "Status", "width": 120},
        {"type": "text", "title": "Sentiment", "width": 100},
        {"type": "text", "title": "Tags", "width": 200},
        {"type": "text", "title": "Conversation", "width": 180},
        {"type": "text", "title": "Script", "width": 200},
        {"type": "text", "title": "Reference", "width": 250},
        {"type": "text", "title": "Created", "width": 150},
        {"type": "numeric", "title": "Comments", "width": 80}
      ],
      "data": []
    }
  ]
}
```

### 5. Extend Schema Validator

**File:** `N5/scripts/n5_schema_validation.py`

Add these two functions:

```python
from pathlib import Path

OUTPUT_REVIEW_SCHEMA = Path("/home/workspace/N5/schemas/output-review.schema.json")
OUTPUT_REVIEW_COMMENT_SCHEMA = Path("/home/workspace/N5/schemas/output-review-comment.schema.json")

def validate_output_review(entry):
    """Validate an output review entry against schema."""
    if not OUTPUT_REVIEW_SCHEMA.exists():
        raise FileNotFoundError(f"Schema not found: {OUTPUT_REVIEW_SCHEMA}")
    
    schema = json.loads(OUTPUT_REVIEW_SCHEMA.read_text())
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(entry), key=lambda e: e.path)
    
    if errors:
        print("Output review validation errors:")
        for error in errors:
            print(f"- {'.'.join(map(str, error.path))}: {error.message}")
        return False
    return True

def validate_output_review_comment(comment):
    """Validate an output review comment against schema."""
    if not OUTPUT_REVIEW_COMMENT_SCHEMA.exists():
        raise FileNotFoundError(f"Schema not found: {OUTPUT_REVIEW_COMMENT_SCHEMA}")
    
    schema = json.loads(OUTPUT_REVIEW_COMMENT_SCHEMA.read_text())
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(comment), key=lambda e: e.path)
    
    if errors:
        print("Output review comment validation errors:")
        for error in errors:
            print(f"- {'.'.join(map(str, error.path))}: {error.message}")
        return False
    return True
```

---

## Success Criteria

- ✅ Both schemas validate as proper JSON Schema draft 2020-12
- ✅ All required fields present, enums match decisions
- ✅ JSONL files created with proper headers
- ✅ Spreadsheet created with correct columns
- ✅ Schema validator extended with new functions
- ✅ No syntax errors in any files

---

## Testing

```bash
# Validate schemas
python3 -c "import json; print('output-review:', json.load(open('N5/schemas/output-review.schema.json')))"
python3 -c "import json; print('comment:', json.load(open('N5/schemas/output-review-comment.schema.json')))"

# Verify files exist
ls -lh Lists/output_reviews.jsonl Lists/output_reviews_comments.jsonl Lists/output_reviews.sheet.json

# Test validator functions
python3 -c "from N5.scripts.n5_schema_validation import validate_output_review, validate_output_review_comment; print('Functions imported successfully')"
```

---

## Report Back

When complete, report:
1. All 5 deliverables created
2. Test results
3. Any issues encountered
4. Ready for Worker 2

---

**Orchestrator Contact:** con_YSy4ld4J113LZQ9A  
**Created:** 2025-10-17 20:56 ET
