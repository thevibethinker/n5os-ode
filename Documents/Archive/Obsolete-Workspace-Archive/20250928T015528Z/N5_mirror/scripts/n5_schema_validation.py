#!/usr/bin/env python3
"""
Schema Validation Utility for N5 Ingestion System.

Validates proposed JSON schema updates using the draft-07 JSON Schema standard.
Prevents invalid schema writes with detailed error reporting.
"""

import json
import sys
from jsonschema import validate, ValidationError, Draft7Validator

SCHEMA_FILE = "./schemas/ingest.plan.schema.json"


def load_schema(path):
    with open(path, 'r') as f:
        return json.load(f)


def validate_schema_update(base_schema, update):
    """Validate update dict against base schema's JSON Schema specification."""
    validator = Draft7Validator(base_schema)
    errors = sorted(validator.iter_errors(update), key=lambda e: e.path)
    if errors:
        print("Schema validation errors:")
        for error in errors:
            print(f"- {'.'.join(map(str, error.path))}: {error.message}")
        return False
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: n5_schema_validation.py <schema_update.json>")
        sys.exit(1)
    
    update_path = sys.argv[1]
    try:
        base_schema = load_schema(SCHEMA_FILE)
        update = load_schema(update_path)
    except Exception as e:
        print(f"Error loading schemas: {e}")
        sys.exit(2)
    
    if validate_schema_update(base_schema, update):
        print("Schema update is valid.")
    else:
        print("Schema update is invalid.")
        sys.exit(3)


if __name__ == "__main__":
    main()
