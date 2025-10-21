#!/usr/bin/env python3
"""
Output Review Manager - Core CRUD operations for output review tracking.

Handles JSONL read/write, validation, filtering, and provenance tracking.
Implements Principles: P1 (Human-Readable), P2 (SSOT), P5 (Anti-Overwrite),
P7 (Dry-Run), P11 (Failure Modes), P15 (Complete), P18 (State Verification),
P19 (Error Handling), P21 (Document Assumptions)
"""

import json
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any
import os
import secrets
import jsonschema

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
        self.review_schema = None
        self.comment_schema = None
        if dry_run:
            logger.info("[DRY RUN MODE]")
        
        # Load schemas
        try:
            if REVIEW_SCHEMA.exists():
                with REVIEW_SCHEMA.open('r') as f:
                    self.review_schema = json.load(f)
            if COMMENT_SCHEMA.exists():
                with COMMENT_SCHEMA.open('r') as f:
                    self.comment_schema = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load schemas: {e}")
    
    def generate_id(self, prefix: str = "out") -> str:
        """Generate unique ID with prefix (out_ or cmt_)."""
        random_suffix = secrets.token_hex(6)
        return f"{prefix}_{random_suffix}"
    
    def compute_hash(self, file_path: str) -> Optional[str]:
        """Compute SHA256 hash of file content."""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"File not found for hashing: {file_path}")
                return None
            if not path.is_file():
                logger.warning(f"Path is not a file: {file_path}")
                return None
            return hashlib.sha256(path.read_bytes()).hexdigest()
        except Exception as e:
            logger.error(f"Cannot hash {file_path}: {e}")
            return None
    
    def detect_conversation_id(self) -> Optional[str]:
        """Detect conversation ID from environment."""
        # Check N5_CONVERSATION_ID env var
        conv_id = os.getenv("N5_CONVERSATION_ID")
        if conv_id:
            logger.info(f"Detected conversation ID from env: {conv_id}")
            return conv_id
        
        # Try to detect from CWD if in conversation workspace
        cwd = Path.cwd()
        if "/.z/workspaces/" in str(cwd):
            parts = str(cwd).split("/.z/workspaces/")
            if len(parts) > 1:
                detected_id = parts[1].split("/")[0]
                logger.info(f"Detected conversation ID from CWD: {detected_id}")
                return detected_id
        
        logger.warning("Could not auto-detect conversation ID")
        return None
    
    def validate_schema(self, entry: Dict[str, Any], schema_type: str) -> bool:
        """Validate entry against schema."""
        if schema_type == "review" and self.review_schema:
            try:
                jsonschema.validate(instance=entry, schema=self.review_schema)
                return True
            except jsonschema.ValidationError as e:
                logger.error(f"Schema validation failed for review: {e.message}")
                return False
        elif schema_type == "comment" and self.comment_schema:
            try:
                jsonschema.validate(instance=entry, schema=self.comment_schema)
                return True
            except jsonschema.ValidationError as e:
                logger.error(f"Schema validation failed for comment: {e.message}")
                return False
        else:
            logger.warning(f"No schema available for {schema_type}, skipping validation")
            return True
    
    def read_jsonl(self, path: Path) -> List[Dict[str, Any]]:
        """Read JSONL file, skipping comment lines."""
        if not path.exists():
            logger.warning(f"JSONL file does not exist: {path}")
            return []
        
        entries = []
        try:
            with path.open("r") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON in {path} line {line_num}: {e}")
        except Exception as e:
            logger.error(f"Error reading {path}: {e}")
            return []
        
        return entries
    
    def write_jsonl(self, path: Path, entries: List[Dict[str, Any]]):
        """Write entries to JSONL file with header."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would write {len(entries)} entries to {path}")
            return
        
        try:
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
            
            # State verification (P18)
            if not self._verify_write(path, len(entries)):
                raise ValueError(f"State verification failed for {path}")
            
            logger.info(f"✓ Wrote {len(entries)} entries to {path}")
        except Exception as e:
            logger.error(f"Failed to write {path}: {e}")
            raise
    
    def _verify_write(self, path: Path, expected_count: int) -> bool:
        """Verify write succeeded (P18: State Verification)."""
        if not path.exists():
            logger.error(f"Verification failed: {path} does not exist")
            return False
        
        if path.stat().st_size == 0:
            logger.error(f"Verification failed: {path} is empty")
            return False
        
        # Count entries
        actual_count = len(self.read_jsonl(path))
        if actual_count != expected_count:
            logger.error(f"Verification failed: expected {expected_count} entries, found {actual_count}")
            return False
        
        return True
    
    def _infer_title(self, reference: str, output_type: str) -> str:
        """Infer title from reference if not provided."""
        if output_type == "file":
            return Path(reference).name
        elif output_type == "url":
            return reference[:80] + ("..." if len(reference) > 80 else "")
        else:
            return reference[:80] + ("..." if len(reference) > 80 else "")
    
    def _load_reviews(self) -> List[Dict[str, Any]]:
        """Load all reviews from JSONL."""
        return self.read_jsonl(REVIEWS_JSONL)
    
    def _save_reviews(self, reviews: List[Dict[str, Any]]):
        """Save all reviews to JSONL."""
        self.write_jsonl(REVIEWS_JSONL, reviews)
    
    def add_review(
        self,
        title: str,
        output_type: str,
        reference: str,
        conversation_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        script_path: Optional[str] = None,
        command_name: Optional[str] = None,
        pipeline_run_id: Optional[str] = None,
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
                "thread_id": thread_id,
                "script_path": script_path,
                "command_name": command_name,
                "pipeline_run_id": pipeline_run_id,
                "parent_output_id": parent_output_id
            },
            "review": {
                "status": "pending",
                "sentiment": None,
                "reviewed_by": None,
                "reviewed_at": None,
                "quality_dimensions": {},
                "improvement_notes": {
                    "what_to_change": None,
                    "optimal_state": None,
                    "priority": "medium"
                }
            },
            "tags": tags or [],
            "notes": notes or "",
            "comment_count": 0,
            "latest_comment_at": None
        }
        
        # Validate against schema
        if not self.validate_schema(entry, "review"):
            raise ValueError("Entry failed schema validation")
        
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
        tags: Optional[List[str]] = None,
        conversation_id: Optional[str] = None
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
        if conversation_id:
            entries = [e for e in entries if e["provenance"]["conversation_id"] == conversation_id]
        
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
        
        # Validate against schema
        if not self.validate_schema(comment, "comment"):
            raise ValueError("Comment failed schema validation")
        
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

    def add_output(
        self,
        reference: str,
        output_type: str,
        title: Optional[str] = None,
        conversation_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None,
        sentiment: Optional[str] = None,
        improvement_notes: Optional[str] = None,
        optimal_state: Optional[str] = None,
        **provenance_kwargs
    ) -> str:
        """Add new output review entry."""
        
        # Validate type
        if output_type not in VALID_TYPES:
            raise ValueError(f"Invalid type: {output_type}. Must be one of {VALID_TYPES}")
        
        # Auto-detect conversation if not provided
        if not conversation_id:
            conversation_id = self.detect_conversation_id()
        
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
            "title": title or self._infer_title(reference, output_type),
            "type": output_type,
            "reference": reference,
            "content_hash": content_hash,
            "provenance": provenance_kwargs,
            "review": {
                "status": "pending",
                "sentiment": sentiment,
                "reviewed_by": None,
                "reviewed_at": None,
                "quality_dimensions": {}
            },
            "tags": tags or [],
            "notes": notes,
            "improvement_notes": improvement_notes,
            "optimal_state": optimal_state,
            "comment_count": 0,
            "latest_comment_at": None
        }
        
        # Validate against schema
        if not self.validate_schema(entry, "review"):
            raise ValueError("Entry failed schema validation")
        
        # Add to JSONL
        entries = self.read_jsonl(REVIEWS_JSONL)
        entries.append(entry)
        self.write_jsonl(REVIEWS_JSONL, entries)
        
        logger.info(f"✓ Added review: {entry['id']} - {entry['title']}")
        return entry["id"]
    
    def update_improvement(
        self,
        output_id: str,
        improvement_notes: Optional[str] = None,
        optimal_state: Optional[str] = None
    ) -> bool:
        """Update improvement notes for an existing output."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would update improvement notes for {output_id}")
            return True
        
        try:
            reviews = self._load_reviews()
            
            for review in reviews:
                if review['id'] == output_id:
                    if improvement_notes is not None:
                        review['improvement_notes'] = improvement_notes
                    if optimal_state is not None:
                        review['optimal_state'] = optimal_state
                    review['updated_at'] = datetime.utcnow().isoformat() + 'Z'
                    
                    self._save_reviews(reviews)
                    logger.info(f"Updated improvement notes for {output_id}")
                    return True
            
            logger.warning(f"Output not found: {output_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to update improvement notes: {e}")
            return False

    def update_improvement_notes(
        self,
        output_id: str,
        what_to_change: Optional[str] = None,
        optimal_state: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update structured improvement notes under review.improvement_notes."""
        entries = self.read_jsonl(REVIEWS_JSONL)
        entry = next((e for e in entries if e["id"] == output_id), None)
        if not entry:
            raise ValueError(f"Output not found: {output_id}")
        now = datetime.now(timezone.utc).isoformat()
        review_obj = entry.setdefault("review", {})
        imp = review_obj.setdefault("improvement_notes", {
            "what_to_change": None,
            "optimal_state": None,
            "priority": "medium"
        })
        if what_to_change is not None:
            imp["what_to_change"] = what_to_change
        if optimal_state is not None:
            imp["optimal_state"] = optimal_state
        if priority is not None:
            imp["priority"] = priority
        entry["updated_at"] = now
        self.write_jsonl(REVIEWS_JSONL, entries)
        logger.info(f"✓ Updated improvement notes for {output_id}")
        return entry


def main():
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Output Review Manager")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--test", action="store_true", help="Run basic tests")
    
    args = parser.parse_args()
    
    if args.test:
        logger.info("Running test suite...")
        manager = ReviewManager(dry_run=args.dry_run)
        
        test_results = []
        review = None
        
        # Test: Add review
        try:
            review = manager.add_review(
                title="Test output document",
                output_type="file",
                reference="/home/workspace/Documents/test.md",
                conversation_id="con_test123",
                tags=["test"],
                notes="Test entry"
            )
            logger.info(f"✓ Test 1/6: Created review {review['id']}")
            test_results.append(True)
        except Exception as e:
            logger.error(f"✗ Test 1/6 failed: {e}")
            test_results.append(False)
            return 1
        
        # Test: Add comment
        try:
            comment = manager.add_comment(
                output_id=review["id"],
                body="This is a test comment",
                author="V"
            )
            logger.info(f"✓ Test 2/6: Created comment {comment['id']}")
            test_results.append(True)
        except Exception as e:
            logger.error(f"✗ Test 2/6 failed: {e}")
            test_results.append(False)
            return 1
        
        # Test: Update status
        try:
            updated = manager.update_status(
                output_id=review["id"],
                status="approved",
                sentiment="good",
                reviewed_by="V"
            )
            logger.info(f"✓ Test 3/6: Updated status to {updated['review']['status']}")
            test_results.append(True)
        except Exception as e:
            logger.error(f"✗ Test 3/6 failed: {e}")
            test_results.append(False)
            return 1
        
        # Test: List reviews
        try:
            reviews = manager.list_reviews(status="approved")
            logger.info(f"✓ Test 4/6: Found {len(reviews)} approved reviews")
            test_results.append(True)
        except Exception as e:
            logger.error(f"✗ Test 4/6 failed: {e}")
            test_results.append(False)
        
        # Test: Get comments
        try:
            comments = manager.get_comments(review["id"])
            logger.info(f"✓ Test 5/6: Found {len(comments)} comments for review")
            test_results.append(True)
        except Exception as e:
            logger.error(f"✗ Test 5/6 failed: {e}")
            test_results.append(False)
        
        # Test: Export
        try:
            export_json = manager.export_reviews(status="approved")
            export_data = json.loads(export_json)
            logger.info(f"✓ Test 6/6: Exported {len(export_data)} reviews with comments")
            test_results.append(True)
        except Exception as e:
            logger.error(f"✗ Test 6/6 failed: {e}")
            test_results.append(False)
        
        # Summary
        passed = sum(test_results)
        total = len(test_results)
        logger.info(f"\n{'='*60}")
        logger.info(f"Test Results: {passed}/{total} passed ({int(passed/total*100)}%)")
        logger.info(f"{'='*60}")
        
        return 0 if all(test_results) else 1
    
    print("Use --test to run basic tests")
    return 0


if __name__ == "__main__":
    exit(main())
