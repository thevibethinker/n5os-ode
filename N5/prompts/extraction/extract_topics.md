---
created: 2025-12-02
last_edited: 2025-12-02
version: 1.0
purpose: Extract discussion topics from meeting transcripts
---

You are analyzing a meeting transcript to identify the topics discussed.

## Transcript

{transcript}

## Task

Identify **topics** — the subjects and themes covered in this conversation.

### Topic Categories to Consider:

**Career & Professional:**
- Job search, interviewing, career transitions
- Resume, LinkedIn, professional branding
- Networking, warm intros, referrals
- Salary negotiation, offers

**Startup & Entrepreneurship:**
- Fundraising, investors, pitch
- Co-founder search, team building
- Product development, launch
- Accelerators (YC, SPC, etc.)

**Consulting & MBA:**
- Consulting interviews, case prep
- McKinsey, BCG, Bain
- MBA applications, programs

**Careerspan-Specific:**
- Careerspan product, services
- Coaching methodology
- Client success stories

**Technology & Tools:**
- Zo Computer, AI tools
- Productivity systems
- Specific software/platforms

**Personal:**
- Background, story
- Goals, aspirations
- Challenges, blockers

### Return structured JSON:

```json
{
  "topics": ["topic1", "topic2", "topic3"],
  "primary_topic": "the main focus of the conversation",
  "secondary_topics": ["other significant topics"],
  "topic_breakdown": [
    {
      "topic": "topic name",
      "estimated_percentage": 30,
      "key_points": ["main point 1", "main point 2"],
      "relevant_for_followup": true
    }
  ],
  "meeting_type_inference": "networking|coaching|sales|partnership|catch-up|interview"
}
```

## Guidelines

- Topics should be **specific enough to be useful** but not overly granular
- `primary_topic` is what the meeting was fundamentally about
- `relevant_for_followup` helps prioritize what to include in follow-up email
- `meeting_type_inference` helps determine email tone and structure

