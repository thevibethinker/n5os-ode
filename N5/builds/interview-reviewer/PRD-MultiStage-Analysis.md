---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.2
provenance: con_F2njykPaFaBaNmKN
---

# PRD: Multi-Stage Analysis Pipeline

**Product:** Am I Hired?  
**Feature:** Multi-stage interview analysis with JD mapping, calibration, and growth mechanics  
**Status:** Approved for implementation  
**Decision Date:** 2026-01-12

---

## Executive Summary

Replace the current single-shot OpenAI analysis with a 5-stage pipeline that delivers:
1. Structured extraction of Q&A pairs
2. Question classification mapped to JD requirements
3. Answer evaluation against V's coaching rubrics
4. Gap analysis + candidate self-perception calibration
5. Synthesized report with actionable feedback

Additionally: Update form fields, add growth mechanic (free-for-feedback offer), and improve output visualization.

---

## Form Changes

### Current Form
```
Company (text) → Sentiment (dropdown: positive/mixed/negative) → Transcript (textarea)
```

### New Form
```
Company (text) → Job Description (textarea, REQUIRED) → Self-Assessment (textarea) → Transcript (textarea)
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company` | text | Yes | Company name |
| `jobDescription` | textarea | **Yes** | Full JD or key requirements — enables question mapping |
| `selfAssessment` | textarea | Yes | Free-form: "How do you feel it went? What are you worried about?" |
| `transcript` | textarea | Yes | Interview transcript |

**Rationale:** 
- JD is required because it produces dramatically better analysis (maps questions → requirements)
- Self-assessment replaces the sentiment dropdown — captures nuance for calibration
- Both are processed ephemerally (same privacy model as transcript)

---

## Analysis Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT                                    │
│  transcript + jobDescription + selfAssessment + company          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 1: EXTRACT Q&A                          [gpt-5.1-mini]   │
│  ─────────────────────────────────────────────────────────────  │
│  Input: Raw transcript                                          │
│  Output: Structured array of {question, answer, speaker, index} │
│  Task: Parse transcript, identify interviewer vs candidate,     │
│        extract clean Q&A pairs                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 2: QUESTION ANALYSIS                    [gpt-5.1]        │
│  ─────────────────────────────────────────────────────────────  │
│  Input: Q&A pairs + Job Description                             │
│  Output: Each question annotated with:                          │
│    - type: behavioral | situational | competency | cultural     │
│    - jd_requirement_mapped: which JD requirement it probes      │
│    - priority: high | medium | low (inferred from JD)           │
│  Note: Technical questions flagged as OUT_OF_SCOPE              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 3: ANSWER EVALUATION                    [gpt-5.1]        │
│  ─────────────────────────────────────────────────────────────  │
│  Input: Annotated Q&A pairs + Coaching Reference                │
│  Output: Each answer scored against:                            │
│    - 6 Questions Framework (Problem, Stakes, Thinking,          │
│      Action, Result, Lesson)                                    │
│    - Red Flags (RF-1 through RF-10)                             │
│    - Green Flags (GF-1 through GF-10)                           │
│    - Specificity score (1-5)                                    │
│    - Overall grade (A/B/C/D/F)                                  │
│  This is the CORE VALUE stage — deep reasoning required         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 4: GAP + CALIBRATION ANALYSIS           [gpt-5.1]        │
│  ─────────────────────────────────────────────────────────────  │
│  Input: Question analysis + Answer evaluation + JD +            │
│         Self-assessment                                         │
│  Output:                                                        │
│    - gap_analysis: JD requirements NOT demonstrated             │
│    - coverage_analysis: JD requirements demonstrated            │
│    - calibration: {                                             │
│        self_perception: summary of how they think it went       │
│        actual_performance: summary of how it actually went      │
│        delta: optimistic | realistic | pessimistic              │
│        insight: personalized observation                        │
│      }                                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 5: SYNTHESIS                            [gpt-5.1]        │
│  ─────────────────────────────────────────────────────────────  │
│  Input: All previous stage outputs                              │
│  Output: Final report with:                                     │
│    - Executive summary (2-3 sentences)                          │
│    - Question breakdown pie chart data                          │
│    - Answer-by-answer feedback (top 5 most important)           │
│    - Gap analysis summary                                       │
│    - Calibration insight (gentle, constructive)                 │
│    - Top 3 actionable improvements                              │
│    - Overall verdict with confidence                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         OUTPUT                                   │
│  Rendered HTML report + structured JSON for visualization       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Model Selection

