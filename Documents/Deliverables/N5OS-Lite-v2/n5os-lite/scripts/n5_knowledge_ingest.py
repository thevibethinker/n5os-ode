#!/usr/bin/env python3
"""
N5 Knowledge Ingest Script

Ingests chunks of biographical, historical, or strategic information,
analyzes them with LLM processing, breaks them into components,
and stores across knowledge reservoirs.

Append-only updates for facts, glossary, timeline, sources.
Controlled overwrites for bio and company files.
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
import uuid
import asyncio

# Paths
WORKSPACE = Path("/home/workspace")
KNOWLEDGE_DIR = WORKSPACE / "Knowledge"
STABLE_DIR = KNOWLEDGE_DIR / "stable"
FACTS_FILE = KNOWLEDGE_DIR / "facts.jsonl"

def ensure_dirs():
    """Ensure all required directories exist."""
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    STABLE_DIR.mkdir(parents=True, exist_ok=True)

def append_fact(fact: dict) -> None:
    """Append a fact to the facts JSONL file."""
    fact["id"] = str(uuid.uuid4())[:8]
    fact["ingested_at"] = datetime.now(timezone.utc).isoformat()
    
    with open(FACTS_FILE, "a") as f:
        f.write(json.dumps(fact) + "\n")
    
    print(f"  ✓ Added fact: {fact.get('summary', fact.get('content', ''))[:60]}...")

def ingest_text(text: str, source: str = "manual", category: str = "general") -> dict:
    """
    Ingest a text chunk into the knowledge system.
    
    In a full implementation, this would:
    1. Send to LLM for analysis and categorization
    2. Extract facts, entities, relationships
    3. Store in appropriate reservoirs
    
    For now, stores as a raw fact for later processing.
    """
    ensure_dirs()
    
    fact = {
        "content": text,
        "source": source,
        "category": category,
        "status": "pending_analysis"
    }
    
    append_fact(fact)
    
    return {
        "status": "ingested",
        "fact_id": fact.get("id"),
        "next_step": "Run LLM analysis to extract structured knowledge"
    }

def main():
    parser = argparse.ArgumentParser(
        description="Ingest knowledge into the N5 system"
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to ingest (or use --file)"
    )
    parser.add_argument(
        "--file", "-f",
        help="File containing text to ingest"
    )
    parser.add_argument(
        "--source", "-s",
        default="manual",
        help="Source of the knowledge (e.g., 'meeting', 'research', 'manual')"
    )
    parser.add_argument(
        "--category", "-c",
        default="general",
        help="Category (e.g., 'bio', 'company', 'market', 'technical')"
    )
    
    args = parser.parse_args()
    
    # Get text from argument or file
    if args.file:
        text = Path(args.file).read_text()
    elif args.text:
        text = args.text
    else:
        print("Error: Provide text as argument or use --file")
        sys.exit(1)
    
    result = ingest_text(text, source=args.source, category=args.category)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
