# Worker 2: Core Review Manager

**Orchestrator:** con_YSy4ld4J113LZQ9A\
**Task ID:** W2-CORE-MANAGER\
**Estimated Time:** 45 minutes\
**Dependencies:** Worker 1 (schemas must exist)

---

## Mission

Build the core Python module (`file review_manager.py` ) that handles all JSONL operations for the Output Review Tracker. This is the foundational CRUD layer.

---

## Context

Output Review Tracker needs a robust backend to manage review entries and comments in JSONL format. This module provides all core operations (add, update, list, filter, export) with full validation and error handling.

---

## Prerequisites

Ensure these exist (created by Worker 1):

- `file N5/schemas/output-review.schema.json` 
- `file N5/schemas/output-review-comment.schema.json` 
- `file Lists/output_reviews.jsonl` 
- `file Lists/output_reviews_comments.jsonl` 

---

## Deliverable

**File:** `file N5/scripts/review_manager.py` 

### Requirements

1. **CRUD Operations:**

   - Add new review entry
   - Update review fields (status, sentiment, tags, scores)
   - List/filter reviews
   - Get single review by ID
   - Add comments to reviews
   - Get comments for a review

2. **Auto-Detection:**

   - Detect conversation ID from environment
   - Compute content hash for files
   - Generate unique IDs (out_XXXX, cmt_XXXX)
   - Auto-populate timestamps

3. **Validation:**

   - Schema validation on all writes
   - Thread depth enforcement (max 3 levels)
   - Status transition validation

4. **Safety:**

   - Dry-run mode support
   - Error handling with logging
   - State verification after writes

---

## Code Template

