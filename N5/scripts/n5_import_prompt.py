#!/usr/bin/env python3
"""
N5 Prompt Import Pipeline
Standardized process for converting personal prompts into N5 commands

Usage:
    python n5_import_prompt.py <prompt_file>
    python n5_import_prompt.py --batch <directory>
"""

import sys
import json
import re
import shutil
from pathlib import Path
from datetime import datetime

# Paths
WORKSPACE = Path("/home/workspace")
COMMANDS_DIR = WORKSPACE / "N5/commands"
COMMANDS_REGISTRY = WORKSPACE / "N5/config/commands.jsonl"
INCANTUM_TRIGGERS = WORKSPACE / "N5/config/incantum_triggers.json"
KNOWLEDGE_DIR = WORKSPACE / "Knowledge"


def extract_metadata(filename):
    """
    Extract metadata from filename pattern:
    Function [NN] - Title v0.0.ext
    """
    # Pattern: Function [NN] - Title v0.0
    match = re.search(r'Function \[(\d+)\] - (.+?) v(\d+\.\d+)', filename)
    
    if match:
        number = match.group(1)
        title = match.group(2)
        version = match.group(3)
        
        # Generate command name from title
        cmd_name = title.lower()
        cmd_name = re.sub(r'[^\w\s-]', '', cmd_name)  # Remove special chars
        cmd_name = re.sub(r'\s+', '-', cmd_name.strip())  # Spaces to hyphens
        cmd_name = re.sub(r'-+', '-', cmd_name)  # Multiple hyphens to single
        
        return {
            "number": number,
            "title": title,
            "version": version,
            "cmd_name": cmd_name
        }
    
    # Pattern: Companion [NN] - Title v0.0
    match = re.search(r'Companion \[(\d+)\] - (.+?) v(\d+\.\d+)', filename)
    
    if match:
        return {
            "type": "companion",
            "number": match.group(1),
            "title": match.group(2),
            "version": match.group(3)
        }
    
    return None


def create_command_file(source_file, metadata):
    """
    Convert prompt file to N5 command format
    """
    cmd_name = metadata["cmd_name"]
    dest_file = COMMANDS_DIR / f"{cmd_name}.md"
    
    # Read source content
    try:
        content = source_file.read_text()
    except:
        content = "[Binary or unreadable content - reference original file]"
    
    # Create N5 command wrapper
    command_content = f"""# `{cmd_name}`

**Version**: {metadata['version']}  
**Summary**: {metadata['title']}  
**Type**: Personal Prompt (imported)

---

## Description

{metadata['title']}

---

## Original Prompt

{content}

---

## Usage

### Via Incantum (Natural Language)
```
N5: {cmd_name.replace('-', ' ')}
N5: {' '.join(cmd_name.split('-')[:3])}
```

### Direct Call
```
N5: {cmd_name}
```

---

## Inputs

[To be documented - analyze prompt for required inputs]

## Outputs

[To be documented - analyze prompt for expected outputs]

---

## Notes

- Imported from: {source_file.name}
- Import date: {datetime.now().strftime('%Y-%m-%d')}
- Original version: {metadata['version']}

---

*Personal prompt integrated into N5 OS*
"""
    
    # Write command file
    dest_file.write_text(command_content)
    
    return dest_file


