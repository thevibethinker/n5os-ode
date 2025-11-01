---
type: "recipe"
category: "automation"
version: "1.0.0"
created: "2025-10-30"
modified: "2025-10-30"
status: "draft"
owner: "zo"
tool: true
---
# `add-digest`

Create a new daily digest system with guided implementation workflow.

**Version:** 1.0.0  
**Updated:** 2025-10-13

---

## Usage

```bash
# Interactive: Describe digest and get guided implementation
add-digest

# With description upfront
add-digest --description "Daily digest of X that does Y"

# Skip to specific phase (after initial creation)
add-digest --digest-name newsletter-v2 --phase 4
```

---

## Description

`add-digest` is a meta-command that guides you through creating a new daily digest type following the N5 digest creation protocol. It handles the entire lifecycle from design through testing and deployment.

**What it does:**

1. **Discovery Phase** — Clarifies purpose, data sources, format, frequency
2. **Design Phase** — Creates structured design document
3. **Implementation Phase** — Generates Python script from template
4. **Documentation Phase** — Creates command documentation
5. **Integration Phase** — Sets up scheduling and command registration
6. **Testing Phase** — Validates functionality end-to-end
7. **Deployment Phase** — Activates scheduled tasks and completes handoff

**Key Features:**
- ✅ Follows `file 'N5/prefs/operations/digest-creation-protocol.md'`
- ✅ Enforces architectural principles (P5, P7, P11, P15-21)
- ✅ Generates production-ready code with error handling
- ✅ Creates complete documentation
- ✅ Validates with fresh thread tests
- ✅ Ensures state verification

---

## Workflow

### Phase 0: Discovery (Interactive)

**Goal:** Gather requirements and clarify design.

**Questions Asked:**
1. **Purpose:** What does this digest do? (1 sentence)
2. **Data Sources:** Where does data come from?
   - Gmail (queries/filters)
   - Google Calendar (event types/tags)
   - Web research (sites/topics)
   - Local files (Knowledge, Lists, Records)
   - External APIs (which services)
3. **Output Format:** How is information presented?
   - Sections and structure
   - Tables, bullets, prose
   - BLUF format? Citations?
4. **Exclusions:** What should NOT appear?
5. **Output Location:** Where does file save?
   - `N5/digests/` (meeting/calendar-related)
   - `N5/knowledge/digests/` (research/content-related)
   - Custom location
6. **Frequency:** When does it run?
   - Daily (time?)
   - Weekdays only?
   - Weekly?
7. **Delivery:** How is it delivered?
   - File only
   - Email (subject format)
   - SMS
   - Multiple channels
8. **Success Criteria:** How do we know it's working?

**Output:** Design document saved to conversation workspace.

---

### Phase 1: Design Validation

**Goal:** Review and approve design before implementation.

**Actions:**
1. Present structured design document
2. Check for similar existing digests
3. Identify reusable components
4. Verify output location doesn't conflict
5. Load architectural principles
6. Define "complete" explicitly

**Checkpoints:**
- [ ] Purpose clear and specific
- [ ] Data sources accessible and well-defined
- [ ] Output format detailed
- [ ] Location won't conflict with existing files
- [ ] Success criteria measurable
- [ ] User approves design

**Output:** Approved design document.

---

### Phase 2: Script Generation

**Goal:** Create production-ready Python script.

**Actions:**
1. Generate script from protocol template
2. Customize for specific data sources
3. Implement filtering/exclusion logic
4. Add markdown generation
5. Include error handling
6. Add state verification
7. Implement dry-run mode

**Script Location:** `file 'N5/scripts/[digest_name].py'`

**Script Includes:**
- ✅ Argument parsing (`--date`, `--dry-run`)
- ✅ Logging with timestamps
- ✅ Input validation
- ✅ Data fetching with error handling
- ✅ Processing and filtering logic
- ✅ Markdown generation
- ✅ File save with verification
- ✅ Exit codes (0=success, 1=failure)
- ✅ Type hints and docstrings

**Checkpoints:**
- [ ] Script generated
- [ ] Made executable (`chmod +x`)
- [ ] Dry-run mode works
- [ ] Production test creates valid file
- [ ] Error handling tested
- [ ] State verification works

