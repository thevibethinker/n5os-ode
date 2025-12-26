# Extract Thought Provocations

Identify 1-3 highly provocative themes or contradictions from the provided inbox snippets.

## Criteria
- **Contradiction:** Ideas that conflict with V's stated positions, Careerspan's mission, or prior commitments.
- **Cross-Pollination:** Synthetic connections between two seemingly disparate threads.
- **Hard Problem:** Complex problems mentioned in the inbox that require original, non-obvious thinking.
- **Market Signal:** Major shifts, competitor moves, or trend anomalies that challenge current assumptions.

## Truth Anchor
Every provocation MUST be rooted in a verifiable, direct quote from the inbox.

## Output Format
Return a JSON object with a list of "provocations":
{
  "provocations": [
    {
      "thread_ids": ["id1", "id2"],
      "subject": "Provocative Topic Title",
      "challenge_prompt": "A challenging, Socratic question for V that forces deeper thought.",
      "truth_anchor_quote": "A direct quote from the email that justifies this challenge.",
      "category": "Contradiction | Cross-Pollination | Hard Problem | Signal"
    }
  ]
}

## Input Data
{inbox_data}

