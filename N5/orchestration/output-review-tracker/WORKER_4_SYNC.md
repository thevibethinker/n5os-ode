# Worker 3: CLI Interface

**Orchestrator:** con_YSy4ld4J113LZQ9A\
**Task ID:** W3-CLI\
**Estimated Time:** 40 minutes\
**Dependencies:** Worker 2 (review_manager.py must exist and work)

---

## Mission

Build the command-line interface (`file review_cli.py`    ) for the Output Review Tracker, providing user-friendly commands for all operations.

---

## Context

Users need intuitive CLI commands to flag outputs for review, update statuses, add comments, and filter/export results. This wraps the core ReviewManager with argparse-based commands.

---

## Prerequisites

Ensure these exist (created by Workers 1-2):

- `file N5/schemas/output-review.schema.json` 
- `file N5/schemas/output-review-comment.schema.json` 
- `file N5/scripts/review_manager.py` 
- `file Lists/output_reviews.jsonl` 

---

## Deliverable

**File:** `file N5/scripts/review_cli.py` 

### Commands to Implement

1. `n5 review add` - Add output for review
2. `n5 review list` - List reviews with filters
3. `n5 review show` - Show full details
4. `n5 review status` - Update status/sentiment
5. `n5 review comment` - Add comment
6. `n5 review export` - Export to JSON

---

## Code Template

