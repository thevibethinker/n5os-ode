# Story Clustering Prompt

You are clustering candidate skills by the stories that demonstrate them, then synthesizing into coherent narrative themes.

## Input

**Skills Data:**
{{skills_json}}

**Hiring POV (what employer values):**
{{hiring_pov}}

## Your Task

### Step 1: Group by Story
Skills in the data have a `support[]` array with `source` (story ID). Group skills by their supporting story.

### Step 2: Synthesize Each Cluster
For each story cluster:
1. Read all the `our_take` fields for skills in this cluster
2. Identify the **theme** — what dimension of capability does this story demonstrate?
3. Write a **unified narrative** (2-3 sentences) that captures the story without repeating details
4. List the **skills demonstrated** (deduplicated)
5. Assess **employer relevance** — how does this map to what the employer cares about?

### Step 3: Identify Cross-Cutting Patterns
Look for behavioral patterns that appear across multiple stories:
- "Problem-finding" behavior (identifies issues without being told)
- "Ownership" pattern (fixes things outside their scope)
- "Shipping" pattern (bias toward action, iteration over perfection)

### Step 4: Rank by Employer Priorities
Order clusters by how well they match:
1. Explicit requirements
2. Implicit filters
3. Valued story types

## Output Format

```json
{
  "story_clusters": [
    {
      "story_id": "COKUmaqSITrBKdtxSgJp",
      "theme": "Building from Zero",
      "narrative": "Led ML SaaS platform from founding stage to enterprise adoption. Owned architecture decisions, built team from 4→20, drove adoption across global R&D.",
      "skills_demonstrated": ["End-to-end delivery", "Technical architecture", "Stakeholder management"],
      "evidence_strength": "story_verified",
      "employer_relevance": "Directly maps to '0→1 experience' requirement and 'ownership mindset' trait signal.",
      "relevance_score": 9
    }
  ],
  "cross_cutting_patterns": [
    {
      "pattern": "Problem-Finding Instinct",
      "description": "Both major stories start with self-identified problems, not assigned tickets.",
      "stories_supporting": ["COKUmaqSITrBKdtxSgJp", "pROFGle1jTPdoivBHQUt"],
      "employer_relevance": "Strong match for 'self-starter' implicit filter."
    }
  ]
}
```

## Key Principles

1. **Deduplicate ruthlessly** — Don't repeat the same detail across clusters
2. **Employer lens** — Frame everything in terms of what the employer cares about
3. **Evidence over claims** — Note whether the narrative is story-verified or resume-only
4. **Theme over skill list** — "Building from Zero" is better than "skill1, skill2, skill3"
