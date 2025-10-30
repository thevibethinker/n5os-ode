# N5 OS Core

> Personal AI Operating System for Zo Computer

## Overview

N5 OS Core (Codename: Cesc v0.1) is a distributable AI operating system that provides session management, safety systems, modular preferences, and workflow automation for Zo Computer instances.

## Quick Start

```bash
# Initialize N5 on your Zo instance
python3 /home/workspace/N5/scripts/n5_install.py

# Start a new session
python3 /home/workspace/N5/scripts/session_state_manager.py init --type discussion
```

## Core Components

- **Session Management** - Context-aware conversation state tracking
- **Safety Systems** - Protected paths, validation, security rules
- **Bulletin System** - System-wide announcements and updates
- **Command Registry** - Custom slash commands and shortcuts
- **Modular Preferences** - User-specific behavioral configurations

## Directory Structure

```
N5/
├── config/          # Active runtime configurations
├── prefs/           # User preference modules
├── scripts/         # Python automation tools
├── schemas/         # JSON validation schemas
├── bulletins/       # System announcements
├── docs/            # Documentation
├── Lists/           # Curated tracking collections
├── Records/         # Append-only audit logs
└── Recipes/         # Reusable workflows
```

## Documentation

- [User Guide](docs/user_guide.md) - Complete usage documentation
- [Developer Guide](docs/developer_guide.md) - Contributing and extending
- [Architecture](docs/architecture.md) - System design principles

## Requirements

- Zo Computer instance
- Python 3.12+
- Git (for version tracking)

## Installation

See [Installation Guide](docs/installation.md) for detailed setup instructions.

## License

MIT License - See LICENSE file for details

## Support

- GitHub Issues: https://github.com/vrijenattawar/zo-n5os-core/issues
- Email: vademonstrator@zo.computer

---

**Version**: 0.1.0 (Cesc)  
**Status**: Beta - Active Development
