#!/usr/bin/env python3
"""Import W1 block registry into W2 database"""

import json
import sqlite3
from pathlib import Path

# Paths
REGISTRY_PATH = Path('/home/.z/workspaces/con_HppHMdNQjer5YGYG/W1_DELIVERABLE_2_master_registry.json')
DB_PATH = Path('/home/workspace/Intelligence/blocks.db')

def import_blocks():
    # Load registry
    with open(REGISTRY_PATH, 'r') as f:
        registry = json.load(f)
    
    blocks = registry.get('blocks', {})
    print(f"Found {len(blocks)} blocks in registry")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    imported = 0
    skipped = 0
    
    for block_id, block_data in blocks.items():
        # Extract block number from ID (e.g., "B01" -> 1)
        try:
            block_num = int(block_id[1:])
        except:
            print(f"Warning: Could not parse block number from {block_id}")
            continue
        
        # Check if block already exists
        cursor.execute("SELECT block_id FROM blocks WHERE block_id = ?", (block_id,))
        if cursor.fetchone():
            print(f"  Skip {block_id}: Already exists")
            skipped += 1
            continue
        
        # Prepare block data
        name = block_data.get('name', block_data.get('block_name', 'Unknown'))
        category = block_data.get('category', 'unknown')
        priority = block_data.get('priority', 'MEDIUM')
        description = block_data.get('description', '')
        
        # Convert sections array to JSON string
        sections = json.dumps(block_data.get('sections', []))
        
        # Generation prompt
        prompt_sections = block_data.get('prompt_sections', [])
        generation_prompt = '\n\n'.join(prompt_sections) if prompt_sections else ''
        
        # Validation rubric (extract from block or use default)
        validation_rubric = json.dumps({
            'required_sections': block_data.get('sections', []),
            'min_length': 100,
            'checks': ['no_placeholders', 'has_content', 'proper_structure']
        })
        
        # Meeting types
        meeting_types = json.dumps(block_data.get('meeting_types', []))
        
        # Insert into database
        cursor.execute("""
            INSERT INTO blocks (
                block_id, block_number, name, category, priority,
                description, sections, generation_prompt, validation_rubric,
                meeting_types, output_format, version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            block_id,
            block_num,
            name,
            category,
            priority,
            description,
            sections,
            generation_prompt,
            validation_rubric,
            meeting_types,
            'markdown',
            '1.0.0'
        ))
        
        print(f"  ✓ Imported {block_id}: {name}")
        imported += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Import complete:")
    print(f"   Imported: {imported}")
    print(f"   Skipped: {skipped}")
    print(f"   Total in DB: {imported + skipped}")

if __name__ == '__main__':
    import_blocks()
