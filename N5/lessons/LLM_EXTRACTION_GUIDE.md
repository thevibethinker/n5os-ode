# LLM Lesson Extraction Guide

**For:** The LLM (me) to follow when extracting lessons during conversation-end  
**Updated:** 2025-10-12  
**Approach:** Option A - Direct extraction before script runs

---

## When This Applies

User triggers `conversation-end` → I extract lessons FIRST → Then run conversation-end script

---

## Step-by-Step Process

### 1. Check Significance

Before extracting, determine if this thread is worth capturing:

**Significance indicators:**
- ✅ Errors or exceptions occurred
- ✅ Troubleshooting or debugging sequences
- ✅ System changes, refactoring, or new implementations
- ✅ Novel techniques or creative problem-solving
- ✅ Multiple file versions (indicates iteration)
- ✅ Design or implementation documents created
- ✅ Glitches, difficulties, or workarounds
- ✅ Repeated mistakes or anti-patterns identified

**Check the conversation workspace:**
```bash
ls -la /home/.z/workspaces/con_[THREAD_ID]/
```

**If NOT significant:** Skip extraction, proceed directly to conversation-end script

**If significant:** Continue to Step 2

---

### 2. Analyze the Conversation

Review what happened in this thread:

**Key questions:**
- What problem were we solving?
- What approaches did we try?
- What worked? What didn't?
- Were there any errors or failures?
- How did we resolve issues?
- What techniques or patterns did we apply?
- What would we do differently next time?
- Are there lessons that apply to architectural principles?

**Data sources:**
- Conversation transcript (my own memory of this thread)
- Files created in workspace
- Commands executed
- Errors encountered
- Solutions implemented

---

### 3. Extract Lessons

For each meaningful lesson, create a structured record:

**Lesson types:**
- **Technique** - Specific method or approach used
- **Strategy** - Higher-level decision-making pattern
- **Design Pattern** - Architectural or structural pattern applied
- **Troubleshooting** - Problem-solving approach that worked
- **Anti-pattern** - Mistake or approach that failed (very important!)

**Required fields:**
- `type`: One of the types above
- `title`: Brief, descriptive (5-100 chars)
- `description`: What we did or encountered (10+ chars, be specific)
- `context`: Why it was needed, what led to this
- `outcome`: Result or resolution achieved
- `principle_refs`: Array of principle numbers this relates to (0-21)
- `tags`: Relevant tags for searching

**Quality criteria:**
- Specific and actionable
- Self-contained (understandable without thread context)
- Reusable (applies to future situations)
- Grounded in what actually happened
- Maps to relevant architectural principles

**Avoid:**
- Vague observations
- Routine operations
- Trivial actions
- Lessons that don't add value

---

### 4. Map to Architectural Principles

For each lesson, identify which principles it relates to:

**Principle quick reference:**
- 0: Rule-of-Two (context loading)
- 1: Human-readable first
- 2: Single Source of Truth
- 5: Safety and anti-overwrite
- 7: Idempotence and dry-run
- 11: Failure modes and recovery
- 15: Complete before claiming complete
- 16: Accuracy over sophistication (NO FALSE API LIMITS!)
- 17: Test with production configuration
- 18: State verification is mandatory
- 19: Error handling is not optional
- 20: Modular design
- 21: Document assumptions/placeholders/stubs

**Example mappings:**
- File write verification → 18
- False API limitation → 16
- Placeholder not documented → 21
- Module splitting → 20
- Error without recovery → 19

---

### 5. Generate Lesson Records

Create Python-compatible JSON objects:

```python
import json
import uuid
from datetime import datetime, timezone

lessons = [
    {
        "lesson_id": str(uuid.uuid4()),
        "thread_id": "con_JB5UD88QWtAkoaXF",  # This thread's ID
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "anti_pattern",
        "title": "Don't invent API limitations without checking docs",
        "description": "Claimed Gmail API had 3-message limit when it actually supports 500/query with pagination",
        "context": "Was testing email retrieval and set maxResults=3 for testing, then incorrectly stated this was an API limit",
        "outcome": "User corrected me. Actual limits: 500/query, pagination via pageToken, date filters, no hard limit",
        "principle_refs": ["16"],
        "tags": ["api-limits", "false-assumptions", "accuracy"],
        "status": "pending"
    },
    {
        "lesson_id": str(uuid.uuid4()),
        "thread_id": "con_JB5UD88QWtAkoaXF",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "design_pattern",
        "title": "Modularize large documents for selective loading",
        "description": "Split 400-line monolithic principles document into 5 focused modules (core, safety, quality, design, operations) for context efficiency",
        "context": "Loading entire document every time wasted tokens. Needed selective loading based on task type.",
        "outcome": "70% context reduction for typical operations. Load index + 1-2 modules instead of entire document.",
        "principle_refs": ["20", "8"],
        "tags": ["modular-design", "context-efficiency", "token-optimization"],
        "status": "pending"
    }
]
```

