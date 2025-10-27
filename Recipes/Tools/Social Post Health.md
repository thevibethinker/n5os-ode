---
description: 'Command: social-post-health'
tags:
- social-media
- health
- diagnostic
---
# Social Post: Health Check

Run diagnostic health check on the social media tracking system.

## Quick Start

```bash
# Basic health check
python3 N5/scripts/n5_social_post.py health

# Verbose output (shows problem details)
python3 N5/scripts/n5_social_post.py health -v
```

## Checks Performed

1. **Registry Exists** - Verifies JSONL file exists
2. **Registry Readable** - Tests JSON parsing
3. **Post Count** - Reports total posts
4. **Platform Distribution** - Shows posts per platform
5. **Status Distribution** - Shows posts per status
6. **File Verification** - Checks all post files exist and are non-empty

## Output

- Registry path and status
- Overall system health (healthy/empty/degraded/error)
- Total post count
- Breakdown by platform and status
- Warning for missing or empty files

## Example Output

```
======================================================================
SOCIAL POSTS SYSTEM HEALTH CHECK
======================================================================

Registry: /home/workspace/N5/data/social-posts.jsonl
  Exists: ✓
  Readable: ✓

Status: HEALTHY
Total Posts: 12

Posts by Platform:
  linkedin: 10
  twitter: 2

Posts by Status:
  draft: 3
  pending: 4
  submitted: 5
```

## Exit Codes

- `0` - Healthy or empty (no issues)
- `1` - Degraded or error (missing files, unreadable registry)

## When to Run

- After bulk imports
- Before/after status updates
- Daily as part of system maintenance
- When troubleshooting issues

## See Also

- `file N5/commands/social-post-verify.md` - Verify specific posts
- `file N5/commands/social-post-stats.md` - View statistics
