#!/usr/bin/env python3
"""
Block Generation Worker

Orchestrates sequential generation of meeting intelligence blocks.
Each block is generated in its own turn with full context and focus.

Workflow:
1. Load meeting transcript and metadata
2. Select relevant blocks based on content
3. Queue blocks to meeting_pipeline.db
4. Generate each block sequentially
5. Update registry as blocks complete
6. Assemble final intelligence.md

Usage:
    python3 worker_generate_blocks.py --meeting-id "2025-11-15_Person1_Person2"
    python3 worker_generate_blocks.py --meeting-path "/path/to/meeting/folder"
"""

import argparse
import json
import logging
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z"
)
logger = logging.getLogger(__name__)

# Constants
BLOCKS_DIR = Path("/home/workspace/N5/prompts/blocks")
DB_PATH = Path("/home/workspace/N5/data/meeting_pipeline.db")
WORKSPACE_ROOT = Path("/home/workspace")


class BlockOrchestrator:
    """Orchestrates sequential block generation for meetings"""
    
    def __init__(self, meeting_path: Path):
        self.meeting_path = meeting_path
        self.meeting_id = meeting_path.name
        self.transcript_path = self._find_transcript()
        self.db_conn = sqlite3.connect(DB_PATH)
        self.db_conn.row_factory = sqlite3.Row
        
    def _find_transcript(self) -> Optional[Path]:
        """Find transcript file in meeting folder"""
        candidates = [
            "transcript.md",
            "transcript.transcript.md",
            f"{self.meeting_id}.transcript.md"
        ]
        
        for candidate in candidates:
            path = self.meeting_path / candidate
            if path.exists():
                return path
        
        # Search for any .transcript.md file
        transcripts = list(self.meeting_path.glob("*.transcript.md"))
        if transcripts:
            return transcripts[0]
        
        logger.error(f"No transcript found in {self.meeting_path}")
        return None
    
    def load_transcript(self) -> str:
        """Load meeting transcript content"""
        if not self.transcript_path:
            raise FileNotFoundError("Transcript not found")
        
        with open(self.transcript_path, 'r') as f:
            return f.read()
    
    def select_blocks(self, transcript: str) -> List[Dict]:
        """
        Select which blocks to generate based on meeting content.
        
        Returns list of block definitions with:
        - block_code: B##
        - block_name: NAME
        - priority: 0-100
        - category: core/recommended/contextual
        """
        # Core blocks - always generate
        selected = [
            {"block_code": "B01", "block_name": "DETAILED_RECAP", "priority": 100, "category": "core"},
            {"block_code": "B02", "block_name": "COMMITMENTS", "priority": 95, "category": "core"},
            {"block_code": "B26", "block_name": "MEETING_METADATA", "priority": 90, "category": "core"},
        ]
        
        # Recommended blocks - usually generate
        selected.extend([
            {"block_code": "B03", "block_name": "DECISIONS", "priority": 80, "category": "recommended"},
            {"block_code": "B05", "block_name": "ACTION_ITEMS", "priority": 75, "category": "recommended"},
            {"block_code": "B21", "block_name": "KEY_MOMENTS", "priority": 70, "category": "recommended"},
        ])
        
        # Contextual blocks - generate based on content
        transcript_lower = transcript.lower()
        
        # Check for technical content
        if any(word in transcript_lower for word in ["technical", "architecture", "implementation", "api", "database", "code"]):
            selected.append({"block_code": "B11", "block_name": "TECHNICAL_DETAILS", "priority": 65, "category": "contextual"})
        
        # Check for business/strategy
        if any(word in transcript_lower for word in ["strategy", "business model", "revenue", "market", "competition"]):
            selected.append({"block_code": "B06", "block_name": "BUSINESS_CONTEXT", "priority": 60, "category": "contextual"})
        
        # Check for stakeholder discussion
        if len(transcript_lower.split()) > 500:  # Substantial meeting
            selected.append({"block_code": "B08", "block_name": "STAKEHOLDER_INTELLIGENCE", "priority": 55, "category": "contextual"})
        
        # Check for open questions
        if "?" in transcript or "question" in transcript_lower:
            selected.append({"block_code": "B04", "block_name": "OPEN_QUESTIONS", "priority": 50, "category": "contextual"})
        
        # Check for deliverables
        if any(word in transcript_lower for word in ["send", "deliver", "email", "follow up", "deck", "document"]):
            selected.append({"block_code": "B25", "block_name": "DELIVERABLES", "priority": 45, "category": "contextual"})
        
        # Check for risks
        if any(word in transcript_lower for word in ["risk", "concern", "worry", "problem", "challenge"]):
            selected.append({"block_code": "B10", "block_name": "RISK_REGISTER", "priority": 40, "category": "contextual"})
        
        # Check for introductions/networking
        if any(word in transcript_lower for word in ["introduce", "connect", "know someone", "meet"]):
            selected.append({"block_code": "B17", "block_name": "WARM_INTROS", "priority": 35, "category": "contextual"})
        
        # Sort by priority
        selected.sort(key=lambda x: x["priority"], reverse=True)
        
        logger.info(f"Selected {len(selected)} blocks for generation")
        for block in selected:
            logger.info(f"  - {block['block_code']}_{block['block_name']} (pri: {block['priority']})")
        
        return selected
    
    def queue_blocks(self, blocks: List[Dict]):
        """Queue blocks to meeting_pipeline.db"""
        cursor = self.db_conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        
        for block in blocks:
            block_id = f"{self.meeting_id}_{block['block_code']}"
            
            cursor.execute("""
                INSERT OR REPLACE INTO blocks 
                (block_id, meeting_id, block_type, status, priority, queued_at)
                VALUES (?, ?, ?, 'pending', ?, ?)
            """, (
                block_id,
                self.meeting_id,
                f"{block['block_code']}_{block['block_name']}",
                block['priority'],
                now
            ))
        
        self.db_conn.commit()
        logger.info(f"Queued {len(blocks)} blocks to registry")
    
    def generate_block(self, block: Dict, transcript: str) -> str:
        """
        Generate a single block using its prompt template.
        
        This is where the LLM generation happens.
        For now, returns a placeholder - will be integrated with LLM API.
        """
        block_code = block['block_code']
        block_name = block['block_name']
        
        # Load block prompt template
        prompt_file = BLOCKS_DIR / f"{block_code}_{block_name}.md"
        
        if not prompt_file.exists():
            logger.warning(f"Prompt template not found: {prompt_file}")
            return f"# {block_code}: {block_name}\n\n[Generation placeholder - prompt template missing]"
        
        with open(prompt_file, 'r') as f:
            block_prompt = f.read()
        
        logger.info(f"Generating {block_code}_{block_name}...")
        
        # TODO: Integrate with LLM API
        # For now, return placeholder
        return f"# {block_code}: {block_name}\n\n[Generated content will appear here]\n\n**Transcript Preview:**\n{transcript[:500]}..."
    
    def update_block_status(self, block: Dict, status: str, content: Optional[str] = None, file_path: Optional[str] = None):
        """Update block status in registry"""
        cursor = self.db_conn.cursor()
        block_id = f"{self.meeting_id}_{block['block_code']}"
        now = datetime.now(timezone.utc).isoformat()
        
        updates = {"status": status}
        
        if status == "generating":
            updates["started_at"] = now
        elif status == "complete":
            updates["completed_at"] = now
            if content:
                updates["content"] = content
                updates["size_bytes"] = len(content.encode('utf-8'))
            if file_path:
                updates["file_path"] = file_path
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [block_id]
        
        cursor.execute(f"UPDATE blocks SET {set_clause} WHERE block_id = ?", values)
        self.db_conn.commit()
    
    def save_block_file(self, block: Dict, content: str) -> Path:
        """Save block content to individual file"""
        block_code = block['block_code']
        block_name = block['block_name']
        filename = f"{block_code}_{block_name}.md"
        file_path = self.meeting_path / filename
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Saved block to {file_path}")
        return file_path
    
    def assemble_intelligence_doc(self, blocks: List[Dict]):
        """Assemble all blocks into intelligence.md"""
        intelligence_path = self.meeting_path / "intelligence.md"
        
        with open(intelligence_path, 'w') as f:
            f.write(f"# Meeting Intelligence: {self.meeting_id}\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}\n\n")
            f.write("---\n\n")
            
            for block in blocks:
                block_file = self.meeting_path / f"{block['block_code']}_{block['block_name']}.md"
                if block_file.exists():
                    with open(block_file, 'r') as bf:
                        content = bf.read()
                        f.write(content)
                        f.write("\n\n---\n\n")
        
        logger.info(f"Assembled intelligence.md at {intelligence_path}")
    
    def run(self):
        """Main orchestration workflow"""
        logger.info(f"Starting block generation for {self.meeting_id}")
        
        # Load transcript
        transcript = self.load_transcript()
        logger.info(f"Loaded transcript: {len(transcript)} chars")
        
        # Select blocks
        blocks = self.select_blocks(transcript)
        
        # Queue blocks
        self.queue_blocks(blocks)
        
        # Generate each block sequentially
        for block in blocks:
            try:
                self.update_block_status(block, "generating")
                
                content = self.generate_block(block, transcript)
                
                file_path = self.save_block_file(block, content)
                
                self.update_block_status(block, "complete", content=content, file_path=str(file_path))
                
            except Exception as e:
                logger.error(f"Failed to generate {block['block_code']}: {e}")
                self.update_block_status(block, "failed")
        
        # Assemble intelligence doc
        self.assemble_intelligence_doc(blocks)
        
        logger.info("Block generation complete!")
        self.db_conn.close()


def main():
    parser = argparse.ArgumentParser(description="Generate meeting intelligence blocks")
    parser.add_argument("--meeting-id", help="Meeting ID (folder name)")
    parser.add_argument("--meeting-path", help="Full path to meeting folder")
    
    args = parser.parse_args()
    
    if args.meeting_path:
        meeting_path = Path(args.meeting_path)
    elif args.meeting_id:
        meeting_path = WORKSPACE_ROOT / "Personal" / "Meetings" / args.meeting_id
    else:
        print("Error: Must provide --meeting-id or --meeting-path")
        return 1
    
    if not meeting_path.exists():
        print(f"Error: Meeting path not found: {meeting_path}")
        return 1
    
    orchestrator = BlockOrchestrator(meeting_path)
    orchestrator.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