---

### Phase 3: Command Documentation

**Goal:** Create comprehensive command documentation.

**Actions:**
1. Generate command doc from protocol template
2. Document usage patterns
3. Describe data sources and logic
4. Provide examples
5. Include troubleshooting guide
6. Add scheduling recommendations

**Doc Location:** `file 'N5/commands/[digest-name].md'`

**Sections:**
- Usage examples
- Detailed description
- Data sources
- Output format
- Scheduling recommendations
- Troubleshooting
- Implementation references
- Change log

**Checkpoints:**
- [ ] Documentation complete
- [ ] Examples accurate
- [ ] Troubleshooting covers common issues
- [ ] References correct

---

### Phase 4: Integration

**Goal:** Register command and set up scheduling.

**Actions:**
1. (Optional) Add to `commands.jsonl`
2. (Optional) Run `docgen` to update catalog
3. Create scheduled task(s)
4. Verify task registration
5. Test manual execution

**Scheduled Task Pattern:**

**Two-task approach** (generation + delivery):
```python
# Task 1: Generate digest (10:00 AM)
{
    "rrule": "FREQ=DAILY;BYHOUR=10;BYMINUTE=0",
    "instruction": "Execute [digest-name] command or run /home/workspace/N5/scripts/[digest_name].py",
    "delivery_method": None
}

# Task 2: Email delivery (10:30 AM)
{
    "rrule": "FREQ=DAILY;BYHOUR=10;BYMINUTE=30",
    "instruction": "Read digest at file 'N5/[location]/[pattern]-{today}.md' and email with subject '[Subject]'",
    "delivery_method": "email"
}
```

**Single-task approach** (generation with auto-email):
```python
{
    "rrule": "FREQ=DAILY;BYHOUR=10;BYMINUTE=0",
    "instruction": "Execute [digest-name] command and email results",
    "delivery_method": "email"
}
```

**Checkpoints:**
- [ ] Command registered (if applicable)
- [ ] Scheduled task(s) created
- [ ] Next run time verified
- [ ] Manual execution works
- [ ] Scheduling confirmed with user

---

### Phase 5: Testing

**Goal:** Validate end-to-end functionality.

**Test Matrix:**

| Test Type | Command | Expected Result |
|-----------|---------|-----------------|
| Dry-run (today) | `[digest-name] --dry-run` | Preview without file |
| Dry-run (past) | `[digest-name] --date 2025-10-10 --dry-run` | Preview with past data |
| Production (past) | `[digest-name] --date 2025-10-10` | File created, valid |
| Production (today) | `[digest-name]` | File created, valid |
| Fresh thread | New conversation, run command | Works independently |
| Scheduled run | Wait for scheduled time | Task executes, file created |
| Email delivery | If enabled | Email arrives correctly |

**Verification Checks:**
- [ ] File exists at correct path
- [ ] File size > 0 bytes
- [ ] Valid markdown structure
- [ ] Content matches design spec
- [ ] Timestamp footer present
- [ ] All expected sections included
- [ ] Data sources queried correctly
- [ ] Filters/exclusions working
- [ ] Error cases handled gracefully

**Fresh Thread Test Protocol:**
1. Start new conversation
2. Load only protocol and command doc
3. Run: `[digest-name] --dry-run`
4. Run: `[digest-name] --date [past-date-with-data]`
5. Verify output matches expectations
6. Document any issues or dependencies

---

### Phase 6: Deployment & Handoff

**Goal:** Complete implementation and document for user.

**Actions:**
1. Update system documentation
2. Add to "Existing Digests" list in protocol
3. Create implementation summary
4. Archive design documents
5. Monitor first scheduled run
6. Gather user feedback

**Implementation Summary Template:**

