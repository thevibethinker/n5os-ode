# ChildZo N5 Installation Instructions

**Date:** 2025-10-20 00:51 ET  
**Package:** n5_clean_verified.tar.gz  
**MD5:** c5316a38db50f11c19700aad8aa0c878  
**Size:** 1.2MB  
**Files:** 593 files

---

## Quick Install (3 Commands)

```bash
# 1. Download verified package from ParentZo
curl -f -o /home/workspace/n5_clean_verified.tar.gz https://va-http-va.zocomputer.io/n5_clean_verified.tar.gz

# 2. Verify MD5 checksum
echo "c5316a38db50f11c19700aad8aa0c878  /home/workspace/n5_clean_verified.tar.gz" | md5sum -c -

# 3. Extract to workspace
cd /home/workspace && tar -xzf n5_clean_verified.tar.gz && rm n5_clean_verified.tar.gz
```

**Expected output from step 2:** `/home/workspace/n5_clean_verified.tar.gz: OK`

---

## Verification After Install

Run these commands to verify installation:

```bash
# Check core structure
ls -ld N5/ Documents/ N5/commands/ N5/scripts/ N5/config/ N5/schemas/

# Count files
echo "Commands: $(ls N5/commands/*.md 2>/dev/null | wc -l) (expect 104)"
echo "Scripts: $(ls N5/scripts/*.py 2>/dev/null | wc -l) (expect 286+)"
echo "Schemas: $(ls N5/schemas/*.json 2>/dev/null | wc -l) (expect 14)"

# Verify key files exist
ls -lh Documents/N5.md N5/prefs/prefs.md N5/config/commands.jsonl

# Check commands.jsonl
wc -l N5/config/commands.jsonl  # Expect: 104 lines

# Make scripts executable
chmod +x N5/scripts/*.py
```

---

## What's Included

✅ **Commands** (104): N5/commands/*.md - All registered commands  
✅ **Scripts** (286+): N5/scripts/*.py - Core automation  
✅ **Schemas** (14): N5/schemas/*.json - Data validation  
✅ **Config**: N5/config/, N5/prefs/ - System configuration  
✅ **Documentation**: Documents/N5.md, architectural principles  

**Excluded (intentionally):**
- N5/logs/ - Will be generated fresh
- N5/exports/ - Not needed on ChildZo
- Large Knowledge/ - Can sync separately if needed
- Python cache files

---

## Troubleshooting

**If download fails:**
```bash
# Try with verbose output
curl -v -f -o /home/workspace/n5_clean_verified.tar.gz https://va-http-va.zocomputer.io/n5_clean_verified.tar.gz
```

**If MD5 doesn't match:**
```bash
# Check what you got
md5sum /home/workspace/n5_clean_verified.tar.gz
# Expected: c5316a38db50f11c19700aad8aa0c878

# If mismatch, re-download
rm /home/workspace/n5_clean_verified.tar.gz
# Try download again
```

**If extraction fails:**
```bash
# Test archive integrity
tar -tzf /home/workspace/n5_clean_verified.tar.gz | head -20

# If corrupt, re-download
```

---

## Post-Install Setup

After successful install, ChildZo should:

1. **Load N5 documentation**
   ```
   Read file 'Documents/N5.md' and file 'N5/prefs/prefs.md'
   ```

2. **Verify commands registry**
   ```bash
   python3 N5/scripts/validate_commands.py
   ```

3. **Report installation status**
   - Total files installed
   - Any missing directories
   - Any errors encountered

---

## Success Criteria

✅ MD5 checksum matches  
✅ 593 files extracted  
✅ 104 command files present  
✅ 286+ script files present  
✅ 14 schema files present  
✅ commands.jsonl has 104 entries  
✅ Documents/N5.md exists  
✅ No extraction errors  

---

**Ready to install!** Copy the 3 Quick Install commands above and run them on ChildZo.

*Installation takes ~30 seconds*  
*Created: 2025-10-20 00:51 ET*
