#!/usr/bin/env python3
"""
N5 Reasoner - Abductive Reasoning for Memory-as-Reasoning

When surprisal events occur (unexpected retrieval results), the reasoner
uses LLM inference to:
1. Understand what the mismatch implies about V
2. Propose belief updates (new beliefs or confidence adjustments)
3. Detect contradictions with existing beliefs

This is the "reasoning layer" that sits atop the retrieval layer.
"""

import os
import json
import requests
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from N5.cognition.belief_store import N5BeliefStore, Belief
from N5.cognition.surprisal_detector import SurprisalEvent, SurprisalDetector

# Feature flags
FEATURE_FLAGS_PATH = Path("/home/workspace/N5/config/feature_flags.json")

def get_config() -> Dict:
    """Load reasoning configuration."""
    if FEATURE_FLAGS_PATH.exists():
        return json.loads(FEATURE_FLAGS_PATH.read_text())
    return {
        "N5_REASONING_ENABLED": False,
        "N5_REASONING_MODEL": "anthropic:claude-sonnet-4-20250514",
        "N5_BELIEF_HITL_THRESHOLD": 0.6
    }


@dataclass
class ReasoningResult:
    """Result of abductive reasoning about a surprisal event."""
    trace_id: str
    inference: str  # What we infer about V
    belief_updates: List[Dict]  # Changes to existing beliefs
    new_beliefs: List[Dict]  # New beliefs to add
    contradictions: List[str]  # IDs of contradicting beliefs
    confidence: float  # Confidence in this reasoning
    raw_response: Optional[str] = None


