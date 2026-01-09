#!/usr/bin/env python3
"""
Position Correlation Engine

Matches incoming tweets against V's positions database using
semantic similarity + keyword matching.

Environment variables:
- OPENAI_API_KEY: For embeddings (optional, falls back to local model)
"""

import os
import sqlite3
import struct
import json
import logging
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

POSITIONS_DB = "/home/workspace/N5/data/positions.db"

DOMAIN_BOOSTS = {
    'hiring-market': 1.0,
    'recruiting': 1.0,
    'talent-acquisition': 1.0,
    'hr-tech': 0.9,
    'future-of-work': 0.8,
    'ai-automation': 0.7,
    'epistemology': 0.5,
    'personal-foundations': 0.3,
}

@dataclass
class PositionMatch:
    position_id: str
    title: str
    insight: str
    domain: str
    similarity_score: float
    match_reasons: List[str]

# --- Embedding Helpers ---

def embedding_to_blob(embedding: List[float]) -> bytes:
    return struct.pack(f'{len(embedding)}f', *embedding)

def blob_to_embedding(blob: bytes) -> List[float]:
    if not blob:
        return []
    count = len(blob) // 4
    return list(struct.unpack(f'{count}f', blob))

def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    a, b = np.array(a), np.array(b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return np.dot(a, b) / (norm_a * norm_b)

_local_model = None

def compute_embedding(text: str) -> List[float]:
    """
    Compute embedding vector for text.
    Uses OpenAI text-embedding-3-small (or local model if available).
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"OpenAI embedding failed: {e}. Falling back to local model.")
    
    # Fallback to local model
    global _local_model
    if _local_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _local_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.error(f"Failed to load local embedding model: {e}")
            raise
    
    return _local_model.encode(text).tolist()

# --- Core Functions ---

def ensure_position_embeddings() -> int:
    """
    Compute and store embeddings for any positions missing them.
    Returns count of positions updated.
    """
    conn = sqlite3.connect(POSITIONS_DB)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, insight FROM positions WHERE embedding IS NULL")
    rows = cursor.fetchall()
    
    updated_count = 0
    for pos_id, insight in rows:
        try:
            logger.info(f"Computing embedding for position: {pos_id}")
            embedding = compute_embedding(insight)
            blob = embedding_to_blob(embedding)
            cursor.execute("UPDATE positions SET embedding = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (blob, pos_id))
            updated_count += 1
        except Exception as e:
            logger.error(f"Failed to update embedding for {pos_id}: {e}")
            
    conn.commit()
    conn.close()
    return updated_count

def get_position_context(position_id: str) -> Dict[str, Any]:
    """
    Get complete position details for draft generation.
    """
    conn = sqlite3.connect(POSITIONS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {}
    
    result = dict(row)
    # Remove binary data
    if 'embedding' in result:
        del result['embedding']
        
    # Parse JSON components if they exist
    if result.get('components'):
        try:
            result['components'] = json.loads(result['components'])
        except:
            pass
            
    return result

def match_positions(tweet_text: str, top_n: int = 5) -> List[PositionMatch]:
    """
    Find positions most relevant to a tweet.
    
    Uses hybrid matching:
    1. Semantic similarity (embeddings)
    2. Keyword overlap boost
    3. Domain relevance boost
    """
    tweet_embedding = compute_embedding(tweet_text)
    tweet_words = set(tweet_text.lower().split())
    
    conn = sqlite3.connect(POSITIONS_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, insight, domain, embedding FROM positions")
    rows = cursor.fetchall()
    conn.close()
    
    matches = []
    for pos_id, title, insight, domain, embedding_blob in rows:
        reasons = []
        
        # 1. Semantic Score (70%)
        semantic_score = 0.0
        if embedding_blob:
            pos_embedding = blob_to_embedding(embedding_blob)
            # If embedding lengths don't match (e.g. OpenAI vs local), semantic similarity won't work well.
            # In a real app we'd force consistent embeddings, but here we'll just check length.
            if len(pos_embedding) == len(tweet_embedding):
                semantic_score = cosine_similarity(tweet_embedding, pos_embedding)
                reasons.append(f"semantic: {semantic_score:.3f}")
            else:
                logger.warning(f"Embedding length mismatch for {pos_id}. Pos: {len(pos_embedding)}, Tweet: {len(tweet_embedding)}")
        
        # 2. Keyword Overlap (20%)
        keyword_score = 0.0
        pos_content = f"{title} {insight} {domain}".lower()
        matched_words = []
        for word in tweet_words:
            if len(word) > 3 and word in pos_content:
                matched_words.append(word)
        
        if matched_words:
            keyword_score = min(1.0, len(matched_words) / 10.0) # Simple heuristic
            reasons.append(f"keyword: {', '.join(matched_words[:5])}")
            
        # 3. Domain Boost (10%)
        domain_boost = DOMAIN_BOOSTS.get(domain, 0.0)
        if domain_boost > 0:
            reasons.append(f"domain: {domain}")
            
        # Weighted Final Score
        final_score = (0.70 * semantic_score) + (0.20 * keyword_score) + (0.10 * domain_boost)
        
        matches.append(PositionMatch(
            position_id=pos_id,
            title=title,
            insight=insight,
            domain=domain,
            similarity_score=final_score,
            match_reasons=reasons
        ))
        
    # Sort and return top N
    matches.sort(key=lambda x: x.similarity_score, reverse=True)
    return matches[:top_n]

# --- CLI Interface ---

if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Position Matcher CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # match command
    match_parser = subparsers.add_parser("match", help="Match tweet to positions")
    match_parser.add_argument("tweet", help="Tweet text to match")
    match_parser.add_argument("--top", type=int, default=5, help="Top N matches")
    
    # backfill command
    backfill_parser = subparsers.add_parser("backfill", help="Backfill position embeddings")
    
    # context command
    context_parser = subparsers.add_parser("context", help="Get position context")
    context_parser.add_argument("position_id", help="Position ID")
    
    args = parser.parse_args()
    
    if args.command == "match":
        results = match_positions(args.tweet, top_n=args.top)
        output = {
            "tweet": args.tweet,
            "matches": [asdict(m) for m in results]
        }
        print(json.dumps(output, indent=2))
        
    elif args.command == "backfill":
        count = ensure_position_embeddings()
        print(f"Updated {count} positions with embeddings.")
        
    elif args.command == "context":
        ctx = get_position_context(args.position_id)
        if ctx:
            print(json.dumps(ctx, indent=2))
        else:
            print(f"Position not found: {args.position_id}")
            sys.exit(1)
    else:
        parser.print_help()

