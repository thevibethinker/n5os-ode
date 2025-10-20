#!/usr/bin/env python3
"""Fix all single-shot workflow entries to proper workflow categories"""
import json
from pathlib import Path

commands_file = Path("/home/workspace/N5/commands.jsonl")
output_file = Path("/home/workspace/N5/commands.jsonl.fixed2")

# Mapping from command name patterns to correct workflows
workflow_mapping = {
    # Lists commands
    "lists-": "lists",
    # Knowledge commands
    "knowledge-": "knowledge",
    # Index/ops commands
    "index-": "ops",
    "docgen": "ops",
    "digest-runs": "ops",
    "core-audit": "ops",
    "git-audit": "ops",
    "git-check": "ops",
    "hygiene-preflight": "ops",
    "file-protector": "ops",
    # Data/jobs commands
    "jobs-": "data",
    "transcript-ingest": "data",
    # Research commands  
    "deep-research": "research",
    # Careerspan/timeline commands
    "careerspan-": "misc",
    "system-timeline": "misc",
    # Writing/content generation
    "functions-b2c": "writing",
    "follow-up-email": "writing",
    "deliverable-": "writing",
    # Analysis/extraction
    "jtbd-plus": "research",
    "pr-intel": "research",
    "stakeholder-": "research",
    # Misc
    "flow-run": "misc",
    "grep-search": "misc",
    "conversation-end": "misc",
    "meeting-approve": "misc",
}

def get_workflow(cmd_name):
    """Determine correct workflow based on command name"""
    for pattern, workflow in workflow_mapping.items():
        if cmd_name.startswith(pattern) or pattern == cmd_name:
            return workflow
    return "misc"  # Default fallback

# Read and fix all commands
commands = []
fixed_count = 0

with open(commands_file) as f:
    for line in f:
        if not line.strip():
            continue
        cmd = json.loads(line)
        
        if cmd.get("workflow") == "single-shot":
            old_workflow = cmd["workflow"]
            cmd["workflow"] = get_workflow(cmd["name"])
            fixed_count += 1
            print(f"✓ {cmd['name']}: single-shot → {cmd['workflow']}")
        
        commands.append(cmd)

# Write fixed version
with open(output_file, 'w') as f:
    for cmd in commands:
        f.write(json.dumps(cmd, separators=(',', ':')) + '\n')

print(f"\n✓ Fixed {fixed_count} workflow entries")
print(f"✓ Wrote to {output_file}")
print(f"\nTo apply: mv {output_file} {commands_file}")
