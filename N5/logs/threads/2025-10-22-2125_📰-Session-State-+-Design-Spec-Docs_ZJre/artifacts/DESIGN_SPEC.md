# Social Media Content Library - Design Specification

**Version:** 1.0.0  
**Date:** 2025-10-22  
**Status:** Design → Implementation

---

## Overview

Automated system for tracking social media posts through their lifecycle: draft → review → pending → submitted → archived.

**Integration:** Extends existing `content_library.py` + adds dedicated social post tracking

---

## Architecture

### Storage (Option C: Hybrid)

**Registry:** `/home/workspace/N5/data/social-posts.jsonl` (SSOT)
- One record per post
- Tracks status, metadata, file location, platform

**Files:** `Knowledge/personal-brand/social-content/{platform}/{status}/`
```
Knowledge/personal-brand/social-content/
├── linkedin/
│   ├── draft/
│   ├── pending/
│   ├── submitted/
│   └── archived/
├── twitter/
│   └── (same structure)
└── README.md
```

**Naming Convention:**
- Format: `🔗_{YYYY-MM-DD-HHMM}_{platform}_{slug}.md`
- Example: `🔗_2025-10-22-1630_linkedin_vulnerable-founder.md`
- Emoji: 🔗 (from emoji-legend.json, indicates linked/social content)

---

## Schema

### Social Post Record (JSONL)

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

## Status Lifecycle

```
draft → pending → submitted → archived
         ↓
      declined
```

**States:**
- `draft` - Work in progress, not ready for review
- `pending` - Ready for review/approval
- `submitted` - Published to platform
- `archived` - Old content, kept for reference
- `declined` - Rejected, won't publish

---

## Commands & Workflows

### Core Commands (to build)

1. **`social-post-add`** - Import/create new social post
   - Auto-detect platform from content
   - Generate ID, slug, move to correct folder
   - Add to registry

2. **`social-post-status`** - Update post status
   - Move file to new status folder
   - Update registry
   - Record transition timestamps

3. **`social-post-list`** - Query posts
   - Filter by platform, status, date range
   - Display summary table

4. **`social-post-review`** - Batch review pending posts
   - TUI showing pending posts
   - Approve → submitted | Decline | Keep pending

5. **`social-post-export`** - Export for publishing
   - Generate clean copy without metadata
   - Copy to clipboard

### Integration Points

- `linkedin-post-generate` → auto-add to library as "draft"
- `content-library` → reference social posts in links
- `conversation-end` → scan for social content, prompt to add

---

## Automation Hooks

### Auto-import triggers:
1. **Post-generation**: When `n5_linkedin_post_generate.py` runs
2. **Conversation-end**: Scan workspace for `linkedin_post_*.md` files
3. **Manual**: User runs `social-post-add <file>`

### Auto-status update:
1. **Published**: User provides URL → status=submitted, record URL
2. **Scheduled**: User sets date → status=pending, record schedule

---

## Files to Create

### Scripts
1. `/home/workspace/N5/scripts/n5_social_post.py` - Main CLI
2. `/home/workspace/N5/scripts/social_post_lib.py` - Library functions

### Commands
1. `/home/workspace/N5/commands/social-post-add.md`
2. `/home/workspace/N5/commands/social-post-status.md`
3. `/home/workspace/N5/commands/social-post-list.md`
4. `/home/workspace/N5/commands/social-post-review.md`

### Config
1. `/home/workspace/N5/data/social-posts.jsonl` - Registry (create empty)
2. Update `/home/workspace/N5/config/commands.jsonl` - Register commands

### Docs
1. `/home/workspace/N5/docs/social-media-tracking-quickstart.md`

---

## Testing Plan

### Phase 1: Import Test Data
- Import 2 posts from parent conversation
- Import 2 posts from existing linkedin folder
- Verify file naming, metadata, registry

### Phase 2: Status Transitions
- Move post: draft → pending
- Move post: pending → submitted (with URL)
- Move post: pending → declined
- Verify file moves, registry updates

### Phase 3: Querying
- List all posts
- Filter by status=pending
- Filter by platform=linkedin
- Verify output format

### Phase 4: Integration
- Generate new post with linkedin-post-generate
- Verify auto-import to library
- Test conversation-end scan

---

## Success Criteria

- [ ] Registry JSONL created and validated
- [ ] Folder structure created
- [ ] 4 test posts imported correctly
- [ ] Files follow naming convention with 🔗
- [ ] Status transitions work (tested all paths)
- [ ] Commands registered and functional
- [ ] Documentation complete
- [ ] No undocumented placeholders (P21)
- [ ] Dry-run tested before production (P7)
- [ ] Integration with existing linkedin-post-generate

---

## Architectural Compliance

**P0 (Rule-of-Two):** ✅ Single registry file, minimal context
**P1 (Human-Readable):** ✅ JSONL + markdown files
**P2 (SSOT):** ✅ Registry is source of truth, files are artifacts
**P5 (Anti-Overwrite):** ✅ Dry-run required, verification steps
**P7 (Dry-Run):** ✅ All commands support --dry-run
**P11 (Failure Modes):** ✅ Validates before moves, atomic operations
**P15 (Complete Before Claiming):** ✅ All success criteria must pass
**P16 (No Invented Limits):** ✅ No artificial constraints
**P19 (Error Handling):** ✅ Try/except with specific errors
**P20 (Modular):** ✅ Lib + CLI separation
**P21 (Document Assumptions):** ✅ This spec documents all decisions
**P22 (Language):** ✅ Python (data processing + LLM corpus advantage)

---

## Next Steps

1. Create folder structure
2. Build `social_post_lib.py` with core functions
3. Build `n5_social_post.py` CLI
4. Create command markdown files
5. Register commands
6. Import test data
7. Test status transitions
8. Write documentation
9. Update parent with completion status

---

**Ready to implement!**
