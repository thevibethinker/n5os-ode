#!/usr/bin/env python3
"""
Append a command entry to commands.jsonl safely with validation and duplication check.
"""
import json
import sys
from pathlib import Path

CMD_FILE = Path(__file__).resolve().parents[1] / "commands.jsonl"

NEW_COMMAND = {
    "name": "knowledge-ingest",
    "version": "0.1.0",
    "summary": "Ingest biographical/historical/strategic information about V and Careerspan, analyze with LLM, and store across knowledge reservoirs.",
    "workflow": "knowledge",
    "tags": ["ingest", "llm", "analysis"],
    "inputs": [
        {
            "name": "input_text",
            "type": "string",
            "description": "The large text chunk to ingest",
            "required": True
        }
    ],
    "outputs": [],
    "uses": {},
    "side_effects": ["modifies:file", "writes:file"],
    "permissions_required": [],
    "flags": {
        "dry_run": True,
        "require_auth": False
    },
    "examples": ["N5: run knowledge-ingest --input_text '...'"],
    "updated_at": "2025-09-18T19:08:43Z"
}


def load_commands():
    if not CMD_FILE.exists():
        return []
    with open(CMD_FILE, "r") as f:
        lines = f.readlines()
    commands = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            commands.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"Warning: Skip invalid JSON line: {line}", file=sys.stderr)
    return commands


def save_commands(commands):
    backup_file = CMD_FILE.with_suffix(".jsonl.bak")
    if CMD_FILE.exists():
        CMD_FILE.rename(backup_file)
        print(f"Backup of command file created at {backup_file}")
    with open(CMD_FILE, "w") as f:
        for cmd in commands:
            f.write(json.dumps(cmd) + "\n")
    print(f"Commands file updated successfully.")


def append_command(new_cmd):
    commands = load_commands()
    for cmd in commands:
        if cmd.get("name") == new_cmd["name"]:
            print(f"Command '{new_cmd['name']}' already exists. No change made.")
            return
    commands.append(new_cmd)
    save_commands(commands)


def main():
    append_command(NEW_COMMAND)


if __name__ == "__main__":
    main()
