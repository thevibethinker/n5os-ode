---
created: 2025-11-15
last_edited: 2025-11-15
version: 1.0
block_code: B28
block_name: WILDCARD
category: optional
---

# B28: Wildcard Block (Custom Analysis)

## Purpose

B28 is NOT a predefined block type. It's a **flexibility mechanism** for meetings that contain intelligence not covered by the canonical 20 blocks.

## When to Use

Use B28 (or unnumbered custom blocks) when:
1. You analyze a meeting transcript
2. You identify valuable intelligence that doesn't fit existing blocks
3. The intelligence is significant enough to warrant dedicated extraction
4. No existing B01-B27 block type adequately captures it

## Examples of Wildcard Usage

**Meeting about legal contract negotiation:**
- Create: `B28_LEGAL_RISK_ANALYSIS`
- Contains: Contract clauses discussed, legal concerns, compliance requirements

**Meeting about product design:**
- Create: `B28_DESIGN_REQUIREMENTS`
- Contains: UX specifications, design constraints, accessibility needs

**Meeting about fundraising:**
- Create: `B28_INVESTOR_SENTIMENT`
- Contains: Investor concerns, valuation discussions, due diligence requirements

**Meeting about M&A due diligence:**
- Create: `B28_DILIGENCE_FINDINGS`
- Contains: Red flags, verification needs, integration risks

## How to Invoke

When orchestrating block generation:

1. **After** selecting canonical blocks (B01-B27)
2. **Ask yourself:** "Is there significant intelligence in this meeting that none of the selected blocks will capture?"
3. **If YES:** 
   - Define the custom block name descriptively
   - Create appropriate extraction prompt on-the-fly
   - Generate as B28 or unnumbered block
4. **If NO:** Skip wildcard

## Quality Criteria

**Use wildcard when:**
- Intelligence is specific to meeting domain (legal, design, finance, etc.)
- It provides actionable value V can't get elsewhere
- It's substantial (not just 1-2 bullet points)

**Don't use wildcard for:**
- Information that fits in existing blocks (even if imperfectly)
- Speculation or low-confidence insights
- Redundant information already captured elsewhere
- Generic meeting observations

## Implementation Note

The wildcard is **orchestration logic**, not a fixed template. The system should:
1. Analyze meeting content semantically
2. Evaluate coverage of canonical blocks
3. Identify gaps in intelligence extraction
4. Dynamically create custom block if valuable
5. Generate with context-appropriate prompt

This allows the system to handle unforeseen meeting types without requiring new canonical blocks for every edge case.

