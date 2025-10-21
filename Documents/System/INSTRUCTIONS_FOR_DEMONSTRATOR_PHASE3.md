# Phase 3 Instructions for Demonstrator Zo

**Status:** Conditional rules pulled ✅  
**Next:** Report status, then pull core N5 documentation

---

## Step 1: Report Phase 2 Completion (30 seconds)

Since you've successfully pulled the conditional rules and confirmed they match your settings, report status to parent:

```bash
curl -X POST https://n5-bootstrap-support-va.zocomputer.io/status \
  -d "✅ Phase 2 complete. Conditional rules pulled and verified. 8 rules active in system prompt. Ready for Phase 3."
```

**Expected:** Returns `{"status": "logged"}`

---

## Step 2: Pull Core N5 Documentation (2 minutes)

Now pull the essential N5 documentation:

```bash
# Create Documents directory
mkdir -p /home/workspace/Documents

# Pull core N5 documentation
curl -s https://n5-bootstrap-support-va.zocomputer.io/docs/N5.md > /home/workspace/Documents/N5.md

# Verify
echo "N5.md downloaded. Size: $(wc -c < /home/workspace/Documents/N5.md) bytes"
echo "Lines: $(wc -l < /home/workspace/Documents/N5.md)"

# Preview first 50 lines
head -50 /home/workspace/Documents/N5.md
```

---

## Step 3: Pull N5 Preferences (1 minute)

```bash
# Create N5/prefs directory
mkdir -p /home/workspace/N5/prefs

# Pull preferences
curl -s https://n5-bootstrap-support-va.zocomputer.io/configs/prefs.md > /home/workspace/N5/prefs/prefs.md

# Verify
echo "prefs.md downloaded. Lines: $(wc -l < /home/workspace/N5/prefs/prefs.md)"
head -30 /home/workspace/N5/prefs/prefs.md
```

---

## Step 4: Report Progress (30 seconds)

```bash
curl -X POST https://n5-bootstrap-support-va.zocomputer.io/status \
  -d "✅ Core documentation pulled: N5.md and prefs.md. Reviewing content now."
```

---

## Step 5: Read and Understand Core Docs (5 minutes)

**Ask your Zo AI:**

```
"Load and review file 'Documents/N5.md' and file 'N5/prefs/prefs.md'. 
Summarize the key concepts of the N5 system and what these preferences define."
```

This will help your Zo AI understand the N5 architecture before proceeding.

---

## Step 6: Get Next Guidance from Advisor (1 minute)

Query the advisor for what comes after documentation:

```bash
curl -X POST https://n5-advisor-va.zocomputer.io/bootstrap/query \
  -H "Content-Type: application/json" \
  -d '{"type": "next_step", "context": {"phase": 3, "completed": ["structure", "conditional_rules", "core_docs"]}}' | python3 -m json.tool
```

---

## Step 7: Check Available Scripts (1 minute)

See what scripts are available from parent:

```bash
curl -s https://n5-advisor-va.zocomputer.io/bootstrap/scripts | python3 -m json.tool
```

This will show you which scripts you can pull in the next phase.

---

## Quick Status Check

After Steps 1-5, you should have:

```bash
# Verify structure
ls -la /home/workspace/N5/
ls -la /home/workspace/Documents/
ls -la /home/workspace/N5/prefs/

# Should show:
# N5/CONDITIONAL_RULES.md ✅
# N5/prefs/prefs.md ✅
# Documents/N5.md ✅
```

---

## Timeline Estimate

- **Step 1:** 30 sec - Report status
- **Step 2:** 2 min - Pull N5.md
- **Step 3:** 1 min - Pull prefs.md
- **Step 4:** 30 sec - Report progress
- **Step 5:** 5 min - Review docs with AI
- **Step 6:** 1 min - Get next guidance
- **Step 7:** 1 min - Check available scripts

**Total:** ~11 minutes for Phase 3

---

## After Phase 3

You'll have:
- ✅ N5 directory structure
- ✅ Conditional rules active
- ✅ Core N5 documentation (N5.md)
- ✅ N5 preferences (prefs.md)
- ✅ Understanding of N5 architecture
- ✅ List of available scripts for Phase 4

**Next phases:**
- Phase 4: Essential scripts (session_state, safety checks, etc.)
- Phase 5: Configuration files
- Phase 6: Testing and validation

---

## Troubleshooting

### Download Issues
If any curl fails:
```bash
# Test connection
curl -s https://n5-bootstrap-support-va.zocomputer.io/README.md

# List all available files
curl -s https://n5-bootstrap-support-va.zocomputer.io/
```

### File Empty or Corrupted
```bash
# Re-download
curl -s https://n5-bootstrap-support-va.zocomputer.io/docs/N5.md > /home/workspace/Documents/N5.md

# Check size (should be > 1000 bytes)
ls -lh /home/workspace/Documents/N5.md
```

### Report Any Issues
```bash
curl -X POST https://n5-bootstrap-support-va.zocomputer.io/status \
  -d "❌ ERROR: [describe issue]"
```

---

**Ready to proceed!** 🚀

*Parent is watching the monitor log - all your status updates appear in real-time*
