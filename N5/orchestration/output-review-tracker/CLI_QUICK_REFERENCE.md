# Output Review CLI - Quick Reference

## Commands

```bash
# Add output for review
n5 review add <reference> [--title TITLE] [--type TYPE] [--tags TAGS] [--notes NOTES]

# List reviews with filters
n5 review list [--status STATUS] [--sentiment SENTIMENT] [--type TYPE] [--tags TAGS]

# Show review details
n5 review show <output_id>

# Update status
n5 review status <output_id> <status> [--sentiment SENTIMENT] [--reviewer NAME] [--score dim=val]

# Add comment
n5 review comment <output_id> --body "text" [--author NAME] [--parent comment_id]

# Export to JSON
n5 review export [--status STATUS] [--sentiment SENTIMENT] [--output FILE]
```

## Quick Examples

```bash
# Flag a file for review
n5 review add Documents/report.md --tags "needs-review" --conversation-id "con_abc"

# Update to approved
n5 review status out_abc123 approved --sentiment excellent --reviewer "V"

# Add quality scores
n5 review status out_abc123 approved --score accuracy=9 --score tone=10

# Add comment
n5 review comment out_abc123 --body "Great work!" --author "V"

# Reply to comment
n5 review comment out_abc123 --body "Thanks!" --parent cmt_xyz789

# Export excellent outputs
n5 review export --sentiment excellent --output /tmp/training.json

# List pending reviews
n5 review list --status pending
```

## Valid Values

**Status:** pending, in_review, approved, rejected, archived  
**Sentiment:** poor, mixed, good, excellent  
**Type:** file, message, image, video, transcript, url

## Dry-Run Mode

Add `--dry-run` before any command to preview without writing:
```bash
n5 review --dry-run add Documents/test.md
n5 review --dry-run status out_abc123 approved
```
