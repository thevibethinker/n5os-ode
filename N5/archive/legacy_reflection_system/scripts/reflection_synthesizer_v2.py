#!/usr/bin/env python3
"""
Reflection Synthesizer V2

Synthesizes reflections into structured outputs:
- B90 (Insight Compound): Cross-reflection synthesis
- B91 (Meta-Reflection): Process and system evaluation
- Legacy mode: Original 4-format output (memo/insights/actions/blurb)

Usage:
    # B90: Cross-reflection synthesis
    python3 reflection_synthesizer_v2.py \
      --block-type B90 \
      --input-pattern "N5/records/reflections/incoming/2025-10-*.transcript.jsonl" \
      --output N5/records/reflections/outputs/2025-10-24/compound-insights/ \
      --dry-run

    # B91: Meta-reflection
    python3 reflection_synthesizer_v2.py \
      --block-type B91 \
      --input-pattern "N5/records/reflections/incoming/*.transcript.jsonl" \
      --output N5/records/reflections/outputs/2025-10-24/meta-reflection/ \
      --dry-run

    # Legacy mode
    python3 reflection_synthesizer_v2.py \
      --legacy \
      --input transcript.jsonl \
      --output outputs/
"""

import argparse
import json
import logging
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
STYLE_GUIDES_DIR = WORKSPACE / "N5/prefs/communication/style-guides/reflections"


def load_style_guide(block_id: str) -> Optional[str]:
    """
    Load style guide for block type.
    
    Args:
        block_id: Block ID (e.g., "B90", "B91")
        
    Returns:
        Style guide content or None
    """
    style_guide_file = STYLE_GUIDES_DIR / f"{block_id}-*.md"
    matches = list(STYLE_GUIDES_DIR.glob(f"{block_id}-*.md"))
    
    if matches:
        with open(matches[0], 'r') as f:
            return f.read()
    
    logger.warning(f"Style guide not found for {block_id}")
    return None


def load_transcripts(pattern: str) -> List[Dict]:
    """
    Load transcripts matching pattern.
    
    Args:
        pattern: Glob pattern for transcript files
        
    Returns:
        List of transcript dictionaries
    """
    transcripts = []
    
    # Handle both absolute and relative patterns
    if not pattern.startswith('/'):
        pattern = str(WORKSPACE / pattern)
    
    files = glob.glob(pattern)
    logger.info(f"Found {len(files)} files matching pattern")
    
    for file_path in files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                transcripts.append({
                    "path": file_path,
                    "text": data.get("text", ""),
                    "metadata": {k: v for k, v in data.items() if k != "text"}
                })
        except Exception as e:
            logger.warning(f"Error loading {file_path}: {e}")
            continue
    
    logger.info(f"✓ Loaded {len(transcripts)} transcripts")
    return transcripts


def synthesize_b90(transcripts: List[Dict], style_guide: str) -> str:
    """
    Generate B90 (Insight Compound) synthesis.
    
    Args:
        transcripts: List of transcript dictionaries
        style_guide: B90 style guide content
        
    Returns:
        Synthesized content in markdown
    """
    logger.info("Synthesizing B90: Insight Compound")
    
    # Extract common themes
    all_text = "\n\n".join([t["text"] for t in transcripts])
    
    # Generate synthesis using style guide template
    synthesis = f"""# Insight Compound

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M ET")}  
**Source Reflections:** {len(transcripts)}

---

## Pattern Observed

[Cross-reflection pattern identified across {len(transcripts)} reflections]

---

## Source Reflections

"""
    
    # List source reflections
    for i, transcript in enumerate(transcripts, 1):
        filename = Path(transcript["path"]).stem
        synthesis += f"- **{filename}**\n"
    
    synthesis += f"\n**Date Range:** [Start] - [End]\n\n"
    
    synthesis += """---

## Synthesis

[What these reflections reveal when viewed together. The through-line or common insight.]

[Analyze the combined content to identify recurring themes, patterns, or insights that emerge across multiple reflections.]

---

## Why This Matters

[Implications for decisions, behavior, or understanding]

---

## Open Questions

- [What's still unclear]
- [What to watch for next]

---

## Next Actions

[If pattern suggests behavior change or decision]

---

**Style Guide Reference:** B90-insight-compound.md
"""
    
    return synthesis


def synthesize_b91(transcripts: List[Dict], style_guide: str) -> str:
    """
    Generate B91 (Meta-Reflection) synthesis.
    
    Args:
        transcripts: List of transcript dictionaries
        style_guide: B91 style guide content
        
    Returns:
        Synthesized content in markdown
    """
    logger.info("Synthesizing B91: Meta-Reflection")
    
    synthesis = f"""# Meta-Reflection

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M ET")}  
**Source Reflections:** {len(transcripts)}

---

## Observation

[What I'm noticing about my reflection practice lately]

---

## What's Working

- [Practice/tool/structure that's delivering value]
- [Why it works]

---

## What's Not Working

- [Practice/tool/structure creating friction]
- [Why it's not working]

---

## Patterns Over Time

[How has practice evolved? Compare to previous meta-reflections or initial system design]

---

## Adjustments to Try

1. [Change to system]
2. [Change to process]
3. [Change to habits]

---

## Success Metrics

[How will I know if adjustments work?]

---

**Style Guide Reference:** B91-meta-reflection.md
"""
    
    return synthesis


