---
created: 2025-12-02
last_edited: 2025-12-02
version: 1.0
purpose: Extract action items from meeting transcripts
---

You are analyzing a meeting transcript to extract action items — things someone agreed to do.

## Transcript

{transcript}

## Task

Identify **action items** — concrete tasks that someone committed to completing.

### Signals to look for:

**Strong signals (high confidence):**
- "I'll [do X]"
- "I will [do X]"
- "Let me [do X]"
- "I can [do X] by [date]"
- "Action item: [X]"
- "Next step is [X]"

**Medium signals:**
- "We should [do X]"
- "It would be good to [do X]"
- "I need to [do X]"
- "Don't forget to [do X]"

**Context clues:**
- Deadlines mentioned ("by Friday", "next week", "before the meeting")
- Specific deliverables ("the deck", "the email", "the intro")
- Named owners ("I'll", "you should", "[Name] will")

### Return structured JSON:

```json
{
  "action_items": [
    {
      "action": "specific, actionable task description",
      "owner": "person responsible (V, other person's name, or 'TBD')",
      "deadline": "date/timeframe mentioned, or null",
      "priority": "high|medium|low (based on urgency signals)",
      "context": "relevant quote from transcript",
      "confidence": "high|medium|low"
    }
  ],
  "v_actions": ["list of actions owned by V"],
  "other_actions": ["list of actions owned by the other party"],
  "follow_up_needed": ["ambiguous items that need clarification"]
}
```

## Guidelines

- An action item must be **specific** and **actionable** — vague intentions don't count
- If owner is unclear, mark as "TBD" and include in `follow_up_needed`
- Distinguish between V's actions (for the follow-up email) and other party's actions
- Deadlines like "soon" or "when you can" are low priority; specific dates are high priority

