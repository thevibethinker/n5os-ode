#!/usr/bin/env python3
"""
Semantic Position Linker v2 (Hybrid)

Synthesizes Worker E + c3Qz-W2 approaches:
- Embedding-based candidate discovery (fast, no API cost)
- Preserves existing hand-crafted edges
- Two-pass algorithm: strong edges (0.80), then bridge edges (0.60)
- Fallback: every orphan gets at least 1 connection (top-1)
- Idempotent: won't add duplicate edges

Usage:
  python3 position_linker.py                    # Dry-run (default)
  python3 position_linker.py --apply            # Write to DB
  python3 position_linker.py --write-embeddings # Also persist embeddings
"""

import argparse
import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

# === CONFIGURATION ===
DB_PATH = Path("/home/workspace/N5/data/positions.db")
BACKUP_DIR = Path("/home/workspace/N5/data/backups")
MODEL_NAME = "all-MiniLM-L6-v2"

# Two-pass thresholds
STRONG_THRESHOLD = 0.80
BRIDGE_THRESHOLD = 0.60
FALLBACK_MIN = 0.25  # Absolute floor for top-1 fallback

MAX_STRONG_CONNECTIONS = 3
MAX_BRIDGE_CONNECTIONS = 2  # Additional bridges after strong pass


def now_et_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")


def backup_database(reason: str = "position_linker_apply") -> Path:
    """Create timestamped backup before any writes."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_reason = reason.replace(" ", "_")[:30]
    backup_path = BACKUP_DIR / f"positions_{ts}_{safe_reason}.db"
    shutil.copy2(DB_PATH, backup_path)
    print(f"✓ Backup created: {backup_path}")
    
    # Rotate: keep only last 10 backups
    backups = sorted(BACKUP_DIR.glob("positions_*.db"), key=lambda p: p.stat().st_mtime)
    while len(backups) > 10:
        oldest = backups.pop(0)
        oldest.unlink()
        print(f"  (rotated out: {oldest.name})")
    
    return backup_path


def load_positions(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Load all positions with their current connections and embeddings."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, domain, title, insight, connections, embedding
        FROM positions
    """)
    rows = cursor.fetchall()
    
    positions = []
    for row in rows:
        pid, domain, title, insight, connections_raw, embedding_blob = row
        
        # Parse existing connections
        existing_connections = []
        if connections_raw and connections_raw.strip() and connections_raw.strip() != "[]":
            try:
                existing_connections = json.loads(connections_raw)
            except json.JSONDecodeError:
                print(f"  ⚠ Invalid JSON in connections for {pid}, treating as empty")
        
        # Parse embedding if present
        embedding = None
        if embedding_blob and len(embedding_blob) > 0:
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
        
        positions.append({
            "id": pid,
            "domain": domain,
            "title": title or "",
            "insight": insight or "",
            "existing_connections": existing_connections,
            "embedding": embedding,
        })
    
    return positions


def get_orphans(positions: list[dict]) -> list[dict]:
    """Return positions with no existing connections."""
    return [p for p in positions if not p["existing_connections"]]


def compute_embeddings(positions: list[dict], model) -> np.ndarray:
    """Compute or retrieve embeddings for all positions."""
    texts = []
    needs_compute = []
    
    for i, p in enumerate(positions):
        if p["embedding"] is not None:
            texts.append(None)  # Placeholder
        else:
            text = f"{p['title']} {p['insight']}"
            texts.append(text)
            needs_compute.append(i)
    
    # Compute missing embeddings
    if needs_compute:
        texts_to_embed = [texts[i] for i in needs_compute]
        new_embeddings = model.encode(texts_to_embed, show_progress_bar=True, batch_size=32)
        for idx, emb in zip(needs_compute, new_embeddings):
            positions[idx]["embedding"] = emb
        print(f"Embeddings computed this run: {len(needs_compute)}")
    else:
        print("All embeddings loaded from DB (none computed)")
    
    # Stack all embeddings
    all_embeddings = np.array([p["embedding"] for p in positions])
    return all_embeddings


def compute_similarity_matrix(embeddings: np.ndarray) -> np.ndarray:
    """Compute cosine similarity matrix (embeddings assumed normalized)."""
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normed = embeddings / (norms + 1e-9)
    return normed @ normed.T


def get_relationship_type(score: float) -> str:
    """Map similarity score to relationship type."""
    if score >= 0.90:
        return "strongly_related"
    elif score >= 0.80:
        return "related"
    elif score >= 0.70:
        return "tangentially_related"
    else:
        return "weakly_related"


