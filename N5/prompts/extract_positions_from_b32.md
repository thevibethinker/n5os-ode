---
created: 2025-12-27
last_edited: 2025-12-27
version: 2.0
provenance: con_vU0lAa14Y6aRjVTI
---

# Position Extraction from B32 (v2)

Extract worldview positions from a B32 Thought Provoking Ideas block. Capture the full wisdom—not just compressed claims.

## Classification Rules

For each idea in the B32, classify as:

1. **V_POSITION** — A belief V endorses as true. Extract as candidate.
2. **V_HYPOTHESIS** — Speculation V is testing. Extract with `v_stance: questioning`.
3. **EXTERNAL_WISDOM** — Someone else's insight worth tracking. Extract with speaker attribution.
4. **QUESTION** — Open question, no stance taken. SKIP.
5. **TACTICAL** — Operational/situational, not worldview. SKIP.
6. **META** — About the meeting mechanics itself. SKIP.

## Extraction Criteria

Only extract if ALL are true:
- Contains a falsifiable belief or insight
- Is worldview-level (not task-specific or ephemeral)
- Has lasting relevance (could inform future decisions)

## Output Format

Return valid JSON array. Each extracted position:

```json
{
  "insight": "2-3 sentence observation. What you see that others don't. The core belief in enough detail to be meaningful.",
  
  "reasoning": "The transferable PRINCIPLE. Why this is true IN GENERAL—not grounded in the specific anecdote, but in underlying mechanisms, human psychology, market dynamics, or structural forces that apply across contexts. Reference analogies or parallel domains where the same principle applies.",
  
  "stakes": "What follows from this. Why it matters. Implications for action, belief, or strategy. If this is true, what should change?",
  
  "conditions": "When this applies. Boundary conditions. Where the principle breaks down or doesn't hold. Edge cases.",
  
  "source_excerpt": "Direct quote or paraphrase from the B32 (the anecdote/evidence that sparked this insight)",
  
  "speaker": "V" or "name of person who said it",
  "v_stance": "endorsed" | "questioning" | "neutral",
  "domain": "hiring-market | careerspan | ai-automation | founder | worldview | epistemology",
  "classification": "V_POSITION" | "V_HYPOTHESIS" | "EXTERNAL_WISDOM"
}
```

If nothing qualifies, return empty array: `[]`

---

## CRITICAL: Principle-Grounded vs. Anecdote-Grounded Reasoning

The `reasoning` field must contain TRANSFERABLE PRINCIPLES, not situation-specific explanations.

### ❌ WRONG (anecdote-grounded)
```
reasoning: "When Rochel described ignoring app notifications but responding 
to bot texts, she showed that the human-like interaction was the key factor."
```
*Problem: Tethered to Rochel's specific behavior. Not transferable.*

### ✅ RIGHT (principle-grounded)
```
reasoning: "Social obligation is a more reliable behavioral driver than utility 
reminders. Humans evolved to respond to perceived social bids—a text that feels 
like it came from a person activates reciprocity instincts that a notification 
cannot. This is the same mechanism that makes people answer phone calls but 
ignore voicemails."
```
*The anecdote (Rochel) is evidence in `source_excerpt`. The reasoning explains WHY this is true in general.*

---

## Examples

### Example 1: V_POSITION with full wisdom

**Input B32:**
```
## The Signaling Lag
Internal understanding of self often lags behind external market validation. 
V notes that external signals (like being treated as a peer by Ryan) act as 
"evidence" that forces an internal recalculation of one's own level. The 
provocation: we are often operating at a "higher level" than we internally 
believe until a formal institution validates it.
```

**Output:**
```json
[{
  "insight": "Internal self-assessment systematically lags external market signals. People often operate at a higher level than they believe until formal validation forces a recalculation of their self-model.",
  
  "reasoning": "Self-perception is anchored to past evidence and updates slowly. External signals (peer treatment, job offers, rate acceptance) provide objective market data that contradicts stale self-models. This is a form of imposter syndrome—but inverted: the 'imposter' feeling persists even when the market has already validated the new level. The lag exists because updating self-identity is psychologically costly; external validation reduces the cost.",
  
  "stakes": "For Careerspan: candidates need help recognizing when market signals indicate they should raise their level. For career coaching: explicit signal-gathering exercises can accelerate the internal update. The lag creates systematic underpricing of labor.",
  
  "conditions": "Applies to people who have recently leveled up but not yet internalized it. Less relevant for those with accurate self-models or those who over-estimate (Dunning-Kruger). Requires the person to trust the external signal source.",
  
  "source_excerpt": "V notes that external signals (like being treated as a peer by Ryan) act as 'evidence' that forces an internal recalculation of one's own level.",
  
  "speaker": "V",
  "v_stance": "endorsed",
  "domain": "worldview",
  "classification": "V_POSITION"
}]
```

### Example 2: SKIP (Question, no stance)

**Input B32:**
```
## 4. Supply-Side Job Ethics
Jake's concern about blasting 5,000 people when supply is limited highlights 
an ethical tension: is it better to give 5,000 people "hope" or to give 50 
people "results"?
```

**Output:**
```json
[]
```
*(This is a QUESTION—no stance is taken, just a tension identified.)*

### Example 3: EXTERNAL_WISDOM

**Input B32:**
```
## Low-Fidelity Architecture Strength
Kristen's observation that "AI means you can get to the answer with less 
infrastructure" — implying that scrappier, more improvised technical 
architectures may outperform over-engineered ones in an AI-augmented world.
```

**Output:**
```json
[{
  "insight": "In an AI-augmented world, low-fidelity technical architecture may outperform over-engineered systems. The marginal value of infrastructure decreases when AI can bridge gaps dynamically.",
  
  "reasoning": "Traditional software architecture optimizes for predictability and scale—expensive upfront investment that pays off over time. AI changes the calculus: gaps in infrastructure can be filled dynamically, reducing the penalty for 'scrappy' approaches. This shifts the optimal build strategy toward speed-to-learning rather than robustness.",
  
  "stakes": "Startups should bias toward shipping fast with AI-augmented duct tape rather than building 'proper' systems. Over-engineering is now more costly because the environment changes faster than infrastructure can adapt.",
  
  "conditions": "Applies when AI tools are reliable enough to bridge gaps. Breaks down for safety-critical systems, high-scale applications, or domains where AI capabilities are immature.",
  
  "source_excerpt": "Kristen's observation that 'AI means you can get to the answer with less infrastructure'",
  
  "speaker": "Kristen",
  "v_stance": "endorsed",
  "domain": "ai-automation",
  "classification": "EXTERNAL_WISDOM"
}]
```

---

## Quality Checklist

Before returning, verify each extraction:
- [ ] `insight` is 2-3 sentences (not a compressed one-liner)
- [ ] `reasoning` explains WHY via transferable principles (not anecdote-bound)
- [ ] `stakes` answers "so what?" with actionable implications
- [ ] `conditions` defines boundaries (not left empty)
- [ ] `source_excerpt` preserves the original evidence/anecdote

