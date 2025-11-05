#!/usr/bin/env python3
"""
Knowledge System V4 - Meeting Intelligence Scanner
Extracts knowledge-worthy intelligence from meeting blocks.

Input: Personal/Meetings/{meeting_folder}/blocks/
Output: Knowledge/intelligence/extracts/meeting_{date}_{hash}.yaml
"""

import argparse
import hashlib
import json
import logging
import re
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
MEETINGS_DIR = WORKSPACE / "Personal" / "Meetings"
INTELLIGENCE_DIR = WORKSPACE / "Knowledge" / "intelligence"
EXTRACTS_DIR = INTELLIGENCE_DIR / "extracts"
LOG_DIR = WORKSPACE / "N5" / "logs"

# Block priority classification for knowledge extraction
BLOCK_PRIORITIES = {
    # High Priority - Strategic & Market Intelligence
    "B08": ("high", "Stakeholder Intelligence"),
    "B10": ("high", "Customer Intelligence"),
    "B28": ("high", "Strategic Intelligence (Legacy)"),  # Legacy format
    "B40": ("high", "Internal Decisions"),
    "B42": ("high", "Market & Competitive Intel"),
    "B43": ("high", "Product Intelligence"),
    "B44": ("high", "GTM & Sales Intel"),
    "B48": ("high", "Strategic Memo"),  # New format replacing B28
    
    # Medium Priority - Insights & Coordination
    "B15": ("medium", "Insights"),
    "B21": ("medium", "Key Moments"),
    "B22": ("medium", "Pilot Expansion"),
    "B24": ("medium", "Product Ideas"),
    "B27": ("medium", "Key Messaging"),
    "B41": ("medium", "Team Coordination"),
    "B45": ("medium", "Operations & Process"),
    "B46": ("medium", "Hiring & Team Building"),
    
    # Low Priority - Context & Planning
    "B05": ("low", "Questions Raised"),
    "B07": ("low", "Warm Introductions"),
    "B13": ("low", "Plan of Action"),
    "B14": ("low", "Blurbs & Descriptions"),
    
    # Skip - Operational/Metadata (not knowledge)
    "B01": ("skip", "Detailed Recap"),
    "B02": ("skip", "Commitments"),
    "B25": ("skip", "Deliverables"),
    "B26": ("skip", "Metadata"),
}


def classify_block_priority(block_prefix: str) -> tuple[str, str]:
    """
    Classify a block's priority level for knowledge extraction.
    
    Args:
        block_prefix: Block prefix like "B42", "B48", etc.
        
    Returns:
        Tuple of (priority_level, description)
        - priority_level: "high", "medium", "low", "skip", or "unknown"
        - description: Human-readable block description
    """
    if not block_prefix or not isinstance(block_prefix, str):
        return ("unknown", "Unknown Block")
    
    if block_prefix in BLOCK_PRIORITIES:
        return BLOCK_PRIORITIES[block_prefix]
    
    logging.warning(f"Unknown block prefix: {block_prefix}")
    return ("unknown", "Unknown Block")


# Intelligence blocks to scan
INTELLIGENCE_BLOCKS = [
    "B15_insights",  # Strategic Insights
    "B28_strategic_intelligence",  # Strategic Intelligence
    "B42_market_intel",  # Market Intelligence
    "B43_product_intelligence",  # Product Intelligence
    "B08_stakeholder_intelligence",  # Stakeholder Intelligence
    "B24_product_ideas",  # Product Ideas
    "B48_strategic_memo",  # Strategic Memo
]

EXTRACTION_PROMPT = """You are extracting knowledge-worthy intelligence from meeting blocks.

MEETING: {meeting_title}
DATE: {meeting_date}
ATTENDEES: {attendees}

BLOCK CONTENT:
{block_content}

EXTRACT:
1. Strategic insights (market trends, customer needs, competitive moves)
2. Product insights (feature requests, usability observations)
3. Business model insights (pricing, partnerships, GTM)
4. Contact signals (job changes, warm intro promises, follow-up commitments)

For strategic/product/business insights, provide:
- confidence: How certain is this insight? (0-1)
- intelligence_type: [strategic_insight, product_insight, market_intelligence, business_model, contact_signal]
- entity.type: concept | person | company
- entity.name: Name of the concept/person/company
- entity.email: Email if person and mentioned
- summary: One sentence
- details: Full context
- quote: Exact words if applicable
- implications: So what? Why does this matter?
- tags.domain: [relevant domains]
- tags.purpose: [thought_leadership, personal_brand, company_messaging, strategic_approach]
- tags.priority: high | medium | low
- knowledge_routing.target: Which Knowledge/ file should this go to?
- knowledge_routing.section: Which section within that file?

For contact signals (job changes, warm intros, follow-up), include:
- entity.type: person
- entity.name: Full name
- entity.email: Email if mentioned
- summary: What signal was detected
- knowledge_routing.target: profiles.db

Output valid JSON array of extractions. Each extraction object must include all fields above.
If no knowledge-worthy insights found, return empty array: []
"""


