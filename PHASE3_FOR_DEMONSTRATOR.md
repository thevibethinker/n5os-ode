# Phase 2 Instructions for Demonstrator Zo

**Status:** Directory structure complete ✅\
**Next:** Pull conditional rules and add to settings

---

## Step 1: Pull Conditional Rules (2 minutes)

Copy and paste these commands into your Zo workspace:

```bash
# Create N5 directory if not exists
mkdir -p /home/workspace/N5

# Pull conditional rules from parent
curl -s https://n5-bootstrap-support-va.zocomputer.io/configs/conditional_rules.md > /home/workspace/N5/CONDITIONAL_RULES.md

# Verify download
echo "File downloaded. Lines: $(wc -l < /home/workspace/N5/CONDITIONAL_RULES.md)"
cat /home/workspace/N5/CONDITIONAL_RULES.md | head -30
```

**Expected:** You should see conditional rules content starting with "# N5 Conditional Rules for Zo"

---

## Step 2: Report Status to Parent (30 seconds)

```bash
curl -X POST https://n5-bootstrap-support-va.zocomputer.io/status \
  -d "✅ Conditional rules downloaded. File has $(wc -l < /home/workspace/N5/CONDITIONAL_RULES.md) lines. Ready to add to Zo settings."
```

**Expected:** Returns `{"status": "logged"}`

**Parent will see:** Your message in their monitor log in real-time

---

## Step 3: Add Rules to Your Zo Settings (3 minutes)

### A. Open the rules file

```bash
cat /home/workspace/N5/CONDITIONAL_RULES.md
```

### B. Copy the rules section

The file contains conditional rules in this format:

```markdown
- CONDITION: When X happens -> RULE: Do Y
```

### C. Add to Zo Settings

1. Go to your Zo Settings (click your avatar → Settings)
2. Find "User Rules" section
3. Look for "Conditional Rules"
4. Paste the rules from the file
5. Save settings

### D. Test that rules are active

Ask your Zo AI to do something that should trigger a rule, or just ask:

```markdown
"Load file 'N5/CONDITIONAL_RULES.md' and confirm you can see conditional rules"
```

---

## Step 4: Confirm Completion (30 seconds)

After rules are added and tested:

```bash
curl -X POST https://n5-bootstrap-support-va.zocomputer.io/status \
  -d "✅ Conditional rules added to Zo settings and tested. Rules are active."
```

---

## Step 5: Get Next Phase Guidance (1 minute)

Ask the advisor what to do next:

```bash
# Get full bootstrap checklist
curl -s https://n5-advisor-va.zocomputer.io/bootstrap/checklist | python3 -m json.tool

# Or get next step specifically
curl -X POST https://n5-advisor-va.zocomputer.io/bootstrap/query \
  -H "Content-Type: application/json" \
  -d '{"type": "next_step", "context": {"phase": 2, "completed": ["structure", "conditional_rules"]}}'
```

---

## Quick Reference: Available Help

### Get Help on Topics

```bash
# Session state management
curl -s https://n5-advisor-va.zocomputer.io/bootstrap/help/session_state

# Commands system
curl -s https://n5-advisor-va.zocomputer.io/bootstrap/help/commands

# Troubleshooting
curl -s https://n5-advisor-va.zocomputer.io/bootstrap/help/troubleshooting
```

### Pull Additional Files

```bash
# See what's available
curl -s https://n5-bootstrap-support-va.zocomputer.io/

# Pull specific files
curl -s https://n5-bootstrap-support-va.zocomputer.io/help/troubleshooting.md
curl -s https://n5-bootstrap-support-va.zocomputer.io/docs/README.md
```

### Report Any Issues

```bash
curl -X POST https://n5-bootstrap-support-va.zocomputer.io/status \
  -d "❌ ERROR: [describe your issue]"
```

---

## Troubleshooting

### Can't Download Files

**Problem:** `curl` fails or returns errors

**Solution:**

1. Test connection: `curl -s https://n5-bootstrap-support-va.zocomputer.io/README.md`
2. Check URL is exactly correct (copy-paste)
3. Try in browser first: <https://n5-bootstrap-support-va.zocomputer.io/configs/conditional_rules.md>

### Rules Not Working

**Problem:** Conditional rules don't seem to trigger

**Solution:**

1. Verify rules were added to correct section in settings
2. Save and reload Zo
3. Test with explicit command that should trigger rule
4. Report issue to parent via POST /status

### Status POST Not Working

**Problem:** Can't send status to parent

**Solution:**

1. Test endpoint: `curl -X POST https://n5-bootstrap-support-va.zocomputer.io/status -d "test"`
2. Should return: `{"status": "logged"}`
3. If fails, report in Zo chat to parent

---

## Timeline Estimate

- **Step 1:** 2 minutes - Pull files
- **Step 2:** 30 seconds - Report status
- **Step 3:** 3 minutes - Add to settings
- **Step 4:** 30 seconds - Confirm
- **Step 5:** 1 minute - Get next guidance

**Total:** \~7 minutes for Phase 2

---

## After Phase 2

You'll have:

- ✅ N5 directory structure
- ✅ Conditional rules active in Zo
- ✅ Connection to parent advisor
- ✅ Ability to pull files on demand

**Next phases** (guided by advisor):

- Core N5 documentation
- Essential scripts
- Configuration files
- Testing and validation

---

**Ready when you are!** 🚀

*Parent is monitoring: any status you POST will appear in their log in real-time*