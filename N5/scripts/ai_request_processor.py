#!/usr/bin/env python3
"""
AI Request Processor - Processes pending AI requests by calling Zo's internal API
This script finds pending requests in N5/inbox/ai_requests/ and invokes Zo to execute them.
"""
import json
import logging
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
REQUESTS = WORKSPACE / "N5/inbox/ai_requests"
RESPONSES = WORKSPACE / "N5/inbox/ai_responses"
PROCESSED = REQUESTS / "processed"


def invoke_zo_for_request(req):
    """
    Invoke Zo to process this AI request.
    This uses Zo's internal API to trigger meeting intelligence generation.
    """
    meeting_id = req['inputs'].get('meeting_id')
    transcript_path = req['inputs'].get('transcript_path')
    prompt_name = req['prompt_name']
    
    # Build the command for Zo to execute
    command = f"""
Load file '{prompt_name}.md' and process the transcript at:
{transcript_path}

Meeting ID: {meeting_id}
Meeting Type: {req['inputs'].get('meeting_type', 'external')}

Generate all required blocks according to the prompt specification.
Output directory: {req['output_requirements'].get('output_dir')}

This is an automated request from the meeting pipeline.
"""
    
    logger.info(f"  Invoking Zo for meeting: {meeting_id}")
    logger.info(f"  Prompt: {prompt_name}")
    logger.info(f"  Transcript: {transcript_path}")
    
    # Return the command that should be executed
    return command


def process_request(req_path):
    """Process a single AI request."""
    logger.info(f"Processing: {req_path.name}")
    req = json.load(open(req_path))
    
    # Create initial response
    resp = {
        "request_id": req['request_id'],
        "status": "pending_execution",
        "queued_at": datetime.now(timezone.utc).isoformat(),
        "prompt_name": req['prompt_name'],
        "inputs": req['inputs'],
        "message": "Request queued - awaiting AI execution"
    }
    
    resp_path = RESPONSES / f"{req['request_id']}.json"
    json.dump(resp, open(resp_path, 'w'), indent=2)
    
    # Generate the Zo command
    zo_command = invoke_zo_for_request(req)
    
    # Save the command to a file for the scheduled task to pick up
    command_file = REQUESTS / f"{req['request_id']}_command.txt"
    command_file.write_text(zo_command)
    
    logger.info(f"  ✓ Command file created: {command_file.name}")
    logger.info(f"  Note: This request needs to be picked up by the AI queue processor")
    
    # Move request to processed (it's been queued for execution)
    req_path.rename(PROCESSED / req_path.name)
    
    return resp_path, command_file


def main():
    logger.info("AI Request Processor - Queueing requests for Zo")
    REQUESTS.mkdir(parents=True, exist_ok=True)
    RESPONSES.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    
    reqs = sorted(REQUESTS.glob("*.json"))
    if not reqs:
        logger.info("No pending requests")
        return 0
    
    logger.info(f"Found {len(reqs)} request(s)")
    
    processed_count = 0
    for r in reqs:
        try:
            resp_path, cmd_file = process_request(r)
            processed_count += 1
        except Exception as e:
            logger.error(f"Error processing {r.name}: {e}", exc_info=True)
    
    logger.info(f"\n✓ Queued {processed_count}/{len(reqs)} request(s)")
    logger.info(f"✓ Command files created in {REQUESTS}")
    logger.info(f"\nNOTE: The AI queue processor scheduled task should pick these up and execute them.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
