#!/usr/bin/env python3
"""
Compute semantic 2D layout for positions using UMAP on embeddings.
This makes proximity = conceptual similarity.
"""

import sqlite3
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import umap

DB_PATH = "/home/workspace/N5/data/positions.db"
SNAPSHOT_PATH = "/home/workspace/Sites/vrijenattawar-staging/data/positions-snapshot.json"


def main():
    print("Loading positions...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, domain, title, insight, stability, confidence, formed_date, connections
        FROM positions
    """)
    rows = cur.fetchall()
    
    positions = []
    texts = []
    
    for row in rows:
        pos_id, domain, title, insight, stability, confidence, formed_date, connections_json = row
        positions.append({
            "id": pos_id,
            "domain": domain or "uncategorized",
            "title": title or "",
            "insight": insight or "",
            "stability": stability or "emerging",
            "confidence": confidence or 5,
            "formed_date": formed_date or "",
            "connections_json": connections_json
        })
        # Combine title and insight for embedding
        texts.append(f"{title}. {insight}" if insight else title)
    
    print(f"  Found {len(positions)} positions")
    
    # Generate embeddings
    print("Computing embeddings...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Apply UMAP to reduce to 2D
    print("Running UMAP dimensionality reduction...")
    reducer = umap.UMAP(
        n_neighbors=15,
        min_dist=0.8,
        spread=3.0,
        n_components=2,
        metric='cosine',
        random_state=42
    )
    coords_2d = reducer.fit_transform(embeddings)
    
    # Normalize to reasonable range for visualization
    x_min, x_max = coords_2d[:, 0].min(), coords_2d[:, 0].max()
    y_min, y_max = coords_2d[:, 1].min(), coords_2d[:, 1].max()
    
    # Scale to fit canvas (with padding) - LARGER for roomier feel
    WIDTH, HEIGHT = 1400, 1000
    PADDING = 80
    
    for i, pos in enumerate(positions):
        x = ((coords_2d[i, 0] - x_min) / (x_max - x_min)) * WIDTH + PADDING
        y = ((coords_2d[i, 1] - y_min) / (y_max - y_min)) * HEIGHT + PADDING
        pos["fx"] = float(x)  # Fixed x position
        pos["fy"] = float(y)  # Fixed y position
    
    # Build links from connections
    print("Building link data...")
    links = []
    node_ids = {p["id"] for p in positions}
    
    for pos in positions:
        if pos["connections_json"]:
            try:
                conns = json.loads(pos["connections_json"])
                for conn in conns:
                    if isinstance(conn, dict):
                        target_id = conn.get("target_id")
                        if target_id and target_id in node_ids:
                            links.append({
                                "source": pos["id"],
                                "target": target_id,
                                "relationship": conn.get("relationship", "related"),
                                "thematic_description": conn.get("thematic_description", "")
                            })
                    elif isinstance(conn, str) and conn in node_ids:
                        links.append({
                            "source": pos["id"],
                            "target": conn,
                            "relationship": "related"
                        })
            except json.JSONDecodeError:
                pass
    
    # Build nodes for snapshot (without connections_json)
    nodes = []
    for pos in positions:
        nodes.append({
            "id": pos["id"],
            "domain": pos["domain"],
            "title": pos["title"],
            "insight": pos["insight"],
            "stability": pos["stability"],
            "confidence": pos["confidence"],
            "formed_date": pos["formed_date"],
            "fx": pos["fx"],
            "fy": pos["fy"]
        })
    
    # Save snapshot
    snapshot = {"nodes": nodes, "links": links}
    with open(SNAPSHOT_PATH, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"\n✅ Generated semantic layout snapshot:")
    print(f"   {len(nodes)} nodes with fixed positions")
    print(f"   {len(links)} links")
    print(f"   Saved to: {SNAPSHOT_PATH}")
    
    # Show domain clustering quality
    print("\nDomain clustering (positions grouped by semantic similarity):")
    from collections import defaultdict
    domain_positions = defaultdict(list)
    for pos in positions:
        domain_positions[pos["domain"]].append((pos["fx"], pos["fy"]))
    
    for domain, coords in sorted(domain_positions.items(), key=lambda x: -len(x[1])):
        if len(coords) >= 2:
            xs, ys = zip(*coords)
            cx, cy = np.mean(xs), np.mean(ys)
            spread = np.std(xs) + np.std(ys)
            print(f"  {domain}: center=({cx:.0f}, {cy:.0f}), spread={spread:.0f}, count={len(coords)}")
    
    conn.close()


if __name__ == "__main__":
    main()
