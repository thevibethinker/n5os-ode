import sqlite3
import json
import re
import os
import requests
import asyncio
import aiohttp
from typing import List, Dict

POSITIONS_DB = "/home/workspace/N5/data/positions.db"
CONTENT_LIBRARY_ROOT = "/home/workspace/Knowledge/content-library/"
ZO_ASK_URL = "https://api.zo.computer/zo/ask"
ZO_TOKEN = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")

def format_paragraphs(text: str) -> str:
    # Basic paragraph splitting: group 2-3 sentences.
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if not sentences:
        return text
    
    paragraphs = []
    current_para = []
    for i, sentence in enumerate(sentences):
        current_para.append(sentence)
        # Split every 2-3 sentences (let's say 2 for shorter blocks)
        if len(current_para) >= 2 or i == len(sentences) - 1:
            paragraphs.append(" ".join(current_para))
            current_para = []
    
    return "\n\n".join(paragraphs)

async def get_references(title: str, insight: str, content_files: List[str]) -> List[Dict]:
    # Use Zo to find relevant content library files
    # We provide a list of sample files and ask Zo to find the best matches
    # Since we can't send all file contents, we'll send the file paths and some context
    
    prompt = f"""
I have a "Position" in a knowledge graph with the following details:
Title: {title}
Insight: {insight}

I want to link this position to relevant documents in the user's Content Library.
Here are the available files in the Content Library:
{chr(10).join(content_files[:200])} 

Task:
1. Select the top 2-3 files that are most semantically related to this position.
2. For each selected file, provide:
   - title: A clean title for the link
   - path: The relative path from Knowledge/content-library/
   - relevance: A brief 1-sentence explanation of why it's related

Respond with a JSON array of objects with keys: title, path, relevance.
If no files are strongly related, respond with an empty array [].
Respond ONLY with the JSON.
"""

    timeout = aiohttp.ClientTimeout(total=120)  # Increase timeout to 2 minutes
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(
                ZO_ASK_URL,
                headers={
                    "authorization": ZO_TOKEN,
                    "content-type": "application/json"
                },
                json={"input": prompt}
            ) as resp:
                data = await resp.json()
                output = data.get("output", "[]")
                try:
                    # Cleanup output if Zo adds markdown fences
                    if "```json" in output:
                        output = output.split("```json")[1].split("```")[0]
                    elif "```" in output:
                        output = output.split("```")[1].split("```")[0]
                    return json.loads(output.strip())
                except:
                    print(f"Failed to parse Zo output for {title}: {output}")
                    return []
        except Exception as e:
            print(f"Request failed for {title}: {e}")
            return []

def get_all_content_files():
    all_files = []
    for root, dirs, files in os.walk(CONTENT_LIBRARY_ROOT):
        for file in files:
            if file.endswith(".md"):
                rel_path = os.path.relpath(os.path.join(root, file), CONTENT_LIBRARY_ROOT)
                all_files.append(rel_path)
    return all_files

async def process_position(db, pos_id, title, insight, content_files):
    print(f"Processing: {title}")
    formatted = format_paragraphs(insight)
    references = await get_references(title, insight, content_files)
    
    cursor = db.cursor()
    cursor.execute(
        "UPDATE positions SET formatted_insight = ?, references_json = ? WHERE id = ?",
        (formatted, json.dumps(references), pos_id)
    )
    db.commit()
    return len(references) > 0

async def main():
    db = sqlite3.connect(POSITIONS_DB)
    cursor = db.cursor()
    # Only process those that haven't been formatted yet to allow resuming
    cursor.execute("SELECT id, title, insight FROM positions WHERE formatted_insight IS NULL")
    positions = cursor.fetchall()
    
    if not positions:
        print("All positions already formatted.")
        return

    content_files = get_all_content_files()
    
    # Process sequentially or in very small batches to avoid timeouts and rate limits
    batch_size = 2
    enriched_count = 0
    with_refs_count = 0
    
    for i in range(0, len(positions), batch_size):
        batch = positions[i:i+batch_size]
        tasks = [process_position(db, pid, title, ins, content_files) for pid, title, ins in batch]
        results = await asyncio.gather(*tasks)
        
        enriched_count += len(batch)
        with_refs_count += sum(1 for r in results if r)
        print(f"Progress: {enriched_count}/{len(positions)} processed. {with_refs_count} with references.")
        
    db.close()
    print(f"DONE. Enriched {enriched_count} positions. {with_refs_count} have references.")

if __name__ == "__main__":
    asyncio.run(main())
