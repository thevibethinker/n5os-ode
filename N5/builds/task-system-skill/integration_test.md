# Thread-Close Integration Test Scenario

## Overview

This document provides a test scenario for the new task-system integration with thread-close.

## Test Flow

### 1. Action Conversation Detection (Conversation Start)

```bash
# Check if conversation is action-oriented
python3 Skills/task-system/scripts/context.py action-check --convo-id con_example123
```

**Expected Output:**
```json
{
  "convo_id": "con_example123",
  "session_state": {
    "focus": "Draft investor memo for Q4 update"
  },
  "existing_tasks": [
    {
      "id": "5",
      "title": "Investor update memo",
      "status": "pending",
      "priority_bucket": "external"
    }
  ],
  "inference_guidance": {
    "action_keywords": ["write", "draft", "build", "create", "send"],
    "task_patterns": ["the X for Y", "let's work on X"]
  }
}
```

**AI Reasoning:** "Focus mentions 'Draft investor memo' and there's an existing task 'Investor update memo' - this is an action conversation."

### 2. Completion Assessment (Conversation Close)

```bash
# Assess task completion
python3 Skills/task-system/scripts/context.py completion-check --convo-id con_example123 --task-id 5
```

**Expected Output:**
```json
{
  "task": {
    "id": 5,
    "title": "Investor update memo",
    "status": "in_progress",
    "milestones": [
      {"description": "Draft memo content"},
      {"description": "Review with team"},
      {"description": "Send to investors"}
    ]
  },
  "artifacts_created": [
    "Documents/memos/investor-update-q4.md"
  ],
  "delivery_indicators": {
    "files_created": ["Documents/memos/investor-update-q4.md"],
    "emails_sent": false,
    "explicit_completion_statement": false
  }
}
```

**AI Reasoning:** "Draft memo created (milestone 1 complete), but not yet reviewed or sent. Status: partial."

### 3. AI Assessment Presentation

**Show to V:**
```
TASK: Investor update memo

Assessment: 🟡 PARTIAL
Evidence: Documents/memos/investor-update-q4.md created

Milestones:
✓ Draft memo content
⬜ Review with team  
⬜ Send to investors

Next step: Review draft with team

Mark as: [complete] [partial] [blocked]
```

### 4. Task Update Based on Choice

If V chooses "partial":
```bash
python3 Skills/task-system/scripts/task.py update 5 --status in_progress --notes "Draft completed"
```

If V chooses "complete":
```bash
python3 Skills/task-system/scripts/task.py complete 5 --actual 45
```

### 5. Next Step Inference

```bash
# Get next step for partial tasks
python3 Skills/task-system/scripts/context.py next-step --task-id 5
```

**Expected Output:**
```json
{
  "task": {
    "title": "Investor update memo",
    "milestones": [
      {"description": "Draft memo content"},
      {"description": "Review with team"},
      {"description": "Send to investors"}
    ]
  },
  "inference_guidance": {
    "next_step_patterns": [
      "If milestones defined: next uncompleted milestone"
    ]
  }
}
```

**AI Reasoning:** "Next milestone is 'Review with team' - schedule review session."

## Integration Points

### In `N5/lib/close/core.py`

- `_check_task_system_integration()` - Calls context.py action-check
- `gather_thread_context()` - Includes task integration status
- No complex task_info - just a flag for the LLM

### In `Skills/thread-close/SKILL.md`

- Clear step-by-step integration instructions
- Points to task-system skill for reasoning guidance
- Uses context scripts instead of close_hooks.py

## Key Changes

**Before (close_hooks.py approach):**
- Regex patterns for action detection
- Complex inference logic in Python
- Tightly coupled assessment and update

**After (context-based approach):**
- Context gathering scripts (no inference)
- AI does semantic reasoning
- Clear separation: gather → reason → act

## Benefits

1. **Semantic Understanding:** AI reasons about task completion vs regex patterns
2. **Maintainable:** Context scripts just gather data, AI provides intelligence
3. **Flexible:** Easy to add new context without changing inference logic
4. **Testable:** Scripts have clear inputs/outputs, AI reasoning is explicit
