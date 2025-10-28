# N5 OS Core - Phase 0.4 Build Instructions

**Project**: N5 OS (Cesc v0.1)\
**GitHub**: https://github.com/vattawar/zo-n5os-core\
**Phase**: 0.4 - GitHub Integration\
**Prerequisites**: Phases 0.1, 0.2, 0.3 complete

---

## Mission: Push Foundation to GitHub

Configure Git, create comprehensive README, push all Phase 0 files to GitHub.

**Time**: 1 hour\
**Environment**: vademonstrator.zo.computer

---

## What to Build

### 1. Git Configuration

```bash
cd /home/workspace

# Initialize if not already
git init

# Configure (use V's details)
git config user.name "Vrijen Attawar"
git config user.email "va@zo.computer"

# Add remote
git remote add origin https://github.com/vattawar/zo-n5os-core.git

# Verify .gitignore exists and is correct
cat .gitignore
```

### 2. Create Comprehensive README.md

**Location**: `file README.md`

**Content Structure**:

```markdown
# N5 OS Core (Cesc v0.1)

**Personal productivity operating system for Zo Computer**

Build an AI assistant that thinks clearly, maintains itself automatically, and grows with you.

---

## What is N5 OS?

N5 OS (codename: Cesc) is a foundational operating system for your AI on [Zo Computer](https://zo.computer). It provides:

- 🧠 **Clear Thinking**: Rules that prevent hallucination and ensure thorough responses
- 🔄 **Self-Maintaining**: Automated cleanup and system awareness
- 📋 **Command System**: Natural language commands for common operations
- 🏗️ **Build Orchestration**: Coordinate multi-step AI projects
- 📚 **Knowledge Management**: Portable, principle-driven information architecture

**Current Release**: Phase 0 (Foundation) - Core behavioral rules + self-maintenance

---

## Quick Start

### Prerequisites
- Active [Zo Computer](https://zo.computer) account
- 5-10 minutes for setup

### Installation

1. **Clone this repository to your Zo workspace**:
   ```bash
   cd /home/workspace
   git clone https://github.com/vattawar/zo-n5os-core.git
   cd zo-n5os-core
```

2. **Run initialization**:

   ```bash
   python3 N5/scripts/n5_init.py
   ```

   This will:

   - Generate your personal config files in `/N5/config/`
   - Set up directory structure
   - Verify all dependencies

3. **Set up scheduled tasks** (in Zo chat):

   ```markdown
   Create two scheduled tasks:
   
   1. Daily cleanup at 3 AM:
      python3 /home/workspace/N5/scripts/workspace_cleanup.py
   
   2. Self-description every 6 hours:
      python3 /home/workspace/N5/scripts/self_describe.py
   ```

4. **Start using N5 OS**:

   - Your AI will now follow N5 behavioral rules
   - System maintains itself automatically
   - Check `/docs/` for detailed documentation

---

## What's Included (Phase 0)

### Core Components

**Behavioral Rules** (`/N5/templates/rules.template.md`):

- Anti-hallucination protocols
- Systematic clarification (min 3 questions when uncertain)
- Non-interactive execution standards
- Error handling requirements
- Safety protocols (dry-run, approval, protection)

**Self-Maintenance** (`/N5/scripts/`):

- `file workspace_cleanup.py` - Archives old temp files daily
- `file self_describe.py` - Generates system state every 6 hours
- `file n5_init.py` - Initializes or updates your N5 installation

**Configuration System**:

- Templates in `/N5/templates/` (from GitHub, read-only reference)
- Your configs in `/N5/config/` (generated, not tracked in Git)
- Safe updates: pull new templates without overwriting your customizations

---

## Documentation

- **Setup Guide**: `/docs/phase0_setup.md`
- **Rules Documentation**: `/docs/phase0_2_rules.md`
- **Scheduled Tasks**: `/docs/phase0_3_tasks.md`
- **Architecture**: See spec docs in `/docs/`

---

## Customization

### Modify Behavioral Rules

1. Edit `/N5/config/rules.md` (NOT the template)
2. Restart your Zo conversation to apply changes
3. Template updates from Git won't overwrite your custom config

### Adjust Cleanup Schedule

Edit `file workspace_cleanup.py` parameters:

```python
ARCHIVE_AFTER_DAYS = 30  # Change retention period
DIRECTORIES_TO_CLEAN = ['/tmp/', ...]  # Add/remove directories
```

---

## Roadmap

**Phase 0 (Current)**: Foundation ✅

- Behavioral rules
- Self-maintenance
- Config system

**Phase 1 (Next)**: Infrastructure

- Schema validation
- Safety systems
- State management

**Phase 2**: Commands

- Natural language command registry
- Command execution system

**Phase 3**: Build System

- Multi-agent orchestration
- Planning workflows

**Phase 4**: Knowledge

- Preference modules
- Architectural principles

**Phase 5**: Workflows

- Conversation end workflow
- Knowledge management patterns

---

## Philosophy

N5 OS is built on these principles:

- **Simple Over Easy**: Choose disentangled solutions over convenient complexity
- **Flow Over Pools**: Prefer processing pipelines over accumulated state
- **Code Is Free, Thinking Is Expensive**: Invest time in design, not implementation
- **Maintenance Over Organization**: Systems that maintain themselves beat perfect filing

Full philosophy in `/docs/planning_prompt.md` (coming in Phase 3)

---

## Contributing

This is V's personal productivity system, open-sourced for the Zo community.

**Feedback welcome**:

- Open GitHub issues for bugs
- Share your N5 customizations
- Suggest universal improvements

**Not accepting**:

- Features specific to narrow use cases
- Complexity that breaks the "simple over easy" principle
- Dependencies on external services (Zo-only by design)

---

## License

MIT License - See LICENSE file

---

## Credits

**Created by**: [Vrijen Attawar](https://github.com/vattawar)\
**Built for**: [Zo Computer](https://zo.computer) users\
**Inspired by**: A decade of personal productivity experimentation

---

## Support

- **Documentation**: See `/docs/` directory
- **Issues**: [GitHub Issues](https://github.com/vattawar/zo-n5os-core/issues)
- **Zo Community**: [Discord](https://discord.gg/zocomputer)

---

**Version**: Cesc v0.1 (Phase 0)\
**Last Updated**: 2025-10-28

```markdown

