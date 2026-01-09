---
created: 2026-01-09
worker_id: W8
component: Approval Queue Handler
status: pending
depends_on: [W7]
---

# W8: Approval Queue Handler

## Objective
Manage the approval queue, process incoming SMS responses, coordinate with poster.

## Output Files
- `Projects/x-thought-leader/src/approval_handler.py`
- `Projects/x-thought-leader/agents/approval_processor.py`

## Queue States

```
pending → approved → posted
        ↘ skipped
        ↘ expired
        ↘ refined → pending (loop)
```

## Core Functions

```python
def get_pending_approvals(db_path: str) -> list[dict]:
    """
    Get all draft sets awaiting approval.
    Filter out expired ones.
    """

def process_sms_response(
    db_path: str,
    response_text: str,
    timestamp: str
) -> dict:
    """
    Main entry point for handling V's SMS.
    
    1. Find the most recent pending draft set
    2. Parse response
    3. Take action (approve/skip/refine)
    4. Return result summary
    """

def approve_draft(
    db_path: str,
    draft_set_id: str,
    variant: int
) -> dict:
    """
    Mark variant as approved, trigger posting.
    """

def skip_draft_set(db_path: str, draft_set_id: str) -> None:
    """Mark entire draft set as skipped."""
```

## Agent Integration

The approval handler needs to process V's SMS responses. This can work via:

1. **Inbound SMS webhook** (if Zo supports) — ideal
2. **Polling agent** that checks for new SMS — fallback

For MVP, assume Zo's SMS system handles routing V's response back.

## Tracking Anti-Patterns

To avoid predictability:

```python
def check_recent_patterns(db_path: str) -> dict:
    """
    Analyze recent posts for patterns to avoid:
    - Same variant used 3x in a row
    - Same position referenced 2x in a row
    - Replied to same author 2x in a day
    """

def add_pattern_warning(draft_set: DraftSet, patterns: dict) -> DraftSet:
    """
    Add warnings to SMS if pattern detected.
    E.g., "⚠️ You've used SPICY 3x in a row"
    """
```

## Acceptance Criteria
- [ ] Queue management works (pending/approved/skipped/expired)
- [ ] SMS responses correctly parsed and routed
- [ ] Approved drafts trigger posting
- [ ] Pattern tracking prevents repetitiveness
- [ ] Refinement loop works
