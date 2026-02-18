#!/usr/bin/env python3
"""
Semantic Links Engine for YCB Content Layer

Auto-discovers relationships between content entries using embeddings and similarity scoring.
Leverages existing N5 vector store infrastructure.
"""

import sqlite3
import os
import sys
import argparse
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

# Add N5 to path
sys.path.insert(0, '/home/workspace')
from N5.cognition.n5_memory_client import N5MemoryClient

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("semantic_links")

class SemanticLinkEngine:
    def __init__(self, 
                 content_db_path: str = "/home/workspace/N5/data/content_library.db",
                 vector_db_path: str = "/home/workspace/N5/cognition/vectors_v2.db"):
        self.content_db_path = content_db_path
        self.vector_db_path = vector_db_path
        self.memory_client = N5MemoryClient(vector_db_path)
        
    def _get_content_conn(self):
        """Get connection to content library database."""
        return sqlite3.connect(self.content_db_path)
    
    def _get_vector_conn(self):
        """Get connection to vector database."""  
        return sqlite3.connect(self.vector_db_path)
    
    def _get_content_item_mapping(self) -> Dict[str, str]:
        """Create mapping from content library file paths to item IDs."""
        mapping = {}
        with self._get_content_conn() as conn:
            cursor = conn.execute("""
                SELECT id, source_file_path, title 
                FROM items 
                WHERE deprecated = 0 AND source_file_path IS NOT NULL
            """)
            for item_id, source_file_path, title in cursor.fetchall():
                if source_file_path:
                    # Store both the source_file_path and derived absolute path
                    abs_path = str(Path("/home/workspace") / source_file_path)
                    mapping[abs_path] = item_id
                    mapping[source_file_path] = item_id
        
        LOG.info(f"Created content mapping with {len(mapping)} entries")
        return mapping
    
    def _find_content_vectors(self, item_id: str = None) -> List[Tuple[str, str, np.ndarray]]:
        """Find vectors for content library items."""
        content_mapping = self._get_content_item_mapping()
        vectors = []
        
        with self._get_vector_conn() as conn:
            if item_id:
                # Find vectors for a specific item
                item_paths = [k for k, v in content_mapping.items() if v == item_id]
                if not item_paths:
                    LOG.warning(f"No file paths found for item {item_id}")
                    return []
                
                placeholders = ','.join('?' for _ in item_paths)
                query = f"""
                    SELECT r.path, b.id, v.embedding
                    FROM resources r
                    JOIN blocks b ON r.id = b.resource_id  
                    JOIN vectors v ON b.id = v.block_id
                    WHERE r.path IN ({placeholders})
                """
                cursor = conn.execute(query, item_paths)
            else:
                # Find all content library vectors
                query = """
                    SELECT r.path, b.id, v.embedding
                    FROM resources r
                    JOIN blocks b ON r.id = b.resource_id
                    JOIN vectors v ON b.id = v.block_id  
                    WHERE r.path LIKE '%content-library%'
                """
                cursor = conn.execute(query)
            
            for resource_path, block_id, embedding_blob in cursor.fetchall():
                try:
                    # Convert blob back to numpy array
                    embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                    
                    # Get the content item ID
                    content_item_id = content_mapping.get(resource_path)
                    if content_item_id:
                        vectors.append((content_item_id, block_id, embedding))
                except Exception as e:
                    LOG.warning(f"Failed to process embedding for {resource_path}: {e}")
        
        LOG.info(f"Found {len(vectors)} vectors for content items")
        return vectors
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2) 
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _classify_link(self, item_a_id: str, item_b_id: str, score: float) -> str:
        """Classify the type of relationship between two items."""
        # Simple scoring-based classification
        if score > 0.9:
            return 'very_similar'
        elif score > 0.85:
            return 'related' 
        elif score > 0.75:
            return 'loosely_related'
        else:
            return 'weakly_related'
    
    def _aggregate_item_similarity(self, vectors: List[Tuple[str, str, np.ndarray]], 
                                 target_item_id: str) -> Dict[str, float]:
        """Aggregate similarity scores across all blocks for each item."""
        target_vectors = [v for item_id, block_id, v in vectors if item_id == target_item_id]
        if not target_vectors:
            return {}
        
        # Group vectors by item
        item_vectors = {}
        for item_id, block_id, vector in vectors:
            if item_id != target_item_id:  # Don't compare to self
                if item_id not in item_vectors:
                    item_vectors[item_id] = []
                item_vectors[item_id].append(vector)
        
        # Calculate max similarity across all block pairs
        similarities = {}
        for item_id, item_vecs in item_vectors.items():
            max_sim = 0.0
            for target_vec in target_vectors:
                for item_vec in item_vecs:
                    sim = self._cosine_similarity(target_vec, item_vec)
                    max_sim = max(max_sim, sim)
            similarities[item_id] = max_sim
        
        return similarities
    
    def get_link_graph(self, root_item_id: str, depth: int = 2) -> Dict:
        """Generate a graph of linked items starting from a root item."""
        nodes = {}
        edges = []
        visited = set()
        to_process = [(root_item_id, 0)]
        
        with self._get_content_conn() as conn:
            while to_process:
                item_id, current_depth = to_process.pop(0)
                
                if item_id in visited or current_depth >= depth:
                    continue
                    
                visited.add(item_id)
                
                # Get item info for node
                cursor = conn.execute("""
                    SELECT title, content_type, url
                    FROM items
                    WHERE id = ?
                """, (item_id,))
                
                row = cursor.fetchone()
                if row:
                    title, content_type, url = row
                    nodes[item_id] = {
                        "id": item_id,
                        "title": title,
                        "content_type": content_type,
                        "url": url,
                        "depth": current_depth
                    }
                
                # Get links from this item
                cursor = conn.execute("""
                    SELECT target_item_id, link_type, strength
                    FROM entry_links
                    WHERE source_item_id = ?
                    ORDER BY strength DESC
                """, (item_id,))
                
                for target_id, link_type, strength in cursor.fetchall():
                    edges.append({
                        "source": item_id,
                        "target": target_id,
                        "link_type": link_type,
                        "strength": strength
                    })
                    
                    if current_depth + 1 < depth:
                        to_process.append((target_id, current_depth + 1))
        
        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "root": root_item_id,
            "depth": depth
        }

    def compute_links(self, item_id: str = None, threshold: float = 0.75, max_links: int = 5) -> Dict:
        """
        Compute semantic links for an item (or all items).
        
        Args:
            item_id: Specific item to process, or None for all
            threshold: Minimum similarity score (0.0-1.0)
            max_links: Max links to create per item
            
        Returns:
            Dictionary with results and statistics
        """
        LOG.info(f"Computing links - item_id: {item_id}, threshold: {threshold}, max_links: {max_links}")
        
        # Get all content vectors
        all_vectors = self._find_content_vectors()
        if not all_vectors:
            return {"error": "No vectors found for content items"}
        
        results = {"links_created": 0, "total_links_created": 0, "items_processed": 0, "errors": []}
        
        if item_id:
            # Process single item
            try:
                similarities = self._aggregate_item_similarity(all_vectors, item_id)
                links = self._create_links_for_item(item_id, similarities, threshold, max_links)
                results["links_created"] = len(links)
                results["total_links_created"] = len(links)
                results["items_processed"] = 1
            except Exception as e:
                results["errors"].append(f"Error processing item {item_id}: {str(e)}")
        else:
            # Process all items
            unique_items = list(set(item_id for item_id, _, _ in all_vectors))
            total_links = 0
            
            for target_item_id in unique_items:
                try:
                    similarities = self._aggregate_item_similarity(all_vectors, target_item_id)
                    links = self._create_links_for_item(target_item_id, similarities, threshold, max_links)
                    total_links += len(links)
                except Exception as e:
                    results["errors"].append(f"Error processing item {target_item_id}: {str(e)}")
            
            results["links_created"] = total_links
            results["total_links_created"] = total_links
            results["items_processed"] = len(unique_items)
        
        LOG.info(f"Created {results['total_links_created']} links for {results['items_processed']} items")
        return results
    
    def _create_links_for_item(self, item_id: str, similarities: Dict[str, float], 
                             threshold: float, max_links: int) -> List[Dict]:
        """Create links for a single item based on similarities."""
        # Filter and sort by similarity
        candidates = [(sim_item_id, score) for sim_item_id, score in similarities.items() 
                     if score >= threshold]
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Take top N
        top_candidates = candidates[:max_links]
        
        links_created = []
        with self._get_content_conn() as conn:
            for target_item_id, score in top_candidates:
                link_type = self._classify_link(item_id, target_item_id, score)
                
                # Convert numpy float to Python float to avoid BLOB storage
                score_float = float(score)
                
                # Insert or replace link
                conn.execute("""
                    INSERT OR REPLACE INTO entry_links 
                    (id, source_item_id, target_item_id, link_type, strength, created_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (
                    f"{item_id}_{target_item_id}_{link_type}",
                    item_id,
                    target_item_id, 
                    link_type,
                    score_float
                ))
                
                links_created.append({
                    "source": item_id,
                    "target": target_item_id,
                    "type": link_type,
                    "strength": score_float
                })
        
        return links_created
    
    def get_related(self, item_id: str, min_strength: float = 0.7, limit: int = 10) -> List[Dict]:
        """Get related items for display."""
        with self._get_content_conn() as conn:
            cursor = conn.execute("""
                SELECT 
                    el.target_item_id,
                    el.link_type,
                    el.strength,
                    i.title,
                    i.content_type,
                    i.url
                FROM entry_links el
                JOIN items i ON el.target_item_id = i.id
                WHERE el.source_item_id = ? AND el.strength >= ?
                ORDER BY el.strength DESC
                LIMIT ?
            """, (item_id, min_strength, limit))
            
            related = []
            for target_id, link_type, strength, title, content_type, url in cursor.fetchall():
                related.append({
                    "item_id": target_id,
                    "title": title,
                    "content_type": content_type,
                    "url": url,
                    "link_type": link_type,
                    "strength": strength
                })
            
            return related


def main():
    parser = argparse.ArgumentParser(description="Semantic Links Engine")
    parser.add_argument("command", choices=["compute", "compute-all", "related", "stats"])
    parser.add_argument("item_id", nargs="?", help="Content item ID")
    parser.add_argument("--threshold", type=float, default=0.75, help="Similarity threshold")
    parser.add_argument("--max-links", type=int, default=5, help="Max links per item")
    parser.add_argument("--min-strength", type=float, default=0.7, help="Min strength for related query")
    parser.add_argument("--limit", type=int, default=10, help="Limit for related query")
    
    args = parser.parse_args()
    
    engine = SemanticLinkEngine()
    
    if args.command == "compute":
        if not args.item_id:
            print("Error: item_id required for compute command")
            sys.exit(1)
        result = engine.compute_links(args.item_id, args.threshold, args.max_links)
        print(json.dumps(result, indent=2))
    
    elif args.command == "compute-all":
        result = engine.compute_links(None, args.threshold, args.max_links)
        print(json.dumps(result, indent=2))
    
    elif args.command == "related":
        if not args.item_id:
            print("Error: item_id required for related command")
            sys.exit(1)
        related = engine.get_related(args.item_id, args.min_strength, args.limit)
        
        if not related:
            print(f"No related items found for {args.item_id}")
            return
        
        print(f"Related to item {args.item_id}:")
        print()
        for item in related:
            strength_bar = "█" * int(item["strength"] * 10)
            print(f"[{item['strength']:.2f}] {strength_bar} {item['link_type']}: {item['title']}")
            if item['url']:
                print(f"    URL: {item['url']}")
            print()
    
    elif args.command == "stats":
        with sqlite3.connect("/home/workspace/N5/data/content_library.db") as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM entry_links")
            link_count = cursor.fetchone()[0]
            
            cursor = conn.execute("""
                SELECT link_type, COUNT(*) 
                FROM entry_links 
                GROUP BY link_type 
                ORDER BY COUNT(*) DESC
            """)
            types = cursor.fetchall()
            
            cursor = conn.execute("""
                SELECT AVG(strength), MIN(strength), MAX(strength)
                FROM entry_links
            """)
            avg_strength, min_strength, max_strength = cursor.fetchone()
            
            print(f"Link Statistics:")
            print(f"  Total links: {link_count}")
            print(f"  Strength - avg: {avg_strength:.3f}, min: {min_strength:.3f}, max: {max_strength:.3f}")
            print(f"  Types:")
            for link_type, count in types:
                print(f"    {link_type}: {count}")


if __name__ == "__main__":
    main()