#!/usr/bin/env python3
"""
N5 Command Registry Validator

Validates commands.jsonl against the commands schema and reports issues.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Paths
ROOT = Path(__file__).resolve().parents[1]
COMMANDS_FILE = ROOT / "config" / "commands.jsonl"
SCHEMA_FILE = ROOT / "schemas" / "commands.schema.json"

# Required fields per schema
REQUIRED_FIELDS = ["name", "version", "summary"]

# Valid enum values
VALID_WORKFLOWS = ["writing", "research", "data", "ops", "knowledge", "lists", "index", "email", "media", "code", "misc", "automation"]
VALID_TYPES = ["prompt", "script", "tool", "reference"]
VALID_STATUSES = ["active", "deprecated", "experimental"]
VALID_SIDE_EFFECTS = [
    "writes:file", "writes:dir", "modifies:file", "deletes:file",
    "starts:service", "stops:service", "sends:email", "posts:web",
    "external:api", "creates:backup", "atomic:operations", "executes:command"
]


def load_commands() -> List[Tuple[int, Dict[str, Any]]]:
    """Load commands from JSONL file."""
    if not COMMANDS_FILE.exists():
        print(f"Error: Commands file not found: {COMMANDS_FILE}")
        sys.exit(1)

    commands = []
    with open(COMMANDS_FILE, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                cmd = json.loads(line)
                commands.append((line_num, cmd))
            except json.JSONDecodeError as e:
                print(f"Line {line_num}: Invalid JSON - {e}")

    return commands


def validate_command(line_num: int, cmd: Dict[str, Any]) -> List[str]:
    """Validate a single command entry. Returns list of errors."""
    errors = []
    cmd_id = cmd.get("id", f"line_{line_num}")

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in cmd or not cmd[field]:
            errors.append(f"[{cmd_id}] Missing required field: {field}")

    # Validate id format (kebab-case)
    if "id" in cmd:
        import re
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", cmd["id"]):
            errors.append(f"[{cmd_id}] Invalid id format (must be kebab-case): {cmd['id']}")

    # Validate version format (semantic versioning)
    if "version" in cmd:
        import re
        if not re.match(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$", cmd["version"]):
            errors.append(f"[{cmd_id}] Invalid version format: {cmd['version']}")

    # Validate summary length
    if "summary" in cmd and len(cmd["summary"]) > 180:
        errors.append(f"[{cmd_id}] Summary too long ({len(cmd['summary'])} chars, max 180)")

    # Validate workflow enum
    if "workflow" in cmd and cmd["workflow"] not in VALID_WORKFLOWS:
        errors.append(f"[{cmd_id}] Invalid workflow: {cmd['workflow']} (valid: {VALID_WORKFLOWS})")

    # Validate type enum
    if "type" in cmd and cmd["type"] not in VALID_TYPES:
        errors.append(f"[{cmd_id}] Invalid type: {cmd['type']} (valid: {VALID_TYPES})")

    # Validate status enum
    if "status" in cmd and cmd["status"] not in VALID_STATUSES:
        errors.append(f"[{cmd_id}] Invalid status: {cmd['status']} (valid: {VALID_STATUSES})")

    # Validate side_effects
    if "side_effects" in cmd:
        for effect in cmd["side_effects"]:
            if effect not in VALID_SIDE_EFFECTS:
                errors.append(f"[{cmd_id}] Invalid side_effect: {effect}")

    # Validate incantum structure
    if "incantum" in cmd:
        incantum = cmd["incantum"]
        if not isinstance(incantum, dict):
            errors.append(f"[{cmd_id}] incantum must be an object")
        else:
            if "trigger" not in incantum:
                errors.append(f"[{cmd_id}] incantum missing 'trigger' field")
            if "aliases" in incantum and not isinstance(incantum["aliases"], list):
                errors.append(f"[{cmd_id}] incantum.aliases must be an array")
            if "confidence_threshold" in incantum:
                thresh = incantum["confidence_threshold"]
                if not isinstance(thresh, (int, float)) or thresh < 0 or thresh > 1:
                    errors.append(f"[{cmd_id}] incantum.confidence_threshold must be 0-1")

    # Validate inputs structure
    if "inputs" in cmd:
        if not isinstance(cmd["inputs"], list):
            errors.append(f"[{cmd_id}] inputs must be an array")
        else:
            for i, inp in enumerate(cmd["inputs"]):
                if not isinstance(inp, dict):
                    errors.append(f"[{cmd_id}] inputs[{i}] must be an object")
                elif "name" not in inp or "type" not in inp:
                    errors.append(f"[{cmd_id}] inputs[{i}] missing 'name' or 'type'")

    # Validate outputs structure
    if "outputs" in cmd:
        if not isinstance(cmd["outputs"], list):
            errors.append(f"[{cmd_id}] outputs must be an array")
        else:
            for i, out in enumerate(cmd["outputs"]):
                if not isinstance(out, dict):
                    errors.append(f"[{cmd_id}] outputs[{i}] must be an object")
                elif "name" not in out or "type" not in out:
                    errors.append(f"[{cmd_id}] outputs[{i}] missing 'name' or 'type'")

    return errors


def check_duplicates(commands: List[Tuple[int, Dict[str, Any]]]) -> List[str]:
    """Check for duplicate command IDs."""
    errors = []
    seen_ids = {}
    seen_triggers = {}

    for line_num, cmd in commands:
        cmd_id = cmd.get("id")
        if cmd_id:
            if cmd_id in seen_ids:
                errors.append(f"Duplicate command ID: {cmd_id} (lines {seen_ids[cmd_id]} and {line_num})")
            else:
                seen_ids[cmd_id] = line_num

        # Check for duplicate triggers
        if "incantum" in cmd and "trigger" in cmd["incantum"]:
            trigger = cmd["incantum"]["trigger"].lower()
            if trigger in seen_triggers:
                errors.append(f"Duplicate trigger: '{trigger}' (commands {seen_triggers[trigger]} and {cmd_id})")
            else:
                seen_triggers[trigger] = cmd_id

    return errors


def main() -> int:
    print(f"Validating: {COMMANDS_FILE}\n")

    commands = load_commands()
    print(f"Loaded {len(commands)} commands\n")

    all_errors = []

    # Validate each command
    for line_num, cmd in commands:
        errors = validate_command(line_num, cmd)
        all_errors.extend(errors)

    # Check for duplicates
    all_errors.extend(check_duplicates(commands))

    # Report results
    if all_errors:
        print(f"Found {len(all_errors)} validation errors:\n")
        for error in all_errors:
            print(f"  - {error}")
        return 1
    else:
        print("All commands valid!")

        # Print summary stats
        workflows = {}
        types = {}
        for _, cmd in commands:
            wf = cmd.get("workflow", "unknown")
            workflows[wf] = workflows.get(wf, 0) + 1
            t = cmd.get("type", "unknown")
            types[t] = types.get(t, 0) + 1

        print(f"\nBy workflow: {dict(sorted(workflows.items(), key=lambda x: -x[1]))}")
        print(f"By type: {dict(sorted(types.items(), key=lambda x: -x[1]))}")

        return 0


if __name__ == "__main__":
    sys.exit(main())
