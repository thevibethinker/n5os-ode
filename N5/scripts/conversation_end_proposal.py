#!/usr/bin/env python3
"""
Conversation-End Proposal Generator
Transforms analysis JSON into human-readable proposals

Part of conversation-end orchestrator system (Worker 2)
Orchestrator: con_O4rpz6MPrQXLbOlX
"""

import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class ProposalGenerator:
    """Generate human-readable proposals from analysis JSON"""
    
    def __init__(self, analysis: Dict[str, Any]):
        self.analysis = analysis
        self.convo = analysis["conversation"]
        self.data = analysis["analysis"]
        self.actions = analysis["proposed_actions"]
    
    def generate_markdown(self) -> str:
        """Generate human-readable markdown proposal"""
        sections = [
            self._header(),
            self._title_section(),
            self._summary(),
            self._actions_grouped(),
            self._conflicts_section(),
            self._review_footer()
        ]
        return "\n\n---\n\n".join(filter(None, sections))
    
    def generate_json(self) -> str:
        """Generate executable JSON proposal with approval metadata"""
        executable = {
            "conversation_id": self.convo["id"],
            "title": self.convo["proposed_title"],
            "generated_at": datetime.now().isoformat(),
            "actions": [
                {
                    **action,
                    "approved": False,
                    "execution_status": "pending"
                }
                for action in self.actions
            ],
            "conflicts": self.data["conflicts"],
            "requires_resolution": len(self.data["conflicts"]) > 0
        }
        return json.dumps(executable, indent=2)
    
    def generate_interactive(self) -> str:
        """Generate terminal UI for interactive selection"""
        lines = ["# Conversation End - Action Selection\n"]
        lines.append(f"**Conversation:** {self.convo['id']}")
        lines.append(f"**Title:** {self.convo['proposed_title']}\n")
        
        if self.data["conflicts"]:
            lines.append("⚠️  **Conflicts detected - must resolve before execution**\n")
        
        lines.append("## Actions to Execute:\n")
        
        for idx, action in enumerate(self.actions, 1):
            if action["action_type"] == "ignore":
                continue
            
            source = Path(action["source"])
            dest = Path(action["destination"]) if action["destination"] else None
            
            # Checkboxes for terminal
            checkbox = "[✓]" if action["confidence"] == "high" else "[ ]"
            
            action_desc = f"{action['action_type'].title()} {source.name}"
            if dest:
                dest_short = self._shorten_path(dest)
                action_desc += f" → {dest_short}"
            
            lines.append(f"{checkbox} {idx}. {action_desc}")
            lines.append(f"    *{action['reason']}*")
            lines.append("")
        
        lines.append("\n**Instructions:**")
        lines.append("- [✓] = Auto-approved (high confidence)")
        lines.append("- [ ] = Review recommended (medium/low confidence)")
        lines.append("- Edit JSON proposal to modify approval flags")
        lines.append(f"- Run: `python3 N5/scripts/conversation_end_executor.py --proposal <file> --dry-run`")
        
        return "\n".join(lines)
    
    def _header(self) -> str:
        """Generate header section"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M ET")
        return f"""# Conversation End Proposal

**Conversation:** {self.convo['id']}  
**Generated:** {timestamp}  
**Workspace:** `{self.convo['workspace_path']}`"""
    
    def _title_section(self) -> str:
        """Generate title proposal"""
        source_desc = {
            "session_state": "SESSION_STATE.md (Objective field)",
            "aar": "After-Action Report",
            "file": "Largest file in workspace",
            "fallback": "Date-based fallback"
        }.get(self.convo["title_source"], "Unknown")
        
        return f"""## Proposed Title

**✓ "{self.convo['proposed_title']}"**

*Source: {source_desc}*"""
    
    def _summary(self) -> str:
        """Generate summary stats"""
        classified = self.data["classified"]
        total_actions = sum(len(v) for k, v in classified.items() if k != "ignore")
        
        return f"""## Summary