def get_api_client() -> anthropic.Anthropic:
    """Get Anthropic API client."""
    return anthropic.Anthropic()


def parse_meeting_date(meeting_folder: str) -> str:
    """Extract date from meeting folder name (e.g., 'xyz-transcript-2025-11-03T08-34-24.986Z')."""
    match = re.search(r"(\d{4}-\d{2}-\d{2})", meeting_folder)
    if match:
        return match.group(1)
    return datetime.now().strftime("%Y-%m-%d")


def get_meeting_metadata(meeting_dir: Path) -> Dict[str, Any]:
    """Extract meeting metadata from folder name and B26_metadata.md if exists."""
    metadata_file = meeting_dir / "B26_metadata.md"
    
    metadata = {
        "title": meeting_dir.name,
        "date": parse_meeting_date(meeting_dir.name),
        "attendees": "Unknown",
    }
    
    if metadata_file.exists():
        try:
            content = metadata_file.read_text()
            # Try to extract attendees if present
            attendees_match = re.search(r"(?:Attendees|Participants):\s*(.+?)(?:\n|$)", content, re.IGNORECASE)
            if attendees_match:
                metadata["attendees"] = attendees_match.group(1).strip()
        except Exception as e:
            logging.warning(f"Could not read metadata from {metadata_file}: {e}")
    
    return metadata


def discover_meeting_blocks(meeting_dir: Path) -> List[str]:
    """
    Discover which blocks exist in a meeting by reading .processed metadata.
    
    Args:
        meeting_dir: Path to meeting directory
        
    Returns:
        List of block prefixes (e.g., ["B42", "B41", "B13"...])
        Returns empty list if .processed not found or invalid
    """
    processed_file = meeting_dir / ".processed"
    
    if not processed_file.exists():
        logging.warning(f"No .processed file found in {meeting_dir}")
        return []
    
    try:
        with processed_file.open("r") as f:
            data = json.load(f)
        
        blocks_generated = data.get("blocks_generated", [])
        
        # Extract block prefixes by stripping .md extension
        block_prefixes = []
        for block_filename in blocks_generated:
            # Extract prefix (e.g., "B42_market_intel.md" -> "B42")
            if block_filename.endswith(".md"):
                prefix = block_filename.split("_")[0]
                block_prefixes.append(prefix)
        
        return block_prefixes
        
    except json.JSONDecodeError as e:
        logging.warning(f"Invalid JSON in {processed_file}: {e}")
        return []
    except Exception as e:
        logging.warning(f"Error reading {processed_file}: {e}")
        return []


def scan_meeting_blocks(days: int = 7) -> List[Dict[str, Any]]:
    """
    Scan past N days of meeting folders for intelligence blocks.
    
    Returns list of dicts with:
    - meeting_title: str
    - meeting_date: str (YYYY-MM-DD)
    - attendees: str
    - block_name: str
    - content: str
    - path: Path
    """
    if not MEETINGS_DIR.exists():
        logging.warning(f"Meetings directory not found: {MEETINGS_DIR}")
        return []
    
    blocks = []
    cutoff_date = datetime.now().date() - timedelta(days=days)
    
    # Scan all meeting directories
    for meeting_dir in MEETINGS_DIR.iterdir():
        if not meeting_dir.is_dir():
            continue
        
        # Skip special directories
        if meeting_dir.name in [".stfolder", ".stversions", "Inbox"]:
            continue
        
        # Parse meeting date
        meeting_date_str = parse_meeting_date(meeting_dir.name)
        try:
            meeting_date = datetime.strptime(meeting_date_str, "%Y-%m-%d").date()
        except:
            logging.warning(f"Could not parse date from {meeting_dir.name}, skipping")
            continue
        
        # Check if within date range
        if meeting_date < cutoff_date:
            continue
        
        # Get metadata
        metadata = get_meeting_metadata(meeting_dir)
        
        # Scan for intelligence blocks
        for block_prefix in INTELLIGENCE_BLOCKS:
            block_file = meeting_dir / f"{block_prefix}.md"
            
            if not block_file.exists():
                continue
            
            try:
                content = block_file.read_text()
                
                # Skip empty or very short blocks
                if len(content.strip()) < 100:
                    logging.debug(f"Skipping short block: {block_file}")
                    continue
                
                blocks.append({
                    "meeting_title": metadata["title"],
                    "meeting_date": metadata["date"],
                    "attendees": metadata["attendees"],
                    "block_name": block_prefix,
                    "content": content,
                    "path": block_file,
                })
                logging.info(f"Found block: {meeting_dir.name}/{block_prefix}")
                
            except Exception as e:
                logging.error(f"Error reading {block_file}: {e}")
    
    return blocks


