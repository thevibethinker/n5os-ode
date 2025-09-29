#!/usr/bin/env python3
"""
N5 OS Phase 0: Schemas Test Suite

Tests JSON schema validation:
- Schemas are valid JSON
- Sample data validates against schemas
"""

import json
import jsonschema
from pathlib import Path
import sys
import hashlib

def load_json(file_path):
    """Load JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def validate_schema_file(schema_path):
    """Validate that a schema file is valid JSON."""
    try:
        schema = load_json(schema_path)
        jsonschema.Draft202012Validator.check_schema(schema)
        return True, None
    except Exception as e:
        return False, str(e)

def validate_data_against_schema(data_path, schema_path):
    """Validate data file against schema."""
    try:
        schema = load_json(schema_path)
        if data_path.suffix == '.json':
            data = load_json(data_path)
            jsonschema.validate(data, schema)
        elif data_path.suffix == '.jsonl':
            # Validate each line in JSONL as individual object
            with open(data_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        obj = json.loads(line)
                        jsonschema.validate(obj, schema)
        return True, None
    except Exception as e:
        return False, str(e)

def test_schemas():
    """Test all schemas."""
    n5_root = Path('/home/workspace/N5')
    schemas_dir = n5_root / 'schemas'
    
    # Test each schema file
    schemas = list(schemas_dir.glob('*.schema.json'))
    results = {}
    
    for schema_file in schemas:
        print(f"Testing schema: {schema_file.name}")
        valid, error = validate_schema_file(schema_file)
        if not valid:
            print(f"❌ Schema invalid: {error}")
            results[schema_file.name] = {'schema_valid': False, 'error': error}
            continue
        
        results[schema_file.name] = {'schema_valid': True}
        
        # Find corresponding data files
        if 'commands' in schema_file.name:
            data_files = [n5_root / 'commands.jsonl']
        elif 'lists.item' in schema_file.name:
            data_files = [f for f in (n5_root / 'lists').glob('*.jsonl') if f.name != 'index.jsonl']
        elif 'lists.registry' in schema_file.name:
            data_files = [n5_root / 'lists' / 'index.jsonl']
        elif 'index' in schema_file.name:
            data_files = [n5_root / 'index.jsonl']
        elif 'knowledge.facts' in schema_file.name:
            data_files = []  # Assume no knowledge facts yet
        else:
            data_files = []
        
        for data_file in data_files:
            if data_file.exists():
                print(f"  Validating data: {data_file.relative_to(n5_root)}")
                valid, error = validate_data_against_schema(data_file, schema_file)
                if not valid:
                    print(f"❌ Data validation failed: {error}")
                    results[schema_file.name]['data_validation'] = False
                    results[schema_file.name]['data_error'] = error
                else:
                    print(f"✅ Data valid")
                    results[schema_file.name]['data_validation'] = True
    
    # Check overall success
    all_passed = all(r.get('schema_valid', False) and r.get('data_validation', True) for r in results.values())
    
    return results, all_passed

def get_file_checksum(file_path):
    """Get SHA256 checksum of file."""
    if not file_path.exists():
        return None
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

if __name__ == '__main__':
    print("Running N5 Phase 0: Schemas Test Suite...")
    
    results, success = test_schemas()
    
    # Telemetry
    telemetry = {
        'phase': 0,
        'component': 'schemas',
        'success': success,
        'results': results,
        'checksums': {}
    }
    
    n5_root = Path('/home/workspace/N5')
    for schema_file in (n5_root / 'schemas').glob('*.schema.json'):
        telemetry['checksums'][schema_file.name] = get_file_checksum(schema_file)
    
    # Save telemetry
    with open('/home/workspace/N5/test/phase0_telemetry.json', 'w') as f:
        json.dump(telemetry, f, indent=2)
    
    print(f"\nPhase 0 {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)