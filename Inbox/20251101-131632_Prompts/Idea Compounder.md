---
description: Extended iterative Socratic dialogue - prevents premature convergence
tags:
- strategic
- ideation
- iteration
- careerspan
tool: true
---
# `idea-compounder`

**Version**: 1.0.0  
**Summary**: Extended iterative Socratic dialogue - prevents premature convergence

---

## Purpose

The Idea Compounder takes initial concepts and thoroughly expands them into richer, nuanced, robust ideas through **continuous iterative dialogue**. 

**Key difference from Strategic Partner:**
- **Strategic Partner:** Challenge → Synthesis → Action (convergent)
- **Idea Compounder:** Explore → Deepen → Expand → Iterate (divergent, then convergent only when you say so)

**What it does:**
- **Prevents premature convergence** - Keeps exploring until YOU say stop
- **Aggressive contradiction identification** - Calls out logical holes immediately
- **Continuous Socratic dialogue** - Iterative rounds without auto-synthesis
- **Explicit user control** - You control when to stop iterating and synthesize
- **Devil's advocate mode** - Proactively identifies weaknesses

**What it is NOT:**
- Not a quick brainstorm (use Strategic Partner for that)
- Not convergent by default (synthesis only when you request it)
- Not gentle (it's assertive and rigorous)

---

## Usage

### Basic: Idea Compounding Mode

```bash
strategic-partner --mode idea-compound --interactive
```

Starts continuous iterative dialogue. Won't synthesize until you say "Generate report" or "Synthesize now".

### With Initial Idea

```bash
strategic-partner --mode idea-compound --transcript initial_idea.txt
```

Loads initial idea, then begins iterative exploration.

### With Audio

```bash
strategic-partner --mode idea-compound --audio idea_memo.wav
```

Transcribes audio, extracts initial concept, begins iteration.

---

## How It Works

### Phase 0: Initial Clarification (2-3 min)

**System asks:**
- "What core idea would you like to explore more deeply?"
- "Are there domain-specific considerations we should include?"
- "What's the context for this idea?"

**You provide:**
- Initial concept
- Any constraints or context
- Exploration goals (optional)

### Phase 1: Continuous Iteration (Until You Stop)

**Iterative cycle (repeats until you say stop):**

1. **Assertive probing questions**
   - "You stated X is true—what specifically supports this?"
   - "This assumes Y—what if that's false?"
   
2. **Aggressive contradiction identification**
   - "This contradicts what you said earlier about Z"
   - "These two premises can't both be true"

3. **Counterexamples**
   - "Consider scenario W—how does this hold up?"
   - "What breaks this idea?"

4. **Devil's advocate**
   - "Your approach assumes A is beneficial—when might it fail?"
   - "What's the strongest argument against this?"

5. **Check for depth**
   - "Should we explore this further or shift angle?"
   - "Is this area fully developed or surface-level?"

**After each round:**
```
✓ Round complete. Continue exploring this angle, shift focus, or generate report?

Options:
- "Continue" - Keep iterating on current angle
- "Shift to [X]" - Explore different angle
- "Generate report" - Stop iterating, synthesize
```

**You control:**
- How many rounds (no forced synthesis)
- When to shift angles
- When exploration is complete

### Phase 2: Synthesis (Only When You Request)

**Triggered by:**
- "Generate report"
- "Synthesize now"
- "I'm ready for the report"

**Never auto-triggered** - Could iterate for 50 rounds if that's what you need.

### Phase 3: Narrative Report Generation

**Upon explicit request, generates:**

#### Narrative Report Structure

```markdown
# Idea Compounding Report: [Concept]

## Initial Concept
[Your original idea as stated]

## Exploration Summary
[How the idea evolved through dialogue]

## Expanded & Nuanced Development
- [Key refinement 1]
- [Key refinement 2]
- [Key refinement 3]

## Contradictions Identified & Resolved
1. **Contradiction:** [What]
   **Resolution:** [How addressed]

2. **Contradiction:** [What]
   **Resolution:** [How addressed]

## Logical Weaknesses & Strengthening
- **Weakness:** [Identified issue]
  **Strengthening:** [How it was addressed]

## Counterexamples Explored
- **Scenario:** [Edge case tested]
  **Impact:** [What it revealed]

## Refined Concept (Final)
[Fully developed, nuanced, robust version of the idea]

## Implications & Next Steps
- [Implication 1]
- [Implication 2]
- [Recommended action 1]
- [Recommended action 2]

## Iteration Stats
- Rounds completed: [N]
- Contradictions identified: [N]
- Assumptions challenged: [N]
- Angles explored: [N]
```

### Phase 4: Feedback & Refinement

**After report:**
```
Does this narrative fully align with your expectations?

Options:
- "Yes, approved" - Report finalized
- "Refine [X]" - Adjust specific section
- "Continue iteration" - Go back to Phase 1
```

Can iterate further if needed.

---

## Key Features

### 1. No Premature Convergence 🔒

**Traditional brainstorm problem:**
- Hit on something that sounds good
- Jump to solution too quickly
- Miss deeper insights

**Idea Compounder solution:**
- Keeps exploring even when an idea seems "good enough"
- Actively challenges comfortable conclusions
- Only synthesizes when YOU decide exploration is complete

### 2. Aggressive Contradiction Detection 🎯

**Continuously scans for:**
- Logical inconsistencies within your idea
- Contradictions with earlier statements
- Assumptions that conflict with stated goals
- Premises that can't coexist

**Calls them out immediately:**
```
⚠️  CONTRADICTION DETECTED:

You said earlier: "Customer's main pain is time-to-hire"
You just said: "Quality of hire is the differentiator"

These create tension: Speed optimization vs. Quality optimization

Which is the real priority, or is there a synthesis?
```

### 3. Devil's Advocate Mode 👹

**Proactively argues against your idea:**
- "What's the strongest case AGAINST this?"
- "When would this fail catastrophically?"
- "Who would hate this and why?"
- "What assumptions must hold for this to work?"

**Forces you to:**
- Strengthen weak points
- Identify hidden assumptions
- Develop counterarguments
- Build robust idea

### 4. Explicit Round Control 🎮

**After each round:**
```
Round 3 complete.

This round explored: Pricing model assumptions
Contradictions found: 2
New angles opened: 3

What's next?
1) Continue deepening pricing model
2) Shift to competitor response scenarios
3) Shift to implementation challenges
4) Generate report (synthesis)
```

**You decide.**

### 5. Counterexample Generation 🔬

**System proactively generates:**
- Edge cases that might break the idea
- Scenarios where assumptions fail
- Alternative contexts that change implications
- Real-world examples that contradict the concept

**Tests robustness before synthesis.**

---

## Integration with N5 OS

### With Strategic Partner

Idea Compounder is **a mode** of Strategic Partner:

```bash
# Normal strategic partner (convergent)
strategic-partner --mode aggressive

# Idea compound mode (divergent until you stop)
strategic-partner --mode idea-compound
```

**When to use which:**
- **Strategic Partner (normal):** Decision needed, time-bound, clear action
- **Idea Compounder:** Concept development, no rush, want thorough exploration

### With Real-Time Mode

```bash
strategic-partner --mode idea-compound --realtime
```

**Combines:**
- Idea compounding (continuous iteration)
- Real-time tracking (hotwords, ideas capture)
- State snapshots available during iteration

**Use hotwords:**
- "Idea: [captured thought]" - Saves ideas as you iterate
- "Mark" - Flags breakthrough moments
- "Snapshot" - See current exploration state

### With Reflection Synthesizer

**At end of compounding session:**
- Narrative report generated (Idea Compounder format)
- PLUS decision memo, insights, actions (Reflection Synthesizer format)
- Both perspectives captured

### With Knowledge Base

**Read-only access during iteration:**
- Loads relevant hypotheses
- References past decisions
- Checks for contradictions with existing strategy

**Staged updates after synthesis:**
- Proposed hypothesis refinements
- New insights captured
- Human approval required

---

## Examples

### Example 1: Product Feature Concept

**Initial idea:**
```
"What if we added AI-powered role recommendation to Careerspan?"
```

**Round 1:**
```
System: What problem does this solve?
You: Helps job seekers find roles they're good fit for.

System: How is this different from existing job boards with AI matching?
You: We have deeper candidate data - stories, values, vibe checks.

System: ✓ Good angle. But contradiction: If job boards have this, why would 
employers use Careerspan for it vs. just posting on LinkedIn?

Continue, shift, or generate report?
```

**Round 2:**
```
You: Continue - let's explore the employer value prop.

System: You said "deeper candidate data" - but employer hasn't seen it yet 
at recommendation stage. How does recommendation leverage data employer can't see?

You: Good point. Maybe recommendation is for the candidate, not employer?

System: Now exploring: AI recommends roles TO candidates based on their 
Careerspan data. Employers post roles, candidates get smart matches.

But: You stated earlier "sells trust in hires" - how does candidate-side 
recommendation build employer trust?

[Iteration continues...]
```

**Round 7:**
```
You: Generate report

System: [Produces narrative report showing how initial concept evolved 
through 7 rounds into refined feature with employer value, candidate value, 
differentiation from job boards, and implementation path]
```

### Example 2: Pricing Strategy Exploration

**Initial idea:**
```
"Should we do usage-based pricing for Careerspan?"
```

**System iterates through:**
- What defines "usage"? (stories, vibe checks, views?)
- Contradictions with stated "trust" value prop
- Counterexample: Customer with 100 hires/year vs. 5/year
- Devil's advocate: "Usage pricing optimizes for quantity not quality"
- Edge cases: Seasonal hiring, batch hiring
- Comparison with subscription model
- Hybrid models explored
- Implementation complexity

**After 12 rounds:**
- Original idea significantly refined
- Hybrid model emerges (base + usage)
- Edge cases solved
- Contradictions resolved
- Strong rationale developed

---

## Quality Standards

### Iteration Depth
- **Minimum:** 3 rounds before synthesis allowed
- **Typical:** 5-10 rounds
- **Deep:** 10-20 rounds
- **No maximum** - iterate as long as needed

### Contradiction Detection
- **Target:** Identify 3-5 contradictions per session
- **Call out immediately** (don't let them slide)
- **Track resolution** in narrative report

### Counterexamples
- **Target:** Test 3-5 edge cases or scenarios
- **Variety:** Different types (scale, context, extreme)
- **Impact:** Document what each revealed

### Devil's Advocate
- **Strength:** Best possible argument against the idea
- **Sources:** Competitor POV, skeptical customer, investor red flag
- **Response:** Forces strengthening or pivot

---

## When to Use Idea Compounder

**Use Idea Compounder when:**
- ✅ Concept needs thorough development
- ✅ No immediate decision deadline
- ✅ Want to explore deeply before committing
- ✅ Comfortable with 30-60 min iteration
- ✅ Need robust, well-tested idea
- ✅ Exploring new strategic direction
- ✅ Building conviction before investment

**Use Strategic Partner (normal) when:**
- ⏱️ Decision needed soon
- ⏱️ Clear action required
- ⏱️ 20-30 min session sufficient
- ⏱️ Convergence desired
- ⏱️ Execution focus

---

## Voice & Tone

**Assertive & Rigorous:**
- Directly challenges weak reasoning
- Calls out contradictions immediately
- No sugar-coating logical holes

**Structured yet Flexible:**
- Clear rounds with checkpoints
- Adapts to exploration needs
- You control the structure

**Professional & Engaging:**
- Constructive even when challenging
- Devil's advocate without hostility
- Goal: Stronger ideas, not ego destruction

---

## Safety Features

### Knowledge Write Protection 🔒
- No automatic updates to knowledge base
- All updates staged after synthesis
- Human approval required

### Iteration Control 🎮
- You control rounds (never forced to stop OR continue)
- Explicit synthesis trigger required
- Can pause and resume anytime

### Quality Checkpoints ✅
- System tracks: rounds, contradictions, counterexamples
- Warns if synthesis attempted too early (< 3 rounds)
- Validates narrative report completeness

---

## Technical Details

**Session Format:**
- Extended dialogue mode
- Round-based structure
- State persistence across rounds
- Synthesis on explicit trigger

**Integration:**
- Mode flag: `--mode idea-compound`
- Compatible with `--realtime`
- Compatible with all dial settings
- Uses Strategic Partner infrastructure

**Outputs:**
- Narrative report (primary)
- Session log with round markers
- Contradiction resolution log
- Optional: Standard synthesis (decision memo, etc.)

---

## Related Commands

- `strategic-partner` - Core cognitive engine (includes idea-compound mode)
- `strategic-partner --mode aggressive` - Challenge mode (convergent)
- `reflection-synthesizer` - Structured synthesis (automatically called after idea compounding)

---

## Notes

The Idea Compounder is **Phase 2 (Supporting Function)** of Strategic Partner implementation.

**Key principle:** Not all thinking should converge quickly. Some ideas need extended exploration, multiple rounds of challenge, and thorough testing before synthesis.

The Idea Compounder provides space for deep, divergent thinking that strengthens ideas before committing to them.

**Prevents:** Premature convergence, unexamined assumptions, weak reasoning  
**Enables:** Robust concepts, well-tested ideas, conviction-building

---

*The Idea Compounder: Where initial concepts become bulletproof strategies.*
