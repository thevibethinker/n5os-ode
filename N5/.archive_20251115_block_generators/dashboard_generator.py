#!/usr/bin/env python3
"""
Dashboard Generator
Generates REVIEW_FIRST.md executive summary dashboard.
"""
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def generate_dashboard(
    meeting_id: str,
    meeting_info: Dict[str, Any],
    blocks_generated: List[str],
    metadata: Dict[str, Any],
    output_dir: Path
) -> bool:
    """
    Generate REVIEW_FIRST.md dashboard from meeting outputs.
    
    Args:
        meeting_id: Unique meeting identifier
        meeting_info: Extracted meeting metadata
        blocks_generated: List of successfully generated block names
        metadata: Meeting processing metadata
        output_dir: Directory to write output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Generating meeting dashboard")
        
        # Read generated blocks
        action_items = _read_file(output_dir / "action-items.md")
        decisions = _read_file(output_dir / "decisions.md")
        insights = _read_file(output_dir / "detailed-notes.md")
        
        # Extract top items
        top_actions = _extract_top_actions(action_items, 4)
        top_decisions = _extract_top_decisions(decisions, 3)
        top_insights = _extract_top_insights(insights, 3)
        
        # Generate executive summary
        exec_summary = _generate_exec_summary(meeting_info, metadata)
        
        # Generate markdown
        markdown = _generate_markdown(
            meeting_info, exec_summary, top_actions, 
            top_decisions, top_insights, blocks_generated, metadata
        )
        
        # Write output
        output_path = output_dir / "REVIEW_FIRST.md"
        output_path.write_text(markdown, encoding='utf-8')
        
        logger.info("Generated meeting dashboard")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate dashboard: {e}", exc_info=True)
        return False


def _read_file(path: Path) -> str:
    """Read file content, return empty string if not exists."""
    try:
        return path.read_text(encoding='utf-8')
    except:
        return ""


def _extract_top_actions(content: str, limit: int) -> List[str]:
    """Extract top N action items from action-items.md."""
    actions = []
    lines = content.split('\n')
    
    for line in lines:
        if line.strip().startswith('- [ ] **'):
            # Extract action description
            action = line.strip()[9:]  # Remove '- [ ] **'
            if '**' in action:
                action = action[:action.index('**')]
            actions.append(action)
            if len(actions) >= limit:
                break
    
    return actions


def _extract_top_decisions(content: str, limit: int) -> List[Dict[str, str]]:
    """Extract top N decisions from decisions.md."""
    decisions = []
    lines = content.split('\n')
    
    current_decision = None
    for line in lines:
        if line.startswith('### '):
            if current_decision and len(decisions) < limit:
                decisions.append(current_decision)
            current_decision = {"title": line[4:].strip()}
        elif line.startswith('**Decision**:') and current_decision:
            current_decision["content"] = line[13:].strip()
    
    if current_decision and len(decisions) < limit:
        decisions.append(current_decision)
    
    return decisions[:limit]


def _extract_top_insights(content: str, limit: int) -> List[Dict[str, str]]:
    """Extract top N insights from detailed-notes.md."""
    insights = []
    lines = content.split('\n')
    
    for line in lines:
        if line.strip().startswith('**') and ':' in line:
            # Speaker: content format
            parts = line.split(':', 1)
            if len(parts) == 2:
                speaker = parts[0].strip('* ')
                content = parts[1].strip()
                if len(content) > 50:  # Substantive content
                    insights.append({
                        "speaker": speaker,
                        "content": content[:200]
                    })
                if len(insights) >= limit:
                    break
    
    return insights


def _generate_exec_summary(meeting_info: Dict, metadata: Dict) -> str:
    """Generate executive summary text."""
    stakeholder = meeting_info.get('stakeholder_primary', 'Unknown')
    date = meeting_info.get('date', 'Unknown Date')
    duration = meeting_info.get('duration_minutes', 0)
    
    summary = f"Meeting with {stakeholder} on {date}"
    if duration:
        summary += f" ({duration} minutes)"
    
    return summary


def _generate_markdown(
    meeting_info: Dict,
    exec_summary: str,
    top_actions: List[str],
    top_decisions: List[Dict],
    top_insights: List[Dict],
    blocks_generated: List[str],
    metadata: Dict
) -> str:
    """Generate full dashboard markdown."""
    stakeholder = meeting_info.get('stakeholder_primary', 'Unknown')
    date = meeting_info.get('date', 'Unknown Date')
    duration = meeting_info.get('duration_minutes', 'Unknown')
    
    md = "# 📊 Meeting Review Dashboard\n"
    md += f"## {stakeholder}\n"
    md += f"**Date**: {date} | **Duration**: {duration} min\n\n"
    md += "---\n\n"
    
    # Executive Summary
    md += "## 🎯 Executive Summary\n\n"
    md += f"{exec_summary}\n\n"
    md += "---\n\n"
    
    # Priority Actions
    if top_actions:
        md += "## ⚡ Priority Actions (Next 48 Hours)\n\n"
        for i, action in enumerate(top_actions, 1):
            md += f"{i}. {action}\n"
        md += "\n---\n\n"
    
    # Top Insights
    if top_insights:
        md += "## 💎 Top Insights\n\n"
        for i, insight in enumerate(top_insights, 1):
            md += f"### {i}. Insight\n"
            md += f"**{insight['speaker']}**: {insight['content']}\n\n"
        md += "---\n\n"
    
    # Key Decisions
    if top_decisions:
        md += "## 📋 Key Decisions\n\n"
        for i, decision in enumerate(top_decisions, 1):
            md += f"### {i}. {decision.get('title', 'Decision')}\n"
            if 'content' in decision:
                md += f"{decision['content']}\n\n"
        md += "---\n\n"
    
    # Processing Info
    md += "## 📈 Processing Information\n\n"
    md += f"- **Meeting ID**: {metadata.get('meeting_id', 'unknown')}\n"
    md += f"- **Blocks Generated**: {', '.join(blocks_generated)}\n"
    md += f"- **Processing Date**: {metadata.get('processing_date', 'Unknown')}\n\n"
    
    return md
