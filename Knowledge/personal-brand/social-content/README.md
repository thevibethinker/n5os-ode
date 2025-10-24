# Social Media Content Library

Automated tracking system for social media posts throughout their lifecycle.

---

## Quick Reference

### View Posts
```bash
python3 /home/workspace/N5/scripts/n5_social_post.py list
python3 /home/workspace/N5/scripts/n5_social_post.py list --status pending
python3 /home/workspace/N5/scripts/n5_social_post.py stats
```

### Update Status
```bash
python3 /home/workspace/N5/scripts/n5_social_post.py status <post_id> <new_status>
```

### Add Post
```bash
python3 /home/workspace/N5/scripts/n5_social_post.py add <file> --platform <platform>
```

---

## Status Lifecycle

```
draft → pending → submitted → archived
         ↓
      declined
```

**Statuses:**
- `draft` - Work in progress, not ready for review
- `pending` - Ready for review and publication
- `submitted` - Published to platform
- `archived` - Old content, kept for reference
- `declined` - Rejected, won't publish

---

## File Naming

**Format:** `🔗_{YYYY-MM-DD-HHMM}_{platform}_{slug}.md`

**Examples:**
- `🔗_2025-10-22-1630_linkedin_vulnerable-founder.md`
- `🔗_2025-10-22-2100_twitter_product-launch.md`

**Note:** 🔗 emoji indicates linked/social content (from N5 emoji-legend system)

---

## Folder Structure

```
social-content/
├── linkedin/
│   ├── draft/          # Work in progress
│   ├── pending/        # Ready for review
│   ├── submitted/      # Published
│   ├── archived/       # Old content
│   └── declined/       # Rejected
├── twitter/
│   └── (same structure)
└── README.md (this file)
```

---

## Registry

**Location:** `/home/workspace/N5/data/social-posts.jsonl`

The registry is the **single source of truth** (SSOT). Files in this directory are managed artifacts.

Each post includes:
- Unique ID
- Title, slug
- Platform, status
- Word count, character count
- Tags
- Creation/update timestamps
- Publication URL (when submitted)
- Source conversation
- Version number

---

## Integration

- **LinkedIn Post Generation:** Auto-imports generated posts
- **Content Library:** Reference posts in link/snippet library
- **Commands System:** Registered N5 commands for all operations
- **Conversation End:** Can scan for draft posts

---

## Documentation

**Quick Start:** `file /home/workspace/N5/docs/social-media-tracking-quickstart.md`  
**Commands:** `file /home/workspace/N5/commands/social-post-*.md`

---

## Maintenance

### Daily
```bash
python3 N5/scripts/n5_social_post.py list --status pending
```

### Weekly
```bash
python3 N5/scripts/n5_social_post.py stats
python3 N5/scripts/n5_social_post.py health
```

### Monthly
- Archive old submitted posts
- Review declined posts for repurposing

---

**Version:** 1.0.0  
**Last Updated:** 2025-10-22  
**Implemented by:** WORKER_dIIMkZpOMGAsZJre
