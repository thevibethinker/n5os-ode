---
created: 2026-01-14
last_edited: 2026-01-14
version: 1.1
provenance: con_nxvKhHpwzg225fn8
---

# Worker E: Semantic Position Linking

**Project:** vrijenattawar-domain-transition
**Component:** Graph Connectivity / Mind Map
**Status:** Ready for Execution (Audit Phase Complete)

---

## Objective

Fix the "Orphan Problem" in the Mind Map. 80% of positions (99/124) are currently disconnected. This worker uses semantic similarity to auto-generate connections between related intellectual positions.

---

## Technical Specs

1. **Source Data**: `file '/home/workspace/N5/data/positions.db'`
2. **Method**:
    - Use `sentence-transformers` (all-MiniLM-L6-v2) to generate embeddings for all 124 positions.
    - Calculate Cosine Similarity between all pairs.
    - For positions with 0 connections: auto-connect to top 3 neighbors with similarity score > 0.85.
    - Format: `{"target_id": "target-slug", "relationship": "related_to"}`
3. **Safety**: Perform a dry-run first and log proposed connections before updating the DB.

---

## Tasks

- [ ] Generate embeddings for all positions (titles + insights)
- [ ] Identify the 99 orphan positions
- [ ] Calculate similarity matrix
- [ ] Generate proposed connections for orphans
- [ ] Update `positions` table `connections` field with valid JSON arrays
- [ ] Verify graph connectivity in the local SQLite database

---

## Deliverables

1. Updated `positions.db` with populated connections.
2. A summary report of newly created connections.
3. Updated Mind Map visualization (automatic upon site reload).

---

## Execution Command

```bash
python3 /home/workspace/N5/scripts/position_linker.py --apply
```

