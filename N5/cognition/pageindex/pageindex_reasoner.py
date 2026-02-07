#!/usr/bin/env python3
"""
PageIndex Reasoner — LLM-based tree navigation for precise retrieval.

Given a query and a document tree, uses LLM reasoning to navigate
to the most relevant nodes (instead of vector similarity matching).

Usage:
    from N5.cognition.pageindex.pageindex_reasoner import PageIndexReasoner
    
    reasoner = PageIndexReasoner()
    result = reasoner.navigate(query, tree_json)
"""

import json
import os
import logging
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path

LOG = logging.getLogger("pageindex_reasoner")

ZO_ASK_URL = "https://api.zo.computer/zo/ask"


class PageIndexReasoner:
    """Navigate document trees using LLM reasoning."""
    
    def __init__(self):
        self.token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
        if not self.token:
            LOG.warning("ZO_CLIENT_IDENTITY_TOKEN not set, using OpenAI fallback")
    
    def navigate(self, query: str, tree: Dict, return_content: bool = True) -> Dict:
        """
        Navigate a document tree to find nodes relevant to a query.
        
        Args:
            query: Natural language query
            tree: PageIndex tree structure
            return_content: Whether to extract content from identified nodes
            
        Returns:
            {
                "nodes": [list of relevant node indices],
                "reasoning": "explanation of navigation path",
                "answer": "synthesized answer if return_content=True"
            }
        """
        # Format tree for LLM consumption
        tree_description = self._format_tree_for_llm(tree)
        
        prompt = f"""You are analyzing a document using its hierarchical structure.

DOCUMENT STRUCTURE:
{tree_description}

QUERY: {query}

TASK:
1. Examine the document structure above
2. Identify which section(s) are most likely to contain information relevant to the query
3. Explain your reasoning for choosing those sections

Respond in this JSON format:
{{
    "relevant_nodes": ["0001", "0002.1"],  // node indices that are relevant
    "reasoning": "Section X is relevant because...",
    "confidence": 0.85  // 0-1 confidence score
}}

Focus on precision — only include nodes that are clearly relevant to the query."""

        try:
            if self.token:
                # Use Zo API
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
                                "relevant_nodes": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "reasoning": {"type": "string"},
                                "confidence": {"type": "number"}
                            },
                            "required": ["relevant_nodes", "reasoning", "confidence"]
                        }
                    },
                    timeout=30
                )
                
                if response.status_code != 200:
                    LOG.error(f"Zo API error: {response.status_code}")
                    return self._fallback_response(query, tree)
                
                result = response.json()["output"]
                
            else:
                # Fallback to OpenAI directly
                result = self._call_openai(prompt)
            
            return {
                "nodes": result.get("relevant_nodes", []),
                "reasoning": result.get("reasoning", ""),
                "confidence": result.get("confidence", 0.5),
                "tree_doc": tree.get("doc_name", "unknown")
            }
            
        except Exception as e:
            LOG.error(f"Navigation failed: {e}")
            return self._fallback_response(query, tree)
    
    def _format_tree_for_llm(self, tree: Dict) -> str:
        """Format tree structure as readable text for LLM."""
        lines = []
        doc_name = tree.get("doc_name", "Document")
        lines.append(f"# {doc_name}")
        
        if tree.get("summary"):
            lines.append(f"Summary: {tree['summary'][:200]}...")
        
        lines.append("\nSections:")
        
        def format_node(node: Dict, indent: int = 0):
            prefix = "  " * indent
            index = node.get("node_index", "?")
            title = node.get("title", "Untitled")
            summary = node.get("summary", "")[:100]
            
            line = f"{prefix}[{index}] {title}"
            if summary:
                line += f" — {summary}"
            lines.append(line)
            
            for child in node.get("nodes", []):
                format_node(child, indent + 1)
        
        for node in tree.get("structure", []):
            format_node(node)
        
        return "\n".join(lines)
    
    def _call_openai(self, prompt: str) -> Dict:
        """Fallback to direct OpenAI call."""
        import openai
        
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _fallback_response(self, query: str, tree: Dict) -> Dict:
        """Fallback when LLM navigation fails."""
        # Return root-level nodes
        root_nodes = [
            node.get("node_index", str(i)) 
            for i, node in enumerate(tree.get("structure", []))
        ]
        
        return {
            "nodes": root_nodes[:3],
            "reasoning": "Fallback: returning top-level sections",
            "confidence": 0.3,
            "tree_doc": tree.get("doc_name", "unknown")
        }
    
    def multi_doc_navigate(self, query: str, trees: List[Dict]) -> List[Dict]:
        """
        Navigate across multiple document trees.
        
        Args:
            query: Natural language query
            trees: List of PageIndex tree structures
            
        Returns:
            List of navigation results, sorted by confidence
        """
        results = []
        
        for tree in trees:
            result = self.navigate(query, tree)
            if result["confidence"] > 0.3:  # Filter low confidence
                results.append(result)
        
        # Sort by confidence
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        return results


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PageIndex Reasoner CLI")
    parser.add_argument("--tree-file", required=True, help="Path to tree JSON")
    parser.add_argument("--query", required=True, help="Query to navigate")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    with open(args.tree_file) as f:
        tree = json.load(f)
    
    reasoner = PageIndexReasoner()
    result = reasoner.navigate(args.query, tree)
    
    print(f"Relevant nodes: {result['nodes']}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"Confidence: {result['confidence']}")
