# N5 OS Bootstrap Package

**Version:** 1.0.0  
**Export Date:** 2025-10-18  
**Scope:** Core + Meeting System (Generic, no personal data)

---

## What is N5?

N5 is a personal operating system designed to run on Zo Computer. It provides:

- **Knowledge Management:** Capture, organize, and retrieve information
- **Meeting Intelligence:** Process meeting transcripts into actionable insights
- **List Management:** Track tasks, opportunities, and follow-ups
- **Command System:** 90+ slash commands for productivity
- **Session Management:** Context-aware conversation state
- **Safety & Quality:** Built-in safeguards and validation

---

## Package Contents

```
N5_Bootstrap_Package/
├── README.md                  # This file
├── INSTALLATION.md            # Detailed installation guide
├── bootstrap.py               # Automated installer
├── scripts/                   # 72 core Python scripts
├── config/                    # System configuration files
├── schemas/                   # JSON/SQL schemas
├── prefs/                     # Preferences and protocols
├── commands/                  # 92 slash commands
├── knowledge/                 # Architectural documentation
└── docs/                      # Additional documentation
```

**Total Files:** 215 files (~8MB compressed)

---

## Quick Start

### Option 1: Automated Installation (Recommended)

```bash
# 1. Upload this entire package to your Zo workspace
# 2. Run the bootstrap script
python3 /home/workspace/N5_Bootstrap_Package/bootstrap.py
```

### Option 2: Manual Installation

See `file 'INSTALLATION.md'` for step-by-step instructions.

---

## System Architecture

### Core Components

1. **Scripts Layer** (`N5/scripts/`)
   - Infrastructure scripts (`n5_*.py`)
   - Meeting system (`meeting_*.py`)
   - Session management (`session_state_manager.py`)

2. **Configuration Layer** (`N5/config/`)
   - Commands registry (`commands.jsonl`)
   - Tag taxonomy and mappings
   - System settings

3. **Schema Layer** (`N5/schemas/`)
   - Data structures for all components
   - Database schemas for CRM/meetings
   - Validation schemas

4. **Preferences Layer** (`N5/prefs/`)
   - Operational protocols
   - Communication templates
   - System governance rules

5. **Command Layer** (`N5/commands/`)
   - User-facing slash commands
   - Workflow orchestration
   - Quick access to functionality

6. **Knowledge Layer** (`Knowledge/`)
   - Architectural principles
   - Operational guidelines
   - System documentation

---

## Key Features

### 🧠 Knowledge Management
- Direct ingestion from conversations
- Semantic search and retrieval
- Conflict resolution
- Adaptive suggestions

### 📅 Meeting Intelligence
- Automatic transcript processing
- Stakeholder intelligence extraction
- Follow-up generation
- Meeting preparation digests

### ✅ List Management
- Multi-list support (tasks, opportunities, etc.)
- List items with rich metadata
- Cross-list relationships
- Health monitoring

### 🎯 Session Management
- Conversation context tracking
- State persistence across chats
- Focus and objective management

### 🛡️ Safety & Quality
- Dry-run mode for destructive operations
- File protection system
- Input validation
- Git governance

---

## What's Included

### Scripts (72 total)
- **Knowledge:** Add, find, ingest, conflict resolution
- **Lists:** Create, add, move, export, health checks
- **Meetings:** Process, monitor, generate intelligence
- **Commands:** Manage slash commands
- **Safety:** File protection, validation
- **Utilities:** Git audit, emoji sync, digest runs

### Commands (92 total)
- **Knowledge:** `/knowledge-add`, `/knowledge-find`, `/knowledge-ingest`
- **Lists:** `/lists-add`, `/lists-create`, `/list-view`
- **Meetings:** `/meeting-process`, `/meeting-approve`, `/auto-process-meetings`
- **Workflow:** `/conversation-end`, `/docgen`, `/deliverable-generate`
- **Utilities:** `/git-audit`, `/index-rebuild`, `/file-protector`

### Configurations
- Command registry with 90+ registered commands
- Tag taxonomy and mapping system
- Emoji legend for visual indicators
- Schema validation rules

### Schemas
- Knowledge, lists, meetings, CRM structures
- Validation rules for all data types
- Database schemas (SQLite)

---

## What's NOT Included

This is a **clean shell** with no personal or business-specific data:

