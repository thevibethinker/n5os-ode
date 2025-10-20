#!/usr/bin/env python3
"""Fix the corrupted lists-create entry in commands.jsonl"""
import json
from pathlib import Path

commands_file = Path("/home/workspace/N5/commands.jsonl")
output_file = Path("/home/workspace/N5/commands.jsonl.fixed")

correct_entry = {
    "name": "lists-create",
    "version": "0.1.0",
    "workflow": "lists",
    "summary": "Create a new list registry entry with JSONL and MD files.",
    "tags": ["lists", "registry"],
    "inputs": [
        {
            "name": "slug",
            "type": "string",
            "required": True,
            "description": "List slug (lowercase, hyphens allowed)"
        },
        {
            "name": "title",
            "type": "text",
            "required": True,
            "description": "List title"
        },
        {
            "name": "tags",
            "type": "json",
            "description": "Tags"
        }
    ],
    "outputs": [
        {
            "name": "registry",
            "type": "path",
            "description": "Path to index.jsonl"
        },
        {
            "name": "jsonl",
            "type": "path",
            "description": "Path to JSONL file"
        },
        {
            "name": "md",
            "type": "path",
            "description": "Path to MD file"
        }
    ],
    "side_effects": ["writes:file", "modifies:file"],
    "examples": [
        'N5: run lists-create slug=ideas title="My Ideas" --dry-run'
    ],
    "entry_point": "script",
    "script": "scripts/n5_lists_create.py",
    "function_file": "commands/lists-create.md"
}

# Read all commands
commands = []
with open(commands_file) as f:
    for line in f:
        if not line.strip():
            continue
        cmd = json.loads(line)
        if cmd.get("name") == "lists-create":
            commands.append(correct_entry)
            print(f"✓ Fixed lists-create entry")
        else:
            commands.append(cmd)

# Write fixed version
with open(output_file, 'w') as f:
    for cmd in commands:
        f.write(json.dumps(cmd, separators=(',', ':')) + '\n')

print(f"✓ Wrote fixed commands to {output_file}")
print("Review the file, then run:")
print(f"  mv {output_file} {commands_file}")