```markdown
#!/usr/bin/env python3
"""
Output Review CLI - User-facing commands for output review tracking.

Usage:
    n5 review add <reference> [options]
    n5 review list [filters]
    n5 review show <output_id>
    n5 review status <output_id> <status> [options]
    n5 review comment <output_id> [options]
    n5 review export [options]
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

# Add N5 scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from review_manager import ReviewManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def cmd_add(args):
    """Add new output for review."""
    manager = ReviewManager(dry_run=args.dry_run)
    
    try:
        # Infer type from reference
        ref = args.reference
        if Path(ref).exists():
            output_type = "file"
        elif ref.startswith("http"):
            output_type = "url"
        else:
            output_type = args.type or "message"
        
        review = manager.add_review(
            title=args.title or Path(ref).name,
            output_type=output_type,
            reference=ref,
            conversation_id=args.conversation_id,
            thread_name=args.thread,
            script_path=args.script,
            pipeline_run=args.pipeline,
            tags=args.tags.split(",") if args.tags else None,
            notes=args.notes
        )
        
        print(f"✓ Added review: {review['id']}")
        print(f"  Title: {review['title']}")
        print(f"  Type: {review['type']}")
        print(f"  Status: {review['review']['status']}")
        
        if not args.dry_run:
            print(f"\nView with: n5 review show {review['id']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to add review: {e}")
        return 1


def cmd_list(args):
    """List reviews with optional filters."""
    manager = ReviewManager(dry_run=args.dry_run)
    
    try:
        reviews = manager.list_reviews(
            status=args.status,
            sentiment=args.sentiment,
            output_type=args.type,
            tags=args.tags.split(",") if args.tags else None
        )
        
        if not reviews:
            print("No reviews found matching filters.")
            return 0
        
        print(f"\n{'ID':<16} {'Title':<40} {'Status':<12} {'Sentiment':<12} {'Comments':<8}")
        print("-" * 90)
        
        for r in reviews:
            title = r['title'][:37] + "..." if len(r['title']) > 40 else r['title']
            status = r['review']['status']
            sentiment = r['review'].get('sentiment') or "-"
            comments = r.get('comment_count', 0)
            
            print(f"{r['id']:<16} {title:<40} {status:<12} {sentiment:<12} {comments:<8}")
        
        print(f"\nTotal: {len(reviews)} reviews")
        return 0
        
    except Exception as e:
        logger.error(f"Failed to list reviews: {e}")
        return 1


def cmd_show(args):
    """Show full review details."""
    manager = ReviewManager(dry_run=args.dry_run)
    
    try:
        review = manager.get_review(args.output_id)
        
        if not review:
            print(f"Review not found: {args.output_id}")
            return 1
        
        print("\n" + "=" * 80)
        print(f"OUTPUT REVIEW: {review['id']}")
        print("=" * 80)
        print(f"\nTitle: {review['title']}")
        print(f"Type: {review['type']}")
        print(f"Reference: {review['reference']}")
        print(f"Status: {review['review']['status']}")
        print(f"Sentiment: {review['review'].get('sentiment') or '-'}")
        print(f"Created: {review['created_at']}")
        print(f"Updated: {review['updated_at']}")
        
        if review.get('tags'):
            print(f"Tags: {', '.join(review['tags'])}")
        
        if review.get('notes'):
            print(f"\nNotes:\n{review['notes']}")
        
        print("\n--- Provenance ---")
        prov = review['provenance']
        print(f"Conversation: {prov.get('conversation_id') or '-'}")
        if prov.get('thread_name'):
            print(f"Thread: {prov['thread_name']}")
        if prov.get('script_path'):
            print(f"Script: {prov['script_path']}")
        if prov.get('pipeline_run'):
            print(f"Pipeline Run: {prov['pipeline_run']}")
        
        if review['review'].get('quality_dimensions'):
            print("\n--- Quality Scores ---")
            for dim, score in review['review']['quality_dimensions'].items():
                print(f"  {dim}: {score}/10")
        
        # Show comments
        comments = manager.get_comments(review['id'])
        if comments:
            print(f"\n--- Comments ({len(comments)}) ---")
            for c in comments:
                indent = "  " * c.get('thread_depth', 0)
                print(f"\n{indent}[{c['id']}] {c['author']} - {c['created_at']}")
                print(f"{indent}{c['body']}")
                if c.get('context'):
                    print(f"{indent}Context: {c['context']}")
        
        print("\n" + "=" * 80 + "\n")
        return 0
        
    except Exception as e:
        logger.error(f"Failed to show review: {e}")
        return 1


def cmd_status(args):
    """Update review status."""
    manager = ReviewManager(dry_run=args.dry_run)
    
    try:
        # Parse quality dimensions if provided
        quality_dims = None
        if args.score:
            quality_dims = {}
            for score in args.score:
                dim, val = score.split('=')
                quality_dims[dim] = float(val)
        
        updated = manager.update_status(
            output_id=args.output_id,
            status=args.status,
            sentiment=args.sentiment,
            reviewed_by=args.reviewer,
            quality_dimensions=quality_dims,
            notes=args.note
        )
        
        print(f"✓ Updated {args.output_id}")
        print(f"  Status: {updated['review']['status']}")
        if updated['review'].get('sentiment'):
            print(f"  Sentiment: {updated['review']['sentiment']}")
        
        if not args.dry_run:
            print(f"\nView with: n5 review show {args.output_id}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to update status: {e}")
        return 1


def cmd_comment(args):
    """Add comment to review."""
    manager = ReviewManager(dry_run=args.dry_run)
    
    try:
        comment = manager.add_comment(
            output_id=args.output_id,
            body=args.body,
            author=args.author or "V",
            context=args.context,
            parent_comment_id=args.parent,
            tags=args.tags.split(",") if args.tags else None
        )
        
        print(f"✓ Added comment: {comment['id']}")
        print(f"  Thread depth: {comment['thread_depth']}")
        
        if not args.dry_run:
            print(f"\nView with: n5 review show {args.output_id}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to add comment: {e}")
        return 1


def cmd_export(args):
    """Export reviews to JSON."""
    manager = ReviewManager(dry_run=args.dry_run)
    
    try:
        export_json = manager.export_reviews(
            status=args.status,
            sentiment=args.sentiment
        )
        
        if args.output:
            output_path = Path(args.output)
            if not args.dry_run:
                output_path.write_text(export_json)
                print(f"✓ Exported to: {output_path}")
            else:
                print(f"[DRY RUN] Would export to: {output_path}")
        else:
            print(export_json)
        
        # Show count
        count = len(json.loads(export_json))
        print(f"\nExported {count} reviews")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to export: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="n5 review",
        description="Output Review Tracker CLI"
    )
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # ADD command
    add_parser = subparsers.add_parser("add", help="Add output for review")
    add_parser.add_argument("reference", help="File path, URL, or message")
    add_parser.add_argument("--title", help="Title (auto-detected if not provided)")
    add_parser.add_argument("--type", choices=["file", "message", "image", "video", "transcript", "url"], help="Output type")
    add_parser.add_argument("--conversation-id", help="Conversation ID (auto-detected)")
    add_parser.add_argument("--thread", help="Thread name")
    add_parser.add_argument("--script", help="Script path")
    add_parser.add_argument("--pipeline", help="Pipeline/run ID")
    add_parser.add_argument("--tags", help="Comma-separated tags")
    add_parser.add_argument("--notes", help="Notes")
    add_parser.set_defaults(func=cmd_add)
    
    # LIST command
    list_parser = subparsers.add_parser("list", help="List reviews")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--sentiment", help="Filter by sentiment")
    list_parser.add_argument("--type", help="Filter by type")
    list_parser.add_argument("--tags", help="Comma-separated tags")
    list_parser.set_defaults(func=cmd_list)
    
    # SHOW command
    show_parser = subparsers.add_parser("show", help="Show review details")
    show_parser.add_argument("output_id", help="Output ID")
    show_parser.set_defaults(func=cmd_show)
    
    # STATUS command
    status_parser = subparsers.add_parser("status", help="Update status")
    status_parser.add_argument("output_id", help="Output ID")
    status_parser.add_argument("status", choices=["pending", "in_review", "approved", "issue", "training", "archived"], help="New status")
    status_parser.add_argument("--sentiment", choices=["excellent", "good", "acceptable", "issue"], help="Sentiment")
    status_parser.add_argument("--reviewer", help="Reviewer name")
    status_parser.add_argument("--score", action="append", help="Quality score (e.g., tone=8)")
    status_parser.add_argument("--note", help="Status note")
    status_parser.set_defaults(func=cmd_status)
    
    # COMMENT command
    comment_parser = subparsers.add_parser("comment", help="Add comment")
    comment_parser.add_argument("output_id", help="Output ID")
    comment_parser.add_argument("--body", required=True, help="Comment text")
    comment_parser.add_argument("--author", help="Author name (default: V)")
    comment_parser.add_argument("--context", help="Context/excerpt being commented on")
    comment_parser.add_argument("--parent", help="Parent comment ID (for replies)")
    comment_parser.add_argument("--tags", help="Comma-separated tags")
    comment_parser.set_defaults(func=cmd_comment)
    
    # EXPORT command
    export_parser = subparsers.add_parser("export", help="Export to JSON")
    export_parser.add_argument("--status", help="Filter by status")
    export_parser.add_argument("--sentiment", help="Filter by sentiment")
    export_parser.add_argument("--output", help="Output file path")
    export_parser.set_defaults(func=cmd_export)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    exit(main())
```

