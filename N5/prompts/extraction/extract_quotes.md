---
created: 2025-12-02
last_edited: 2025-12-02
version: 1.0
purpose: Extract quotable moments from meeting transcripts
---

You are analyzing a meeting transcript to identify **quotable moments** — eloquent, insightful, or memorable statements.

## Transcript

{transcript}

## Task

Identify statements worth capturing — things V said that are:
- **Insightful** — novel perspective, wisdom, aha-moment
- **Eloquent** — well-phrased, memorable, quotable
- **Useful** — could be repurposed for content, testimonials, marketing
- **Personal** — reveals V's story, values, or philosophy

### What makes something quotable:

**Content signals:**
- Original insight or perspective
- Memorable phrasing or metaphor
- Distilled wisdom or principle
- Authentic personal story
- Client-facing value proposition

**Delivery signals (if discernible):**
- Audience reaction (laughter, agreement, "that's great")
- Emphasis or repetition
- Natural pause before/after (indicating weight)

### Return structured JSON:

```json
{
  "quotes": [
    {
      "speaker": "V or speaker name",
      "text": "exact quote",
      "cleaned_text": "quote cleaned up for readability (remove filler words, fix grammar)",
      "category": "insight|story|philosophy|value_prop|wisdom|humor",
      "potential_use": "where this could be used (social, website, pitch, etc.)",
      "audience_reaction": "reaction if any, or null",
      "context": "what prompted this statement",
      "quotability_score": 1-10
    }
  ],
  "top_3_quotes": ["best three for immediate use"],
  "content_opportunities": [
    {
      "theme": "recurring theme",
      "quotes": ["related quotes"],
      "content_idea": "how to turn into content"
    }
  ]
}
```

## Guidelines

- Focus primarily on V's statements, but capture great lines from others too
- `cleaned_text` should be publication-ready (remove "um", "like", fix grammar)
- `quotability_score` considers both content quality and phrasing
- `content_opportunities` identifies themes that could become blog posts, social content, etc.

