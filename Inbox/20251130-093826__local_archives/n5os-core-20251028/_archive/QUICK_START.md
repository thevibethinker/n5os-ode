# N5 OS Core — Quick Start

**Get productive with N5 OS in 15 minutes**

---

## For End Users

### Installation (5 min)

```bash
git clone https://github.com/vrijenattawar/n5os-core.git
cd n5os-core
bash bootstrap.sh
```

### First Steps (10 min)

1. **Read the philosophy**:
   ```bash
   cat docs/zero_touch_manifesto.md | less
   ```

2. **Configure Zo rules** (CRITICAL):
   ```bash
   cat Documents/System/ZO_SETTINGS_REQUIRED.md
   ```
   
   Go to Zo Settings → Rules → Add the 10 essential rules

3. **System overview**:
   ```bash
   cat Documents/N5.md
   ```

4. **Explore commands** (32 available):
   ```bash
   ls N5/commands/
   python3 N5/scripts/n5_search_commands.py "list"
   ```

5. **Try your first command**:
   ```bash
   # Add an idea to your lists
   python3 N5/scripts/n5_lists_add.py --tag ideas --data '{"idea": "Test N5 OS", "priority": "high"}'
   
   # View it
   python3 N5/scripts/n5_lists_find.py --tag ideas
   ```

### Daily Workflow

**Morning**:
```bash
# Check system health
python3 N5/scripts/n5_git_check.py
python3 N5/scripts/n5_lists_health_check.py
```

**During work**:
- Use conversation-end at end of each Zo conversation
- Add to lists as ideas emerge
- Ingest important knowledge

**End of day**:
```bash
# Review your lists
python3 N5/scripts/n5_lists_find.py --tag must-contact
python3 N5/scripts/n5_lists_find.py --tag ideas
```

---

## For Developers

**Want to build custom commands and workflows?**

→ Read `DEVELOPER_QUICKSTART.md` (15 min guided tutorial)

**Quick links**:
- Create commands: `N5/commands/command-author.md`
- Auto-generate docs: `N5/commands/docgen.md`
- System design: `N5/commands/system-design-workflow.md`

---

## Next Steps

### Complete Setup (30 min)

Follow the complete checklist:
```bash
cat Documents/System/FIRST_RUN_CHECKLIST.md
```

### Set Up Automation (15 min)

Add scheduled tasks (optional but recommended):
```bash
cat SCHEDULED_TASKS.md
```

### Learn the Architecture (20 min)

Understand the system:
```bash
cat Documents/System/ARCHITECTURE.md
cat Knowledge/architectural/architectural_principles.md
```

---

## Getting Help

### Documentation

All docs in `Documents/System/`:
- `ZO_SETTINGS_REQUIRED.md` — Essential Zo rules
- `FIRST_RUN_CHECKLIST.md` — Complete setup
- `ONBOARDING_DESIGN.md` — Future interactive setup
- `CONSULTANT_GUIDE.md` — Remote troubleshooting
- `SESSION_STATE_GUIDE.md` — Context management
- `CONVERSATION_DATABASE_GUIDE.md` — Query history

### Troubleshooting

```bash
# Check system status
python3 N5/scripts/n5_safety.py

# Rebuild index if commands aren't found
python3 N5/scripts/n5_index_rebuild.py

# Check git status
python3 N5/scripts/n5_git_check.py
```

### Community

- GitHub Issues: Report bugs
- Discussions: Ask questions
- Roadmap: See `ROADMAP.md`

---

**Time to productivity**: 15 minutes (basic), 1 hour (complete)  
**Version**: 1.0-core  
**Date**: 2025-10-27
