---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_zTfB7kehxEEHmaoC
---

# WORKER ASSIGNMENT: W2b — Content Library Ingestion

**Blocked by:** W2 (needs `top_posts_candidates.jsonl`)
**Objective:** Ingest selected top posts into V's Content Library.

## Context from Parent

W2 selected V's best LinkedIn posts based on originality + evergreen criteria. Now we ingest the INCLUDE-recommended posts into the Content Library database.

## Input Files

From W2's conversation workspace:
- `top_posts_candidates.jsonl` — Posts with `recommendation: "INCLUDE"`

## Content Library System

Location: `/home/workspace/Knowledge/content-library/`
Database: `/home/workspace/N5/data/content_library.db`
Ingest script: `python3 /home/workspace/N5/scripts/content_ingest.py`

## Ingestion Process

### Step 1: Create Markdown Files

For each INCLUDE post, create a markdown file:

```markdown
---
created: [original_post_date]
last_edited: 2026-01-12
version: 1.0
provenance: linkedin-export-2026-01
type: social-post
platform: linkedin
original_url: [share_link]
tags: [suggested_tags from W2]
originality_score: [from W2]
evergreen_score: [from W2]
---

# [Generated title from first line or topic]

[Full post text]
```

Save to: `/home/workspace/Knowledge/content-library/social-posts/linkedin/`

Filename format: `YYYY-MM-DD_[slug-from-title].md`

### Step 2: Run Ingest Script

For each file:
```bash
python3 /home/workspace/N5/scripts/content_ingest.py "/home/workspace/Knowledge/content-library/social-posts/linkedin/[filename].md" --type social-post
```

### Step 3: Handle MAYBE Posts

For posts with `recommendation: "MAYBE"`:
- Create a review file at `N5/review/content-library/linkedin_maybes_2026-01-12.md`
- List each MAYBE post with its scores and first 100 chars
- V can review and promote later

## Output Artifacts

1. Markdown files in `Knowledge/content-library/social-posts/linkedin/`
2. Database records in `content_library.db`
3. Review file for MAYBE posts (if any)

## Success Criteria

1. All INCLUDE posts have markdown files created
2. All files successfully ingested to database
3. MAYBE posts documented for review
4. No duplicate ingestion (check before creating)

## On Completion

1. Print: "Ingested X posts to Content Library"
2. Print: "Y MAYBE posts staged for review at [path]"
3. Update STATUS.md: mark W2b as ✅ Complete

