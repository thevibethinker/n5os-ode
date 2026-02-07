#!/usr/bin/env python3
"""
Surprisal Detector - Detects when retrieval doesn't match expectations

When a query returns low-similarity results, this indicates the system's
"working model of V" may be incomplete or incorrect. These surprisal events
trigger abductive reasoning to update beliefs.
"""

import sqlite3
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Load threshold from feature flags
FEATURE_FLAGS_PATH = Path("/home/workspace/N5/config/feature_flags.json")

def get_threshold() -> float:
    """Get surprisal threshold from feature flags."""
    if FEATURE_FLAGS_PATH.exists():
        flags = json.loads(FEATURE_FLAGS_PATH.read_text())
        return flags.get("N5_SURPRISAL_THRESHOLD", 0.3)
    return 0.3

REASONING_DB = Path("/home/workspace/N5/cognition/reasoning.db")


@dataclass
class SurprisalEvent:
    """A detected surprisal event - unexpected retrieval result."""
    id: str
    query: str
    expected_domain: Optional[str]
    top_similarity: float
    result_count: int
    threshold: float
    needs_reasoning: bool
    timestamp: str
    context_snippet: Optional[str] = None  # First result content preview
    
    def to_dict(self) -> Dict:
        return asdict(self)


class SurprisalDetector:
    """
    Detects and logs surprisal events during semantic search.
    
    A surprisal event occurs when:
    1. Query returns no results, OR
    2. Top result similarity < threshold
    
    These events indicate the retrieval system found something unexpected,
    which may warrant updating our beliefs about V.
    """
    
    def __init__(self, db_path: Path = REASONING_DB, threshold: float = 0.3):
        self.db_path = db_path
        self.threshold = threshold
        self._init_db()
    
    def _init_db(self):
        """Initialize the reasoning traces schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reasoning_traces (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                surprisal_score REAL,
                top_similarity REAL,
                result_count INTEGER,
                expected_domain TEXT,
                reasoning_invoked INTEGER DEFAULT 0,
                reasoning_result TEXT,  -- JSON
                belief_updates TEXT,  -- JSON array of changes
                context_snippet TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_traces_timestamp ON reasoning_traces(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_traces_surprisal ON reasoning_traces(surprisal_score)")
        conn.commit()
        conn.close()
    
    def _generate_id(self) -> str:
        """Generate unique trace ID."""
        import hashlib
        now = datetime.now(timezone.utc).isoformat()
        return hashlib.md5(now.encode()).hexdigest()[:12]
    
    def _infer_domain(self, query: str) -> Optional[str]:
        """
        Infer the expected domain from query content.
        
        Simple keyword-based heuristic. Future: Use LLM classification.
        """
        query_lower = query.lower()
        
        domain_keywords = {
            "identity": ["who am i", "my background", "my experience", "my name", "about me"],
            "preference": ["prefer", "like", "favorite", "want", "enjoy", "love", "hate", "dislike"],
            "behavior": ["usually", "always", "tend to", "habit", "pattern", "workflow", "how i"],
            "goal": ["goal", "objective", "want to", "planning", "trying to", "aim", "mission"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(kw in query_lower for kw in keywords):
                return domain
        
        return None
    
    def detect(
        self,
        query: str,
        results: List[Dict],
        threshold: Optional[float] = None
    ) -> Optional[SurprisalEvent]:
        """
        Detect if the search results indicate a surprisal event.
        
        Args:
            query: The search query
            results: List of search results with 'score' field
            threshold: Override default threshold
        
        Returns:
            SurprisalEvent if surprisal detected, None otherwise
        """
        threshold = threshold or self.threshold
        
        top_similarity = results[0]["score"] if results else 0.0
        result_count = len(results)
        
        # Calculate surprisal score (inverse of similarity)
        surprisal_score = 1.0 - top_similarity
        
        # Determine if this warrants reasoning
        needs_reasoning = (
            result_count == 0 or  # No results at all
            top_similarity < threshold  # Top result below threshold
        )
        
        if not needs_reasoning:
            return None
        
        # Create surprisal event
        event = SurprisalEvent(
            id=self._generate_id(),
            query=query,
            expected_domain=self._infer_domain(query),
            top_similarity=top_similarity,
            result_count=result_count,
            threshold=threshold,
            needs_reasoning=True,
            timestamp=datetime.now(timezone.utc).isoformat(),
            context_snippet=results[0]["content"][:200] if results else None
        )
        
        # Log the trace
        self._log_trace(event)
        
        return event
    
    def _log_trace(self, event: SurprisalEvent):
        """Log surprisal event to reasoning_traces table."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO reasoning_traces 
            (id, timestamp, query, surprisal_score, top_similarity, result_count, 
             expected_domain, reasoning_invoked, context_snippet)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
        """, (
            event.id,
            event.timestamp,
            event.query,
            1.0 - event.top_similarity,  # surprisal_score
            event.top_similarity,
            event.result_count,
            event.expected_domain,
            event.context_snippet
        ))
        conn.commit()
        conn.close()
    
    def mark_reasoning_complete(
        self,
        trace_id: str,
        reasoning_result: Dict,
        belief_updates: List[Dict]
    ):
        """Update trace with reasoning outcome."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            UPDATE reasoning_traces 
            SET reasoning_invoked = 1, 
                reasoning_result = ?,
                belief_updates = ?
            WHERE id = ?
        """, (
            json.dumps(reasoning_result),
            json.dumps(belief_updates),
            trace_id
        ))
        conn.commit()
        conn.close()
    
    def get_recent_traces(self, limit: int = 20) -> List[Dict]:
        """Get recent reasoning traces."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM reasoning_traces 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def get_uninvoked_traces(self, limit: int = 10) -> List[Dict]:
        """Get traces where reasoning was not yet invoked."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM reasoning_traces 
            WHERE reasoning_invoked = 0
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def stats(self) -> Dict[str, Any]:
        """Get surprisal detection statistics."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM reasoning_traces")
        total = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM reasoning_traces WHERE reasoning_invoked = 1")
        reasoned = cur.fetchone()[0]
        
        cur.execute("SELECT AVG(surprisal_score) FROM reasoning_traces")
        avg_surprisal = cur.fetchone()[0] or 0
        
        cur.execute("SELECT AVG(top_similarity) FROM reasoning_traces")
        avg_similarity = cur.fetchone()[0] or 0
        
        cur.execute("""
            SELECT expected_domain, COUNT(*) 
            FROM reasoning_traces 
            WHERE expected_domain IS NOT NULL
            GROUP BY expected_domain
        """)
        by_domain = dict(cur.fetchall())
        
        conn.close()
        
        return {
            "total_events": total,
            "reasoning_invoked": reasoned,
            "pending_reasoning": total - reasoned,
            "avg_surprisal_score": round(avg_surprisal, 3),
            "avg_top_similarity": round(avg_similarity, 3),
            "by_domain": by_domain,
            "threshold": self.threshold
        }


