#!/usr/bin/env python3
"""
N5 Prompt Converter - Convert personal prompts to N5 commands

Usage:
    python3 n5_convert_prompt.py <prompt_file>
    python3 n5_convert_prompt.py <directory>  # Batch convert

Process:
1. Parse prompt file metadata (name, version, type)
2. Copy to Prompts/ with standardized naming
3. Register in executables.db
4. Create incantum triggers
5. Move companion files to Knowledge/
6. Report results

Naming Convention:
    "Function [01] - Deep Research v1.0.txt"
    → "deep-research.md" (command file)
    → "deep-research" (command name)
    → Triggers: ["deep research", "research deep", "deep"]
"""

import sys
import json
import re
import shutil
from pathlib import Path
from datetime import datetime

# Paths
WORKSPACE = Path("/home/workspace")
PROMPTS_DIR = WORKSPACE / "Personal/Prompts"
COMMANDS_DIR = WORKSPACE / "N5/commands"
KNOWLEDGE_DIR = WORKSPACE / "Knowledge"
COMMANDS_FILE = WORKSPACE / "N5/data/executables.db"
TRIGGERS_FILE = WORKSPACE / "N5/config/incantum_triggers.json"
LOG_FILE = WORKSPACE / "N5/runtime/prompt_conversion.log"

def log(message):
    """Log to file and print"""
    timestamp = datetime.now().isoformat()
    log_line = f"[{timestamp}] {message}"
    print(message)
    with open(LOG_FILE, 'a') as f:
        f.write(log_line + '\n')

def parse_prompt_metadata(filepath):
    """
    Extract metadata from prompt filename
    
    Patterns:
    - Function [NN] - Name v1.0.txt
    - Companion [NN] - Name v1.0.txt
    
    Returns:
        dict: {type, number, name, version, extension}
    """
    filename = filepath.name
    
    # Pattern: Function/Companion [NN] - Name vX.X.ext
    pattern = r'(Function|Companion) \[(\d+)\] - (.+?) v(\d+\.\d+)\.(\w+)$'
    match = re.match(pattern, filename)
    
    if not match:
        return None
    
    return {
        "type": match.group(1),
        "number": match.group(2),
        "name": match.group(3),
        "version": match.group(4),
        "extension": match.group(5),
        "original_name": filename
    }

def create_command_name(name_text):
    """
    Convert name text to command name
    
    "Deep Research Due Diligence" → "deep-research-due-diligence"
    """
    cmd_name = name_text.lower()
    cmd_name = re.sub(r'[^\w\s-]', '', cmd_name)  # Remove special chars
    cmd_name = re.sub(r'\s+', '-', cmd_name.strip())  # Spaces to hyphens
    cmd_name = re.sub(r'-+', '-', cmd_name)  # Multiple hyphens to single
    cmd_name = cmd_name.strip('-')  # Remove leading/trailing hyphens
    
    return cmd_name

def create_triggers(command_name, name_text):
    """
    Generate natural language triggers
    
    Returns list of trigger phrases
    """
    triggers = []
    
    # Full name with spaces
    full_name = command_name.replace('-', ' ')
    triggers.append(full_name)
    
    # Original name (lowercase)
    triggers.append(name_text.lower())
    
    # First 2-3 words
    words = command_name.split('-')
    if len(words) >= 2:
        triggers.append(' '.join(words[:2]))
    if len(words) >= 3:
        triggers.append(' '.join(words[:3]))
    
    # Short form (first word + last word if >2 words)
    if len(words) > 2:
        triggers.append(f"{words[0]} {words[-1]}")
    
    # Remove duplicates, keep order
    seen = set()
    unique_triggers = []
    for t in triggers:
        if t not in seen:
            seen.add(t)
            unique_triggers.append(t)
    
    return unique_triggers

def convert_function_prompt(filepath, metadata):
    """Convert Function prompt to N5 command"""
    
    cmd_name = create_command_name(metadata["name"])
    cmd_file = f"{cmd_name}.md"
    dest = COMMANDS_DIR / cmd_file
    
    # Check if already exists
    if dest.exists():
        log(f"  ⚠️  Command already exists: {cmd_name}")
        return None
    
    # Copy prompt file to commands/
    shutil.copy(filepath, dest)
    log(f"  ✓ Copied: {metadata['original_name']}")
    log(f"    → {cmd_file}")
    
    # Create command registry entry
    command_entry = {
        "name": cmd_name,
        "version": metadata["version"],
        "workflow": "single-shot",
        "summary": f"{metadata['name']} (personal prompt)",
        "function_file": f"commands/{cmd_file}",
        "entry_point": "function_file",
        "tags": ["personal", "prompt"] + cmd_name.split('-')[:2]
    }
    
    # Create incantum triggers
    trigger_phrases = create_triggers(cmd_name, metadata["name"])
    trigger_entry = {
        "trigger": trigger_phrases[0],
        "aliases": trigger_phrases[1:],
        "command": cmd_name
    }
    
    return {
        "command": command_entry,
        "trigger": trigger_entry,
        "name": cmd_name
    }