| Stage | Model | Rationale |
|-------|-------|-----------|
| 1. Extract Q&A | `gpt-5.1-mini` | Structured extraction, doesn't need deep reasoning |
| 2. Question Analysis | `gpt-5.1` | Needs judgment to classify and map to JD |
| 3. Answer Evaluation | `gpt-5.1` | Core value — must apply rubrics with nuance |
| 4. Gap + Calibration | `gpt-5.1` | Comparative analysis, needs reasoning |
| 5. Synthesis | `gpt-5.1` | Report quality matters, needs coherent writing |

**Cost estimate per analysis:** ~$0.50-1.00 (at current gpt-5.1 pricing)  
**Margin at $5:** ~$4.00-4.50 (80-90%)  
**Decision:** Quality first — can optimize costs after validating reception

---

## Question Type Taxonomy

| Type | Description | Scope |
|------|-------------|-------|
| `behavioral` | "Tell me about a time when..." — STAR/6Q applies | ✅ In scope |
| `situational` | "What would you do if..." — hypothetical scenarios | ✅ In scope |
| `competency` | "Describe your experience with..." — skill probing | ✅ In scope |
| `cultural` | "Why us?" / "What motivates you?" — fit questions | ✅ In scope |
| `technical` | Coding, system design, domain-specific knowledge | ❌ Out of scope |
| `logistical` | Salary, availability, location | ❌ Out of scope |

**Technical question handling:**
- Flagged as `OUT_OF_SCOPE` in Stage 2
- Not evaluated in Stage 3
- Shown in report: "We identified X technical questions — these are outside our analysis scope"
- Still counted in pie chart breakdown

---

## Output: Report Structure

### 1. Executive Summary
> Based on your interview at [Company] for [Role], you demonstrated strong [X] but have room to improve on [Y]. Our calibration suggests you're [more pessimistic than warranted / appropriately calibrated / slightly overconfident].

### 2. Question Breakdown (Pie Chart)
```
Behavioral: 40% (4 questions)
Situational: 20% (2 questions)
Competency: 20% (2 questions)
Cultural: 10% (1 question)
Technical: 10% (1 question) — not analyzed
```

### 3. JD Coverage Map
```
✅ Demonstrated: Leadership, Problem-solving, Communication
⚠️ Partially covered: Strategic thinking
❌ Not addressed: Stakeholder management, Budget experience
```

### 4. Answer-by-Answer Feedback (Top 5)
For each critical Q&A:
- The question (classified)
- What they said (summary)
- What was good (green flags)
- What was missing (red flags, 6Q gaps)
- How to improve

### 5. Calibration Insight
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Self-Perception Calibration

You said: "I think it went okay but I rambled too much 
on the leadership question and probably came across as 
nervous."

Our analysis: You actually performed well on the 
leadership question — your STAR structure was solid. 
The nervousness you perceived didn't come through in 
the transcript. You're being harder on yourself than 
the evidence warrants.

Calibration: Slightly pessimistic ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6. Top 3 Improvements
Concrete, actionable recommendations

### 7. Verdict
```
Overall Assessment: B+ (Strong with specific gaps)
Hire Likelihood: Moderate-High (65-75%)
Key Risk: [specific gap identified]
```

---

## Growth Mechanic: Feedback Loop

### Goal
Turn early users into product advocates by trading detailed feedback for free analyses.

### Mechanism

**On Results Page:**
```
📬 Help us improve!
Your session: AMH-7K2X-9M4P

Email us at feedback@careerspan.io with:
- This session ID
- What worked well
- What could be better

In return, we'll send you a promo code for free analyses for 90 days.
```

**Promo Code System:**
- **Format:** `THANKS-XXXX` (e.g., `THANKS-7K2X`)
- **Validity:** 90 days from issue
- **Scope:** 5 analyses per code during validity period
- **Generation:** Manual initially — V reviews feedback, generates code, emails back
- **Tracking:** Simple spreadsheet with columns: `session_id | email | feedback_summary | code_issued | issued_date | expires_date | uses_remaining`

**Form Integration (Phase 4.5):**
- Add optional "Promo Code" field to form
- If valid code entered → bypass payment, proceed to analysis
- Log usage: `code | used_date | session_id`

### Implementation Notes
- Promo codes stored in simple JSON file or SQLite table
- No Stripe integration needed — code validation happens before payment redirect
- Invalid/expired codes show friendly error, redirect to normal payment flow

---

## 9. Confirmed Decisions

