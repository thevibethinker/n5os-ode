# Consultant Troubleshooting Guide

**For working on someone else's N5 OS installation (remote or in-person)**

---

## Quick Diagnostic Checklist

Run this first when helping a user:

```bash
# 1. Check N5 OS installed
ls -la /home/workspace/N5/ | head -10

# 2. Check version
cat /home/workspace/Documents/N5.md | head -3

# 3. Check recent activity
python3 /home/workspace/N5/scripts/n5_convo_list.py --limit 5

# 4. Check session state (if conversation active)
ls /home/workspace/N5/runtime/sessions/

# 5. Check for errors
tail -50 /home/workspace/N5/logs/*.log 2>/dev/null | grep -i error

# 6. Check git status
cd /home/workspace && python3 N5/scripts/n5_git_check.py

# 7. Check telemetry (if enabled)
python3 /home/workspace/N5/scripts/n5_telemetry_view.py --last 7-days
```

**Time**: ~2 minutes

---

## Essential Information Sources

### 1. Conversation Database
```bash
# What has the user been working on?
python3 N5/scripts/n5_convo_list.py --limit 20 --verbose

# Find conversations about specific topic
python3 N5/scripts/n5_convo_search.py "keyword"

# Show full details of a conversation
python3 N5/scripts/n5_convo_show.py con_ABC123
```

**Use Case**: Understand user's recent work before asking questions

### 2. Session State
```bash
# Current conversation state (if active)
find N5/runtime/sessions -name "SESSION_STATE.md" -type f -exec cat {} \;

# All session metadata
find N5/runtime/sessions -name ".metadata.json" -type f -exec cat {} \;
```

**Use Case**: Resume interrupted work, understand current focus

### 3. Git History
```bash
# Recent changes
cd /home/workspace && git log --oneline --since="7 days ago"

# Uncommitted changes
cd /home/workspace && git status

# Files changed recently
cd /home/workspace && git diff --name-only
```

**Use Case**: See what user has been modifying, find recent breakage

### 4. Lists Status
```bash
# What's in their lists?
for f in /home/workspace/Lists/*.jsonl; do 
  echo "$f: $(wc -l < $f) items"
done

# Recent additions
for f in /home/workspace/Lists/*.jsonl; do
  echo "=== $f ==="
  tail -5 "$f"
done
```

**Use Case**: Understand workflows, check data quality

### 5. Command Usage
```bash
# If telemetry enabled
python3 N5/scripts/n5_telemetry_view.py --last 30-days --summary

# Check command registry
cat N5/config/commands.jsonl | jq -r '.command' | sort
```

**Use Case**: See what features they're actually using

---

## Common Issues & Solutions

### Issue 1: "AI isn't maintaining context"

**Diagnostic**:
```bash
# Check if session state is initializing
ls N5/runtime/sessions/*/SESSION_STATE.md

# Check Zo rules configured
echo "Ask user: Are Zo rules configured? See ZO_SETTINGS_REQUIRED.md"
```

**Solution**:
1. Verify Rule 4 (Session State) in Zo settings
2. Test: Start new conversation, check if SESSION_STATE.md appears
3. If not: Walk through ZO_SETTINGS_REQUIRED.md setup

### Issue 2: "Commands aren't working"

**Diagnostic**:
```bash
# Check script exists
ls -la N5/scripts/n5_index_rebuild.py

# Check Python available
python3 --version

# Try running manually
python3 N5/scripts/n5_index_rebuild.py --dry-run
```

**Solution**:
1. Check Prerequisites in SETUP_REQUIREMENTS.md
2. Verify Python 3.8+ installed
3. Check script permissions: `chmod +x N5/scripts/*.py`

### Issue 3: "Git conflicts / merge issues"

**Diagnostic**:
```bash
cd /home/workspace
git status
git log --graph --oneline --all -10
```

**Solution**:
1. Run safety check: `python3 N5/scripts/n5_git_check.py`
2. If conflicts: Help user resolve manually or use snapshots
3. Document in session state for future reference

### Issue 4: "Lost work / can't find file"

**Diagnostic**:
```bash
# Search conversation database for file mention
python3 N5/scripts/n5_convo_search.py "filename"

# Check recent files
find /home/workspace -name "*filename*" -mtime -7

# Check conversation artifacts
python3 N5/scripts/n5_convo_show.py con_ABC123 --show-artifacts
```

**Solution**:
1. Check conversation database for which convo created it
2. Check session state of that conversation
3. Look in conversation workspace: `/home/.z/workspaces/con_*/`

### Issue 5: "System feels slow"

**Diagnostic**:
```bash
# Check disk space
df -h /home/workspace

# Check large files
du -sh /home/workspace/* | sort -h | tail -10

# Check session count
find N5/runtime/sessions -type d | wc -l
```

