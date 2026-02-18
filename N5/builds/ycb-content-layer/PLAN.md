---
created: 2026-02-11
last_edited: 2026-02-11
version: 1.0
provenance: con_b35rjnbig858pzQQ
---

# Build Plan: YCB Content Layer Integration

## Objective
Integrate Your Commonbase architectural patterns into N5 OS: Entry/Comment threading, Content Carts, Preprocessor Pipeline, and Semantic Links.

## Background
Your Commonbase (YCB) is an open-source project for "Personal Library Science"—a self-organizing scrapbook for storing, searching, synthesizing, and sharing personal knowledge. After reviewing YCB, we've identified 4 key architectural patterns worth borrowing:

1. **Entry/Comment Threading** - Non-destructive annotation via a DAG of comments
2. **Content Carts** - Collections of entries for synthesis workflows  
3. **Preprocessor Pipeline** - Staged content extraction, cleaning, and enrichment
4. **Semantic Links** - Auto-discovered relationships via embeddings

## Current State
- N5 has a Content Library at `Knowledge/content-library/` with ~87 items
- Content is ingested via `N5/scripts/content_ingest.py`
- SQLite database at `N5/data/content_library.db` with `items` table
- Vector embeddings already exist (186K vectors in ANN index)

## Target State
- Threaded discussions on any content item
- Carts for gathering content for synthesis
- Multi-stage preprocessor (extract → clean → enrich → store)
- Auto-discovered semantic links between related items
- CLI commands: `n5 content thread`, `n5 content cart`, `n5 content links`

## Open Questions
- [x] Which embedding store to use? → Reuse existing `N5/cognition/vectors_v2.db`
- [x] Should carts be persistent or session-only? → Persistent with archive option
- [x] Preprocessor: in-place refactor or new module? → New module, refactor ingest to use it

## Phase 1: Database Schema (Wave 1)
**Drops:** D1.1 (Threading Schema), D1.2 (Carts Schema)

Create tables:
- `content_threads` - Thread headers
- `thread_comments` - Comments/syntheses (YCB model)
- `entry_links` - Explicit/semantic connections
- `content_carts` - Cart headers
- `cart_items` - Items in carts

## Phase 2: CLI Commands (Wave 2)
**Drops:** D2.1 (Thread Commands), D2.2 (Cart Commands)

Implement CLI:
- `n5 content thread create/list/show`
- `n5 content comment add/edit/delete`
- `n5 content cart create/list/show/add/remove`
- `n5 content cart synthesize` (the big one)

## Phase 3: Preprocessor Pipeline (Wave 3)
**Drops:** D3.1 (Preprocessor)

Create `content_preprocessor.py` with stages:
1. Extract (trafilatura/pdfplumber)
2. Clean (boilerplate removal)
3. Enrich (entities, summary, embeddings)
4. Store (content library)

Refactor `content_ingest.py` to use pipeline.

## Phase 4: Semantic Links (Wave 4)
**Drops:** D4.1 (Semantic Links Engine)

Implement:
- `SemanticLinkEngine` class
- `n5 content links compute/related/graph` commands
- Use existing vector store for similarity queries

## Success Criteria
- [ ] Thread can be created on any content item
- [ ] Comments can be nested (parent-child)
- [ ] Cart can gather items and synthesize them
- [ ] Preprocessor extracts, cleans, enriches content
- [ ] Semantic links connect related items
- [ ] All features work via CLI

## Integration Points
- Content Library database (`N5/data/content_library.db`)
- Vector store (`N5/cognition/vectors_v2.db`)
- Existing `content_ingest.py` (refactor target)
- CLI namespace `n5 content` (extend)

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Schema migration breaks existing data | Add tables only, don't modify existing |
| Vector store query performance | Use existing ANN index, don't rebuild |
| CLI namespace collision | Use `n5 content <subcommand>` pattern |

## Timeline Estimate
- Wave 1: 1-2 hours (schema design is straightforward)
- Wave 2: 2-3 hours (CLI commands + integration)
- Wave 3: 2-3 hours (pipeline + refactor)
- Wave 4: 1-2 hours (leverage existing vector store)
- Total: ~8 hours of Drop work

## Rollback Plan
- Schema: Delete new tables, data loss limited to new features
- Code: Remove new scripts, revert content_ingest.py changes
- No changes to existing content items or vector store

## Notes
- Delegate-only mode enabled (all work in Drops)
- Build uses existing N5 infrastructure (vector store, DB patterns)
- YCB inspiration but N5 implementation (not a port)
