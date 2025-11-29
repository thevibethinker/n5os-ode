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

**Protected File Patterns (2025-10-14):**
- **Pattern:** Identify architecturally critical files that should never be auto-modified
- **Examples:**
  - `architectural_principles.md` - Core system design
  - `commands.jsonl` - System command registry
  - Schema files (`.schema.json`) - Data contracts
  - Production configuration files
- **Implementation:** 
  - Maintain protected file list in config
  - Scripts check against list before writes
  - Require `--force` flag + explicit confirmation for protected files
  - Log all attempted modifications to protected files
- **Rationale:** Some files are foundational; accidental corruption cascades through system
- **Key insight:** Protection is about blast radius, not just importance

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
- Destructive changes
- System migrations
- System modifications
- Scheduled tasks

**Implementation:**
- `--dry-run` flag on all commands
- Preview changes before applying
- Log what would happen without executing

**Lessons Learned:**

**Automated Cleanup Pattern (2025-10-14):**
- **Context:** Phase 7 cleanup after CRM consolidation
- **Implementation:** Comprehensive dry-run preview showing all changes (21 files, 85 replacements, 13 archived files, 3 backup sets)
- **Result:** User validated preview, zero errors, zero broken references after execution
- **Key insight:** Dry-run validation prevents destructive mistakes; detailed preview builds confidence

**Multi-Phase Cleanup Operations (2025-10-14):**
- **Pattern:** Three discrete phases: (1) Deprecate legacy scripts with notices, (2) Archive legacy directories to Documents/Archive/ with metadata, (3) Compress migration artifacts
- **Why it works:** Each phase is reversible; failures don't cascade; state is verifiable at each step
- **Application:** Applies to any large-scale cleanup or migration operation

---

## 11) Failure Modes and Recovery

**Purpose:** Design for predictable, recoverable failures

**Rules:**
- Anticipate failure points in automation.
- Provide recovery instructions or auto-resume capabilities.
- Log failures with context for debugging.

**When to apply:**
- Multi-step workflows
- External API integrations
- Long-running processes
- Automated deployments

**Implementation:**
- Checkpoint progress in multi-phase operations
- Provide rollback mechanisms
- Document recovery procedures
- Design for graceful degradation

**Lessons Learned:**

**Graceful Degradation for Enhancement Integrations (2025-10-14):**
- **Context:** Integrating timeline automation into thread export workflow
- **Problem:** Core workflow should complete successfully even if enhancement features fail
- **Solution:** Wrap enhancement imports in try/except, check availability flag before execution, log failures but continue
- **Example:** `try: from enhancements import timeline; HAS_TIMELINE = True except: HAS_TIMELINE = False; log warning; continue core workflow`
- **Key insight:** Core functionality must never be blocked by optional enhancements
- **Application:** Any feature integration where base system should work independently

**Post-Archive Timeline Integration (2025-10-14):**
- **Context:** Placing timeline automation in export workflow
- **Decision:** Timeline check (Phase 6) placed AFTER archive creation (Phase 5) but BEFORE completion message
- **Rationale:** Archive is safe on disk before attempting risky timeline automation; if timeline fails, export still succeeds
- **Key insight:** Order operations by criticality and reversibility

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

## Summary

Safety principles ensure that N5 operations are:
- **Reversible**: Via dry-run and versioning
- **Protected**: Via anti-overwrite and confirmation
- **Recoverable**: Via failure modes and backups
- **Resilient**: Via error handling

**Always load these principles for:**
- File operations
- Automation workflows
- Destructive actions
- System-critical scripts

---

## 34) Secrets Management

**Purpose:** Centralize and protect all API keys, tokens, and credentials

**Rules:**
- All secrets MUST be stored in encrypted secrets manager (`N5/scripts/n5_secrets.py`)
- Never store secrets in plaintext files, `.env` files, or hardcoded in scripts
- Zo-managed secrets (OPENAI_API_KEY, etc.) remain in environment
- All secret access automatically logged to audit trail
- Rotation tracking enforced per secret type

**When to apply:**
- Any script requiring third-party API authentication
- Service account credentials
- Database passwords
- OAuth tokens
- Internal authentication tokens

**Implementation:**
```python
from n5_secrets import SecretsManager

secrets = SecretsManager()
api_key = secrets.get("service_api_key")
# Use api_key...
# Access automatically logged to N5/data/secrets_audit.jsonl
```

**Full specification:** `file 'Knowledge/architectural/principles/P34-secrets-management.md'`

**Related:** P2 (SSOT), P5 (Anti-Overwrite), P19 (Error Handling)
