#!/usr/bin/env python3
"""
N5 Query Router — Classifies queries and routes to appropriate retriever.

Routes queries to:
- PageIndex: Document-specific, section-based, "where does it say" queries
- GraphRAG: Entity/relationship queries, "who", "connected to"
- Vector: General semantic search, "find content about"
- Hybrid: Ambiguous queries, combines multiple retrievers

Usage:
    from N5.cognition.query_router import QueryRouter
    
    router = QueryRouter()
    route = router.classify("what does the AISS section say?")
    # Returns: {"mode": "pageindex", "confidence": 0.9, "reasoning": "..."}
"""

import os
import re
import logging
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

LOG = logging.getLogger("query_router")

ZO_ASK_URL = "https://api.zo.computer/zo/ask"


class RouteMode(Enum):
    PAGEINDEX = "pageindex"
    GRAPH = "graph"
    VECTOR = "vector"
    HYBRID = "hybrid"


@dataclass
class RouteDecision:
    mode: RouteMode
    confidence: float
    reasoning: str
    fallback_mode: Optional[RouteMode] = None


# Pattern-based fast classification (before LLM)
PAGEINDEX_PATTERNS = [
    r"what does .+ (section|chapter|part) say",
    r"where does it (say|mention|discuss)",
    r"in (which|what) section",
    r"find the (section|part|chapter) (about|on|discussing)",
    r"what's in the .+ section",
    r"according to (section|chapter|part)",
    r"the .+ framework",  # Named frameworks often have dedicated sections
    r"table of contents",
    r"document structure",
]

GRAPH_PATTERNS = [
    r"who (is|are|knows|works)",
    r"connected to",
    r"relationship (between|with)",
    r"related (to|entities)",
    r"what entities",
    r"people (involved|mentioned|connected)",
    r"organizations? (mentioned|involved)",
    r"network of",
]

VECTOR_PATTERNS = [
    r"find (content|documents|files) (about|on|related)",
    r"search for",
    r"what do (I|we) (know|have) about",
    r"show me .+ (about|on)",
    r"anything (about|on|related)",
]


class QueryRouter:
    """Routes queries to appropriate retrieval systems."""
    
    def __init__(self, use_llm: bool = True):
        """
        Args:
            use_llm: Whether to use LLM for ambiguous queries.
                     If False, relies only on pattern matching.
        """
        self.use_llm = use_llm
        self.token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    
    def classify(self, query: str) -> RouteDecision:
        """
        Classify a query and determine the best retrieval mode.
        
        Args:
            query: Natural language query
            
        Returns:
            RouteDecision with mode, confidence, and reasoning
        """
        query_lower = query.lower()
        
        # Fast path: pattern matching
        pattern_result = self._pattern_classify(query_lower)
        if pattern_result and pattern_result.confidence >= 0.8:
            LOG.debug(f"Pattern match: {pattern_result.mode.value}")
            return pattern_result
        
        # LLM classification for ambiguous queries
        if self.use_llm and self.token:
            llm_result = self._llm_classify(query)
            if llm_result:
                return llm_result
        
        # Fallback: hybrid for ambiguous
        return RouteDecision(
            mode=RouteMode.HYBRID,
            confidence=0.5,
            reasoning="Ambiguous query, using hybrid retrieval",
            fallback_mode=RouteMode.VECTOR
        )
    
    def _pattern_classify(self, query_lower: str) -> Optional[RouteDecision]:
        """Fast classification using regex patterns."""
        
        # Check PageIndex patterns
        for pattern in PAGEINDEX_PATTERNS:
            if re.search(pattern, query_lower):
                return RouteDecision(
                    mode=RouteMode.PAGEINDEX,
                    confidence=0.85,
                    reasoning=f"Matched PageIndex pattern: {pattern}",
                    fallback_mode=RouteMode.VECTOR
                )
        
        # Check Graph patterns
        for pattern in GRAPH_PATTERNS:
            if re.search(pattern, query_lower):
                return RouteDecision(
                    mode=RouteMode.GRAPH,
                    confidence=0.85,
                    reasoning=f"Matched Graph pattern: {pattern}",
                    fallback_mode=RouteMode.VECTOR
                )
        
        # Check Vector patterns
        for pattern in VECTOR_PATTERNS:
            if re.search(pattern, query_lower):
                return RouteDecision(
                    mode=RouteMode.VECTOR,
                    confidence=0.85,
                    reasoning=f"Matched Vector pattern: {pattern}"
                )
        
        return None
    
    def _llm_classify(self, query: str) -> Optional[RouteDecision]:
        """LLM-based classification for ambiguous queries."""
        
        prompt = f"""Classify this search query to determine the best retrieval strategy.

QUERY: "{query}"

RETRIEVAL MODES:
1. **pageindex** — For document-specific queries where the answer is in a specific section
   - "What does section X say about Y?"
   - "Where is the part about Z?"
   - Looking for specific frameworks, methodologies, structured content
   
2. **graph** — For entity and relationship queries
   - "Who is connected to X?"
   - "What organizations work with Y?"
   - Entity names, people, relationships
   
3. **vector** — For general semantic search
   - "Find content about X"
   - "What do we know about Y?"
   - Broad topic searches
   
4. **hybrid** — When multiple strategies might help
   - Ambiguous queries
   - Complex multi-part questions

Respond with JSON:
{{
    "mode": "pageindex|graph|vector|hybrid",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation"
}}"""

        try:
            response = requests.post(
                ZO_ASK_URL,
                headers={
                    "authorization": self.token,
                    "content-type": "application/json"
                },
                json={
                    "input": prompt,
                    "output_format": {
                        "type": "object",
                        "properties": {
                            "mode": {"type": "string", "enum": ["pageindex", "graph", "vector", "hybrid"]},
                            "confidence": {"type": "number"},
                            "reasoning": {"type": "string"}
                        },
                        "required": ["mode", "confidence", "reasoning"]
                    }
                },
                timeout=15
            )
            
            if response.status_code != 200:
                LOG.error(f"LLM classification failed: {response.status_code}")
                return None
            
            result = response.json()["output"]
            
            mode_map = {
                "pageindex": RouteMode.PAGEINDEX,
                "graph": RouteMode.GRAPH,
                "vector": RouteMode.VECTOR,
                "hybrid": RouteMode.HYBRID
            }
            
            return RouteDecision(
                mode=mode_map.get(result["mode"], RouteMode.HYBRID),
                confidence=result["confidence"],
                reasoning=result["reasoning"],
                fallback_mode=RouteMode.VECTOR if result["mode"] != "vector" else None
            )
            
        except Exception as e:
            LOG.error(f"LLM classification error: {e}")
            return None
    
    def explain(self, query: str) -> str:
        """Get a human-readable explanation of routing decision."""
        decision = self.classify(query)
        
        return f"""Query: "{query}"
Route: {decision.mode.value}
Confidence: {decision.confidence:.0%}
Reasoning: {decision.reasoning}
Fallback: {decision.fallback_mode.value if decision.fallback_mode else 'None'}"""


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Query Router CLI")
    parser.add_argument("query", help="Query to classify")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM classification")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    router = QueryRouter(use_llm=not args.no_llm)
    print(router.explain(args.query))
