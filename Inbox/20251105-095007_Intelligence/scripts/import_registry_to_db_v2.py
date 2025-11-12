#!/usr/bin/env python3
"""Import W1 block registry into W2 database - Fixed for actual schema"""

import json
import sqlite3
from pathlib import Path

REGISTRY_PATH = Path('/home/.z/workspaces/con_HppHMdNQjer5YGYG/W1_DELIVERABLE_2_master_registry.json')
DB_PATH = Path('/home/workspace/Intelligence/blocks.db')

def import_blocks():
    with open(REGISTRY_PATH, 'r') as f:
        registry = json.load(f)
    
    blocks = registry.get('blocks', {})
    print(f"📦 Found {len(blocks)} blocks in registry\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    imported = 0
    skipped = 0
    
    for block_id, block_data in blocks.items():
        try:
            block_num = int(block_id[1:])
        except:
            continue
        
        # Check if exists
        cursor.execute("SELECT block_id FROM blocks WHERE block_id = ?", (block_id,))
        if cursor.fetchone():
            print(f"  ⊘ {block_id}: Already exists")
            skipped += 1
            continue
        
        # Extract data
        name = block_data.get('name', block_data.get('block_name', 'Unknown'))
        category = block_data.get('category', 'unknown')
        description = block_data.get('description', '')
        
        # Serialize complex fields
        sections = json.dumps(block_data.get('sections', []))
        prompt_sections = block_data.get('prompt_sections', [])
        generation_prompt = '\n\n'.join(prompt_sections) if prompt_sections else ''
        
        validation_rubric = json.dumps({
            'required_sections': block_data.get('sections', []),
            'min_length': 100,
            'checks': ['no_placeholders', 'has_content']
        })
        
        meeting_types = json.dumps(block_data.get('meeting_types', []))
        
        # Insert with actual schema columns
        cursor.execute("""
            INSERT INTO blocks (
                block_id, block_number, name, category,
                description, sections, generation_prompt, validation_rubric,
                meeting_types, output_format, version, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            block_id, block_num, name, category,
            description, sections, generation_prompt, validation_rubric,
            meeting_types, 'markdown', '1.0.0'
        ))
        
        print(f"  ✓ {block_id}: {name}")
        imported += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Import complete:")
    print(f"   Imported: {imported}")
    print(f"   Skipped: {skipped}")
    print(f"   Total: {imported + skipped}")

if __name__ == '__main__':
    import_blocks()
