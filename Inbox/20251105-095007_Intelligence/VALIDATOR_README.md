# Block Validator - Integration Guide

**File:** `Intelligence/scripts/block_validator.py`  
**Version:** 1.0  
**Created:** 2025-11-03

## Purpose

Validates generated block content against rubrics with quality scoring and actionable feedback for retry loops.

## Quick Start

```python
from Intelligence.scripts import block_validator

# Validate with custom rubric
result = block_validator.validate_block(
    content=generated_content,
    rubric={
        "required_sections": ["## Summary", "## Details"],
        "min_length": 100
    },
    generation_id=gen_id,
    block_id="B01",
    log_to_db=True
)

if not result["valid"]:
    print(f"Validation failed (score: {result['score']})")
    print(result["feedback"])
    # Use feedback to retry generation
```

## Integration with W3 (Generation Engine)

```python
# W3 retry loop pattern
max_attempts = 3
for attempt in range(1, max_attempts + 1):
    # Generate content
    content = generate_block(block_id, transcript, context)
    
    # Log generation
    gen_id = block_db.log_generation(
        block_id=block_id,
        meeting_id=meeting_id,
        status="pending",
        attempt_number=attempt
    )
    
    # Validate
    result = block_validator.validate_block(
        content=content,
        rubric=rubric,
        generation_id=gen_id,
        block_id=block_id,
        log_to_db=True
    )
    
    if result["valid"]:
        block_db.update_generation(gen_id, status="success")
        break
    else:
        # Use feedback for next attempt
        improvement_prompt = f"""
Previous attempt failed validation (score: {result['score']}/100).

{result['feedback']}

Please regenerate the content addressing these issues.
"""
        block_db.update_generation(
            gen_id, 
            status="failed",
            error_message=result["feedback"]
        )
```

## Validation Result Structure

```python
{
    "valid": bool,           # True if passes all critical checks + score >= 70
    "score": float,          # Quality score 0-100
    "feedback": str,         # Actionable guidance for improvement
    "checks": {              # Individual check results
        "check_name": {
            "passed": bool,
            "message": str,
            "details": dict
        }
    }
}
```

## Rubric Schema

```json
{
  "required_sections": [
    "## Section Name",
    "## Another Section"
  ],
  "forbidden_patterns": [
    "TBD",
    "TODO",
    "[Insert"
  ],
  "min_length": 100,
  "structure_rules": {
    "must_start_with_heading": true,
    "require_bullet_points": false,
    "require_numbered_list": false,
    "require_paragraphs": false,
    "no_excessive_whitespace": true
  }
}
```

## Validation Checks

### 1. Required Sections
Checks for presence of specified markdown headings.

**Example:**
```json
"required_sections": ["## Summary", "## Action Items"]
```

### 2. No Placeholders
Detects incomplete content markers like:
- TBD, TODO
- [Insert, [Add, [Fill in
- Ellipsis (...), [XXX]
- <placeholder>, PLACEHOLDER

**Example:**
```json
"forbidden_patterns": ["PENDING", "NEEDS REVIEW"]
```

### 3. Minimum Length
Ensures content meets character count requirement.

**Example:**
```json
"min_length": 150
```

### 4. Structure Rules
Validates document structure:
- Must start with heading
- Contains bullet points
- Contains numbered lists
- Contains paragraph text
- No excessive whitespace

**Example:**
```json
"structure_rules": {
  "must_start_with_heading": true,
  "require_bullet_points": true
}
```

### 5. Completeness
Heuristic checks for content completeness:
- Ends with proper punctuation
- No very short sections
- Appears finished

## Quality Scoring

Scores are weighted by check importance:

| Check | Weight |
|-------|--------|
| Required Sections | 30% |
| No Placeholders | 25% |
| Structure | 20% |
| Minimum Length | 15% |
| Completeness | 10% |

**Passing threshold:** Valid = all critical checks pass + score >= 70

## Database Integration

Validation results are automatically logged to `validation_results` table:

```sql
CREATE TABLE validation_results (
    validation_id INTEGER PRIMARY KEY,
    generation_id INTEGER,
    block_id TEXT,
    validation_type TEXT,
    status TEXT,              -- 'pass' or 'fail'
    score REAL,
    criteria_checked TEXT,    -- JSON array
    failures TEXT,            -- JSON array
    warnings TEXT,
    validator_version TEXT,
    created_at TIMESTAMP
);
```

## Loading Rubrics from Database

```python
# Load from database
rubric = block_validator.load_rubric_from_db("B01")

# Use default if none exists
if not rubric:
    rubric = block_validator.get_default_rubric()
```

## Default Rubric

When no rubric is specified:

```python
{
    "required_sections": [],
    "min_length": 100,
    "structure_rules": {
        "must_start_with_heading": True,
        "no_excessive_whitespace": True
    }
}
```

## Sample Rubrics by Block Type

### External Meeting Blocks (B01-B39)

```json
{
  "required_sections": ["## Summary", "## Key Points"],
  "min_length": 150,
  "structure_rules": {
    "must_start_with_heading": true,
    "require_bullet_points": true
  }
}
```

### Internal Meeting Blocks (B40-B49)

```json
{
  "required_sections": ["## Decisions", "## Action Items"],
  "min_length": 100,
  "structure_rules": {
    "must_start_with_heading": true,
    "require_bullet_points": true
  }
}
```

### Reflection Blocks (B50-B99)

```json
{
  "min_length": 200,
  "structure_rules": {
    "must_start_with_heading": true,
    "require_paragraphs": true
  }
}
```

## Error Handling

```python
try:
    result = block_validator.validate_block(...)
except Exception as e:
    # Validation errors don't stop processing
    # Database logging failures are caught internally
    print(f"Validation error: {e}")
    # Continue with generation
```

## Testing

Run built-in tests:

```bash
python3 Intelligence/scripts/block_validator.py
```

## API Reference

### `validate_block(content, rubric, generation_id=None, block_id=None, log_to_db=True)`

Main validation function.

**Args:**
- `content` (str): Markdown content to validate
- `rubric` (dict): Validation criteria
- `generation_id` (int, optional): DB reference for logging
- `block_id` (str, optional): Block ID for logging
- `log_to_db` (bool): Whether to log to database (default: True)

**Returns:**
- dict with keys: `valid`, `score`, `feedback`, `checks`

### `load_rubric_from_db(block_id)`

Load rubric from database.

**Args:**
- `block_id` (str): Block identifier

**Returns:**
- dict or None

### `get_default_rubric()`

Get default rubric for blocks without specific requirements.

**Returns:**
- dict

## Version History

- **1.0** (2025-11-03): Initial release
  - Core validation checks
  - Quality scoring
  - Feedback generation
  - Database integration

---

**Worker 4 Deliverable**  
Part of Unified Block Generator System
