---
created: 2026-01-09
worker_id: W7
component: SMS Formatter
status: pending
depends_on: [W5]
---

# W7: SMS Formatter

## Objective
Format draft sets for SMS approval with all 4 variants, handle responses.

## Output Files
- `Projects/x-thought-leader/src/sms_formatter.py`

## SMS Format Design

V's requirements:
- See all 4 variants with labels
- Respond with number (1-4) or keyword + suggestion
- "skip" or "0" to skip
- Expiry: EOD

### Outbound Format
```
🐦 @asanwal just tweeted:
"AI is going to change how we assess candidates"

Your drafts:

1️⃣ SUPPORTIVE:
Been saying this for years. The real unlock is replacing the entire signal layer.

2️⃣ CHALLENGING:
True, but AI isn't changing assessment — it's exposing how broken it already was.

3️⃣ SPICY:
Hot take: AI won't fix hiring. Hiring was never a technology problem.

4️⃣ COMEDIC:
Resumes watching AI enter the chat: 👀💀

Reply 1-4 to post, or "skip"
Expires: 11:59 PM ET
```

### Inbound Parsing
```python
def parse_approval_response(text: str) -> dict:
    """
    Parse V's SMS response.
    
    Returns:
        {
            "action": "approve" | "skip" | "refine",
            "variant": 1-4 or None,
            "suggestion": str or None
        }
    
    Examples:
        "2" → {"action": "approve", "variant": 2}
        "skip" → {"action": "skip"}
        "0" → {"action": "skip"}
        "3 but make it shorter" → {"action": "refine", "variant": 3, "suggestion": "make it shorter"}
        "spicy but less aggressive" → {"action": "refine", "variant": 3, "suggestion": "less aggressive"}
    """
```

## Core Functions

```python
def format_approval_sms(draft_set: DraftSet) -> str:
    """Format a draft set for SMS delivery."""
    
def send_approval_request(draft_set: DraftSet) -> str:
    """
    Send SMS via send_sms_to_user tool.
    Returns message_id for tracking.
    """
    
def handle_approval_response(
    response_text: str,
    draft_set_id: str
) -> dict:
    """
    Process V's response, update DB, return action taken.
    """
```

## Refinement Flow

If V responds with suggestion (e.g., "3 but shorter"):
1. Parse variant and suggestion
2. Regenerate that single variant with suggestion in prompt
3. Send new SMS with just the refined version
4. Await final approval

```python
def refine_draft(
    original_draft: TweetDraft,
    suggestion: str
) -> TweetDraft:
    """
    Regenerate a draft incorporating V's feedback.
    """
```

## Expiry Handling

```python
def expire_pending_drafts(db_path: str) -> int:
    """
    Mark drafts past EOD as expired.
    Run at midnight or on next poll.
    Returns count expired.
    """
```

## Acceptance Criteria
- [ ] SMS format is readable and compact
- [ ] All 4 variants fit in reasonable SMS length
- [ ] Parser handles: numbers, "skip", keywords, suggestions
- [ ] Refinement flow works
- [ ] Expiry is enforced
