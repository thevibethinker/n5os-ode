#!/usr/bin/env python3
"""
Internal Meeting Block Generator for N5
Generates B40-B48 blocks for internal stakeholder meetings following MECEM principles.

Architecture:
- Uses stakeholder_classifier to detect internal meetings
- Loads block definitions from N5/prefs/internal_block_definitions.json
- Generates blocks with proper cross-references following MECEM (Mutually Exclusive, Collectively Exhaustive, Minimally Repeating)
- Integrates with existing meeting processing workflow

Usage:
    python generate_internal_blocks.py --transcript <path> --output-dir <path> --meeting-type <type>
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / "utils"))
from stakeholder_classifier import classify_meeting, get_participant_details

# Load configurations
WORKSPACE = Path("/home/workspace")
BLOCK_DEFS_PATH = WORKSPACE / "N5/prefs/internal_block_definitions.json"
REGISTRY_PATH = WORKSPACE / "N5/prefs/block_type_registry.json"
ARCH_PRINCIPLES_PATH = WORKSPACE / "N5/prefs/architectural_principles.md"


def load_block_definitions() -> Dict:
    """Load internal block definitions."""
    if not BLOCK_DEFS_PATH.exists():
        raise FileNotFoundError(f"Block definitions not found: {BLOCK_DEFS_PATH}")
    
    with open(BLOCK_DEFS_PATH, 'r') as f:
        return json.load(f)


def load_registry() -> Dict:
    """Load block type registry."""
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Registry not found: {REGISTRY_PATH}")
    
    with open(REGISTRY_PATH, 'r') as f:
        return json.load(f)


def should_generate_block(block_id: str, block_def: Dict, transcript: str, meeting_duration_min: int) -> bool:
    """
    Determine if a block should be generated based on conditions.
    
    Args:
        block_id: Block identifier (e.g., "B40")
        block_def: Block definition from config
        transcript: Meeting transcript text
        meeting_duration_min: Meeting duration in minutes
        
    Returns:
        True if block should be generated
    """
    # Always generate blocks
    if block_def.get("always_generate", False):
        return True
    
    # Check generation conditions
    conditions = block_def.get("generation_conditions", [])
    if not conditions:
        return False
    
    transcript_lower = transcript.lower()
    
    # B42 - Market/Competitive Intelligence
    if block_id == "B42":
        keywords = ["market", "competitor", "competitive", "customer feedback", "icp", "positioning", "differentiation"]
        return any(kw in transcript_lower for kw in keywords)
    
    # B43 - Product Intelligence
    if block_id == "B43":
        keywords = ["product", "roadmap", "feature", "architecture", "engineering", "technical", "ux", "user experience"]
        return any(kw in transcript_lower for kw in keywords)
    
    # B44 - GTM/Sales Intelligence
    if block_id == "B44":
        keywords = ["sales", "gtm", "go-to-market", "pricing", "packaging", "distribution", "marketing", "messaging"]
        return any(kw in transcript_lower for kw in keywords)
    
    # B45 - Operations/Process
    if block_id == "B45":
        keywords = ["process", "workflow", "tool", "efficiency", "operations", "operational"]
        return any(kw in transcript_lower for kw in keywords)
    
    # B46 - Hiring/Team
    if block_id == "B46":
        keywords = ["hiring", "recruit", "candidate", "role", "team expansion", "compensation", "hire"]
        return any(kw in transcript_lower for kw in keywords)
    
    # B48 - Strategic Memo (duration >= 30min AND significant content)
    if block_id == "B48":
        if meeting_duration_min < 30:
            return False
        # Check for strategic keywords
        strategic_keywords = ["strategy", "strategic", "decision", "direction", "pivot", "focus", "priority"]
        return any(kw in transcript_lower for kw in strategic_keywords)
    
    return False


def create_block_prompt(block_id: str, block_def: Dict, transcript: str, participant_details: Dict) -> str:
    """
    Create a prompt for Zo to generate the block content.
    
    Args:
        block_id: Block identifier
        block_def: Block definition from config
        transcript: Meeting transcript
        participant_details: Participant classification details
        
    Returns:
        Prompt string for LLM
    """
    block_name = block_def["name"]
    purpose = block_def["purpose"]
    scope = block_def["scope"]
    mecem_role = block_def.get("misi_role", "")  # Still misi_role in JSON, represents MECEM
    structure = block_def.get("structure", {})
    generation_guidance = block_def.get("generation_guidance", {})
    cross_refs = block_def.get("cross_references", {})
    
    prompt = f"""# Generate {block_id}_{block_name}

