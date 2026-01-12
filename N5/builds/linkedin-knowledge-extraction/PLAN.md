---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_zTfB7kehxEEHmaoC
---

# Build Plan: LinkedIn Knowledge Extraction

## Objective

Extract structured value from V's LinkedIn corpus (130 posts, 3 articles, 689 comments) and populate:
1. **Content Library** — Best original, evergreen posts archived as reusable social content
2. **Positions System** — Worldview positions extracted and indexed (extend existing if ≥50% overlap)
3. **Psychographic Portrait** — Synthesis-level analysis of V as a LinkedIn presence

## Key Decisions (from V)

- **Position overlap ≥50%**: Extend existing position, do not create new or flag
- **Top post criteria**: Originality + Evergreen only (not reshares, still relevant)
- **Portrait depth**: Synthesis/semantic level (voice library has linguistic artifacts)

## Data Sources

| Source | Records | Path |
|--------|---------|------|
| Posts | 130 | `Datasets/linkedin-full-pre-jan-10/source/extracted/Shares.csv` |
| Articles | 3 | `Datasets/linkedin-full-pre-jan-10/source/extracted/Articles/Articles/*.html` |
| Comments | 689 | `Datasets/linkedin-full-pre-jan-10/source/extracted/Comments.csv` |

## Phase Checklist

### Phase 0: Foundation (W0)
- [x] Extract posts to `posts.jsonl` (date, text, URLs, visibility, is_reshare flag)
- [x] Extract articles to `articles.jsonl` (title, full text from HTML)
- [x] Extract comments to `comments.jsonl` (date, text, link)
- [x] Validate record counts match source

**Affected files:**
- `Datasets/linkedin-full-pre-jan-10/source/extracted/Shares.csv` (read)
- `Datasets/linkedin-full-pre-jan-10/source/extracted/Articles/Articles/*.html` (read)
- `Datasets/linkedin-full-pre-jan-10/source/extracted/Comments.csv` (read)
- Conversation workspace: `posts.jsonl`, `articles.jsonl`, `comments.jsonl` (write)

### Phase 1: Parallel Analysis (W1, W2, W3)

#### W1: Thematic Coding
- [ ] Topic frequency distribution across posts
- [ ] Emotional markers (frustration, excitement, advocacy, humor)
- [ ] Recurring phrases / verbal fingerprints
- [ ] Self-positioning patterns (how V frames himself)
- [ ] Output `thematic_analysis.json`

#### W2: Top Posts Selection
- [ ] Filter to original posts only (exclude reshares)
- [ ] Score on evergreen quality (still relevant, not time-bound)
- [ ] Select top 15-25 posts
- [ ] Tag each with themes and recommended use cases
- [ ] Output `top_posts_candidates.jsonl`

#### W3: Position Extraction
- [ ] Extract compound insights from posts + articles
- [ ] Structure: domain, title, insight, reasoning, stakes, conditions
- [ ] Run overlap check against existing 106 positions (threshold 0.5)
- [ ] Mark candidates as `extend:<position-id>` or `new`
- [ ] Output `position_candidates.jsonl`

**Affected files (Phase 1):**
- Conversation workspace: `posts.jsonl`, `articles.jsonl`, `comments.jsonl` (read)
- Conversation workspace: `thematic_analysis.json`, `top_posts_candidates.jsonl`, `position_candidates.jsonl` (write)
- `N5/data/positions.db` (read for overlap check)

### Phase 2: System Integration (W2b, W3b)

#### W2b: Content Library Ingest
- [ ] Create markdown files for each selected post
- [ ] Ingest via `content_ingest.py --type social-post`
- [ ] Verify DB records created

#### W3b: Position Integration
- [ ] For `extend` candidates: run `positions.py extend` commands
- [ ] For `new` candidates: generate HITL review sheet
- [ ] Output review sheet to `N5/review/positions/`

**Affected files (Phase 2):**
- `Knowledge/content-library/social-posts/*.md` (write)
- `N5/data/content_library.db` (write)
- `N5/data/positions.db` (write for extends)
- `N5/review/positions/2026-01-12_linkedin-positions-review_batch-001.md` (write)

### Phase 3: Synthesis (W4)

- [ ] Synthesize all analysis into psychographic portrait
- [ ] Structure: Quick Read, Thematic Map, Emotional Landscape, Values, Blind Spots
- [ ] Output to `Knowledge/content-library/personal/linkedin-psychographic-portrait.md`

**Affected files (Phase 3):**
- Conversation workspace: all analysis files (read)
- `Knowledge/content-library/personal/linkedin-psychographic-portrait.md` (write)

### Phase 4: Human Review (Manual)

- [ ] V reviews position candidates in HITL sheet
- [ ] Mark each as accept/amend/reject
- [ ] Run `b32_position_extractor.py review-sheet-ingest` + `promote-reviewed`

## Worker Dependency Graph

```
W0 (Foundation)
 │
 ├──► W1 (Thematic) ──────────────────┐
 │                                    │
 ├──► W2 (Top Posts) ──► W2b (Ingest) │
 │                                    ├──► W4 (Portrait)
 └──► W3 (Positions) ──► W3b (HITL)───┘
```

## Success Criteria

1. **Content Library**: 15-25 new posts in `social-posts/` with DB records
2. **Positions**: Existing positions extended + new candidates in HITL queue
3. **Portrait**: Complete synthesis document at semantic level
4. All source data preserved in conversation workspace for audit

## Estimated Effort

| Phase | Workers | Parallel | Est. Turns |
|-------|---------|----------|------------|
| 0 | W0 | No | 1 |
| 1 | W1, W2, W3 | Yes | 1-2 each |
| 2 | W2b, W3b | Yes | 1 each |
| 3 | W4 | No | 1 |
| **Total** | 7 workers | | 7-9 turns |


