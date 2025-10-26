# Social Media Content Library - Quick Start Guide

**Version:** 1.0.0  
**Last Updated:** 2025-10-22

---

## Overview

Automated system for tracking social media posts through their lifecycle:

```
draft → pending → submitted → archived
         ↓
      declined
```

**Registry:** `/home/workspace/N5/data/social-posts.jsonl` (SSOT)  
**Files:** `Knowledge/personal-brand/social-content/{platform}/{status}/`

---

## Quick Start

### 1. Check System Health

```bash
python3 N5/scripts/n5_social_post.py health
```

### 2. List Existing Posts

```bash
# All posts
python3 N5/scripts/n5_social_post.py list

# Filter by status
python3 N5/scripts/n5_social_post.py list --status pending
```

### 3. Add New Post

```bash
# From file
python3 N5/scripts/n5_social_post.py add /path/to/post.md \
    --platform linkedin \
    --status draft

# With tags and conversation link
python3 N5/scripts/n5_social_post.py add /path/to/post.md \
    --platform linkedin \
    --status pending \
    --tags "founder,startup" \
    --conversation-id con_abc123
```

### 4. Update Status

```bash
# Move to pending (ready for review)
python3 N5/scripts/n5_social_post.py status post_abc123 pending

# Mark as published
python3 N5/scripts/n5_social_post.py status post_abc123 submitted \
    --url "https://linkedin.com/posts/..."
```

---

## File Naming Convention

**Format:** `🔗_{YYYY-MM-DD-HHMM}_{platform}_{slug}.md`

**Examples:**
- `🔗_2025-10-22-1630_linkedin_vulnerable-founder.md`
- `🔗_2025-10-22-2100_twitter_product-launch.md`

**Emoji:** 🔗 indicates social/linked content (from emoji-legend system)

---

## Folder Structure

```
Knowledge/personal-brand/social-content/
├── linkedin/
│   ├── draft/          # Work in progress
│   ├── pending/        # Ready for review
│   ├── submitted/      # Published
│   ├── archived/       # Old content
│   └── declined/       # Rejected
├── twitter/
│   └── (same structure)
└── README.md
```

---

## Common Workflows

### Publishing Workflow

```bash
# 1. List posts ready for review
python3 N5/scripts/n5_social_post.py list --status pending

# 2. Review content (open file in editor)

# 3. Publish to platform (external: LinkedIn, Twitter, etc.)

# 4. Mark as submitted
python3 N5/scripts/n5_social_post.py status post_abc123 submitted \
    --url "https://linkedin.com/posts/va/123456"
```

### Draft to Pending

```bash
# Review drafts
python3 N5/scripts/n5_social_post.py list --status draft

# Move to pending when ready
python3 N5/scripts/n5_social_post.py status post_abc123 pending
```

### Declining a Post

```bash
python3 N5/scripts/n5_social_post.py status post_abc123 declined \
    --notes "Too similar to recent post. Consider rewriting with different angle."
```

### Archiving Old Content

```bash
# Find old submitted posts
python3 N5/scripts/n5_social_post.py list --status submitted

# Archive posts older than 6 months
python3 N5/scripts/n5_social_post.py status post_abc123 archived
```

---

## Integration Points

### With LinkedIn Post Generation

When you generate a LinkedIn post with `n5_linkedin_post_generate.py`, it automatically:
1. Creates post file in conversation workspace
2. Imports to social media library
3. Sets status to "pending"
4. Links to source conversation

### With Conversation End

At conversation end, system can:
1. Scan workspace for social media drafts
2. Prompt to import to library
3. Set appropriate status
4. Clean up conversation artifacts

### With Content Library

Social posts can be referenced in the main content library for:
- Link reuse across posts
- Common snippets/CTAs
- Brand voice examples

---

## Commands Reference

| Command | Purpose |
|---------|---------|
| `social-post-add` | Import new post |
| `social-post-status` | Update status, move file |
| `social-post-list` | Query and filter posts |
| `social-post-stats` | View summary statistics |
| `social-post-health` | Run system diagnostics |
| `social-post-verify` | Verify file integrity |

**Detailed docs:** `file N5/commands/social-post-*.md`

---

## Registry Format (JSONL)

Each line is a JSON record:

```json
{
  "id": "post_abc123",
  "created": "2025-10-22T20:04:37Z",
  "updated": "2025-10-22T20:30:15Z",
  "platform": "linkedin",
  "status": "pending",
  "title": "Vulnerable Founder Moment",
  "slug": "vulnerable-founder",
  "file_path": "Knowledge/personal-brand/social-content/linkedin/pending/🔗_2025-10-22-1630_linkedin_vulnerable-founder.md",
  "word_count": 245,
  "character_count": 1450,
  "tags": ["founder", "vulnerability", "authenticity"],
  "scheduled_date": null,
  "published_date": null,
  "published_url": null,
  "source": "manual",
  "conversation_id": "con_f7Xbld76jdowigLo",
  "review_notes": "",
  "version": 1
}
```

---

## Safety Features (Architectural Principles)

- **P5 (Anti-Overwrite):** Atomic file moves with verification
- **P7 (Dry-Run):** All commands support `--dry-run`
- **P11 (Failure Modes):** Rollback on registry update failure
- **P19 (Error Handling):** Specific exceptions with logging
- **P2 (SSOT):** Registry is source of truth, files are artifacts

---

## Troubleshooting

### Post file missing

```bash
python3 N5/scripts/n5_social_post.py health -v
python3 N5/scripts/n5_social_post.py verify
```

### Registry corrupted

```bash
# Backup registry
cp N5/data/social-posts.jsonl N5/data/social-posts.jsonl.backup

# Manually fix JSON syntax errors
# Each line must be valid JSON
```

### Status update failed

Always use `--dry-run` first:

```bash
python3 N5/scripts/n5_social_post.py status post_abc123 pending --dry-run
```

Check logs for specific error.

---

## Next Steps

1. Run health check: `python3 N5/scripts/n5_social_post.py health`
2. List existing posts: `python3 N5/scripts/n5_social_post.py list`
3. Review pending posts: `python3 N5/scripts/n5_social_post.py list --status pending`
4. Publish content and mark as submitted

---

**Questions?** See command docs in `N5/commands/social-post-*.md`