**Solution**:
1. Archive old sessions: `python3 N5/scripts/session_state_manager.py archive --days 30`
2. Clean up logs: `find N5/logs -name "*.log" -mtime +30 -delete`
3. Rebuild index: `python3 N5/scripts/n5_index_rebuild.py`

---

## Remote Troubleshooting Protocol

### Step 1: Get Context (5 min)
```bash
# Run diagnostic checklist above
# Review recent conversations
# Check telemetry (if enabled)
```

### Step 2: Reproduce Issue (10 min)
```bash
# Ask user for:
# - Exact steps to reproduce
# - Expected vs actual behavior
# - When did it start?

# Try to reproduce in their environment
# Check session state during reproduction
```

### Step 3: Identify Root Cause (10 min)
```bash
# Common causes:
# 1. Missing Zo rules → Check ZO_SETTINGS_REQUIRED.md
# 2. Python/Git not installed → Check SETUP_REQUIREMENTS.md
# 3. User config issue → Check user_config/
# 4. Script permissions → Check chmod +x
# 5. Path issues → Check hardcoded paths in scripts
```

### Step 4: Fix & Verify (10 min)
```bash
# Apply fix
# Test with user
# Document in conversation or session state
# Update user_config if needed
```

### Step 5: Document (5 min)
```bash
# Add to conversation database
python3 N5/scripts/n5_conversation_end.py \
  --convo-id con_ABC123 \
  --summary "Fixed [issue]: [solution]" \
  --outcome complete

# If it's a common issue, add to TROUBLESHOOTING.md
```

**Total Time**: ~40 minutes per issue

---

## Privacy & Access

### What You CAN Access
✅ System files (scripts, configs, docs)  
✅ Conversation metadata (titles, summaries)  
✅ Session state files  
✅ Telemetry (if user enabled)  
✅ Git history  
✅ Error logs

### What You CANNOT/SHOULD NOT Access
❌ `user_config/` — User's personal settings  
❌ `Lists/*.jsonl` — User's list data (unless debugging lists specifically)  
❌ `Records/` — User's personal records  
❌ Full conversation text (only metadata)  
❌ Credentials/API keys

### Getting Permission
```
"I need to check [X] to troubleshoot this. Is that okay?"

Examples:
- "Can I review your recent conversation summaries?"
- "Can I check your Lists to debug the list system?"
- "Can I view your user config to see your preferences?"
```

**Rule**: Always ask before accessing potentially sensitive data.

---

## User Education Tips

### Teaching Troubleshooting
1. **Show, don't just fix** — Walk through diagnostic steps together
2. **Document** — Add notes to their session state or conversation
3. **Empower** — Teach them to run diagnostics themselves next time

### Common User Mistakes
1. **Editing config files directly** → Use scripts instead
2. **Ignoring dry-run prompts** → Explain why they exist
3. **Not reading error messages** → Teach them to check logs
4. **Assuming AI remembers everything** → Explain session state

### Building Trust
1. **Explain what you're doing** — Narrate your diagnostic steps
2. **Ask permission** — Before accessing anything sensitive
3. **Document fixes** — So they can reference later
4. **Follow up** — Check if issue stayed fixed

---

## Billing & Time Tracking

### What to Log
```
- Date/Time
- User ID (installation_id if telemetry enabled)
- Issue description
- Time spent (diagnostic, fix, testing, documentation)
- Solution applied
- Follow-up needed?
```

### Time Estimates
- Quick question: 5-10 min
- Standard troubleshooting: 30-60 min
- Complex issue: 1-2 hours
- System design consultation: 2-4 hours

---

## Essential Files Reference

| File | Purpose | When to Check |
|------|---------|---------------|
| `SESSION_STATE.md` | Current work context | Active conversation |
| `conversation_registry.jsonl` | All past conversations | Finding prior work |
| `user_config/config.json` | User preferences | Config issues |
| `N5/logs/*.log` | Error logs | Debugging errors |
| `telemetry.jsonl` | Usage patterns | Understanding habits |
| `N5/config/commands.jsonl` | Available commands | Feature questions |
| `.git/` | Version history | Lost work, conflicts |

---

## Quick Commands Cheat Sheet

```bash
# Conversation history
python3 N5/scripts/n5_convo_list.py --limit 10

# Search conversations
python3 N5/scripts/n5_convo_search.py "keyword"

# Session state
cat N5/runtime/sessions/*/SESSION_STATE.md

# Git status
python3 N5/scripts/n5_git_check.py

# Rebuild index
python3 N5/scripts/n5_index_rebuild.py

# List health
for f in Lists/*.jsonl; do echo "$f: $(wc -l < $f)"; done

# Disk space
df -h /home/workspace

# Telemetry
python3 N5/scripts/n5_telemetry_view.py --last 7-days

# System info
cat Documents/N5.md | head -10
```

---

**Version**: 1.0-core  
**For**: Remote troubleshooting & consulting  
**Time to read**: 15 minutes  
**Date**: 2025-10-26
