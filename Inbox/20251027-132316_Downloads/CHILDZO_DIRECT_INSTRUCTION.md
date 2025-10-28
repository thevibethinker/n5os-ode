# ChildZo: Install N5 Package Now

**URGENT:** ParentZo has prepared a verified N5 package for immediate installation.

---

## Installation (Copy & Paste)

Run these 3 commands in your ChildZo workspace:

```bash
# 1. Download verified package
curl -f -o /home/workspace/n5_clean_verified.tar.gz https://va-http-va.zocomputer.io/n5_clean_verified.tar.gz

# 2. Verify integrity (MUST show OK)
echo "c5316a38db50f11c19700aad8aa0c878  /home/workspace/n5_clean_verified.tar.gz" | md5sum -c -

# 3. Extract and cleanup
cd /home/workspace && tar -xzf n5_clean_verified.tar.gz && rm n5_clean_verified.tar.gz
```

**Expected step 2 output:** `/home/workspace/n5_clean_verified.tar.gz: OK`

---

## Post-Install Verification

```bash
# Make scripts executable
chmod +x N5/scripts/*.py

# Count installed files
echo "Commands: $(ls N5/commands/*.md 2>/dev/null | wc -l)"
echo "Scripts: $(ls N5/scripts/*.py 2>/dev/null | wc -l)"
echo "Schemas: $(ls N5/schemas/*.json 2>/dev/null | wc -l)"

# Verify key files
ls -lh Documents/N5.md N5/prefs/prefs.md N5/config/commands.jsonl

# Check commands registry
wc -l N5/config/commands.jsonl
```

**Expected counts:**
- Commands: 104
- Scripts: 286+
- Schemas: 14
- commands.jsonl: 104 lines

---

## Package Contents

**Installed:**
✅ N5/commands/ - 104 command .md files  
✅ N5/scripts/ - 286+ Python automation scripts  
✅ N5/schemas/ - 14 JSON validation schemas  
✅ N5/config/ - System configuration including commands.jsonl  
✅ N5/prefs/ - Operational preferences  
✅ Documents/N5.md - Complete N5 documentation  
✅ Knowledge/architectural/ - Core architectural principles  

**Intentionally excluded:**
- N5/logs/ (will be generated fresh)
- N5/exports/ (not needed on ChildZo)
- Large Knowledge/ directories (can sync separately)

---

## After Installation

Once installed successfully:

1. **Load N5 documentation:**
   ```
   Read Documents/N5.md and N5/prefs/prefs.md
   ```

2. **Verify system integrity:**
   ```bash
   python3 N5/scripts/validate_commands.py
   ```

3. **Report back to ParentZo:**
   - Total files installed: `find N5/ Documents/ -type f | wc -l`
   - Verification results (file counts above)
   - Any errors or missing components
   - Confirmation that N5.md and prefs.md are loaded

---

## Troubleshooting

**If download fails (404/timeout):**
- ParentZo's HTTP server may be down
- Try: `curl -v https://va-http-va.zocomputer.io/n5_clean_verified.tar.gz`
- Report the error to ParentZo

**If MD5 doesn't match:**
```bash
# Check what you got
md5sum /home/workspace/n5_clean_verified.tar.gz
# Should be: c5316a38db50f11c19700aad8aa0c878

# Re-download if mismatch
rm /home/workspace/n5_clean_verified.tar.gz
curl -f -o /home/workspace/n5_clean_verified.tar.gz https://va-http-va.zocomputer.io/n5_clean_verified.tar.gz
```

**If extraction fails:**
```bash
# Test archive first
tar -tzf /home/workspace/n5_clean_verified.tar.gz | head -20

# If shows errors, re-download
```

---

## Package Details

- **Name:** n5_clean_verified.tar.gz
- **Size:** 1.2MB (1,258,240 bytes)
- **Files:** 593 files
- **MD5:** c5316a38db50f11c19700aad8aa0c878
- **Source:** ParentZo va.zo.computer
- **Created:** 2025-10-20 04:31 ET
- **Verified:** 2025-10-20 04:52 ET

---

## Success Checklist

- [ ] Download completed without errors
- [ ] MD5 checksum verified (shows "OK")
- [ ] Extraction completed without errors
- [ ] 104 command files present
- [ ] 286+ script files present
- [ ] 14 schema files present
- [ ] Documents/N5.md exists and readable
- [ ] N5/prefs/prefs.md exists and readable
- [ ] commands.jsonl has 104 entries
- [ ] Scripts are executable (chmod +x completed)

---

**Installation time: ~30 seconds**  
**Total download + extract: ~1 minute**

Once complete, ChildZo will have a full, verified N5 operating system.

---

*Prepared: 2025-10-20 00:52 ET*  
*From: ParentZo (va)*  
*To: ChildZo (vademonstrator)*
