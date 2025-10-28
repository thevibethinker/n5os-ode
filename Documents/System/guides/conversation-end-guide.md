# Conversation-End System Guide

**Version:** 2.0  
**Status:** Production Ready  
**Updated:** 2025-10-27

---

## Quick Start

### Interactive Mode (Recommended)

```bash
python3 N5/scripts/n5_conversation_end.py
```

This will:
1. Analyze your conversation workspace
2. Show you a proposal with recommended actions
3. Let you review and approve/modify actions
4. Execute approved actions safely

### Auto Mode (Scheduled Tasks)

```bash
python3 N5/scripts/n5_conversation_end.py --auto
```

Uses intelligent defaults and executes immediately without user prompts. Perfect for automated cleanup tasks.

### Dry-Run Mode (Preview Only)

```bash
python3 N5/scripts/n5_conversation_end.py --dry-run
```

Shows what would be done without making any changes. Safe to run anytime.

---

## How It Works

The conversation-end system follows a **three-phase workflow**:

### 1. Analysis Phase

**What it does:**
- Scans all files in conversation workspace
- Classifies files by purpose (temporary, final, deliverable, etc.)
- Detects conflicts and potential issues
- Generates conversation title
- Proposes appropriate actions for each file

**File Classification:**
- **Temporary** - Draft files, scratch notes (TEMP_, draft_, scratch_,_v2, _v3, etc.)
- **Final** - Completed work (FINAL_, final_, complete_)
- **Deliverable** - User-facing outputs (DELIVERABLE_, deliverable_)
- **Keep** - Important files to preserve (README, SESSION_STATE, etc.)
- **Ignore** - System files (.git, .backup, __pycache__, etc.)

### 2. Proposal Phase

**What it does:**
- Generates human-readable proposal
- Groups actions by type (archive, delete, promote, keep)
- Explains rationale for each action
- Highlights conflicts and warnings
- Provides interactive selection UI

**Action Types:**
- **archive** - Move to Records/Archive with timestamp
- **delete** - Remove temporary/draft files
- **promote** - Move deliverables to user workspace
- **keep** - No action, file stays in place
- **rename** - Update title/filename

### 3. Execution Phase

**What it does:**
- Creates backup before making changes
- Executes approved actions atomically
- Verifies each operation
- Logs all changes
- Enables rollback if needed

**Safety Features:**
- Anti-overwrite protection (P5)
- Dry-run mode (P7)
- Atomic operations
- Full rollback capability
- Comprehensive logging

---

## Usage Examples

### Example 1: End of Build Session

You've been working on a new feature. You have drafts, final versions, and test files:

```
workspace/
├── TEMP_notes.md
├── TEMP_draft_v2.py
├── FINAL_feature.py
├── DELIVERABLE_readme.md
├── test_output.json
└── SESSION_STATE.md
```

Run:
```bash
python3 N5/scripts/n5_conversation_end.py
```

The system will propose:
- **Archive** TEMP_notes.md → Records/Archive/2025-10-27/
- **Delete** TEMP_draft_v2.py (superseded by final)
- **Promote** DELIVERABLE_readme.md → /home/workspace/
- **Archive** FINAL_feature.py → Records/Archive/2025-10-27/
- **Delete** test_output.json (temporary output)
- **Keep** SESSION_STATE.md

### Example 2: Research Session

You've collected notes, web research, and analysis:

```
workspace/
├── research_notes.md
├── web_article_1.md
├── web_article_2.md
├── FINAL_analysis.md
└── SESSION_STATE.md
```

The system will propose:
- **Archive** all research materials together
- **Promote** FINAL_analysis.md to Knowledge/ or Documents/
- **Update** SESSION_STATE.md with completion metadata

### Example 3: Quick Cleanup

You want to clean up without reviewing everything:

```bash
python3 N5/scripts/n5_conversation_end.py --auto
```

The system will:
- Auto-approve safe actions (archive temps, delete obvious drafts)
- Prompt for conflicts only
- Execute immediately

---

## Modes Explained

### Interactive Mode (Default)

**When to use:** Normal conversation cleanup

**How it works:**
1. Analyzes workspace
2. Shows full proposal
3. Lets you select/deselect actions
4. Executes your selections
5. Confirms completion

**Advantages:**
- Full control
- Review before execution
- Learn what the system proposes
- Customize for special cases

### Auto Mode

**When to use:** Scheduled cleanup, routine maintenance

**How it works:**
1. Analyzes workspace
2. Auto-approves using intelligent defaults
3. Prompts only for conflicts
4. Executes immediately
5. Logs results

**Defaults:**
- Archive: TEMP_, FINAL_, versioned files
- Delete: obvious duplicates, old drafts
- Promote: DELIVERABLE_ files
- Keep: README, SESSION_STATE, important files

**Advantages:**
- Fast
- Consistent
- No interaction needed
- Perfect for automation

### Dry-Run Mode

**When to use:** Testing, learning, verification

**How it works:**
1. Analyzes workspace
2. Shows complete proposal
3. Simulates execution
4. **Makes NO changes**
5. Shows what would happen

**Advantages:**
- 100% safe
- Preview actions
- Verify behavior
- Debug issues

**Combine with other modes:**
```bash
python3 N5/scripts/n5_conversation_end.py --auto --dry-run
```

---

## Special Features

### Rollback

If you need to undo changes:

```bash
# System creates automatic backup before execution
# Backup stored in workspace/.backup/

# To rollback (from any conversation):
python3 N5/scripts/conversation_end_executor.py --rollback --workspace /path/to/workspace
```

### Title Generation

The system automatically generates conversation titles based on:
1. SESSION_STATE.md focus/objective
2. Most significant file in workspace
3. File name patterns
4. Content analysis

