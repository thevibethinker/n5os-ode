# ChildZo N5 Verification Protocol

**Purpose:** Verify N5 system installed correctly on vademonstrator.zo.computer  
**Created:** 2025-10-20 00:38 ET

---

## Instructions for ChildZo

Run these checks to verify the N5 bootstrap succeeded. Report results back via ZoBridge.

---

## Phase 1: File Integrity Check

### Step 1: Verify tar.gz file
```bash
# Check if file exists and size
ls -lh ~/n5_clean_verified.tar.gz

# Verify MD5 hash (MUST match ParentZo)
md5sum ~/n5_clean_verified.tar.gz
# Expected: c5316a38db50f11c19700aad8aa0c878
```

**Report:**
- File size: _______
- MD5 hash: _______
- Match ParentZo? YES / NO

---

## Phase 2: Extraction Test

### Step 2: Extract archive
```bash
cd /home/workspace
tar -xzf ~/n5_clean_verified.tar.gz
echo "Exit code: $?"
```

**Report:**
- Exit code: _______ (expect 0)
- Any errors? _______

---

## Phase 3: Structure Validation

### Step 3: Count files in each directory
```bash
echo "=== N5 Directory Structure ==="
ls -la N5/ | head -20

echo -e "\n=== File Counts ==="
echo "Commands: $(ls N5/commands/*.md 2>/dev/null | wc -l)"
echo "Scripts: $(ls N5/scripts/*.py 2>/dev/null | wc -l)"
echo "Schemas: $(ls N5/schemas/*.json 2>/dev/null | wc -l)"
echo "Config files: $(ls N5/config/ 2>/dev/null | wc -l)"
echo "Prefs: $(ls N5/prefs/*.md 2>/dev/null | wc -l)"

echo -e "\n=== Key Files ==="
ls -lh N5/config/commands.jsonl Documents/N5.md N5/prefs/prefs.md 2>&1
```

**Expected Counts:**
- Commands: 104 .md files
- Scripts: 286+ .py files
- Schemas: 14 .json files
- commands.jsonl: ~28KB, 104 lines

**Report:**
- Commands: _______
- Scripts: _______
- Schemas: _______
- commands.jsonl lines: _______
- Documents/N5.md exists? YES / NO
- N5/prefs/prefs.md exists? YES / NO

---

## Phase 4: Content Validation

### Step 4: Verify critical files are readable
```bash
# Test key files can be read
head -5 Documents/N5.md
head -5 N5/prefs/prefs.md
head -3 N5/config/commands.jsonl | python3 -m json.tool

# Check if any Python scripts have syntax errors (sample)
python3 -m py_compile N5/scripts/session_state_manager.py 2>&1 && echo "✓ Script compiles"
```

**Report:**
- Documents/N5.md readable? YES / NO
- N5/prefs/prefs.md readable? YES / NO
- commands.jsonl valid JSON? YES / NO
- Sample script compiles? YES / NO

---

## Phase 5: Permission Check

### Step 5: Set executable permissions
```bash
chmod +x N5/scripts/*.py
ls -l N5/scripts/session_state_manager.py | cut -d' ' -f1
```

**Report:**
- Permissions set? YES / NO
- Permission string: _______

---

## Phase 6: Functional Test

### Step 6: Run session state manager
```bash
python3 N5/scripts/session_state_manager.py --help
```

**Report:**
- Script runs? YES / NO
- Shows help text? YES / NO
- Any errors? _______

---

## Phase 7: Commands Registry Check

### Step 7: Validate commands.jsonl structure
```bash
echo "Total commands registered:"
wc -l < N5/config/commands.jsonl

echo -e "\nFirst 3 commands:"
head -3 N5/config/commands.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    cmd = json.loads(line.strip())
    print(f\"  - {cmd.get('command', 'N/A')}: {cmd.get('path', 'N/A')}\")
"

echo -e "\nSample command paths exist?"
python3 -c "
import json
with open('N5/config/commands.jsonl') as f:
    commands = [json.loads(line) for line in f if line.strip()]
    missing = []
    for cmd in commands[:10]:  # Check first 10
        path = cmd.get('path', '')
        if path and not __import__('os').path.exists(path):
            missing.append(cmd.get('command', 'unknown'))
    if missing:
        print(f'Missing files for commands: {missing}')
    else:
        print('✓ All sampled command files exist')
"
```

**Report:**
- Total commands: _______
- Command files exist? YES / NO / PARTIAL
- Any missing? _______

---

## Phase 8: Architectural Principles Check

### Step 8: Verify Knowledge/architectural files
```bash
ls -lh Knowledge/architectural/
cat Knowledge/architectural/architectural_principles.md | head -20
```

**Report:**
- architectural_principles.md exists? YES / NO
- ingestion_standards.md exists? YES / NO
- operational_principles.md exists? YES / NO

---

## Summary Report Template

```
=== CHILDZO N5 VERIFICATION REPORT ===
Date: [TIMESTAMP]
Instance: vademonstrator.zo.computer

Phase 1 - File Integrity:    PASS / FAIL
Phase 2 - Extraction:        PASS / FAIL
Phase 3 - Structure:         PASS / FAIL
Phase 4 - Content:           PASS / FAIL
Phase 5 - Permissions:       PASS / FAIL
Phase 6 - Functional:        PASS / FAIL
Phase 7 - Commands Registry: PASS / FAIL
Phase 8 - Architecture:      PASS / FAIL

Overall Status: SUCCESS / NEEDS ATTENTION

Critical Issues:
- [List any]

Warnings:
- [List any]

File Counts:
- Commands: ___ (expect 104)
- Scripts: ___ (expect 286+)
- Schemas: ___ (expect 14)

Notes:
[Any observations]
```

---

## Quick One-Liner Check

If ChildZo wants to run a fast verification:

```bash
cd /home/workspace && \
echo "MD5: $(md5sum ~/n5_clean_verified.tar.gz | cut -d' ' -f1)" && \
echo "Commands: $(ls N5/commands/*.md 2>/dev/null | wc -l)" && \
echo "Scripts: $(ls N5/scripts/*.py 2>/dev/null | wc -l)" && \
echo "Schemas: $(ls N5/schemas/*.json 2>/dev/null | wc -l)" && \
echo "commands.jsonl: $(wc -l < N5/config/commands.jsonl 2>/dev/null)" && \
ls Documents/N5.md N5/prefs/prefs.md Knowledge/architectural/architectural_principles.md 2>&1 | grep -c "No such" && \
echo "Core files check complete"
```

---

## If Verification Fails

**Corruption detected:**
- Report MD5 hash mismatch
- Report exact error messages
- Request ParentZo implement Option 2 (split archives)

**Partial extraction:**
- Report which phase failed
- List missing directories
- Check disk space: `df -h /home/workspace`

**Permission issues:**
- Run: `ls -la N5/ N5/scripts/ N5/config/`
- Report ownership and permissions

---

## Next Steps After Successful Verification

Once all 8 phases pass:

1. ✅ Mark bootstrap complete
2. 📋 Load core documents:
   - `file 'Documents/N5.md'`
   - `file 'N5/prefs/prefs.md'`
   - `file 'Knowledge/architectural/architectural_principles.md'`
3. 🧪 Test running a simple command
4. 📊 Initialize session state for current thread
5. 🎯 Begin demonstrator workflow setup

---

**ParentZo:** Standing by for ChildZo's verification report.