---

## Success Criteria

- ✅ All 6 commands implemented and working
- ✅ Help text clear and useful
- ✅ Output formatting clean and readable
- ✅ Error handling with helpful messages
- ✅ Dry-run mode works for all commands
- ✅ Auto-detection works (conversation ID, type)

---

## Testing

```bash
# Test help
python3 N5/scripts/review_cli.py --help
python3 N5/scripts/review_cli.py add --help

# Test add (dry-run)
python3 N5/scripts/review_cli.py add Documents/N5.md --title "N5 System Docs" --tags "docs,n5" --dry-run

# Test add (real)
python3 N5/scripts/review_cli.py add Documents/N5.md --title "N5 System Docs" --tags "docs,n5"

# Get the output_id from previous command, then test other commands
OUTPUT_ID="out_XXXXXXXXXXXX"  # Replace with actual ID

# Test list
python3 N5/scripts/review_cli.py list
python3 N5/scripts/review_cli.py list --status pending

# Test show
python3 N5/scripts/review_cli.py show $OUTPUT_ID

# Test status update
python3 N5/scripts/review_cli.py status $OUTPUT_ID in_review --sentiment good --reviewer "V" --dry-run
python3 N5/scripts/review_cli.py status $OUTPUT_ID in_review --sentiment good --reviewer "V"

# Test comment
python3 N5/scripts/review_cli.py comment $OUTPUT_ID --body "Great documentation!" --author "V" --dry-run
python3 N5/scripts/review_cli.py comment $OUTPUT_ID --body "Great documentation!" --author "V"

# Test export
python3 N5/scripts/review_cli.py export --sentiment good
python3 N5/scripts/review_cli.py export --sentiment excellent --output /tmp/training.json
```

---

## Report Back

When complete, report:

1. All commands tested
2. Sample output showing success
3. Any UX improvements made
4. Ready for Worker 4

---

**Orchestrator Contact:** con_YSy4ld4J113LZQ9A\
**Created:** 2025-10-19 15:18 ET