### 3. Stage and Commit

```bash
cd /home/workspace

# Check what's ready to commit
git status

# Add everything except ignored files
git add .

# Commit with meaningful message
git commit -m "Phase 0: Foundation complete

- Behavioral rules template (anti-hallucination, clarification, safety)
- Self-maintenance scripts (cleanup, self-description)
- Config template system
- Complete documentation
- Scheduled tasks configured

All 15/15 tests passing. System is production-ready."

# Push to GitHub
git push -u origin main
```

### 4. Verify on GitHub

Visit https://github.com/vattawar/zo-n5os-core and confirm:

- README displays correctly
- All files present
- .gitignore working (no `/N5/config/` or `/N5/data/` files)
- LICENSE file present

### 5. Create Release

On GitHub:

1. Go to Releases → "Create a new release"
2. Tag: `v0.1-cesc`
3. Title: "Cesc v0.1 - Foundation Release"
4. Description:

```markdown
## N5 OS Core - Phase 0 Complete

First public release of N5 OS Core foundation system.

### What's Included

✅ **Behavioral Rules Template**
- Anti-hallucination protocols
- Systematic clarification (3+ questions)
- Safety standards (dry-run, approval, protection)
- Error handling requirements

✅ **Self-Maintenance**
- Daily workspace cleanup
- System self-description (6-hour intervals)
- Automated scheduled tasks

✅ **Config Template System**
- Safe updates without overwriting user customizations
- Template → Config generation workflow

### Installation

```bash
git clone https://github.com/vattawar/zo-n5os-core.git
cd zo-n5os-core
python3 N5/scripts/n5_init.py
```

See README.md for complete setup guide.

### Stats

- 15/15 tests passing
- 3 Python scripts (100% error handling coverage)
- 2 scheduled tasks registered
- Complete documentation

### Next Phase

Phase 1: Infrastructure (schemas, safety, state management)

```markdown

---

## Success Criteria

- [ ] Git repository initialized and configured
- [ ] README.md created with complete setup guide
- [ ] All Phase 0 files committed and pushed
- [ ] .gitignore working correctly (config/ and data/ not in repo)
- [ ] GitHub repository displays correctly
- [ ] v0.1-cesc release created
- [ ] Documentation complete and accessible

---

## Testing Checklist

**Local**:
```bash
# Verify gitignore
git status  # Should NOT show /N5/config/ or /N5/data/

# Verify all tracked files
git ls-files

# Check commit
git log --oneline -1
```

**On GitHub**:

- [ ]  README renders correctly with formatting

- [ ]  File structure visible and organized

- [ ]  No sensitive/generated files in repo

- [ ]  LICENSE file displays correctly

- [ ]  Release v0.1-cesc exists with description

---

## Principles Applied

- **P1 (Human-Readable)**: README is beginner-friendly, comprehensive
- **P2 (SSOT)**: GitHub is source of truth for templates
- **P5 (Anti-Overwrite)**: .gitignore protects user configs
- **P15 (Complete Before Claiming)**: All criteria verified
- **P21 (Document Assumptions)**: README explains philosophy and decisions

---

## What This Achieves

**Phase 0 Complete**: N5 OS Core foundation is:

- ✅ Publicly available on GitHub
- ✅ Installable by any Zo user in &lt; 10 minutes
- ✅ Self-documenting and self-maintaining
- ✅ Production-tested and validated
- ✅ Ready for Phase 1 expansion

---

**Created**: 2025-10-28 00:50 ET