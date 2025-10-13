#!/usr/bin/env python3
"""
On-demand deliverable generator for processed meetings.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
MEETINGS_DIR = WORKSPACE / "Careerspan" / "Meetings"

async def generate_deliverables(
    meeting_folder: str,
    deliverable_types: List[str],
    knowledge_base: Dict[str, Any] = None
):
    """
    Generate requested deliverables for a processed meeting.
    """
    logger.info(f"Generating deliverables for: {meeting_folder}")
    logger.info(f"Requested: {', '.join(deliverable_types)}")
    
    # Find meeting directory
    meeting_dir = MEETINGS_DIR / meeting_folder
    if not meeting_dir.exists():
        # Try finding by partial match
        matches = list(MEETINGS_DIR.glob(f"*{meeting_folder}*"))
        if len(matches) == 1:
            meeting_dir = matches[0]
        else:
            raise ValueError(f"Meeting folder not found: {meeting_folder}")
    
    # Load transcript
    transcript_file = meeting_dir / "transcript.txt"
    if not transcript_file.exists():
        raise ValueError(f"Transcript not found: {transcript_file}")
    
    transcript_content = transcript_file.read_text(encoding='utf-8')
    
    # Load metadata
    metadata_file = meeting_dir / "_metadata.json"
    meeting_info = {}
    if metadata_file.exists():
        metadata = json.loads(metadata_file.read_text())
        meeting_info = {
            "date": metadata.get("meeting_date"),
            "participants": metadata.get("participants", []),
            "meeting_types": metadata.get("meeting_types", []),
        }
    
    # Load knowledge base if not provided
    if knowledge_base is None:
        from deliverable_orchestrator import DeliverableOrchestrator
        temp_orch = DeliverableOrchestrator(transcript_content, meeting_info, {})
        knowledge_base = temp_orch._load_knowledge_base()
    
    # Create deliverables directory
    deliverables_dir = meeting_dir / "DELIVERABLES"
    deliverables_dir.mkdir(exist_ok=True)
    
    # Generate each requested deliverable
    generated = []
    
    for deliverable_type in deliverable_types:
        try:
            logger.info(f"Generating {deliverable_type}...")
            
            if deliverable_type == "blurb":
                from blocks.deliverables import blurb_generator
                output_dir = deliverables_dir / "blurbs"
                output_dir.mkdir(exist_ok=True)
                path = await blurb_generator.generate_blurb(
                    transcript_content,
                    meeting_info,
                    knowledge_base,
                    output_dir
                )
                generated.append({"type": "blurb", "path": str(path)})
                logger.info(f"✓ Blurb generated: {path}")
                
            elif deliverable_type == "follow_up_email":
                # Use command-based email generator (SSOT)
                logger.info("Generating follow-up email via command system...")
                
                # Prepare context for command
                context_note = f"""
Generate follow-up email for meeting.

Context:
- Meeting folder: {meeting_dir}
- Transcript available at: {meeting_dir / 'transcript.txt'}
- Meeting info: {json.dumps(meeting_info, indent=2)}

Reference: command 'N5/commands/follow-up-email-generator.md'

Generate the email following all style constraints from:
file 'N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md'

