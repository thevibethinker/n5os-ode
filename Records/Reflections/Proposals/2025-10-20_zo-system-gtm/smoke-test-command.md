---
category: system
priority: high
description: Smoke test for demonstrator or cloned Zo System to verify core ingestion and output workflows.
---
# Smoke Test (Demonstrator / Clone Validation)

**Purpose:** Validate that reflection and meeting ingestion pipelines work end-to-end after clone or deployment.

---

## Usage

```bash
command 'N5/commands/smoke-test.md'
# Or directly:
python3 /home/workspace/N5/scripts/smoke_test.py [--skip-reflection] [--skip-meeting]
```

---

## Test Coverage

### 1. Reflection Pipeline
- Stage a test text reflection: `N5/records/reflections/incoming/smoke_test_reflection.txt`
- Run: `python3 /home/workspace/N5/scripts/reflection_ingest.py`
- Assert:
  - Transcript created: `.transcript.jsonl` exists
  - Outputs generated: `N5/records/reflections/outputs/smoke_test_reflection/`
  - Registry entry: status=awaiting-approval
  - Proposal created: `Records/Reflections/Proposals/smoke_test_reflection_proposal.md` or folder

### 2. Meeting Pipeline
- Query Calendar for a recent/test event
- Process via: `command 'N5/commands/auto-process-meetings.md'` or equivalent
- Assert:
  - Meeting notes/summary saved to appropriate Records path
  - No crashes, logs indicate success

### 3. Lists Write
- Add a test item: `python3 /home/workspace/N5/scripts/n5_lists_add.py ideas "Smoke test item"`
- Assert:
  - Item appears in `Lists/ideas.jsonl`
  - Markdown view updated
  - Command exits 0

### 4. Commands Registry
- Verify: `file 'N5/config/commands.jsonl'` is valid JSON and contains at least:
  - reflection-ingest
  - auto-process-meetings
  - thread-export

---

## Exit Codes
- 0: All tests passed
- 1: At least one failure

---

## Implementation

Script: `file 'N5/scripts/smoke_test.py'`

Example workflow:
```python
#!/usr/bin/env python3
import sys, subprocess, json
from pathlib import Path

def test_reflection():
    # Stage test file
    incoming = Path("/home/workspace/N5/records/reflections/incoming")
    test_file = incoming / "smoke_test_reflection.txt"
    test_file.write_text("This is a smoke test reflection.")
    
    # Run ingest
    result = subprocess.run(["python3", "/home/workspace/N5/scripts/reflection_ingest.py"], capture_output=True)
    if result.returncode != 0:
        return False
    
    # Check outputs
    outputs = Path("/home/workspace/N5/records/reflections/outputs/smoke_test_reflection")
    if not outputs.exists():
        return False
    
    return True

def test_lists():
    result = subprocess.run([
        "python3", "/home/workspace/N5/scripts/n5_lists_add.py",
        "ideas", "Smoke test item", "--tags", "smoke-test"
    ], capture_output=True)
    return result.returncode == 0

def test_commands_registry():
    reg = Path("/home/workspace/N5/config/commands.jsonl")
    if not reg.exists():
        return False
    try:
        data = [json.loads(line) for line in reg.read_text().strip().split("\n") if line]
        return len(data) > 0
    except:
        return False

def main():
    tests = [
        ("Reflection Pipeline", test_reflection),
        ("Lists Write", test_lists),
        ("Commands Registry", test_commands_registry),
    ]
    
    failures = []
    for name, test in tests:
        print(f"Running: {name}... ", end="")
        try:
            if test():
                print("✓ PASS")
            else:
                print("✗ FAIL")
                failures.append(name)
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failures.append(name)
    
    if failures:
        print(f"\n✗ {len(failures)} test(s) failed: {', '.join(failures)}")
        return 1
    else:
        print("\n✓ All smoke tests passed")
        return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## Notes
- Meeting test requires Calendar integration; skip with `--skip-meeting` if not set up yet.
- Cleanup: Smoke test items can be archived or deleted after validation.
