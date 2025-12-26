# N5OS Lite

**A lightweight, portable AI operating system for Zo Computer**

N5OS Lite is a distilled, privacy-safe version of the N5 operating system - a framework for managing AI-assisted workflows with structure, safety, and efficiency.

## What is N5OS?

N5OS is an organizational layer that helps you and your AI assistant:

- **Stay organized** with consistent file structures and naming conventions
- **Work safely** with protection systems for important files
- **Track state** across complex, multi-step workflows
- **Route intelligently** between specialized AI personas for different tasks
- **Build knowledge** with structured ingestion and retrieval

## Quick Start

```bash
# 1. Clone or extract to your workspace
tar -xzf n5os-lite-v2.0.tar.gz -C /home/workspace/

# 2. Run the setup script
cd /home/workspace/n5os-lite
./setup.sh

# 3. Run the onboarding wizard (optional)
python3 scripts/onboarding_wizard.py
```

## Core Components

### 📁 Structure
```
n5os-lite/
├── personas/       # AI persona definitions (Operator, Builder, etc.)
├── principles/     # Operating principles (P01-P37)
├── rules/          # Behavior rules templates
├── scripts/        # Core operational scripts
├── prompts/        # Workflow prompts
├── system/         # System documentation
├── config/         # Configuration files
└── schemas/        # Data schemas
```

### 🤖 Personas
Eight specialized AI modes for different tasks:
- **Operator** - Navigation, execution, state tracking (home base)
- **Builder** - Implementation, coding, automation
- **Strategist** - Planning, analysis, decisions
- **Researcher** - Information gathering, synthesis
- **Writer** - Content creation, communication
- **Teacher** - Explanations, learning
- **Architect** - System design, meta-design
- **Debugger** - Troubleshooting, QA

### 🛡️ Safety Systems
- **n5_protect.py** - Mark directories as protected from deletion
- **n5_safety.py** - Validate operations before execution
- **Dry-run previews** - See what will happen before it does

### 📊 State Management
- **session_state_manager.py** - Track conversation progress
- **Context loader** - Load relevant context per task type

## Key Principles

N5OS is built on 37+ operating principles. The most critical:

- **P15: Complete Before Claiming** - Report "X/Y done (Z%)" not "Done" until truly complete
- **P07: Idempotence** - Operations should be safe to re-run
- **P05: Safety Determinism** - Predictable, safe behavior
- **P16: Accuracy Over Sophistication** - Correct beats clever

## Installation Requirements

- Zo Computer (or compatible AI-assisted environment)
- Python 3.10+
- Basic shell access

## Customization

1. **Personas** - Edit `personas/*.yaml` to adjust AI behavior
2. **Rules** - Customize `rules/essential_rules.yaml` with your preferences
3. **Principles** - Disable/enable principles in `principles/`

## Privacy

This distribution contains **no personal information**. It's a clean framework ready for your own customization.

## License

MIT License - See LICENSE file

## Version

**v2.0** - December 2025
- Full PII sanitization
- Updated principles (37 total)
- Added session state management
- Added context loading system
- Added debug logging
- Refreshed documentation
