# N5 Bootstrap Troubleshooting Guide

## Common Issues After Installation

### 1. Scripts Failing to Run

**Symptom:** `ModuleNotFoundError` or `ImportError`

**Fix:**
```bash
# Install missing Python dependencies
pip3 install --upgrade pip
pip3 install anthropic openai aiohttp python-dotenv pyyaml jsonschema

# Verify installation
python3 -c "import anthropic; import openai; print('✓ Dependencies OK')"
```

### 2. Commands Not Working

**Symptom:** Slash commands don't appear or don't execute

**Fix:**
```bash
# Check commands.jsonl exists and is valid
ls -la /home/workspace/N5/config/commands.jsonl
cat /home/workspace/N5/config/commands.jsonl | jq . | head -20

# If file is empty or missing, regenerate from command files
python3 /home/workspace/N5/scripts/n5_commands_manage.py rebuild
```

### 3. Session State Not Initializing

**Symptom:** `SESSION_STATE.md not found` errors

**Fix:**
```bash
# Initialize session state manually
cd /home/.z/workspaces/<your_convo_id>
python3 /home/workspace/N5/scripts/session_state_manager.py init \
    --convo-id <your_convo_id> \
    --type discussion
```

### 4. Missing Directory Structures

**Symptom:** `FileNotFoundError: [Errno 2] No such file or directory`

**Fix:**
```bash
# Create core directories
mkdir -p /home/workspace/{Knowledge,Lists,Records/{meetings,temporary},N5/{intelligence,lists,records}}

# Verify structure
tree -L 2 /home/workspace
```

### 5. Conditional Rules Not Applied

**Symptom:** Zo doesn't follow N5 patterns, ignores protocols

**Fix:**
1. Go to Zo settings (https://<your-handle>.zo.computer/settings)
2. Add conditional rules from: `curl http://<bootstrap-server>/configs/conditional_rules.md`
3. Save and refresh conversation

### 6. Permissions Issues

**Symptom:** `Permission denied` errors

**Fix:**
```bash
# Make scripts executable
chmod +x /home/workspace/N5/scripts/*.py

# Check ownership (should be root in Zo)
ls -la /home/workspace/N5/scripts/ | head -10
```

## Getting More Help

**From this server:**
```bash
# Check what's available
curl http://<bootstrap-server>/help/

# Get specific fixes
curl http://<bootstrap-server>/fixes/common_issues.md

# Get dependencies list
curl http://<bootstrap-server>/help/dependencies.txt
```

**Ask me directly:**
```
"I'm getting error X when trying to Y. Here's the output: [paste output]"
```

I'll fetch the right fix from my support server and guide you.

## Bootstrap Phases

If totally stuck, rebuild incrementally:

1. **Phase 1:** Directory structure only
2. **Phase 2:** Schemas + configs
3. **Phase 3:** Core scripts (n5_commands_manage, session_state_manager)
4. **Phase 4:** Commands
5. **Phase 5:** Meeting system
6. **Phase 6:** Test each layer before proceeding

---

*Mobius Maneuver: Pull help, never push changes*