---

### 6. Write to Pending Directory

```python
from pathlib import Path

# Ensure directory exists
pending_dir = Path("/home/workspace/N5/lessons/pending")
pending_dir.mkdir(parents=True, exist_ok=True)

# Generate filename
date_str = datetime.now().strftime("%Y-%m-%d")
thread_id = "con_JB5UD88QWtAkoaXF"  # Current thread
filename = f"{date_str}_{thread_id}.lessons.jsonl"
filepath = pending_dir / filename

# Write JSONL (one JSON object per line)
with open(filepath, 'w') as f:
    for lesson in lessons:
        f.write(json.dumps(lesson) + '\n')

print(f"✓ Extracted {len(lessons)} lessons to {filepath}")
```

---

### 7. Verify Write Succeeded

**Apply Principle 18:** State verification is mandatory

```python
# Verify file exists
if not filepath.exists():
    raise IOError(f"Failed to create lessons file: {filepath}")

# Verify size > 0
if filepath.stat().st_size == 0:
    raise IOError(f"Lessons file is empty: {filepath}")

# Verify valid JSONL
with open(filepath, 'r') as f:
    line_count = 0
    for line in f:
        if line.strip():
            json.loads(line)  # Will raise if invalid
            line_count += 1

if line_count != len(lessons):
    raise ValueError(f"Expected {len(lessons)} lessons, found {line_count}")

print(f"✓ Verified {line_count} lessons written correctly")
```

---

### 8. Report to User

After extraction, tell the user what was captured:

```
✓ Lesson Extraction Complete

Analyzed conversation: con_JB5UD88QWtAkoaXF
Significance: Errors, system changes, novel techniques
Extracted: 5 lessons
  - 2 anti-patterns
  - 2 design patterns
  - 1 troubleshooting

Saved to: N5/lessons/pending/2025-10-12_con_JB5UD88QWtAkoaXF.lessons.jsonl

These will be reviewed in your next Sunday evening lesson review.

Now proceeding with conversation-end...
```

---

### 9. Continue to Conversation-End

After extraction is complete, run the conversation-end script:

```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "/home/workspace/N5/scripts/n5_conversation_end.py"],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.returncode != 0:
    print(f"Error: {result.stderr}", file=sys.stderr)
```

---

## Complete Example Flow

```
USER: "conversation-end"

ME:
1. Check significance
   → Yes: Design/implementation docs, multiple file versions

2. Analyze conversation
   → Built lessons extraction system
   → Split monolithic principles into modules
   → Made mistakes with API limits and placeholders

3. Extract lessons
   → 5 lessons identified:
      - Anti-pattern: False API limits (Principle 16)
      - Design pattern: Document modularization (Principle 20)
      - Anti-pattern: Undocumented placeholders (Principle 21)
      - Troubleshooting: LLM self-invocation pattern
      - Technique: Significance detection heuristics

4. Generate records
   → Create JSON objects with all required fields
   → Map to principles 16, 20, 21, etc.
   → Add descriptive tags

5. Write to pending/
   → /home/workspace/N5/lessons/pending/2025-10-12_con_XXX.lessons.jsonl

6. Verify write
   → File exists ✓
   → Size > 0 ✓
   → Valid JSONL ✓
   → Count matches ✓

7. Report to user
   → "✓ Extracted 5 lessons..."

8. Run conversation-end script
   → python3 /home/workspace/N5/scripts/n5_conversation_end.py
   → [Normal conversation-end flow continues]
```

---

## Error Handling

**If extraction fails:**
- Log the error
- Don't block conversation-end
- Tell user: "⚠️ Lesson extraction failed (non-blocking), continuing with conversation-end..."
- User can manually extract later if needed

**If not significant:**
- Skip extraction entirely
- Proceed directly to conversation-end
- Optional: "→ Thread not significant for lesson extraction"

---

## Quality Checklist

Before writing lessons, verify:

- [ ] Each lesson is specific and actionable
- [ ] Description explains WHAT happened clearly
- [ ] Context explains WHY it happened
- [ ] Outcome shows RESULT achieved
- [ ] Principle refs are accurate (0-21)
- [ ] Tags are relevant and searchable
- [ ] No false information (Principle 16!)
- [ ] Self-contained (understandable alone)
- [ ] Adds real value (not trivial)

---

## Common Mistakes to Avoid

❌ **Don't:**
- Invent lessons that didn't happen
- Be vague ("we did some stuff")
- Forget to map to principles
- Skip verification after writing
- Block conversation-end if extraction fails
- Extract trivial routine operations

✅ **Do:**
- Be specific about what happened
- Map lessons to architectural principles
- Verify file write succeeded
- Allow conversation-end to continue
- Focus on meaningful, reusable lessons
- Capture anti-patterns (mistakes are valuable!)

---

**This guide is normative** - follow it exactly when extracting lessons during conversation-end.
