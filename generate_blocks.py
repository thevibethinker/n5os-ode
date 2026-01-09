import asyncio
import aiohttp
import os
import json
from datetime import datetime

CONVO_ID = "074838b3-3b6f-4e5c-a843-858a7d072141"
MEETING_PATH = "/home/workspace/Personal/Meetings/Inbox/2026-01-06_David-x-Vrijen_[M]"
TRANSCRIPT_PATH = f"{MEETING_PATH}/transcript.jsonl"

async def ask_zo(session, prompt):
    async with session.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
            "content-type": "application/json"
        },
        json={"input": prompt}
    ) as resp:
        return (await resp.json())["output"]

async def main():
    with open(TRANSCRIPT_PATH, 'r') as f:
        transcript = f.read()

    blocks = {
        "B01_DETAILED_RECAP": "/home/workspace/Prompts/Blocks/Generate_B01.prompt.md",
        "B03_STAKEHOLDER_INTELLIGENCE": "/home/workspace/Prompts/Blocks/Generate_B08.prompt.md", # B08 is canonical for Stakeholder Intel
        "B03_DECISIONS": "/home/workspace/Prompts/Blocks/Generate_B03.prompt.md",
        "B05_ACTION_ITEMS": "/home/workspace/Prompts/Blocks/Generate_B05.prompt.md",
        "B06_BUSINESS_CONTEXT": "/home/workspace/Prompts/Blocks/Generate_B06.prompt.md",
        "B07_TONE_AND_CONTEXT": "/home/workspace/Prompts/Blocks/Generate_B15.prompt.md", # B15 is Energy & Sentiment, closest to Tone
        "B14_BLURBS_REQUESTED": "/home/workspace/Prompts/Blocks/Generate_B14.prompt.md",
        "B21_KEY_MOMENTS": "/home/workspace/Prompts/Blocks/Generate_B21.prompt.md",
        "B25_DELIVERABLES": "/home/workspace/Prompts/Blocks/Generate_B25.prompt.md",
        "B26_MEETING_METADATA": "/home/workspace/Prompts/Blocks/Generate_B26.prompt.md",
        "B32_THOUGHT_PROVOKING_IDEAS": "/home/workspace/Prompts/Blocks/Generate_B32.prompt.md"
    }

    async with aiohttp.ClientSession() as session:
        tasks = []
        for block_name, prompt_path in blocks.items():
            with open(prompt_path, 'r') as f:
                prompt_template = f.read()
            
            full_prompt = f"Using the following meeting transcript, generate the intelligence block {block_name}.\n\nTranscript:\n{transcript}\n\nPrompt Instructions:\n{prompt_template}\n\nIMPORTANT: Return ONLY the markdown content for the block, including the YAML frontmatter. Ensure the provenance field in frontmatter is set to {CONVO_ID}."
            tasks.append((block_name, ask_zo(session, full_prompt)))

        results = await asyncio.gather(*[t[1] for t in tasks])
        
        generated_blocks = []
        for (block_name, _), content in zip(tasks, results):
            file_path = f"{MEETING_PATH}/{block_name}.md"
            with open(file_path, 'w') as f:
                f.write(content)
            generated_blocks.append(block_name)
            print(f"Generated {file_path}")

        # Update manifest.json
        manifest_path = f"{MEETING_PATH}/manifest.json"
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        manifest["blocks_generated"]["stakeholder_intelligence"] = True
        manifest["blocks_generated"]["brief"] = True
        manifest["last_updated_by"] = "MG-2_Prompt"
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print("Updated manifest.json")

        # Log to PROCESSING_LOG.jsonl
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "stage": "MG-2",
            "meeting_id": os.path.basename(MEETING_PATH),
            "status": "mg2_completed",
            "blocks_generated": generated_blocks,
            "source": "Meeting Intelligence Generator [MG-2]"
        }
        
        log_path = "/home/workspace/Personal/Meetings/PROCESSING_LOG.jsonl"
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
        print(f"Logged to {log_path}")

if __name__ == "__main__":
    asyncio.run(main())
