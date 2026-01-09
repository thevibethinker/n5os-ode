import os
import json
import requests
import asyncio
import aiohttp
from pathlib import Path

ZO_TOKEN = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
API_URL = "https://api.zo.computer/zo/ask"

async def process_meeting(session, meeting_path):
    meeting_name = os.path.basename(meeting_path)
    print(f"Processing: {meeting_name}")
    
    prompt = f"""You are an expert content strategist working on a meeting folder.
Folder: file '{meeting_path}'

Your task is to execute the 'Blurb Generator' protocol for this meeting.

STEP 1: Load Meeting Context
Check for:
- B14_BLURBS_REQUESTED.md or .jsonl
- B01_DETAILED_RECAP.md
- B21_KEY_MOMENTS.md
- B08_STAKEHOLDER_INTELLIGENCE.md
- B25_DELIVERABLES.md
- manifest.json

STEP 2: PHASE 0 SELECTIVITY GATE
Decide if a blurb is needed per 'file 'Prompts/Blurb-Generator.prompt.md''.
If skipped, respond with: "SKIP: [Reason]"

STEP 3: GENERATION
If needed, generate the B14_BLURBS.md content following the protocol.
Include:
- Raw Blurb
- Forwardable Email Wrapper
- Fact Verification Status table

STEP 4: SAVE
Save the output to file '{meeting_path}/B14_BLURBS.md'.

Final output: A brief confirmation of what you did (or why you skipped)."""

    try:
        async with session.post(
            API_URL,
            headers={"authorization": ZO_TOKEN, "content-type": "application/json"},
            json={"input": prompt},
            timeout=300
        ) as resp:
            if resp.status == 200:
                res_json = await resp.json()
                return meeting_name, res_json.get("output", "No output")
            else:
                return meeting_name, f"Error: {resp.status}"
    except Exception as e:
        return meeting_name, f"Exception: {str(e)}"

async def main():
    meetings = [
        "/home/workspace/Personal/Meetings/Inbox/2026-01-08_Real-Raw-Test_[M]",
        "/home/workspace/Personal/Meetings/Inbox/2026-01-09_Discovery-Session-V_[M]",
        "/home/workspace/Personal/Meetings/Inbox/2026-01-09_Ivor-Stratford-x-Vrijen-Attawar_[M]",
        "/home/workspace/Personal/Meetings/Inbox/2026-01-09_ilse_x_vrijen_[M]",
        "/home/workspace/Personal/Meetings/Inbox/2026-01-09_Daily-team-stand-up_[M]",
        "/home/workspace/Personal/Meetings/Inbox/2026-01-08_careerspan_founders_powwow_call_[M]",
        "/home/workspace/Personal/Meetings/Inbox/2026-01-11_Actual-Raw-Meeting_[M]",
        "/home/workspace/Personal/Meetings/Inbox/2026-01-09_ilse_x_vrijen__[M]"
    ]
    
    async with aiohttp.ClientSession() as session:
        # Run in batches of 3 to avoid overwhelming
        batch_size = 3
        results = []
        for i in range(0, len(meetings), batch_size):
            batch = meetings[i:i+batch_size]
            batch_results = await asyncio.gather(*[process_meeting(session, m) for m in batch])
            results.extend(batch_results)
            
    print("\n=== BATCH RESULTS ===")
    for name, status in results:
        print(f"[{name}]: {status[:200]}...")

if __name__ == "__main__":
    asyncio.run(main())
