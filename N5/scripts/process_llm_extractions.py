#!/usr/bin/env python3
"""
Batch LLM Extraction Processor
Processes all pending extraction requests for a meeting using Zo's conversation LLM.

This script displays all pending extraction requests and provides instructions
for having the conversation LLM (Zo's AI) process them.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def process_meeting_extractions(meeting_id: str):
    """
    Process all LLM extraction requests for a specific meeting.
    
    Args:
        meeting_id: The meeting identifier (e.g., 'sofia-2025-10-09')
    """
    meeting_dir = Path(f"/home/workspace/Personal/Meetings/{meeting_id}")
    request_dir = meeting_dir / "extraction_requests"
    
    if not request_dir.exists():
        print(f"❌ No extraction requests found for meeting: {meeting_id}")
        print(f"Expected directory: {request_dir}")
        return
    
    # Find all pending requests (those without responses)
    request_files = sorted(request_dir.glob("request_*.json"))
    pending_requests = []
    
    for request_file in request_files:
        request_id = request_file.stem.replace("request_", "")
        response_file = request_dir / f"response_{request_id}.json"
        
        if not response_file.exists():
            with open(request_file, 'r') as f:
                request_data = json.load(f)
                pending_requests.append({
                    "file": request_file,
                    "response_file": response_file,
                    "data": request_data
                })
    
    if not pending_requests:
        print(f"✅ All extraction requests have been processed for meeting: {meeting_id}")
        print(f"Total requests: {len(request_files)}")
        return
    
    print(f"\n📋 Found {len(pending_requests)} pending extraction requests for meeting: {meeting_id}")
    print(f"=" * 80)
    
    # Display each pending request
    for i, req in enumerate(pending_requests, 1):
        print(f"\n### Request {i}/{len(pending_requests)}")
        print(f"Request ID: {req['data']['request_id']}")
        print(f"Timestamp: {req['data']['timestamp']}")
        print(f"\n**System Prompt:**")
        print(req['data']['system_prompt'])
        print(f"\n**User Prompt (first 300 chars):**")
        print(req['data']['user_prompt'][:300] + "...")
        print(f"\n**Response should be written to:**")
        print(f"`{req['response_file']}`")
        print("-" * 80)
    
    # Generate batch processing instructions
    print(f"\n\n🤖 TO PROCESS THESE REQUESTS:")
    print(f"=" * 80)
    print(f"\nAsk Zo's LLM to process each request by saying:")
    print(f'\n"Please process the {len(pending_requests)} extraction requests in:')
    print(f'{request_dir}')
    print(f'\nFor each request_*.json file, analyze the transcript according to the prompts')
    print(f'and write the JSON response to the corresponding response_*.json file."')
    print(f"\n" + "=" * 80)
    
    # Save a batch processing instruction file
    instruction_file = meeting_dir / "LLM_PROCESSING_NEEDED.md"
    with open(instruction_file, 'w') as f:
        f.write(f"# LLM Processing Instructions for Meeting: {meeting_id}\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
        f.write(f"## Pending Requests: {len(pending_requests)}\n\n")
        f.write(f"### Request Directory\n")
        f.write(f"`{request_dir}`\n\n")
        f.write(f"### Instructions\n\n")
        f.write(f"Process each `request_*.json` file and write structured JSON responses to the corresponding `response_*.json` file.\n\n")
        f.write(f"### Request Details\n\n")
        
        for i, req in enumerate(pending_requests, 1):
            f.write(f"#### Request {i}: {req['data']['request_id']}\n\n")
            f.write(f"- **System**: {req['data']['system_prompt'][:200]}...\n")
            f.write(f"- **Response File**: `{req['response_file']}`\n\n")
    
    print(f"\n📄 Instructions saved to: {instruction_file}")
    print(f"\nYou can also manually review requests in: {request_dir}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 process_llm_extractions.py <meeting_id>")
        print("\nExample:")
        print("python3 process_llm_extractions.py sofia-2025-10-09")
        sys.exit(1)
    
    meeting_id = sys.argv[1]
    process_meeting_extractions(meeting_id)

if __name__ == "__main__":
    main()