```markdown
# [Digest Name] Implementation Complete

## Overview
[One-sentence description]

## Files Created
- **Script:** `file 'N5/scripts/[digest_name].py'`
- **Command Doc:** `file 'N5/commands/[digest-name].md'`
- **Output Location:** `N5/[location]/[pattern]-YYYY-MM-DD.md`

## Scheduled Tasks
- **Task ID:** [id from list_scheduled_tasks]
- **Schedule:** [description]
- **Next Run:** [timestamp]
- **Delivery:** [method]

## Testing Results
- [x] Dry-run: Passed
- [x] Production: Passed
- [x] Fresh thread: Passed
- [x] Scheduled task: Verified
- [x] Email delivery: [Tested/Not applicable]

## Usage
\`\`\`bash
# Generate today's digest
[digest-name]

# Generate for specific date
[digest-name] --date 2025-10-14

# Preview without saving
[digest-name] --dry-run
\`\`\`

## Data Sources
- [Source 1]: [description]
- [Source 2]: [description]

## Output Format
[Brief description of sections and structure]

## Monitoring
- First scheduled run: [date/time]
- Review after: [3-5 runs]
- Adjust filters if needed based on output quality

## Next Steps
- [ ] Monitor first week of scheduled runs
- [ ] Gather user feedback on content/format
- [ ] Adjust filters if too noisy/sparse
- [ ] Document any issues in command doc

---

**Status:** ✅ Deployed  
**Created:** [timestamp]  
**Implemented by:** Vibe Builder persona
```

**Checkpoints:**
- [ ] Summary document created
- [ ] System docs updated
- [ ] Protocol updated with new digest
- [ ] User notified of completion
- [ ] First run monitored
- [ ] Feedback loop established

---

## Examples

### Example 1: Weekly Summary Digest

```bash
User: "Create a digest that summarizes my week's meetings every Friday"

add-digest --description "Weekly meeting summary every Friday"

# Workflow:
# 1. Clarify: Which meetings? Format? Time?
# 2. Design: Scan N5/records/meetings for past week
# 3. Implement: Group by stakeholder type, extract key decisions
# 4. Document: Command doc with usage
# 5. Schedule: FREQ=WEEKLY;BYDAY=FR;BYHOUR=17;BYMINUTE=0
# 6. Test: Generate for past week, verify output
# 7. Deploy: Activate scheduled task, monitor first run
```

### Example 2: Morning News Briefing

```bash
User: "I want a daily briefing of news articles about AI and education"

add-digest

# Discovery questions:
Q: What does this digest do?
A: Curate daily news about AI in education

Q: Data sources?
A: Web research (specific news sites, RSS feeds)

Q: Output format?
A: Grouped by theme, 3 bullet takeaways per article, citations

Q: Exclusions?
A: Opinion pieces, paywalled content

Q: Output location?
A: N5/knowledge/digests/

Q: Frequency?
A: Daily at 6:00 AM ET

Q: Delivery?
A: Email with subject "AI in Education Daily — {date}"

Q: Success criteria?
A: 5-10 articles per day, diverse sources, actionable insights

# Then proceeds through phases 1-6
```

### Example 3: Sprint Summary (Bi-Weekly)

```bash
add-digest --description "Bi-weekly sprint summary from Careerspan meetings and tasks"

# Workflow customizes for:
# - Frequency: FREQ=WEEKLY;INTERVAL=2;BYDAY=FR;BYHOUR=16;BYMINUTE=0
# - Data sources: N5/records/meetings + Lists/tasks.jsonl
# - Output: Accomplishments, blockers, next sprint goals
# - Location: N5/digests/sprint-summary-YYYY-MM-DD.md
```

---

## Command Inputs

### Required
- `description` (text) — One-sentence description of digest purpose

### Optional
- `digest-name` (text) — Slug for files (auto-generated if not provided)
- `phase` (int: 0-6) — Resume at specific phase (default: 0)
- `interactive` (bool) — Use interactive mode (default: true)
- `dry-run` (bool) — Preview without creating files (default: false)

---

## Outputs

### Files Created
- Design document → Conversation workspace
- Script → `N5/scripts/[digest_name].py`
- Command doc → `N5/commands/[digest-name].md`
- Implementation summary → Conversation workspace
- First digest output → `N5/[location]/[pattern]-YYYY-MM-DD.md`

### System Changes
- (Optional) Command registered in `commands.jsonl`
- Scheduled task(s) created
- System documentation updated

