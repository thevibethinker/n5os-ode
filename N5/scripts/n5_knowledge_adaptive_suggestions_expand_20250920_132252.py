import argparse

#!/usr/bin/env python3
"""
Adaptive Suggestion Parser and Schema Updater for N5 Knowledge Ingestion.

Parses LLM suggestions, validates them, and safely applies schema and reservoir expansions.
"""

import json
import re
import subprocess
from pathlib import Path

SCHEMA_FILE = Path(__file__).resolve().parents[1] / "schemas" / "ingest.plan.schema.json"
KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"


def load_schema():
    with open(SCHEMA_FILE, "r") as f:
        return json.load(f)


def validate_schema_file(schema_path: Path) -> bool:
    result = subprocess.run(["python3", "./scripts/n5_schema_validation.py", str(schema_path)], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Schema validation failed for {schema_path}")
        print(result.stderr)
        return False
    return True


def save_schema(schema):
    backup_file = SCHEMA_FILE.with_suffix('.bak')
    SCHEMA_FILE.rename(backup_file)

    # Temporarily save to a temp file for validation
    temp_path = SCHEMA_FILE.with_suffix('.temp.json')
    with open(temp_path, "w") as f:
        json.dump(schema, f, indent=2)

    if not validate_schema_file(temp_path):
        print("Schema update aborted due to validation errors.")
        temp_path.unlink()
        SCHEMA_FILE.rename(backup_file)
        return

    temp_path.rename(SCHEMA_FILE)
    print(f"Schema updated with backup saved to {backup_file}")


def parse_suggestions(raw_text):
    try:
        return json.loads(raw_text)
    except Exception:
        # Fallback regex extraction
        matches = re.findall(r'\[\{.*?\}\]', raw_text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except Exception:
                continue
    return []


def validate_and_apply_suggestions(suggestions, schema):
    existing_reservoirs = set(schema["properties"].keys())
    added = False

    for suggestion in suggestions:
        s_type = suggestion.get("type")
        name = suggestion.get("name")

        if s_type not in ["new_reservoir", "new_subcategory"]:
            print(f"Ignoring invalid suggestion type: {s_type}")
            continue

        if s_type == "new_reservoir" and name not in existing_reservoirs:
            print(f"Adding new reservoir: {name}")
            # Add empty object stub
            schema["properties"][name] = {"type": "object", "additionalProperties": true}
            # Create placeholder file
            placeholder = KNOWLEDGE_DIR / f"{name}.md"
            if not placeholder.exists():
                placeholder.write_text(f"# {name} (New Reservoir)\n\nDescription pending.")
                print(f"Created placeholder file {placeholder}")
            added = True

        elif s_type == "new_subcategory" and name not in existing_reservoirs:
            # For simplicity, treat as reservoir too; enhancement: add nested property instead
            print(f"Adding new subcategory (treated as reservoir): {name}")
            schema["properties"][name] = {"type": "object", "additionalProperties": true}
            placeholder = KNOWLEDGE_DIR / f"{name}.md"
            if not placeholder.exists():
                placeholder.write_text(f"# {name} (New Subcategory)\n\nDescription pending.")
                print(f"Created placeholder file {placeholder}")
            added = True

    if added:
        save_schema(schema)
    else:
        print("No new reservoirs or subcategories to add.")


def main(raw_response_file=None):
    schema = load_schema()
    if raw_response_file:
        raw_text = Path(raw_response_file).read_text()
    else:
        print("Error: Must provide raw LLM suggestion response file to parse and apply.")
        return

    suggestions = parse_suggestions(raw_text)
    print(f"Parsed {len(suggestions)} suggestions from LLM output.")

    validate_and_apply_suggestions(suggestions, schema)



parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode')
args = parser.parse_args()

if __name__ == '__main__':
    import sys
    raw_file = sys.argv[1] if len(sys.argv) > 1 else None
    main(raw_file)