Save output to: {meeting_dir}/follow-up-email-draft.md
"""
                
                # Log that this requires manual invocation for now
                logger.info("NOTE: Follow-up email generation uses command-based workflow.")
                logger.info("Command file: N5/commands/follow-up-email-generator.md")
                logger.info(f"Context for generation: {meeting_dir}")
                
                # Create placeholder file indicating command-based generation needed
                placeholder_path = meeting_dir / "follow-up-email-draft.md"
                with open(placeholder_path, 'w') as f:
                    f.write("# Follow-Up Email Draft\n\n")
                    f.write("**Status:** Pending generation via command system\n\n")
                    f.write("To generate:\n")
                    f.write(f"1. Load command 'N5/commands/follow-up-email-generator.md'\n")
                    f.write(f"2. Reference meeting folder: {meeting_dir}\n")
                    f.write(f"3. Use transcript: {meeting_dir / 'transcript.txt'}\n")
                    f.write(f"4. Apply style constraints: N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md\n\n")
                    f.write(context_note)
                
                generated.append({"type": "follow_up_email", "path": str(placeholder_path)})
                logger.info(f"✓ Follow-up email placeholder created: {placeholder_path}")
                logger.info("  Run command-based generator to complete email draft")
                
            elif deliverable_type == "one_pager_memo":
                from blocks.deliverables import one_pager_memo_generator
                output_dir = deliverables_dir / "one_pagers"
                output_dir.mkdir(exist_ok=True)
                path = await one_pager_memo_generator.generate_one_pager_memo(
                    transcript_content,
                    meeting_info,
                    knowledge_base,
                    output_dir
                )
                generated.append({"type": "one_pager_memo", "path": str(path)})
                logger.info(f"✓ One-pager generated: {path}")
                
            elif deliverable_type == "proposal_pricing":
                from blocks.deliverables import proposal_pricing_generator
                output_dir = deliverables_dir / "proposals_pricing"
                output_dir.mkdir(exist_ok=True)
                path = await proposal_pricing_generator.generate_proposal_pricing(
                    transcript_content,
                    meeting_info,
                    knowledge_base,
                    output_dir
                )
                generated.append({"type": "proposal_pricing", "path": str(path)})
                logger.info(f"✓ Proposal/pricing generated: {path}")
                
            else:
                logger.warning(f"Unknown deliverable type: {deliverable_type}")
                
        except Exception as e:
            logger.error(f"Failed to generate {deliverable_type}: {e}", exc_info=True)
    
    # Update metadata
    if metadata_file.exists():
        metadata = json.loads(metadata_file.read_text())
        metadata["deliverables_generated"] = True
        metadata["generated_deliverables"] = generated
        metadata_file.write_text(json.dumps(metadata, indent=2))
    
    return generated

async def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate deliverables for a processed meeting")
    parser.add_argument("meeting_folder", help="Name of the meeting folder")
    parser.add_argument("--deliverables", help="Comma-separated list of deliverables to generate")
    parser.add_argument("--recommended", action="store_true", help="Generate all recommended deliverables")
    parser.add_argument("--all", action="store_true", help="Generate all possible deliverables")
    
    args = parser.parse_args()
    
    # Determine which deliverables to generate
    deliverable_types = []
    
    if args.all:
        deliverable_types = ["blurb", "follow_up_email", "one_pager_memo", "proposal_pricing"]
    elif args.recommended:
        # Load recommendations from metadata
        meeting_dir = MEETINGS_DIR / args.meeting_folder
        if not meeting_dir.exists():
            matches = list(MEETINGS_DIR.glob(f"*{args.meeting_folder}*"))
            if len(matches) == 1:
                meeting_dir = matches[0]
        
        metadata_file = meeting_dir / "_metadata.json"
        if metadata_file.exists():
            metadata = json.loads(metadata_file.read_text())
            recommendations = metadata.get("recommendations", {})
            deliverable_types = [r["type"] for r in recommendations.get("recommended", [])]
        
        if not deliverable_types:
            print("⚠️  No recommendations found. Use --deliverables or --all instead.")
            return
    elif args.deliverables:
        deliverable_types = [d.strip() for d in args.deliverables.split(',')]
    else:
        print("❌ Must specify --deliverables, --recommended, or --all")
        parser.print_help()
        return
    
    print(f"📝 Generating: {', '.join(deliverable_types)}")
    print()
    
    generated = await generate_deliverables(args.meeting_folder, deliverable_types)
    
    print()
    print("=" * 80)
    print(f"✅ Generated {len(generated)} deliverables")
    print("=" * 80)
    for item in generated:
        print(f"  ✓ {item['type']}: {item['path']}")
    print()

if __name__ == "__main__":
    asyncio.run(main())