- **Total Files:** {self.data['total_files']}
- **To Move:** {len(classified['deliverables'])} deliverables
- **To Archive:** {len(classified['finals'])} finals, {len(classified['temp'])} temp
- **To Ignore:** {len(classified['ignore'])}
- **Total Actions:** {total_actions}"""
    
    def _actions_grouped(self) -> str:
        """Group and format actions by type"""
        groups = {
            "move": [],
            "archive": [],
            "ignore": []
        }
        
        for action in self.actions:
            groups[action["action_type"]].append(action)
        
        sections = []
        
        # Deliverables → User Workspace
        if groups["move"]:
            section = ["## Actions\n", "### 1. Deliverables → User Workspace\n"]
            for action in groups["move"]:
                section.append(self._format_action(action))
            sections.append("\n".join(section))
        
        # Finals → Archive
        archive_finals = [a for a in groups["archive"] if "scratch" not in a["destination"]]
        if archive_finals:
            section = ["### 2. Final Work Products → Archive\n"]
            for action in archive_finals:
                section.append(self._format_action(action))
            sections.append("\n".join(section))
        
        # Temp → Archive/scratch
        archive_temp = [a for a in groups["archive"] if "scratch" in a["destination"]]
        if archive_temp:
            section = ["### 3. Temporary Files → Archive/scratch\n"]
            for action in archive_temp:
                section.append(self._format_action(action))
            sections.append("\n".join(section))
        
        # Ignore
        if groups["ignore"]:
            section = ["### 4. Files to Ignore (leave in place)\n"]
            for action in groups["ignore"][:5]:  # Limit display
                source = Path(action["source"])
                section.append(f"- **{source.name}** — *{action['reason']}*")
            
            if len(groups["ignore"]) > 5:
                section.append(f"- *...and {len(groups['ignore']) - 5} more*")
            
            sections.append("\n".join(section))
        
        return "\n\n".join(sections)
    
    def _format_action(self, action: Dict[str, Any]) -> str:
        """Format a single action for display"""
        source = Path(action["source"])
        dest = Path(action["destination"]) if action["destination"] else None
        
        confidence_icon = {
            "high": "✓",
            "medium": "◆",
            "low": "⚠"
        }.get(action["confidence"], "•")
        
        lines = [f"**{confidence_icon} {source.name}**"]
        
        if dest:
            dest_short = self._shorten_path(dest)
            lines.append(f"  → `{dest_short}`")
        
        lines.append(f"  *Reason: {action['reason']}*")
        
        if action.get("impacts"):
            lines.append(f"  *Impact: {', '.join(action['impacts'])}*")
        
        return "\n".join(lines) + "\n"
    
    def _conflicts_section(self) -> str:
        """Format conflicts with resolution options"""
        if not self.data["conflicts"]:
            return None
        
        section = [f"## ⚠️ Conflicts Detected ({len(self.data['conflicts'])})\n"]
        
        for conflict in self.data["conflicts"]:
            severity_icon = "🛑" if conflict["severity"] == "error" else "⚠️"
            section.append(f"**{severity_icon} {conflict['type'].replace('_', ' ').title()}**")
            section.append(f"{conflict['description']}")
            section.append(f"*Affected: {', '.join(Path(f).name for f in conflict['affected_files'])}*")
            
            if conflict["type"] == "overwrite":
                section.append("\n**Resolution Options:**")
                section.append("- Rename destination file before execution")
                section.append("- Skip this action (remove from proposal)")
                section.append("- Backup existing file first (recommended)")
            
            section.append("")
        
        section.append("**⚠️ Conflicts must be resolved before execution.**")
        
        return "\n".join(section)
    
    def _review_footer(self) -> str:
        """Add review instructions"""
        has_conflicts = len(self.data["conflicts"]) > 0
        
        footer = ["## Next Steps\n"]
        
        if has_conflicts:
            footer.append("1. **Resolve conflicts** (see above)")
            footer.append("2. Edit proposal JSON to adjust actions")
            footer.append("3. Run dry-run to preview")
        else:
            footer.append("1. Review proposed actions above")
            footer.append("2. Edit proposal JSON if needed")
            footer.append("3. Run dry-run to preview")
        
        footer.append("\n**Dry-Run Command:**")
        footer.append("```bash")
        footer.append("python3 N5/scripts/conversation_end_executor.py \\")
        footer.append("  --proposal /path/to/proposal.json \\")
        footer.append("  --dry-run")
        footer.append("```")
        
        if self.data.get("warnings"):
            footer.append("\n**Warnings:**")
            for warning in self.data["warnings"]:
                footer.append(f"- ⚠️  {warning}")
        
        return "\n".join(footer)
    
    def _shorten_path(self, path: Path) -> str:
        """Shorten path for display"""
        path_str = str(path)
        workspace = "/home/workspace/"
        
        if path_str.startswith(workspace):
            return path_str[len(workspace):]
        
        return path_str


def generate_demo() -> int:
    """Generate demo proposal with mock data"""
    logger.info("Generating demo proposal...")
    
    mock_analysis = {
        "conversation": {
            "id": "con_DEMO0000000000",
            "proposed_title": "Oct 27 | System Design Workflow",
            "title_source": "session_state",
            "workspace_path": "/home/.z/workspaces/con_DEMO0000000000"
        },
        "analysis": {
            "total_files": 12,
            "classified": {
                "deliverables": ["DELIVERABLE_report.md", "README.md"],
                "finals": ["FINAL_output.md", "analysis.md", "notes.md"],
                "temp": ["TEMP_draft.md", "test_v2.py", "scratch.txt"],
                "ignore": ["SESSION_STATE.md", ".git/config", "CONTEXT.md"]
            },
            "conflicts": [
                {
                    "type": "overwrite",
                    "description": "Destination file already exists: /home/workspace/Documents/report.md",
                    "affected_files": [
                        "/home/.z/workspaces/con_DEMO/DELIVERABLE_report.md",
                        "/home/workspace/Documents/report.md"
                    ],
                    "severity": "error"
                }
            ],
            "warnings": []
        },
        "proposed_actions": [
            {
                "action_type": "move",
                "source": "/home/.z/workspaces/con_DEMO/DELIVERABLE_report.md",
                "destination": "/home/workspace/Documents/report.md",
                "reason": "Deliverable file for user workspace",
                "confidence": "high",
                "impacts": []
            },
            {
                "action_type": "move",
                "source": "/home/.z/workspaces/con_DEMO/README.md",
                "destination": "/home/workspace/Documents/README.md",
                "reason": "Documentation deliverable",
                "confidence": "high",
                "impacts": []
            },
            {
                "action_type": "archive",
                "source": "/home/.z/workspaces/con_DEMO/FINAL_output.md",
                "destination": "/home/workspace/Documents/Archive/2025-10-27_con-DEMO/FINAL_output.md",
                "reason": "Final work product for archive",
                "confidence": "high",
                "impacts": []
            },
            {
                "action_type": "archive",
                "source": "/home/.z/workspaces/con_DEMO/TEMP_draft.md",
                "destination": "/home/workspace/Documents/Archive/2025-10-27_con-DEMO/scratch/TEMP_draft.md",
                "reason": "Temporary file for scratch archive",
                "confidence": "medium",
                "impacts": []
            },
            {
                "action_type": "ignore",
                "source": "/home/.z/workspaces/con_DEMO/SESSION_STATE.md",
                "destination": "",
                "reason": "System file to leave in place",
                "confidence": "high",
                "impacts": []
            }
        ]
    }
    
    generator = ProposalGenerator(mock_analysis)
    
    print("\n" + "="*60)
    print("MARKDOWN FORMAT")
    print("="*60 + "\n")
    print(generator.generate_markdown())
    
    print("\n" + "="*60)
    print("INTERACTIVE FORMAT")
    print("="*60 + "\n")
    print(generator.generate_interactive())
    
    print("\n" + "="*60)
    print("JSON FORMAT (excerpt)")
    print("="*60 + "\n")
    json_output = json.loads(generator.generate_json())
    print(json.dumps(json_output, indent=2)[:500] + "...")
    
    logger.info("✓ Demo generation complete")
    return 0


def main(
    analysis_path: str = None,
    format: str = "markdown",
    output: str = None,
    demo: bool = False
) -> int:
    """Main entry point"""
    try:
        if demo:
            return generate_demo()
        
        if not analysis_path:
            logger.error("Error: --analysis required (or use --demo)")
            return 1
        
        analysis_file = Path(analysis_path)
        if not analysis_file.exists():
            logger.error(f"Analysis file not found: {analysis_path}")
            return 1
        
        logger.info(f"Loading analysis from {analysis_path}")
        analysis = json.loads(analysis_file.read_text())
        
        generator = ProposalGenerator(analysis)
        
        if format == "markdown":
            result = generator.generate_markdown()
        elif format == "json":
            result = generator.generate_json()
        elif format == "interactive":
            result = generator.generate_interactive()
        else:
            logger.error(f"Unknown format: {format}")
            return 1
        
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result)
            logger.info(f"✓ Proposal written: {output}")
        else:
            print(result)
        
        logger.info(f"✓ Generated {format} proposal")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate human-readable proposals from conversation-end analysis"
    )
    parser.add_argument(
        "--analysis",
        help="Path to analysis JSON from conversation_end_analyzer.py"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "interactive"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Generate demo proposal with mock data"
    )
    
    args = parser.parse_args()
    
    exit(main(
        analysis_path=args.analysis,
        format=args.format,
        output=args.output,
        demo=args.demo
    ))
