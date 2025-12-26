---
created: 2025-12-16
last_edited: 2025-12-16
version: 1.0
type: build_plan
status: complete
---

# Plan: ANN Vector Index for brain.db Semantic Search

**Objective:** Add HNSW-based approximate nearest neighbor indexing to `n5_memory_client.py` with rebuild-only generation, runtime toggle, and transparent fallback.

**Trigger:** Audit confirmed brute-force O(N) search; need sub-linear search for scaling.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

<!-- All resolved during Nemawashi -->
- [x] Which ANN library? → `hnswlib` (lightweight, fast, simple)
- [x] Where to store index? → `N5/cognition/brain.hnsw` alongside `brain.db`
- [x] How to handle dimension mismatch? → Store dimension in index metadata, rebuild if changed
- [x] Fallback strategy? → If index missing/stale/disabled, use existing brute-force

---

## Checklist

### Phase 1: Core Infrastructure
- ☑ Install hnswlib dependency
- ☑ Add index file path constant and USE_VECTOR_INDEX env toggle
- ☑ Create `_load_ann_index()` method
- ☑ Create `_search_ann()` method
- ☑ Test: Verify index loads and searches return results

### Phase 2: Index Builder & Integration
- ☑ Create `rebuild_ann_index()` method
- ☑ Create standalone `n5_rebuild_ann_index.py` script
- ☑ Integrate ANN path into `search()` with fallback
- ☑ Test: End-to-end search with index vs brute-force benchmark

---

## Phase 1: Core Infrastructure

### Affected Files
- `N5/cognition/n5_memory_client.py` - UPDATE - Add ANN loading and search methods
- `requirements.txt` or inline pip - UPDATE - Add hnswlib dependency

### Changes

**1.1 Add Constants and Imports:**
At top of `n5_memory_client.py`, add:
```python
# ANN Index support
try:
    import hnswlib
    HAS_HNSWLIB = True
except ImportError:
    HAS_HNSWLIB = False

ANN_INDEX_PATH = "/home/workspace/N5/cognition/brain.hnsw"
```

**1.2 Add Toggle Check in `__init__`:**
```python
self.use_vector_index = os.getenv("USE_VECTOR_INDEX", "true").lower() == "true"
self.ann_index = None
self.ann_block_ids = []  # Ordered list mapping index position → block_id
if self.use_vector_index:
    self._load_ann_index()
```

**1.3 Create `_load_ann_index()` Method:**
```python
def _load_ann_index(self) -> bool:
    """Load the pre-built HNSW index if available."""
    if not HAS_HNSWLIB:
        LOG.warning("hnswlib not installed, falling back to brute-force")
        return False
    
    index_path = ANN_INDEX_PATH
    mapping_path = ANN_INDEX_PATH + ".ids"
    
    if not os.path.exists(index_path) or not os.path.exists(mapping_path):
        LOG.info("ANN index not found, will use brute-force search")
        return False
    
    try:
        # Load block_id mapping
        with open(mapping_path, 'r') as f:
            self.ann_block_ids = json.load(f)
        
        # Detect dimension from first vector in DB
        cursor = self._get_db().cursor()
        cursor.execute("SELECT embedding FROM vectors LIMIT 1")
        row = cursor.fetchone()
        if not row:
            return False
        dim = len(np.frombuffer(row[0], dtype=np.float32))
        
        # Load index
        self.ann_index = hnswlib.Index(space='cosine', dim=dim)
        self.ann_index.load_index(index_path)
        self.ann_index.set_ef(100)  # Search accuracy parameter
        LOG.info(f"ANN index loaded: {len(self.ann_block_ids)} vectors, dim={dim}")
        return True
    except Exception as e:
        LOG.warning(f"Failed to load ANN index: {e}")
        self.ann_index = None
        self.ann_block_ids = []
        return False
```

**1.4 Create `_search_ann()` Method:**
```python
def _search_ann(self, query_vec: np.ndarray, k: int = 100) -> List[Tuple[str, float]]:
    """Search ANN index, return list of (block_id, distance)."""
    if self.ann_index is None or not self.ann_block_ids:
        return []
    
    try:
        # hnswlib returns (labels, distances) where labels are indices
        labels, distances = self.ann_index.knn_query(query_vec.reshape(1, -1), k=min(k, len(self.ann_block_ids)))
        
        results = []
        for idx, dist in zip(labels[0], distances[0]):
            if idx < len(self.ann_block_ids):
                block_id = self.ann_block_ids[idx]
                # Convert cosine distance to similarity: sim = 1 - dist
                similarity = 1.0 - dist
                results.append((block_id, similarity))
        return results
    except Exception as e:
        LOG.warning(f"ANN search failed: {e}")
        return []
```

### Unit Tests
- `pip install hnswlib` succeeds
- `_load_ann_index()` returns False gracefully when index doesn't exist
- After Phase 2 builds index: `_search_ann()` returns results with valid block_ids

---

## Phase 2: Index Builder & Integration

### Affected Files
- `N5/cognition/n5_memory_client.py` - UPDATE - Add rebuild method, integrate into search()
- `N5/scripts/n5_rebuild_ann_index.py` - CREATE - Standalone rebuild script

### Changes

