# N5 OS Core

**Version:** 0.1 (Cesc)  
**Status:** Alpha - Core distribution package  
**License:** MIT

## What Is N5?

N5 is a **flow-based cognitive operating system** for AI-human collaboration on Zo Computer. It transforms how you work with AI by creating self-maintaining systems that minimize manual organization and maximize productive flow.

**Core Philosophy:** Information either flows or it pools. When it pools, it rots.

## Key Features

- **Zero-Touch Operations** - AI automates routine tasks, you review exceptions (<15% touch rate)
- **Flow-Based Architecture** - Every piece of information has an entry point, processing stages, and defined exit conditions
- **Self-Maintaining Systems** - Automated detection, routing, and alerting for failures
- **Command System** - Natural language commands trigger complex workflows
- **Session State Management** - Context-aware conversations with persistent memory
- **Modular Design** - Clean separation between core system and personal content

## Quick Start

See `QUICK_START.md` for installation instructions.

## Core Components

### Commands (`N5/commands/`)
Markdown-defined commands that compile to executable triggers. Natural language interface to system operations.

### Scripts (`N5/scripts/`)
Python automation scripts following safety-first patterns (dry-run, logging, error handling, state verification).

### Lists (`Lists/`)
Action tracking system with automatic timestamping and state management.

### Knowledge (`Knowledge/`)
Single Source of Truth (SSOT) for system documentation, architectural principles, and reusable knowledge.

### Records (`Records/`)
Staging area for processing information flows: Company/, Personal/, Temporary/ subdirectories.

## Architecture Principles

N5 follows these core design values (in priority order):

1. **Simple Over Easy** - Disentangled systems over convenient complexity
2. **Flow Over Pools** - Time-bounded processing stages, not static storage
3. **Maintenance Over Organization** - Self-maintaining systems beat manual filing
4. **Code Is Free, Thinking Is Expensive** - 70% planning, 20% review, 10% execution
5. **Nemawashi** - Explore 2-3 alternatives before deciding

See `DEVELOPER_QUICKSTART.md` for detailed architecture documentation.

## Documentation

- `user_guide_template.md` - Complete user guide for installation, features, and workflows
- `developer_guide_template.md` - Architecture, contribution guidelines, and extension points
- `generalization_guide.md` - How to separate your personal content from core system
- `content_library_design.md` - Content management system schema and design

## Installation

```bash
curl -O https://[distribution-url]/n5_install_script.py
python3 n5_install_script.py --target /home/workspace
```

See user guide for detailed installation instructions.

## Community & Support

- Issues: [GitHub Issues](https://github.com/[org]/n5-os-core/issues)
- Discussions: [GitHub Discussions](https://github.com/[org]/n5-os-core/discussions)
- Documentation: [Full docs](https://[docs-url])

## Contributing

See `developer_guide_template.md` for contribution guidelines and architecture overview.

## License

MIT License - See LICENSE file for details.

---

**Built for Zo Computer** - Personal AI cloud computing platform
