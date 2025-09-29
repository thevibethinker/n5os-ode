#!/usr/bin/env python3
"""
Manage commands.jsonl safely with append-only updates,
with LLM-powered similarity and merge suggestions using Zo internal LLM.

Usage examples:
  n5_commands_manage.py --list
  n5_commands_manage.py --add-file new_command.json
  n5_commands_manage.py --add-json '{"name":"xyz", ...}'
"""

import json
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS_FILE = ROOT / "N5" / "commands.jsonl"

# Placeholder for Zo internal LLM call
from functions import use_app_gpt


def load_commands():
    commands = []
    if COMMANDS_FILE.exists():
        with open(COMMANDS_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        commands.append(json.loads(line))
                    except json.JSONDecodeError:
                        print(f"Warning: Skipping invalid JSON line: {line}", file=sys.stderr)
    return commands


def save_commands(commands):
    with open(COMMANDS_FILE, "w") as f:
        for cmd in commands:
            f.write(json.dumps(cmd))
            f.write("\n")
    print(f"Saved {len(commands)} commands.")


def prompt_llm_similarity(new_cmd, existing_cmds):
    docs = []
    for cmd in existing_cmds:
        docs.append(f"Command name: {cmd.get('name')}, summary: {cmd.get('summary')}.")
    joined_cmds = '\n'.join(docs)
    prompt = f"""
You are an assistant to help manage a command repository.

A new candidate command was proposed:
{json.dumps(new_cmd, indent=2)}

Compare it to the existing commands below:
{joined_cmds}

Assess:
- Is the new command very similar to any existing command?
- Could it be merged by adding parameters or options to an existing command?
- Or is it unique enough to be simply added?

Return a concise, actionable summary of your assessment.
"""

    gpt = use_app_gpt("chat-completions")
    response = gpt.chat_completions_create({
        "messages": [
            {"role": "system", "content": "You are a helpful command catalog assistant."},
            {"role": "user", "content": prompt}
        ],
        "model": "gpt-4o",
        "temperature": 0.0,
        "max_tokens": 512
    })

    result = response["choices"][0]["message"]["content"]
    return result


def add_command(commands, new_cmd):
    existing_names = {cmd.get('name') for cmd in commands}
    if new_cmd.get('name') in existing_names:
        print(f"Error: Command with name '{new_cmd.get('name')}' already exists.")
        return False
    
    suggestion = prompt_llm_similarity(new_cmd, commands)
    print(f"LLM Suggestion: {suggestion}")

    commands.append(new_cmd)
    print(f"Added new command '{new_cmd.get('name')}'.")
    return True


def list_commands(commands):
    for cmd in commands:
        print(f"- {cmd.get('name', 'UNKNOWN')} - {cmd.get('summary', '')}")


def main():
    parser = argparse.ArgumentParser(description="Manage commands.jsonl safely with LLM similarity check")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List all commands")
    group.add_argument("--add-file", help="Add a new command from JSON file")
    group.add_argument("--add-json", help="Add a new command from JSON string")
    args = parser.parse_args()

    commands = load_commands()

    if args.list:
        list_commands(commands)
    elif args.add_file:
        path = Path(args.add_file)
        if not path.exists():
            print(f"Error: File not found: {args.add_file}")
            sys.exit(1)
        with open(path) as f:
            new_cmd = json.load(f)
        if add_command(commands, new_cmd):
            save_commands(commands)
    elif args.add_json:
        try:
            new_cmd = json.loads(args.add_json)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}")
            sys.exit(1)
        if add_command(commands, new_cmd):
            save_commands(commands)


if __name__ == "__main__":
    main()