```markdown
#!/usr/bin/env python3
"""
Output Review Manager - Core CRUD operations for output review tracking.

Handles JSONL read/write, validation, filtering, and provenance tracking.
"""

import json
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any
import os
import secrets

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
REVIEWS_JSONL = Path("/home/workspace/Lists/output_reviews.jsonl")
COMMENTS_JSONL = Path("/home/workspace/Lists/output_reviews_comments.jsonl")
REVIEW_SCHEMA = Path("/home/workspace/N5/schemas/output-review.schema.json")
COMMENT_SCHEMA = Path("/home/workspace/N5/schemas/output-review-comment.schema.json")

# Valid enums
VALID_STATUSES = ["pending", "in_review", "approved", "issue", "training", "archived"]
VALID_SENTIMENTS = ["excellent", "good", "acceptable", "issue", None]
VALID_TYPES = ["file", "message", "image", "video", "transcript", "url"]

class ReviewManager:
    """Core manager for output review operations."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        if dry_run:
            logger.info("[DRY RUN MODE]")
    
    def generate_id(self, prefix: str = "out") -> str:
        """Generate unique ID with prefix (out_ or cmt_)."""
        random_suffix = secrets.token_urlsafe(9)[:12]
        return f"{prefix}_{random_suffix}"
    
    def compute_hash(self, file_path: str) -> Optional[str]:
        """Compute SHA256 hash of file content."""
        try:
            path = Path(file_path)
            if not path.exists() or not path.is_file():
                return None
            return hashlib.sha256(path.read_bytes()).hexdigest()
        except Exception as e:
            logger.warning(f"Cannot hash {file_path}: {e}")
            return None
    
    def detect_conversation_id(self) -> Optional[str]:
        """Detect conversation ID from environment."""
        # Check N5_CONVERSATION_ID env var
        conv_id = os.getenv("N5_CONVERSATION_ID")
        if conv_id:
            return conv_id
        
        # Try to detect from CWD if in conversation workspace
        cwd = Path.cwd()
        if "/.z/workspaces/" in str(cwd):
            parts = str(cwd).split("/.z/workspaces/")
            if len(parts) > 1:
                return parts[1].split("/")[0]
        
        return None
    
    def read_jsonl(self, path: Path) -> List[Dict[str, Any]]:
        """Read JSONL file, skipping comment lines."""
        if not path.exists():
            return []
        
        entries = []
        with path.open("r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in {path}: {e}")
        return entries
    
    def write_jsonl(self, path: Path, entries: List[Dict[str, Any]]):
        """Write entries to JSONL file with header."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would write {len(entries)} entries to {path}")
            return
        
        # Read existing header
        header_lines = []
        if path.exists():
            with path.open("r") as f:
                for line in f:
                    if line.startswith("#"):
                        header_lines.append(line)
                    else:
                        break
        
        # Write header + entries
        with path.open("w") as f:
            for header in header_lines:
                f.write(header)
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
        
        logger.info(f"✓ Wrote {len(entries)} entries to {path}")
    
    def add_review(
        self,
        title: str,
        output_type: str,
        reference: str,
        conversation_id: Optional[str] = None,
        thread_name: Optional[str] = None,
        script_path: Optional[str] = None,
        pipeline_run: Optional[str] = None,
        parent_output_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add new output review entry."""
        
        # Validate type
        if output_type not in VALID_TYPES:
            raise ValueError(f"Invalid type: {output_type}. Must be one of {VALID_TYPES}")
        
        # Auto-detect conversation if not provided
        if not conversation_id:
            conversation_id = self.detect_conversation_id()
            if conversation_id:
                logger.info(f"Auto-detected conversation: {conversation_id}")
        
        if not conversation_id:
            raise ValueError("conversation_id required and could not be auto-detected")
        
        # Compute content hash for files
        content_hash = None
        if output_type == "file":
            content_hash = self.compute_hash(reference)
        
        # Build entry
        now = datetime.now(timezone.utc).isoformat()
        entry = {
            "id": self.generate_id("out"),
            "created_at": now,
            "updated_at": now,
            "archived_at": None,
            "title": title,
            "type": output_type,
            "reference": reference,
            "content_hash": content_hash,
            "provenance": {
                "conversation_id": conversation_id,
                "thread_name": thread_name,
                "script_path": script_path,
                "pipeline_run": pipeline_run,
                "parent_output_id": parent_output_id
            },
            "review": {
                "status": "pending",
                "sentiment": None,
                "reviewed_by": None,
                "reviewed_at": None,
                "quality_dimensions": None
            },
            "tags": tags or [],
            "notes": notes,
            "comment_count": 0,
            "latest_comment_at": None
        }
        
        # Validate against schema
        # TODO: Add schema validation here
        
        # Add to JSONL
        entries = self.read_jsonl(REVIEWS_JSONL)
        entries.append(entry)
        self.write_jsonl(REVIEWS_JSONL, entries)
        
        logger.info(f"✓ Added review: {entry['id']} - {title}")
        return entry
    
    def update_status(
        self,
        output_id: str,
        status: str,
        sentiment: Optional[str] = None,
        reviewed_by: Optional[str] = None,
        quality_dimensions: Optional[Dict[str, float]] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update review status and related fields."""
        
        # Validate
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}. Must be one of {VALID_STATUSES}")
        if sentiment and sentiment not in [s for s in VALID_SENTIMENTS if s]:
            raise ValueError(f"Invalid sentiment: {sentiment}")
        
        entries = self.read_jsonl(REVIEWS_JSONL)
        entry = next((e for e in entries if e["id"] == output_id), None)
        
        if not entry:
            raise ValueError(f"Output not found: {output_id}")
        
        # Update fields
        now = datetime.now(timezone.utc).isoformat()
        entry["review"]["status"] = status
        entry["updated_at"] = now
        
        if status == "archived":
            entry["archived_at"] = now
        
        if sentiment:
            entry["review"]["sentiment"] = sentiment
        
        if reviewed_by:
            entry["review"]["reviewed_by"] = reviewed_by
            entry["review"]["reviewed_at"] = now
        
        if quality_dimensions:
            entry["review"]["quality_dimensions"] = quality_dimensions
        
        if notes:
            entry["notes"] = notes
        
        self.write_jsonl(REVIEWS_JSONL, entries)
        
        logger.info(f"✓ Updated {output_id} status: {status}")
        return entry
    
    def list_reviews(
        self,
        status: Optional[str] = None,
        sentiment: Optional[str] = None,
        output_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List reviews with optional filters."""
        entries = self.read_jsonl(REVIEWS_JSONL)
        
        # Apply filters
        if status:
            entries = [e for e in entries if e["review"]["status"] == status]
        if sentiment:
            entries = [e for e in entries if e["review"].get("sentiment") == sentiment]
        if output_type:
            entries = [e for e in entries if e["type"] == output_type]
        if tags:
            entries = [e for e in entries if any(t in e.get("tags", []) for t in tags)]
        
        return entries
    
    def get_review(self, output_id: str) -> Optional[Dict[str, Any]]:
        """Get single review by ID."""
        entries = self.read_jsonl(REVIEWS_JSONL)
        return next((e for e in entries if e["id"] == output_id), None)
    
    def add_comment(
        self,
        output_id: str,
        body: str,
        author: str,
        context: Optional[str] = None,
        parent_comment_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add comment to a review."""
        
        # Verify output exists
        if not self.get_review(output_id):
            raise ValueError(f"Output not found: {output_id}")
        
        # Calculate thread depth
        thread_depth = 0
        if parent_comment_id:
            parent = self.get_comment(parent_comment_id)
            if not parent:
                raise ValueError(f"Parent comment not found: {parent_comment_id}")
            thread_depth = parent.get("thread_depth", 0) + 1
            
            if thread_depth > 3:
                raise ValueError("Maximum comment depth (3) exceeded")
        
        # Build comment
        now = datetime.now(timezone.utc).isoformat()
        comment = {
            "id": self.generate_id("cmt"),
            "output_id": output_id,
            "created_at": now,
            "author": author,
            "body": body,
            "context": context,
            "parent_comment_id": parent_comment_id,
            "thread_depth": thread_depth,
            "tags": tags or []
        }
        
        # Add to JSONL
        comments = self.read_jsonl(COMMENTS_JSONL)
        comments.append(comment)
        self.write_jsonl(COMMENTS_JSONL, comments)
        
        # Update review metadata
        entries = self.read_jsonl(REVIEWS_JSONL)
        for entry in entries:
            if entry["id"] == output_id:
                entry["comment_count"] = entry.get("comment_count", 0) + 1
                entry["latest_comment_at"] = now
                entry["updated_at"] = now
                break
        self.write_jsonl(REVIEWS_JSONL, entries)
        
        logger.info(f"✓ Added comment {comment['id']} to {output_id}")
        return comment
    
    def get_comment(self, comment_id: str) -> Optional[Dict[str, Any]]:
        """Get single comment by ID."""
        comments = self.read_jsonl(COMMENTS_JSONL)
        return next((c for c in comments if c["id"] == comment_id), None)
    
    def get_comments(self, output_id: str) -> List[Dict[str, Any]]:
        """Get all comments for a review."""
        comments = self.read_jsonl(COMMENTS_JSONL)
        return [c for c in comments if c["output_id"] == output_id]
    
    def export_reviews(
        self,
        status: Optional[str] = None,
        sentiment: Optional[str] = None
    ) -> str:
        """Export reviews as JSON string."""
        reviews = self.list_reviews(status=status, sentiment=sentiment)
        
        # Enrich with comments
        for review in reviews:
            review["comments"] = self.get_comments(review["id"])
        
        return json.dumps(reviews, indent=2)


def main():
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Output Review Manager")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--test", action="store_true", help="Run basic tests")
    
    args = parser.parse_args()
    
    if args.test:
        manager = ReviewManager(dry_run=args.dry_run)
        
        # Test: Add review
        review = manager.add_review(
            title="Test output document",
            output_type="file",
            reference="/home/workspace/Documents/test.md",
            tags=["test"],
            notes="Test entry"
        )
        print(f"✓ Created review: {review['id']}")
        
        # Test: Add comment
        comment = manager.add_comment(
            output_id=review["id"],
            body="This is a test comment",
            author="V"
        )
        print(f"✓ Created comment: {comment['id']}")
        
        # Test: Update status
        updated = manager.update_status(
            output_id=review["id"],
            status="approved",
            sentiment="good",
            reviewed_by="V"
        )
        print(f"✓ Updated status: {updated['review']['status']}")
        
        # Test: List reviews
        reviews = manager.list_reviews(status="approved")
        print(f"✓ Found {len(reviews)} approved reviews")
        
        return 0
    
    print("Use --test to run basic tests")
    return 0


if __name__ == "__main__":
    exit(main())
```

---

## Success Criteria

- ✅ All CRUD operations work correctly
- ✅ Auto-detection of conversation ID works
- ✅ Content hashing works for files
- ✅ Comment threading enforces 3-level max
- ✅ Status/sentiment validation works
- ✅ Dry-run mode functional
- ✅ Error handling with proper logging
- ✅ Test suite passes

---

## Testing

```bash
# Run built-in tests
python3 N5/scripts/review_manager.py --test --dry-run
python3 N5/scripts/review_manager.py --test

# Verify JSONL updated
cat Lists/output_reviews.jsonl
cat Lists/output_reviews_comments.jsonl

# Test import
python3 -c "from N5.scripts.review_manager import ReviewManager; print('✓ Import successful')"
```

---

## Report Back

When complete, report:

1. All CRUD operations tested
2. Test output showing success
3. Any issues encountered
4. Ready for Worker 3

---

**Orchestrator Contact:** con_YSy4ld4J113LZQ9A\
**Created:** 2025-10-17 20:56 ET