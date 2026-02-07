---
created: 2026-01-30
last_edited: 2026-01-30
version: 1.0
provenance: con_6OX93W9N6VqWoRE4
---

# Semantic Memory Embedding Dimension Mismatch - Technical Debt Report

## Summary

**Issue**: `positions.py find_similar()` failed with `ValueError: shapes (384,) and (3072,) not aligned`

**Root Cause**: Mixed embedding dimensions in `brain.db` vectors table due to switching between different embedding models:
- **384 dimensions**: 15,341 vectors (local model: `all-MiniLM-L6-v2`)
- **3072 dimensions**: 3,113 vectors (OpenAI model: `text-embedding-3-large`)

**Resolution Applied**: Added dimension validation in brute-force search to skip mismatched vectors with warning logging.

---

## Diagnosis

### Database State

```sql
SELECT COUNT(*) FROM vectors;
-- Total: 18,454 vectors

-- By dimension:
-- 384 dims: 15,341 vectors (83.2%)
-- 3072 dims: 3,113 vectors (16.8%)
```

### Affected Systems

1. **N5 Memory Client** (`N5/cognition/n5_memory_client.py`)
   - Line 731: `np.dot(query_vec, stored_vec)` failed when dimensions didn't match
   - Both embedding models coexisted in same database without dimension tracking

2. **Positions System** (`N5/scripts/positions.py`)
   - `find_similar()` function failed with dimension mismatch error
   - All 38 position embeddings were 384-dim (safe from this specific issue)
   - General semantic search across all brain.db vectors was affected

### Provider Configuration

```python
# Default provider: local (384-dim all-MiniLM-L6-v2)
self.provider = os.getenv("N5_EMBEDDING_PROVIDER", "local")
self.local_model_name = "all-MiniLM-L6-v2"  # 384-dim
self.openai_model = "text-embedding-3-large"  # 3072-dim
```

The `OPENAI_API_KEY` exists in environment, but local model is preferred. The 3072-dim vectors are legacy embeddings from previous OpenAI usage.

---

## Fix Applied

### Code Change

**File**: `N5/cognition/n5_memory_client.py` (line ~727-732)

**Before**:
```python
for row in cursor.fetchall():
    block_id, content, block_type, path, content_date, start_line, end_line, emb_blob = row
    stored_vec = np.frombuffer(emb_blob, dtype=np.float32)
    
    # Cosine similarity
    similarity = np.dot(query_vec, stored_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(stored_vec) + 1e-9)
```

**After**:
```python
for row in cursor.fetchall():
    block_id, content, block_type, path, content_date, start_line, end_line, emb_blob = row
    stored_vec = np.frombuffer(emb_blob, dtype=np.float32)
    
    # Skip vectors with mismatched dimensions (different embedding models)
    if len(query_vec) != len(stored_vec):
        LOG.warning(f"Skipping block {block_id}: query dim {len(query_vec)} != stored dim {len(stored_vec)}")
        continue
    
    # Cosine similarity
    similarity = np.dot(query_vec, stored_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(stored_vec) + 1e-9)
```

### Impact

- ✅ **Immediate**: Search operations no longer crash
- ✅ **Behavioral**: Mismatched vectors are silently skipped with warning log
- ⚠️ **Data Loss**: 3,113 vectors (16.8% of brain.db) are now inaccessible during search
- ✅ **Positions Safe**: All 38 position embeddings are 384-dim and fully functional

---

## Testing

### Test Results

```bash
# Test 1: Basic search (previously crashed)
$ python3 N5/scripts/positions.py search "test query"
No similar positions found.

# Test 2: Semantic search with results
$ python3 N5/scripts/positions.py search "career coaching"
Found 1 similar position(s):
[0.61] everyone-has-valuable-things-to-say-about-themselv

# Test 3: Higher recall with lower threshold
$ python3 N5/scripts/positions.py search "AI automation complexity" --threshold 0.4
Found 14 similar position(s):
[0.74] complexity-is-an-illusion
[0.62] mental-model-bottleneck
[...]
```

### Positions Embedding Validation

All 38 positions use 384-dim embeddings:
- No positions use 3072-dim embeddings
- `find_similar()` fully operational
- No data loss for positions system

---

## Technical Debt Notes

### Outstanding Issues

1. **Legacy Data Inaccessible**: 3,113 3072-dim vectors cannot be searched with current 384-dim queries
2. **No Migration Path**: No automated re-embedding strategy for legacy vectors
3. **Mixed Index**: ANN HNSW index (`brain.hnsw`) was built with mixed dimensions, now partially useless

### Recommendations

#### Short Term (Stability)

- ✅ **DONE**: Dimension validation prevents crashes
- ✅ **DONE**: Warning logging tracks skipped vectors
- Consider: Set `USE_VECTOR_INDEX=false` to disable HNSW index until rebuilt

#### Medium Term (Data Integrity)

1. **Add dimension column** to `vectors` table:
   ```sql
   ALTER TABLE vectors ADD COLUMN embedding_dim INTEGER;
   UPDATE vectors SET embedding_dim = length(embedding) / 4;
   ```

2. **Re-embed legacy vectors** to 384-dim:
   ```python
   # Identify and re-index all 3072-dim resources
   for resource in get_resources_with_3072_embeddings():
       reindex_with_local_model(resource)
   ```

3. **Rebuild HNSW index** after consolidation:
   ```bash
   rm N5/cognition/brain.hnsw*
   # Rebuild via n5_memory_client.py build_index()
   ```

#### Long Term (Architecture)

1. **Single embedding model** - Enforce one model per database instance
2. **Migration scripts** - Automated model upgrades without data loss
3. **Dimension tracking** - Schema-level constraint to prevent mixing

---

## Commands Used for Diagnosis

```bash
# Check embedding dimensions
python3 -c "
import sqlite3, numpy as np
conn = sqlite3.connect('/home/workspace/N5/cognition/brain.db')
cur = conn.cursor()
cur.execute('SELECT embedding FROM vectors LIMIT 5')
dims = [len(np.frombuffer(r[0], dtype=np.float32)) for r in cur.fetchall()]
print(f'Dimensions: {dims}')
"

# Count by dimension
python3 -c "
import sqlite3, numpy as np
conn = sqlite3.connect('/home/workspace/N5/cognition/brain.db')
cur = conn.cursor()
cur.execute('SELECT embedding FROM vectors')
dim_counts = {}
for r in cur.fetchall():
    dim = len(np.frombuffer(r[0], dtype=np.float32))
    dim_counts[dim] = dim_counts.get(dim, 0) + 1
for dim, count in sorted(dim_counts.items()):
    print(f'{dim} dims: {count} vectors')
"

# Test positions search
python3 N5/scripts/positions.py search "test query"
python3 N5/scripts/positions.py search "career coaching" --threshold 0.5
```

---

## Verification Checklist

- [x] `positions.py search "test query"` runs without error
- [x] `positions.py search "career coaching"` returns results
- [x] No `ValueError: shapes (...) not aligned` errors
- [x] All 38 positions remain accessible and searchable
- [x] Warning logs track skipped vectors
- [x] Report documented with diagnostic commands

---

**Status**: ✅ **FIXED** - Search operations stable, partial data loss (16.8% of vectors)

**Next Action**: Consider re-embedding 3072-dim legacy vectors to recover full search coverage.