Override:
```bash
python3 N5/scripts/n5_conversation_end.py --title "Custom Title"
```

### Conflict Detection

The system detects:
- Multiple final versions
- Files that would overwrite in destination
- Ambiguous classifications
- Missing dependencies

Conflicts require manual resolution.

### Batch Operations

Process multiple conversations:

```bash
# Archive all conversations from date range
for conv in $(ls -d /home/.z/workspaces/con_*); do
    python3 N5/scripts/n5_conversation_end.py --workspace "$conv" --auto
done
```

---

## Integration

### Scheduled Tasks

Create agent to run daily:

```bash
# In Zo conversation:
Create scheduled task:
- Schedule: Daily at 11pm
- Instruction: "Run conversation-end cleanup on all old conversations using N5/scripts/n5_conversation_end.py --auto"
```

### Manual Triggers

Add to your workflow:

```bash
# End of session command
alias convend='python3 /home/workspace/N5/scripts/n5_conversation_end.py'
```

### From Any Conversation

The system works in fresh conversations (P12):

```bash
python3 /home/workspace/N5/scripts/n5_conversation_end.py --workspace /path/to/workspace
```

---

## Troubleshooting

### "No files to process"

**Cause:** Empty workspace or all files classified as "ignore"

**Solution:** Check that workspace has analyzable files. System ignores .git/, .backup/, etc.

### "Conflicts detected"

**Cause:** Multiple files competing for same action (e.g., two FINAL_ files)

**Solution:** Review proposal, manually resolve conflicts, re-run

### "Failed to archive"

**Cause:** Permission issues or destination path problems

**Solution:** 
- Check logs for specific error
- Verify /home/workspace/Records/ exists
- Check disk space

### "Backup failed"

**Cause:** Insufficient disk space or permission issues

**Solution:**
- Check disk space: `df -h`
- Check workspace permissions
- Clear old backups: `rm -rf workspace/.backup/*`

### Rollback Not Working

**Cause:** Backup directory missing or corrupted

**Solution:**
- Check backup exists: `ls workspace/.backup/`
- Restore manually from snapshot (System page)
- Re-run original operation

---

## Advanced Usage

### Custom Classification Rules

Edit analyzer to add custom patterns:

```python
# In conversation_end_analyzer.py
TEMP_PATTERNS = [
    r'^TEMP_',
    r'_draft_',
    r'your_custom_pattern'
]
```

### Custom Actions

Add new action types in proposal generator:

```python
# In conversation_end_proposal.py
def propose_custom_action(file):
    return {
        "type": "custom",
        "file": file,
        "destination": "/custom/path/",
        "reason": "Custom logic"
    }
```

### Integration with Other Systems

Export proposal for external processing:

```bash
python3 N5/scripts/n5_conversation_end.py --export-json > proposal.json
# Process with your tool
# Import results
python3 N5/scripts/conversation_end_executor.py --proposal proposal.json
```

---

## FAQ

**Q: Will this delete important files?**\
A: No. The system classifies files conservatively. TEMP_ and draft files are archived, not deleted. You review all actions before execution.

**Q: Can I undo changes?**\
A: Yes. Automatic backup created before execution. Use rollback feature or restore from system snapshot.

**Q: Does it work in scheduled tasks?**\
A: Yes. Use `--auto` mode. Perfect for automated cleanup.

**Q: What happens to SESSION_STATE.md?**\
A: It's always kept and updated with completion metadata.

**Q: Can I customize proposals?**\
A: Yes. In interactive mode, select/deselect any actions. Or edit classification rules.

**Q: Is it safe to run multiple times?**\
A: Yes. Idempotent design. Running twice does nothing if already clean.

**Q: How do I see what it would do?**\
A: Use `--dry-run` mode. Shows all actions without executing.

**Q: Can I run it on old conversations?**\
A: Yes. Specify `--workspace /path/to/conversation` from any conversation.

---

## Architecture Overview

### Components

**conversation_end_analyzer.py**
- Workspace scanning
- File classification
- Conflict detection
- Title generation

**conversation_end_proposal.py**
- Proposal generation
- Human-readable formatting
- Interactive UI
- JSON export

**conversation_end_executor.py**
- Atomic execution
- Backup management
- Rollback capability
- State verification

**n5_conversation_end.py**
- CLI interface
- Mode orchestration
- User interaction
- Logging and reporting

### Data Flow

```
Workspace Files
     ↓
[Analyzer] → Analysis JSON
     ↓
[Proposal] → Proposal (human + JSON)
     ↓
[User Review] → Approved Actions
     ↓
[Executor] → File Operations
     ↓
Updated Workspace
```

### Safety Layers

1. **Pre-flight:** Analysis and conflict detection
2. **Review:** User approval (interactive mode)
3. **Backup:** Full workspace backup
4. **Atomic:** All-or-nothing execution
5. **Verification:** Post-execution checks
6. **Rollback:** Undo capability
7. **Logging:** Complete audit trail

---

## Principle Compliance

This system adheres to N5 architectural principles:

- **P0 (Rule-of-Two):** Minimal context loading
- **P5 (Anti-Overwrite):** Never overwrites without user approval
- **P7 (Dry-Run):** Full dry-run capability
- **P11 (Failure Modes):** Comprehensive error handling
- **P12 (Fresh Conversation):** Works without prior context
- **P19 (Error Handling):** Robust exception handling
- **P20 (Modular):** Clean component separation
- **P22 (Language Selection):** Python for data processing

---

## Support

**Issues:** Report via "Report an issue" button in Zo app

**Discord:** https://discord.gg/zocomputer

**Logs:** Check `/dev/shm/n5_conversation_end.log` for debugging

---

**Version:** 2.0  
**Last Updated:** 2025-10-27 11:45 ET  
**Status:** Production Ready
