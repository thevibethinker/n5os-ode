---
date: "2025-10-12T00:00:00Z"
version: 2.0
category: safety
priority: critical
---
# Safety Principles

These principles prevent data loss, corruption, and destructive actions.

## 5) Safety, Determinism, and Anti-Overwrite

**Purpose:** Protect critical files from accidental destruction

**Rules:**
- Never overwrite protected files without explicit confirmation.
- If a filename conflict exists, auto-version: `_v2`, `_v3`, … and log.
- Keep a rolling backup and write an audit line per operation.

**When to apply:**
- Any file write operation
- Bulk operations
- Automated workflows

**Implementation:**
- Check file protection status before writing
- Require explicit approval for hard-protected files
- Always create backups before destructive operations

---

## 7) Idempotence and Dry-Run by Default

**Purpose:** Make operations safe to repeat and test

**Rules:**
- Support `dry-run` mode for any workflow that writes files or schedules events.
- Re-running the same instruction should produce identical end-state unless inputs changed.
- Always offer dry-run before executing destructive operations.

**When to apply:**
- New automation workflows
- Bulk file operations
- System modifications
- Scheduled tasks

**Implementation:**
- `--dry-run` flag on all commands
- Preview changes before applying
- Log what would happen without executing

---

## 11) Failure Modes and Recovery

**Purpose:** Handle errors gracefully and enable recovery

**Rules:**
- If transcript quality is low or uncertainty >25%, pause for better input.
- On any exception, write a minimal incident note to logs and stop before destructive actions.
- Document recovery steps for common failures.

**When to apply:**
- Ingestion workflows
- Automated processing
- Multi-step operations

**Implementation:**
- Quality checks before processing
- Checkpoint between major steps
- Clear error messages with recovery instructions
- Log files for post-mortem analysis

---

## 19) Error Handling is Not Optional

**Purpose:** Every system must gracefully handle failures

**Rules:**
- Every system must have explicit error handling and recovery paths.
- Document what to do when things fail.
- Log errors for post-mortem analysis.
- Use atomic writes to prevent partial/corrupt state.

**When to apply:** All systems, especially:
- File I/O operations
- API calls
- Multi-step workflows
- State updates

**Implementation:**
- Try-catch blocks with specific handlers
- Rollback mechanisms for failed transactions
- Error logging with context
- User-facing error messages with actionable guidance

**Anti-patterns:**
- Omitting error paths because "it should work"
- Silent failures that corrupt state
- Generic error messages without context
- No recovery mechanism after failure

**Example from thread export refactoring (2025-10-12):**
- Bad: Assume file writes succeed
- Good: Verify file exists, check size, validate structure after write
