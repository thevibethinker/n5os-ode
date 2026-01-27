#!/usr/bin/env python3
"""Classify incoming messages as task types."""

import json
import argparse

TASK_TYPES = ["code_build", "research", "content", "analysis", "hybrid"]

def classify_heuristic(message: str) -> dict:
    """Fast heuristic classification (no API call)."""
    message_lower = message.lower()
    
    # Code/build signals
    code_signals = ["build", "script", "implement", "create a", "automation", "code", "deploy", "fix", "debug"]
    # Research signals
    research_signals = ["research", "find out", "look into", "investigate", "due diligence", "market", "competitor"]
    # Content signals
    content_signals = ["write", "draft", "intro", "email", "post", "blog", "content", "newsletter", "announcement"]
    # Analysis signals
    analysis_signals = ["analyze", "review", "assess", "evaluate", "summary", "report on", "synthesize"]
    
    scores = {
        "code_build": sum(1 for s in code_signals if s in message_lower),
        "research": sum(1 for s in research_signals if s in message_lower),
        "content": sum(1 for s in content_signals if s in message_lower),
        "analysis": sum(1 for s in analysis_signals if s in message_lower)
    }
    
    max_score = max(scores.values())
    if max_score == 0:
        return {"type": "hybrid", "confidence": 0.5, "method": "heuristic"}
    
    best_type = max(scores, key=scores.get)
    confidence = min(0.9, 0.5 + (max_score * 0.1))
    
    return {"type": best_type, "confidence": confidence, "method": "heuristic"}

def classify(message: str, use_llm: bool = False) -> dict:
    """Classify a message."""
    # For now, always use heuristic - LLM can be added later if needed
    result = classify_heuristic(message)
    print(json.dumps(result))
    return result

def main():
    parser = argparse.ArgumentParser(description="Task Classifier")
    parser.add_argument("message", help="Message to classify")
    parser.add_argument("--llm", action="store_true", help="Use LLM for classification (future)")
    
    args = parser.parse_args()
    if args.llm:
        print(json.dumps({"error": "LLM classification not implemented yet. Use heuristic mode."}))
    else:
        classify(args.message, args.llm)

if __name__ == "__main__":
    main()