**2.1 Create `rebuild_ann_index()` Method in Client:**
```python
def rebuild_ann_index(self, ef_construction: int = 200, M: int = 16) -> bool:
    """Rebuild the HNSW index from all vectors in database."""
    if not HAS_HNSWLIB:
        LOG.error("hnswlib not installed")
        return False
    
    cursor = self._get_db().cursor()
    cursor.execute("SELECT block_id, embedding FROM vectors")
    rows = cursor.fetchall()
    
    if not rows:
        LOG.warning("No vectors to index")
        return False
    
    # Detect dimension
    dim = len(np.frombuffer(rows[0][1], dtype=np.float32))
    
    # Build index
    index = hnswlib.Index(space='cosine', dim=dim)
    index.init_index(max_elements=len(rows), ef_construction=ef_construction, M=M)
    
    block_ids = []
    vectors = []
    for block_id, emb_blob in rows:
        block_ids.append(block_id)
        vectors.append(np.frombuffer(emb_blob, dtype=np.float32))
    
    vectors_array = np.array(vectors, dtype=np.float32)
    index.add_items(vectors_array, list(range(len(block_ids))))
    
    # Save index and mapping
    index.save_index(ANN_INDEX_PATH)
    with open(ANN_INDEX_PATH + ".ids", 'w') as f:
        json.dump(block_ids, f)
    
    LOG.info(f"ANN index rebuilt: {len(block_ids)} vectors, dim={dim}")
    
    # Reload into memory
    self._load_ann_index()
    return True
```

**2.2 Create Standalone Script `N5/scripts/n5_rebuild_ann_index.py`:**
```python
#!/usr/bin/env python3
"""Rebuild the HNSW ANN index for brain.db semantic search."""
import argparse
import sys
sys.path.insert(0, "/home/workspace/N5/cognition")
from n5_memory_client import N5MemoryClient

def main():
    parser = argparse.ArgumentParser(description="Rebuild ANN index")
    parser.add_argument("--ef", type=int, default=200, help="ef_construction parameter")
    parser.add_argument("--M", type=int, default=16, help="M parameter (connections per node)")
    args = parser.parse_args()
    
    client = N5MemoryClient()
    success = client.rebuild_ann_index(ef_construction=args.ef, M=args.M)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

**2.3 Integrate ANN into `search()` Method:**

Modify the `search()` method. After getting `query_vec`, add this block BEFORE the brute-force SQL query:

```python
# === ANN INDEX FAST PATH ===
if self.use_vector_index and self.ann_index is not None:
    # Get top candidates from ANN
    ann_k = max(limit * 5, rerank_top_k * 2) if use_reranker else limit * 3
    ann_results = self._search_ann(query_vec, k=ann_k)
    
    if ann_results:
        # Fetch block metadata for ANN results
        block_ids = [r[0] for r in ann_results]
        sim_map = {r[0]: r[1] for r in ann_results}
        
        placeholders = ','.join('?' * len(block_ids))
        cursor = self._get_db().cursor()
        cursor.execute(f"""
            SELECT b.id, b.content, b.block_type, r.path, b.content_date, b.start_line, b.end_line
            FROM blocks b
            JOIN resources r ON b.resource_id = r.id
            WHERE b.id IN ({placeholders})
        """, block_ids)
        
        raw_results = []
        for row in cursor.fetchall():
            block_id, content, block_type, path, content_date, start_line, end_line = row
            
            # Apply metadata filters if specified
            if metadata_filters:
                skip = False
                for field, value in metadata_filters.items():
                    if field == 'path':
                        if isinstance(value, tuple) and value[0] == 'startswith':
                            if not path.startswith(value[1]):
                                skip = True
                        elif path != value:
                            skip = True
                    # Add other filters as needed
                if skip:
                    continue
            
            raw_results.append({
                'block_id': block_id,
                'content': content,
                'block_type': block_type,
                'path': path,
                'content_date': content_date,
                'start_line': int(start_line or 0),
                'end_line': int(end_line or 0),
                'lines': [int(start_line or 0), int(end_line or 0)],
                'similarity': sim_map.get(block_id, 0.0)
            })
        
        # Continue with BM25/reranking as normal using raw_results
        # (existing code handles this)
```

Add an `else` clause to fall through to existing brute-force when ANN not available.

### Unit Tests
- `python3 N5/scripts/n5_rebuild_ann_index.py` creates `brain.hnsw` and `brain.hnsw.ids`
- `search("test query")` with `USE_VECTOR_INDEX=true` returns results
- `search("test query")` with `USE_VECTOR_INDEX=false` uses brute-force (benchmark both)
- Metadata filters work with ANN path

---

## Success Criteria

1. **Index Exists:** `brain.hnsw` and `brain.hnsw.ids` created by rebuild script
2. **Toggle Works:** `USE_VECTOR_INDEX=false` disables ANN path, uses brute-force
3. **Fallback Works:** Missing index file → graceful fallback to brute-force
4. **Performance:** ANN search is ≥10x faster than brute-force for >1000 vectors
5. **Correctness:** Top-10 results overlap ≥70% between ANN and brute-force

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Index stale after re-indexing files | Document: run `n5_rebuild_ann_index.py` after bulk indexing |
| Dimension mismatch if embedding model changes | Rebuild script deletes old index; load fails gracefully |
| hnswlib not installed | `HAS_HNSWLIB` flag; graceful fallback |
| Memory pressure with large index | HNSW is memory-mapped; monitor if >100k vectors |

---

## Level Upper Review

*Skipped for this build - straightforward implementation with clear prior art.*

---

## Handoff

**Ready for Builder.** Start with Phase 1.

```
Plan: N5/builds/ann-vector-index/PLAN.md
Starting Phase: 1
```