def edge_exists(existing: list[dict], target_id: str) -> bool:
    """Check if an edge to target_id already exists."""
    return any(c.get("target_id") == target_id for c in existing)


def generate_connections_two_pass(
    positions: list[dict],
    orphans: list[dict],
    similarity_matrix: np.ndarray,
    id_to_idx: dict[str, int],
) -> dict[str, list[dict]]:
    """
    Two-pass algorithm:
    1. Strong pass: Add up to MAX_STRONG_CONNECTIONS edges at STRONG_THRESHOLD
    2. Bridge pass: For remaining orphans, add edges at BRIDGE_THRESHOLD
    3. Fallback: Any still-orphaned position gets its top-1 neighbor (if >= FALLBACK_MIN)
    """
    proposed = {}
    orphan_ids = {p["id"] for p in orphans}
    
    # Pass 1: Strong connections
    for orphan in orphans:
        orphan_idx = id_to_idx[orphan["id"]]
        similarities = similarity_matrix[orphan_idx]
        sorted_indices = np.argsort(similarities)[::-1]
        
        connections = []
        for idx in sorted_indices:
            target = positions[idx]
            if target["id"] == orphan["id"]:
                continue
            score = similarities[idx]
            if score < STRONG_THRESHOLD:
                break
            if len(connections) >= MAX_STRONG_CONNECTIONS:
                break
            if edge_exists(connections, target["id"]):
                continue
            
            connections.append({
                "target_id": target["id"],
                "relationship": get_relationship_type(score),
                "score": round(float(score), 3),
            })
        
        if connections:
            proposed[orphan["id"]] = connections
    
    # Pass 2: Bridge connections for remaining orphans
    still_orphaned = [p for p in orphans if p["id"] not in proposed]
    
    for orphan in still_orphaned:
        orphan_idx = id_to_idx[orphan["id"]]
        similarities = similarity_matrix[orphan_idx]
        sorted_indices = np.argsort(similarities)[::-1]
        
        connections = []
        for idx in sorted_indices:
            target = positions[idx]
            if target["id"] == orphan["id"]:
                continue
            score = similarities[idx]
            if score < BRIDGE_THRESHOLD:
                break
            if len(connections) >= MAX_BRIDGE_CONNECTIONS:
                break
            if edge_exists(connections, target["id"]):
                continue
            
            connections.append({
                "target_id": target["id"],
                "relationship": get_relationship_type(score),
                "score": round(float(score), 3),
            })
        
        if connections:
            proposed[orphan["id"]] = connections
    
    # Pass 3: Fallback for any still-orphaned (top-1 if above floor)
    final_orphaned = [p for p in orphans if p["id"] not in proposed]
    
    for orphan in final_orphaned:
        orphan_idx = id_to_idx[orphan["id"]]
        similarities = similarity_matrix[orphan_idx]
        sorted_indices = np.argsort(similarities)[::-1]
        
        for idx in sorted_indices:
            target = positions[idx]
            if target["id"] == orphan["id"]:
                continue
            score = similarities[idx]
            if score < FALLBACK_MIN:
                break  # Even top-1 is below floor, leave orphaned
            
            proposed[orphan["id"]] = [{
                "target_id": target["id"],
                "relationship": get_relationship_type(score),
                "score": round(float(score), 3),
            }]
            break
    
    return proposed


def apply_connections(conn: sqlite3.Connection, proposed: dict[str, list[dict]], positions: list[dict]):
    """
    Write proposed connections to DB.
    PRESERVES existing connections (merges, doesn't overwrite).
    IDEMPOTENT: won't add duplicate edges.
    """
    cursor = conn.cursor()
    id_to_pos = {p["id"]: p for p in positions}
    
    for position_id, new_connections in proposed.items():
        pos = id_to_pos[position_id]
        existing = pos["existing_connections"]
        
        # Merge: add only new edges
        merged = list(existing)  # Copy existing
        for nc in new_connections:
            if not edge_exists(merged, nc["target_id"]):
                # Remove score from final storage
                merged.append({
                    "target_id": nc["target_id"],
                    "relationship": nc["relationship"],
                })
        
        cursor.execute(
            "UPDATE positions SET connections = ? WHERE id = ?",
            (json.dumps(merged), position_id)
        )
    
    conn.commit()


def write_embeddings_to_db(conn: sqlite3.Connection, positions: list[dict]):
    """Persist computed embeddings back to DB."""
    cursor = conn.cursor()
    written = 0
    for p in positions:
        if p["embedding"] is not None:
            blob = p["embedding"].astype(np.float32).tobytes()
            cursor.execute(
                "UPDATE positions SET embedding = ? WHERE id = ?",
                (blob, p["id"])
            )
            written += 1
    conn.commit()
    print(f"✓ Wrote {written} embeddings to DB")


