#!/usr/bin/env python3
from N5.lib.paths import SECRETS_DIR, N5_DATA_DIR
POSITIONS_DB = N5_DATA_DIR / "positions.db"
"""
Vector Space Analysis of V's Worldview

Embeds positions, finds clusters, centroids, and the geometric
relationships that reveal latent dimensions and implicit beliefs.
"""

import json
import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import os

# Load API key
key_path = SECRETS_DIR / "openai.key"
if not os.getenv("OPENAI_API_KEY") and key_path.exists():
    with open(key_path) as f:
        os.environ["OPENAI_API_KEY"] = f.read().strip()

# OpenAI for embeddings
from openai import OpenAI


def get_positions() -> List[Dict]:
    """Load all positions from the database."""
    db_path = POSITIONS_DB
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, domain, insight, confidence, 
               reasoning, stability
        FROM positions 
        WHERE confidence >= 3
        ORDER BY confidence DESC
    """)
    
    positions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return positions


def get_embedding(client: OpenAI, text: str) -> np.ndarray:
    """Get embedding vector for text."""
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return np.array(response.data[0].embedding)


def embed_positions(positions: List[Dict]) -> Tuple[np.ndarray, List[str]]:
    """Embed all positions, return matrix and labels."""
    client = OpenAI()
    
    embeddings = []
    labels = []
    
    for p in positions:
        # Combine title + insight for richer embedding
        text = f"{p['title']}: {p['insight']}"
        emb = get_embedding(client, text)
        embeddings.append(emb)
        labels.append(p['id'])
        print(f"  Embedded: {p['title'][:50]}...")
    
    return np.array(embeddings), labels


def find_centroid(embeddings: np.ndarray) -> np.ndarray:
    """Find the centroid of all position embeddings."""
    return np.mean(embeddings, axis=0)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def find_nearest_to_centroid(
    embeddings: np.ndarray, 
    labels: List[str], 
    centroid: np.ndarray,
    positions: List[Dict]
) -> List[Tuple[str, float, str]]:
    """Find positions nearest to centroid (core beliefs)."""
    similarities = []
    for i, (emb, label) in enumerate(zip(embeddings, labels)):
        sim = cosine_similarity(emb, centroid)
        title = positions[i]['title']
        similarities.append((label, sim, title))
    
    return sorted(similarities, key=lambda x: -x[1])


def find_outliers(
    embeddings: np.ndarray,
    labels: List[str],
    centroid: np.ndarray,
    positions: List[Dict]
) -> List[Tuple[str, float, str]]:
    """Find positions furthest from centroid (edge beliefs)."""
    similarities = []
    for i, (emb, label) in enumerate(zip(embeddings, labels)):
        sim = cosine_similarity(emb, centroid)
        title = positions[i]['title']
        similarities.append((label, sim, title))
    
    return sorted(similarities, key=lambda x: x[1])


def find_bridging_concepts(
    embeddings: np.ndarray,
    labels: List[str],
    positions: List[Dict],
    client: OpenAI
) -> List[Dict]:
    """
    Find concepts that are equidistant from multiple position clusters.
    These are the implicit beliefs in the "negative space".
    """
    # First, do simple clustering by finding pairs with high similarity
    # Then probe the midpoints
    
    bridging = []
    n = len(embeddings)
    
    # Find the most distant pairs (these define the space)
    distant_pairs = []
    for i in range(n):
        for j in range(i+1, n):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            if sim < 0.7:  # Meaningfully different
                distant_pairs.append((i, j, sim))
    
    distant_pairs.sort(key=lambda x: x[2])
    
    # For top distant pairs, compute midpoint and find what concept lives there
    for i, j, sim in distant_pairs[:10]:
        midpoint = (embeddings[i] + embeddings[j]) / 2
        midpoint = midpoint / np.linalg.norm(midpoint)  # Normalize
        
        bridging.append({
            'position_a': positions[i]['title'],
            'position_b': positions[j]['title'],
            'similarity': sim,
            'midpoint_vector': midpoint
        })
    
    return bridging


def probe_latent_dimensions(
    embeddings: np.ndarray,
    positions: List[Dict],
    client: OpenAI
) -> List[Dict]:
    """
    Use PCA to find the principal axes of V's belief space,
    then probe what concepts define those axes.
    """
    from sklearn.decomposition import PCA
    
    # Reduce to top components
    pca = PCA(n_components=10)
    reduced = pca.fit_transform(embeddings)
    
    # Get the principal components (these are the latent dimensions)
    components = pca.components_
    explained_variance = pca.explained_variance_ratio_
    
    dimensions = []
    for i, (comp, var) in enumerate(zip(components[:5], explained_variance[:5])):
        # Find positions that load highest on this dimension
        loadings = reduced[:, i]
        
        # Top positive loading
        pos_idx = np.argmax(loadings)
        # Top negative loading  
        neg_idx = np.argmin(loadings)
        
        dimensions.append({
            'dimension': i + 1,
            'variance_explained': var,
            'positive_pole': positions[pos_idx]['title'],
            'positive_insight': positions[pos_idx]['insight'][:200],
            'negative_pole': positions[neg_idx]['title'],
            'negative_insight': positions[neg_idx]['insight'][:200],
            'component_vector': comp
        })
    
    return dimensions


def synthesize_implicit_beliefs(
    dimensions: List[Dict],
    bridging: List[Dict],
    centroid: np.ndarray,
    client: OpenAI
) -> str:
    """
    Given the latent dimensions and bridging concepts,
    synthesize the implicit beliefs that V holds but hasn't articulated.
    """
    
    # Build a prompt for the LLM to synthesize
    dim_text = ""
    for d in dimensions[:5]:
        dim_text += f"""
