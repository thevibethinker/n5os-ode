# Quick Fixes for Common N5 Bootstrap Issues

## 1. "No module named 'anthropic'" (or similar)

```bash
pip3 install anthropic openai aiohttp python-dotenv pyyaml jsonschema
```

## 2. "commands.jsonl not found"

```bash
# If you have the command .md files:
python3 /home/workspace/N5/scripts/n5_commands_manage.py rebuild

# If commands don't exist yet, that's OK - you'll build them incrementally
```

## 3. "SESSION_STATE.md not found"

```bash
# Get your conversation ID first
echo $ZO_CONVERSATION_ID

# Then initialize
python3 /home/workspace/N5/scripts/session_state_manager.py init \
    --convo-id $ZO_CONVERSATION_ID \
    --type discussion
```

## 4. Scripts not executable

```bash
chmod +x /home/workspace/N5/scripts/*.py
```

## 5. Missing directories

```bash
mkdir -p /home/workspace/{Knowledge/{architectural},Lists,Records/{meetings,temporary}}
mkdir -p /home/workspace/N5/{intelligence,lists,records,config/credentials}
```

## 6. Empty or invalid JSON configs

```bash
# Check if file is valid JSON
jq . /home/workspace/N5/config/commands.jsonl

# If empty or invalid, you may need to rebuild from scratch
# Start with minimal valid JSON:
echo '[]' > /home/workspace/N5/config/commands.jsonl
```

## 7. Git errors

```bash
cd /home/workspace
git init
git config user.name "N5 Bootstrap"
git config user.email "bootstrap@n5.local"
```

## 8. Can't find architectural principles

```bash
# Check if file exists
ls -la /home/workspace/Knowledge/architectural/architectural_principles.md

# If missing, the bootstrap package has it - check extracted folder
ls -la /home/workspace/N5_Bootstrap_Package_Extracted/knowledge/architectural/
```

## Emergency Reset

If completely broken:

```bash
# Backup current state
mv /home/workspace/N5 /home/workspace/N5_BROKEN_$(date +%s)

# Re-extract bootstrap
cd /home/workspace
tar -xzf N5_Bootstrap_Package.tar.gz
cd N5_Bootstrap_Package
python3 bootstrap.py
```

---

*Pull this file anytime: `curl http://<server>/fixes/common_issues.md`*
