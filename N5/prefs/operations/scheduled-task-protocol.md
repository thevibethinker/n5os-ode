---
created: 2025-10-13
last_edited: 2026-03-15
version: 2.0
provenance: n5os-ode-export/D2.1
---

# Scheduled Task Protocol

**Module:** Operations
**Version:** 2.0

---

## Purpose

Standardize creation, documentation, and maintenance of scheduled tasks to ensure consistency, reliability, and adherence to system principles.

**References:**
- Safety requirements (your system's safety module)
- Digest creation protocol (if using digests)
- Scheduling configuration
- Architectural principles

---

## Core Principles

### P0: Minimal Context
Instructions must be self-contained but concise. Reference existing commands/scripts rather than inline complex logic.

### P15: Complete Before Claiming
Tasks must be fully tested before deployment. Never mark a task as "done" until verification complete.

### P18: Verify State
Every scheduled task must include explicit success criteria and verification steps.

### P19: Error Handling
All tasks must handle failure gracefully and log meaningful errors for debugging.

### P21: Document Assumptions
All dependencies, expected states, and edge cases must be explicitly documented.

---

## Task Naming Convention

### Title Format

```
{emoji} {Frequency?} {Subject/Action}
```

**Components:**

1. **Emoji** (Required) - Category indicator
   - 🔧 Maintenance/system operations
   - 🧠 Intelligence/strategic/analysis tasks
   - 📰 Digests/information gathering/content
   - 💾 Data collection/sync operations
   - 📊 Analytics/metrics/reporting
   - 📧 Email operations and monitoring
   - 📅 Meeting/calendar operations
   - 🎓 Learning/ML training tasks
   - 📝 Documentation/content writing
   - ⏰ Scheduled automation tasks

2. **Frequency** (Conditional) - Include when helpful for clarity
   - Daily, Weekly, Monthly for standard recurrence
   - "Every 2 Hours", "Every 6 Hours" for interval-based tasks
   - **Omit** for very frequent tasks (< 1 hour) - describe function instead
   - **Omit** when obvious from context or when task name is self-explanatory

3. **Subject/Action** - Clear, concise, noun-first description
   - 3-5 words maximum
   - Describe WHAT is being done, not HOW
   - Avoid redundant qualifiers ("Auto", "Automated", "System Check")
   - Use active, specific language

**Examples:**
- ✅ `🔧 Daily File Guardian` - Maintenance with clear frequency
- ✅ `📰 Daily Meeting Preparation Digest` - Digest with frequency
- ✅ `🧠 Monthly System Audit` - Intelligence task with clear cadence
- ✅ `📅 Meeting Pipeline Processing` - Frequent task (30min), no frequency in name
- ✅ `🎓 Weekly Lessons Review` - Learning task, concise
- ❌ `Productivity Tracker Auto-Scan` - Missing emoji, redundant "Auto-Scan"
- ❌ `Meeting Pipeline V2 Processing Completed` - Version number, awkward "Completed"
- ❌ `Automatic Conversation Initialization Check` - Missing emoji, verbose

**Guidelines:**
- Use action verb + clear subject
- No version numbers in titles
- No frequency in title when RRULE defines timing and cadence is obvious
- Consistent with universal naming principles

---

## Instruction Structure

### Template

```markdown
[One-sentence purpose statement]

**Prerequisites:**
- [Required state/files/dependencies]

**Execution:**
1. [Step 1: Specific, actionable]
2. [Step 2: Reference commands/scripts by path]
3. [Step 3: Output handling]

**Success Criteria:**
- [Measurable outcome 1]
- [Measurable outcome 2]

**Error Handling:**
- [What to do if X fails]
- [When to alert/email user]

**References:**
- [path/to/command.md]
- [path/to/script.py]
```

### Guidelines

**DO:**
- Lead with clear purpose (one sentence)
- Reference existing commands by path
- Specify exact script paths for execution
- Include explicit success criteria
- Define error conditions and responses
- Use bullet points and numbered lists
- Include timezone context when relevant

**DON'T:**
- Write inline code blocks (use scripts instead)
- Leave ambiguous verbs ("check", "review" → specify exactly how)
- Omit error handling
- Assume file existence without verification
- Use relative time references ("yesterday" → compute dynamically)
- Include placeholder TODOs or unimplemented logic

---

## Schedule Specification

### RRULE Format

Use RFC 5545 RRULE syntax without DTSTART (system handles timing):

**Common Patterns:**
```
Daily at 6am:           FREQ=DAILY;BYHOUR=6;BYMINUTE=0
Weekly Sunday 8pm:      FREQ=WEEKLY;BYDAY=SU;BYHOUR=20;BYMINUTE=0
Every 30 minutes:       FREQ=MINUTELY;INTERVAL=30
Monthly 1st at 8pm:     FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=20;BYMINUTE=0
Mon/Wed/Fri 2:30pm:     FREQ=WEEKLY;BYDAY=MO,WE,FR;BYHOUR=14;BYMINUTE=30
One-time on a date:     FREQ=DAILY;BYMONTH=11;BYMONTHDAY=5;BYHOUR=8;BYMINUTE=0;COUNT=1
```

**Guidelines:**
- Always use user timezone for human-friendly times
- System converts to UTC automatically
- Validate RRULE before deployment
- Document next expected run in task notes

---

## Model Selection

### Guidelines

**Lightweight model:** Use for routine, well-defined operations
- File integrity checks
- List health validation
- Data collection/sync
- Simple digest delivery

**Full model:** Use for complex reasoning, decision-making
- Strategic analysis
- Content generation requiring creativity
- Multi-step workflows with branching logic
- Digest creation (preparation, not delivery)

**Premium model:** Reserved for specialized tasks requiring highest capability
- Complex NLP/reasoning
- User explicitly requests premium model

**General Advice:**
- Default to lightweight for straightforward automation
- Upgrade to full when task requires judgment
- Document model choice rationale in notes
- Consider cost vs. capability trade-offs

---

## Testing Requirements

### Pre-Deployment Checklist

**Phase 1: Dry Run**
- [ ] Execute instruction manually in conversation
- [ ] Verify all file paths exist
- [ ] Confirm commands/scripts are registered and functional
- [ ] Test error conditions (missing files, API failures)
- [ ] Validate output format and location

**Phase 2: Scheduled Task Creation**
- [ ] Create task with `--dry-run` or test RRULE first
- [ ] Verify next_run timestamp is correct
- [ ] Confirm timezone interpretation
- [ ] Review instruction for typos and ambiguities

**Phase 3: First Run Monitoring**
- [ ] Monitor first execution for errors
- [ ] Verify success criteria met
- [ ] Check logs for warnings or unexpected behavior
- [ ] Validate delivery method (email/SMS if configured)

**Phase 4: Post-Deployment**
- [ ] Document task in relevant location
- [ ] Add to task inventory (if maintained)
- [ ] Set calendar reminder for first review (1 week)
- [ ] Note any adjustments needed for future iterations

---

## Safety Requirements

### Mandatory Pre-Creation Steps

**1. User Consent**
- Show proposed schedule in human-readable format
- Explain what will run and when
- Request explicit approval before creation
- Confirm timezone interpretation

**2. Impact Assessment**
- Identify destructive operations (deletes, overwrites, external sends)
- Require `--dry-run` for file operations
- Preview email/SMS content before auto-sending
- Consider rate limits and API quotas

**3. Rollback Plan**
- Document how to disable task quickly
- Identify monitoring signals for failure
- Define escalation path (log → email → SMS)
- Backup critical state before modifications

### Anti-Patterns (Critical Violations)

❌ **No External LLM Calls**
- Scheduled tasks execute via your system's LLM
- Never instruct task to "call external API for LLM"
- Distinction: Data APIs (Gmail, Calendar) are fine; LLM APIs are redundant

❌ **No Invented Limits (P16)**
- Don't claim "API limits to 3 messages" without docs
- Cite actual quota/rate limits or acknowledge uncertainty
- Test real limits before asserting constraints

❌ **No Premature Completion (P15)**
- Never claim task is "ready" until all phases tested
- Report progress as percentage: "Phase 2/4 complete (50%)"
- Final verification required before marking ✅

❌ **No Undocumented Placeholders (P21)**
- Never leave `# TODO` or `[IMPLEMENT LATER]` in instructions
- Document all assumptions in task notes

---

## Integration Standards

### Digest Creation Protocol

Scheduled tasks that generate digests should follow the digest creation protocol:

**Digest Generation Tasks:**
- Use dedicated generation task (e.g., "📰 Daily Meeting Prep Digest")
- Save to a canonical digests location (e.g., `digests/[name]-{date}.md`)
- Follow naming convention: `[topic]-YYYY-MM-DD.md`
- Include metadata header (date, sources, version)

**Digest Delivery Tasks:**
- Separate task reads pre-generated digest
- Subject line: "[Topic] — {date}" (readable format)
- Verify file exists before attempting to send
- Fail gracefully if digest missing (log, don't error)

**Sequencing:**
```
Generation Task → Writes file → Delivery Task → Reads file → Sends email
(10:00 AM)                      (10:30 AM)
```

### Command Integration

**Prefer Commands Over Inline Logic:**
```markdown
❌ BAD:
Execute: python3 -c "import os; files = os.listdir('/path'); print(files)"

✅ GOOD:
Execute command 'list-health-check' from your commands directory.
```

**When to Create Supporting Command:**
- Task logic >5 lines
- Reusable across multiple tasks
- Requires configuration management
- Benefits from version control and documentation

---

## Documentation Standards

### Task Notes Field

Every scheduled task should include structured notes:

```json
{
  "notes": [
    "Purpose: [One-sentence description]",
    "Dependencies: [Commands, files, APIs]",
    "Output: [Where results are saved]",
    "Monitor: [Key success metrics]",
    "Owner: [System/user responsibility]",
    "Related: [Links to commands, workflows, digests]"
  ]
}
```

**Example:**
```json
{
  "notes": [
    "Purpose: Generate and email daily meeting preparation digest",
    "Dependencies: Google Calendar API, digest protocol",
    "Output: digests/daily-meeting-prep-YYYY-MM-DD.md",
    "Monitor: Email delivery confirmation, file creation",
    "Owner: System-managed, user reviews weekly",
    "Related: commands/meeting-prep-digest.md"
  ]
}
```

### Registry System

**Maintain Scheduled Task Inventory:**
- Keep a central registry of all scheduled tasks (e.g., JSONL or JSON)
- Update on create/modify/delete operations
- Weekly review for stale or redundant tasks

---

## Maintenance Workflow

### Weekly Review (Automated)

Scheduled task: `🔧 Weekly Scheduled Task Audit`

**Checks:**
1. All tasks have run successfully in past 7 days
2. No tasks with error rate >10%
3. Email/SMS delivery working as expected
4. Task instructions still reference valid files/commands
5. No duplicate or redundant tasks

**Output:** Report to logs or audit file

### Monthly Deep Review (Manual)

**Questions to Ask:**
1. Are all tasks still necessary?
2. Can any tasks be consolidated?
3. Are schedules optimal (frequency, timing)?
4. Are models appropriately selected (cost vs. capability)?
5. Are instructions up-to-date with system changes?

**Action Items:**
- Archive obsolete tasks
- Refactor redundant logic into commands
- Update documentation for changed workflows
- Optimize resource usage (model, frequency)

---

## Common Patterns

### Pattern: Data Collection + Processing

**Structure:**
- **Task 1:** Pull data from external source (every N minutes/hours)
- **Task 2:** Process accumulated data (once daily at optimal time)

**Example:**
```
Task 1: "💾 Drive Document Pull" (every 30 min)
  → Collects new documents, deduplicates, queues for processing

Task 2: "📊 Weekly Document Insights" (Sunday 8pm)
  → Analyzes queued documents, generates summary
```

### Pattern: Generation + Delivery

**Structure:**
- **Task 1:** Generate content/report (early, allows prep time)
- **Task 2:** Deliver via email/SMS (later, user-friendly timing)

**Example:**
```
Task 1: "📰 Daily Meeting Prep Digest" (6am)
  → Fetches calendar, generates markdown digest

Task 2: "📧 Daily Meeting Prep Email" (10am)
  → Reads digest, sends email with formatted content
```

### Pattern: Maintenance + Notification

**Structure:**
- **Task 1:** Perform maintenance operation (off-peak hours)
- **Task 2:** Notify user of results only if action needed

**Example:**
```
Task 1: "🔧 Weekly Health Check" (Monday 3am)
  → Validates schemas, detects stale items, logs results

Task 2: "🚨 Health Alert" (Monday 9am, conditional)
  → Send email only if critical issues found
```

---

## Troubleshooting Guide

### Task Not Running

**Check:**
1. Verify next_run timestamp via task listing
2. Confirm task is not disabled
3. Check system time vs. expected timezone
4. Review logs for scheduler errors

### Task Running But Failing

**Check:**
1. Review execution logs for error messages
2. Verify all file paths and commands exist
3. Test instruction manually in conversation
4. Check API rate limits or authentication issues
5. Validate input data format hasn't changed

### Task Producing Wrong Output

**Check:**
1. Verify instruction matches current system state
2. Check for stale references to deprecated commands
3. Test with fresh data (not cached results)
4. Review model selection (lightweight vs. full capability)
5. Validate success criteria still appropriate

### Task Spamming Errors

**Immediate Actions:**
1. Disable task via delete or pause
2. Review error logs to identify root cause
3. Fix underlying issue (script, command, API)
4. Test manually before re-enabling
5. Consider adding retry backoff or error threshold

---

## Cornerstone Tasks

Tasks marked with ⇱ in their title are **cornerstone tasks** — critical infrastructure that should not be deleted without explicit confirmation. Before deleting or significantly editing a cornerstone task, always confirm with the user.

---

## Version History

### v2.0 — 2026-03-15
- Ported to n5os-ode as reusable protocol
- Generalized all examples
- Added cornerstone tasks section
- Removed system-specific file references

### v1.0.0 — 2025-10-13
- Initial protocol creation
- Integrated safety requirements
- Established naming and instruction standards
- Defined testing requirements
- Documented common patterns

---

## Meta

This protocol is a living document. Update based on:
- User feedback on task quality
- Emerging patterns from new scheduled tasks
- System changes affecting task execution
- Lessons learned from task failures

**Review Frequency:** Monthly (aligned with system audit)

---

*Protocol effective immediately for all new scheduled task creation.*
