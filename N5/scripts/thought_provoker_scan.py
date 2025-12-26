#!/usr/bin/env python3
"""
Thought Provoker Scan Script

Scans recently processed inbox items for provocative themes, contradictions,
and synthetic connections. Generates candidates for the Daily Thought Provoker Session.

Usage:
    python3 thought_provoker_scan.py [--input path/to/inbox.json] [--output path/to/candidates.json]
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add N5/scripts to path for imports
sys.path.append(str(Path(__file__).resolve().parent))

try:
    from llm_extractor import LLMExtractor
except ImportError:
    # Fallback or local implementation if needed
    LLMExtractor = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DEFAULT_INBOX_PATH = Path("/home/workspace/N5/data/email_scan_temp.json")
DEFAULT_OUTPUT_PATH = Path("/home/workspace/N5/data/provocation_candidates.json")
PROMPT_PATH = Path("/home/workspace/N5/prompts/extraction/extract_provocations.md")

class ThoughtProvokerScanner:
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.extractor = LLMExtractor(model=model) if LLMExtractor else None
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        if PROMPT_PATH.exists():
            return PROMPT_PATH.read_text()
        return ""

    def load_inbox_data(self, path: Path) -> List[Dict]:
        if not path.exists():
            logger.error(f"Inbox data not found at {path}")
            return []
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return data
        except Exception as e:
            logger.error(f"Failed to load inbox data: {e}")
            return []

    def select_snippets(self, data: List[Dict], limit: int = 20) -> str:
        """Select and format snippets for the LLM"""
        # Prioritize unread or recent (assuming order is recent first)
        selected = data[:limit]
        formatted = []
        for item in selected:
            snippet = {
                "id": item.get("id"),
                "threadId": item.get("threadId"),
                "subject": item.get("subject", "No Subject"),
                "sender": item.get("sender", "Unknown"),
                "content": item.get("body", item.get("snippet", ""))[:500] # Limit per email
            }
            formatted.append(json.dumps(snippet))
        
        return "\n---\n".join(formatted)

    def scan(self, inbox_path: Path) -> Dict[str, Any]:
        if not self.extractor:
            logger.error("LLMExtractor not available")
            return {"provocations": []}

        inbox_data = self.load_inbox_data(inbox_path)
        if not inbox_data:
            return {"provocations": []}

        formatted_inbox = self.select_snippets(inbox_data)
        
        prompt = self.prompt_template.replace("{inbox_data}", formatted_inbox)
        
        # Manually call the extractor's internal method to use our custom prompt
        # (This assumes the extractor has a generic _call_llm method)
        result = self.extractor._call_llm(prompt)
        
        if not result or "provocations" not in result:
            logger.warning("No provocations extracted or invalid format")
            return {"provocations": []}

        # Add metadata
        result["scan_date"] = datetime.utcnow().isoformat()
        result["source_file"] = str(inbox_path)
        
        return result

    def save_candidates(self, result: Dict, output_path: Path):
        try:
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Saved {len(result.get('provocations', []))} candidates to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save candidates: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Thought Provoker Scan")
    parser.add_argument("--input", type=Path, default=DEFAULT_INBOX_PATH, help="Path to inbox JSON data")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Path to save candidates")
    args = parser.parse_args()

    scanner = ThoughtProvokerScanner()
    result = scanner.scan(args.input)
    scanner.save_candidates(result, args.output)

if __name__ == "__main__":
    main()

