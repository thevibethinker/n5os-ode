# Scheduled Task Examples

**Purpose:** Example automated tasks using N5OS Lite workflows  
**Platform:** Zo Computer scheduled tasks (or similar automation platform)  
**Version:** 1.0

---

## Overview

Scheduled tasks automate recurring workflows using RRULE syntax and N5OS Lite prompts. These examples demonstrate common automation patterns.

## Task Structure

```yaml
rrule: "FREQ=DAILY;BYHOUR=9;BYMINUTE=0"  # When to run
instruction: |                             # What to execute
  Clear, actionable instruction referencing
  prompts, scripts, and specific files.
```

---

## Example 1: Daily Workspace Cleanup

**Schedule:** Every day at 7 AM

```yaml
rrule: "FREQ=DAILY;BYHOUR=7;BYMINUTE=0"
instruction: |
  Run daily workspace cleanup:
  
  1. Check Inbox/ for files older than 7 days
  2. Categorize and route to appropriate directories
  3. Archive completed work from last week
  4. Generate cleanup summary
  
  Report: Files moved, archived, and remaining in Inbox
```

**Uses:**
- File system awareness
- Automated filing
- Periodic maintenance

---

## Example 2: Weekly List Health Check

**Schedule:** Every Monday at 9 AM

```yaml
rrule: "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0"
instruction: |
  Run weekly list health check:
  
  1. Validate all .jsonl files in Lists/
     - Run: python3 scripts/validate_list.py Lists/*.jsonl
  
  2. Check for stale items (>30 days with no update)
  
  3. Identify duplicates
  
  4. Generate health report
  
  Email report if issues found.
```

**Uses:**
- List validation script
- Quality monitoring
- Automated reporting

---

## Example 3: Monthly Knowledge Review

**Schedule:** First day of month at 10 AM

```yaml
rrule: "FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=10;BYMINUTE=0"
instruction: |
  Monthly knowledge base review:
  
  1. List all files in Knowledge/ modified in past month
  
  2. Check for:
     - Missing cross-references
     - Outdated information
     - Low-confidence items needing validation
  
  3. Generate review digest:
     - New knowledge added
     - Items needing attention
     - Suggested consolidations
  
  Email digest for review.
```

**Uses:**
- Knowledge maintenance
- Quality monitoring
- Periodic review

---

## Example 4: Daily Meeting Prep

**Schedule:** Every weekday at 8 AM

```yaml
rrule: "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=8;BYMINUTE=0"
instruction: |
  Generate today's meeting prep:
  
  1. Check calendar for today's meetings
     (Requires calendar integration)
  
  2. For each meeting:
     - Find related knowledge files
     - Pull recent conversation notes
     - Identify action items from Lists/
  
  3. Generate prep digest with:
     - Meeting context
     - Key discussion points
     - Action item status
  
  Save to: Documents/meeting-prep-{date}.md
  Email prep digest.
```

**Uses:**
- Calendar integration
- Knowledge retrieval
- List querying
- Automated prep

---

## Example 5: Weekly Project Summary

**Schedule:** Every Friday at 5 PM

```yaml
rrule: "FREQ=WEEKLY;BYDAY=FR;BYHOUR=17;BYMINUTE=0"
instruction: |
  Generate weekly project summary:
  
  1. Load planning prompt (Prompts/planning_prompt.md)
  
  2. Review this week's work:
     - Closed conversations (check Archives/)
     - Completed action items (Lists/action-items.jsonl)
     - New knowledge added (Knowledge/ git log)
  
  3. Generate summary:
     - Accomplishments
     - Blockers identified
     - Next week priorities
  
  4. Apply P15: Report actual completion (X/Y done, Z%)
  
  Save to: Documents/weekly-summary-{date}.md
  Email summary.
```

**Uses:**
- Planning prompt
- Progress tracking (P15)
- Automated reporting
- Git integration

---

## Example 6: Bi-Weekly Principle Review

**Schedule:** Every other Monday at 9 AM

```yaml
rrule: "FREQ=WEEKLY;INTERVAL=2;BYDAY=MO;BYHOUR=9;BYMINUTE=0"
instruction: |
  Bi-weekly principle compliance review:
  
  1. Review recent work for principle violations:
     - P15: Progress reporting accuracy
     - P7: Dry-run usage
     - P16: Accuracy over speculation
  
  2. Check conversation archives for patterns:
     - Are principles being referenced?
     - Are violations being caught?
     - Are quality bars maintained?
  
  3. Generate compliance report:
     - Adherence rate
     - Common violations
     - Improvement areas
  
  Email report with specific examples.
```

**Uses:**
- Quality monitoring
- Principle enforcement
- Process improvement

---

## Example 7: Daily File Protection Check

**Schedule:** Every day at midnight

```yaml
rrule: "FREQ=DAILY;BYHOUR=0;BYMINUTE=0"
instruction: |
  Daily file protection audit:
  
  1. List all protected directories:
     python3 scripts/file_guard.py list
  
  2. Verify .protected files are intact
  
  3. Check for unprotected critical directories:
     - N5/
     - Lists/
     - Knowledge/
  
  4. Alert if protections missing or modified
  
  Log results to: N5/logs/protection-audit-{date}.log
```

**Uses:**
- File protection system
- Security monitoring
- Automated auditing

---

## RRULE Syntax Reference

**Common Patterns:**

```
Daily at 9 AM:
FREQ=DAILY;BYHOUR=9;BYMINUTE=0

Weekdays at 2 PM:
FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=14;BYMINUTE=0

Weekly on Monday at 10 AM:
FREQ=WEEKLY;BYDAY=MO;BYHOUR=10;BYMINUTE=0

First of month at 9 AM:
FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=9;BYMINUTE=0

Every 30 minutes:
FREQ=MINUTELY;INTERVAL=30

One-time at 2 PM:
FREQ=DAILY;BYHOUR=14;BYMINUTE=0;COUNT=1
```

---

## Best Practices

1. **Clear Instructions**
   - Step-by-step workflow
   - Reference specific prompts/scripts
   - Define success criteria

2. **Error Handling**
   - What to do if something fails
   - Where to log errors
   - When to alert vs. silent fail

3. **Reporting**
   - Always report what was done
   - Include metrics (X/Y completed)
   - Attach relevant artifacts

4. **Time Zones**
   - Specify times in your local timezone
   - Platform handles conversion

5. **Dependencies**
   - List required files/scripts
   - Note any integrations needed
   - Test in isolation first

---

## Testing Tasks

**Before scheduling:**
1. Run instruction manually
2. Verify all files/scripts exist
3. Check output is correct
4. Test error paths
5. Confirm reporting works

**After scheduling:**
1. Monitor first few runs
2. Check logs for errors
3. Validate output quality
4. Refine instruction as needed

---

## Common Pitfalls

**Avoid:**
- ❌ Vague instructions ("check things")
- ❌ Missing file paths
- ❌ No error handling
- ❌ No reporting
- ❌ Untested workflows

**Instead:**
- ✅ Specific, actionable steps
- ✅ Explicit file references
- ✅ Clear error protocols
- ✅ Always report results
- ✅ Test before scheduling

---

## Related

- System: `scheduled-task-protocol.md` (if exists)
- Prompts: All workflow prompts can be automated
- Scripts: Validation and utility scripts
- Principles: P15 (progress reporting)

---

**Automation amplifies good workflows and bad ones equally. Design carefully.**

*Last Updated: 2025-11-03*
