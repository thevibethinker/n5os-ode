#!/usr/bin/env python3
"""
Consolidated Email Ingestion Workflow
Orchestrates transcript processing, content mapping, and output generation per N5OS standards
"""
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
import asyncio
import subprocess
from typing import Dict, List, Optional
import threading
import front_matter_manager as fmm  # Assuming it's in same dir

# Setup N5OS logging
LOG_DIR = '/home/workspace/N5/knowledge/logs/Email'
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import our modules
sys.path.append(os.path.dirname(__file__))
from blurb_ticket_generator import BlurbTicketGenerator

class ConsolidatedWorkflow:
    def __init__(self, workspace_dir: str, dry_run: bool = False):
        self.workspace_dir = Path(workspace_dir)
        self.dry_run = dry_run
        self.script_dir = Path(__file__).parent
        
        # Ensure workspace structure
        self.workspace_dir.mkdir(exist_ok=True)
        (self.workspace_dir / "content_maps").mkdir(exist_ok=True)
        (self.workspace_dir / "emails").mkdir(exist_ok=True)
        (self.workspace_dir / "tickets").mkdir(exist_ok=True)
        
        logger.info(f"Initialized workflow in {self.workspace_dir.absolute()}")

    def run_script(self, script_name: str, args: List[str]) -> int:
        """Run N5_mirror script with error handling"""
        script_path = self.script_dir / script_name
        if not script_path.exists():
            logger.error(f"Script not found: {script_path}")
            return 1
            
        cmd = [sys.executable, str(script_path)] + args
        if self.dry_run and "--dry-run" not in args:
            cmd.append("--dry-run")
            
        logger.info(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                logger.error(f"Script failed: {script_name}\nStderr: {result.stderr}")
            else:
                logger.info(f"Script completed: {script_name}")
            return result.returncode
        except Exception as e:
            logger.error(f"Exception running {script_name}: {e}")
            return 1

    def process_transcript(self, transcript_path: str) -> Optional[str]:
        """Step 1: Process transcript into segments"""
        transcript_path = Path(transcript_path)
        if not transcript_path.exists():
            logger.error(f"Transcript not found: {transcript_path}")
            return None
            
        segments_path = self.workspace_dir / "content_maps" / f"{transcript_path.stem}_segments.json"
        
        # Run summarize_segments.py
        args = [str(transcript_path), str(segments_path)]
        if self.run_script("summarize_segments.py", args) != 0:
            return None
            
        return str(segments_path) if segments_path.exists() else None

    def create_content_map(self, segments_path: str, metadata: Dict = None) -> Optional[str]:
        """Step 2: Create JSONL content map from segments"""
        segments_path = Path(segments_path)
        if not segments_path.exists():
            logger.error(f"Segments file not found: {segments_path}")
            return None
            
        # Load segments
        with open(segments_path, 'r') as f:
            segments = json.load(f)
            
        # Create comprehensive content map
        content_map = {
            "source_file": str(segments_path),
            "created": datetime.now().isoformat(),
            "metadata": metadata or {},
            "segments": segments,
            "participants": [],  # To be populated by LLM analysis
            "key_topics": [],
            "action_items": [],
            "decisions": [],
            "follow_up_needed": []
        }
        
        content_map_path = self.workspace_dir / "content_maps" / f"{segments_path.stem.replace('_segments', '')}_content_map.json"
        
        if not self.dry_run:
            with open(content_map_path, 'w') as f:
                json.dump(content_map, f, indent=2)
            logger.info(f"Content map created: {content_map_path.absolute()}")
        else:
            logger.info("Dry run: Content map structure validated but not saved")
            
        return str(content_map_path) if content_map_path.exists() or self.dry_run else None

    async def generate_outputs(self, content_map_path: str) -> Dict:
        """Step 3: Generate all outputs (emails, tickets, blurbs)"""
        content_map_path = Path(content_map_path)
        if not content_map_path.exists():
            logger.error(f"Content map not found: {content_map_path}")
            return {}
            
        # Load content map
        with open(content_map_path, 'r') as f:
            content_map = json.load(f)
            
        # Generate using BlurbTicketGenerator
        generator = BlurbTicketGenerator()
        output_dir = str(self.workspace_dir / "tickets")
        
        results = await generator.process_content_map(content_map, output_dir, self.dry_run)
        
        # Save individual email drafts
        if results.get("follow_up_emails") and not self.dry_run:
            email_dir = self.workspace_dir / "emails"
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for i, email_data in enumerate(results["follow_up_emails"]):
                email_file = email_dir / f"follow_up_{timestamp}_{i+1}.md"
                with open(email_file, 'w') as f:
                    f.write(f"# Follow-up Email - {email_data['recipient']}\n\n")
                    f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
                    f.write(f"**Recipient:** {email_data['recipient']}\n\n")
                    f.write("---\n\n")
                    f.write(email_data['email'])
                logger.info(f"Email draft saved: {email_file.absolute()}")
        
        return results

    def validate_outputs(self, results: Dict) -> bool:
        """Step 4: Validation per N5OS standards"""
        validation_passed = True
        
        # Check required components
        required_keys = ["blurbs", "follow_up_emails", "warm_intro_tickets"]
        for key in required_keys:
            if key not in results:
                logger.error(f"Missing required output: {key}")
                validation_passed = False
                
        # Voice fidelity check (basic)
        for email_data in results.get("follow_up_emails", []):
            email_content = email_data.get("email", "")
            if len(email_content) < 50:
                logger.warning(f"Email may be too short: {len(email_content)} chars")
            if len(email_content) > 2000:
                logger.warning(f"Email may be too long: {len(email_content)} chars")
                
        # Warm intro validation
        for ticket in results.get("warm_intro_tickets", []):
            if not ticket.get("content", {}).get("opportunity", {}).get("connection_rationale"):
                logger.warning(f"Weak connection rationale in ticket {ticket.get('ticket_id', 'unknown')}")
                
        logger.info(f"Validation {'PASSED' if validation_passed else 'FAILED'}")
        return validation_passed

    async def run_full_pipeline(self, transcript_path: str, metadata: Dict = None) -> Dict:
        """Execute complete workflow pipeline"""
        logger.info("=== Starting Consolidated Email Ingestion Workflow ===")
        
        # Step 1: Process transcript
        logger.info("Step 1: Processing transcript into segments")
        segments_path = self.process_transcript(transcript_path)
        if not segments_path:
            logger.error("Failed at transcript processing step")
            return {}
            
        # Step 2: Create content map
        logger.info("Step 2: Creating content map")
        content_map_path = self.create_content_map(segments_path, metadata)
        if not content_map_path:
            logger.error("Failed at content map creation step")
            return {}
            
        # Step 3: Generate outputs
        logger.info("Step 3: Generating emails, tickets, and blurbs")
        results = await self.generate_outputs(content_map_path)
        if not results:
            logger.error("Failed at output generation step")
            return {}
            
        # Step 4: Validate
        logger.info("Step 4: Validating outputs")
        if not self.validate_outputs(results):
            logger.warning("Validation warnings detected - review outputs")
            
        logger.info("=== Workflow Completed Successfully ===")
        logger.info(f"Workspace: {self.workspace_dir.absolute()}")
        
        return {
            "segments_path": segments_path,
            "content_map_path": content_map_path,
            "results": results,
            "workspace": str(self.workspace_dir.absolute())
        }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Consolidated Email Ingestion Workflow")
    parser.add_argument("transcript", help="Path to transcript file")
    parser.add_argument("--workspace", default="./email_workflow_output", 
                       help="Workspace directory for outputs")
    parser.add_argument("--metadata", help="JSON metadata file")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Preview workflow without saving files")
    
    args = parser.parse_args()
    
    # Load metadata if provided
    metadata = {}
    if args.metadata and os.path.exists(args.metadata):
        with open(args.metadata, 'r') as f:
            metadata = json.load(f)
    
    # Initialize workflow
    workflow = ConsolidatedWorkflow(args.workspace, dry_run=args.dry_run)
    
    # Run pipeline
    try:
        results = asyncio.run(workflow.run_full_pipeline(args.transcript, metadata))
        
        if results:
            print(f"\n=== Pipeline Summary ===")
            print(f"Workspace: {results['workspace']}")
            print(f"Segments: {results.get('segments_path', 'N/A')}")
            print(f"Content Map: {results.get('content_map_path', 'N/A')}")
            
            pipeline_results = results.get('results', {})
            print(f"Blurbs: {len(pipeline_results.get('blurbs', []))}")
            print(f"Follow-up Emails: {len(pipeline_results.get('follow_up_emails', []))}")
            print(f"Warm Intro Tickets: {len(pipeline_results.get('warm_intro_tickets', []))}")
            
            if args.dry_run:
                print("\nDry run completed - no files saved")
            
            return 0
        else:
            logger.error("Pipeline failed")
            return 1
            
    except Exception as e:
        logger.error(f"Pipeline exception: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())