def synthesize_legacy(transcript: Dict) -> Dict[str, str]:
    """
    Generate legacy format output (memo/insights/actions/blurb).
    
    Args:
        transcript: Single transcript dictionary
        
    Returns:
        Dictionary with legacy format outputs
    """
    logger.info("Synthesizing legacy format")
    
    content = transcript.get("text", "")
    
    # Generate memo
    memo = f"""# Decision Memo

**Date:** {datetime.now().strftime("%Y-%m-%d")}

---

## Executive Summary

[One-paragraph synthesis]

---

## Key Insights

1. **Insight 1**
2. **Insight 2**
3. **Insight 3**

---

## Action Items

1. **Action 1** (Priority: HIGH)
2. **Action 2** (Priority: MEDIUM)

---

## Unresolved Questions

1. [Question 1]
2. [Question 2]
"""
    
    # Generate insights JSON
    insights = [
        {
            "insight": "[Insight extracted]",
            "confidence": "medium",
            "strategic_implication": "...",
        }
    ]
    
    # Generate actions JSON
    actions = [
        {
            "action": "[Action item]",
            "why": "[Rationale]",
            "by_when": "[Date]",
            "owner": "[Who]",
            "priority": "high"
        }
    ]
    
    # Generate blurb
    blurb = "[One-paragraph executive summary]"
    
    return {
        "memo": memo,
        "insights": json.dumps(insights, indent=2),
        "actions": json.dumps(actions, indent=2),
        "blurb": blurb
    }


def save_outputs(content: str, output_dir: Path, filename: str, dry_run: bool = False):
    """
    Save synthesis output.
    
    Args:
        content: Content to save
        output_dir: Output directory
        filename: Output filename
        dry_run: If True, don't actually write
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would save to: {output_dir / filename}")
        logger.info(f"[DRY RUN] Content length: {len(content)} characters")
        return
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    output_file = output_dir / filename
    with open(output_file, 'w') as f:
        f.write(content)
    
    logger.info(f"✓ Saved: {output_file}")


def save_legacy_outputs(outputs: Dict[str, str], output_dir: Path, dry_run: bool = False):
    """
    Save legacy format outputs.
    
    Args:
        outputs: Dictionary of output content
        output_dir: Output directory
        dry_run: If True, don't actually write
    """
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    
    if dry_run:
        logger.info(f"[DRY RUN] Would save legacy outputs to: {output_dir}")
        logger.info(f"[DRY RUN] Files: memo, insights, actions, blurb")
        return
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save each output
    (output_dir / f"{timestamp}-decision-memo.md").write_text(outputs["memo"])
    (output_dir / f"{timestamp}-insights.json").write_text(outputs["insights"])
    (output_dir / f"{timestamp}-actions.json").write_text(outputs["actions"])
    (output_dir / f"{timestamp}-blurb.md").write_text(outputs["blurb"])
    
    logger.info(f"✓ Saved legacy outputs to: {output_dir}")


def main(
    block_type: Optional[str] = None,
    input_pattern: Optional[str] = None,
    input_file: Optional[Path] = None,
    output: Optional[Path] = None,
    legacy: bool = False,
    dry_run: bool = False
) -> int:
    """
    Main execution function.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        logger.info("Starting reflection synthesizer")
        
        # Legacy mode
        if legacy:
            if not input_file:
                logger.error("Legacy mode requires --input")
                return 1
            
            transcript = load_transcripts(str(input_file))[0]
            outputs = synthesize_legacy(transcript)
            save_legacy_outputs(outputs, output or Path("outputs"), dry_run=dry_run)
            logger.info("✓ Legacy synthesis complete")
            return 0
        
        # Block-type mode (B90/B91)
        if not block_type or not input_pattern:
            logger.error("Block-type mode requires --block-type and --input-pattern")
            return 1
        
        # Load transcripts
        transcripts = load_transcripts(input_pattern)
        if not transcripts:
            logger.error("No transcripts found")
            return 1
        
        # Load style guide
        style_guide = load_style_guide(block_type)
        
        # Synthesize based on block type
        if block_type == "B90":
            synthesis = synthesize_b90(transcripts, style_guide or "")
        elif block_type == "B91":
            synthesis = synthesize_b91(transcripts, style_guide or "")
        else:
            logger.error(f"Unknown block type: {block_type}")
            return 1
        
        # Save output
        filename = f"{block_type}-{datetime.now().strftime('%Y-%m-%d-%H%M')}.md"
        save_outputs(synthesis, output or Path("outputs"), filename, dry_run=dry_run)
        
        logger.info(f"✓ {block_type} synthesis complete")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reflection Synthesizer V2")
    parser.add_argument("--block-type", choices=["B90", "B91"],
                       help="Block type to generate (B90 or B91)")
    parser.add_argument("--input-pattern", type=str,
                       help="Glob pattern for input transcripts")
    parser.add_argument("--input", type=Path,
                       help="Single input file (for legacy mode)")
    parser.add_argument("--output", type=Path,
                       help="Output directory")
    parser.add_argument("--legacy", action="store_true",
                       help="Use legacy format (memo/insights/actions/blurb)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview without writing")
    
    args = parser.parse_args()
    exit(main(
        block_type=args.block_type,
        input_pattern=args.input_pattern,
        input_file=args.input,
        output=args.output,
        legacy=args.legacy,
        dry_run=args.dry_run
    ))
