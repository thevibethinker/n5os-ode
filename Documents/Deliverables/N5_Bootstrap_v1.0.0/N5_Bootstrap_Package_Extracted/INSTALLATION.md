# N5 OS Installation Guide

**Version:** 1.0.0  
**Target Environment:** Zo Computer workspace  
**Installation Time:** ~10 minutes

---

## Prerequisites

- Fresh Zo Computer workspace (or willingness to merge with existing files)
- Python 3.12+ (pre-installed on Zo)
- Internet connection (for dependency installation)
- ~50MB free storage space

---

## Installation Methods

### Method 1: Automated Installation (Recommended)

```bash
# 1. Navigate to the bootstrap package
cd /path/to/N5_Bootstrap_Package

# 2. Run the bootstrap script
python3 bootstrap.py

# 3. Follow the prompts
```

The bootstrap script will:
- ✅ Verify your environment
- ✅ Create the N5 directory structure
- ✅ Copy all files to /home/workspace/N5
- ✅ Install Python dependencies
- ✅ Initialize empty data directories
- ✅ Create starter configuration

### Method 2: Manual Installation

If you prefer manual control:

```bash
# 1. Create N5 directory
mkdir -p /home/workspace/N5

# 2. Copy components
cp -r scripts /home/workspace/N5/
cp -r config /home/workspace/N5/
cp -r schemas /home/workspace/N5/
cp -r prefs /home/workspace/N5/
cp -r commands /home/workspace/N5/

# 3. Create Knowledge directory
mkdir -p /home/workspace/Knowledge
cp -r knowledge/architectural /home/workspace/Knowledge/

# 4. Create data directories
mkdir -p /home/workspace/N5/{lists,records/meetings,intelligence,config/credentials}

# 5. Install dependencies (see below)
```

---

## Post-Installation Setup

### 1. Install Python Dependencies

```bash
# Core dependencies
pip install -U anthropic openai aiohttp beautifulsoup4 pyyaml jsonschema

# Optional: For meeting system
pip install -U watchdog

# Optional: For Git operations
pip install -U gitpython
```

### 2. Initialize Your First Session

```bash
# Initialize session state for a new conversation
python3 /home/workspace/N5/scripts/session_state_manager.py init --type setup

# This creates SESSION_STATE.md in your current conversation workspace
```

### 3. Configure System Preferences

Edit the following files to match your preferences:

- `file 'N5/prefs/prefs.md'` - Core system preferences
- `file 'N5/prefs/communication/email-voice.md'` - Communication style
- `file 'N5/config/meeting_monitor_config.json'` - Meeting system settings

### 4. Set Up Documents/N5.md

Create the main system index:

```bash
# Create file
touch /home/workspace/Documents/N5.md

# Add this content:
```

```markdown
# N5 Operating System

**Version:** 1.0.0  
**Initialized:** [YOUR_DATE]

## Quick Reference

- Commands: `file 'N5/commands/README.md'`
- Scripts: `file 'N5/scripts/'`
- Schemas: `file 'N5/schemas/'`
- Preferences: `file 'N5/prefs/prefs.md'`

## System Architecture

See `file 'Knowledge/architectural/architectural_principles.md'` for core principles.

## Getting Started

1. **Initialize sessions:** Use `python3 N5/scripts/session_state_manager.py init --type [type]`
2. **Browse commands:** Look through `N5/commands/` for slash commands
3. **Configure preferences:** Edit files in `N5/prefs/`
4. **Start using:** Begin with `/knowledge-add` to add your first knowledge

## Core Components

### Lists System
- **Purpose:** Track items across categories (ideas, todos, opportunities, etc.)
- **Location:** `N5/lists/`
- **Commands:** `/lists-add`, `/lists-find`, `/lists-move`

### Meeting System
- **Purpose:** Process and extract intelligence from meetings
- **Location:** `N5/records/meetings/`
- **Commands:** `/meeting-process`, `/meeting-approve`

### Knowledge Base
- **Purpose:** Store and retrieve your personal knowledge
- **Location:** `Knowledge/`
- **Commands:** `/knowledge-add`, `/knowledge-find`

### Intelligence Layer
- **Purpose:** Learn and adapt to your patterns
- **Location:** `N5/intelligence/`
- **Auto-updated:** By various systems

## Customization

This is YOUR system. Feel free to:
- Add new commands in `N5/commands/`
- Create custom scripts in `N5/scripts/`
- Extend schemas in `N5/schemas/`
- Build on architectural principles

## Support

- **Documentation:** `N5/prefs/` and `Knowledge/architectural/`
- **Zo Discord:** https://discord.gg/zocomputer
- **Report Issues:** Use the "Report an issue" button in Zo
```

---

## Verification

Run these commands to verify your installation:

```bash
# Check core scripts
ls /home/workspace/N5/scripts/n5_*.py | wc -l
# Should show: 62

# Check meeting scripts
ls /home/workspace/N5/scripts/meeting_*.py | wc -l  
# Should show: 9

# Check schemas
ls /home/workspace/N5/schemas/*.json | wc -l
# Should show: 14

# Test a script
python3 /home/workspace/N5/scripts/n5_safety.py
# Should run without errors
```

---

## What to Do Next

### Option 1: Start Using Core Features

```bash
# Add your first knowledge
# In Zo chat: /knowledge-add

# Create your first list
# In Zo chat: /lists-create
```

### Option 2: Set Up Meeting Processing

1. Configure meeting monitor: Edit `file 'N5/config/meeting_monitor_config.json'`
2. Process your first meeting: Use `/meeting-process`
3. Review meeting output: Use `/meeting-approve`

### Option 3: Customize the System

1. Read architectural principles: `file 'Knowledge/architectural/architectural_principles.md'`
2. Review existing commands for patterns: `ls N5/commands/`
3. Create your first custom command
4. Extend the system to your needs

---

## Troubleshooting

### "Module not found" errors
```bash
pip install -U [missing_module]
```

### "Permission denied" errors
```bash
# Zo runs as root, but if you encounter issues:
chmod +x /home/workspace/N5/scripts/*.py
```

### Scripts reference missing files
- Normal on first run - many scripts expect data that doesn't exist yet
- Build up data by using the system
- Check schema files for expected data structures

### Need to reset
```bash
# Remove all data (keeps system files)
rm -rf /home/workspace/N5/{lists,records,intelligence}/*

# Keep backups if needed
```

---

## File Structure Reference

```
/home/workspace/
├── N5/                          # OS layer
│   ├── commands/                # Slash commands
│   ├── config/                  # System configuration
│   ├── intelligence/            # Learned patterns (empty on install)
│   ├── lists/                   # List system data (empty on install)
│   ├── prefs/                   # Preferences and docs
│   ├── records/                 # Meeting records (empty on install)
│   ├── schemas/                 # Data schemas
│   └── scripts/                 # Python scripts
├── Documents/
│   └── N5.md                    # Main system index (create manually)
└── Knowledge/                   # Knowledge base
    └── architectural/           # System architecture docs
```

---

## Getting Help

1. **Read the docs:** Start with `file 'Knowledge/architectural/architectural_principles.md'`
2. **Check commands:** Look through `N5/commands/` for examples
3. **Ask in Zo chat:** Your AI assistant knows this system
4. **Zo Discord:** Join the community at https://discord.gg/zocomputer

---

**Ready to begin!** 🚀

Start with: `/init-state-session` or `/knowledge-add`
