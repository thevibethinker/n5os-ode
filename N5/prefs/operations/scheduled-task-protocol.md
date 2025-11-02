# Scheduled Task Protocol

**Module:** Operations  
**Version:** 1.0.0  
**Date:** 2025-10-13

---

## Purpose

Standardize creation, documentation, and maintenance of scheduled tasks to ensure consistency, reliability, and adherence to system principles.

**References:**
- `file 'N5/prefs/system/safety.md'` — Safety requirements
- `file 'N5/prefs/operations/digest-creation-protocol.md'` — Digest integration
- `file 'N5/prefs/operations/scheduling.md'` — Scheduling configuration
- `file 'Knowledge/architectural/architectural_principles.md'` — Design principles

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

**IMPORTANT:** All scheduled task naming follows centralized conventions.

**Source of Truth:** `file 'N5/prefs/naming-conventions.md'` (Section: Scheduled Task Naming)  
**Emoji Legend:** `file 'N5/config/emoji-legend.json'` (machine-readable)  
**Emoji Docs:** `file 'N5/prefs/emoji-legend.md'` (human-readable)

### Title Format

```
{emoji} {Action} {Subject}
```

**Emoji Selection (from centralized legend):**
- 📰 Digests and reports
- 💾 Data collection/sync
- 🔧 Maintenance operations
- 📊 Analytics/metrics
- 🚨 Alerts/monitoring
- 📝 Documentation updates
- 🎯 Strategic/planning tasks
- ⚡ Urgent/time-sensitive tasks

**Action Verb:**
- Clear, specific action (not generic "check" or "review")
- Examples: Generate, Pull, Validate, Analyze, Alert

**Subject:**
- Noun-first principle (consistent with thread naming)
- What is being acted upon

**Examples:**
- ✅ `📰 Daily Meeting Prep Digest` (report generation)
- ✅ `💾 Gdrive Meeting Pull` (data collection)
- ✅ `🔧 Weekly List Health Check` (maintenance)
- ✅ `📊 Monthly System Audit` (analytics)
- ❌ `meeting-monitor-cycle` (no emoji, unclear purpose)
- ❌ `Scheduled Maintenance: Solution Proposal Generation` (verbose, inconsistent)

**Guidelines:**
- Follow centralized emoji selection from `file 'N5/config/emoji-legend.json'`
- Use action verb + clear subject
- No frequency in title (RRULE defines timing)
- Consistent with universal naming principles

**For full naming standards, see:** `file 'N5/prefs/naming-conventions.md'`

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
- file '[path/to/command.md]'
- file '[path/to/script.py]'
```

### Guidelines

**DO:**
- Lead with clear purpose (one sentence)
- Reference existing commands via `file 'N5/commands/[name].md'`
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
Daily at 6am ET:        FREQ=DAILY;BYHOUR=6;BYMINUTE=0
Weekly Sunday 8pm ET:   FREQ=WEEKLY;BYDAY=SU;BYHOUR=20;BYMINUTE=0
Every 30 minutes:       FREQ=MINUTELY;INTERVAL=30
Monthly 1st at 8pm ET:  FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=20;BYMINUTE=0
Mon/Wed/Fri 2:30pm ET:  FREQ=WEEKLY;BYDAY=MO,WE,FR;BYHOUR=14;BYMINUTE=30
```

**Guidelines:**
- Always use user timezone (ET) for human-friendly times
- System converts to UTC automatically
- Validate RRULE before deployment
- Document next expected run in task notes

---

## Model Selection

### Current Standards

**Mini (gpt-5-mini):** Use for routine, well-defined operations
- File integrity checks
- List health validation
- Data collection/sync
- Simple digest delivery

**Full (gpt-5):** Use for complex reasoning, decision-making
- Strategic analysis
- Content generation requiring creativity
- Multi-step workflows with branching logic
- Digest creation (preparation, not delivery)

**Sonnet 4:** Reserved for specialized tasks requiring highest capability
- Complex NLP/reasoning
- User explicitly requests premium model

**Guidelines:**
- Default to mini for straightforward automation
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
- [ ] Confirm timezone interpretation (ET vs UTC)
- [ ] Review instruction for typos and ambiguities

**Phase 3: First Run Monitoring**
- [ ] Monitor first execution for errors
- [ ] Verify success criteria met
- [ ] Check logs for warnings or unexpected behavior
- [ ] Validate delivery method (email/SMS if configured)

**Phase 4: Post-Deployment**
- [ ] Document task in N5/docs or relevant location
- [ ] Add to task inventory (if maintained)
- [ ] Set calendar reminder for first review (1 week)
- [ ] Note any adjustments needed for future iterations

---

## Safety Requirements

### Mandatory Pre-Creation Steps

**1. User Consent (P11: Failure Modes)**
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
- Scheduled tasks execute via Zo's LLM (you)
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
- Use ASSUMPTIONS.md for complex dependencies

---

## Integration Standards

### Digest Creation Protocol

Scheduled tasks that generate digests must comply with `file 'N5/prefs/operations/digest-creation-protocol.md'`:

**Digest Generation Tasks:**
- Use dedicated generation task (e.g., "📰 Daily Meeting Prep Digest")
- Save to `N5/digests/[name]-{date}.md`
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
Execute: python3 -c "import os; files = os.listdir('/home/workspace/Lists'); print(files)"

✅ GOOD:
Execute command 'list-health-check' from file 'N5/commands/list-health-check.md'.
```

**Command Invocation Pattern:**
```markdown
Execute command '[command-name]' from file 'N5/commands/[command-name].md'.

[Additional context-specific parameters if needed]
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
    "Dependencies: Google Calendar API, N5 digest protocol",
    "Output: N5/digests/daily-meeting-prep-YYYY-MM-DD.md",
    "Monitor: Email delivery confirmation, file creation",
    "Owner: System-managed, user reviews weekly",
    "Related: file 'N5/commands/meeting-prep-digest.md'"
  ]
}
```

### Registry System

**Maintain Scheduled Task Inventory:**
- Location: `N5/config/scheduled_tasks.jsonl`
- Schema: See `file 'N5/schemas/scheduled_task.schema.json'`
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

**Output:** Report to `N5/logs/scheduled_task_audit.md`

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
Task 1: "💾 Gdrive Meeting Pull" (every 30 min)
  → Collects transcripts, deduplicates, queues for processing

Task 2: "📊 Meeting Insights Weekly" (Sunday 8pm)
  → Analyzes queued transcripts, generates summary
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
Task 1: "🔧 Weekly List Health Check" (Monday 3am)
  → Validates schemas, detects stale items, logs results

Task 2: "🚨 List Health Alert" (Monday 9am, conditional)
  → Send email only if critical issues found
```

---

## Troubleshooting Guide

### Task Not Running

**Check:**
1. Verify next_run timestamp: `list_scheduled_tasks`
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
4. Review model selection (mini vs. full capability)
5. Validate success criteria still appropriate

### Task Spamming Errors

**Immediate Actions:**
1. Disable task via `delete_scheduled_task`
2. Review error logs to identify root cause
3. Fix underlying issue (script, command, API)
4. Test manually before re-enabling
5. Consider adding retry backoff or error threshold

---

## Version History

### v1.0.0 — 2025-10-13
- Initial protocol creation
- Integrated safety requirements (P11, P16, P19)
- Linked digest creation protocol
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
**Owner:** System architecture (via Operator switching to Vibe Builder persona)  
**Change Process:** Follow `file 'N5/commands/system-design-workflow.md'`

---

*Protocol effective immediately for all new scheduled task creation.*
