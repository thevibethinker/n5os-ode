# Conversation-End Output Template

**Version:** 1.1.0  
**Date:** 2025-10-30  
**Purpose:** Strict formatting template for conversation closure outputs to ensure consistency

---

## ⚠️ CRITICAL INSTRUCTIONS FOR AI

**YOUR ROLE - YOU MUST:**
1. **Perform actual analysis yourself** - Read conversation files, understand what was built/discussed/accomplished
2. **Never use placeholder data** - All content must be real, specific, accurate from THIS conversation
3. **Never use stub data** - No "example.py", "Sample Report", "script.py", generic descriptions
4. **Never hardcode or reuse data** - Each conversation is unique, analyze it fresh every time
5. **Scripts only provide structure** - Python scripts give you the format template, YOU do the semantic analysis

**ABSOLUTELY PROHIBITED:**
❌ Generic titles like "Conversation 2025-10-30" or "Discussion Thread"
❌ Placeholder filenames like "script.py", "document.md", "file.txt"
❌ Copy-pasted descriptions from previous conversations
❌ Stub data like "3 files created" without listing the ACTUAL filenames
❌ Any content that doesn't reflect THIS SPECIFIC conversation's actual work

**ABSOLUTELY REQUIRED:**
✅ Specific, descriptive title based on what was ACTUALLY built/discussed (e.g., "Zo Feedback System Build + Debugger Verification")
✅ Real filenames with actual paths from THIS conversation workspace
✅ Accurate descriptions of what was ACTUALLY built/fixed/discussed
✅ Concrete numbers based on YOUR analysis (count files yourself, read git logs yourself)
✅ Real artifact paths that you verified exist

**THE SCRIPTS ARE DUMB, YOU ARE SMART:**
- Scripts can scan directories and match filename patterns
- Scripts CANNOT understand what the conversation was about
- Scripts CANNOT write meaningful summaries
- Scripts CANNOT determine if work was significant
- **YOU must do all semantic understanding and analysis**

---

## Output Structure

When presenting conversation closure results to the user, **you MUST follow this exact structure**:

```markdown
✅ Conversation Closed Successfully

Summary

Conversation: con_[CONVERSATION_ID]
Title: [Specific Descriptive Title Based on Actual Work]
Duration: ~[X] hours
Status: [Completed | Partially Complete | Blocked]

What Was Built / Accomplished

✅ [Primary Deliverable - be specific]

- [Specific detail 1]
- [Specific detail 2]
- [Specific detail 3]

[Additional sections as needed - e.g., "Debugger Verification Results", "Research Findings", etc.]

✅ [Secondary category if applicable]

- [Detail]
- [Detail]

Known Limitations

⚠️ [Specific limitation with technical details]

- **Workaround:** [Actual workaround implemented]
- **Impact:** [Concrete impact description]

Artifacts Archived

📁 [Actual archive path]

- 📄 [actual_filename.ext] - [Purpose description]
- 📄 [actual_filename2.ext] - [Purpose description]

Key Files Created

- 📄 [actual_file.py] - [Actual description]
- 📊 [actual_database.db] - [Actual description]
- 📄 [actual_config.yaml] - [Actual description]

Capability Registry Updates

- [Either a concrete list of capability changes, or an explicit statement that no capability changes were logged]

System Status

⚡ [Production Ready | Ready for Testing | Work in Progress]

- [Actual next step 1]
- [Actual next step 2]
- [Actual metric or status detail]

Conversation record updated and closed.
```

---

## Formatting Rules

### Required Elements
1. **Title** - Must be descriptive and specific to what was accomplished
2. **Duration** - Approximate from conversation timestamps
3. **What Was Built** - Primary deliverables with checkmarks
4. **Artifacts Archived** - Full path with folder icon
5. **Key Files Created** - Bullet list with file icons and descriptions
6. **Capability Registry Updates** - Explicit section reporting capability changes or explicitly stating that none were logged

