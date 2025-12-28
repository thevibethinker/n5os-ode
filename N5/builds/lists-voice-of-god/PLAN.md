---
created: 2025-12-27
last_edited: 2025-12-27
version: 1
provenance: con_tD6dy87hIIevo1Zw
---
# PLAN: Lists Voice of God - Semantic Search + B-Blocks

**Architect:** Vibe Architect  
**Status:** DEFERRED  
**Priority:** Low (deferred - overkill for current list volume)

> **Deferral Note (2025-12-27):** V correctly identified this as overbuilding for the current use case. The hybrid storage system works well without semantic search. This plan is preserved for future reference if list volume grows or semantic querying becomes valuable.

---

## Open Questions

1. **Embedding Model Choice:** Should we use OpenAI's `text-embedding-3-large` (higher quality, cost) or local `all-MiniLM-L6-v2` (free, lower quality)?
   - **Recommendation:** Use existing `N5_EMBEDDING_PROVIDER` env var - already supports both via `n5_memory_client.py`

2. **Index Granularity:** Should we index:
   - (A) Full markdown file as one chunk
   - (B) Semantic sections (Ingredients, Instructions, Notes separately)
   - **Recommendation:** Start with (A), iterate to (B) if retrieval quality is insufficient

3. **B-Block Generation Trigger:** On-demand vs. at-add-time?
   - **Recommendation:** At-add-time for recipes (complex content), on-demand for simple lists

---

## Alternatives Considered (Nemawashi)

### Alternative A: Direct Integration into n5_memory_client.py
- Add `index_list_item()` method directly
- **Pros:** Single integration point
- **Cons:** Couples list logic with general memory system

### Alternative B: Separate Lists Search Module (Recommended)
- Create `n5_lists_search.py` that uses `n5_memory_client` as backend
- Add "lists" profile to memory client config
- **Pros:** Clean separation, testable, follows existing patterns
- **Cons:** One more file

### Alternative C: SQLite FTS5 (Full-Text Search)
- Use SQLite's built-in FTS5 for search
- **Pros:** No embeddings cost, fast
- **Cons:** Keyword-only, no semantic understanding (defeats "Voice of God" purpose)

**Decision:** Alternative B - Separate module using existing embedding infrastructure

---

## Trap Doors (Irreversible Decisions)

1. **⚠️ Embedding Model Selection:** Once content is indexed with one model, changing models requires full re-index
   - **Mitigation:** Store model name in resource metadata for future migration

2. **⚠️ B-Block Schema:** Once B-Blocks are generated and referenced, schema changes are breaking
   - **Mitigation:** Version the schema from day 1

---

## Checklist

### Phase 1: Memory Client Integration
- [ ] Add "lists" profile to `n5_memory_client.py`
- [ ] Define path prefixes for lists content (`/home/workspace/Lists/content/`)
- [ ] Test: Verify profile loads correctly

### Phase 2: Lists Search CLI
- [ ] Create `n5_lists_search.py` with semantic search capability
- [ ] Implement `search(query, list_slug=None)` → returns ranked items
- [ ] Add `index_all()` to bulk-index existing hybrid entries
- [ ] Test: Search "egg pasta dish" returns Carbonara

### Phase 3: Auto-Index on Add
- [ ] Modify `n5_lists_add.py` to call index when hybrid entry created
- [ ] Extract and index content from linked markdown file
- [ ] Test: Add new recipe → verify it's immediately searchable

### Phase 4: B-Blocks for Lists (Optional Enhancement)
- [ ] Design B-Block schema for lists: `B01_Summary`, `B02_Tags_Expanded`
- [ ] Create `n5_lists_intelligence.py` for block generation
- [ ] Store blocks in JSONL `intelligence` field or sibling file
- [ ] Test: Generate B-Blocks for Carbonara recipe

---

## Phase Details

### Phase 1: Memory Client Integration

**Affected Files:**
- `N5/cognition/n5_memory_client.py`

