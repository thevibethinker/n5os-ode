import os
import json
import argparse
import uuid
from datetime import datetime
from pathlib import Path

LAB_ROOT = Path("/home/workspace/Personal/Knowledge/Lab")
EXPLORATIONS_DIR = LAB_ROOT / "Explorations"
IDEAS_LIST = Path("/home/workspace/Lists/ideas.jsonl")

def promote_idea(idea_id):
    # 1. Find the idea in ideas.jsonl
    target_idea = None
    if IDEAS_LIST.exists():
        with open(IDEAS_LIST, 'r') as f:
            for line in f:
                if not line.strip(): continue
                item = json.loads(line)
                if item.get('id') == idea_id:
                    target_idea = item
                    break
    
    if not target_idea:
        print(f"Error: Idea ID {idea_id} not found.")
        return

    # 2. Create the exploration slug
    title = target_idea.get('title', 'untitled_exploration')
    slug = title.lower().replace(" ", "_").replace(":", "").replace("(", "").replace(")", "").replace("/", "_")[:100]
    timestamp = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"{timestamp}_{slug}"
    folder_path = EXPLORATIONS_DIR / folder_name
    
    os.makedirs(folder_path, exist_ok=True)

    # 3. Initialize the README
    readme_content = f"""---
created: {timestamp}
last_edited: {timestamp}
version: 1.1
provenance: {os.environ.get('CONVERSATION_ID', 'manual')}
idea_id: {idea_id}
---

# Exploration: {title}

## Core Spark
{target_idea.get('body', target_idea.get('title'))}

## Status: ACTIVE
- [ ] Phase 1: Socratic Dialogue
- [ ] Phase 2: Adversarial Stress Test
- [ ] Phase 3: First Principles Decomposition
- [ ] Phase 4: Synthesis & Crystallization

## Reference Materials
- Original Idea: `file 'Lists/ideas.jsonl'` (ID: {idea_id})
- Tags: {", ".join(target_idea.get('tags', []))}
"""
    with open(folder_path / "README.md", 'w') as f:
        f.write(readme_content)

    # 4. Copy templates as stubs
    templates = ["Socratic_Dialogue.md", "Adversarial_Stress_Test.md", "First_Principles.md", "Synthesis.md"]
    for t in templates:
        template_path = LAB_ROOT / "Templates" / t
        if template_path.exists():
            with open(template_path, 'r') as tf:
                content = tf.read()
            with open(folder_path / t, 'w') as outf:
                outf.write(content)

    # 5. Update Lab README
    update_lab_index(timestamp, title, folder_name)

    # 6. Update ideas.jsonl status
    update_idea_status(idea_id, "promoted")

    print(f"Successfully promoted idea to: {folder_path}")
    return folder_path

def update_idea_status(idea_id, status):
    if not IDEAS_LIST.exists():
        return
    
    lines = []
    with open(IDEAS_LIST, 'r') as f:
        for line in f:
            if not line.strip(): continue
            item = json.loads(line)
            if item.get('id') == idea_id:
                item['status'] = status
                item['updated_at'] = datetime.now().isoformat()
            lines.append(json.dumps(item))
            
    with open(IDEAS_LIST, 'w') as f:
        for line in lines:
            f.write(line + "\n")

def update_lab_index(date, title, folder_name):
    index_path = LAB_ROOT / "README.md"
    new_row = f"| {date} | [{title}](./Explorations/{folder_name}/README.md) | Active | Explore |"
    
    if not index_path.exists():
        return

    with open(index_path, 'r') as f:
        lines = f.readlines()
    
    with open(index_path, 'w') as f:
        for line in lines:
            f.write(line)
            if "| :--- | :--- | :--- | :--- |" in line:
                f.write(new_row + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("idea_id", help="The UUID of the idea to promote")
    args = parser.parse_args()
    promote_idea(args.idea_id)


