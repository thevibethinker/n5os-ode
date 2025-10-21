# N5 Quickstart Guide

**Goal:** Get N5 running in 15 minutes

---

## Step 1: Upload Package (2 min)

If you received this as a .tar.gz file:

```bash
cd /home/workspace
tar -xzf N5_Bootstrap_Package.tar.gz
cd N5_Bootstrap_Package
```

Or if files are already in your workspace, navigate to the package directory.

---

## Step 2: Run Bootstrap Installer (5 min)

```bash
python3 bootstrap.py
```

This will:
- Copy all files to correct locations
- Create directory structure
- Install Python dependencies
- Initialize the system

**Expected output:**
```
✅ Scripts installed: 72
✅ Configs installed: 15
✅ Commands registered: 92
✅ System ready!
```

---

## Step 3: Verify Installation (2 min)

Check that N5 directories exist:

```bash
ls -la /home/workspace/N5
ls -la /home/workspace/Knowledge
ls -la /home/workspace/Lists
```

Test a basic command:

```bash
cd /home/workspace
python3 N5/scripts/session_state_manager.py --help
```

---

## Step 4: Initialize Your First Session (3 min)

In Zo chat, type:

```
/init-state-session
```

This creates `SESSION_STATE.md` and loads system preferences.

---

## Step 5: Try Core Commands (3 min)

### Add knowledge
```
/knowledge-add
```

Zo will guide you through capturing a piece of information.

### Search knowledge
```
/knowledge-find
```

Search for what you just added.

### View available commands
Type `/` in Zo chat to see autocomplete list of all commands.

---

## Common First Actions

### Capture a meeting
1. Upload a transcript file to `/home/workspace/Records/`
2. Run `/meeting-process`
3. Review and approve the processed output

### Add a task
```
/lists-add
```

### Read the docs
```
Read file 'Documents/N5.md'
```

---

## Troubleshooting

### "Command not found"
- Check that files are in `/home/workspace/N5/commands/`
- Refresh Zo (Cmd+R or Ctrl+R)

### "Module not found" errors
```bash
pip install anthropic openai aiohttp
```

### Scripts won't run
```bash
chmod +x /home/workspace/N5/scripts/*.py
```

### Need help
- Read `INSTALLATION.md` for detailed steps
- Check `docs/ARCHITECTURE.md` for system overview
- Ask in Zo chat: "How does N5 work?"

---

## Next Steps

1. **Read:** `file 'Knowledge/architectural/architectural_principles.md'`
2. **Explore:** Browse `/home/workspace/N5/commands/` to see what's available
3. **Customize:** Edit `N5/prefs/prefs.md` to match your preferences
4. **Build:** Start capturing your knowledge and meetings

---

**You're ready!** 🎉

Start with what you need most: knowledge capture, meeting processing, or task tracking.