def register_command(metadata):
    """
    Add command to commands.jsonl registry
    """
    # Load existing commands
    existing = []
    if COMMANDS_REGISTRY.exists():
        with open(COMMANDS_REGISTRY) as f:
            existing = [json.loads(line) for line in f]
    
    # Check if already exists
    existing_names = {cmd['name'] for cmd in existing}
    if metadata['cmd_name'] in existing_names:
        print(f"  ⚠️  Command '{metadata['cmd_name']}' already exists in registry")
        return False
    
    # Create registry entry
    entry = {
        "name": metadata["cmd_name"],
        "version": metadata["version"],
        "workflow": "single-shot",
        "summary": f"{metadata['title']} (personal prompt)",
        "function_file": f"commands/{metadata['cmd_name']}.md",
        "entry_point": "function_file",
        "tags": ["personal", "prompt"] + metadata['cmd_name'].split('-')[:2]
    }
    
    # Append to registry
    with open(COMMANDS_REGISTRY, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    return True


def create_incantum_triggers(metadata):
    """
    Add natural language triggers for command
    """
    # Load existing triggers
    with open(INCANTUM_TRIGGERS) as f:
        triggers = json.load(f)
    
    # Check if already exists
    existing_cmds = {t['command'] for t in triggers}
    if metadata['cmd_name'] in existing_cmds:
        print(f"  ⚠️  Triggers for '{metadata['cmd_name']}' already exist")
        return False
    
    # Generate trigger phrases
    words = metadata['cmd_name'].split('-')
    title_words = metadata['title'].lower().split()
    
    trigger = {
        "trigger": ' '.join(words),
        "aliases": [
            metadata['cmd_name'].replace('-', ' '),
            metadata['title'].lower(),
            ' '.join(words[:3]),  # First 3 words
            ' '.join(title_words[:3])  # First 3 words of title
        ],
        "command": metadata['cmd_name']
    }
    
    # Add trigger
    triggers.append(trigger)
    
    # Write back
    with open(INCANTUM_TRIGGERS, 'w') as f:
        json.dump(triggers, f, indent=2)
    
    return True


def import_companion(source_file, metadata):
    """
    Import companion file to Knowledge/
    """
    dest = KNOWLEDGE_DIR / source_file.name
    
    if dest.exists():
        print(f"  ⚠️  {source_file.name} already exists in Knowledge/")
        return False
    
    shutil.copy(str(source_file), str(dest))
    return True


def import_prompt(source_file):
    """
    Main import pipeline for a single prompt
    """
    print(f"\n{'='*60}")
    print(f"Importing: {source_file.name}")
    print(f"{'='*60}\n")
    
    # Step 1: Extract metadata
    metadata = extract_metadata(source_file.name)
    if not metadata:
        print("❌ Could not extract metadata from filename")
        print("   Expected format: Function [NN] - Title v0.0.ext")
        return False
    
    # Check if it's a Companion file
    if metadata.get("type") == "companion":
        print("Type: Companion (context file)")
        print(f"Importing to: Knowledge/\n")
        
        success = import_companion(source_file, metadata)
        if success:
            print(f"✓ Imported {source_file.name} to Knowledge/")
            return True
        return False
    
    # It's a Function file
    print(f"Type: Function (command prompt)")
    print(f"Command name: {metadata['cmd_name']}")
    print(f"Version: {metadata['version']}")
    print(f"Title: {metadata['title']}\n")
    
    # Step 2: Create command file
    print("Step 1: Creating command file...")
    cmd_file = create_command_file(source_file, metadata)
    print(f"  ✓ Created: {cmd_file.relative_to(WORKSPACE)}")
    
    # Step 3: Register command
    print("\nStep 2: Registering command...")
    registered = register_command(metadata)
    if registered:
        print(f"  ✓ Added to commands.jsonl")
    
    # Step 4: Create incantum triggers
    print("\nStep 3: Creating incantum triggers...")
    triggers_added = create_incantum_triggers(metadata)
    if triggers_added:
        print(f"  ✓ Added natural language triggers")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"✅ IMPORT COMPLETE: {metadata['cmd_name']}")
    print(f"{'='*60}")
    print(f"\nUsage:")
    print(f"  N5: {metadata['cmd_name'].replace('-', ' ')}")
    print(f"  N5: {' '.join(metadata['cmd_name'].split('-')[:3])}")
    
    return True


def import_batch(directory):
    """
    Import all prompts from a directory
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"❌ Directory not found: {directory}")
        return
    
    # Find all Function and Companion files
    prompt_files = []
    for pattern in ["Function*", "Companion*"]:
        prompt_files.extend(dir_path.glob(pattern))
    
    if not prompt_files:
        print(f"❌ No prompt files found in {directory}")
        print("   Looking for files starting with 'Function' or 'Companion'")
        return
    
    print(f"\n{'='*60}")
    print(f"BATCH IMPORT: {len(prompt_files)} files")
    print(f"{'='*60}")
    
    success_count = 0
    for prompt_file in sorted(prompt_files):
        try:
            if import_prompt(prompt_file):
                success_count += 1
        except Exception as e:
            print(f"\n❌ Error importing {prompt_file.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE: {success_count}/{len(prompt_files)} imported")
    print(f"{'='*60}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single file:  python n5_import_prompt.py <prompt_file>")
        print("  Batch import: python n5_import_prompt.py --batch <directory>")
        print("\nExpected filename format:")
        print("  Function [NN] - Title v0.0.ext")
        print("  Companion [NN] - Title v0.0.ext")
        sys.exit(1)
    
    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("❌ Please specify directory for batch import")
            sys.exit(1)
        import_batch(sys.argv[2])
    else:
        source_file = Path(sys.argv[1])
        if not source_file.exists():
            print(f"❌ File not found: {sys.argv[1]}")
            sys.exit(1)
        import_prompt(source_file)


if __name__ == "__main__":
    main()
