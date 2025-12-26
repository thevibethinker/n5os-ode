# N5 OS Core — First Run Checklist

**Complete these steps after installation to ensure everything works**

---

## Pre-Installation (5 minutes)

- [ ] Git installed (`git --version`)
- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] Have 500 MB free disk space (`df -h`)
- [ ] Read `README.md` (overview)

---

## Installation (3 minutes)

- [ ] Cloned repo: `git clone https://github.com/vrijenattawar/n5os-core.git`
- [ ] Ran installer: `bash bootstrap.sh`
- [ ] No errors during installation
- [ ] Directory structure created (check with `ls -la`)

---

## Core Verification (5 minutes)

### 1. Test Scripts
```bash
# Index rebuild (dry-run)
python3 N5/scripts/n5_index_rebuild.py --dry-run
# Should output: "[DRY RUN] Would rebuild index..."

# Git safety check
python3 N5/scripts/n5_git_check.py
# Should output git status

# Session state manager
python3 N5/scripts/session_state_manager.py --help
# Should show help text
```

- [ ] All 3 scripts run without errors

### 2. Verify Structure
```bash
ls N5/
ls Lists/
ls Knowledge/
```

- [ ] `N5/` directory exists with subfolders
- [ ] `Lists/` directory exists
- [ ] `Knowledge/` directory exists
- [ ] `Documents/` directory exists

### 3. Check Files
```bash
cat N5/prefs/prefs.md | head -20
cat docs/zero_touch_manifesto.md | head -30
```

- [ ] Prefs file readable
- [ ] Zero-Touch manifesto readable
- [ ] No empty/corrupt files

---

## Zo Settings Configuration (10 minutes)

Follow `file 'ZO_SETTINGS_REQUIRED.md'`:

- [ ] Added Rule 1: Anti-Hallucination
- [ ] Added Rule 2: Clarifying Questions (3+)
- [ ] Added Rule 3: Safety Checks (dry-run/confirmation)
- [ ] Added Rule 4: Session State Management
- [ ] Added Rule 5: Load System Files First

**Test**: Ask Zo to "build a script" - should ask 3+ questions first.

---

## Lists Initialization (3 minutes)

```bash
# Create your first lists from templates
cp Lists/ideas.jsonl.template Lists/ideas.jsonl
cp Lists/must-contact.jsonl.template Lists/must-contact.jsonl

# Add a test entry
echo '{"tag": "ideas", "title": "Test N5 OS", "description": "Verify system works", "date": "2025-10-26"}' >> Lists/ideas.jsonl

# Verify
cat Lists/ideas.jsonl
```

- [ ] Lists created
- [ ] Test entry added
- [ ] File readable

---

## Git Initialization (2 minutes)

```bash
cd /home/workspace
git init
git add N5/ Lists/ Knowledge/ Documents/
git commit -m "Initial N5 OS setup"
```

- [ ] Git repo initialized
- [ ] Initial commit made
- [ ] No errors

---

## First Documentation Read (15 minutes)

**Essential Reading** (in order):
1. [ ] `QUICK_START.md` (5 min) — Get oriented
2. [ ] `docs/zero_touch_manifesto.md` (10 min) — Understand philosophy
3. [ ] `core/knowledge/architectural_principles.md` (skim, 5 min) — Design patterns

**Optional** (for later):
- [ ] `HOW_TO_BUILD.md` — If extending
- [ ] `SCHEDULED_TASKS.md` — If automating
- [ ] `SETUP_REQUIREMENTS.md` — For integrations

---

## Optional: Scheduled Tasks (5 minutes)

See `SCHEDULED_TASKS.md` for full guide.

**Minimal Setup**:
- [ ] Daily index rebuild (6am)
- [ ] Weekly git check (Monday 9am)

**Setup via**: https://[username].zo.computer/agents

---

## Optional: Persona Setup (2 minutes)

```bash
# Load Vibe Builder persona in Zo
# In any conversation, say:
"Load Vibe Builder persona"

# Or: Copy content of core/personas/vibe_builder_persona.md 
# into Zo settings → Custom Persona
```

- [ ] Persona loaded/configured
- [ ] Test: "Build a simple script" should follow principles

---

## Success Verification

**You're ready if**:
✅ All scripts run without errors  
✅ Directory structure complete  
✅ Zo settings configured (5 rules)  
✅ Git initialized  
✅ Lists created and testable  
✅ Read Zero-Touch manifesto  

---

## First Real Task (10 minutes)

**Test the system**:
1. Create an idea
   ```bash
   echo '{"tag": "ideas", "title": "My first real idea", "description": "Something useful", "date": "2025-10-26"}' >> Lists/ideas.jsonl
   ```

2. Rebuild index
   ```bash
   python3 N5/scripts/n5_index_rebuild.py
   ```

3. Check git status
   ```bash
   python3 N5/scripts/n5_git_check.py
   ```

4. Commit your work
   ```bash
   git add Lists/ideas.jsonl
   git commit -m "Added first idea"
   ```

- [ ] All steps completed successfully
- [ ] No errors encountered
- [ ] System feels responsive

---

## Troubleshooting

**Problem**: Script errors  
**Solution**: Check Python version (`python3 --version` should be 3.8+)

**Problem**: Permission denied  
**Solution**: `chmod +x N5/scripts/*.py`

**Problem**: Git errors  
**Solution**: Configure git: `git config --global user.name "Your Name"` and `git config --global user.email "you@example.com"`

**Problem**: Empty files  
**Solution**: Re-run bootstrap.sh

**Problem**: Zo not following rules  
**Solution**: Double-check rules are saved in settings

---

## Next Steps

After completing this checklist:
1. **Use it for 1 week** — Track ideas, test workflows
2. **Review** — What worked? What didn't?
3. **Customize** — Add your own scripts/workflows
4. **Expand** — Consider expansion packs (future)

---

## Getting Help

- **Docs**: All `.md` files in package
- **GitHub Issues**: https://github.com/vrijenattawar/n5os-core/issues
- **Philosophy**: Re-read Zero-Touch manifesto

---

**Estimated Total Time**: 45 minutes  
**Status**: Ready to use daily

**Version**: 1.0-core  
**Date**: 2025-10-26