class N5Reasoner:
    """
    Performs abductive reasoning when surprisal events occur.
    
    Uses /zo/ask API to invoke LLM reasoning about what unexpected
    retrieval results imply about V's identity, preferences, and behaviors.
    """
    
    def __init__(
        self,
        belief_store: Optional[N5BeliefStore] = None,
        surprisal_detector: Optional[SurprisalDetector] = None
    ):
        self.beliefs = belief_store or N5BeliefStore()
        self.detector = surprisal_detector or SurprisalDetector()
        self.config = get_config()
        self._api_token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    
    def is_enabled(self) -> bool:
        """Check if reasoning layer is enabled."""
        return self.config.get("N5_REASONING_ENABLED", False)
    
    def reason_about(
        self,
        event: SurprisalEvent,
        context: List[Dict]
    ) -> Optional[ReasoningResult]:
        """
        Perform abductive reasoning about a surprisal event.
        
        Args:
            event: The surprisal event to reason about
            context: The search results (for context)
        
        Returns:
            ReasoningResult with inferences and proposed belief updates
        """
        if not self.is_enabled():
            return None
        
        if not self._api_token:
            print("Warning: ZO_CLIENT_IDENTITY_TOKEN not set, skipping reasoning")
            return None
        
        # Get relevant existing beliefs
        relevant_beliefs = []
        if event.expected_domain:
            relevant_beliefs = self.beliefs.get_beliefs(
                domain=event.expected_domain,
                min_confidence=0.3,
                limit=10
            )
        
        # Build reasoning prompt
        prompt = self._build_reasoning_prompt(event, context, relevant_beliefs)
        
        # Call /zo/ask
        try:
            response = requests.post(
                "https://api.zo.computer/zo/ask",
                headers={
                    "authorization": self._api_token,
                    "content-type": "application/json"
                },
                json={
                    "input": prompt,
                    "output_format": {
                        "type": "object",
                        "properties": {
                            "inference": {"type": "string"},
                            "belief_updates": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "belief_id": {"type": "string"},
                                        "confidence_delta": {"type": "number"}
                                    }
                                }
                            },
                            "new_beliefs": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "content": {"type": "string"},
                                        "confidence": {"type": "number"},
                                        "domain": {"type": "string"}
                                    },
                                    "required": ["content", "confidence", "domain"]
                                }
                            },
                            "reasoning_confidence": {"type": "number"}
                        },
                        "required": ["inference", "belief_updates", "new_beliefs", "reasoning_confidence"]
                    }
                },
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"Reasoning API error: {response.status_code}")
                return None
            
            result_data = response.json().get("output", {})
            if isinstance(result_data, str):
                result_data = json.loads(result_data)
            
        except Exception as e:
            print(f"Reasoning failed: {e}")
            return None
        
        # Parse result
        result = ReasoningResult(
            trace_id=event.id,
            inference=result_data.get("inference", ""),
            belief_updates=result_data.get("belief_updates", []),
            new_beliefs=result_data.get("new_beliefs", []),
            contradictions=[],  # Will be populated during apply
            confidence=result_data.get("reasoning_confidence", 0.5),
            raw_response=json.dumps(result_data)
        )
        
        return result
    
    def _build_reasoning_prompt(
        self,
        event: SurprisalEvent,
        context: List[Dict],
        existing_beliefs: List[Belief]
    ) -> str:
        """Build the prompt for abductive reasoning."""
        
        context_text = ""
        if context:
            context_text = "\n".join([
                f"- [{r.get('score', 0):.2f}] {r.get('content', '')[:200]}..."
                for r in context[:5]
            ])
        else:
            context_text = "(No results returned)"
        
        beliefs_text = ""
        if existing_beliefs:
            beliefs_text = "\n".join([
                f"- [{b.id}] ({b.confidence:.2f}) {b.content}"
                for b in existing_beliefs
            ])
        else:
            beliefs_text = "(No existing beliefs in this domain)"
        
        return f"""You are analyzing a surprisal event in V's semantic memory system.

## Context
A search query returned unexpected results (low similarity or no results).
This may indicate that our "working model of V" is incomplete or incorrect.

## The Event
- **Query:** {event.query}
- **Top Result Similarity:** {event.top_similarity:.3f} (threshold: {event.threshold})
- **Results Count:** {event.result_count}
- **Inferred Domain:** {event.expected_domain or "unknown"}

## Retrieved Content (if any)
{context_text}

## Existing Beliefs About V (in this domain)
{beliefs_text}

## Your Task
Using abductive reasoning, determine:

1. **Inference**: What does this mismatch suggest about V's current focus, priorities, or characteristics? Be specific and actionable.

2. **Belief Updates**: Should any existing beliefs have their confidence adjusted?
   - Positive delta = evidence supports the belief
   - Negative delta = evidence contradicts the belief
   - Range: -0.3 to +0.3

3. **New Beliefs**: Should any new beliefs be added based on this observation?
   - Only add beliefs with clear evidence
   - Confidence should reflect uncertainty (0.4-0.7 for inferred beliefs)
   - Domain must be: identity, preference, behavior, or goal

4. **Reasoning Confidence**: How confident are you in this analysis? (0.0-1.0)

Be conservative. Only propose updates with genuine evidence. It's better to acknowledge uncertainty than to fabricate beliefs.
"""
    
    def apply_reasoning(self, result: ReasoningResult) -> Dict[str, Any]:
        """
        Apply reasoning results to the belief store.
        
        Returns summary of changes made.
        """
        changes = {
            "updates_applied": 0,
            "beliefs_added": 0,
            "contradictions_found": 0,
            "hitl_queued": 0
        }
        
        hitl_threshold = self.config.get("N5_BELIEF_HITL_THRESHOLD", 0.6)
        
        # Apply confidence updates to existing beliefs
        for update in result.belief_updates:
            belief_id = update.get("belief_id")
            delta = update.get("confidence_delta", 0)
            if belief_id and delta:
                updated = self.beliefs.update_confidence(belief_id, delta)
                if updated:
                    changes["updates_applied"] += 1
        
        # Add new beliefs
        for new_belief in result.new_beliefs:
            content = new_belief.get("content")
            confidence = new_belief.get("confidence", 0.5)
            domain = new_belief.get("domain", "behavior")
            
            if not content:
                continue
            
            # Check for contradictions
            contradictions = self.beliefs.find_contradictions(content, domain)
            if contradictions:
                result.contradictions.extend([c.id for c in contradictions])
                changes["contradictions_found"] += len(contradictions)
                # Lower confidence if contradictions exist
                confidence = min(confidence, 0.4)
            
            # Add the belief
            belief = self.beliefs.add_belief(
                content=content,
                confidence=confidence,
                domain=domain,
                source="inferred",
                evidence=[f"reasoning:{result.trace_id}"]
            )
            changes["beliefs_added"] += 1
            
            if confidence < hitl_threshold:
                changes["hitl_queued"] += 1
            
            # Mark contradictions
            for contra_id in result.contradictions:
                self.beliefs.mark_contradiction(belief.id, contra_id)
                self.beliefs.mark_contradiction(contra_id, belief.id)
        
        # Update the reasoning trace
        self.detector.mark_reasoning_complete(
            result.trace_id,
            {
                "inference": result.inference,
                "confidence": result.confidence
            },
            result.belief_updates + [{"new": b} for b in result.new_beliefs]
        )
        
        return changes
    
    def process_pending(self, limit: int = 5) -> List[Dict]:
        """
        Process pending surprisal events that haven't been reasoned about.
        
        Returns list of processing results.
        """
        if not self.is_enabled():
            return []
        
        pending = self.detector.get_uninvoked_traces(limit)
        results = []
        
        for trace in pending:
            # Reconstruct event
            event = SurprisalEvent(
                id=trace["id"],
                query=trace["query"],
                expected_domain=trace["expected_domain"],
                top_similarity=trace["top_similarity"],
                result_count=trace["result_count"],
                threshold=self.detector.threshold,
                needs_reasoning=True,
                timestamp=trace["timestamp"],
                context_snippet=trace.get("context_snippet")
            )
            
            # Get context (we don't have original results, use snippet)
            context = []
            if trace.get("context_snippet"):
                context = [{"score": trace["top_similarity"], "content": trace["context_snippet"]}]
            
            # Reason about it
            reasoning = self.reason_about(event, context)
            if reasoning:
                changes = self.apply_reasoning(reasoning)
                results.append({
                    "trace_id": event.id,
                    "inference": reasoning.inference,
                    "changes": changes
                })
        
        return results


