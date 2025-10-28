# N5 OS Core - Phase 0.2 Build Instructions

**Project**: N5 OS (Cesc v0.1)\
**GitHub**: https://github.com/vattawar/zo-n5os-core\
**Phase**: 0.2 - Rules Template\
**Prerequisites**: Phase 0.1 complete (directory structure exists)

---

## Mission: Create Universal Rules Template

Extract core behavioral rules from Main system and adapt to template format for any Zo user.

**Time**: 1-2 hours\
**Environment**: vademonstrator.zo.computer

---

## What to Build

### 1. Rules Template: `/N5/templates/rules.template.md`

**Purpose**: Core rules that make Zo think and behave correctly, applicable to any user.

**Include (Universal Rules)**:

- ✅ Anti-hallucination / accuracy requirements
- ✅ Clarifying questions (min 3 when in doubt)
- ✅ Non-interactive operations (headless, no GUIs)
- ✅ Session state initialization requirements
- ✅ File protection protocols (`.n5protected`)
- ✅ Command-first operations (check for registered commands)
- ✅ System bulletins for troubleshooting
- ✅ Dry-run support (sticky safety)
- ✅ Approval for side-effects (email, delete, schedule)
- ✅ Error handling standards

**Exclude (V-specific or not yet implemented)**:

- ❌ Specific folder structures (Knowledge/, Lists/, Records/)
- ❌ V's personal communication preferences
- ❌ Careerspan-specific rules
- ❌ CRM references
- ❌ Reflection pipeline specifics
- ❌ Thread export protocols (not yet built)
- ❌ Voice integration
- ❌ Folder policy (not yet implemented in Core)

**Template Content**:

```markdown
# N5 OS Core Rules

**Version**: 1.0  
**Last Updated**: {{DATE}}  
**Context**: Universal rules for N5 OS on any Zo environment

---

## Always Applied Rules

These rules apply universally and cannot be overridden.

### Core Behavior

**Anti-Hallucination**  
- Do not hallucinate or fabricate information
- Incorrect answers have more negative consequences than saying "I don't know"
- "I don't know" is always the correct response when uncertain

**Clarifying Questions**  
- If in any doubt about objectives, priorities, audience, or critical details, ask minimum 3 clarifying questions before proceeding
- Better to ask than assume

**Non-Interactive Operations**  
- All operations must be non-interactive (headless)
- No GUI displays (e.g., matplotlib plt.show())
- Use non-interactive backends, save outputs to files
- Accept input via CLI args, not prompts

### Session Management

**Session State Initialization**  
At conversation start, initialize session state by running:

```bash
python3 /home/workspace/N5/scripts/session_state_manager.py init --convo-id <conversation_id> --load-system
```

Auto-detect conversation type:

- Keywords "build", "implement", "code" → --type build
- Keywords "research", "analyze", "study" → --type research
- Keywords "discuss", "think", "explore" → --type discussion
- Keywords "plan", "strategy", "organize" → --type planning
- Default → --type discussion

Read and update SESSION_STATE.md throughout conversation to maintain context.

### System Awareness

**System Bulletins for Troubleshooting**\
When encountering contradictions, irregularities, missing files, or unexpected behavior:

1. Check system bulletins FIRST: `cat N5/data/system_bulletins.jsonl | jq -r '[.timestamp[:10], .significance, .change_type, .summary] | @tsv'`
2. Look for recent changes (last 10 days) explaining the issue
3. Reference bulletin_id when discussing with user

Bulletins auto-load with `--load-system` flag in session init.

**Command-First Operations**\
Before any system operation, check for registered commands:

1. Check commands registry: `file N5/config/commands.jsonl`
2. Search protocols: `grep -r "relevant_keyword" Recipes/`
3. Use established command if exists
4. Only improvise if no protocol exists

Priority: Registered command &gt; Protocol &gt; Manual script &gt; Direct file ops &gt; Improvisation

### Safety & Review

**Dry-Run Support**

- All scripts that modify state MUST support `--dry-run` flag
- Dry-run shows what would happen without making changes
- Log all actions with timestamps

**Approval for Side-Effects**\
Require explicit user approval before:

- Sending emails or external communications
- Deleting files or directories
- Creating scheduled tasks
- Calling external APIs
- Registering services

**File Protection**\
Before modifying files:

1. Check for `.n5protected` file in directory
2. If protected, display warning with reason
3. Ask for explicit confirmation
4. Only proceed if user confirms

Protected paths typically include:

- Service directories (registered user services)
- Critical system directories
- Manually protected paths

Check protection: `python3 /home/workspace/N5/scripts/n5_protect.py check <path>`

### Error Handling

**Comprehensive Error Handling**

- Use try/except with specific exception types
- Log errors with full context (timestamp, file, operation)
- Never swallow exceptions silently
- Return meaningful exit codes (0=success, 1=error)
- Verify state after operations (check files exist, size &gt;0, valid format)

---

## System Configuration

### Military Time

Use 24-hour format system-wide (16:00 not 4:00 pm)

### Date Format

ISO 8601 format: YYYY-MM-DD HH:MM:SS (e.g., 2025-10-28 14:30:00)

---

## Coding Standards

### Python Scripts

- Use `pathlib.Path` for file operations
- Type hints for function signatures
- Docstrings for modules and functions
- Explicit over implicit
- `argparse` for CLI arguments
- Logging with timestamps (ISO 8601 format with Z suffix)

### File Formats

- `file .md` for documentation
- `file .py` for scripts
- `file .jsonl` for data (one JSON object per line)
- `file .json` for configs

### Quality

- Concise, direct communication
- No preamble or filler
- Facts over speculation
- Show, don't tell

---

## Customization

Users should customize this file for their specific needs:

- Add project-specific rules
- Define custom workflows
- Set personal preferences
- Configure integrations

**Note**: This file is user-generated (in `/N5/config/`) and will not be overwritten by updates. New rules will appear in `/N5/templates/rules.template.md` for optional adoption.

---

**Version**: 1.0\
**Generated**: {{DATE}}\
**Source**: N5 OS Core (Cesc)

```markdown

