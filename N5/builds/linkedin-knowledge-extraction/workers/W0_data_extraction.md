---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_zTfB7kehxEEHmaoC
---

# WORKER ASSIGNMENT: W0 — Data Extraction & Prep

**Assigned to:** Zo (Mode: Builder)
**Objective:** Extract and normalize V's LinkedIn corpus into clean JSONL files for downstream analysis workers.

## Context from Parent

This is Phase 0 of the `linkedin-knowledge-extraction` build. V wants to analyze their LinkedIn presence to:
1. Populate the Content Library with best posts
2. Extract worldview positions for the Positions System
3. Generate a psychographic portrait

You are preparing the foundation data that W1, W2, and W3 will consume in parallel.

## Your Mission

Extract data from three LinkedIn export sources and produce clean, normalized JSONL files.

## Input Files

| Source | Path | Est. Records |
|--------|------|--------------|
| Posts | `/home/workspace/Datasets/linkedin-full-pre-jan-10/source/extracted/Shares.csv` | 130 |
| Articles | `/home/workspace/Datasets/linkedin-full-pre-jan-10/source/extracted/Articles/Articles/*.html` | 3 |
| Comments | `/home/workspace/Datasets/linkedin-full-pre-jan-10/source/extracted/Comments.csv` | 689 |

## Output Files

All outputs go to YOUR conversation workspace (not the user workspace).

### 1. `posts.jsonl`
One JSON object per line:
```json
{
  "id": "post_001",
  "date": "2025-12-18",
  "timestamp": "2025-12-18T22:02:41",
  "text": "Full post text...",
  "share_link": "https://linkedin.com/...",
  "shared_url": "https://example.com/..." or null,
  "media_url": "..." or null,
  "visibility": "MEMBER_NETWORK",
  "is_reshare": false,
  "word_count": 150,
  "char_count": 850
}
```

**Key logic:**
- `is_reshare = true` if `shared_url` is not null AND `text` is short (<50 words) — indicates sharing someone else's content with brief commentary
- `is_reshare = false` if original content

### 2. `articles.jsonl`
One JSON object per line:
```json
{
  "id": "article_001",
  "filename": "original-filename.html",
  "title": "Article Title",
  "text": "Full article text extracted from HTML...",
  "word_count": 1200
}
```

**Key logic:**
- Extract text from HTML (strip tags)
- Extract title from `<title>` tag or `<h1>`

### 3. `comments.jsonl`
One JSON object per line:
```json
{
  "id": "comment_001",
  "date": "2026-01-08",
  "timestamp": "2026-01-08T18:22:42",
  "text": "Comment text...",
  "link": "https://linkedin.com/...",
  "word_count": 45
}
```

## Validation Requirements

After extraction, print a summary:
```
=== Extraction Summary ===
Posts: X extracted (expected ~130)
  - Original: Y
  - Reshares: Z
Articles: X extracted (expected 3)
Comments: X extracted (expected ~689)

Output files:
  - posts.jsonl: X bytes
  - articles.jsonl: X bytes  
  - comments.jsonl: X bytes
```

## Success Criteria

1. All three JSONL files created in conversation workspace
2. Record counts within 5% of expected
3. No parsing errors
4. `is_reshare` flag correctly applied to posts

## On Completion

1. Print the extraction summary
2. Print the absolute paths to all three output files
3. Update STATUS.md: mark W0 as ✅ Complete
4. Declare: "W0 complete. W1, W2, W3 are now unblocked."

## Files to Reference

- Plan: `file 'N5/builds/linkedin-knowledge-extraction/PLAN.md'`
- Status: `file 'N5/builds/linkedin-knowledge-extraction/STATUS.md'`