### Optional Elements (include if relevant)
- **Known Limitations** - Only if there are actual limitations
- **Debugger Results** - If verification was performed
- **Research Findings** - If research was conducted
- **System Status** - Production readiness info

### Emoji Usage
- ✅ Completed items, success status
- ⚠️ Warnings, limitations, cautions
- 📁 Archive folders
- 📄 Regular files (.md, .py, .txt, docs)
- 📊 Data files (.db, .json, .csv, spreadsheets)
- 🍳 Recipe files (.md in Prompts/)
- ⚡ Status indicators (ready, in-progress)

### Capability Registry Updates Section

- Always include the **"Capability Registry Updates"** header in the final output.
- For **non-build / non-orchestrator threads** (no persistent system behavior created or modified), use a single bullet like:
  - `- None – No capability changes logged for this conversation (non-build or ephemeral thread).`
- For **build/orchestrator threads with registry changes**, enumerate each concrete change, e.g.:
  - `- New capability: meeting-pipeline-v3 – Meeting pipeline refactor with MG-2 integration (file 'N5/capabilities/internal/meeting-pipeline-v3.md').`
  - `- Updated capability: crm-v3 – Expanded entry points for Akiflow actions bridge (file 'N5/capabilities/internal/crm-v3.md').`
- Do **not** use placeholders like `capability-foo` or generic descriptions; reference real `capability_id` values and real capability file paths when changes are made.

### Path Formatting
- Archive paths: `📁 Documents/Archive/YYYY-MM-DD_con_XXXXX/`
- Key files: Relative to workspace root or absolute for N5 system files
- Use `file 'path'` syntax for clickable references where appropriate

---

## Transient Data Normalization Rules

- Remove or standardize all timestamps (e.g., replace with `<TIMESTAMP>`)
- Normalize session or conversation IDs consistently (e.g., `CONV_ID`)
- Convert all counters or counts to fixed placeholders
- Ensure any randomly generated IDs are replaced with deterministic placeholders

---

## Example 1: Feature Build + Verification

```markdown
✅ Conversation Closed Successfully

Summary

Conversation: con_uU5ZQJaeKT65AYVm
Title: Zo Feedback System Build + Debugger Verification
Duration: ~2 hours
Status: Completed

What Was Built

✅ Complete Zo Feedback System

- CLI submission tool (`zo_report.py`)
- SQLite database for feedback storage
- Google Drive integration (folder: "Zo Feedback")
- Automated daily sync (scheduled task @ 08:00 ET)
- Full documentation

Debugger Verification Results

✅ All Systems Verified

- Core scripts compile and execute correctly
- Database schema validated
- Drive integration tested (create→move→populate workflow)
- Scheduled task fixed (outdated instruction corrected)
- End-to-end workflow verified

Known Limitations

⚠️ Binary file uploads via `google_drive-upload-file` return internal server errors

- **Workaround:** Text-based reports work via `create-file-from-text`
- **Impact:** Image attachments stored locally, not uploaded (future enhancement)

Artifacts Archived

📁 Documents/Archive/2025-10-30_con_uU5ZQJaeKT65AYVm/

- 📄 DEBUGGER_REPORT.md - Full verification report

Key Files Created

- 📄 zo_report.py - Submission CLI
- 📄 feedback_sync_orchestrator.py - Sync orchestrator
- 📊 zo_feedback.db - Feedback database
- 📄 zo_feedback_system.md - User documentation
- 📄 zo_feedback_quickref.md - Quick reference
- 🍳 Zo Feedback Sync.md - Sync recipe

Capability Registry Updates

- New capability: zo-feedback-system – End-to-end Zo Feedback submission + processing workflow (file 'N5/capabilities/workflows/zo-feedback-system.md').

System Status

⚡ Production Ready

- Next sync: 2025-10-30 @ 08:00 ET
- Pending feedback: 1 item
- Drive folder: Zo Feedback

Conversation record updated and closed.
```

---

## Example 2: System Restoration

