---
description: 'Command: social-post-list'
tags:
- social-media
- query
- list
tool: true
---
# Social Post: List

List social media posts with optional filters.

## Quick Start

```bash
# List all posts
python3 N5/scripts/n5_social_post.py list

# Filter by status
python3 N5/scripts/n5_social_post.py list --status pending

# Filter by platform
python3 N5/scripts/n5_social_post.py list --platform linkedin

# Combined filters
python3 N5/scripts/n5_social_post.py list \
    --platform linkedin \
    --status pending \
    --limit 10
```

## Parameters

- `--platform` - Filter by platform (linkedin, twitter, etc.)
- `--status` - Filter by status (draft, pending, submitted, etc.)
- `--limit` - Maximum number of posts to show

## Output Format

For each post:
- ID (for use in other commands)
- Title
- Platform
- Status
- Creation date
- Word count
- File path
- Published URL (if submitted)
- Tags

## Examples

### Review Pending Posts

```bash
python3 N5/scripts/n5_social_post.py list --status pending
```

### Find LinkedIn Posts

```bash
python3 N5/scripts/n5_social_post.py list --platform linkedin
```

### Published Content Audit

```bash
python3 N5/scripts/n5_social_post.py list --status submitted
```

## See Also

- `file N5/commands/social-post-add.md` - Add new post
- `file N5/commands/social-post-status.md` - Update status
- `file N5/commands/social-post-stats.md` - View statistics
