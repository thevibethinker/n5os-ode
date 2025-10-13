---
date: "2025-10-12T00:00:00Z"
version: 2.0
category: operations
priority: medium
---
# Operations Principles

These principles guide day-to-day operations, testing, and maintenance.

## 6) Mirror Sync Hygiene

**Purpose:** Detect and handle sync issues

**Rules:**
- If a file suddenly appears empty or truncated, suspect mirror sync.
- Action: halt writes, snapshot directory, compare against last known checksums, then proceed.

**When to apply:**
- Bulk file operations
- Unexpected file state changes
- Automated sync processes

---

## 9) Copyable Blocks Philosophy

**Purpose:** Reduce friction for user actions

**Rules:**
- Provide crisp, ready-to-paste blocks for follow-ups and questions.
- Avoid boilerplate; surface the crux and let V add connective tissue.
- Focus on actionable, minimal-edit content.

**When to apply:**
- Email drafts
- Follow-up questions
- Action items
- Command examples

**Examples:**
- Email drafts that need only subject line changes
- Calendar entries ready to paste
- Commands ready to execute

---

## 10) Calendar & Time Semantics

**Purpose:** Respect timezone and user control

**Rules:**
- When creating follow-ups, propose calendar entries with clear descriptions like: "Processed via N5 Ingestion – [Component]".
- Respect the user's timezone; never auto-schedule without confirmation.
- Always show proposed times for user approval.

**When to apply:**
- Action item follow-ups
- Meeting scheduling
- Reminder creation
- Scheduled tasks

---

## 12) Testing in Fresh Threads

**Purpose:** Validate context assumptions

**Rules:**
- To validate changes, run workflows in a new thread to guarantee only declared files are in context.
- Test with clean slate to ensure reproducibility.

**When to apply:**
- New workflow validation
- System changes
- Command updates
- Troubleshooting loading issues

---

## 13) Naming and Placement

**Purpose:** Consistent organization

**Rules:**
- Meetings go under `/home/workspace/Meetings/` using `{type}_{date}_{topic}.md`.
- Ask for location if ambiguous; never create new roots without consent.
- Follow existing folder structures and naming conventions.

**When to apply:**
- Creating new files
- Processing meeting notes
- Organizing outputs

---

## 14) Change Tracking

**Purpose:** Document evolution

**Rules:**
- Append a concise change log in standards files.
- Example: `2025-09-21 — Added Rule-of-Two, tiered voice policy, anti-overwrite.`
- Include date, version, and summary of changes.

**When to apply:**
- Standards updates
- Principle additions
- System changes
- Workflow modifications


**Example from lesson extraction (2025-10-12):**
- Thread: con_JB5UD88QWtAkoaXF
- Issue: Repeatedly made mistake of saying 'call LLM API' or 'implement LLM integration' when designing lessons extraction. Correct approach: I AM the LLM running in this environment. I should do the analysis directly during conversation, not call external services.
- Context: User has been 'burned by this multiple times' - I keep treating myself as external to the system rather than recognizing I'm the processing engine. This violates operational principles and adds unnecessary complexity.
- Resolution: Clarified: When scripts need LLM analysis, I do it during the conversation, not via API. Implemented Option A: During conversation-end, I extract lessons FIRST (before script runs), then proceed with normal workflow. No API keys, no external calls - just me doing the work directly.


**Example from lesson extraction (2025-10-12):**
- Thread: con_JB5UD88QWtAkoaXF
- Issue: Instead of updating architectural principles ad-hoc during conversations, capture lessons to pending storage for weekly batch review. Review session allows approve/edit/reject with principle updates only for approved lessons. Archive approved, discard rejected, keep pending for next time.
- Context: Making same mistakes repeatedly because lessons weren't formally captured and integrated into principles. Needed systematic way to learn from experience and update decision-making frameworks.
- Resolution: Built complete workflow: auto-extract on conversation-end → pending/ storage → Sunday evening review → update principles → archive. Scheduled task reminds weekly. Takes 15-30 min/week. Enables continuous improvement without disrupting conversations.

---

## 17) Test with Production Configuration

**Purpose:** Ensure real-world validity

**Rules:**
- Always test with the actual runtime environment, models, and tools.
- If production uses gpt-5-mini, don't test with Claude and assume it works.
- Validate that automated tasks use the exact same code paths as manual execution.

**When to apply:**
- Automation development
- Workflow testing
- System validation
- Before deployment

**Anti-patterns:**
- Testing with one model, deploying with another, claiming it works
- Using different code paths for test vs. production
- Skipping production validation because "it worked in dev"

**Example from meeting digest model inconsistency (2025-10-12):**
- Tested with Claude in interactive mode
- Deployed with gpt-5-mini in scheduled task
- Results differed; needed production testing
