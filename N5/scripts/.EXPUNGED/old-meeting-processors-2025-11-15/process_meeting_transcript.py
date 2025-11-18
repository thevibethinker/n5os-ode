#!/usr/bin/env python3
"""
Meeting Transcript Processor - Simple Delegation to Zo

This script prepares a meeting transcript and creates a request file for Zo to process.
Zo will semantically analyze the transcript and generate all intelligence outputs.

NO REGEX PARSING. NO STUBS. NO LLM SIMULATION.
Just delegates to Zo (the actual LLM) for semantic processing.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
MEETINGS_DIR = WORKSPACE / "Careerspan" / "Meetings"


def convert_docx_to_txt(docx_path: Path) -> Path:
    """Convert .docx to .txt if needed."""
    txt_path = docx_path.with_suffix('.txt')
    
    if txt_path.exists():
        logger.info(f"Text version already exists: {txt_path}")
        return txt_path
    
    logger.info(f"Converting {docx_path} to text...")
    import subprocess
    
    try:
        subprocess.run(
            ['pandoc', str(docx_path), '-t', 'plain', '-o', str(txt_path)],
            check=True,
            capture_output=True
        )
        logger.info(f"✓ Converted to {txt_path}")
        return txt_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Pandoc conversion failed: {e.stderr.decode()}")
        raise


def create_meeting_directory(transcript_path: Path, meeting_date: str, meeting_type: str, stakeholder: str) -> Path:
    """Create output directory for meeting intelligence."""
    # Format: YYYY-MM-DD_HHMM_type_stakeholder
    dir_name = f"{meeting_date}_0000_{meeting_type}_{stakeholder}"
    output_dir = MEETINGS_DIR / dir_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create INTELLIGENCE subdirectory
    intelligence_dir = output_dir / "INTELLIGENCE"
    intelligence_dir.mkdir(exist_ok=True)
    
    # Copy transcript to output directory
    transcript_dest = output_dir / "transcript.txt"
    if not transcript_dest.exists():
        import shutil
        shutil.copy2(transcript_path, transcript_dest)
        logger.info(f"✓ Transcript copied to {transcript_dest}")
    
    return output_dir


def create_processing_request(transcript_path: Path, output_dir: Path, meeting_type: str) -> Path:
    """Create a request file for Zo to process."""
    request_file = output_dir / "_PROCESSING_REQUEST.md"
    
    transcript_content = transcript_path.read_text(encoding='utf-8')
    
    request_content = f"""# MEETING PROCESSING REQUEST

**Timestamp**: {datetime.utcnow().isoformat()}Z
**Transcript**: {transcript_path}
**Output Directory**: {output_dir}
**Meeting Type**: {meeting_type}

---

## INSTRUCTIONS FOR ZO

Please semantically analyze the transcript below and generate the following intelligence files in `{output_dir / 'INTELLIGENCE'}`:

### Required Outputs:

1. **action-items.md** - Extract all action items with:
   - Owner (actual person's name from transcript)
   - Deadline (inferred from context)
   - Priority level
   - Context/rationale
   - Categorize by timeframe (Immediate, Short-term, Medium-term, Long-term)

2. **decisions.md** - Extract all decisions made with:
   - Clear decision statement
   - Who decided
   - Rationale/reasoning
   - Impact assessment
   - Category (Strategic, Tactical, Resource Allocation, etc.)

3. **detailed-notes.md** - Extract key insights including:
   - Important quotes with attribution
   - Pain points identified
   - Advice and recommendations shared
   - Realizations/aha moments
   - Market insights
   - Numbers, metrics, facts mentioned

### Requirements:

- **Use REAL content from the transcript** - no generic stubs or placeholders
- **Attribute quotes accurately** - use actual names from the transcript
- **Extract semantic meaning** - understand context, not just keyword matching
- **Be comprehensive** - don't miss important items
- **Format professionally** - use clear markdown structure

---

## TRANSCRIPT

```
{transcript_content}
```

---

**PROCESS THIS NOW**
"""
    
    request_file.write_text(request_content, encoding='utf-8')
    logger.info(f"✓ Processing request created: {request_file}")
    
    return request_file


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python process_meeting_transcript.py <transcript_path> [meeting_type] [stakeholder_slug]")
        print()
        print("Example:")
        print("  python process_meeting_transcript.py transcript.txt sales allie-cialeo")
        sys.exit(1)
    
    transcript_path = Path(sys.argv[1]).resolve()
    meeting_type = sys.argv[2] if len(sys.argv) > 2 else "general"
    stakeholder = sys.argv[3] if len(sys.argv) > 3 else "meeting"
    
    if not transcript_path.exists():
        logger.error(f"Transcript not found: {transcript_path}")
        sys.exit(1)
    
    # Convert docx to txt if needed
    if transcript_path.suffix.lower() in ['.docx', '.doc']:
        transcript_path = convert_docx_to_txt(transcript_path)
    
    # Get meeting date
    meeting_date = datetime.now().strftime('%Y-%m-%d')
    
    # Create output directory
    logger.info(f"Creating meeting directory for {stakeholder} ({meeting_type})...")
    output_dir = create_meeting_directory(transcript_path, meeting_date, meeting_type, stakeholder)
    logger.info(f"✓ Output directory: {output_dir}")
    
    # Create processing request for Zo
    request_file = create_processing_request(transcript_path, output_dir, meeting_type)
    
    print()
    print("=" * 80)
    print("✅ MEETING PROCESSING REQUEST CREATED")
    print("=" * 80)
    print()
    print(f"📁 Output Directory: {output_dir}")
    print(f"📄 Request File: {request_file}")
    print()
    print("🤖 NEXT STEP: Open the request file and Zo will process it automatically.")
    print()
    print(f"   Open: file '{request_file.relative_to(WORKSPACE)}'")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
