#!/usr/bin/env python3
"""
Decisions Extractor
Extracts decisions made during meetings with rationale and context.
"""
import logging
import re
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def generate_decisions(
    transcript: str,
    meeting_info: Dict[str, Any],
    output_dir: Path
) -> bool:
    """
    Extract decisions from transcript and generate decisions.md.
    
    Args:
        transcript: Full meeting transcript text
        meeting_info: Extracted meeting metadata
        output_dir: Directory to write output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Extracting decisions from transcript")
        
        # Parse transcript into statements
        statements = _parse_transcript(transcript)
        
        # Extract decisions
        decisions = _extract_decisions(statements)
        
        # Categorize decisions
        categorized = _categorize_decisions(decisions)
        
        # Generate markdown
        markdown = _generate_markdown(categorized, meeting_info)
        
        # Write output
        output_path = output_dir / "decisions.md"
        output_path.write_text(markdown, encoding='utf-8')
        
        logger.info(f"Generated decisions: {len(decisions)} total decisions")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate decisions: {e}", exc_info=True)
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
            
        # Check if line is a speaker name
        if _is_likely_speaker(line):
            if current_speaker and current_content:
                statements.append({
                    "speaker": current_speaker,
                    "content": " ".join(current_content)
                })
            current_speaker = line
            current_content = []
        else:
            current_content.append(line)
    
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
    if any(word in text.lower() for word in ["decided", "going", "will", "should"]):
        return False
    if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', text):
        return True
    if re.match(r'^[A-Z][a-z]+$', text) and len(text) < 20:
        return True
    return False


def _extract_decisions(statements: List[Dict]) -> List[Dict]:
    """Extract decision statements from parsed transcript."""
    decisions = []
    
    decision_indicators = [
        "decided", "decision", "going with", "chose", "choosing",
        "will not", "won't", "agreed", "agree", "conclusion",
        "determined", "settled on", "final", "definitely"
    ]
    
    for stmt in statements:
        content = stmt["content"]
        content_lower = content.lower()
        speaker = stmt["speaker"]
        
        # Check for decision indicators
        for indicator in decision_indicators:
            if indicator in content_lower:
                # Extract context
                context = _extract_context(content, indicator)
                rationale = _extract_rationale(content)
                
                decision = {
                    "decision": context["decision"],
                    "rationale": rationale,
                    "decided_by": speaker,
                    "full_context": content,
                    "type": _infer_type(content)
                }
                decisions.append(decision)
                break  # Only extract once per statement
    
    return decisions


def _extract_context(content: str, indicator: str) -> Dict[str, str]:
    """Extract decision context around indicator."""
    lower_content = content.lower()
    pos = lower_content.find(indicator.lower())
    
    if pos == -1:
        return {"decision": content[:150]}
    
    # Extract around indicator
    start = max(0, pos - 30)
    end = min(len(content), pos + 200)
    context_window = content[start:end]
    
    return {"decision": context_window.strip()[:200]}


def _extract_rationale(content: str) -> str:
    """Extract rationale for decision."""
    rationale_indicators = ["because", "since", "reason", "so that", "in order to"]
    
    content_lower = content.lower()
    for indicator in rationale_indicators:
        if indicator in content_lower:
            pos = content_lower.find(indicator)
            rationale = content[pos:pos+200]
            return rationale.strip()
    
    return "No explicit rationale provided"


def _infer_type(content: str) -> str:
    """Infer decision type from content."""
    content_lower = content.lower()
    
    if any(word in content_lower for word in ["strategy", "direction", "approach", "vision"]):
        return "Strategic"
    if any(word in content_lower for word in ["hire", "budget", "invest", "resource"]):
        return "Resource Allocation"
    if any(word in content_lower for word in ["process", "workflow", "procedure", "how we"]):
        return "Process"
    if any(word in content_lower for word in ["product", "feature", "build", "design"]):
        return "Product"
    
    return "Tactical"


def _categorize_decisions(decisions: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize decisions by type."""
    categorized = {
        "Strategic": [],
        "Product": [],
        "Resource Allocation": [],
        "Process": [],
        "Tactical": []
    }
    
    for decision in decisions:
        decision_type = decision.get("type", "Tactical")
        if decision_type in categorized:
            categorized[decision_type].append(decision)
        else:
            categorized["Tactical"].append(decision)
    
    return categorized


def _generate_markdown(categorized: Dict[str, List[Dict]], meeting_info: Dict) -> str:
    """Generate markdown output for decisions."""
    title = f"Decisions Made: {meeting_info.get('stakeholder_primary', 'Meeting')}"
    date = meeting_info.get('date', 'Unknown Date')
    
    md = f"# {title}\n"
    md += f"**Date**: {date}\n\n"
    md += "---\n\n"
    
    decision_count = sum(len(decisions) for decisions in categorized.values())
    
    if decision_count == 0:
        md += "_No explicit decisions identified in this meeting._\n"
        return md
    
    # Generate sections for each category
    for category, decisions in categorized.items():
        if not decisions:
            continue
            
        md += f"## {category} Decisions\n\n"
        
        for i, decision in enumerate(decisions, 1):
            md += f"### {i}. {decision['decision'][:100]}\n\n"
            md += f"**Decision**: {decision['decision']}\n\n"
            
            if decision['rationale'] != "No explicit rationale provided":
                md += f"**Rationale**: {decision['rationale']}\n\n"
            
            md += f"**Decided By**: {decision['decided_by']}\n\n"
            
            # Add impact if we can infer it
            md += f"**Type**: {decision['type']}\n\n"
            md += "---\n\n"
    
    return md
