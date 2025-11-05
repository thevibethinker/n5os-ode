#!/usr/bin/env python3
"""
Knowledge System V4 - Reflection Knowledge Bridge
Extracts knowledge-worthy insights from daily reflection blocks.

Input: Personal/Reflections/{date}/{block}/
Output: Knowledge/intelligence/extracts/reflection_{date}_{hash}.yaml
"""

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import anthropic
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

WORKSPACE = Path("/home/workspace")
REFLECTIONS_DIR = WORKSPACE / "Personal" / "Reflections"
INTELLIGENCE_DIR = WORKSPACE / "Knowledge" / "intelligence"
EXTRACTS_DIR = INTELLIGENCE_DIR / "extracts"
LOG_DIR = WORKSPACE / "N5" / "logs"

EXTRACTION_PROMPT = """You are extracting knowledge-worthy insights from V's daily reflections.

REFLECTION BLOCK:
{block_content}

EXTRACT:
1. Any predictions, beliefs, or hypotheses
2. Strategic insights or frameworks
3. Market intelligence or competitive observations
4. Novel frameworks or mental models

For each extraction, provide:
- confidence: How certain is this insight? (0-1)
- intelligence_type: [prediction, strategic_insight, market_intelligence, framework, critique]
- summary: One sentence
- details: Full context
- quote: Exact words if applicable
- implications: So what? Why does this matter?
- tags.domain: [relevant domains]
- tags.purpose: [thought_leadership, personal_brand, company_messaging, strategic_approach]
- tags.priority: high | medium | low
- knowledge_routing.target: Which Knowledge/ file should this go to?
- knowledge_routing.section: Which section within that file?

Output valid JSON array of extractions. Each extraction object must include all fields above.
If no knowledge-worthy insights found, return empty array: []
"""


def get_api_client() -> anthropic.Anthropic:
    """Get Anthropic API client."""
    return anthropic.Anthropic()


def scan_reflection_blocks(days: int = 7) -> List[Dict[str, Any]]:
    """
    Scan past N days of reflection blocks.
    
    Returns list of dicts with:
    - date: str (YYYY-MM-DD)
    - block_name: str (R01-R11)
    - content: str
    - path: Path
    """
    if not REFLECTIONS_DIR.exists():
        logging.warning(f"Reflections directory not found: {REFLECTIONS_DIR}")
        return []
    
    blocks = []
    today = datetime.now().date()
    
    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        date_dir = REFLECTIONS_DIR / date_str
        
        if not date_dir.exists():
            continue
        
        # Look for reflection block files
        for block_file in date_dir.rglob("*.md"):
            try:
                content = block_file.read_text()
                block_name = block_file.stem
                
                blocks.append({
                    "date": date_str,
                    "block_name": block_name,
                    "content": content,
                    "path": block_file,
                })
                logging.info(f"Found block: {date_str}/{block_name}")
            except Exception as e:
                logging.error(f"Error reading {block_file}: {e}")
    
    return blocks


def extract_intelligence(client: anthropic.Anthropic, block: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract knowledge-worthy intelligence from reflection block using LLM.
    
    Returns list of extraction dicts (confidence >= 0.50).
    """
    try:
        prompt = EXTRACTION_PROMPT.format(block_content=block["content"])
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}],
        )
        
        response_text = message.content[0].text.strip()
        
        # Parse JSON response
        if response_text.startswith("```json"):
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif response_text.startswith("```"):
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        extractions = json.loads(response_text)
        
        # Filter by confidence threshold
        filtered = [e for e in extractions if e.get("confidence", 0) >= 0.50]
        
        logging.info(f"Extracted {len(extractions)} items, {len(filtered)} above threshold")
        return filtered
        
    except Exception as e:
        logging.error(f"LLM extraction failed for {block['date']}/{block['block_name']}: {e}")
        return []


def write_extraction_yaml(extraction: Dict[str, Any], source_block: Dict[str, Any]) -> Optional[Path]:
    """
    Write extraction to YAML file in intelligence/extracts/.
    
    Returns path to written file, or None on error.
    """
    try:
        # Generate hash for unique filename
        content_hash = hashlib.sha256(extraction["summary"].encode()).hexdigest()[:8]
        filename = f"reflection_{source_block['date']}_{content_hash}.yaml"
        output_path = EXTRACTS_DIR / filename
        
        # Build YAML structure
        yaml_data = {
            "source_type": "reflection",
            "source_id": f"{source_block['date']}_{source_block['block_name']}",
            "captured_at": datetime.now().isoformat(),
            "confidence": extraction["confidence"],
            "status": "pending_review",
            "intelligence_type": extraction.get("intelligence_type", []),
            "entity": {
                "type": "concept",
                "name": extraction.get("summary", "")[:100],
            },
            "content": {
                "summary": extraction.get("summary", ""),
                "details": extraction.get("details", ""),
                "quote": extraction.get("quote", ""),
                "implications": extraction.get("implications", ""),
            },
            "tags": {
                "domain": extraction.get("tags", {}).get("domain", []),
                "purpose": extraction.get("tags", {}).get("purpose", []),
                "priority": extraction.get("tags", {}).get("priority", "medium"),
            },
            "knowledge_routing": {
                "target": extraction.get("knowledge_routing", {}).get("target", ""),
                "action": "append",
                "section": extraction.get("knowledge_routing", {}).get("section", ""),
            },
            "metadata": {
                "processed_by": "reflection_knowledge_bridge.py v1.0",
                "curator_reviewed": False,
                "internalized": False,
            },
        }
        
        with output_path.open("w") as f:
            yaml.safe_dump(yaml_data, f, default_flow_style=False, sort_keys=False)
        
        logging.info(f"Wrote extraction: {output_path}")
        return output_path
        
    except Exception as e:
        logging.error(f"Failed to write extraction: {e}", exc_info=True)
        return None


def main(days: int = 7, dry_run: bool = False) -> int:
    """Main execution."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        EXTRACTS_DIR.mkdir(parents=True, exist_ok=True)
        
        log_file = LOG_DIR / f"reflection_bridge_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)sZ %(levelname)s %(message)s"))
        logging.getLogger().addHandler(file_handler)
        
        logging.info(f"Starting reflection knowledge bridge (days={days}, dry_run={dry_run})")
        
        # Scan reflection blocks
        blocks = scan_reflection_blocks(days=days)
        if not blocks:
            logging.warning("No reflection blocks found")
            return 0
        
        logging.info(f"Found {len(blocks)} reflection blocks")
        
        if dry_run:
            logging.info("DRY RUN: Would process blocks but not write extractions")
            return 0
        
        # Get API client
        client = get_api_client()
        
        # Process each block
        total_extractions = 0
        for block in blocks:
            logging.info(f"Processing {block['date']}/{block['block_name']}")
            
            extractions = extract_intelligence(client, block)
            
            for extraction in extractions:
                output_path = write_extraction_yaml(extraction, block)
                if output_path:
                    total_extractions += 1
        
        logging.info(f"✓ Complete: {total_extractions} extractions written")
        return 0
        
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract knowledge from reflection blocks")
    parser.add_argument("--days", type=int, default=7, help="Number of days to scan (default: 7)")
    parser.add_argument("--dry-run", action="store_true", help="Scan but don't write extractions")
    
    args = parser.parse_args()
    sys.exit(main(days=args.days, dry_run=args.dry_run))
