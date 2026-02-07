# Final Narrative Generation Prompt

You are generating the final employer-focused narrative for a candidate. Your audience is a hiring manager with 30 seconds to decide if they should take a meeting.

## Input

**Candidate:**
{{candidate_name}} for {{role}} at {{company}}

**Hiring POV:**
{{hiring_pov}}

**Story Clusters:**
{{story_clusters}}

**Resume Diff:**
{{resume_diff}}

**Scores:**
- Overall: {{overall_score}}/100
- Signal Strength: {{signal_strength}}

## Your Task

Generate a narrative that answers these questions IN ORDER OF PRIORITY:

### 1. Should I Take This Meeting? (BLUF)
- Score interpretation (what does 89/100 mean?)
- One-sentence verdict
- 2-3 sentence reasoning tied to what employer cares about

### 2. What Would They Bring to My Team?
- Lead with the most relevant story cluster
- Frame in employer's language (use their trait signals)
- Don't list skills — describe capabilities through story themes
- Maximum 3 clusters, ranked by employer relevance

### 3. What Should I Probe?
- Risks ordered by what employer cares about most
- Each risk needs:
  - What the risk is
  - Why it matters to THIS employer
  - Specific probe question
- Maximum 4 risks

### 4. What Potential Have We Unveiled?
- What Careerspan found that resume doesn't show
- Transferable abilities for this specific role
- Frame as "confidence boosters" for the employer

## Spikes Generation

Create 5-7 upward spikes and 2-4 downward spikes:

**Upward Spikes (▲)**
- 5 words or less
- Behavioral insight, not skill name
- Ordered by employer relevance
- Include evidence marker (✓✓ = story-verified, ✓ = resume-only)

**Downward Spikes (▼)**
- 5 words or less
- Risk or gap
- Ordered by importance to employer

Examples:
- ▲ "Problem-finder, not ticket-taker" ✓✓
- ▲ "Ships under ambiguity" ✓✓
- ▼ "Async experience unverified" ✓

## Interview Questions

Generate 4-5 questions that:
1. Target the highest-priority risks
2. Are specific to this candidate's gaps
3. Would give employer confidence if answered well
4. Are framed for their cultural context

## Output Format

```json
{
  "verdict": {
    "score": 89,
    "action": "Take This Meeting",
    "summary": "...",
    "reasoning": "..."
  },
  "spikes": {
    "up": [{"label": "...", "verified": "✓✓", "importance": 10}],
    "down": [{"label": "...", "verified": "✓", "importance": 7}]
  },
  "what_they_bring": [
    {
      "theme": "...",
      "narrative": "...",
      "employer_relevance": "..."
    }
  ],
  "risks_to_probe": [
    {
      "risk": "...",
      "priority": "high|medium|low",
      "why_it_matters": "...",
      "probe_question": "..."
    }
  ],
  "unveiled_potential": {
    "substantiated": ["..."],
    "revealed": ["..."],
    "transferable": ["..."]
  },
  "interview_questions": [
    {
      "topic": "...",
      "question": "...",
      "why": "..."
    }
  ]
}
```

## Key Principles

1. **BLUF first** — If they read nothing else, they know if it's a yes/no
2. **Employer's language** — Use their trait signals, not generic terms
3. **Story over skills** — "Built platform from 0→1" not "Python, AWS, React"
4. **Honest about gaps** — Trust comes from transparency, not overselling
5. **Actionable questions** — Every probe should unlock confidence
