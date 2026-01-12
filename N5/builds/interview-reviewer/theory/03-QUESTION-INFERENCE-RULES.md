---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_UbZ5BSRD1yOMzrsF
---

# Question Inference Rules

**Purpose:** Define how to infer which competencies an interview question is testing.

---

## The Core Problem

Interviewers rarely say "I'm testing your stakeholder management skills." They ask:
> "Tell me about a time you had to get alignment from people who didn't report to you."

We need rules to **infer the true intent** from the surface question.

---

## Question Classification

### Step 1: Identify Question Type

| Type | Trigger Patterns | What It Tests |
|------|------------------|---------------|
| **Behavioral** | "Tell me about a time...", "Describe a situation where...", "Give me an example of..." | Past behavior → Future performance |
| **Situational** | "What would you do if...", "How would you handle...", "Imagine you're..." | Judgment, reasoning, values |
| **Competency** | "How do you approach [X]?", "What's your process for...", "How do you think about..." | Mental models, frameworks |
| **Technical** | Role-specific knowledge probes, "How does [X] work?", "Walk me through..." | Domain expertise |
| **Motivational** | "Why [company]?", "Why this role?", "Where do you see yourself..." | Fit, ambition, authenticity |
| **Cultural** | "How do you like to work?", "What kind of environment...", "Tell me about your ideal..." | Values, style, team fit |

### Step 2: Extract the Core Competency Probe

Once classified, extract what's being tested:

#### Behavioral Questions
Parse the situation descriptor:

| Situation Descriptor | Primary Competency | Secondary |
|---------------------|-------------------|-----------|
| "...had to influence without authority" | L02 | B02 |
| "...faced a tight deadline" | E03 | R03 |
| "...dealt with a difficult stakeholder" | C06, B03 | R03 |
| "...made a decision with incomplete information" | T06, L06 | |
| "...failed at something" | R06, R02 | R05 |
| "...led a team through change" | L03, L01 | C06 |
| "...had to prioritize competing demands" | E02 | L06 |
| "...disagreed with your manager" | C06 | R01 |
| "...had to learn something new quickly" | T05 | E05 |
| "...went above and beyond" | E01 | G01 |

#### Situational Questions
Parse the scenario for values/judgment being tested:

| Scenario Type | Tests |
|---------------|-------|
| Ethical dilemma | R01 (Integrity), L06 (Decision Making) |
| Resource constraint | E02 (Prioritization), E05 (Resourcefulness) |
| Team conflict | B03 (Conflict Resolution), C06 (Difficult Conversations) |
| Ambiguous problem | T06 (Judgment Under Uncertainty), T03 (Creative Problem Solving) |
| Stakeholder pressure | B02 (Stakeholder Management), R03 (Resilience) |

#### Motivational Questions
These always test the same competencies:

| Question | Tests |
|----------|-------|
| "Why this company?" | G04 (Company Fit), research effort |
| "Why this role?" | G03 (Role Fit), self-awareness |
| "Where do you see yourself in X years?" | G01 (Ambition), G02 (Potential) |
| "What are you looking for?" | G03, R05 (Self-Awareness) |

---

## Keyword → Competency Mapping

When a question contains these keywords, weight the associated competencies:

### Action Keywords
| Keyword | Competencies |
|---------|-------------|
| lead, led, leading | L01, L02, L03 |
| manage, managed | L01, B02, E02 |
| influence, persuade, convince | L02, C01, C05 |
| build, built, create | E01, E05 |
| analyze, analyzed | T01, T04 |
| decide, decision | L06, T06 |
| prioritize | E02 |
| collaborate, partner | B01, B02 |
| communicate, present | C01, C03 |
| solve, resolved | T03, B03 |

### Context Keywords
| Keyword | Competencies |
|---------|-------------|
| stakeholder | B02 |
| cross-functional | B02, L02 |
| deadline, timeline | E03, E02 |
| ambiguous, unclear | T06 |
| conflict, disagreement | B03, C06 |
| failure, mistake | R06, R02, R05 |
| feedback | C06, R02 |
| strategy, strategic | T02 |
| data, metrics | T01 |
| customer, client, user | B05 |

### Difficulty Modifiers
| Modifier | Implication |
|----------|-------------|
| "most challenging" | Probing upper limit of competency |
| "proudest" | Values, self-concept |
| "recent" | Current capability, not historical |
| "biggest" | Scale, impact, stakes |

---

## Confidence Scoring

Not all inferences are equally confident. Score each inference:

