# N5 OS Quick Start for Eric

Welcome! This is a **5-minute guide** to get N5 OS running on your Zo instance.

---

## Installation (3 minutes)

### Step 1: Clone the Repository

```bash
git clone https://github.com/zo-n5os/bootstrap.git
cd bootstrap
```

### Step 2: Run the Installer

```bash
bash bootstrap.sh
```

The installer will:
1. Check prerequisites (Python 3, Git)
2. Ask you which modules to install
3. Copy files to your installation path
4. Initialize git (optional)

### Step 3: Accept Defaults (or Customize)

When prompted:
- **Core Foundation**: Always installed (required)
- **List Management**: Recommended (y/n) → **Press Enter** for yes
- **Meeting Ingestion**: Recommended (y/n) → **Press Enter** for yes
- **Knowledge Base**: Optional (y/n) → **Press Enter** for no (or yes if interested)
- **Scripts Package**: Choose **B** (Standard) — best balance
- **Communications**: Optional (y/n) → **Press Enter** for no

**Total time**: ~2 minutes. Takes ~55 MB disk space with defaults.

---

## After Installation (2 minutes)

### Step 1: Verify Installation

```bash
cd [installation-path]  # or just cd . if you installed in current dir

# Check the structure
ls -la

# Should see: N5/, Knowledge/, Lists/, Documents/, Records/, .gitignore
```

### Step 2: Review System Overview

```bash
# Read the preferences index (understand the system)
cat N5/prefs/prefs.md

# Should see: Preferences structure, file paths, system status
```

### Step 3: Initialize Your First List

```bash
# Create an empty list from template
cp Lists/templates/ideas.jsonl.template Lists/ideas.jsonl

# Add your first idea
echo '{"tag": "ideas", "content": "Test N5 OS with Eric!", "date_created": "2025-10-26"}' >> Lists/ideas.jsonl

# View your lists
cat Lists/ideas.jsonl
```

### Step 4: Test a Command

```bash
# Rebuild the system index (safe dry-run)
python3 N5/scripts/n5_index_rebuild.py --dry-run

# Should output: "[DRY RUN] Index rebuilt" (no actual changes)
```

### Step 5: Initialize Git (Recommended)

```bash
git add -A
git commit -m "Initial N5 OS installation"

# Check status
git log --oneline | head -3
```

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `N5/prefs/prefs.md` | System overview and preferences index |
| `N5/config/commands.jsonl` | All registered commands (83+) |
| `N5/commands/` | Command documentation (.md files) |
| `Lists/POLICY.md` | Rules for working with lists |
| `Knowledge/stable/` | Reference materials (if installed) |
| `docs/ARCHITECTURE.md` | Deep dive into system design |
| `docs/MODULES.md` | Explanation of each module |

---

## Common First Tasks

### Task 1: View All Commands

```bash
# Pretty-print the command registry
python3 -m json.tool < N5/config/commands.jsonl | head -50

# Or search for a specific command
grep "meeting" N5/config/commands.jsonl
```

### Task 2: Add to Your Lists

```bash
# Add a person to contact
echo '{"tag": "must-contact", "name": "Alice", "email": "alice@example.com"}' >> Lists/must-contact.jsonl

# Add a task
echo '{"tag": "tasks", "description": "Learn N5 OS", "priority": "high"}' >> Lists/tasks.jsonl
```

### Task 3: Run a Real Command

```bash
# Process a git check (safely)
python3 N5/scripts/n5_git_check.py --dry-run

# Or rebuild the index (real)
python3 N5/scripts/n5_index_rebuild.py
```

### Task 4: Read a Protocol

```bash
# Understand how conversations work
cat N5/commands/conversation-end.md

# Understand git governance
cat N5/prefs/system/git-governance.md
```

---

## When You're Ready to Explore More

1. **Understand Preferences**: Read `N5/prefs/prefs.md` carefully
2. **See All Modules**: Read `docs/MODULES.md` for what you installed
3. **Deep Architecture**: Read `docs/ARCHITECTURE.md` for system design
4. **Add Commands**: See `Knowledge/stable/architectural_principles.md` for design patterns
5. **Work with Meetings**: Review `N5/commands/` for meeting-related commands

---

## Troubleshooting

### Q: Installation failed — Python not found

**A**: Install Python 3
```bash
# Ubuntu/Debian
sudo apt-get install python3

# macOS
brew install python3
```

### Q: Directory structure looks weird

**A**: Verify with:
```bash
find . -maxdepth 2 -type d | sort
```

Should see: N5/, Knowledge/, Lists/, etc.

### Q: Scripts aren't running

**A**: Check permissions:
```bash
chmod -R u+w .
```

Then try again:
```bash
python3 N5/scripts/n5_index_rebuild.py --dry-run
```

### Q: Want to add more modules later?

**A**: Run the bootstrap again or download specific modules from GitHub.

---

## Useful Commands to Know

| Command | Purpose |
|---------|---------|
| `python3 N5/scripts/n5_index_rebuild.py --dry-run` | Preview index changes |
| `python3 N5/scripts/n5_git_check.py` | Audit git changes |
| `cat N5/prefs/prefs.md` | System overview |
| `grep "command-name" N5/config/commands.jsonl` | Find a command |
| `cat Lists/POLICY.md` | List handling rules |

---

## Next: Call Vrijen

At this point, you're ready to:
1. Call Vrijen to discuss your N5 OS setup
2. Customize preferences in `N5/prefs/`
3. Start using commands from `N5/commands/`
4. Build workflows with your lists

---

**You're All Set!** 🎉

- Installation time: ~5 minutes ✅
- System files in place: ✅
- Ready to explore: ✅

**Next call with Vrijen:** Review `N5/prefs/prefs.md` together and discuss customizations.

---

**Version**: 1.0  
**For**: Eric's Zo Instance  
**Date**: 2025-10-26
