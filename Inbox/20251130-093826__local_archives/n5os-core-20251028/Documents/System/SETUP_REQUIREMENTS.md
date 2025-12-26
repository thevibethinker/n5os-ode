# N5 OS Core — Setup Requirements

**What Eric's Zo needs before installation**

---

## Prerequisites

### 1. Git (REQUIRED)
**Check if installed**:
```bash
git --version
```

**If not installed**:
```bash
apt update && apt install -y git
```

**Configure Git** (first time only):
```bash
git config --global user.name "Eric [Last Name]"
git config --global user.email "eric@example.com"
```

### 2. Python 3 (REQUIRED)
**Check if installed**:
```bash
python3 --version
```

**Should be**: Python 3.8+ (Zo typically has 3.12)

### 3. Basic Unix Tools (Usually Pre-installed)
- `bash` — For running bootstrap.sh
- `mkdir`, `cp`, `chmod` — File operations

---

## What bootstrap.sh Does

The installer:
1. ✅ Creates N5 directory structure
2. ✅ Copies all core files
3. ✅ Initializes git repo in `/home/workspace` (if needed)
4. ✅ Sets up empty Lists/ directory
5. ❌ **Does NOT**: Install scheduled tasks (manual, see below)
6. ❌ **Does NOT**: Set up integrations (optional, see below)

---

## After Installation

### Initialize Your First List
```bash
cp Lists/ideas.jsonl.template Lists/ideas.jsonl
```

### Run Your First Command
```bash
python3 N5/scripts/n5_index_rebuild.py --dry-run
```

---

## Optional: Integrations

N5 Core works standalone. These integrations are optional:

**Gmail** — Email scanning
- Requires: Google service account
- Setup: Follow Zo integration guide

**Google Calendar** — Meeting detection  
- Requires: Zo Calendar integration
- Setup: Zo settings → Integrations

**Google Drive** — File sync
- Requires: Zo Drive integration
- Setup: Zo settings → Integrations

**Notion** — Knowledge base sync
- Requires: Zo Notion integration
- Setup: Zo settings → Integrations

---

## Next Steps

1. Read: `QUICKSTART.md`
2. Explore: `docs/zero_touch_manifesto.md`
3. Review: `core/prefs/prefs.md`
4. Test: Run a script in dry-run mode

---

**Version**: 1.0-core  
**Date**: 2025-10-26