def convert_companion_file(filepath, metadata):
    """Move Companion file to Knowledge/"""
    
    dest = KNOWLEDGE_DIR / filepath.name
    
    if dest.exists():
        log(f"  ⚠️  File already exists in Knowledge/: {filepath.name}")
        return None
    
    shutil.move(filepath, dest)
    log(f"  ✓ Moved to Knowledge/: {filepath.name}")
    
    return {"name": filepath.name, "location": "Knowledge/"}

def update_registries(new_commands, new_triggers):
    """Update executables.db and incantum_triggers.json"""
    
    if not new_commands and not new_triggers:
        return
    
    # Update executables.db
    if new_commands:
        with open(COMMANDS_FILE, 'a') as f:
            for cmd in new_commands:
                f.write(json.dumps(cmd) + '\n')
        log(f"\n✓ Added {len(new_commands)} commands to registry")
    
    # Update incantum_triggers.json
    if new_triggers:
        with open(TRIGGERS_FILE, 'r') as f:
            triggers = json.load(f)
        
        triggers.extend(new_triggers)
        
        with open(TRIGGERS_FILE, 'w') as f:
            json.dump(triggers, f, indent=2)
        
        log(f"✓ Added {len(new_triggers)} triggers")

def convert_single_file(filepath):
    """Convert a single prompt file"""
    
    log(f"\n{'='*60}")
    log(f"Converting: {filepath.name}")
    log('='*60)
    
    # Parse metadata
    metadata = parse_prompt_metadata(filepath)
    
    if not metadata:
        log(f"  ✗ Could not parse metadata from filename")
        log(f"    Expected format: Function/Companion [NN] - Name vX.X.ext")
        return None
    
    log(f"  Type: {metadata['type']}")
    log(f"  Name: {metadata['name']}")
    log(f"  Version: {metadata['version']}")
    
    # Convert based on type
    if metadata["type"] == "Function":
        return convert_function_prompt(filepath, metadata)
    elif metadata["type"] == "Companion":
        return convert_companion_file(filepath, metadata)
    else:
        log(f"  ✗ Unknown type: {metadata['type']}")
        return None

def convert_directory(directory):
    """Batch convert all prompts in directory"""
    
    directory = Path(directory)
    
    if not directory.exists():
        log(f"✗ Directory not found: {directory}")
        return
    
    # Find all prompt files
    prompt_files = []
    for f in directory.iterdir():
        if f.is_file() and (f.name.startswith("Function") or f.name.startswith("Companion")):
            prompt_files.append(f)
    
    if not prompt_files:
        log(f"No prompt files found in {directory}")
        return
    
    log(f"\nFound {len(prompt_files)} prompt files to convert\n")
    
    new_commands = []
    new_triggers = []
    companions = []
    
    for filepath in sorted(prompt_files):
        result = convert_single_file(filepath)
        
        if result:
            if "command" in result:
                new_commands.append(result["command"])
                new_triggers.append(result["trigger"])
            elif "location" in result:
                companions.append(result)
    
    # Update registries
    update_registries(new_commands, new_triggers)
    
    # Summary
    log("\n" + "="*60)
    log("CONVERSION SUMMARY")
    log("="*60)
    log(f"Commands created: {len(new_commands)}")
    log(f"Companions moved: {len(companions)}")
    log(f"Total processed: {len(new_commands) + len(companions)}")
    
    if new_commands:
        log("\nNew Commands:")
        for cmd in new_commands:
            log(f"  - {cmd['name']}: {cmd['summary']}")
    
    if companions:
        log("\nCompanions moved to Knowledge/:")
        for comp in companions:
            log(f"  - {comp['name']}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Convert single file:")
        print("    python3 n5_convert_prompt.py <prompt_file>")
        print("  Convert directory:")
        print("    python3 n5_convert_prompt.py <directory>")
        print("\nExample:")
        print('    python3 n5_convert_prompt.py "Function [01] - My Prompt v1.0.txt"')
        print('    python3 n5_convert_prompt.py Personal/Prompts/')
        sys.exit(1)
    
    target = Path(sys.argv[1])
    
    # Create log directory if needed
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    log(f"\nN5 Prompt Converter")
    log(f"Target: {target}\n")
    
    if target.is_file():
        result = convert_single_file(target)
        if result and "command" in result:
            update_registries([result["command"]], [result["trigger"]])
            log(f"\n✓ Conversion complete!")
            log(f"\nYou can now use:")
            log(f"  N5: {result['trigger']['trigger']}")
    elif target.is_dir():
        convert_directory(target)
    else:
        log(f"✗ Target not found: {target}")
        sys.exit(1)

if __name__ == "__main__":
    main()
