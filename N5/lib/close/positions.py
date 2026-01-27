#!/usr/bin/env python3
"""Position extraction from conversations and builds."""

from pathlib import Path
from typing import List

def extract_from_conversation(convo_id: str) -> List[str]:
    """Extract position candidates from a single conversation.
    
    Returns list of position summaries for review.
    """
    # This would invoke LLM to scan conversation
    # For now, return empty (LLM integration needed)
    return []

def extract_from_build(slug: str, deposits: List[dict]) -> List[str]:
    """Extract position candidates from build deposits.
    
    Aggregates learnings and decisions across all workers.
    """
    candidates = []
    
    for deposit in deposits:
        learnings = deposit.get('learnings', '')
        if learnings and len(learnings) > 50:
            # Heuristic: substantial learnings might be position-worthy
            candidates.append(f"[{deposit['drop_id']}] {learnings[:100]}...")
    
    return candidates