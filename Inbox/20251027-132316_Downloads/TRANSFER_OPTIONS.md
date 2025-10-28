# N5 Transfer Options - Corruption Workaround

**Problem:** tar.gz files getting corrupted during transfer to ChildZo\
**Created:** 2025-10-20 00:31 ET

---

## ✅ Option 1: Fresh Verified Package (RECOMMENDED)

**File:** `file n5_clean_verified.tar.gz` 

- **Size:** 1.2MB
- **Files:** 564 files (core N5 system)
- **Status:** ✅ Extracted and verified on ParentZo
- **MD5:** c5316a38db50f11c19700aad8aa0c878

**What's Included:**

- ✅ 104 command .md files (N5/commands/)
- ✅ 286+ Python scripts (N5/scripts/)
- ✅ 14 schema files (N5/schemas/)
- ✅ commands.jsonl registry (28KB, 104 entries)
- ✅ Core config (N5/config/, N5/prefs/)
- ✅ Essential docs ([N5.md](http://N5.md), architectural principles)

**What's Excluded (to reduce size):**

- ❌ Logs (N5/logs/)
- ❌ Exports (N5/exports/)
- ❌ Python cache files (\*.pyc, **pycache**)
- ❌ Large Knowledge/ directory (can sync separately if needed)

**Installation:**

```bash
cd /home/workspace
tar -xzf n5_clean_verified.tar.gz
chmod +x N5/scripts/*.py
```

**Verification:**

```bash
ls N5/commands/*.md | wc -l      # Expect: 104
ls N5/scripts/*.py | wc -l       # Expect: 286+
ls N5/schemas/*.json | wc -l     # Expect: 14
wc -l N5/config/commands.jsonl   # Expect: 104
ls Documents/N5.md N5/prefs/prefs.md
```

---

## Option 2: Split Archives (If Option 1 Still Corrupts)

Create 5 smaller archives to reduce transfer corruption risk:

1. **n5_commands.tar.gz** (\~100KB) - Commands only
2. **n5_scripts.tar.gz** (\~900KB) - Python scripts
3. **n5_config.tar.gz** (\~50KB) - Config & schemas
4. **n5_docs.tar.gz** (\~20KB) - Documentation
5. **n5_prefs.tar.gz** (\~100KB) - Preferences

Each file under 1MB for safer transfer.

---

## Option 3: Base64 Text Transfer (Slow but Reliable)

Convert tar.gz to base64 text, split into chunks, transfer via ZoBridge messages.

**Pros:**

- Text-based, survives copy/paste
- Can verify each chunk

**Cons:**

- 33% size overhead (1.2MB → 1.6MB)
- Requires multiple messages
- Manual reassembly

**Would only use if Options 1-2 fail**

---

## Option 4: Git Repository (Most Reliable)

Create a git repo of N5 on ParentZo, push to GitHub private repo, ChildZo clones.

**Pros:**

- Built-in integrity checking
- Version control
- Can push updates later

**Cons:**

- Requires GitHub setup
- More steps

**Best for long-term but overkill for one-time transfer**

---

## Option 5: Direct HTTP Download

Host the tar.gz on a temporary HTTP server from ParentZo, ChildZo downloads via curl.

```bash
# ParentZo:
cd /home/workspace/Downloads
python3 -m http.server 8000

# ChildZo:
curl -O http://[parentzo-ip]:8000/n5_clean_verified.tar.gz
```

**Pros:**

- Direct binary transfer
- No intermediary corruption

**Cons:**

- Need network connectivity between instances
- Port forwarding may be complex

---

## Recommended Strategy

1. **Try Option 1** (n5_clean_verified.tar.gz) - Fresh verified package
2. **If corrupted → Option 2** - Split into smaller archives
3. **If still failing → Option 5** - Direct HTTP download
4. **Last resort → Option 3** - Base64 text chunks

---

## Corruption Investigation

**Possible causes:**

- File upload size limits in Zo interface
- Browser caching issues during download/upload
- Network interruption during transfer
- File permission issues

**To diagnose:**

- Compare MD5 hash after each step
- Check file size at each stage
- Try different browser
- Try downloading/uploading from different location

---

## Next Step

**Which option would you like to try first?**

Default: Option 1 (n5_clean_verified.tar.gz)