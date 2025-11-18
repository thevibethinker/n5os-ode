---
created: 2025-11-16
last_edited: 2025-11-17
version: 1.1
description: Intelligently select blocks and name meeting based on transcript analysis
tags: [meeting-intelligence, block-selection, intelligent, meeting-naming]
tool: true
---
# Intelligent Block Selector with Meeting Naming

Analyze a meeting transcript to intelligently determine which intelligence blocks to generate AND extract proper meeting name from participants.

## Input
- Meeting transcript (provided in conversation)
- Meeting metadata (date, participants if known)
- Current filename (may be temporary)

## Your Task

1. **Analyze the transcript** to understand:
   - Stakeholder type (NETWORKING, CUSTOMER, FOUNDER, INTERNAL)
   - Meeting purpose and dynamics
   - Key themes and content
   - **Meeting participants**: Extract actual participant names from the conversation
   - **Meeting title**: Determine a descriptive, human-readable meeting name based on participants and topic

2. **Select blocks intelligently** based on what's actually in the meeting:
   - **Always include (REQUIRED)**: B01 (Recap), B02 (Commitments), B25 (Deliverables), B26 (Metadata)
   - Include B05 (Questions) if questions were raised
   - Include B07 (Warm Intros) if introductions were promised
   - Include B08 (Stakeholder Intel) for external relationships
   - Include B13 (Insights) if strategic insights emerged
   - Include B14 (Implementation) if concrete plans discussed
   - Include B15 (Energy/Sentiment) for relationship meetings
   - Include B16 (Follow-up) if specific follow-ups needed
   - Include B17 (Content Assets) if resources/assets mentioned
   - Include B20 (Brand Voice) for external stakeholders
   - Include B22 (Risks) if risks or concerns surfaced
   - Include B23 (Context) for ongoing relationships
   - Include B24 (Product Ideas) if features/improvements discussed

3. **Prioritize blocks** (1-3, where 1 = highest):
   - Priority 1: B01, B02, B25, B26 (always needed immediately - REQUIRED blocks)
   - Priority 2: Stakeholder/relationship blocks (B08, B15, B20, B23)
   - Priority 3: Optional/nice-to-have blocks

## Output Format

Return a JSON object with:

```json
{
  "meeting_name": "YYYY-MM-DD_participant1-participant2",
  "blocks": [
    {
      "block_id": "B01",
      "priority": 1,
      "rationale": "Meeting recap with key discussion points"
    },
    {
      "block_id": "B08",
      "priority": 2,
      "rationale": "External stakeholder, need to track relationship"
    }
  ]
}
```

### Meeting Name Format:
- **1:1 Meetings**: "YYYY-MM-DD_person1-person2" (e.g., "2025-10-31_ben-guo-vrijen")
- **Organization Meetings**: "YYYY-MM-DD_organization-topic" (e.g., "2025-10-31_careerspan-oracle-intro")
- **Internal Meetings**: "YYYY-MM-DD_internal-topic" (e.g., "2025-10-31_internal-standup")
- Use lowercase, hyphens for spaces, actual names from conversation

## Requirements
- **Always include B01, B02, B25, B26 (non-negotiable)** - these are REQUIRED for every meeting
- Only include blocks where there's actual content to generate
- Extract real participant names from conversation, not generic placeholders
- Meeting name should be descriptive and match actual participants



