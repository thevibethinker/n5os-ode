#!/usr/bin/env python3
"""
Action Items Extractor
Extracts action items from meeting transcripts with owner, deadline, and context.
"""
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def generate_action_items(
    transcript: str,
    meeting_info: Dict[str, Any],
    output_dir: Path
) -> bool:
    """
    Extract action items from transcript and generate action-items.md.
    
    Args:
        transcript: Full meeting transcript text
        meeting_info: Extracted meeting metadata
        output_dir: Directory to write output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Extracting action items from transcript")
        
        # Parse transcript into statements
        statements = _parse_transcript(transcript)
        
        # Extract commitments
        commitments = _extract_commitments(statements, meeting_info)
        
        # Categorize by timeframe
        categorized = _categorize_by_timeframe(commitments, meeting_info.get("date"))
        
        # Generate markdown
        markdown = _generate_markdown(categorized, meeting_info)
        
        # Write output
        output_path = output_dir / "action-items.md"
        output_path.write_text(markdown, encoding='utf-8')
        
        logger.info(f"Generated action items: {len(commitments)} total items")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate action items: {e}", exc_info=True)
        return False


def _parse_transcript(transcript: str) -> List[Dict[str, Any]]:
    """Parse transcript into speaker-attributed statements."""
    statements = []
    lines = transcript.strip().split('\n')
    
    current_speaker = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line is a speaker name (simple heuristic)
        if _is_likely_speaker(line):
            # Save previous statement
            if current_speaker and current_content:
                statements.append({
                    "speaker": current_speaker,
                    "content": " ".join(current_content)
                })
            current_speaker = line
            current_content = []
        else:
            current_content.append(line)
    
    # Save final statement
    if current_speaker and current_content:
        statements.append({
            "speaker": current_speaker,
            "content": " ".join(current_content)
        })
    
    return statements


def _is_likely_speaker(text: str) -> bool:
    """Check if text line is likely a speaker name."""
    if len(text) > 50:
        return False
    if any(word in text.lower() for word in ["will", "going", "should", "need", "want"]):
        return False
    # Name-like patterns
    if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', text):
        return True
    if re.match(r'^[A-Z][a-z]+$', text) and len(text) < 20:
        return True
    return False


def _extract_commitments(statements: List[Dict], meeting_info: Dict) -> List[Dict]:
    """Extract commitment statements from parsed transcript."""
    commitments = []
    
    commitment_indicators = [
        "i'll", "i will", "i'm going to", "i need to", "i should", "i have to",
        "going to", "will", "need to", "have to", "plan to", "must"
    ]
    
    for stmt in statements:
        content = stmt["content"].lower()
        speaker = stmt["speaker"]
        
        # Check for commitment indicators
        for indicator in commitment_indicators:
            if indicator in content:
                # Extract context around indicator
                context = _extract_context(stmt["content"], indicator)
                deadline = _infer_deadline(content, meeting_info.get("date"))
                
                commitment = {
                    "owner": speaker,
                    "action": context["action"],
                    "context": context["full"],
                    "deadline": deadline,
                    "priority": _infer_priority(content)
                }
                commitments.append(commitment)
                break  # Only extract once per statement
    
    return commitments


def _extract_context(content: str, indicator: str) -> Dict[str, str]:
    """Extract action context around commitment indicator."""
    # Find the indicator position
    lower_content = content.lower()
    pos = lower_content.find(indicator.lower())
    
    if pos == -1:
        return {"action": content[:100], "full": content}
    
    # Extract sentence containing indicator
    start = max(0, pos - 50)
    end = min(len(content), pos + 150)
    context_window = content[start:end]
    
    # Clean up
    action = context_window.strip()
    if action.startswith("..."):
        action = action[3:].strip()
    
    return {
        "action": action[:200],
        "full": content
    }


def _infer_deadline(content: str, meeting_date: str) -> str:
    """Infer deadline from content and meeting date."""
    content_lower = content.lower()
    
    try:
        base_date = datetime.strptime(meeting_date, "%Y-%m-%d")
    except:
        base_date = datetime.now()
    
    # Explicit date references
    if "tomorrow" in content_lower:
        deadline = base_date + timedelta(days=1)
        return deadline.strftime("%Y-%m-%d")
    if "today" in content_lower:
        return base_date.strftime("%Y-%m-%d")
    if "next week" in content_lower:
        deadline = base_date + timedelta(weeks=1)
        return deadline.strftime("%Y-%m-%d")
    if "end of week" in content_lower or "this week" in content_lower:
        days_until_friday = (4 - base_date.weekday()) % 7
        deadline = base_date + timedelta(days=days_until_friday)
        return deadline.strftime("%Y-%m-%d")
    
    # Urgency-based inference
    if any(word in content_lower for word in ["asap", "urgent", "immediately", "right away"]):
        deadline = base_date + timedelta(days=1)
        return deadline.strftime("%Y-%m-%d")
    
    # Default: 1 week
    deadline = base_date + timedelta(weeks=1)
    return deadline.strftime("%Y-%m-%d")


def _infer_priority(content: str) -> str:
    """Infer priority level from content."""
    content_lower = content.lower()
    
    if any(word in content_lower for word in ["critical", "urgent", "asap", "immediately"]):
        return "high"
    if any(word in content_lower for word in ["important", "priority", "should"]):
        return "medium"
    return "normal"


def _categorize_by_timeframe(commitments: List[Dict], meeting_date: str) -> Dict[str, List[Dict]]:
    """Categorize commitments by timeframe."""
    try:
        base_date = datetime.strptime(meeting_date, "%Y-%m-%d")
    except:
        base_date = datetime.now()
    
    categorized = {
        "immediate": [],  # 0-2 days
        "short_term": [],  # 3-14 days
        "medium_term": [],  # 15-30 days
        "long_term": []  # 30+ days
    }
    
    for commitment in commitments:
        try:
            deadline = datetime.strptime(commitment["deadline"], "%Y-%m-%d")
            days_away = (deadline - base_date).days
            
            if days_away <= 2:
                categorized["immediate"].append(commitment)
            elif days_away <= 14:
                categorized["short_term"].append(commitment)
            elif days_away <= 30:
                categorized["medium_term"].append(commitment)
            else:
                categorized["long_term"].append(commitment)
        except:
            categorized["short_term"].append(commitment)
    
    return categorized


def _generate_markdown(categorized: Dict[str, List[Dict]], meeting_info: Dict) -> str:
    """Generate markdown output for action items."""
    participants = meeting_info.get("participants", [])
    title = f"Action Items: {meeting_info.get('stakeholder_primary', 'Meeting')}"
    
    md = f"# {title}\n\n"
    
    # Immediate actions
    if categorized["immediate"]:
        md += "## Immediate (Next 24-48 Hours)\n\n"
        for item in categorized["immediate"]:
            md += f"- [ ] **{item['action']}**\n"
            md += f"  - **Owner**: {item['owner']}\n"
            md += f"  - **Deadline**: {item['deadline']}\n"
            if item.get('priority') == 'high':
                md += f"  - **Priority**: HIGH\n"
            md += f"  - **Context**: {item['context'][:200]}\n\n"
    
    # Short-term actions
    if categorized["short_term"]:
        md += "## Short-Term (1-2 Weeks)\n\n"
        for item in categorized["short_term"]:
            md += f"- [ ] **{item['action']}**\n"
            md += f"  - **Owner**: {item['owner']}\n"
            md += f"  - **Deadline**: {item['deadline']}\n"
            md += f"  - **Context**: {item['context'][:200]}\n\n"
    
    # Medium-term actions
    if categorized["medium_term"]:
        md += "## Medium-Term (2-4 Weeks)\n\n"
        for item in categorized["medium_term"]:
            md += f"- [ ] **{item['action']}**\n"
            md += f"  - **Owner**: {item['owner']}\n"
            md += f"  - **Deadline**: {item['deadline']}\n"
            md += f"  - **Context**: {item['context'][:200]}\n\n"
    
    # Long-term actions
    if categorized["long_term"]:
        md += "## Long-Term (1+ Months)\n\n"
        for item in categorized["long_term"]:
            md += f"- [ ] **{item['action']}**\n"
            md += f"  - **Owner**: {item['owner']}\n"
            md += f"  - **Deadline**: {item['deadline']}\n"
            md += f"  - **Context**: {item['context'][:200]}\n\n"
    
    if not any(categorized.values()):
        md += "_No explicit action items identified in this meeting._\n"
    
    return md
