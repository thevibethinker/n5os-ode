---
created: 2025-12-02
last_edited: 2025-12-02
version: 1.0
purpose: Extract decisions made during meetings
---

You are analyzing a meeting transcript to identify **decisions** — conclusions reached or agreements made.

## Transcript

{transcript}

## Task

Identify **decisions** — things that were decided, agreed upon, or concluded.

### Signals to look for:

**Explicit decisions:**
- "Let's do [X]"
- "We agreed to [X]"
- "The plan is [X]"
- "I've decided to [X]"
- "We'll go with [X]"

**Implicit decisions:**
- Moving past a topic after reaching conclusion
- Confirming understanding ("So we're aligned on [X]")
- Ruling out options ("We won't [X]")

**Types of decisions:**
- Strategic (direction, approach, priorities)
- Tactical (specific actions, timelines)
- Relational (who will do what, introductions)
- Logistical (meeting times, communication channels)

### Return structured JSON:

```json
{
  "decisions": [
    {
      "decision": "clear statement of what was decided",
      "type": "strategic|tactical|relational|logistical",
      "parties_involved": ["V", "other person"],
      "context": "relevant quote showing the decision",
      "implications": "what this means going forward",
      "confidence": "high|medium|low"
    }
  ],
  "open_questions": [
    {
      "question": "unresolved topic",
      "context": "where it came up",
      "suggested_resolution": "how to resolve"
    }
  ],
  "key_agreements": ["summary list of main agreements"]
}
```

## Guidelines

- Decisions are **conclusions**, not just discussions
- Look for language that signals closure on a topic
- `open_questions` captures things that were raised but not resolved
- `key_agreements` is a quick summary for the follow-up email

