#!/usr/bin/env python3
"""Import W1 registry blocks into W2 database - matches actual schema"""

import json
import sqlite3
from pathlib import Path

REGISTRY = '/home/.z/workspaces/con_HppHMdNQjer5YGYG/W1_DELIVERABLE_2_master_registry.json'
DB = '/home/workspace/Intelligence/blocks.db'

with open(REGISTRY) as f:
    registry = json.load(f)

blocks = registry.get('blocks', {})
print(f"📦 Registry has {len(blocks)} blocks\n")

conn = sqlite3.connect(DB)
cursor = conn.cursor()

imported = 0
skipped = 0

for block_id, data in blocks.items():
    try:
        block_num = int(block_id[1:])
    except:
        continue
    
    # Check exists
    cursor.execute("SELECT 1 FROM blocks WHERE block_id = ?", (block_id,))
    if cursor.fetchone():
        print(f"  ⊘ {block_id}")
        skipped += 1
        continue
    
    name = data.get('name', data.get('block_name', 'Unknown'))
    category = data.get('category', 'unknown')
    description = data.get('description', '')
    
    # Build validation rubric from available data
    rubric = {
        'required_sections': data.get('sections', []),
        'min_length': 100
    }
    
    # Insert using ONLY columns that exist in schema
    cursor.execute("""
        INSERT INTO blocks (
            block_id, block_number, name, category,
            description, validation_rubric, output_format
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        block_id,
        block_num,
        name,
        category,
        description,
        json.dumps(rubric),
        'markdown'
    ))
    
    print(f"  ✓ {block_id}: {name}")
    imported += 1

conn.commit()
conn.close()

print(f"\n✅ Imported: {imported}, Skipped: {skipped}, Total: {imported + skipped}")