def main():
    parser = argparse.ArgumentParser(description="Semantic Position Linker v2 (Hybrid)")
    parser.add_argument("--db", default=str(DB_PATH), help="Path to positions.db")
    parser.add_argument("--apply", action="store_true", help="Actually write to DB (default: dry-run)")
    parser.add_argument("--write-embeddings", action="store_true", help="Also write computed embeddings to DB")
    parser.add_argument("--strong-threshold", type=float, default=STRONG_THRESHOLD, help=f"Pass 1 threshold (default: {STRONG_THRESHOLD})")
    parser.add_argument("--bridge-threshold", type=float, default=BRIDGE_THRESHOLD, help=f"Pass 2 threshold (default: {BRIDGE_THRESHOLD})")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Semantic Position Linker v2 (Hybrid)")
    print("=" * 60)
    print(f"DB: {args.db}")
    print(f"Model: {MODEL_NAME}")
    print(f"Strong threshold (pass 1): {args.strong_threshold}")
    print(f"Bridge threshold (pass 2): {args.bridge_threshold}")
    print(f"Fallback floor: {FALLBACK_MIN}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"Write embeddings: {args.write_embeddings}")
    print(f"Started at {now_et_str()}")
    print()
    
    # Load model
    print("Loading embedding model...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_NAME)
    
    # Connect to DB
    conn = sqlite3.connect(args.db)
    
    # Load data
    print("Loading positions...")
    positions = load_positions(conn)
    print(f"Total positions: {len(positions)}")
    
    # Count existing edges
    total_existing_edges = sum(len(p["existing_connections"]) for p in positions)
    positions_with_edges = sum(1 for p in positions if p["existing_connections"])
    print(f"Positions with existing edges: {positions_with_edges}")
    print(f"Total existing edges: {total_existing_edges}")
    
    # Find orphans
    orphans = get_orphans(positions)
    print(f"Orphans detected: {len(orphans)}")
    print()
    
    # Build index
    id_to_idx = {p["id"]: i for i, p in enumerate(positions)}
    
    # Compute embeddings
    print("Computing / loading embeddings...")
    embeddings = compute_embeddings(positions, model)
    print()
    
    # Compute similarity
    print("Computing similarity matrix...")
    similarity_matrix = compute_similarity_matrix(embeddings)
    print()
    
    # Generate connections
    print("Generating proposed connections (two-pass + fallback)...")
    proposed = generate_connections_two_pass(positions, orphans, similarity_matrix, id_to_idx)
    print()
    
    # Report
    print("=" * 60)
    print("PROPOSED CONNECTIONS")
    print("=" * 60)
    
    total_new_connections = 0
    by_relationship = {}
    
    for position_id, connections in sorted(proposed.items()):
        pos = next(p for p in positions if p["id"] == position_id)
        title_preview = pos["title"][:60] + "..." if len(pos["title"]) > 60 else pos["title"]
        print(f"\n[{pos['domain']}] {title_preview}")
        for c in connections:
            target = next(p for p in positions if p["id"] == c["target_id"])
            target_preview = target["title"][:50] + "..." if len(target["title"]) > 50 else target["title"]
            print(f"  → {c['relationship']} ({c['score']:.3f}): {target_preview}")
            total_new_connections += 1
            by_relationship[c["relationship"]] = by_relationship.get(c["relationship"], 0) + 1
    
    remaining_orphans = len(orphans) - len(proposed)
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Positions to update: {len(proposed)}")
    print(f"New connections: {total_new_connections}")
    print(f"Remaining orphans (after this run, if applied): {remaining_orphans}")
    print()
    print("Connections by type:")
    for rel, count in sorted(by_relationship.items(), key=lambda x: -x[1]):
        print(f"  {rel}: {count}")
    
    # Apply if requested
    if args.apply:
        print()
        backup_database("two_pass_apply")
        apply_connections(conn, proposed, positions)
        print("✓ Connections written to database")
        
        if args.write_embeddings:
            write_embeddings_to_db(conn, positions)
    else:
        print()
        print("This was a DRY-RUN. To apply changes, re-run with --apply.")
        if not args.write_embeddings:
            print("To also persist embeddings, add --write-embeddings.")
    
    conn.close()
    print()
    print(f"Completed at {now_et_str()}")


if __name__ == "__main__":
    main()
