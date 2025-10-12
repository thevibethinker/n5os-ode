# Lessons System - Quick Start Guide

**Version:** 1.0  
**Date:** 2025-10-12

---

## What Is This?

An automated system that captures lessons learned from your conversations and uses them to continuously improve your architectural principles.

**Flow:** Conversation → Extract lessons → Weekly review → Update principles → Better future decisions

---

## How It Works (Automatic)

### 1. During Conversation End

When you close a conversation with `conversation-end`:

```
Phase -1: Lesson Extraction (automatic)
├── Checks if thread is significant
│   ├── Errors/troubleshooting?
│   ├── System changes?
│   └── Novel techniques?
├── If YES: Extracts lessons → saves to pending/
└── If NO: Skips extraction
```

**You don't need to do anything** - this happens automatically.

---

### 2. Sunday Evenings (19:00)

Scheduled task runs weekly lesson review:

```
1. Loads all pending lessons
2. Sends you email notification
3. You review and approve/edit/reject each lesson
4. Approved lessons update architectural principles
5. Archived for future reference
```

**You'll receive an email** reminder to run the review.

---

## Manual Commands

### Review Pending Lessons

```bash
# Interactive review
python3 /home/workspace/N5/scripts/n5_lessons_review.py

# Preview only (dry-run)
python3 /home/workspace/N5/scripts/n5_lessons_review.py --dry-run

# Auto-approve all (use carefully!)
python3 /home/workspace/N5/scripts/n5_lessons_review.py --auto-approve
```

---

### Create Test Lesson

```bash
# Create a test lesson for current thread
python3 /home/workspace/N5/scripts/test_lessons_system.py
```

---

### Force Extract from Thread

```bash
# Extract even if not significant
python3 /home/workspace/N5/scripts/n5_lessons_extract.py --force
```

---

## Review Interface

When reviewing, you'll see:

```
======================================================================
LESSON 1 of 3
======================================================================
Thread: con_ABC123
Date: 2025-10-12
Type: troubleshooting

Title: Fix file write verification by checking size and structure

Description:
  When writing state files, only checking exists() missed truncated writes

Context:
  Files written but truncated due to process interruption

Outcome:
  Added exists() + size > 0 + valid JSON checks. Caught 2 partial writes.

Principle Refs: [18]
Tags: state-verification, file-io, error-handling

----------------------------------------------------------------------
[A]pprove  [E]dit  [R]eject  [S]kip  [Q]uit
>
```

**Actions:**
- **A**pprove → Updates principles, archives lesson
- **E**dit → Modify fields, then approve/reject
- **R**eject → Discards permanently (with confirmation)
- **S**kip → Keep in pending for next week
- **Q**uit → Exit and save progress

---

## File Locations

### Pending Lessons (awaiting review)
```
N5/lessons/pending/YYYY-MM-DD_con_XXXXX.lessons.jsonl
```

### Archived Lessons (permanent)
```
N5/lessons/archive/YYYY-MM_con_XXXXX.lessons.jsonl
```

### Architectural Principles (updated by approved lessons)
```
Knowledge/architectural/principles/
├── core.md
├── safety.md
├── quality.md
├── design.md
└── operations.md
```

---

## Typical Weekly Workflow

**Sunday evening (19:00):**

1. **Receive email:** "You have N pending lessons to review"

2. **Run review command:**
   ```bash
   python3 /home/workspace/N5/scripts/n5_lessons_review.py
   ```

3. **Review each lesson:**
   - Read title, description, context, outcome
   - Approve if valuable
   - Edit if needs refinement
   - Reject if not useful
   - Skip if unsure

4. **Commit updates:**
   ```bash
   cd /home/workspace
   git add Knowledge/architectural/principles/
   git commit -m "Update principles with weekly lessons"
   ```

**Time:** 15-30 minutes per week

---

## What Gets Extracted?

### Significance Criteria

Lessons are extracted when thread contains:

✅ **Errors or exceptions** - What went wrong and how we fixed it  
✅ **Troubleshooting sequences** - Problem-solving approaches that worked  
✅ **System changes** - Design decisions and implementations  
✅ **Novel techniques** - Creative or unusual approaches  
✅ **Multiple iterations** - Signs of trial-and-error learning  
✅ **Design documents** - Planning artifacts indicating architecture work

---

## Lesson Types

1. **Technique** - Specific method or approach used
2. **Strategy** - Higher-level decision-making pattern
3. **Design Pattern** - Architectural or structural pattern
4. **Troubleshooting** - Problem-solving approach that worked
5. **Anti-pattern** - Mistake or approach that failed

---

## Tips & Best Practices

### During Review

- **Be selective** - Quality over quantity
- **Edit vague lessons** - Make them specific and actionable
- **Fix wrong principle refs** - Ensure they map correctly
- **Reject noise** - Not every action is a lesson
- **Skip if unsure** - You can review again next week

### For Better Extraction

- **Document decisions** - Note why you chose an approach
- **Capture errors** - Include error messages and resolutions
- **Create design docs** - Implementation plans signal significance
- **Note workarounds** - Creative solutions are valuable lessons

### Maintenance

- **Commit regularly** - Principle updates should be version controlled
- **Review monthly** - Look at archived lessons for patterns
- **Clean old pending** - If lessons sit >30 days, they're probably not valuable

---

## Troubleshooting

### "No pending lessons found"

- Threads may not have been significant (no errors, changes, etc.)
- Check `N5/lessons/pending/` directory
- Create test lesson with `test_lessons_system.py`

### "Principle update failed"

- Check principle number is valid (0-20)
- Verify principle module file exists
- Check file permissions

### "Extraction not running"

- Verify `conversation-end` command works
- Check conversation workspace exists
- Run extraction manually with `--force` flag

---

## Advanced

### Manual Lesson Creation

Create a JSONL file in `N5/lessons/pending/`:

```json
{
  "lesson_id": "generated-uuid",
  "thread_id": "con_ABC123",
  "timestamp": "2025-10-12T18:00:00Z",
  "type": "technique",
  "title": "Your lesson title",
  "description": "What happened",
  "context": "Why it happened",
  "outcome": "Result",
  "principle_refs": ["15", "18"],
  "tags": ["tag1", "tag2"],
  "status": "pending"
}
```

### Export Lessons

```bash
# All lessons
cat N5/lessons/archive/*.jsonl

# Specific month
cat N5/lessons/archive/2025-10*.jsonl

# Count by type
jq -r '.type' N5/lessons/archive/*.jsonl | sort | uniq -c
```

---

## Questions?

- **Documentation:** file 'N5/lessons/README.md'
- **Command reference:** file 'N5/commands/lessons-review.md'
- **Schema:** file 'N5/lessons/schemas/lesson.schema.json'
- **Scripts:** file 'N5/scripts/n5_lessons_*.py'

---

**Next scheduled review:** Sunday 19:00  
**Pending lessons:** Check `N5/lessons/pending/`
