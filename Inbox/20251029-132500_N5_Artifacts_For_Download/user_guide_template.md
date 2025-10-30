# N5 OS Core - User Guide

## Introduction

N5 OS Core transforms your Zo Computer into an intelligent operating system with persistent memory, safety guardrails, and workflow automation.

## Getting Started

### Installation

1. **Clone or copy N5 to your workspace**:
   ```bash
   # Zo will handle this during distribution
   ```

2. **Run installation script**:
   ```bash
   python3 N5/scripts/n5_install.py
   ```

3. **Initialize your first session**:
   ```bash
   python3 N5/scripts/session_state_manager.py init --type discussion
   ```

### First Conversation

After installation, N5 automatically initializes for each new conversation:

```
You: "Help me plan a project"
Zo: [Initializes session, loads preferences, presents conversation ID]
```

## Core Features

### Session Management

N5 tracks conversation context across your interactions:

- **Session State**: Focus, objectives, tags, notes
- **Auto-detection**: Conversation type based on your language
- **Persistence**: State maintained throughout conversation

**Session Types**:
- `build` - Development and implementation
- `research` - Investigation and analysis  
- `discussion` - Exploration and brainstorming
- `planning` - Strategy and organization

### Safety Systems

Protected paths prevent accidental deletion:

```bash
# Check if path is protected
python3 N5/scripts/n5_protect.py check /home/workspace/N5

# Protect a new directory
python3 N5/scripts/n5_protect.py protect /home/workspace/important-project --reason "Active client work"
```

### Bulletin System

System-wide announcements for important updates:

```bash
# View active bulletins
python3 N5/scripts/bulletins.py list

# Create new bulletin
python3 N5/scripts/bulletins.py create --title "System Update" --message "New feature available"
```

### Command Registry

Custom slash commands for common operations:

```bash
# List registered commands
python3 N5/scripts/commands.py list

# Register new command
python3 N5/scripts/commands.py register --label "audit" --command "python3 N5/scripts/n5_audit.py"
```

## Working with N5

### Daily Workflow

1. **Morning**: Check bulletins for updates
2. **Work**: N5 auto-initializes sessions
3. **Evening**: Review session summaries in Records/

### Customization

Edit preference modules in `N5/prefs/`:

- `operations/` - Operational protocols
- `workflows/` - Process definitions  
- `prefs.md` - Master preferences file

### Content Management

**Lists** - Track items requiring attention:
- `Lists/todos.md` - Action items
- `Lists/reading_list.md` - Content to consume

**Records** - Immutable history:
- `Records/decisions.jsonl` - Architecture choices
- `Records/sessions.jsonl` - Session summaries

**Recipes** - Reusable workflows (slash-invokable):
- `Recipes/quick_audit.md` - System health check
- `Recipes/backup.md` - Backup procedure

## Troubleshooting

### Session Not Initializing

Check system state:
```bash
python3 N5/scripts/n5_audit.py
```

### Command Not Found

Verify registration:
```bash
python3 N5/scripts/commands.py list
```

### Path Protection Issues

List protected paths:
```bash
python3 N5/scripts/n5_protect.py list
```

## Advanced Usage

### Scheduled Tasks Integration

N5 protocols integrate with Zo's scheduled tasks:
```markdown
Load file 'N5/prefs/operations/scheduled-task-protocol.md' before creating agents
```

### Custom Workflows

Create recipes in `Recipes/`:
```markdown
---
description: Your workflow description
tags: [tag1, tag2]
---

# Workflow steps here
```

## Best Practices

1. **Review bulletins regularly** - Stay informed of system updates
2. **Protect critical paths** - Prevent accidental deletion
3. **Document decisions** - Append to Records/decisions.jsonl
4. **Customize preferences** - Tailor N5 to your workflow
5. **Create recipes** - Automate repetitive tasks

## Getting Help

- Check `N5/docs/` for detailed documentation
- Review `N5/bulletins/` for known issues
- File issues at: https://github.com/vrijenattawar/zo-n5os-core/issues

---

**Next**: [Developer Guide](developer_guide.md) for extending N5
