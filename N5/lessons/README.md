# N5 Lessons System

**Purpose:** Automatically capture and review techniques, strategies, design patterns, and troubleshooting lessons from conversation threads to improve system principles.

---

## Directory Structure

```
N5/lessons/
├── pending/           # Lessons awaiting weekly review
├── archive/           # Approved lessons (permanent storage)
├── schemas/           # JSON schemas for validation
│   └── lesson.schema.json
└── README.md          # This file
```

---

## How It Works

### 1. Automatic Extraction

When a conversation ends (`conversation-end` command), the system:
- Analyzes the thread for significance (errors, troubleshooting, novel techniques)
- If significant, extracts lessons learned
- Stores as JSONL in `pending/YYYY-MM-DD_<thread-id>.lessons.jsonl`

**Significance criteria:**
- Errors or exceptions occurred
- Troubleshooting sequences
- System changes or refactoring
- Novel or creative techniques
- Glitches or difficulties
- Multiple retry attempts
- Workarounds or fixes

### 2. Weekly Review

Every Sunday evening, scheduled task:
- Loads all pending lessons
- Presents for approval/edit/rejection
- Updates architectural principle modules with approved lessons
- Moves approved lessons to `archive/`
- Discards rejected lessons

### 3. Principle Updates

Approved lessons are integrated into principles:
- **Append examples** to existing principles
- **Create new principles** if they don't fit existing ones
- **Update anti-patterns** sections
- **Maintain change logs** in each module

---

## Lesson Schema

See `file 'N5/lessons/schemas/lesson.schema.json'` for full schema.

**Key fields:**
```json
{
  "lesson_id": "uuid",
  "thread_id": "con_XXX",
  "timestamp": "2025-10-12T13:08:44Z",
  "type": "technique|strategy|design_pattern|troubleshooting|anti_pattern",
  "title": "Brief title",
  "description": "What we did/encountered",
  "context": "Why it was needed",
  "outcome": "Result/resolution",
  "principle_refs": ["15", "16"],
  "tags": ["error-handling", "state-verification"],
  "status": "pending|approved|rejected"
}
```

---

## Commands

### lessons-review
**Purpose:** Batch review pending lessons (run weekly)

**Usage:**
```bash
python3 /home/workspace/N5/scripts/n5_lessons_review.py
```

**Features:**
- Interactive TUI for approve/edit/reject
- Bulk operations
- Preview principle updates before applying
- Dry-run mode

### lessons-export
**Purpose:** Export lessons by date range or tag

**Usage:**
```bash
python3 /home/workspace/N5/scripts/n5_lessons_export.py \
  --start-date 2025-10-01 \
  --end-date 2025-10-31 \
  --format markdown > october_lessons.md
```

---

## Integration Points

### conversation-end
- Calls lesson extraction logic
- Only for significant threads
- Non-blocking (failures don't stop conversation end)

### thread-export (optional)
- Can include extracted lessons in export
- Opt-in feature

### Scheduled Tasks
- `lessons-review` runs Sunday evenings
- Configured in Zo scheduled tasks

---

## File Naming Convention

**Pending lessons:**
```
pending/YYYY-MM-DD_con_XXXXX.lessons.jsonl
```

**Archived lessons:**
```
archive/YYYY-MM_con_XXXXX.lessons.jsonl
```

**Organized by month in archive for easier browsing.**

---

## Maintenance

### Retention Policy
- **Pending:** Auto-clean after 30 days if not reviewed
- **Archive:** Keep forever

### Backup
- Archive directory should be included in git tracking
- Regular backups via N5 backup system

---

## Version History

**v1.0 (2025-10-12)**
- Initial implementation
- Automatic extraction on conversation-end
- Weekly review workflow
- Integration with architectural principles

---

**Status:** Active  
**Last Updated:** 2025-10-12
