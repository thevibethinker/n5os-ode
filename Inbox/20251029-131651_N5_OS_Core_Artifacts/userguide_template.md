# N5 User Guide

**Version:** 0.1\
**Last Updated:** 2025-10-28

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Core Concepts](#core-concepts)
5. [Daily Workflows](#daily-workflows)
6. [Commands Reference](#commands-reference)
7. [Troubleshooting](#troubleshooting)

---

## Introduction

### What Is N5?

N5 is a cognitive operating system for AI-human collaboration. It automates routine information processing so you can focus on high-value decisions and creative work.

**Core Philosophy:** Zero-Touch Operations

- AI handles routing, categorization, and processing
- You review exceptions and make strategic decisions
- Systems maintain themselves and alert you to failures
- Target: &lt;15% manual touch rate

### Who Is This For?

- **Knowledge workers** managing high information volume
- **Entrepreneurs** needing systematic follow-up and relationship management
- **Anyone** who wants AI to handle routine tasks while maintaining control

---

## Installation

### Prerequisites

- Zo Computer account (sign up at zo.computer)
- Basic familiarity with file systems and command line (helpful but not required)

### Installation Steps

1. **Download the installer:**

   ```bash
   curl -O https://[distribution-url]/n5_install_script.py
   ```

2. **Run installation:**

   ```bash
   python3 n5_install_script.py --target /home/workspace
   ```

3. **Verify installation:**

   ```bash
   python3 /home/workspace/N5/scripts/session_state_manager.py --version
   ```

4. **Initialize your first session:**\
   In Zo chat, the system will auto-initialize when you start a conversation.

### Post-Installation

The installer creates this structure:

```markdown
/home/workspace/
├── Documents/          # Long-form documentation
├── Knowledge/          # Architectural principles, system knowledge
├── Lists/             # Action tracking (inbox, someday, waiting)
├── Records/           # Processing staging area
│   ├── Company/       # Business-related
│   ├── Personal/      # Personal information
│   └── Temporary/     # Short-term processing
└── N5/               # Core operating system
    ├── commands/      # Command definitions
    ├── config/        # System configuration
    ├── data/          # Databases and state
    ├── prefs/         # User preferences
    ├── schemas/       # JSON schemas
    └── scripts/       # Automation scripts
```

---

## Getting Started

### Your First Session

When you start a new conversation with Zo, N5 automatically:

1. Initializes session state
2. Detects conversation type (build/research/discussion/planning)
3. Loads relevant system context
4. Tracks objectives and progress

You'll see:

```markdown
This is conversation con_XYZ123
```

### Basic Commands

N5 provides natural language commands. Try these:

**Add to inbox:**

```markdown
/add Follow up with John about Q4 roadmap
```

**Check what's waiting:**

```markdown
/waiting
```

**Mark something done:**

```markdown
/done Follow up with John
```

**Search knowledge:**

```markdown
/search architectural principles
```

### Understanding Flow

Every piece of information in N5 follows a flow:

1. **Entry** - Information arrives (email, meeting, idea)
2. **Triage** - Categorize and route (automated when possible)
3. **Processing** - Work through stages with time limits
4. **Exit** - Archive, delete, or convert to permanent knowledge

**Key insight:** Nothing should stay in limbo. Everything has a next action or expiration date.

---

## Core Concepts

### 1. Session State

Each conversation tracks:

- **Focus** - Current primary objective
- **Context** - Relevant files, past conversations, system state
- **Objectives** - What you're trying to accomplish
- **Progress** - Completion status and next steps

Session state is stored in `file SESSION_STATE.md` in each conversation workspace.

### 2. Commands

Commands are markdown files in `N5/commands/` that compile to triggers. They:

- Use natural language syntax
- Support parameters and variants
- Execute complex workflows
- Maintain audit trails

### 3. Lists

Three primary lists manage actions:

- **Inbox** (`file Lists/inbox.md`) - New items requiring triage
- **Someday** (`file Lists/someday.md`) - Deferred but not forgotten
- **Waiting** (`file Lists/waiting.md`) - Blocked on external dependencies

Each entry auto-timestamps creation and completion.

### 4. Records

Temporary staging area for active processing:

- **Company/** - Business stakeholder intelligence, meeting notes, follow-ups
- **Personal/** - Personal projects, learning, health tracking
- **Temporary/** - Short-lived processing artifacts (14-day auto-archive)

Records flow through stages and eventually archive or delete.

### 5. Knowledge

Permanent, reusable information:

- **Architectural principles** - System design rules
- **Workflows** - Documented processes
- **Templates** - Reusable formats
- **Lessons** - Captured insights from experience

Knowledge is your Single Source of Truth (SSOT).

---

## Daily Workflows

### Morning Routine

1. **Review inbox:**

   ```markdown
   /inbox
   ```

2. **Check waiting items:**

   ```markdown
   /waiting
   ```

3. **Process overnight captures:**\
   Zo will alert you to items needing triage

### Processing Email

When Zo emails you a digest or alert:

1. Reply directly to the email with instructions
2. Or click through to conversation and work there
3. Zo routes your response and updates state

### Adding Tasks/Ideas

Use natural language:

```markdown
/add Review Q4 budget with finance team
/add someday Learn about knowledge graphs
/add waiting Response from vendor on pricing
```

### Completing Items

```markdown
/done Review Q4 budget
```

Or let Zo mark items complete automatically when objectives are met.

### Session Management

At conversation end, Zo will:

1. Review what was accomplished
2. Classify the conversation
3. Propose any follow-up actions
4. Update relevant lists and records

---

## Commands Reference

### List Management

- `/add <item>` - Add to inbox
- `/add someday <item>` - Add to someday list
- `/add waiting <item>` - Add to waiting list
- `/done <item>` - Mark complete
- `/inbox` - Show inbox
- `/someday` - Show someday list
- `/waiting` - Show waiting list

### Knowledge Management

- `/search <query>` - Search knowledge base
- `/kb <topic>` - Browse knowledge by topic
- `/learn <topic>` - Start learning session

### System Operations

- `/rebuild` - Rebuild system indices
- `/status` - System health check
- `/backup` - Create system backup
- `/restore <timestamp>` - Restore from backup

### Custom Commands

You can create custom commands by adding markdown files to `N5/commands/`. See developer guide for details.

---

## Troubleshooting

### Common Issues

**Problem:** Session state not initializing

- **Solution:** Check that `file session_state_manager.py` is executable and database exists at `N5/data/conversations.db`

**Problem:** Commands not recognized

- **Solution:** Run `/rebuild` to recompile command registry

**Problem:** Lists not updating

- **Solution:** Verify list files exist in `Lists/` directory and are writable

**Problem:** High memory usage

- **Solution:** Archive old records with `/archive --older-than 30d`

### Getting Help

1. **In-system:** Ask Zo "How do I \[task\]?"
2. **Documentation:** Check `file Documents/N5.md` for system overview
3. **Community:** [GitHub Discussions](https://github.com/%5Borg%5D/n5-os-core/discussions)
4. **Issues:** [GitHub Issues](https://github.com/%5Borg%5D/n5-os-core/issues)

### Advanced Configuration

Edit `file N5/prefs/prefs.md` to customize:

- Touch rate thresholds
- Auto-archive timeouts
- Confidence thresholds for automation
- Default conversation types
- Custom workflows

---

## Next Steps

1. **Customize preferences** - Edit `file N5/prefs/prefs.md`
2. **Create custom commands** - See developer guide
3. **Set up scheduled tasks** - Configure automated agents
4. **Integrate external tools** - Connect calendars, email, CRM

---

## Appendix: Keyboard Shortcuts

*Note: Available when using Zo Computer desktop application*

- `Cmd/Ctrl + K` - Command palette
- `Cmd/Ctrl + P` - File search
- `Cmd/Ctrl + Shift + P` - Session state viewer
- `Cmd/Ctrl + /` - Command reference

---

**Questions or feedback?** Open a discussion at [GitHub](https://github.com/%5Borg%5D/n5-os-core/discussions)