Dimension {d['dimension']} ({d['variance_explained']:.1%} of variance):
  + Pole: {d['positive_pole']}
  - Pole: {d['negative_pole']}
"""
    
    bridge_text = ""
    for b in bridging[:5]:
        bridge_text += f"""
Bridge between:
  A: {b['position_a']}
  B: {b['position_b']}
  (similarity: {b['similarity']:.3f})
"""
    
    prompt = f"""Analyze the latent structure of this person's worldview.

PRINCIPAL DIMENSIONS (the axes that organize their beliefs):
{dim_text}

BRIDGING CONCEPTS (what connects distant beliefs):
{bridge_text}

Based on this geometric structure of their belief space:

1. What are the 3-5 IMPLICIT meta-beliefs that organize all their explicit positions?
   (These are the generating functions, not the outputs)

2. What beliefs likely exist in the "negative space" — things they almost certainly 
   believe but haven't articulated, based on the geometric relationships?

3. What PREDICTIONS would these implicit structures generate about:
   - Human behavior under uncertainty
   - Institutional performance
   - Technology adoption
   - Market efficiency

Be specific and concrete. These insights should be tradeable."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Vector space analysis of V's worldview")
    parser.add_argument("command", choices=["analyze", "dimensions", "bridges", "full"])
    args = parser.parse_args()
    
    print("Loading positions...")
    positions = get_positions()
    print(f"Found {len(positions)} positions")
    
    client = OpenAI()
    
    print("\nEmbedding positions...")
    embeddings, labels = embed_positions(positions)
    
    print("\nComputing centroid (core of worldview)...")
    centroid = find_centroid(embeddings)
    
    if args.command in ["analyze", "full"]:
        print("\n" + "="*60)
        print("POSITIONS NEAREST TO CENTROID (Core Beliefs)")
        print("="*60)
        nearest = find_nearest_to_centroid(embeddings, labels, centroid, positions)
        for label, sim, title in nearest[:10]:
            print(f"  [{sim:.3f}] {title}")
        
        print("\n" + "="*60)
        print("POSITIONS FURTHEST FROM CENTROID (Edge Beliefs)")
        print("="*60)
        outliers = find_outliers(embeddings, labels, centroid, positions)
        for label, sim, title in outliers[:10]:
            print(f"  [{sim:.3f}] {title}")
    
    if args.command in ["dimensions", "full"]:
        print("\n" + "="*60)
        print("LATENT DIMENSIONS (Principal Axes of Belief Space)")
        print("="*60)
        dimensions = probe_latent_dimensions(embeddings, positions, client)
        for d in dimensions:
            print(f"\nDimension {d['dimension']} ({d['variance_explained']:.1%} variance)")
            print(f"  + {d['positive_pole']}")
            print(f"  - {d['negative_pole']}")
        
        # Save for later use
        output_path = Path("/home/workspace/Projects/prediction-markets/analysis/latent_dimensions.json")
        with open(output_path, 'w') as f:
            # Convert numpy arrays to lists for JSON serialization
            for d in dimensions:
                d['component_vector'] = d['component_vector'].tolist()
            json.dump(dimensions, f, indent=2)
        print(f"\nSaved dimensions to {output_path}")
    
    if args.command in ["bridges", "full"]:
        print("\n" + "="*60)
        print("BRIDGING CONCEPTS (Negative Space)")
        print("="*60)
        bridging = find_bridging_concepts(embeddings, labels, positions, client)
        for b in bridging[:10]:
            print(f"\nBridge (sim: {b['similarity']:.3f}):")
            print(f"  A: {b['position_a']}")
            print(f"  B: {b['position_b']}")
    
    if args.command == "full":
        print("\n" + "="*60)
        print("SYNTHESIZING IMPLICIT BELIEFS...")
        print("="*60)
        dimensions = probe_latent_dimensions(embeddings, positions, client)
        bridging = find_bridging_concepts(embeddings, labels, positions, client)
        synthesis = synthesize_implicit_beliefs(dimensions, bridging, centroid, client)
        print(synthesis)
        
        # Save synthesis
        output_path = Path("/home/workspace/Projects/prediction-markets/analysis/implicit_beliefs.md")
        with open(output_path, 'w') as f:
            f.write("# Implicit Beliefs (Vector Space Analysis)\n\n")
            f.write(synthesis)
        print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()