### High Confidence (0.8-1.0)
- Explicit competency language ("...demonstrate leadership...")
- Well-known behavioral question patterns
- Direct skill probes ("How do you prioritize?")

### Medium Confidence (0.5-0.7)
- Implied through context
- Multiple possible interpretations
- Compound questions testing several things

### Low Confidence (0.3-0.4)
- Very open-ended questions
- Novel or unusual phrasing
- Cultural/fit questions with unclear intent

### Flag for Human (< 0.3)
- Can't determine intent
- Technical domain outside our ontology
- Possible small talk / not a real question

---

## Question Sequence Analysis

Questions don't exist in isolation. The sequence reveals strategy:

### Pattern: Funnel
```
General → Specific → Very Specific
"Tell me about yourself" → "You mentioned project X, tell me more" → "What was your specific role in the database migration?"
```
**Intent:** Verify claims, probe for depth vs breadth

### Pattern: Stress Test
```
Easy → Hard → Harder
"Tell me about a success" → "Tell me about a failure" → "What would you do differently?"
```
**Intent:** Test self-awareness, honesty, resilience

### Pattern: Multi-Angle
```
Same competency from different angles
"How do you prioritize?" → "Tell me about a time you had too much on your plate" → "How do you decide what NOT to do?"
```
**Intent:** Cross-validate, test consistency

### Pattern: Red Flag Follow-Up
```
Question → Follow-up drilling into concerning answer
"Tell me about X" → [candidate gives vague answer] → "Can you be more specific about YOUR role?"
```
**Intent:** Interviewer detected RF-1 (Invisible I) and is probing

---

## The Full Inference Pipeline

```
Input: "Tell me about a time you had to get buy-in from stakeholders who were resistant to change"

Step 1: Classify
→ Behavioral (trigger: "Tell me about a time")

Step 2: Extract situation descriptor
→ "get buy-in from stakeholders who were resistant to change"

Step 3: Keyword extraction
→ "buy-in" (persuasion), "stakeholders" (cross-functional), "resistant" (conflict)

Step 4: Map to competencies
→ L02 (Influence Without Authority): 0.9
→ B02 (Stakeholder Management): 0.85
→ C06 (Difficult Conversations): 0.6
→ B03 (Conflict Resolution): 0.5

Step 5: Consider context
→ If PM role: weight B02 higher
→ If senior level: weight L02 higher

Output:
{
  "questionType": "behavioral",
  "surfaceQuestion": "Tell me about a time you had to get buy-in from stakeholders who were resistant to change",
  "trueIntent": "Assess ability to influence without authority and manage resistant stakeholders",
  "competenciesTested": [
    {"id": "L02", "name": "Influence Without Authority", "confidence": 0.9},
    {"id": "B02", "name": "Stakeholder Management", "confidence": 0.85},
    {"id": "C06", "name": "Difficult Conversations", "confidence": 0.6}
  ],
  "evaluationFocus": [
    "Did they identify the stakes (why buy-in mattered)?",
    "Did they explain their influence strategy (not just the outcome)?",
    "Did they show empathy for the resistant stakeholders' perspective?"
  ]
}
```

---

## Edge Cases

### Technical Questions
Flag but don't deeply analyze:
```
{
  "questionType": "technical",
  "note": "Technical questions are outside coaching scope. Flagged for awareness.",
  "competenciesTested": [{"id": "D01", "name": "Technical Depth", "confidence": 0.5}]
}
```

### Small Talk
Filter out:
- "How was your commute?"
- "Did you find the office okay?"
- "Would you like water?"

### Compound Questions
Split and analyze separately:
```
"Tell me about yourself and why you're interested in this role"
→ Split into:
  1. "Tell me about yourself" (Motivational/Overview)
  2. "Why you're interested in this role" (G03, G04)
```

---

## Connecting to JD Requirements

After inferring competencies from all questions, compare to JD:

```
JD Required: [L02, B02, E03, D03, G04]
Questions Asked: [L02, B02, T01, G03, G04]

Coverage Analysis:
✓ L02 - Required and tested
✓ B02 - Required and tested
✗ E03 - Required but NOT tested (gap: interviewer didn't probe execution speed)
✗ D03 - Required but NOT tested (gap: no technical depth questions)
✓ G04 - Required and tested
+ T01 - Tested but not explicitly required (bonus or interviewer preference)
+ G03 - Tested but not explicitly required (standard motivational)
```

This feeds directly into the **Bidirectional Gap Analysis** in the coaching reference.

---

*Version 1.0 | January 2026*

