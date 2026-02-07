#!/usr/bin/env python3
"""
N5 Belief Store - Working Model of V

Stores inferred beliefs about V's identity, preferences, behaviors, and goals.
Beliefs are logical primitives that can be composed, validated, and updated
based on reasoning outcomes.

Storage: reasoning.db (SQLite) + periodic JSON export
"""

import sqlite3
import json
import os
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Paths
REASONING_DB = Path("/home/workspace/N5/cognition/reasoning.db")
BELIEFS_EXPORT = Path("/home/workspace/N5/cognition/beliefs_export.json")
HITL_QUEUE = Path("/home/workspace/N5/review/beliefs/")

@dataclass
class Belief:
    """A single belief about V."""
    id: str
    content: str
    confidence: float  # 0.0-1.0
    domain: str  # identity | preference | behavior | goal
    source: str  # inferred | explicit | resonance
    evidence: List[str]  # Block IDs or source references
    created_at: str
    last_validated: Optional[str] = None
    validation_count: int = 0
    contradicted_by: Optional[List[str]] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_row(cls, row: tuple) -> 'Belief':
        return cls(
            id=row[0],
            content=row[1],
            confidence=row[2],
            domain=row[3],
            source=row[4],
            evidence=json.loads(row[5]) if row[5] else [],
            created_at=row[6],
            last_validated=row[7],
            validation_count=row[8] or 0,
            contradicted_by=json.loads(row[9]) if row[9] else None
        )