# CLI interface
if __name__ == "__main__":
    import sys
    
    reasoner = N5Reasoner()
    
    if len(sys.argv) < 2:
        print("Usage: reasoner.py <command> [args]")
        print("Commands: status, process, test")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        enabled = reasoner.is_enabled()
        print(f"Reasoning enabled: {enabled}")
        print(f"Model: {reasoner.config.get('N5_REASONING_MODEL')}")
        print(f"HITL threshold: {reasoner.config.get('N5_BELIEF_HITL_THRESHOLD')}")
        
        belief_stats = reasoner.beliefs.stats()
        print(f"\nBeliefs: {belief_stats['total']} total")
        print(f"  Avg confidence: {belief_stats['avg_confidence']}")
        print(f"  Needs review: {belief_stats['needs_review']}")
        
        detector_stats = reasoner.detector.stats()
        print(f"\nSurprisal events: {detector_stats['total_events']} total")
        print(f"  Pending reasoning: {detector_stats['pending_reasoning']}")
    
    elif cmd == "process":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        results = reasoner.process_pending(limit)
        print(f"Processed {len(results)} pending events")
        for r in results:
            print(f"\n{r['trace_id']}:")
            print(f"  Inference: {r['inference'][:100]}...")
            print(f"  Changes: {r['changes']}")
    
    elif cmd == "test":
        # Test with a synthetic event
        event = SurprisalEvent(
            id="test_" + datetime.now().strftime("%H%M%S"),
            query="What does V prioritize in career decisions?",
            expected_domain="goal",
            top_similarity=0.25,
            result_count=3,
            threshold=0.3,
            needs_reasoning=True,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        context = [
            {"score": 0.25, "content": "V is the founder of Careerspan, focused on semantic identity modeling."},
            {"score": 0.22, "content": "V believes in the 'socialist view of data' - workers should own their career data."}
        ]
        
        print(f"Testing reasoning for: {event.query}")
        result = reasoner.reason_about(event, context)
        if result:
            print(f"\nInference: {result.inference}")
            print(f"Confidence: {result.confidence}")
            print(f"New beliefs: {len(result.new_beliefs)}")
            print(f"Updates: {len(result.belief_updates)}")
        else:
            print("Reasoning not enabled or failed")
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