---

## Failure Modes

### Discovery Phase
- **Issue:** Unclear requirements
- **Recovery:** Ask 3+ clarifying questions, provide examples

### Design Phase
- **Issue:** Output location conflicts with existing files
- **Recovery:** Propose alternative location or pattern

### Implementation Phase
- **Issue:** Data source unavailable or requires credentials
- **Recovery:** Document dependency, guide credential setup

### Testing Phase
- **Issue:** Fresh thread test fails due to missing context
- **Recovery:** Identify missing dependencies, update script/docs

### Deployment Phase
- **Issue:** Scheduled task fails on first run
- **Recovery:** Check logs, verify production config, re-test

---

## Architectural Principles Applied

**Core:**
- **P2 (SSOT):** Reference protocol as single source, don't duplicate

**Safety:**
- **P5 (Anti-Overwrite):** Check for conflicts before creating files
- **P7 (Dry-Run):** All digests must support `--dry-run` flag
- **P11 (Failure Modes):** Document recovery for common errors
- **P19 (Error Handling):** All scripts have try-catch with logging

**Quality:**
- **P1 (Human-Readable):** Markdown output, clear sections
- **P15 (Complete Before Claiming):** Define "complete" in Phase 1
- **P16 (Accuracy):** No invented limitations, cite real constraints
- **P18 (State Verification):** Always verify file writes succeeded
- **P21 (Document Assumptions):** Design doc captures all assumptions

**Design:**
- **P8 (Minimal Context):** Load only what's needed per phase
- **P20 (Modular):** Each phase can be run independently

**Operations:**
- **P12 (Fresh Thread Test):** Mandatory before deployment
- **P17 (Production Config):** Test with real APIs/credentials

---

## Related Components

**Protocol:** `file 'N5/prefs/operations/digest-creation-protocol.md'`

**Existing Digests:**
- `meeting-prep-digest` — Daily meeting intelligence
- Daily newsletter digest — Curated content briefing

**Related Commands:**
- `digest-runs` — Analyze digest execution history
- `docgen` — Update command catalog
- `system-upgrades-add` — Add enhancement requests

**Principles:** `file 'Knowledge/architectural/architectural_principles.md'`

---

## Troubleshooting

### Issue: Design phase keeps asking same questions

**Cause:** Requirements unclear or contradictory  
**Fix:** 
1. Pause and consolidate what you know
2. Ask user to prioritize unclear areas
3. Provide concrete examples to clarify

### Issue: Script generation fails

**Cause:** Complex data source without clear API  
**Fix:**
1. Break into simpler steps
2. Document manual data collection first
3. Automate incrementally

### Issue: Fresh thread test fails

**Cause:** Script depends on conversation-specific context  
**Fix:**
1. Identify hardcoded paths or assumptions
2. Make script self-contained
3. Add input validation
4. Document all external dependencies

### Issue: Scheduled task doesn't run

**Cause:** RRULE syntax error or timezone mismatch  
**Fix:**
1. Verify RRULE with online validator
2. Check timezone is correct (America/New_York)
3. Test manual execution first
4. Check scheduled task logs

### Issue: Digest output is empty or wrong

**Cause:** Data source query incorrect or date handling issue  
**Fix:**
1. Test data fetch separately
2. Log query results before processing
3. Verify date parsing (UTC vs local)
4. Check filters aren't too restrictive

---

## Change Log

### 1.0.0 (2025-10-13)
- Initial implementation
- Six-phase guided workflow
- Interactive discovery mode
- Automated script generation from template
- Fresh thread test enforcement
- Integration with scheduling system
- Based on digest creation protocol v1.0

---

## Implementation

**Protocol:** `file 'N5/prefs/operations/digest-creation-protocol.md'`  
**Principles:** `file 'Knowledge/architectural/architectural_principles.md'`  
**Script Template:** See protocol Phase 2.1  
**Persona:** Vibe Builder (system building specialist)

---

**Last Updated:** 2025-10-13  
**Maintained By:** Vibe Builder persona  
**Review Schedule:** Quarterly (after 3+ digests created)