| Decision | Confirmed Value |
|----------|-----------------|
| Pricing | $5 (unchanged) |
| JD field | Required |
| Sentiment field | Free-form selfAssessment |
| Free pass mechanism | Promo code (90 days, 5 uses) |
| Model - Stage 1 | gpt-5.1-mini |
| Model - Stages 2-5 | gpt-5.1 |
| Technical questions | Out of scope (acknowledged in output) |
| Inbound monitoring | Manual initially, tracking sheet |

---

## Technical Implementation

### New Files
```
Sites/interview-reviewer-staging/src/lib/
├── pipeline/
│   ├── index.ts           # Pipeline orchestrator
│   ├── stage1-extract.ts  # Q&A extraction
│   ├── stage2-questions.ts # Question analysis
│   ├── stage3-answers.ts  # Answer evaluation
│   ├── stage4-gaps.ts     # Gap + calibration
│   └── stage5-synthesis.ts # Report synthesis
├── types/
│   └── pipeline.ts        # TypeScript interfaces for all stages
└── openai.ts              # Updated to support different models per call
```

### Interface Contracts

```typescript
// Stage 1 Output
interface ExtractedQA {
  index: number;
  speaker: 'interviewer' | 'candidate';
  question: string;
  answer: string;
  timestamp?: string;
}

// Stage 2 Output
interface AnalyzedQuestion extends ExtractedQA {
  type: 'behavioral' | 'situational' | 'competency' | 'cultural' | 'technical' | 'logistical';
  jdRequirementMapped: string | null;
  priority: 'high' | 'medium' | 'low';
  inScope: boolean;
}

// Stage 3 Output
interface EvaluatedAnswer extends AnalyzedQuestion {
  sixQuestionsScore: {
    problem: boolean;
    stakes: boolean;
    thinking: boolean;
    action: boolean;
    result: boolean;
    lesson: boolean;
  };
  redFlags: string[];  // e.g., ["RF-3: Vague quantification"]
  greenFlags: string[]; // e.g., ["GF-1: Strong opening hook"]
  specificityScore: 1 | 2 | 3 | 4 | 5;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  feedback: string;
}

// Stage 4 Output
interface GapAnalysis {
  demonstrated: string[];      // JD requirements covered
  partiallyDemonstrated: string[];
  notDemonstrated: string[];   // Gaps
  calibration: {
    selfPerception: string;
    actualPerformance: string;
    delta: 'optimistic' | 'realistic' | 'pessimistic';
    insight: string;
  };
}

// Stage 5 Output (Final Report)
interface AnalysisReport {
  executiveSummary: string;
  questionBreakdown: Record<string, number>;  // For pie chart
  jdCoverage: GapAnalysis;
  topAnswers: EvaluatedAnswer[];  // Top 5 most important
  calibrationInsight: string;
  topImprovements: string[];
  verdict: {
    grade: string;
    hireLikelihood: string;
    keyRisk: string;
  };
  sessionId: string;
}
```

---

## Migration Path

### Phase 1: Form Updates (Quick)
1. Change JD field from optional → required
2. Replace sentiment dropdown with selfAssessment textarea
3. Update validation and submission handler

### Phase 2: Pipeline Infrastructure (Medium)
1. Create pipeline directory structure
2. Implement Stage 1 (extraction) with gpt-5.1-mini
3. Create pipeline orchestrator with model routing
4. Test Stage 1 in isolation

### Phase 3: Core Analysis Stages (Heavy)
1. Implement Stage 2 (question analysis)
2. Implement Stage 3 (answer evaluation) — most complex
3. Implement Stage 4 (gap + calibration)
4. Test stages 2-4 in sequence

### Phase 4: Synthesis + Output (Medium)
1. Implement Stage 5 (synthesis)
2. Design and implement new report template
3. Add pie chart visualization (client-side JS or SVG)
4. Add session ID generation and display

### Phase 5: Growth Mechanic (Light)
1. Generate memorable session IDs
2. Add feedback CTA to results page
3. Store session ID in database
4. Document manual email processing workflow

---

## Success Criteria

1. **Accuracy:** Analysis correctly identifies question types and applies rubrics
2. **Calibration:** Self-perception comparison feels insightful, not judgmental
3. **Actionability:** User knows exactly what to improve
4. **Reception:** First 10 users report high satisfaction (qualitative feedback)
5. **Performance:** Full analysis completes in <60 seconds

---

## Appendix: Coaching Reference Dependencies

This pipeline relies on content from:
- `content/coaching-reference.md` — 6 Questions framework, Red/Green flags
- V's coaching methodology for evaluation criteria

Ensure this content is populated before Stage 3 implementation.




