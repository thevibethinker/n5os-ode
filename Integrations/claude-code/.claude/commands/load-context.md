# /load-context

Load domain-specific N5OS preferences and modules into the conversation.

## Usage

```
/load-context <context_name>
```

## Available Contexts

| Context | Description | When to Use |
|---------|-------------|-------------|
| `system_ops` | Safety, file protection, git governance, risk scoring | System admin, file operations |
| `content_generation` | Voice profiles, quality validation, style guide | Writing emails, documents |
| `crm_operations` | CRM usage, relationship thresholds, stakeholder rules | Contact management |
| `code_work` | File protection, git governance, coding agent, distributed builds | Code modifications |
| `scheduling` | Scheduling settings, task protocol, presets | Creating scheduled tasks |
| `research` | Enrichment settings, quality validation | Deep research, analysis |
| `conversation_end` | Thread closure triggers | Ending conversations |
| `build` | Planning prompt, architectural principles | Implementation work |
| `strategy` | Principles, company timeline | High-level planning |
| `health` | Bio-context, medications, supplements | Health planning |
| `full` | All modules (use sparingly per P08) | Complete context needed |

## Instructions

When the user invokes `/load-context <context>`:

1. **Validate context name**: Check if it's a known context from the table above
2. **Load via preference loader**:
   ```bash
   python3 N5/scripts/load_preferences.py load <context> --content --json
   ```
3. **For manifest-based contexts** (build, strategy, health, etc.):
   ```bash
   python3 N5/scripts/n5_load_context.py --context <context>
   ```
4. **Present loaded modules**: Show which preference files were loaded
5. **Summarize key rules**: Extract and present the most important rules from loaded modules

## Context Resolution

The system uses two loaders with different strengths:

**Hub Loader** (`load_preferences.py`):
- Uses `N5/config/user_preferences.yaml` as registry
- Best for: system_ops, content_generation, crm_operations, code_work, scheduling, research, conversation_end, full
- Provides: Module paths, priorities, precedence hierarchy

**Manifest Loader** (`n5_load_context.py`):
- Uses `N5/prefs/context_manifest.yaml` for simpler mapping
- Best for: build, strategy, system, safety, scheduler, writer, research, health, general
- Provides: Direct file content loading

## Example Output

```
Loaded context: code_work

Modules (5):
- [critical] safety → N5/prefs/system/safety-rules.md
- [critical] file_protection → N5/prefs/system/file-protection.md
- [high] git_governance → N5/prefs/system/git-governance.md
- [medium] coding_agent → N5/prefs/integration/coding-agent.md
- [medium] distributed_builds → N5/prefs/operations/distributed-builds/SYSTEM_OVERVIEW.md

Key Rules Active:
- Never overwrite protected files without confirmation
- Auto-version on filename conflict (_v2, _v3)
- Use coding agent for multi-file changes >3 files
- Check .n5protected markers before move/delete
```

## Combining with Manual Loading

After loading a context, you can load additional specific files:

```
file 'N5/prefs/communication/voice.md'
file 'Knowledge/stable/company/strategy.md'
```

## Notes

- Core principles (P02, P05, P08, P15, P16, P22) are always active from session start
- Loading `full` context violates P08 (Minimal Context) - use only when truly needed
- Context loading is additive - you can load multiple contexts in sequence
