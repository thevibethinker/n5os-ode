---
description: 'Command: lessons-review'
tags:
- lessons
- review
- principles
- learning
---
# Lessons Review

**Purpose:** Batch review pending lessons from conversation threads and update architectural principles

**When to use:** Weekly (Sunday evenings, scheduled) or on-demand

**Duration:** 15-30 minutes depending on lesson count

---

## Quick Start

```bash
# Run interactive review
python3 /home/workspace/N5/scripts/n5_lessons_review.py

# Dry-run (preview only)
python3 /home/workspace/N5/scripts/n5_lessons_review.py --dry-run

# Auto-approve all (use with caution)
python3 /home/workspace/N5/scripts/n5_lessons_review.py --auto-approve
```

---

## What It Does

1. **Loads pending lessons** from `N5/lessons/pending/`
2. **Presents each lesson** for review with context
3. **Allows editing** of title, description, tags, principle refs
4. **Approve/Reject** decisions
5. **Updates principles** with approved lessons
6. **Archives** approved lessons to `N5/lessons/archive/`
7. **Discards** rejected lessons

---

## Review Interface

For each lesson, you'll see:

```
================================================================================
LESSON 1 of 5
================================================================================
Thread: con_ABC123
Date: 2025-10-12
Type: troubleshooting

Title: Fix file write verification by checking size and structure

Description:
When writing state files, we initially only checked if file.exists().
This missed truncated writes. Added size > 0 check and JSON structure
validation to catch partial writes.

Context:
Thread export v2.2 implementation - files were being written but truncated
due to process interruption.

Outcome:
Now verify: exists() + size > 0 + valid JSON. Caught 2 partial writes
during testing that would have corrupted state.

Principle Refs: [18] (State Verification is Mandatory)
Tags: state-verification, file-io, error-handling

────────────────────────────────────────────────────────────────────────────
[A]pprove  [E]dit  [R]eject  [S]kip  [Q]uit
>
```

---

## Actions

### Approve (A)
- Adds lesson as example to referenced principle(s)
- If no matching principle, prompts to create new one
- Archives lesson to `N5/lessons/archive/`
- Updates principle change log

### Edit (E)
- Modify any field before approving
- Interactive prompts for each field
- Returns to approval screen after editing

### Reject (R)
- Discards lesson permanently
- Requires confirmation
- Logs rejection reason

### Skip (S)
- Leaves lesson in pending for next review
- Useful if you need more context

### Quit (Q)
- Saves progress and exits
- Pending lessons remain for next session

---

## Principle Update Logic

When a lesson is approved:

1. **Find matching principle(s)** from `principle_refs`
2. **Load principle module** (e.g., `principles/quality.md`)
3. **Append as example** to relevant principle section
4. **Update change log** in module
5. **If no match**: Prompt to create new principle

**Example update to Principle 18 (State Verification):**

```markdown
## 18) State Verification is Mandatory

[... existing content ...]

**Example from lesson extraction (2025-10-12):**
- Thread: con_ABC123
- Issue: File writes succeeded but produced truncated files
- Solution: Added triple verification: exists() + size > 0 + valid structure
- Outcome: Caught 2 partial writes during testing
```

---

## Scheduled Task

**Frequency:** Weekly, Sunday 19:00 (7pm)

**Configuration:**
```
RRULE: FREQ=WEEKLY;BYDAY=SU;BYHOUR=19;BYMINUTE=0
Instruction: Review pending lessons and update architectural principles
```

**Automation:**
- Loads all pending lessons
- Sends summary email with lesson count
- Interactive review via email response (future enhancement)
- For now: Manual review when email received

---

## File Structure

**Pending lessons:**
```
N5/lessons/pending/
└── 2025-10-12_con_ABC123.lessons.jsonl
```

**Archived lessons:**
```
N5/lessons/archive/
└── 2025-10_con_ABC123.lessons.jsonl
```

**Organized by month for easier browsing**

---

## Tips

### Weekly Review Workflow
1. Check email Sunday evening for lesson summary
2. Run `lessons-review` command
3. Batch review all pending lessons (15-30 min)
4. Commit principle updates to git
5. Done until next week

### Quality Control
- If a lesson is vague, edit it before approving
- If principle ref is wrong, fix it during edit
- If lesson doesn't add value, reject it
- If you're unsure, skip for next week

### Creating New Principles
- When no existing principle fits
- Review index to ensure no overlap
- Assign next available number
- Follow module structure pattern
- Add to appropriate module file

---

## Related Commands

- `lessons-export` - Export lessons by date/tag
- `conversation-end` - Auto-extracts lessons from threads
- `thread-export` - Can include extracted lessons

---

## Error Handling

**If principle file locked:**
- Skip that lesson, continue with others
- Retry on next review

**If archive write fails:**
- Keeps lesson in pending
- Logs error for investigation

**If review is interrupted:**
- Progress saved
- Resume from where you left off

---

**Version:** 1.0  
**Last Updated:** 2025-10-12  
**Status:** Active
