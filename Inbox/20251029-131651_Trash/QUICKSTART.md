# N5 OS Core - Quick Start Guide

**Get up and running in 10 minutes**

---

## What is N5 OS?

N5 OS is a **personal operating system** for AI-assisted productivity. It provides:

- **📁 Organized workspace** - Structured file system for knowledge, tasks, and automation
- **🤖 AI-first design** - Built specifically for human-AI collaboration
- **⚙️ Automation framework** - Scripts, workflows, and command registry
- **📊 Knowledge management** - Principles, standards, and SSOT architecture
- **🔄 Zero-touch operations** - Automated maintenance and self-healing systems

---

## Prerequisites (2 minutes)

### Required

- **Git** - Version control
  ```bash
  git --version  # Check if installed
  # If not: apt update && apt install -y git
  ```

- **Python 3.8+** - Scripting runtime
  ```bash
  python3 --version  # Check version
  ```

### Recommended

- **Zo Computer** - AI workspace platform (but N5 OS works anywhere)
- **500 MB disk space** - For core system files

---

## Installation (3 minutes)

### Option A: Interactive Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/vrijenattawar/n5os-core.git
cd n5os-core

# Run interactive onboarding
python3 bootstrap_interactive.py
```

This will:
1. Check prerequisites ✓
2. Gather your info (name, email, timezone)
3. Create directory structure
4. Initialize templates
5. Save configuration

### Option B: Quick Install (Advanced)

```bash
# Clone and run basic bootstrap
git clone https://github.com/vrijenattawar/n5os-core.git
cd n5os-core
bash bootstrap.sh

# Then configure manually
python3 bootstrap_interactive.py --non-interactive \
  --name "Your Name" \
  --email "you@example.com" \
  --timezone "America/New_York"
```

### Option C: Dry Run (Preview only)

```bash
python3 bootstrap_interactive.py --dry-run
```

---

## Verify Installation (2 minutes)

### Test core scripts

```bash
# Git safety check
python3 N5/scripts/n5_git_check.py

# System health
python3 N5/scripts/n5_system_health.py

# Index rebuild (dry-run)
python3 N5/scripts/n5_index_rebuild.py --dry-run
```

### Check directory structure

```bash
ls -la N5/
# Should see: commands/ config/ data/ prefs/ scripts/ schemas/ templates/

ls -la
# Should see: Documents/ Knowledge/ Lists/ N5/ Records/
```

---

## First Steps (3 minutes)

### 1. Read the docs

- **System overview** → file 'Documents/N5.md'
- **First run checklist** → file 'Documents/System/FIRST_RUN_CHECKLIST.md'
- **Architectural principles** → file 'Knowledge/architectural/architectural_principles.md'

### 2. Customize preferences

Edit file 'N5/prefs/prefs.md' to:
- Add your communication style preferences
- Configure integrations (Gmail, Drive, Calendar)
- Set up naming conventions
- Define folder policies

### 3. Try commands

If using Zo Computer, tell Zo:

```
Load Vibe Builder persona
```

```
Show me my N5 system
```

```
Create a new principle for [topic]
```

### 4. Add your first content

```bash
# Add an idea
echo '{"tag":"ideas","title":"Improve onboarding","description":"Make setup even easier","date_added":"2025-10-27"}' >> Lists/ideas.jsonl

# View lists
python3 N5/scripts/lists_cli.py show ideas
```

---

## What's Next?

### Learn the system

- **Planning philosophy** → file 'Knowledge/architectural/planning_prompt.md'
- **Command registry** → file 'N5/config/commands.jsonl'
- **Conversation database** → file 'Documents/System/CONVERSATION_DATABASE_GUIDE.md'

### Customize workflows

- Add custom commands to `N5/commands/`
- Create automation scripts in `N5/scripts/`
- Define your own principles in `Knowledge/architectural/principles/`

### Set up integrations

If using Zo Computer:
1. Connect Gmail, Drive, Calendar in Zo settings
2. Configure detection rules in `Lists/detection_rules.md`
3. Set up scheduled tasks for automation

### Join the community

- **GitHub Discussions** - Ask questions, share workflows
- **Issues** - Report bugs, request features
- **Contributions** - Submit PRs, improve docs

---

## Common Issues

### "Git not found"

```bash
apt update && apt install -y git
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### "Permission denied" errors

Run scripts with `python3` prefix:
```bash
python3 N5/scripts/script_name.py
```

### "Module not found" errors

Install required Python packages:
```bash
pip3 install pytz
```

### Directory structure incorrect

Re-run bootstrap:
```bash
python3 bootstrap_interactive.py
```

---

## Getting Help

### Documentation

- file 'Documents/N5.md' - System architecture
- file 'Documents/System/ONBOARDING_DESIGN.md' - Setup design
- file 'Knowledge/architectural/architectural_principles.md' - Core principles

### GitHub

- **Issues** - https://github.com/vrijenattawar/n5os-core/issues
- **Discussions** - https://github.com/vrijenattawar/n5os-core/discussions

### Community

- Share your setup on GitHub Discussions
- Contribute improvements via Pull Requests

---

## Next Level

Once you're comfortable with the basics:

1. **Build custom commands** - Extend the command registry
2. **Create automation** - Set up scheduled tasks and workflows
3. **Develop personas** - Define AI personas for different contexts
4. **Optimize workflows** - Apply architectural principles to your own systems
5. **Contribute back** - Share your improvements with the community

---

**Version:** 1.0  
**Last Updated:** 2025-10-27  
**License:** MIT

---

**Welcome to N5 OS!** 🚀