class N5BeliefStore:
    """
    Manages beliefs about V - the "working model" in Memory-as-Reasoning.
    
    Key operations:
    - add_belief: Store a new belief
    - get_beliefs: Retrieve beliefs with optional filters
    - update_confidence: Adjust belief confidence based on evidence
    - find_contradictions: Detect conflicting beliefs
    - queue_for_review: Send low-confidence beliefs to HITL
    - prune: Remove beliefs below threshold
    """
    
    HITL_THRESHOLD = 0.6  # Beliefs below this go to review queue
    PRUNE_THRESHOLD = 0.2  # Beliefs below this are auto-pruned
    
    def __init__(self, db_path: Path = REASONING_DB):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the beliefs schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS beliefs (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                confidence REAL NOT NULL,
                domain TEXT NOT NULL,
                source TEXT NOT NULL,
                evidence TEXT,  -- JSON array
                created_at TEXT NOT NULL,
                last_validated TEXT,
                validation_count INTEGER DEFAULT 0,
                contradicted_by TEXT  -- JSON array of belief IDs
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_beliefs_domain ON beliefs(domain)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_beliefs_confidence ON beliefs(confidence)")
        conn.commit()
        conn.close()
    
    def _generate_id(self, content: str) -> str:
        """Generate stable ID from content hash."""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def add_belief(
        self,
        content: str,
        confidence: float,
        domain: str,
        source: str = "inferred",
        evidence: Optional[List[str]] = None
    ) -> Belief:
        """
        Add a new belief to the store.
        
        If confidence < HITL_THRESHOLD, automatically queues for review.
        """
        belief_id = self._generate_id(content)
        now = datetime.now(timezone.utc).isoformat()
        
        belief = Belief(
            id=belief_id,
            content=content,
            confidence=confidence,
            domain=domain,
            source=source,
            evidence=evidence or [],
            created_at=now,
            last_validated=None,
            validation_count=0,
            contradicted_by=None
        )
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO beliefs 
            (id, content, confidence, domain, source, evidence, created_at, last_validated, validation_count, contradicted_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            belief.id,
            belief.content,
            belief.confidence,
            belief.domain,
            belief.source,
            json.dumps(belief.evidence),
            belief.created_at,
            belief.last_validated,
            belief.validation_count,
            json.dumps(belief.contradicted_by) if belief.contradicted_by else None
        ))
        conn.commit()
        conn.close()
        
        # Queue for HITL if low confidence
        if confidence < self.HITL_THRESHOLD:
            self.queue_for_review(belief)
        
        return belief
    
    def get_belief(self, belief_id: str) -> Optional[Belief]:
        """Get a single belief by ID."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM beliefs WHERE id = ?", (belief_id,))
        row = cur.fetchone()
        conn.close()
        return Belief.from_row(row) if row else None
    
    def get_beliefs(
        self,
        domain: Optional[str] = None,
        min_confidence: Optional[float] = None,
        source: Optional[str] = None,
        limit: int = 100
    ) -> List[Belief]:
        """
        Retrieve beliefs with optional filters.
        
        Args:
            domain: Filter by domain (identity, preference, behavior, goal)
            min_confidence: Only beliefs above this confidence
            source: Filter by source (inferred, explicit, resonance)
            limit: Max results
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        query = "SELECT * FROM beliefs WHERE 1=1"
        params = []
        
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        if min_confidence is not None:
            query += " AND confidence >= ?"
            params.append(min_confidence)
        if source:
            query += " AND source = ?"
            params.append(source)
        
        query += " ORDER BY confidence DESC LIMIT ?"
        params.append(limit)
        
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        
        return [Belief.from_row(row) for row in rows]
    
    def update_confidence(self, belief_id: str, delta: float) -> Optional[Belief]:
        """
        Adjust belief confidence by delta.
        
        Clamps to [0.0, 1.0]. If drops below PRUNE_THRESHOLD, belief is removed.
        If drops below HITL_THRESHOLD, queued for review.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT confidence FROM beliefs WHERE id = ?", (belief_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return None
        
        new_confidence = max(0.0, min(1.0, row[0] + delta))
        
        if new_confidence < self.PRUNE_THRESHOLD:
            cur.execute("DELETE FROM beliefs WHERE id = ?", (belief_id,))
            conn.commit()
            conn.close()
            return None
        
        now = datetime.now(timezone.utc).isoformat()
        cur.execute("""
            UPDATE beliefs 
            SET confidence = ?, last_validated = ?, validation_count = validation_count + 1
            WHERE id = ?
        """, (new_confidence, now, belief_id))
        conn.commit()
        
        # Fetch updated belief
        cur.execute("SELECT * FROM beliefs WHERE id = ?", (belief_id,))
        row = cur.fetchone()
        conn.close()
        
        belief = Belief.from_row(row) if row else None
        
        # Queue for review if dropped below threshold
        if belief and new_confidence < self.HITL_THRESHOLD:
            self.queue_for_review(belief)
        
        return belief
    
    def find_contradictions(self, new_content: str, domain: str) -> List[Belief]:
        """
        Find beliefs that might contradict the new content.
        
        Simple heuristic: beliefs in same domain with opposite sentiment.
        Future: Use LLM for semantic contradiction detection.
        """
        existing = self.get_beliefs(domain=domain, min_confidence=0.3)
        
        # Simple keyword-based contradiction detection
        # (Will be enhanced with LLM in reasoner.py)
        contradictions = []
        negations = ["not", "never", "don't", "doesn't", "won't", "isn't", "aren't"]
        
        new_lower = new_content.lower()
        has_negation = any(neg in new_lower for neg in negations)
        
        for belief in existing:
            belief_lower = belief.content.lower()
            belief_has_negation = any(neg in belief_lower for neg in negations)
            
            # If one has negation and other doesn't, potential contradiction
            if has_negation != belief_has_negation:
                # Check for overlapping key terms
                new_terms = set(new_lower.split())
                belief_terms = set(belief_lower.split())
                overlap = new_terms & belief_terms - set(negations) - {"a", "the", "is", "are", "v", "to"}
                if len(overlap) >= 2:
                    contradictions.append(belief)
        
        return contradictions
    
    def mark_contradiction(self, belief_id: str, contradicting_id: str):
        """Record that two beliefs contradict each other."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT contradicted_by FROM beliefs WHERE id = ?", (belief_id,))
        row = cur.fetchone()
        if row:
            existing = json.loads(row[0]) if row[0] else []
            if contradicting_id not in existing:
                existing.append(contradicting_id)
            cur.execute(
                "UPDATE beliefs SET contradicted_by = ? WHERE id = ?",
                (json.dumps(existing), belief_id)
            )
            conn.commit()
        conn.close()
    
    def queue_for_review(self, belief: Belief):
        """
        Add belief to HITL review queue.
        
        Creates a markdown file in N5/review/beliefs/ for human review.
        """
        HITL_QUEUE.mkdir(parents=True, exist_ok=True)
        
        filename = f"{datetime.now().strftime('%Y%m%d')}_{belief.id}.md"
        filepath = HITL_QUEUE / filename
        
        content = f"""---
belief_id: {belief.id}
domain: {belief.domain}
confidence: {belief.confidence}
source: {belief.source}
created_at: {belief.created_at}
status: pending
---

# Belief Review: {belief.id}

## Content
> {belief.content}

## Evidence
{chr(10).join(f"- {e}" for e in belief.evidence) if belief.evidence else "- No evidence recorded"}

## Review Actions
- [ ] **Approve** - Boost confidence to 0.7
- [ ] **Reject** - Remove belief
- [ ] **Edit** - Modify content and re-evaluate

## Notes
_Add review notes here_
"""
        filepath.write_text(content)
    
    def export_to_json(self, path: Path = BELIEFS_EXPORT):
        """Export all beliefs to JSON for backup/inspection."""
        beliefs = self.get_beliefs(limit=10000)
        data = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "count": len(beliefs),
            "beliefs": [b.to_dict() for b in beliefs]
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        return path
    
    def get_review_queue(self, status: str = "pending") -> List[Dict]:
        """Get items from HITL review queue by status."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Check if review_queue table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='review_queue'")
        if not cur.fetchone():
            conn.close()
            return []
        
        cur.execute("""
            SELECT rq.*, b.content, b.confidence
            FROM review_queue rq
            LEFT JOIN beliefs b ON rq.belief_id = b.id
            WHERE rq.status = ?
            ORDER BY rq.created_at DESC
        """, (status,))
        
        rows = cur.fetchall()
        conn.close()
        return [dict(zip([c[0] for c in cur.description], row)) for row in rows]
    
    def approve_review(self, belief_id: str, notes: str = None):
        """Approve a belief review and increase confidence."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Get current confidence
        cur.execute("SELECT confidence FROM beliefs WHERE id = ?", (belief_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Belief {belief_id} not found")
        
        # Boost confidence by 0.2 (up to 0.8 max)
        new_confidence = min(0.8, row[0] + 0.2)
        now = datetime.now(timezone.utc).isoformat()
        
        cur.execute("""
            UPDATE beliefs
            SET confidence = ?, last_validated = ?, validation_count = validation_count + 1
            WHERE id = ?
        """, (new_confidence, now, belief_id))
        
        # Mark review as approved
        cur.execute("""
            UPDATE review_queue
            SET status = 'approved', reviewer_notes = ?, reviewed_at = ?
            WHERE belief_id = ? AND status = 'pending'
        """, (notes or "", now, belief_id))
        
        conn.commit()
        conn.close()
    
    def reject_review(self, belief_id: str, notes: str = None):
        """Reject a belief review and archive belief."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        
        # Archive belief
        cur.execute("""
            UPDATE beliefs
            SET status = 'archived', last_validated = ?
            WHERE id = ?
        """, (now, belief_id))
        
        # Mark review as rejected
        cur.execute("""
            UPDATE review_queue
            SET status = 'rejected', reviewer_notes = ?, reviewed_at = ?
            WHERE belief_id = ? AND status = 'pending'
        """, (notes or "", now, belief_id))
        
        conn.commit()
        conn.close()
    
    def prune(self, threshold: float = None) -> int:
        """Remove beliefs below confidence threshold. Returns count removed."""
        threshold = threshold or self.PRUNE_THRESHOLD
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM beliefs WHERE confidence < ?", (threshold,))
        removed = cur.rowcount
        conn.commit()
        conn.close()
        return removed
    
    def stats(self) -> Dict[str, Any]:
        """Get belief store statistics."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM beliefs")
        total = cur.fetchone()[0]
        
        cur.execute("SELECT domain, COUNT(*) FROM beliefs GROUP BY domain")
        by_domain = dict(cur.fetchall())
        
        cur.execute("SELECT AVG(confidence) FROM beliefs")
        avg_confidence = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(*) FROM beliefs WHERE confidence < ?", (self.HITL_THRESHOLD,))
        needs_review = cur.fetchone()[0]
        
        conn.close()
        
        return {
            "total": total,
            "by_domain": by_domain,
            "avg_confidence": round(avg_confidence, 3),
            "needs_review": needs_review
        }


# CLI interface
if __name__ == "__main__":
    import sys
    
    store = N5BeliefStore()
    
    if len(sys.argv) < 2:
        print("Usage: belief_store.py <command> [args]")
        print("Commands: stats, list, add, export, prune, review-queue")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "stats":
        stats = store.stats()
        print(json.dumps(stats, indent=2))
    
    elif cmd == "list":
        domain = sys.argv[2] if len(sys.argv) > 2 else None
        beliefs = store.get_beliefs(domain=domain, limit=20)
        for b in beliefs:
            print(f"[{b.confidence:.2f}] ({b.domain}) {b.content[:80]}...")
    
    elif cmd == "add":
        if len(sys.argv) < 5:
            print("Usage: belief_store.py add <content> <domain> <confidence>")
            sys.exit(1)
        content = sys.argv[2]
        domain = sys.argv[3]
        confidence = float(sys.argv[4])
        belief = store.add_belief(content, confidence, domain, source="explicit")
        print(f"Added belief {belief.id}")
    
    elif cmd == "export":
        path = store.export_to_json()
        print(f"Exported to {path}")
    
    elif cmd == "prune":
        removed = store.prune()
        print(f"Pruned {removed} low-confidence beliefs")
    
    elif cmd == "review-queue":
        import os
        queue_files = list(HITL_QUEUE.glob("*.md")) if HITL_QUEUE.exists() else []
        print(f"HITL Queue: {len(queue_files)} beliefs pending review")
        for f in queue_files[:10]:
            print(f"  - {f.name}")
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
