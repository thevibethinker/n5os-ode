#!/usr/bin/env python3
"""
Dependency Graph Visualizer for Session State System

Parses SESSION_STATE.md dependencies and generates D2 diagram.
Shows conversation relationships, data flow, and bottlenecks.

Usage:
  python3 dependency_graph.py --orchestrator con_ORCH_123
  python3 dependency_graph.py --orchestrator con_ORCH_123 --output /path/to/output.d2
  python3 dependency_graph.py --orchestrator con_ORCH_123 --dry-run
"""

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACES_ROOT = Path("/home/.z/workspaces")


@dataclass
class Conversation:
    """Conversation node"""
    id: str
    type: str
    mode: str
    focus: str
    status: str
    depends_on: List[str]
    blocks: List[str]


class DependencyGraphBuilder:
    """Build dependency graph from SESSION_STATE files"""
    
    def __init__(self, orchestrator_id: str, dry_run: bool = False):
        self.orchestrator_id = orchestrator_id
        self.dry_run = dry_run
        self.conversations: Dict[str, Conversation] = {}
    
    def parse_session_state(self, convo_id: str) -> Optional[Conversation]:
        """Parse SESSION_STATE.md for a conversation"""
        state_file = WORKSPACES_ROOT / convo_id / "SESSION_STATE.md"
        
        if not state_file.exists():
            logger.warning(f"SESSION_STATE.md not found for {convo_id}")
            return None
        
        try:
            content = state_file.read_text()
            
            # Extract fields
            type_match = re.search(r"\*\*Primary Type:\*\* (.+)", content)
            mode_match = re.search(r"\*\*Mode:\*\* (.+)", content)
            focus_match = re.search(r"\*\*Focus:\*\* (.+)", content)
            status_match = re.search(r"\*\*Status:\*\* (.+)", content)
            
            conv_type = type_match.group(1).strip() if type_match else "unknown"
            mode = mode_match.group(1).strip() if mode_match else ""
            focus = focus_match.group(1).strip().strip("*") if focus_match else ""
            status = status_match.group(1).strip() if status_match else "active"
            
            # Extract dependencies
            depends_on = []
            blocks = []
            
            # Find Dependencies section
            dep_section_match = re.search(r"## Relationships.*?### Dependencies.*?\*\*Depends on:\*\*(.*?)\*\*Blocks:\*\*(.*?)(?:---|\Z)", content, re.DOTALL)
            
            if dep_section_match:
                depends_text = dep_section_match.group(1)
                blocks_text = dep_section_match.group(2)
                
                # Extract conversation IDs
                depends_on = re.findall(r"con_[A-Za-z0-9_]+", depends_text)
                blocks = re.findall(r"con_[A-Za-z0-9_]+", blocks_text)
            
            return Conversation(
                id=convo_id,
                type=conv_type,
                mode=mode,
                focus=focus,
                status=status,
                depends_on=depends_on,
                blocks=blocks
            )
        
        except Exception as e:
            logger.error(f"Failed to parse {state_file}: {e}")
            return None
    
    def discover_conversations(self) -> None:
        """Discover all related conversations from orchestrator"""
        # Start with orchestrator
        orch_conv = self.parse_session_state(self.orchestrator_id)
        if not orch_conv:
            raise ValueError(f"Could not parse orchestrator {self.orchestrator_id}")
        
        self.conversations[self.orchestrator_id] = orch_conv
        
        # BFS to discover all related conversations
        to_visit = set(orch_conv.depends_on + orch_conv.blocks)
        visited = {self.orchestrator_id}
        
        while to_visit:
            convo_id = to_visit.pop()
            
            if convo_id in visited:
                continue
            
            visited.add(convo_id)
            
            conv = self.parse_session_state(convo_id)
            if conv:
                self.conversations[convo_id] = conv
                to_visit.update(conv.depends_on + conv.blocks)
        
        logger.info(f"Discovered {len(self.conversations)} conversations")
    
    def generate_d2(self) -> str:
        """Generate D2 diagram from conversations"""
        lines = []
        
        # Title
        lines.append("# Session State Dependency Graph")
        lines.append("")
        
        # Define nodes
        for convo_id, conv in self.conversations.items():
            short_id = convo_id.replace("con_", "")
            
            # Node with label
            label = f"{short_id}\\n{conv.type}"
            if conv.mode:
                label += f"\\n{conv.mode}"
            
            lines.append(f"{short_id}: {{")
            lines.append(f"  label: \"{label}\"")
            lines.append(f"  shape: rectangle")
            
            # Color by type
            if conv.type == "build":
                lines.append(f"  style.stroke: \"#4A90E2\"")
                lines.append(f"  style.stroke-width: 2")
            elif conv.type == "research":
                lines.append(f"  style.stroke: \"#7B68EE\"")
                lines.append(f"  style.stroke-width: 2")
            elif conv.type == "planning":
                lines.append(f"  style.stroke: \"#50C878\"")
                lines.append(f"  style.stroke-width: 2")
            elif conv.type == "discussion":
                lines.append(f"  style.stroke: \"#FFA500\"")
                lines.append(f"  style.stroke-width: 2")
            
            # Status indicators
            if conv.status == "complete":
                lines.append(f"  style.opacity: 0.6")
            elif conv.status == "blocked":
                lines.append(f"  style.stroke: \"#FF0000\"")
                lines.append(f"  style.stroke-width: 3")
            
            # Special styling for orchestrator
            if convo_id == self.orchestrator_id:
                lines.append(f"  style.stroke-width: 4")
                lines.append(f"  style.bold: true")
            
            lines.append(f"}}")
            lines.append("")
        
        # Define edges (dependencies)
        for convo_id, conv in self.conversations.items():
            short_id = convo_id.replace("con_", "")
            
            for dep in conv.depends_on:
                if dep in self.conversations:
                    dep_short = dep.replace("con_", "")
                    lines.append(f"{dep_short} -> {short_id}: \"depends on\"")
            
            for blocked in conv.blocks:
                if blocked in self.conversations:
                    blocked_short = blocked.replace("con_", "")
                    lines.append(f"{short_id} -> {blocked_short}: \"blocks\"")
        
        # Legend
        lines.append("")
        lines.append("legend: {")
        lines.append("  near: bottom-right")
        lines.append("  Build: {style.stroke: \"#4A90E2\"; style.stroke-width: 2; shape: rectangle}")
        lines.append("  Research: {style.stroke: \"#7B68EE\"; style.stroke-width: 2; shape: rectangle}")
        lines.append("  Planning: {style.stroke: \"#50C878\"; style.stroke-width: 2; shape: rectangle}")
        lines.append("  Discussion: {style.stroke: \"#FFA500\"; style.stroke-width: 2; shape: rectangle}")
        lines.append("}")
        
        return "\n".join(lines)
    
    def save_d2(self, output_path: Path) -> None:
        """Save D2 diagram to file"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would save D2 to {output_path}")
            return
        
        d2_content = self.generate_d2()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(d2_content)
        
        logger.info(f"✓ Saved D2 diagram: {output_path}")


def main(orchestrator_id: str, output_path: Optional[Path] = None, dry_run: bool = False) -> int:
    """Main entry point"""
    try:
        builder = DependencyGraphBuilder(orchestrator_id, dry_run=dry_run)
        
        logger.info(f"Building dependency graph for {orchestrator_id}")
        
        builder.discover_conversations()
        
        if not output_path:
            output_path = WORKSPACES_ROOT / orchestrator_id / "DEPENDENCY_GRAPH.d2"
        
        builder.save_d2(output_path)
        
        if not dry_run:
            # Print summary
            logger.info(f"Graph contains {len(builder.conversations)} conversations")
            
            # Count by type
            type_counts = defaultdict(int)
            for conv in builder.conversations.values():
                type_counts[conv.type] += 1
            
            for conv_type, count in type_counts.items():
                logger.info(f"  {conv_type}: {count}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Failed to build dependency graph: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate dependency graph from SESSION_STATE files")
    parser.add_argument("--orchestrator", required=True, help="Orchestrator conversation ID")
    parser.add_argument("--output", type=Path, help="Output path for D2 file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    sys.exit(main(args.orchestrator, args.output, args.dry_run))
