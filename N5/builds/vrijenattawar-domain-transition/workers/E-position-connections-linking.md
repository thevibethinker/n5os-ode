---
created: 2026-01-14
last_edited: 2026-01-15
version: 2
provenance: con_nxvKhHpwzg225fn8
---
# Worker E: Semantic Position Linking

**Project:** vrijenattawar-domain-transition  
**Component:** Graph Connectivity / Mind Map  
**Status:** Ready for Execution  
**Parent Conversation:** con_nxvKhHpwzg225fn8

---

## Context

The Mind Map at [vrijenattawar.com/mind](https://vrijenattawar.com/mind) visualizes V's intellectual positions as an interactive force-directed graph. However, an audit revealed that **79.8% of positions (99/124) are orphans** — they have no connections to other nodes, making the graph sparse and less explorable.

### Audit Findings (from Parent Conversation)

| Domain | Total | Connected | Orphans | Connectivity |
|--------|-------|-----------|---------|--------------|
| hiring-market | 42 | 11 | 31 | 26.2% |
| worldview | 24 | 3 | 21 | 12.5% |
| careerspan | 22 | 0 | 22 | **0%** |
| ai-automation | 20 | 0 | 20 | **0%** |
| epistemology | 7 | 7 | 0 | 100% |
| founder | 5 | 0 | 5 | **0%** |
| personal-foundations | 3 | 0 | 3 | **0%** |
| education | 1 | 1 | 0 | 100% |

The `careerspan`, `ai-automation`, `founder`, and `personal-foundations` domains are **entirely disconnected**.

---

## Objective

Use semantic similarity to auto-generate meaningful connections between related positions, transforming the sparse graph into a rich, explorable intellectual landscape.

---

## Technical Specification

### Source Data
- **Database:** `/home/workspace/N5/data/positions.db`
- **Table:** `positions`
- **Key Fields:**
  - `id` (TEXT) — slug identifier
  - `title` (TEXT) — position title
  - `insight` (TEXT) — detailed explanation
  - `connections` (TEXT) — JSON array of `{target_id, relationship}`
  - `domain` (TEXT) — category
  - `embedding` (BLOB) — pre-computed embedding (may exist)

### Algorithm

1. **Generate Embeddings**: Use `sentence-transformers` (`all-MiniLM-L6-v2`) to create 384-dimensional embeddings for each position using `title + " " + insight` as input text.

2. **Identify Orphans**: Query positions where `connections IS NULL OR connections = '' OR connections = '[]'`.

3. **Calculate Similarity**: For each orphan, compute cosine similarity against ALL other positions.

4. **Generate Connections**: For each orphan, select top N neighbors where:
   - Similarity score > 0.80 (threshold)
   - Target is not self
   - Maximum 5 connections per orphan
   - Relationship type inferred from similarity score:
     - 0.90+ → `"strongly_related"`
     - 0.85-0.90 → `"related_to"`
     - 0.80-0.85 → `"tangentially_related"`

5. **Update Database**: Write connections as JSON array to `connections` field.

### Safety Protocol
- **Dry-run first**: Generate and display proposed connections before any DB writes
- **Backup**: Create timestamped backup of positions.db before modification
- **Validation**: Verify all target_ids exist in database before linking

---

## Execution Steps

### Step 1: Create the Linker Script

Create `/home/workspace/N5/scripts/position_linker.py`:

```python
#!/usr/bin/env python3
"""
Semantic Position Linker
Generates connections between orphan positions using sentence embeddings.
"""

import argparse
import json
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

DB_PATH = Path("/home/workspace/N5/data/positions.db")
BACKUP_DIR = Path("/home/workspace/N5/data/backups")
SIMILARITY_THRESHOLD = 0.80
MAX_CONNECTIONS = 5

def get_relationship_type(score: float) -> str:
    if score >= 0.90:
        return "strongly_related"
    elif score >= 0.85:
        return "related_to"
    else:
        return "tangentially_related"

def backup_database():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"positions_backup_{timestamp}.db"
    shutil.copy(DB_PATH, backup_path)
    print(f"✓ Backup created: {backup_path}")
    return backup_path

def load_positions(conn):
    cursor = conn.execute("""
        SELECT id, title, insight, connections, domain 
        FROM positions
    """)
    positions = []
    for row in cursor:
        connections = row[3]
        if connections:
            try:
                connections = json.loads(connections)
            except json.JSONDecodeError:
                connections = []
        else:
            connections = []
        positions.append({
            "id": row[0],
            "title": row[1],
            "insight": row[2] or "",
            "connections": connections,
            "domain": row[4]
        })
    return positions

def identify_orphans(positions):
    return [p for p in positions if not p["connections"]]

def generate_embeddings(positions, model):
    texts = [f"{p['title']} {p['insight']}" for p in positions]
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    return embeddings

def compute_similarities(embeddings):
    # Cosine similarity for normalized vectors is just dot product
    return np.dot(embeddings, embeddings.T)

def generate_connections(positions, orphans, similarity_matrix, id_to_idx):
    proposed = {}
    
    for orphan in orphans:
        orphan_idx = id_to_idx[orphan["id"]]
        similarities = similarity_matrix[orphan_idx]
        
        # Get indices sorted by similarity (descending), excluding self
        sorted_indices = np.argsort(similarities)[::-1]
        
        connections = []
        for idx in sorted_indices:
            if idx == orphan_idx:
                continue
            score = similarities[idx]
            if score < SIMILARITY_THRESHOLD:
                break
            if len(connections) >= MAX_CONNECTIONS:
                break
            
            target = positions[idx]
            connections.append({
                "target_id": target["id"],
                "relationship": get_relationship_type(score),
                "score": round(float(score), 3)
            })
        
        if connections:
            proposed[orphan["id"]] = connections
    
    return proposed

def apply_connections(conn, proposed):
    cursor = conn.cursor()
    for position_id, connections in proposed.items():
        # Remove score from final JSON (it was just for reporting)
        clean_connections = [
            {"target_id": c["target_id"], "relationship": c["relationship"]}
            for c in connections
        ]
        cursor.execute(
            "UPDATE positions SET connections = ? WHERE id = ?",
            (json.dumps(clean_connections), position_id)
        )
    conn.commit()
    print(f"✓ Applied connections to {len(proposed)} positions")

def main():
    parser = argparse.ArgumentParser(description="Semantic Position Linker")
    parser.add_argument("--apply", action="store_true", help="Apply changes to database")
    parser.add_argument("--threshold", type=float, default=SIMILARITY_THRESHOLD, 
                        help=f"Similarity threshold (default: {SIMILARITY_THRESHOLD})")
    parser.add_argument("--max-connections", type=int, default=MAX_CONNECTIONS,
                        help=f"Max connections per orphan (default: {MAX_CONNECTIONS})")
    args = parser.parse_args()
    
    global SIMILARITY_THRESHOLD, MAX_CONNECTIONS
    SIMILARITY_THRESHOLD = args.threshold
    MAX_CONNECTIONS = args.max_connections
    
    print("=" * 60)
    print("SEMANTIC POSITION LINKER")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print(f"Threshold: {SIMILARITY_THRESHOLD}")
    print(f"Max connections: {MAX_CONNECTIONS}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    print()
    
    # Load model
    print("Loading sentence-transformers model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    
    # Load positions
    print("Loading positions...")
    positions = load_positions(conn)
    print(f"  Total positions: {len(positions)}")
    
    # Identify orphans
    orphans = identify_orphans(positions)
    print(f"  Orphan positions: {len(orphans)}")
    
    if not orphans:
        print("✓ No orphans found. Graph is fully connected!")
        return
    
    # Build index mapping
    id_to_idx = {p["id"]: i for i, p in enumerate(positions)}
    
    # Generate embeddings
    print("Generating embeddings...")
    embeddings = generate_embeddings(positions, model)
    
    # Compute similarity matrix
    print("Computing similarity matrix...")
    similarity_matrix = compute_similarities(embeddings)
    
    # Generate proposed connections
    print("Generating proposed connections...")
    proposed = generate_connections(positions, orphans, similarity_matrix, id_to_idx)
    
    # Report
    print()
    print("=" * 60)
    print("PROPOSED CONNECTIONS")
    print("=" * 60)
    
    total_new_connections = 0
    for position_id, connections in sorted(proposed.items()):
        pos = next(p for p in positions if p["id"] == position_id)
        print(f"\n[{pos['domain']}] {pos['title'][:60]}...")
        for c in connections:
            target = next(p for p in positions if p["id"] == c["target_id"])
            print(f"  → {c['relationship']} ({c['score']:.3f}): {target['title'][:50]}...")
            total_new_connections += 1
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Positions to update: {len(proposed)}")
    print(f"New connections: {total_new_connections}")
    print(f"Remaining orphans: {len(orphans) - len(proposed)}")
    
    # Apply if requested
    if args.apply:
        print()
        backup_database()
        apply_connections(conn, proposed)
        print("✓ Database updated successfully")
    else:
        print()
        print("This was a DRY-RUN. To apply changes, run with --apply flag.")
    
    conn.close()
    print()
    print(f"Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")

if __name__ == "__main__":
    main()
```

### Step 2: Execute Dry-Run

```bash
python3 /home/workspace/N5/scripts/position_linker.py
```

Review the proposed connections. Verify they make semantic sense.

### Step 3: Apply Changes

```bash
python3 /home/workspace/N5/scripts/position_linker.py --apply
```

### Step 4: Verify Results

```bash
sqlite3 /home/workspace/N5/data/positions.db "SELECT COUNT(*) FROM positions WHERE connections IS NOT NULL AND connections != '' AND connections != '[]'"
```

Expected: Should be close to 124 (all positions connected).

### Step 5: Test Mind Map

Visit [vrijenattawar.com/mind](https://vrijenattawar.com/mind) — the graph should now show connection lines between related positions.

---

## Deliverables

1. ✅ `/home/workspace/N5/scripts/position_linker.py` — the linker script
2. ✅ `/home/workspace/N5/data/backups/positions_backup_*.db` — timestamped backup
3. ✅ Updated `positions.db` with populated connections
4. ✅ Summary report (stdout from script)
5. ✅ Visually richer Mind Map on the live site

---

## Success Criteria

- [ ] Orphan count reduced from 99 to <10
- [ ] All domains have at least some connectivity
- [ ] Mind Map shows visible connection lines
- [ ] No broken connections (all target_ids valid)

---

## Notes

- The similarity threshold (0.80) is intentionally conservative. If results are too sparse, lower to 0.75.
- The `epistemology` domain is already 100% connected — use it as a reference for what "good" connections look like.
- Connection lines won't appear in the Mind Map unless the `MindMap.tsx` component is updated to render edges. Check if `links` data is being passed to the graph component.