**Changes:**
1. Add to `self.profiles` dict:
```python
"lists": {
    "path_prefixes": [
        "/home/workspace/Lists/content/",
    ]
}
```

**Unit Test:**
```bash
python3 -c "from n5_memory_client import N5MemoryClient; c = N5MemoryClient(); print(c.profiles.get('lists'))"
```

---

### Phase 2: Lists Search CLI

**Affected Files:**
- `N5/scripts/n5_lists_search.py` (new)
- `N5/cognition/n5_memory_client.py` (import validation)

**Changes:**
1. Create CLI with commands:
   - `python3 n5_lists_search.py search "query"` → semantic search
   - `python3 n5_lists_search.py index --all` → bulk index
   - `python3 n5_lists_search.py index --list recipes` → index specific list

2. Search function:
   - Read JSONL files from Lists/
   - For entries with `links`, extract content via `n5_lists_content_extractor.py`
   - Index content using `n5_memory_client.index_file()`
   - Search using `n5_memory_client.search(query, profile="lists")`

**Unit Tests:**
```bash
# Index existing recipes
python3 N5/scripts/n5_lists_search.py index --all

# Search
python3 N5/scripts/n5_lists_search.py search "classic Italian pasta with eggs"
# Expected: Should return Spaghetti Carbonara
```

---

### Phase 3: Auto-Index on Add

**Affected Files:**
- `N5/scripts/n5_lists_add.py`
- `N5/scripts/n5_lists_search.py` (import)

**Changes:**
1. After writing JSONL entry, check if `links` field exists
2. If hybrid entry, call `index_list_item(item_id, content)`
3. Log indexing success/failure

**Unit Test:**
```bash
# Add new recipe and verify indexing
python3 N5/scripts/n5_lists_add.py recipes "Cacio e Pepe" --tags pasta,italian --notes "Simple Roman pasta"
python3 N5/scripts/n5_lists_search.py search "Roman cheese pepper pasta"
# Expected: Should return Cacio e Pepe
```

---

### Phase 4: B-Blocks for Lists (Optional)

**Affected Files:**
- `N5/scripts/n5_lists_intelligence.py` (new)
- `Lists/schemas/lists.b-blocks.schema.json` (new)

**B-Block Schema (v1):**
```json
{
  "B01_SUMMARY": "2-3 sentence summary of the item",
  "B02_TAGS_EXPANDED": ["tag1", "tag2", "semantic_tag"],
  "B03_RELATED_ITEMS": ["item_id_1", "item_id_2"],
  "generated_at": "2025-12-27T00:00:00Z",
  "schema_version": "1.0"
}
```

**Changes:**
1. Create intelligence generator that reads hybrid content
2. Use LLM to generate B01 (summary), expand tags for B02
3. Store in JSONL `intelligence` field or `Lists/intelligence/<item_id>.json`

---

## Success Criteria

1. **[SC1]** `python3 n5_lists_search.py search "egg pasta"` returns Carbonara within top 3 results
2. **[SC2]** Adding a new hybrid recipe auto-indexes it within same execution
3. **[SC3]** Search latency < 2 seconds for 100 items
4. **[SC4]** (Phase 4) B-Blocks generate valid JSON for any hybrid entry

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Embedding API rate limits | Low | Medium | Batch indexing, local fallback |
| Poor search quality with local model | Medium | Medium | Allow model override via env var |
| Schema evolution breaks existing B-Blocks | Medium | High | Version field + migration script |

---

## Rollback Plan

1. Phase 1-3 are additive - no existing functionality affected
2. If search quality is poor, disable auto-indexing and revert to JSONL-only
3. B-Blocks are stored separately - can be regenerated or deleted without data loss

---

## Handoff Notes

**For Builder:**
- Start with Phase 1 (Memory Client Integration)
- Test thoroughly before Phase 2
- Phase 4 is optional - implement only if Phases 1-3 are solid

**Estimated Effort:**
- Phase 1: 15 min
- Phase 2: 45 min
- Phase 3: 30 min
- Phase 4: 60 min (optional)


