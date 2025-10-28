# Conversation-End System User Guide

**Version:** 1.0  
**Created:** 2025-10-27  
**System:** N5 Conversation Management

---

## Overview

The Conversation-End System automates workspace cleanup and file organization at the end of AI conversations. It analyzes your conversation workspace, proposes actions, and executes them with safety guarantees.

**Key Benefits:**
- Automated file classification and organization
- Safe execution with dry-run and rollback
- Conflict detection and resolution
- Production-ready with comprehensive testing

---

## Quick Start

### Basic Usage

```bash
# Analyze current conversation
python3 /home/workspace/N5/scripts/conversation_end_analyzer.py

# Generate proposal
python3 /home/workspace/N5/scripts/conversation_end_proposal.py <analysis.json>

# Execute with dry-run
python3 /home/workspace/N5/scripts/conversation_end_executor.py --proposal <proposal.json> --dry-run

# Execute for real
python3 /home/workspace/N5/scripts/conversation_end_executor.py --proposal <proposal.json>
```

### All-in-One CLI

```bash
# Interactive mode (recommended)
python3 /home/workspace/N5/scripts/n5_conversation_end.py --interactive

# Auto mode (approve all)
python3 /home/workspace/N5/scripts/n5_conversation_end.py --auto

# Email mode (send proposal)
python3 /home/workspace/N5/scripts/n5_conversation_end.py --email

# Dry-run (preview only)
python3 /home/workspace/N5/scripts/n5_conversation_end.py --dry-run
```

---

## Modes

### Interactive Mode
- Review each proposed action
- Approve/reject individually
- Resolve conflicts manually
- Safest option

```bash
python3 /home/workspace/N5/scripts/n5_conversation_end.py --interactive
```

### Auto Mode
- Approves all non-conflicting actions
- Skips actions with conflicts
- Fast but less control

```bash
python3 /home/workspace/N5/scripts/n5_conversation_end.py --auto
```

### Email Mode
- Sends proposal to your email
- Review asynchronously
- No immediate execution

```bash
python3 /home/workspace/N5/scripts/n5_conversation_end.py --email
```

### Dry-Run Mode
- Preview without execution
- See what would happen
- Safe for testing

```bash
python3 /home/workspace/N5/scripts/n5_conversation_end.py --dry-run
```

---

## File Classification

### Automatic Rules

**TEMP Files** (Archived to scratch/)
- Prefix: `TEMP_`, `temp_`, `TMP_`
- Patterns: `scratch_*`, `test_*`, `draft_*`
- Versions: `*_v1.*`, `*_v2.*`, etc.

**FINAL Files** (Archived to root)
- Prefix: `FINAL_`, `final_`
- Suffix: `_final.*`
- Generally important deliverables

**DELIVERABLE Files** (Moved to Knowledge/Lists)
- Prefix: `DELIVERABLE_`
- High-value outputs to preserve

**Ignore Files** (Never touched)
- System files: `.git/`, `.env`, etc.
- Config: `package.json`, `.gitignore`
- Session: `SESSION_STATE.md`

---

## Safety Features

### P5: Anti-Overwrite
- Never overwrites existing files
- Checks destinations before execution
- Fails fast on conflicts

### P7: Dry-Run
- Preview all actions
- No filesystem changes
- Verify before committing

### P11: Failure Modes
- Atomic execution
- Rollback on error
- Transaction logging

### P19: Error Handling
- Graceful degradation
- Detailed error messages
- Context preservation

---

## Rollback

If something goes wrong:

```bash
# From executor instance (immediately after execution)
# Rollback is automatic on errors

# From transaction log (later recovery)
python3 /home/workspace/N5/scripts/conversation_end_executor.py \
  --rollback /tmp/conversation_end_transaction_<conv_id>.log
```

**Rollback Actions:**
- Move: Reverses destination → source
- Archive: Restores from archive
- Delete: Restores from backup

---

## Troubleshooting

### "Destination exists" errors
**Cause:** Target location already has a file  
**Solution:** Use interactive mode to resolve conflicts

### "No approved actions"
**Cause:** All actions were rejected or have conflicts  
**Solution:** Review proposal, resolve conflicts, try again

### "Precondition check failed"
**Cause:** Source missing or destination blocked  
**Solution:** Check file permissions and paths

### "Analysis failed"
**Cause:** Invalid workspace or missing SESSION_STATE.md  
**Solution:** Ensure you're in a valid conversation workspace

---

## Advanced Usage

### Custom Destinations

Edit the proposal JSON before execution:

```json
{
  "conversation_id": "con_123",
  "title": "My Conversation",
  "actions": [
    {
      "action_type": "move",
      "source": "/path/to/file.md",
      "destination": "/custom/destination/file.md",
      "approved": true
    }
  ]
}
```

### Batch Processing

Process multiple conversations:

```bash
for conv_dir in /home/.z/workspaces/con_*; do
  python3 /home/workspace/N5/scripts/n5_conversation_end.py \
    --workspace "$conv_dir" \
    --auto \
    --output "/tmp/results/$(basename $conv_dir).json"
done
```

### Integration with Workflows

Add to conversation cleanup automation:

```python
from N5.scripts.conversation_end_analyzer import ConversationAnalyzer
from N5.scripts.conversation_end_proposal import ProposalGenerator
from N5.scripts.conversation_end_executor import ConversationEndExecutor

# Analyze
analyzer = ConversationAnalyzer(workspace_path)
analysis = analyzer.analyze()

# Generate proposal
generator = ProposalGenerator(analysis)
proposal_json = generator.generate_json()

# Save and execute
proposal_path = Path("/tmp/proposal.json")
proposal_path.write_text(proposal_json)

executor = ConversationEndExecutor(proposal_path, dry_run=False)
result = executor.execute_proposal()
```

---

## Best Practices

1. **Always use dry-run first** - Preview before committing
2. **Resolve conflicts manually** - Don't force auto-approval with conflicts
3. **Check transaction logs** - Verify execution history
4. **Test rollback** - Ensure recovery works
5. **Use interactive mode** - When in doubt, review manually

---

## File Locations

- **Analyzer:** `/home/workspace/N5/scripts/conversation_end_analyzer.py`
- **Proposal Generator:** `/home/workspace/N5/scripts/conversation_end_proposal.py`
- **Executor:** `/home/workspace/N5/scripts/conversation_end_executor.py`
- **CLI:** `/home/workspace/N5/scripts/n5_conversation_end.py`
- **Tests:** `/home/workspace/N5/scripts/test_conversation_end.py`
- **Schema:** `/home/workspace/N5/schemas/conversation-end-proposal.schema.json`

---

## Support

**Issues:** Use `/N5/lists/detection_rules.md` to report bugs  
**Documentation:** `/home/workspace/Documents/System/`  
**Tests:** Run `python3 /home/workspace/N5/scripts/test_conversation_end.py`

---

**Last Updated:** 2025-10-27 11:49 ET