```markdown
✅ Conversation Closed Successfully

Summary

Conversation: con_B3VVZzx9mqkiHwg5
Title: Recipe System Restoration + Validator Build
Duration: ~2 hours
Status: Completed

What Was Accomplished

✅ Fixed recipes.jsonl duplication
✅ Restored 17 corrupted recipes
✅ Built recipe validator tool
✅ Enhanced Close Conversation recipe
✅ Debugger verification passed
✅ Working files archived

Key Deliverables

- 🍳 Repaired recipe registry (recipes.jsonl) - 98.6% valid
- 📄 Recipe validator (recipe_validator.py) - Ongoing maintenance tool
- 📄 Enhanced conversation-end protocol with safety checks
- 📄 Complete restoration documentation

Capability Registry Updates

- None – No capability changes logged for this conversation (system restoration and tooling hardening only).

System Status

⚡ Recipe system now 98.6% valid with proper tooling for ongoing maintenance

Artifacts Archived

📁 Documents/Archive/2025-10-30_Recipe-Restoration_con_B3VVZzx9mqkiHwg5/

- 📄 README.md (detailed summary)
- 📄 recipe_restoration_summary.md (technical details)
- 📄 completion_summary.txt
- 📄 debugger_report.txt
- 📄 summary.txt

Conversation record updated and closed.
```

---

## Example 3: Bug Fix

```markdown
✅ Conversation Closed Successfully

Summary

Conversation: con_XyZ123AbC456DeF7
Title: Fixed Email Integration Timeout Issue
Duration: ~45 minutes
Status: Completed

What Was Fixed

✅ Gmail API timeout issue resolved

- Increased timeout from 5s to 30s in email connector
- Added exponential backoff retry logic (3 attempts)
- Improved error logging with specific timeout messages

Debugger Verification Results

✅ Email Integration Verified

- Send test email: Success (delivered in 2.3s)
- Retry logic tested with simulated timeout: Working
- Error messages now include timestamp and attempt count

Key Files Modified

- 📄 N5/scripts/email_connector.py - Updated timeout and retry logic
- 📄 N5/logs/email_connector.log - Enhanced logging format

Capability Registry Updates

- None – No capability changes logged for this conversation (targeted bug fix only).

System Status

⚡ Production Ready

- Email integration stable
- No pending issues

Conversation record updated and closed.
```

---

## Checklist Before Presenting Output

Before showing your final output to the user, verify:

- [ ] Title is specific and describes actual work (not generic)
- [ ] All filenames are real files from THIS conversation
- [ ] All paths are accurate and verifiable
- [ ] Numbers are based on YOUR analysis (file counts, durations, etc.)
- [ ] Descriptions match what was ACTUALLY built/fixed/discussed
- [ ] No placeholder data (no "script.py", "file.txt", generic names)
- [ ] No stub data (no "several files", "some scripts" - be specific)
- [ ] Archive path follows format: Documents/Archive/YYYY-MM-DD_[title]_con_XXXXX/
- [ ] Emoji usage matches guidelines above
- [ ] Structure matches template exactly

---

## What The Recipe Will Tell You

When you run the Close Conversation recipe, you will receive:

1. **This template** - The structure to follow
2. **Instructions** - What phases to execute
3. **Script commands** - Python scripts to run for file operations

**The scripts will:**
- Scan conversation workspace directory
- Move files according to basic rules (pattern matching)
- Generate git status info
- Create archive folders

**The scripts will NOT:**
- Understand what the conversation was about
- Write meaningful descriptions
- Determine significance of work
- Create summaries or titles

**YOU must:**
- Read the actual conversation messages
- Understand what was built/discussed
- Write accurate, specific descriptions
- Generate meaningful title
- Determine what belongs in summary

---

## Maintenance

Update this template when:
- New required sections identified
- Archive structure changes
- User feedback indicates format improvements needed

**Version history:**
- 1.1.0 (2025-10-30): Added CRITICAL INSTRUCTIONS section clarifying AI analysis role
- 1.0.0 (2025-10-30): Initial template based on successful closure format