**Purpose:** {purpose}
**Scope:** {scope}
**MECEM Role:** {mecem_role}

## Architectural Principles

This block follows MECEM (Mutually Exclusive, Collectively Exhaustive, Minimally Repeating) principles:
- Store information once in its canonical location
- Use cross-references to link related information
- Avoid duplicating context from other blocks
- Reference format: [B##.ID#] for cross-block references

"""
    
    # Add structure guidance
    if structure:
        prompt += "\n## Structure\n\n"
        if "sections" in structure:
            prompt += "Generate the following sections:\n\n"
            for section in structure["sections"]:
                if isinstance(section, dict):
                    prompt += f"### {section.get('name', 'Section')}\n"
                    if "format" in section:
                        prompt += f"Format: {section['format']}\n"
                    if "note" in section:
                        prompt += f"Note: {section['note']}\n"
                    prompt += "\n"
                else:
                    prompt += f"- {section}\n"
        elif "format" in structure:
            prompt += f"Format: {structure['format']}\n"
            if "note" in structure:
                prompt += f"Note: {structure['note']}\n"
    
    # Add generation guidance
    if generation_guidance:
        prompt += "\n## Generation Guidance\n\n"
        if "extract_from_transcript" in generation_guidance:
            prompt += "Look for these indicators in the transcript:\n"
            for indicator in generation_guidance["extract_from_transcript"]:
                prompt += f"- {indicator}\n"
            prompt += "\n"
        
        if "rules" in generation_guidance:
            prompt += "Rules:\n"
            for rule in generation_guidance["rules"]:
                prompt += f"- {rule}\n"
            prompt += "\n"
        
        if "two_axis_framework" in generation_guidance:
            framework = generation_guidance["two_axis_framework"]
            prompt += "Decision Framework:\n"
            for key, value in framework.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"
    
    # Add cross-reference guidance
    if cross_refs:
        prompt += "\n## Cross-References\n\n"
        if cross_refs.get("references_to"):
            prompt += f"This block should REFERENCE: {', '.join(cross_refs['references_to'])}\n"
        if cross_refs.get("referenced_by"):
            prompt += f"This block will be REFERENCED BY: {', '.join(cross_refs['referenced_by'])}\n"
        if "format" in cross_refs:
            prompt += f"Reference format: {cross_refs['format']}\n"
        if "note" in cross_refs:
            prompt += f"Note: {cross_refs['note']}\n"
        prompt += "\n"
    
    # Add meeting context
    prompt += f"""## Meeting Context

**Meeting Type:** {participant_details.get('meeting_type', 'INTERNAL')}
**Participants:** {participant_details.get('total_participants', 0)} internal team members
**Has N5OS Tag:** {participant_details.get('has_n5os_tag', False)}

"""
    
    # Add transcript
    prompt += f"""## Transcript

```
{transcript}
```

## Instructions

1. Extract relevant information from the transcript for this block
2. Follow the structure guidelines above
3. Use proper cross-references (don't duplicate information)
4. Be comprehensive but focused on this block's purpose
5. Use markdown formatting
6. If no relevant content found, create a brief note explaining why

Generate the complete {block_id}_{block_name}.md content now:
"""
    
    return prompt


def generate_block(block_id: str, block_def: Dict, transcript: str, participant_details: Dict, output_dir: Path) -> Optional[Path]:
    """
    Generate a single internal meeting block.
    
    Args:
        block_id: Block identifier
        block_def: Block definition
        transcript: Meeting transcript
        participant_details: Participant details
        output_dir: Output directory
        
    Returns:
        Path to generated block file, or None if generation failed
    """
    block_name = block_def["name"]
    output_file = output_dir / f"{block_id}_{block_name}.md"
    
    logger.info(f"Generating {block_id}_{block_name}...")
    
    # Create prompt
    prompt = create_block_prompt(block_id, block_def, transcript, participant_details)
    
    # Create prompt file for Zo to process
    prompt_file = output_dir / f"_PROMPT_{block_id}.md"
    prompt_file.write_text(prompt, encoding='utf-8')
    
    logger.info(f"  ✓ Prompt created: {prompt_file}")
    logger.info(f"  → Output will be: {output_file}")
    
    return prompt_file


def generate_internal_blocks(transcript_path: Path, output_dir: Path, meeting_type: str, meeting_duration_min: int = 30):
    """
    Generate all appropriate internal meeting blocks.
    
    Args:
        transcript_path: Path to transcript file
        output_dir: Directory for output files
        meeting_type: Meeting type (INTERNAL_STANDUP_COFOUNDER, INTERNAL_STANDUP_TEAM, INTERNAL_STRATEGIC)
        meeting_duration_min: Meeting duration in minutes
    """
    logger.info(f"Starting internal block generation for {meeting_type}")
    logger.info(f"Transcript: {transcript_path}")
    logger.info(f"Output: {output_dir}")
    
    # Load configurations
    logger.info("Loading configurations...")
    block_defs = load_block_definitions()
    registry = load_registry()
    
    # Read transcript
    logger.info("Reading transcript...")
    transcript = transcript_path.read_text(encoding='utf-8')
    
    # Classify meeting (to get participant details)
    logger.info("Classifying meeting...")
    participant_details = get_participant_details("", transcript)
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get blocks to generate from registry
    meeting_blocks = registry["blocks"][meeting_type]["block_ids"] if meeting_type in registry["blocks"] else []
    
    if not meeting_blocks:
        logger.warning(f"No blocks defined for meeting type: {meeting_type}")
        return
    
    logger.info(f"Registered blocks for {meeting_type}: {meeting_blocks}")
    
    # Generate each block
    generated_blocks = []
    skipped_blocks = []
    
    for block_id in meeting_blocks:
        # Find block definition
        block_key = None
        for key in block_defs["block_definitions"].keys():
            if key.startswith(block_id):
                block_key = key
                break
        
        if not block_key:
            logger.warning(f"No definition found for block: {block_id}")
            continue
        
        block_def = block_defs["block_definitions"][block_key]
        
        # Check if should generate
        if should_generate_block(block_id, block_def, transcript, meeting_duration_min):
            prompt_file = generate_block(block_id, block_def, transcript, participant_details, output_dir)
            if prompt_file:
                generated_blocks.append(block_id)
        else:
            logger.info(f"Skipping {block_id} (conditions not met)")
            skipped_blocks.append(block_id)
    
    # Create summary
    logger.info("\n" + "=" * 80)
    logger.info("INTERNAL BLOCK GENERATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Meeting Type: {meeting_type}")
    logger.info(f"Blocks Generated: {len(generated_blocks)}")
    logger.info(f"  {', '.join(generated_blocks)}")
    logger.info(f"Blocks Skipped: {len(skipped_blocks)}")
    logger.info(f"  {', '.join(skipped_blocks)}")
    logger.info(f"\nOutput Directory: {output_dir}")
    logger.info("\nNext Step: Process the prompt files with Zo to generate block content")
    logger.info("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate internal meeting blocks (B40-B48)")
    parser.add_argument("--transcript", required=True, help="Path to transcript file")
    parser.add_argument("--output-dir", required=True, help="Output directory for blocks")
    parser.add_argument("--meeting-type", required=True, 
                       choices=["INTERNAL_STANDUP_COFOUNDER", "INTERNAL_STANDUP_TEAM", "INTERNAL_STRATEGIC"],
                       help="Type of internal meeting")
    parser.add_argument("--duration", type=int, default=30, help="Meeting duration in minutes (default: 30)")
    
    args = parser.parse_args()
    
    transcript_path = Path(args.transcript)
    output_dir = Path(args.output_dir)
    
    if not transcript_path.exists():
        logger.error(f"Transcript not found: {transcript_path}")
        sys.exit(1)
    
    try:
        generate_internal_blocks(transcript_path, output_dir, args.meeting_type, args.duration)
        logger.info("\n✅ Internal block generation complete!")
    except Exception as e:
        logger.error(f"\n❌ Error during generation: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