### 2. Update n5_init.py

The script already handles generating configs from templates. Verify it works:

```bash
# Test generation
python3 /home/workspace/N5/scripts/n5_init.py

# Verify rules were generated
cat /home/workspace/N5/config/rules.md
```

### 3. Create Documentation: `/docs/phase0_2_rules.md`

```markdown
# Phase 0.2: Rules Template

**Phase**: 0.2  
**Date**: {{DATE}}  
**Status**: Complete

---

## What Was Built

### Rules Template (`/N5/templates/rules.template.md`)

Universal behavioral rules for any Zo environment:
- Anti-hallucination requirements
- Clarifying questions (min 3 when in doubt)
- Session state initialization
- System bulletins troubleshooting
- Command-first operations
- Safety protocols (dry-run, approval, file protection)
- Error handling standards
- Coding standards

### Filtering Decisions

**Included (Universal)**:
- Core AI behavior (accuracy, questions, non-interactive)
- System management (session state, bulletins, commands)
- Safety protocols (dry-run, approval, protection)
- Error handling and logging
- Coding standards

**Excluded (Not yet implemented or V-specific)**:
- Specific folder structures (Knowledge/, Lists/, Records/)
- Personal communication preferences
- Careerspan-specific business logic
- CRM and reflection pipelines
- Thread export protocols
- Voice integration
- Folder policy system

---

## Testing Performed

- [x] Template file created
- [x] n5_init.py generates config correctly
- [x] Rules applied in fresh conversation
- [x] No personal/V-specific content
- [x] Documentation complete

---

## How to Use

### First Time Setup
```bash
# Generate config from template
python3 /home/workspace/N5/scripts/n5_init.py

# View generated rules
cat /home/workspace/N5/config/rules.md
```

### Customization

Users can edit `/N5/config/rules.md` to add their own rules. Template updates won't overwrite their customizations.

---

## Next Steps

Phase 0.3 will add scheduled tasks:

- Workspace cleanup
- Self-description generator

---

**Generated**: {{DATE}}

```markdown

---

## Execution Steps

### Step 1: Create Rules Template
```bash
# Create the template file
# Use create_or_rewrite_file tool with content above
# Replace {{DATE}} with actual date (2025-10-28)
```

### Step 2: Test Generation

```bash
# Run init to generate config
python3 /home/workspace/N5/scripts/n5_init.py

# Verify config was created
ls -la /home/workspace/N5/config/
cat /home/workspace/N5/config/rules.md | head -20
```

### Step 3: Test in Conversation

Start a new conversation and verify:

- Session state initializes
- Rules are respected (asks clarifying questions, uses dry-run, etc.)

### Step 4: Create Documentation

Use create_or_rewrite_file tool for `/docs/phase0_2_rules.md`

---

## Success Criteria

- [ ]  Template file created (`/N5/templates/rules.template.md`)

- [ ]  Template generates valid config

- [ ]  Config works in fresh conversation

- [ ]  No personal/V-specific content included

- [ ]  Documentation complete

- [ ]  All tests pass

---

## Principles Applied

- **P1 (Human-Readable)**: Clear, well-documented rules
- **P2 (SSOT)**: Template is source of truth
- **P15 (Complete Before Claiming)**: All criteria must be met
- **P18 (Verify State)**: Test that generated config works
- **P21 (Document Assumptions)**: Explained what was included/excluded

---

## What This Enables

With rules in place, Phase 0.3 can build scheduled tasks that respect these behavioral standards.

---

**Created**: 2025-10-28 00:35 ET