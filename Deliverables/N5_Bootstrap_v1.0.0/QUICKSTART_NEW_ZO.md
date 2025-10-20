# N5 Bootstrap - New Zo Quickstart

**You are setting up N5 in a fresh Zo workspace!**

This guide will connect you to the parent Zo for guidance (Mobius Maneuver).

---

## Step 1: Extract Package (30 seconds)

```bash
cd /home/workspace
tar -xzf N5_Bootstrap_Package.tar.gz
cd N5_Bootstrap_Package
```

---

## Step 2: Connect to Parent Zo (Mobius Maneuver)

The parent Zo is running a support server at:

**`https://n5-bootstrap-support-va.zocomputer.io`**

Test connection:
```bash
curl https://n5-bootstrap-support-va.zocomputer.io/README.md
```

---

## Step 3: Get Conditional Rules (CRITICAL)

```bash
curl https://n5-bootstrap-support-va.zocomputer.io/configs/conditional_rules.md > conditional_rules.txt
cat conditional_rules.txt
```

**Action Required:** Copy these rules into your Zo user settings.

1. Go to https://[your-handle].zo.computer/settings
2. Find "Conditional Rules" section
3. Paste the rules from `conditional_rules.txt`
4. Save

---

## Step 4: Run Bootstrap Installer

```bash
python3 bootstrap.py
```

This will:
- ✅ Create directory structure
- ✅ Copy all files to correct locations
- ✅ Install dependencies
- ✅ Create initial documents

**Time:** ~5 minutes

---

## Step 5: Initialize Session State

```bash
python3 /home/workspace/N5/scripts/session_state_manager.py init --convo-id $ZO_CONVERSATION_ID --load-system
```

This loads core system files and creates your session state.

---

## Step 6: Test Core Commands

```bash
# Test commands system
python3 /home/workspace/N5/scripts/n5_commands_manage.py list

# Test knowledge system
python3 /home/workspace/N5/scripts/n5_knowledge_add.py --dry-run
```

---

## When You Get Stuck

Pull help from parent Zo:

```bash
# Troubleshooting guide
curl https://n5-bootstrap-support-va.zocomputer.io/help/troubleshooting.md

# Dependencies list
curl https://n5-bootstrap-support-va.zocomputer.io/help/dependencies.txt

# Quick fixes
curl https://n5-bootstrap-support-va.zocomputer.io/fixes/common_issues.md
```

---

## Next Steps

1. **Read docs:** `file 'Documents/N5.md'`
2. **Try commands:** Type `/` in chat to see available commands
3. **Add knowledge:** `/knowledge-add`
4. **Process meeting:** Upload a transcript and use `/meeting-process`

---

**Mobius Maneuver Active - Parent Zo is here to help!** 🚀

**Questions?** Ask your Zo AI - it has the bootstrap persona loaded.
