---
description: 'Command: social-post-stats'
tags:
- social-media
- analytics
- stats
---
# Social Post: Statistics

View summary statistics for the social media content library.

## Quick Start

```bash
python3 N5/scripts/n5_social_post.py stats
```

## Output

- Total post count
- Breakdown by status (draft, pending, submitted, etc.)
- Breakdown by platform (linkedin, twitter, etc.)

## Example Output

```
Total Posts: 12

By Status:
  draft: 3
  pending: 4
  submitted: 5

By Platform:
  linkedin: 10
  twitter: 2
```

## Use Cases

- Daily standup: Check pending review queue
- Content audit: See publication rate
- Planning: Identify draft backlog

## See Also

- `file N5/commands/social-post-list.md` - List posts
- `file N5/commands/social-post-health.md` - System health check
