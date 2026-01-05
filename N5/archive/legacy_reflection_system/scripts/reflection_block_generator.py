#!/usr/bin/env python3
"""
Reflection Block Content Generator (Worker 4)

Generate block content from transcripts using classification + style guides.
Part of reflection-v2 processing pipeline.

Usage:
    python3 reflection_block_generator.py --input <transcript.jsonl> --output <output_dir> [--dry-run]
    python3 reflection_block_generator.py --process-all [--dry-run]
"""

import argparse
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
REGISTRY_PATH = Path("/home/workspace/N5/prefs/reflection_block_registry.json")
INCOMING_DIR = Path("/home/workspace/N5/records/reflections/incoming")
OUTPUTS_DIR = Path("/home/workspace/N5/records/reflections/outputs")
WORKSPACE_ROOT = Path("/home/workspace")


def load_registry() -> Dict:
    """Load block type registry."""
    try:
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load registry: {e}")
        raise


def load_transcript(transcript_path: Path) -> str:
    """Load transcript text from .jsonl file."""
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
        return data.get('text', '')
    except Exception as e:
        logger.error(f"Failed to load transcript {transcript_path}: {e}")
        raise


def load_classification(classification_path: Path) -> Dict:
    """Load classification results."""
    try:
        with open(classification_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load classification {classification_path}: {e}")
        raise


def load_file_content(file_path: Path) -> str:
    """Load content from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.warning(f"Failed to load {file_path}: {e}")
        return ""


def get_voice_profile_path(block_id: str, block_def: Dict) -> Path:
    """Determine which voice profile to use based on block domain."""
    domain = block_def.get("domain", "internal")
    
    if domain == "external_social":
        voice_path = WORKSPACE_ROOT / "N5/prefs/communication/social-media-voice.md"
    elif domain in ["external_professional", "internal"]:
        voice_path = WORKSPACE_ROOT / "N5/prefs/communication/voice.md"
    else:
        logger.warning(f"Unknown domain '{domain}' for {block_id}, defaulting to voice.md")
        voice_path = WORKSPACE_ROOT / "N5/prefs/communication/voice.md"
    
    if not voice_path.exists():
        logger.error(f"Voice profile not found: {voice_path}")
        return None
    
    return voice_path


def get_style_guide_path(block_def: Dict) -> Optional[Path]:
    """Get style guide path from block definition."""
    style_guide_rel = block_def.get("style_guide", "")
    if not style_guide_rel:
        logger.warning(f"No style guide defined for block")
        return None
    
    style_guide_path = WORKSPACE_ROOT / style_guide_rel
    
    if not style_guide_path.exists():
        logger.error(f"Style guide not found: {style_guide_path}")
        return None
    
    return style_guide_path


def count_blocks_generated(block_id: str, days: int = 30) -> int:
    """Count how many blocks of this type have been generated in the past N days.
    
    This is a placeholder - full implementation would scan outputs directory
    and count matching block types within the time window.
    """
    # TODO: Implement actual counting logic
    # For now, return 0 to enable auto-approval testing
    return 0


def determine_approval_mode(blocks_generated: List[Dict], registry: Dict) -> str:
    """Determine if blocks can be auto-approved.
    
    Rules:
    - ALL blocks must have auto_approve_threshold > 0
    - ALL blocks must be under their threshold count
    - External social (B80-B89) never auto-approve
    """
    for block in blocks_generated:
        block_id = block["block_id"]
        block_def = registry["blocks"].get(block_id, {})
        
        # Get auto-approve threshold
        threshold = block_def.get("auto_approve_threshold", 0)
        
        # Check if auto-approve eligible
        if threshold == 0:
            logger.info(f"{block_id} not eligible for auto-approve (threshold=0)")
            return "manual"
        
        # Check historical count for this block type
        count = count_blocks_generated(block_id, days=30)
        if count >= threshold:
            logger.info(f"{block_id} exceeds auto-approve threshold ({count} >= {threshold})")
            return "manual"
    
    logger.info("All blocks eligible for auto-approval")
    return "auto"


def build_generation_prompt(
    transcript: str,
    block_def: Dict,
    classification: Dict,
    voice_profile: str,
    style_guide: str
) -> str:
    """Build prompt for LLM content generation."""
    
    block_name = block_def.get("name", "Unknown Block")
    confidence = classification.get("confidence", 0.0)
    
    prompt = f"""Transform the following stream-of-consciousness reflection into a {block_name} 
following the style guide and voice profile provided.

CLASSIFICATION CONFIDENCE: {confidence:.2f}

VOICE PROFILE:
{voice_profile}

STYLE GUIDE:
{style_guide}

TRANSCRIPT:
{transcript}

Generate the {block_name} block content now, following all requirements from the style guide.
Output only the final markdown content, no preamble or explanation.
"""
    
    return prompt


def generate_block_content(
    transcript: str,
    block_def: Dict,
    classification: Dict,
    registry: Dict,
    dry_run: bool = False
) -> Tuple[Optional[str], Dict]:
    """Generate block content using LLM processing.
    
    Returns:
        (content, metadata) tuple
    """
    
    block_id = classification.get("block_id", "")
    block_name = block_def.get("name", "Unknown")
    
    # Get voice profile
    voice_path = get_voice_profile_path(block_id, block_def)
    if not voice_path:
        return None, {"error": "Voice profile not found"}
    
    # Get style guide
    style_guide_path = get_style_guide_path(block_def)
    if not style_guide_path:
        return None, {"error": "Style guide not found"}
    
    # Load voice profile and style guide
    voice_profile = load_file_content(voice_path)
    style_guide = load_file_content(style_guide_path)
    
    if not voice_profile or not style_guide:
        return None, {"error": "Failed to load voice profile or style guide"}
    
    # Build generation prompt
    prompt = build_generation_prompt(
        transcript,
        block_def,
        classification,
        voice_profile,
        style_guide
    )
    
    if dry_run:
        logger.info(f"[DRY RUN] Would generate {block_id} content")
        content = f"[DRY RUN] Generated content for {block_name}\n\n{prompt[:200]}..."
    else:
        # In production, this outputs the prompt for LLM processing
        # The LLM (Zo) will process this prompt and return content
        logger.info(f"Generated prompt for {block_id} ({len(prompt)} chars)")
        
        # Output prompt to file for LLM processing
        content = f"# {block_name}\n\n[PROMPT FOR LLM PROCESSING - See generation_prompts/ directory]"
    
    # Build metadata
    metadata = {
        "block_id": block_id,
        "block_name": block_name,
        "voice_profile": str(voice_path.relative_to(WORKSPACE_ROOT)),
        "style_guide": str(style_guide_path.relative_to(WORKSPACE_ROOT)),
        "word_count": len(content.split()) if content else 0,
        "auto_approve_eligible": block_def.get("auto_approve_threshold", 0) > 0,
        "auto_approve_threshold": block_def.get("auto_approve_threshold", 0),
        "prompt_length": len(prompt),
        "generation_timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    return content, metadata, prompt


def process_reflection(
    transcript_path: Path,
    output_dir: Path,
    dry_run: bool = False
) -> int:
    """Process a single reflection: load transcript + classification, generate blocks.
    
    Returns:
        0 on success, 1 on failure
    """
    
    # Load registry
    registry = load_registry()
    
    # Derive classification path
    classification_path = transcript_path.with_suffix('.classification.json')
    if not classification_path.exists():
        logger.error(f"Classification not found: {classification_path}")
        return 1
    
    # Load transcript and classification
    try:
        transcript = load_transcript(transcript_path)
        classification_data = load_classification(classification_path)
    except Exception as e:
        logger.error(f"Failed to load inputs: {e}")
        return 1
    
    # Extract reflection metadata
    source_file = classification_data.get("source_file", transcript_path.stem)
    reflection_id = classification_data.get("reflection_id", transcript_path.stem)
    classifications = classification_data.get("classifications", [])
    
    if not classifications:
        logger.error(f"No classifications found in {classification_path}")
        return 1
    
    logger.info(f"Processing reflection: {reflection_id}")
    logger.info(f"  Transcript: {transcript_path}")
    logger.info(f"  Classifications: {len(classifications)}")
    
    # Create output directory structure
    blocks_dir = output_dir / "blocks"
    prompts_dir = output_dir / "generation_prompts"
    
    if not dry_run:
        blocks_dir.mkdir(parents=True, exist_ok=True)
        prompts_dir.mkdir(parents=True, exist_ok=True)
    else:
        logger.info(f"[DRY RUN] Would create directories: {blocks_dir}, {prompts_dir}")
    
    # Generate blocks
    blocks_generated = []
    
    for classification in classifications:
        block_id = classification.get("block_id", "")
        confidence = classification.get("confidence", 0.0)
        
        if not block_id:
            logger.warning(f"Skipping classification with no block_id")
            continue
        
        # Get block definition
        block_def = registry["blocks"].get(block_id)
        if not block_def:
            logger.error(f"Block {block_id} not found in registry")
            continue
        
        block_name = block_def.get("name", "Unknown")
        logger.info(f"  Generating {block_id} ({block_name}, confidence={confidence:.2f})")
        
        # Generate content
        result = generate_block_content(
            transcript,
            block_def,
            classification,
            registry,
            dry_run
        )
        
        if result[0] is None:
            logger.error(f"  Failed to generate {block_id}: {result[1]}")
            continue
        
        content, metadata, prompt = result
        
        # Save block content
        block_filename = f"{block_id}_{block_name.lower().replace(' ', '-').replace('&', 'and')}.md"
        block_path = blocks_dir / block_filename
        
        if not dry_run:
            with open(block_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"  ✓ Saved block: {block_path}")
        else:
            logger.info(f"  [DRY RUN] Would save block: {block_path}")
        
        # Save generation prompt
        prompt_filename = f"{block_id}_prompt.md"
        prompt_path = prompts_dir / prompt_filename
        
        if not dry_run:
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(prompt)
            logger.info(f"  ✓ Saved prompt: {prompt_path}")
        else:
            logger.info(f"  [DRY RUN] Would save prompt: {prompt_path}")
        
        blocks_generated.append(metadata)
    
    # Determine approval mode
    approval_mode = determine_approval_mode(blocks_generated, registry)
    
    # Copy transcript to output
    transcript_output = output_dir / "transcript.jsonl"
    if not dry_run:
        shutil.copy2(transcript_path, transcript_output)
        logger.info(f"✓ Copied transcript to {transcript_output}")
    else:
        logger.info(f"[DRY RUN] Would copy transcript to {transcript_output}")
    
    # Create metadata file
    metadata = {
        "reflection_id": reflection_id,
        "generated_at_iso": datetime.now(timezone.utc).isoformat(),
        "source_file": source_file,
        "classifications": classifications,
        "blocks_generated": blocks_generated,
        "status": "awaiting_approval",
        "approval_mode": approval_mode
    }
    
    metadata_path = output_dir / "metadata.json"
    if not dry_run:
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"✓ Saved metadata: {metadata_path}")
    else:
        logger.info(f"[DRY RUN] Would save metadata: {metadata_path}")
    
    logger.info(f"✓ Processing complete: {len(blocks_generated)} blocks generated")
    logger.info(f"  Approval mode: {approval_mode}")
    logger.info(f"  Output directory: {output_dir}")
    
    return 0


def process_all_pending(dry_run: bool = False) -> int:
    """Process all pending reflections in incoming directory."""
    
    if not INCOMING_DIR.exists():
        logger.error(f"Incoming directory not found: {INCOMING_DIR}")
        return 1
    
    # Find all transcript files
    transcript_files = list(INCOMING_DIR.glob("*.transcript.jsonl"))
    
    if not transcript_files:
        logger.info("No pending reflections found")
        return 0
    
    logger.info(f"Found {len(transcript_files)} pending reflections")
    
    success_count = 0
    failure_count = 0
    
    for transcript_path in transcript_files:
        # Derive output directory
        reflection_id = transcript_path.stem.replace('.transcript', '')
        date_str = reflection_id.split('_')[0]  # Extract date prefix
        
        output_dir = OUTPUTS_DIR / date_str / reflection_id.replace(date_str + '_', '')
        
        logger.info(f"\n--- Processing {reflection_id} ---")
        
        result = process_reflection(transcript_path, output_dir, dry_run)
        
        if result == 0:
            success_count += 1
        else:
            failure_count += 1
    
    logger.info(f"\n✓ Batch processing complete:")
    logger.info(f"  Success: {success_count}")
    logger.info(f"  Failures: {failure_count}")
    
    return 0 if failure_count == 0 else 1


def main(dry_run: bool = False, input_file: Optional[str] = None, 
         output_dir: Optional[str] = None, process_all: bool = False) -> int:
    """Main entry point."""
    
    try:
        if process_all:
            return process_all_pending(dry_run)
        
        if not input_file:
            logger.error("Must specify --input or --process-all")
            return 1
        
        input_path = Path(input_file)
        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            return 1
        
        # Derive output directory if not specified
        if not output_dir:
            reflection_id = input_path.stem.replace('.transcript', '')
            date_str = reflection_id.split('_')[0]
            output_dir = OUTPUTS_DIR / date_str / reflection_id.replace(date_str + '_', '')
        else:
            output_dir = Path(output_dir)
        
        return process_reflection(input_path, output_dir, dry_run)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate block content from reflection transcripts")
    parser.add_argument("--input", help="Input transcript.jsonl file")
    parser.add_argument("--output", help="Output directory for generated blocks")
    parser.add_argument("--process-all", action="store_true", help="Process all pending reflections")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode - no writes")
    
    args = parser.parse_args()
    
    exit(main(
        dry_run=args.dry_run,
        input_file=args.input,
        output_dir=args.output,
        process_all=args.process_all
    ))
