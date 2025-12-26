---
created: 2025-12-02
last_edited: 2025-12-02
version: 1.0
purpose: Extract resource commitments from meeting transcripts
---

You are analyzing a meeting transcript to identify resources that V (Vrijen) committed to sending or sharing.

## Transcript

{transcript}

## Available Content Library Items

These are resources V has available to share:

{library_items}

## Task

1. **Identify every commitment** where V offers to send, share, or provide something:
   
   **Explicit signals:**
   - "I'll send you..."
   - "Let me share..."
   - "Here's a link to..."
   - "I'll follow up with..."
   - "Check out..."
   - "I'll include that in the follow-up"
   
   **Implicit signals:**
   - "We have a great [resource] for that"
   - "There's a [guide/tool/link] that could help"
   - "You should look at..."
   - Mentioning a specific tool, product, or resource by name

2. **Match each commitment** to a Content Library item:
   - Match by title similarity (e.g., "YC founder matching" → "YC Founder Match")
   - Match by category (e.g., "scheduling link" → Calendly items)
   - Match by context (e.g., "consulting guide" → McKinsey guide)

3. **Return structured JSON:**

```json
{
  "resources": [
    {
      "commitment_text": "exact quote showing the commitment",
      "intent": "what V is offering (e.g., 'co-founder matching tool')",
      "matched_item_id": "content library ID or null if no match",
      "matched_item_title": "title of matched item",
      "matched_item_url": "URL if available",
      "confidence": "high|medium|low",
      "reasoning": "brief explanation of match logic"
    }
  ],
  "unmatched_commitments": [
    {
      "commitment_text": "quote",
      "intent": "what was promised",
      "suggested_action": "what to do (e.g., 'add to content library')"
    }
  ]
}
```

## Guidelines

- Be **generous** in detecting commitments — better to catch more than miss important ones
- A commitment doesn't need the word "send" — offering to share information counts
- If V mentions a tool/product by name, that's likely a commitment to share it
- If no Content Library match exists, include in `unmatched_commitments` so V can add it

