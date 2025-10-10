#!/usr/bin/env python3
"""
Action Items Extractor (Direct Parsing)
Extracts action items from meeting transcripts using direct text analysis.
"""
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


async def generate_action_items(
    transcript: str,
    meeting_info: Dict[str, Any],
    output_dir: Path
) -> bool:
    """
    Extract action items from transcript using direct parsing.
    
    Args:
        transcript: Full meeting transcript text
        meeting_info: Extracted meeting metadata
        output_dir: Directory to write output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Extracting action items from transcript using direct parsing")
        
        # Extract action items
        action_items = extract_action_items_from_text(transcript, meeting_info)
        
        # Generate markdown
        markdown = _generate_markdown(action_items, meeting_info)
        
        # Write output
        output_path = output_dir / "action-items.md"
        output_path.write_text(markdown, encoding='utf-8')
        
        logger.info(f"Generated action items: {len(action_items)} total items")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate action items: {e}", exc_info=True)
        return False


def extract_action_items_from_text(transcript: str, meeting_info: Dict[str, Any]) -> List[Dict]:
    """
    Extract action items by parsing transcript for action-oriented language.
    """
    action_items = []
    lines = transcript.split('\n')
    
    # Action patterns to look for
    action_patterns = [
        (r"\b(?:I'll|I will|I am going to|I'm gonna)\s+(.+)", "immediate"),
        (r"\b(?:we'll|we will|we are going to|we're gonna)\s+(.+)", "short_term"),
        (r"\b(?:should|need to|have to|got to|gotta)\s+(.+)", "short_term"),
        (r"\b(?:follow up|reach out|send|share|provide|create|schedule|set up)\s+(.+)", "immediate"),
        (r"\b(?:next step|next steps|moving forward|going forward)(?:\s+is|\s+are)?\s*[:–-]?\s*(.+)", "immediate"),
    ]
    
    # Deadline patterns
    deadline_patterns = [
        (r"\b(tomorrow|tmrw)\b", 1),
        (r"\b(?:this|next) week\b", 7),
        (r"\b(?:by|before) (?:next )?(monday|tuesday|wednesday|thursday|friday)\b", 7),
        (r"\b(?:in a|next) (?:few )?days?\b", 3),
        (r"\b(?:by|before) (?:the )?end of (?:the )?week\b", 7),
        (r"\b(?:by|before) (?:the )?end of (?:the )?month\b", 30),
    ]
    
    participants = meeting_info.get('participants', [])
    meeting_date_str = meeting_info.get('date', datetime.now().strftime('%Y-%m-%d'))
    meeting_date = datetime.strptime(meeting_date_str, '%Y-%m-%d')
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped or len(line_stripped) < 20:
            continue
        
        # Try to extract speaker from line
        speaker = None
        text = line_stripped
        
        # Check for speaker patterns: "Name: text" or "Name\ntext"
        speaker_match = re.match(r'^([A-Z][a-zA-Z\s]+?)(?::|$)', line_stripped)
        if speaker_match:
            potential_speaker = speaker_match.group(1).strip()
            if any(potential_speaker in p for p in participants):
                speaker = potential_speaker
                text = line_stripped[len(potential_speaker):].lstrip(':').strip()
        
        # Look for action patterns
        for pattern, default_timeframe in action_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                action_text = match.group(1).strip()
                
                # Clean up action text (remove trailing punctuation from sentences)
                action_text = re.sub(r'[.!?]+\s*$', '', action_text)
                
                # Skip if too short or looks incomplete
                if len(action_text) < 10:
                    continue
                
                # Truncate at sentence end if very long
                if len(action_text) > 200:
                    sentence_end = re.search(r'[.!?]', action_text[100:])
                    if sentence_end:
                        action_text = action_text[:100 + sentence_end.start() + 1]
                
                # Determine deadline
                deadline_days = 7  # default
                deadline_found = False
                for deadline_pattern, days in deadline_patterns:
                    if re.search(deadline_pattern, action_text, re.IGNORECASE):
                        deadline_days = days
                        deadline_found = True
                        break
                
                deadline = meeting_date + timedelta(days=deadline_days)
                
                # Determine timeframe based on deadline
                if deadline_days <= 2:
                    timeframe = "immediate"
                    priority = "high"
                elif deadline_days <= 14:
                    timeframe = "short_term"
                    priority = "medium"
                elif deadline_days <= 30:
                    timeframe = "medium_term"
                    priority = "medium"
                else:
                    timeframe = "long_term"
                    priority = "normal"
                
                # Extract owner - prefer identified speaker, fallback to parsing text
                owner = speaker if speaker else "Unknown"
                if not speaker:
                    # Try to find a name in the action text
                    for participant in participants:
                        first_name = participant.split()[0]
                        if first_name.lower() in action_text.lower():
                            owner = participant
                            break
                
                # Build context from surrounding lines
                context_lines = []
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    if j != i and lines[j].strip():
                        context_lines.append(lines[j].strip()[:100])
                context = " | ".join(context_lines[:2]) if context_lines else ""
                
                action_items.append({
                    "action": action_text,
                    "owner": owner,
                    "deadline": deadline.strftime('%Y-%m-%d'),
                    "timeframe": timeframe,
                    "priority": priority,
                    "context": context[:200] if context else "Extracted from meeting transcript"
                })
    
    # Deduplicate similar actions
    action_items = _deduplicate_actions(action_items)
    
    return action_items


def _deduplicate_actions(action_items: List[Dict]) -> List[Dict]:
    """Remove duplicate or very similar action items."""
    if not action_items:
        return []
    
    unique_actions = []
    seen_texts = set()
    
    for item in action_items:
        action_text = item['action'].lower()
        
        # Create a normalized key (first 50 chars, no punctuation)
        key = re.sub(r'[^\w\s]', '', action_text[:50])
        
        if key not in seen_texts:
            seen_texts.add(key)
            unique_actions.append(item)
    
    return unique_actions


def _generate_markdown(action_items: List[Dict], meeting_info: Dict) -> str:
    """Generate markdown output for action items."""
    stakeholder = meeting_info.get('stakeholder_primary', 'Meeting')
    date = meeting_info.get('date', 'Unknown Date')
    
    md = f"# Action Items: {stakeholder}\n"
    md += f"**Date**: {date}\n\n"
    md += "---\n\n"
    
    if not action_items:
        md += "_No explicit action items identified in this meeting._\n"
        return md
    
    # Categorize by timeframe
    categorized = {
        "immediate": [],
        "short_term": [],
        "medium_term": [],
        "long_term": []
    }
    
    for item in action_items:
        timeframe = item.get("timeframe", "short_term")
        if timeframe in categorized:
            categorized[timeframe].append(item)
    
    # Immediate actions
    if categorized["immediate"]:
        md += "## ⚡ Immediate (Next 24-48 Hours)\n\n"
        for item in categorized["immediate"]:
            md += f"- [ ] **{item['action']}**\n"
            md += f"  - **Owner**: {item.get('owner', 'Unknown')}\n"
            md += f"  - **Deadline**: {item.get('deadline', 'TBD')}\n"
            if item.get('priority') == 'high':
                md += f"  - **Priority**: 🔴 HIGH\n"
            if item.get('context') and item['context'] != "Extracted from meeting transcript":
                md += f"  - **Context**: {item['context']}\n"
            md += "\n"
    
    # Short-term actions
    if categorized["short_term"]:
        md += "## 📅 Short-Term (1-2 Weeks)\n\n"
        for item in categorized["short_term"]:
            md += f"- [ ] **{item['action']}**\n"
            md += f"  - **Owner**: {item.get('owner', 'Unknown')}\n"
            md += f"  - **Deadline**: {item.get('deadline', 'TBD')}\n"
            if item.get('context') and item['context'] != "Extracted from meeting transcript":
                md += f"  - **Context**: {item['context'][:100]}\n"
            md += "\n"
    
    # Medium-term actions
    if categorized["medium_term"]:
        md += "## 📆 Medium-Term (2-4 Weeks)\n\n"
        for item in categorized["medium_term"]:
            md += f"- [ ] **{item['action']}**\n"
            md += f"  - **Owner**: {item.get('owner', 'Unknown')}\n"
            md += f"  - **Deadline**: {item.get('deadline', 'TBD')}\n"
            md += "\n"
    
    # Long-term actions
    if categorized["long_term"]:
        md += "## 🗓️ Long-Term (1+ Months)\n\n"
        for item in categorized["long_term"]:
            md += f"- [ ] **{item['action']}**\n"
            md += f"  - **Owner**: {item.get('owner', 'Unknown')}\n"
            md += f"  - **Deadline**: {item.get('deadline', 'TBD')}\n"
            md += "\n"
    
    return md
