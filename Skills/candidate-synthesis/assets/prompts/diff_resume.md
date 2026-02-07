# Resume Diff Prompt

You are comparing a candidate's resume against Careerspan's findings to identify where Careerspan adds value beyond the resume alone.

## Input

**Resume Text:**
{{resume_text}}

**Careerspan Skills Data:**
{{skills_json}}

**Story Clusters:**
{{story_clusters}}

## Your Task

### Category 1: Substantiated Beyond Resume
What did the resume claim that Careerspan verified with story evidence?

For each item:
- What the resume claimed (brief)
- What Careerspan found (with story evidence)
- Why this matters: Verification increases employer confidence

Example:
- Resume: "Built ML platform"
- Careerspan: "Verified with detailed story of architecture decisions, user adoption metrics (200+ DAU), stakeholder navigation across 5 teams, and scaling from 4→20 person team"
- Why it matters: Resume bullet → Rich evidence of execution capability

### Category 2: Revealed Beyond Resume
What did Careerspan discover that the resume doesn't show?

Look for:
- Behavioral patterns (problem-finding, ownership) not stated on resume
- Soft skills demonstrated in stories but not listed
- Decision-making quality visible in story details
- Collaboration patterns not captured in bullet points

Example:
- Finding: "Designs for adoption, not just function — built persuasion into the product"
- Resume gap: Resume lists features built, not the strategic thinking behind them
- Why it matters: Shows product sense beyond engineering execution

### Category 3: Unverified Claims (Caution)
What did the resume claim that Careerspan couldn't verify?

For each:
- The claim
- Why it matters (if employer cares about it)
- Probe suggestion

### Category 4: Transferable Potential
What abilities are transferable to the target role but not obvious from resume?

Look for:
- Skills demonstrated in different contexts that apply here
- Patterns that would transfer (e.g., "solo product owner" → "async-first work")
- Growth trajectory indicators

## Output Format

```json
{
  "substantiated_beyond_resume": [
    {
      "resume_claim": "Built ML platform",
      "careerspan_evidence": "Verified with detailed story: architecture decisions, 200+ DAU, 5-team stakeholder navigation, 4→20 person scaling",
      "confidence_boost": "Bullet → rich evidence of execution at scale"
    }
  ],
  "revealed_beyond_resume": [
    {
      "finding": "Problem-finding instinct: Both stories start with self-identified problems, not tickets",
      "resume_gap": "Resume doesn't highlight this pattern — just lists accomplishments",
      "why_it_matters": "Strong signal for 'self-starter' filter"
    }
  ],
  "unverified_claims": [
    {
      "claim": "Strong async communication",
      "why_it_matters": "Employer is async-first",
      "probe": "How do you operate when decisions are async?"
    }
  ],
  "transferable_potential": [
    {
      "ability": "Stakeholder translation without PM buffer",
      "evidence": "Solo product owner at AmEx, managed feedback across functions",
      "transfer_to": "FlowFuse's 'no PM' culture",
      "confidence": "high"
    }
  ]
}
```

## Key Principles

1. **Employer pays for confidence** — Substantiation is the core value
2. **Revealed > Stated** — What we discover that resume hides is premium insight
3. **Honest about gaps** — Unverified claims protect employer from bad hires
4. **Potential is forward-looking** — Connect past evidence to future fit
