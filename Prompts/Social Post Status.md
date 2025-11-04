---
description: 'Command: social-post-status'
tool: true
tags:
- social-media
- workflow
- status
---
# Social Post: Status Update

Update the status of a social media post.

## Quick Start

```bash
# Move post to pending (ready for review)
python3 N5/scripts/n5_social_post.py status post_abc123 pending

# Mark as submitted with URL
python3 N5/scripts/n5_social_post.py status post_abc123 submitted \
    --url "https://linkedin.com/posts/..."

# Decline with review notes
python3 N5/scripts/n5_social_post.py status post_abc123 declined \
    --notes "Too similar to recent post"

# Dry-run first (recommended)
python3 N5/scripts/n5_social_post.py status post_abc123 pending --dry-run
```

## Parameters

- `post_id` - Post ID (from list command)
- `new_status` - Target status
  - `draft` - Work in progress
  - `pending` - Ready for review
  - `submitted` - Published
  - `archived` - Old content
  - `declined` - Rejected
- `--url` - Published URL (for submitted status)
- `--notes` - Review or decline notes
- `--dry-run` - Preview without making changes

## Status Lifecycle

```
draft → pending → submitted → archived
         ↓
      declined
```

## What it Does

1. Finds post by ID in registry
2. Verifies current file exists
3. Creates target status folder
4. Moves file atomically
5. Updates registry with:
   - New status
   - New file path
   - Updated timestamp
   - Published URL (if provided)
   - Review notes (if provided)
6. Increments version number

## Safety

- Always uses dry-run mode first
- Atomic file move operation
- Registry update with rollback on failure
- Verifies source file exists before move

## Examples

### Publishing Workflow

```bash
# 1. Review pending posts
python3 N5/scripts/n5_social_post.py list --status pending

# 2. Publish to platform (external)
# (Copy content, post to LinkedIn/Twitter/etc.)

# 3. Mark as submitted
python3 N5/scripts/n5_social_post.py status post_abc123 submitted \
    --url "https://linkedin.com/posts/va/123456"
```

### Declining Post

```bash
python3 N5/scripts/n5_social_post.py status post_abc123 declined \
    --notes "Tone doesn't match brand voice. Consider rewriting with more professional language."
```

## See Also

- `file N5/commands/social-post-list.md` - List posts
- `file N5/commands/social-post-add.md` - Add new post
- `file N5/docs/social-media-tracking-quickstart.md` - Full guide
