import os
import json
import asyncio
import aiohttp
from datetime import datetime

ZO_TOKEN = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
LOG_FILE = "/home/workspace/Personal/Meetings/PROCESSING_LOG.jsonl"

async def call_zo(prompt):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": ZO_TOKEN,
                "content-type": "application/json"
            },
            json={"input": prompt}
        ) as resp:
            data = await resp.json()
            return data.get("output", "")

async def process_meeting(target_dir):
    print(f"Processing {target_dir}...")
    
    # 1. Read Transcript
    transcript_path = os.path.join(target_dir, "transcript.jsonl")
    if not os.path.exists(transcript_path):
        print(f"Skipping {target_dir}: No transcript.jsonl")
        return

    with open(transcript_path, "r") as f:
        transcript_content = f.read()
    
    # 2. Generate Blocks
    blocks = [
        "B01_DETAILED_RECAP",
        "B03_STAKEHOLDER_INTELLIGENCE",
        "B03_DECISIONS",
        "B05_ACTION_ITEMS",
        "B06_BUSINESS_CONTEXT",
        "B07_TONE_AND_CONTEXT",
        "B14_BLURBS_REQUESTED",
        "B21_KEY_MOMENTS",
        "B25_DELIVERABLES",
        "B26_MEETING_METADATA",
        "B32_THOUGHT_PROVOKING_IDEAS"
    ]
    
    generated_list = []
    
    for block in blocks:
        file_path = os.path.join(target_dir, f"{block}.md")
        # Only generate if missing
        if os.path.exists(file_path):
            print(f"Block {block} already exists. Skipping.")
            continue
            
        print(f"Generating {block}...")
        
        block_code = block[0:3]
        if block == "B03_STAKEHOLDER_INTELLIGENCE":
            block_code = "B31"
        
        prompt_file = f"/home/workspace/Prompts/Blocks/Generate_{block_code}.prompt.md"
        
        if not os.path.exists(prompt_file):
             prompt = f"Using this transcript:\n{transcript_content}\n\nGenerate the {block}.md file content. Respond ONLY with the markdown content."
        else:
            with open(prompt_file, "r") as f:
                prompt_template = f.read()
            prompt = f"{prompt_template}\n\nTRANSCRIPT:\n{transcript_content}\n\nRespond ONLY with the generated markdown content for {block}.md."
        
        content = await call_zo(prompt)
        
        content = content.strip()
        if content.startswith("```markdown"):
            content = content[11:].strip()
            if content.endswith("```"):
                content = content[:-3].strip()
        elif content.startswith("```"):
            content = content[3:].strip()
            if content.endswith("```"):
                content = content[:-3].strip()
                
        with open(file_path, "w") as f:
            f.write(content)
        
        generated_list.append(block)
        print(f"Finished {block}")

    if not generated_list:
        print(f"No blocks generated for {target_dir}")
        return

    # 3. Update Manifest
    manifest_path = os.path.join(target_dir, "manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        
        manifest.setdefault("blocks_generated", {})
        manifest["blocks_generated"]["stakeholder_intelligence"] = True
        manifest["blocks_generated"]["brief"] = True
        manifest["last_updated_by"] = "MG-2_Prompt"
        manifest["last_updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print("Updated manifest.json")

    # 4. Log to PROCESSING_LOG.jsonl
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "stage": "MG-2",
        "meeting_id": os.path.basename(target_dir),
        "status": "mg2_completed",
        "blocks_generated": generated_list,
        "source": "Meeting Intelligence Generator [MG-2]"
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    print(f"Logged to PROCESSING_LOG.jsonl for {os.path.basename(target_dir)}")

async def main():
    targets = ["/home/workspace/Personal/Meetings/Inbox/2026-01-08_Testing-Raw-Folder_[M]"]
    for t in targets:
        await process_meeting(t)

if __name__ == "__main__":
    asyncio.run(main())