# CLI interface
if __name__ == "__main__":
    import sys
    
    detector = SurprisalDetector()
    
    if len(sys.argv) < 2:
        print("Usage: surprisal_detector.py <command> [args]")
        print("Commands: stats, recent, pending, test")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "stats":
        stats = detector.stats()
        print(json.dumps(stats, indent=2))
    
    elif cmd == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        traces = detector.get_recent_traces(limit)
        for t in traces:
            reasoned = "✓" if t["reasoning_invoked"] else "○"
            print(f"[{reasoned}] {t['timestamp'][:16]} | sim={t['top_similarity']:.2f} | {t['query'][:50]}...")
    
    elif cmd == "pending":
        traces = detector.get_uninvoked_traces()
        print(f"Pending reasoning: {len(traces)} traces")
        for t in traces:
            print(f"  {t['id']}: {t['query'][:60]}...")
    
    elif cmd == "test":
        # Simulate a surprisal event
        fake_results = [{"score": 0.15, "content": "This is a low-similarity result..."}]
        event = detector.detect("What is V's primary goal?", fake_results)
        if event:
            print(f"Surprisal detected: {event.id}")
            print(f"  Similarity: {event.top_similarity}")
            print(f"  Domain: {event.expected_domain}")
            print(f"  Needs reasoning: {event.needs_reasoning}")
        else:
            print("No surprisal detected")
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
