# Simple Workflow Systematization for N5 OS

## Core Problem Statement
N5 has many individual scripts but lacks a unified way for users to interact with them. We need a simple "record" command that routes user inputs to the appropriate scripts.

## First Principles Analysis

### What We Know About N5
- Scripts exist in `/home/workspace/N5/scripts/`
- Each script is CLI-driven with argparse
- Scripts store data in JSONL files with schemas
- Scripts use n5_safety and n5_run_record
- Users currently must know specific script names

### What We Want
- Single "record" command for common operations
- `record link <url>` → routes to essential links script
- `record fact <fact>` → routes to knowledge script
- `record person <name>` → routes to person script

## Simple Implementation Plan

### Step 1: Create Basic Record Dispatcher
Build one simple script: `n5_record.py`

**Purpose**: Route "record" commands to existing scripts
**Example**: `python3 n5_record.py link "https://example.com" "My Link"`

**Logic**:
1. Parse first argument (data type: link, fact, person)
2. Map to existing script (link → n5_essential_links_add.py)
3. Pass remaining arguments to that script
4. Return result to user

### Step 2: Map Existing Scripts
Create simple mapping file: `record_mappings.json`

**Content**:
```json
{
  "link": {
    "script": "n5_essential_links_add.py",
    "description": "Add essential links"
  },
  "fact": {
    "script": "n5_knowledge_add.py", 
    "description": "Add knowledge facts"
  }
}
```

### Step 3: Test with Essential Links
Since we have Essential Links from Phase 1:
1. Create n5_record.py
2. Test: `python3 n5_record.py link "https://test.com" "Test Link"`
3. Verify it calls n5_essential_links_add.py correctly

## Implementation Details

### File to Create: `/home/workspace/N5/scripts/n5_record.py`

**Basic Structure**:
```python
#!/usr/bin/env python3
import argparse
import subprocess
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Record data in N5 system')
    parser.add_argument('data_type', help='Type of data (link, fact, person)')
    parser.add_argument('data', help='Data to record')
    parser.add_argument('title', nargs='?', help='Optional title/description')
    
    args = parser.parse_args()
    
    # Load mappings
    mappings_file = Path(__file__).parent.parent / 'knowledge' / 'record_mappings.json'
    with open(mappings_file) as f:
        mappings = json.load(f)
    
    # Find target script
    if args.data_type not in mappings:
        print(f"Unknown data type: {args.data_type}")
        return 1
    
    # Execute target script
    target_script = mappings[args.data_type]['script']
    script_path = Path(__file__).parent / target_script
    
    # Build command based on data type
    if args.data_type == 'link':
        cmd = ['python3', str(script_path), '--url', args.data]
        if args.title:
            cmd.extend(['--title', args.title])
    
    # Execute
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode

if __name__ == "__main__":
    exit(main())
```

### File to Create: `/home/workspace/N5/knowledge/record_mappings.json`

```json
{
  "link": {
    "script": "n5_essential_links_add.py",
    "description": "Add essential links",
    "args_pattern": ["--url", "data", "--title", "title"]
  }
}
```

## Execution Steps

1. **Create Record Dispatcher Script**
   - Create `/home/workspace/N5/scripts/n5_record.py`
   - Implement basic routing logic
   - Add error handling

2. **Create Mappings File**
   - Create `/home/workspace/N5/knowledge/record_mappings.json`
   - Start with just "link" mapping
   - Add more types incrementally

3. **Test Integration**
   - Test: `python3 n5_record.py link "https://example.com" "Test"`
   - Verify it calls n5_essential_links_add.py
   - Check output and error handling

4. **Expand Gradually**
   - Add "fact" mapping to n5_knowledge_add.py
   - Add "person" mapping when person script exists
   - Test each addition separately

## Success Criteria
- `n5_record.py` successfully routes to existing scripts
- No data corruption or system crashes
- Simple, understandable code that follows N5 patterns
- Easy to add new data types and mappings

## Safety Measures
- Test with non-destructive operations first
- Validate all file paths before execution
- Capture and display all output/errors
- Use existing N5 safety patterns
- Keep implementation minimal and focused

This approach builds one simple piece at a time, testing each step, rather than attempting a complex system all at once.