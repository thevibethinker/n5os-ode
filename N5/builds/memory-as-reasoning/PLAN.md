---
created: 2026-01-31
last_edited: 2026-01-31
version: 2.0
type: build_plan
status: ready
provenance: con_mzmorv1rSBgdsdfl
---

# Plan: Memory as Reasoning — Semantic Memory System Upgrade

**Status:** ✅ FINALIZED — Ready for execution

**Objective:** Upgrade N5 semantic memory from "retrieve relevant chunks" to "maintain + refine a working model of V" via:
1. Re-embedding all content to OpenAI `text-embedding-3-large` (3072-dim) in a shadow store
2. A reasoning layer that stores beliefs, detects surprisal, and logs traces

**Core principle:** P35 (Version, Don't Overwrite). Shadow stores first, cut over behind flags.

---

## Locked Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Embedding model** | OpenAI `text-embedding-3-large` (3072-dim) | Better quality for ~$3 total cost |
| **Embedding strategy** | Shadow store (`brain_v2.db`) + feature flag cutover | Rollback-safe |
| **Belief storage** | Separate SQLite (`reasoning.db`) + periodic JSON export | Isolation + auditability |
| **Surprisal threshold** | 0.3 | Accepted |
| **Cold start** | Forward-only | Backfill is separate future build |
| **Low-confidence beliefs** | HITL review queue | Safety over speed |

---

## Current State (Baseline)

- `brain.db`: 5,310 resources / 48,647 blocks / 48,561 vectors (384-dim)
- Backup created: `N5/cognition/backups/brain_pre-reasoning_20260131_141310.db`
- Manifest: `N5/cognition/backups/manifest.json`

---

## Checklist

### Phase 1: Safety & Baseline ✅ PARTIALLY COMPLETE
- [x] Create versioned backup of brain.db
- [x] Create backup manifest with rollback instructions
- [ ] Create `N5/cognition/BASELINE.md` documenting exact pre-upgrade state
- [ ] Create `N5/config/feature_flags.json` with all flags defaulting to safe values
- [ ] Test: restore from backup successfully (dry run)

### Phase 2: Re-Embedding Migration
- [ ] Create `N5/cognition/brain_v2.db` with schema including `embedding_model_id`, `embedding_dim`
- [ ] Implement migration script that:
  - Reads all resources/blocks from brain.db
  - Re-embeds content via OpenAI `text-embedding-3-large`
  - Writes to brain_v2.db with model metadata
  - Includes checkpoint/resume capability (for interruption safety)
- [ ] Add DB selector in `n5_memory_client.py` to switch between legacy/v2
- [ ] Run migration (est. ~$3, ~30-60 min)
- [ ] Test: compare sample searches; confirm consistent 3072-dim

### Phase 3: Beliefs + Surprisal Logging
- [ ] Create `N5/cognition/reasoning.db` with schema:
  - `beliefs` table (id, content, confidence, domain, evidence_json, created_at, updated_at)
  - `reasoning_traces` table (id, timestamp, query, surprisal_score, reasoning_result, belief_updates_json)
  - `review_queue` table (id, belief_id, status, created_at, reviewed_at, reviewer_notes)
- [ ] Implement `N5BeliefStore` class (SQLite-backed CRUD + export)
- [ ] Implement `SurprisalDetector` with threshold 0.3
- [ ] Wire surprisal detection into search (behind feature flag)
- [ ] Test: low-similarity queries generate traces; beliefs can be stored/retrieved

### Phase 4: Reasoning Loop + HITL Guardrails
- [ ] Implement `N5Reasoner` class using `/zo/ask` for abductive reasoning
- [ ] Connect surprisal events → reasoner → belief updates
- [ ] Implement HITL review queue for beliefs with confidence < 0.6:
  - New low-confidence beliefs go to `review_queue` as "pending"
  - Daily digest or on-demand review via CLI
  - Approved beliefs get confidence boost; rejected get deleted
- [ ] Add periodic JSON snapshot export (`beliefs_snapshot.json`)
- [ ] Test: end-to-end reasoning trace with belief update

---

## Phase 1: Safety & Baseline

### Affected Files
| Path | Action | Description |
|------|--------|-------------|
| `N5/cognition/backups/brain_pre-reasoning_*.db` | CREATED ✅ | Baseline backup |
| `N5/cognition/backups/manifest.json` | CREATED ✅ | Rollback metadata |
| `N5/cognition/BASELINE.md` | CREATE | Pre-upgrade system state doc |
| `N5/config/feature_flags.json` | CREATE | Feature flags |

### Feature Flags Schema
```json
{
  "N5_EMBEDDING_STORE": "legacy",
  "N5_REASONING_ENABLED": false,
  "N5_SURPRISAL_THRESHOLD": 0.3,
  "N5_REASONING_MODEL": "anthropic:claude-sonnet-4-20250514",
  "N5_BELIEF_HITL_THRESHOLD": 0.6
}
```

---

## Phase 2: Re-Embedding Migration

### Affected Files
| Path | Action | Description |
|------|--------|-------------|
| `N5/cognition/brain_v2.db` | CREATE | New embedding store (3072-dim) |
| `N5/cognition/n5_memory_client.py` | UPDATE | Add DB selector logic |
| `N5/scripts/migrate_embeddings.py` | CREATE | Migration script with checkpoints |

### Migration Script Requirements
- **Checkpoint/resume:** save progress every 500 blocks; can restart from last checkpoint
- **Rate limiting:** respect OpenAI rate limits (~3000 RPM for embeddings)
- **Validation:** verify dimension consistency after each batch
- **Logging:** detailed progress output for monitoring

### Schema for brain_v2.db
```sql
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);
-- Store: embedding_model = "text-embedding-3-large", embedding_dim = 3072

CREATE TABLE resources (
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    hash TEXT,
    last_indexed_at DATETIME,
    content_date DATETIME
);

CREATE TABLE blocks (
    id TEXT PRIMARY KEY,
    resource_id TEXT NOT NULL,
    block_type TEXT,
    content TEXT NOT NULL,
    start_line INTEGER,
    end_line INTEGER,
    token_count INTEGER,
    content_date DATETIME,
    FOREIGN KEY(resource_id) REFERENCES resources(id) ON DELETE CASCADE
);

CREATE TABLE vectors (
    block_id TEXT PRIMARY KEY,
    embedding BLOB NOT NULL,
    embedding_dim INTEGER DEFAULT 3072,
    FOREIGN KEY(block_id) REFERENCES blocks(id) ON DELETE CASCADE
);
```

---

## Phase 3: Beliefs + Surprisal Logging

### Affected Files
| Path | Action | Description |
|------|--------|-------------|
| `N5/cognition/reasoning.db` | CREATE | Beliefs + traces store |
| `N5/cognition/belief_store.py` | CREATE | BeliefStore class |
| `N5/cognition/surprisal_detector.py` | CREATE | Surprisal detection logic |
| `N5/cognition/n5_memory_client.py` | UPDATE | Wire in surprisal detection |

### Schema for reasoning.db
```sql
CREATE TABLE beliefs (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    confidence REAL DEFAULT 0.5,
    domain TEXT,  -- identity | preference | behavior | goal
    source TEXT,  -- inferred | explicit | resonance
    evidence_json TEXT,  -- JSON array of block_ids
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    validation_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active'  -- active | archived | rejected
);

CREATE TABLE reasoning_traces (
    id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    query TEXT,
    top_similarity REAL,
    surprisal_triggered BOOLEAN,
    reasoning_result TEXT,  -- JSON
    belief_updates_json TEXT
);

CREATE TABLE review_queue (
    id TEXT PRIMARY KEY,
    belief_id TEXT NOT NULL,
    reason TEXT,  -- low_confidence | contradiction | manual
    status TEXT DEFAULT 'pending',  -- pending | approved | rejected
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME,
    reviewer_notes TEXT,
    FOREIGN KEY(belief_id) REFERENCES beliefs(id)
);

CREATE INDEX idx_beliefs_domain ON beliefs(domain);
CREATE INDEX idx_beliefs_confidence ON beliefs(confidence);
CREATE INDEX idx_review_status ON review_queue(status);
```

---

## Phase 4: Reasoning Loop + HITL Guardrails

### Affected Files
| Path | Action | Description |
|------|--------|-------------|
| `N5/cognition/reasoner.py` | CREATE | Abductive reasoning engine |
| `N5/cognition/belief_store.py` | UPDATE | Add HITL queue methods |
| `N5/scripts/review_beliefs.py` | CREATE | CLI for HITL review |
| `N5/cognition/beliefs_snapshot.json` | CREATE | Periodic export |

### HITL Review Queue Flow
```
New belief (confidence < 0.6)
    ↓
Insert into review_queue (status=pending)
    ↓
Daily digest or CLI review
    ↓
V approves → confidence += 0.2, status=approved
V rejects → belief.status=rejected, removed from active
```

### Reasoner Prompt Template
```
Given a surprisal event (query produced unexpected results):

Query: {query}
Top results: {top_3_results}
Current relevant beliefs: {domain_beliefs}

Using abductive reasoning:
1. What does this mismatch suggest about V's current focus?
2. Should existing beliefs be updated (confidence +/-)?
3. Should new beliefs be proposed?

Return JSON:
{
  "inference": "...",
  "belief_updates": [{"belief_id": "...", "confidence_delta": 0.1}],
  "new_beliefs": [{"content": "...", "confidence": 0.5, "domain": "..."}]
}
```

---

## Rollback Procedures

### Full Rollback (nuclear option)
```bash
# 1. Disable reasoning
echo '{"N5_EMBEDDING_STORE": "legacy", "N5_REASONING_ENABLED": false}' > N5/config/feature_flags.json

# 2. Restore legacy brain.db if needed
cp N5/cognition/backups/brain_pre-reasoning_20260131_141310.db N5/cognition/brain.db

# 3. Optionally remove new artifacts
rm -f N5/cognition/brain_v2.db N5/cognition/reasoning.db
```

### Partial Rollback (keep v2 embeddings, disable reasoning)
```bash
echo '{"N5_EMBEDDING_STORE": "v2", "N5_REASONING_ENABLED": false}' > N5/config/feature_flags.json
```

### Embedding-only Rollback (keep reasoning, use legacy embeddings)
```bash
echo '{"N5_EMBEDDING_STORE": "legacy", "N5_REASONING_ENABLED": true}' > N5/config/feature_flags.json
```

---

## MECE Worker Assignment

| Wave | Worker | Scope | Files Owned |
|------|--------|-------|-------------|
| 1 | W1.1 | Safety, baseline, feature flags | `BASELINE.md`, `feature_flags.json`, rollback tests |
| 1 | W1.2 | Re-embedding migration pipeline | `brain_v2.db`, `migrate_embeddings.py`, DB selector |
| 2 | W2.1 | Beliefs store + surprisal detection | `reasoning.db`, `belief_store.py`, `surprisal_detector.py` |
| 2 | W2.2 | Reasoner + HITL + integration | `reasoner.py`, `review_beliefs.py`, search integration |

---

## Success Criteria

1. ✅ Legacy system (`brain.db`) unchanged and functional
2. ✅ v2 embedding store complete with 48K+ vectors at 3072-dim
3. ✅ Can switch between legacy/v2 via feature flag in <1 min
4. ✅ Beliefs stored with evidence pointers and confidence scores
5. ✅ Surprisal events logged at threshold 0.3
6. ✅ Low-confidence beliefs (<0.6) route to HITL queue
7. ✅ Full rollback tested and documented

---

## Estimated Effort

| Phase | Time | Cost |
|-------|------|------|
| Phase 1 | 30 min | $0 |
| Phase 2 | 60-90 min (migration runtime) | ~$3 (OpenAI embeddings) |
| Phase 3 | 45 min | $0 |
| Phase 4 | 60 min | $0 |
| **Total** | ~3-4 hours | ~$3 |

---

## Level Upper Review

### Failure Modes to Watch
1. **Migration interruption:** checkpoint system handles this
2. **OpenAI rate limits:** script includes backoff
3. **Dimension mismatch (again):** v2 schema enforces single model via metadata table
4. **Belief pollution:** HITL queue + confidence threshold

### Approved for execution
Plan finalized by V on 2026-01-31.