- ❌ Personal knowledge base content
- ❌ Meeting records and transcripts
- ❌ List items and tasks
- ❌ CRM/stakeholder data
- ❌ Credentials or API keys
- ❌ Business-specific scripts or commands
- ❌ Scheduled tasks
- ❌ Careerspan-specific functionality

---

## Installation Requirements

### System Requirements
- Zo Computer workspace
- Python 3.12+
- 50MB storage space
- Internet connection (for dependencies)

### Dependencies (auto-installed)
```
anthropic
openai
google-auth
google-api-python-client
python-dotenv
pydantic
fuzzywuzzy
python-Levenshtein
```

---

## Post-Installation

### 1. Initialize Your System
```bash
# In Zo chat
/init-state-session
```

### 2. Add Your First Knowledge
```bash
/knowledge-add
```

### 3. Explore Commands
```bash
# Type / in Zo chat to see all available commands
```

### 4. Read the Docs
- Start with: `file 'Documents/N5.md'`
- Principles: `file 'Knowledge/architectural/architectural_principles.md'`
- Preferences: `file 'N5/prefs/prefs.md'`

---

## Architecture Philosophy

N5 follows these core principles:

1. **Modularity (P20):** Separate concerns, clear interfaces
2. **Single Source of Truth (P2):** One authoritative location per data type
3. **Human-Readable (P1):** Prefer JSON/markdown over binary
4. **Safety-First (P5, P7, P19):** Dry-run, backups, error handling
5. **Context Efficiency (P0, P8):** Minimal context, Rule-of-Two
6. **Complete Before Claiming (P15):** Verify state before reporting success

See `file 'Knowledge/architectural/architectural_principles.md'` for full details.

---

## Directory Structure

After installation:

```
/home/workspace/
├── N5/                         # Operating system layer
│   ├── commands/               # Slash commands (92 files)
│   ├── config/                 # System configuration
│   ├── schemas/                # Data structure definitions
│   ├── scripts/                # Python automation (72 files)
│   ├── prefs/                  # Preferences & protocols
│   ├── records/                # Runtime data (empty)
│   │   └── meetings/           # Meeting records
│   └── intelligence/           # Processed insights (empty)
│
├── Knowledge/                  # Knowledge base (empty)
│   └── architectural/          # System documentation
│
├── Lists/                      # Action items (empty)
│
├── Documents/                  # User documents
│   └── N5.md                   # System overview
│
└── Records/                    # Staging area (empty)
```

---

## Customization

### Adding Your Own Commands
```python
python3 /home/workspace/N5/scripts/n5_commands_manage.py add \
  --name "my-command" \
  --script "/path/to/script.py" \
  --description "What it does"
```

### Configuring Preferences
Edit files in `N5/prefs/` to customize:
- Operational protocols
- Communication templates
- Safety rules
- Naming conventions

### Extending Schemas
Add new schemas to `N5/schemas/` following existing patterns.

---

## Troubleshooting

### Bootstrap Fails
- Check Python version: `python3 --version` (need 3.12+)
- Check permissions: Ensure you can write to `/home/workspace`
- Check logs: Look for error messages in bootstrap output

### Commands Don't Work
- Rebuild commands registry: `/index-rebuild`
- Check script paths in `N5/config/commands.jsonl`
- Ensure scripts are executable: `chmod +x N5/scripts/*.py`

### Dependencies Missing
```bash
pip install anthropic openai google-auth google-api-python-client \
  python-dotenv pydantic fuzzywuzzy python-Levenshtein
```

---

## Support & Community

- **Report Issues:** Use "Report an issue" button in Zo sidebar
- **Join Discord:** https://discord.gg/zocomputer
- **Documentation:** All docs included in `Knowledge/` and `N5/prefs/`

---

## Version History

### v1.0.0 (2025-10-18)
- Initial bootstrap package
- 72 core scripts
- 92 slash commands
- Complete meeting system
- Knowledge management system
- List management system
- Session management
- Safety and validation tools

---

## License & Attribution

This package is a derivative work based on a production N5 system.
All personal and business-specific information has been removed.

The core architecture and principles are generic and reusable.

---

## Next Steps

1. **Install:** Run `bootstrap.py` or follow `INSTALLATION.md`
2. **Initialize:** Use `/init-state-session` in Zo
3. **Learn:** Read `Documents/N5.md` and architectural principles
4. **Customize:** Adapt preferences and add your own commands
5. **Build:** Start capturing knowledge and processing meetings

---

**Welcome to N5!** 🚀

*A personal operating system for your digital life*