def extract_intelligence(client: anthropic.Anthropic, block: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract knowledge-worthy intelligence from meeting block using LLM.
    
    Returns list of extraction dicts (confidence >= 0.65).
    """
    try:
        prompt = EXTRACTION_PROMPT.format(
            meeting_title=block["meeting_title"],
            meeting_date=block["meeting_date"],
            attendees=block["attendees"],
            block_content=block["content"],
        )
        
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
        
        # Filter by confidence threshold (0.65 for meetings vs 0.50 for reflections)
        filtered = [e for e in extractions if e.get("confidence", 0) >= 0.65]
        
        logging.info(f"Extracted {len(extractions)} items, {len(filtered)} above threshold")
        return filtered
        
    except Exception as e:
        logging.error(f"LLM extraction failed for {block['meeting_title']}/{block['block_name']}: {e}")
        return []


def write_extraction_yaml(extraction: Dict[str, Any], source_block: Dict[str, Any]) -> Optional[Path]:
    """
    Write extraction to YAML file in intelligence/extracts/.
    
    Returns path to written file, or None on error.
    """
    try:
        # Generate hash for unique filename
        content_hash = hashlib.sha256(extraction["summary"].encode()).hexdigest()[:8]
        filename = f"meeting_{source_block['meeting_date']}_{content_hash}.yaml"
        output_path = EXTRACTS_DIR / filename
        
        # Build YAML structure
        entity_data = extraction.get("entity", {})
        yaml_data = {
            "source_type": "meeting",
            "source_id": f"{source_block['meeting_title']}_{source_block['block_name']}",
            "captured_at": datetime.now().isoformat(),
            "confidence": extraction["confidence"],
            "status": "pending_review",
            "intelligence_type": extraction.get("intelligence_type", []),
            "entity": {
                "type": entity_data.get("type", "concept"),
                "name": entity_data.get("name", extraction.get("summary", "")[:100]),
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
                "processed_by": "meeting_intelligence_scanner.py v1.0",
                "curator_reviewed": False,
                "internalized": False,
                "meeting_date": source_block["meeting_date"],
                "meeting_title": source_block["meeting_title"],
            },
        }
        
        # Add email if entity is person and email exists
        if entity_data.get("type") == "person" and entity_data.get("email"):
            yaml_data["entity"]["email"] = entity_data["email"]
        
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
        
        log_file = LOG_DIR / f"meeting_scanner_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)sZ %(levelname)s %(message)s"))
        logging.getLogger().addHandler(file_handler)
        
        logging.info(f"Starting meeting intelligence scanner (days={days}, dry_run={dry_run})")
        
        # Scan meeting blocks
        blocks = scan_meeting_blocks(days=days)
        if not blocks:
            logging.warning("No meeting intelligence blocks found")
            return 0
        
        logging.info(f"Found {len(blocks)} meeting intelligence blocks")
        
        if dry_run:
            logging.info("DRY RUN: Would process blocks but not write extractions")
            return 0
        
        # Get API client
        client = get_api_client()
        
        # Process each block
        total_extractions = 0
        for block in blocks:
            logging.info(f"Processing {block['meeting_title']}/{block['block_name']}")
            
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
    parser = argparse.ArgumentParser(description="Extract intelligence from meeting blocks")
    parser.add_argument("--days", type=int, default=7, help="Number of days to scan (default: 7)")
    parser.add_argument("--dry-run", action="store_true", help="Scan but don't write extractions")
    
    args = parser.parse_args()
    sys.exit(main(days=args.days, dry_run=args.dry_run))
