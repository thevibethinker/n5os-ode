# Hiring POV Generation Prompt

You are analyzing a job description to extract what the employer **really** cares about — both explicit requirements and implicit filters.

## Input

**Job Description:**
{{jd_text}}

**Company Context (if available):**
{{company_context}}

## Your Task

Generate a Hiring POV document with these sections:

### 1. Explicit Requirements
List the stated requirements (skills, experience, education). Be specific.

### 2. Implicit Filters
What are they *really* filtering for that isn't stated directly? Look for:
- Phrases like "self-starter", "fast-paced", "ambiguous" → they want someone who doesn't need management
- Emphasis on "ownership" → they're filtering out task-followers
- "Writing skills" in a tech role → async culture, writing = thinking proxy
- "Side projects" or "built something" → filtering out 9-to-5 mentality
- Remote/async mentions → timezone and communication style filters

### 3. Trait Signals
What traits would make someone succeed here? Frame as observable behaviors:
- "Ownership mindset: 'That's not my job' doesn't exist here"
- "Shipping velocity: Measures progress in days/weeks, not quarters"

### 4. Red Flags
What would disqualify someone even if they meet explicit requirements?
- No evidence of building from scratch
- Slow shipping mindset
- Expects hand-holding
- Cannot explain work simply

### 5. Story Types Valued
What kind of stories would resonate with this employer?
- Stories about building 0→1
- Stories about fixing something that "wasn't my job"
- Stories about shipping quickly and iterating

### 6. Validation Questions
What questions should Careerspan's analysis answer about any candidate?
- Has this person actually built and shipped something real?
- Can they work independently?
- Do they take ownership or wait to be assigned?

## Output Format

Return JSON matching this schema:
```json
{
  "explicit_requirements": ["string"],
  "implicit_filters": ["string"],
  "trait_signals": ["string"],
  "red_flags": ["string"],
  "story_types_valued": ["string"],
  "validation_questions": ["string"],
  "culture_markers": ["string"]
}
```

Be specific and actionable. Every filter should help distinguish between candidates who would thrive vs struggle.
