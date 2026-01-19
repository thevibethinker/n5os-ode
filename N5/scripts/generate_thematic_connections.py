import sqlite3
import json
import os
import requests
import asyncio
import aiohttp
from typing import List, Dict

# Configuration
DB_PATH = "/home/workspace/N5/data/positions.db"
ASK_API_URL = "https://api.zo.computer/zo/ask"
IDENTITY_TOKEN = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")

async def generate_description(session, pos_a, pos_b):
    prompt = f"""Position A: "{pos_a['title']}"
Insight A: "{pos_a['insight']}"

Position B: "{pos_b['title']}"
Insight B: "{pos_b['insight']}"

These positions are connected in V's intellectual map. In 3-6 words, describe the thematic thread that connects them.
Focus on the intellectual relationship, not generic terms. Use lowercase and be concise.

Good examples: "hiring signal authenticity", "AI trust erosion", "market dysfunction patterns", "self-knowledge as constraint"
Bad examples: "related ideas", "similar topics", "both about hiring"

Return ONLY the 3-6 word description."""

    try:
        async with session.post(
            ASK_API_URL,
            headers={
                "authorization": IDENTITY_TOKEN,
                "content-type": "application/json"
            },
            json={"input": prompt}
        ) as resp:
            data = await resp.json()
            description = data.get("output", "").strip().strip('"').strip("'")
            # Basic validation/cleanup
            description = description.split('\n')[0] # Take first line if multi-line
            return description
    except Exception as e:
        print(f"Error calling LLM for {pos_a['id']} -> {pos_b['id']}: {e}")
        return None

async def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Load all positions into memory for easy access
    cursor.execute("SELECT id, title, insight, connections FROM positions")
    positions = {row['id']: dict(row) for row in cursor.fetchall()}

    # Collect all connections to process
    tasks = []
    connection_map = [] # To keep track of which result goes where

    print("Collecting connections to analyze...")
    for pid, pos in positions.items():
        if not pos['connections']:
            continue
        
        try:
            conns = json.loads(pos['connections'])
        except:
            continue

        for c in conns:
            # Handle both object and string formats
            if isinstance(c, dict):
                target_id = c.get('target_id')
            elif isinstance(c, str):
                target_id = c
            else:
                continue

            if target_id in positions:
                # To avoid duplicate work if A->B and B->A exist (though they might have different descriptions)
                # But here we process them as directed connections as the schema suggests.
                connection_map.append({
                    "source_id": pid,
                    "target_id": target_id,
                    "original_conn": c
                })
                tasks.append((pid, target_id))

    print(f"Found {len(tasks)} connections to process.")

    # Process in batches to respect API limits and concurrency
    batch_size = 10
    results = []
    
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1} ({i} to {min(i+batch_size, len(tasks))})...")
            
            batch_tasks = []
            for src_id, tgt_id in batch:
                batch_tasks.append(generate_description(session, positions[src_id], positions[tgt_id]))
            
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
            # Small sleep to be nice
            await asyncio.sleep(0.5)

    # Apply results back to positions
    print("Enriching database...")
    processed_count = 0
    for i, desc in enumerate(results):
        if desc:
            info = connection_map[i]
            source_id = info['source_id']
            target_id = info['target_id']
            
            # Find the connection in the source's connections list
            source_conns = json.loads(positions[source_id]['connections'])
            updated = False
            for idx, c in enumerate(source_conns):
                # Handle dictionary
                if isinstance(c, dict) and c.get('target_id') == target_id:
                    c['thematic_description'] = desc
                    updated = True
                    break
                # Handle string - convert to dictionary
                elif isinstance(c, str) and c == target_id:
                    source_conns[idx] = {
                        "target_id": target_id,
                        "relationship": "related",
                        "thematic_description": desc
                    }
                    updated = True
                    break
            
            if updated:
                positions[source_id]['connections'] = json.dumps(source_conns)
                processed_count += 1

    # Save to DB
    for pid, pos in positions.items():
        cursor.execute(
            "UPDATE positions SET connections = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (pos['connections'], pid)
        )
    
    conn.commit()
    conn.close()
    print(f"Done! Enriched {processed_count} connections.")

if __name__ == "__main__":
    asyncio.run(main())
