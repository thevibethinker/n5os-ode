---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.1
provenance: con_UbZ5BSRD1yOMzrsF
---

# Sync Document: Interview Reviewer Theory Work

> **Note:** This is a **sync artifact** to keep the parent conversation informed. Work is ongoing in this conversation.

**Source Conversation:** con_UbZ5BSRD1yOMzrsF  
**Parent Conversation:** con_g62UmSAYGCHuZjmN  
**Date:** 2026-01-12  
**Builder:** Zo (Vibe Builder persona)

---

## Summary

This conversation completed the **intellectual framework** for the Am I Hired? interview analysis tool. V provided a data dump of 23+ coaching documents. We extracted the relevant interview theory, built the coaching reference, and drafted the JD decomposition rules.

---

## Artifacts Created

### 1. Coaching Reference (COMPLETE)
**Location:** `Sites/interview-reviewer-staging/src/content/coaching-reference.md`

Contains 6 parts:
- **Part I: Philosophy** — The Bragging Paradox, Composite Candidate Model (4 Cs)
- **Part II: Evaluation Framework** — 6-Point "Art of The Brag" rubric
- **Part III: JD Integration** — Requirement mapping framework
- **Part IV: Red Flags Catalog** — RF-1 through RF-10 with patterns and feedback templates
- **Part V: Question Decomposition** — Question taxonomy (Behavioral, Situational, Competency, Cultural, Technical), OPM proficiency scale, True Intent vs Surface Intent framework
- **Part VI: Bidirectional Gap Analysis** — Coverage analysis + proactive surfacing advice

### 2. JD Decomposition Theory (COMPLETE)
**Location:** `N5/builds/interview-reviewer/theory/01-JD-DECOMPOSITION.md`

Defines:
- Signal layers (Hard, Soft, Experience, Outcome, Implied)
- Noise layers (Boilerplate, Fluff, Kitchen Sink)
- Extraction rules (Priority by Position, Verb Analysis, Quantifier Detection, Synonym Normalization, Implicit Extraction)
- Output schema (TypeScript interface)
- JD Quality assessment rubric

### 3. OpenAI Engine (UPDATED)
**Location:** `Sites/interview-reviewer-staging/src/lib/openai.ts`

Updated to:
- Load coaching reference content
- Support optional JD parameter
- Build enhanced system prompts with JD context
- Include bidirectional gap analysis instructions

### 4. Form (UPDATED)
**Location:** `Sites/interview-reviewer-staging/src/index.tsx`

Added:
- Optional JD textarea field (to be made REQUIRED per V's decision)
- JD passed through session store
- JD passed to analysis function

---

## Theory Documents

### 01-JD-DECOMPOSITION.md ✅ COMPLETE
**Location:** `N5/builds/interview-reviewer/theory/01-JD-DECOMPOSITION.md`

Defines:
- Signal layers (Hard, Soft, Experience, Outcome, Implied)
- Noise layers (Boilerplate, Fluff, Kitchen Sink)
- Extraction rules (Priority by Position, Verb Analysis, Quantifier Detection, Synonym Normalization, Implicit Extraction)
- Output schema (TypeScript interface)
- JD Quality assessment rubric

### 02-COMPETENCY-ONTOLOGY.md ✅ COMPLETE
**Location:** `N5/builds/interview-reviewer/theory/02-COMPETENCY-ONTOLOGY.md`

Defines:
- 8 competency clusters (Execution, Leadership, Communication, Collaboration, Thinking, Character, Domain, Trajectory)
- ~60 canonical competencies with IDs, synonyms, and assessment indicators
- Synonym resolution rules (exact match, phrase patterns, context clues, cluster affinity)
- How the ontology connects JD → Questions → Evaluation

### 03-QUESTION-INFERENCE-RULES.md ✅ COMPLETE
**Location:** `N5/builds/interview-reviewer/theory/03-QUESTION-INFERENCE-RULES.md`

Defines:
- Question type classification (Behavioral, Situational, Competency, Technical, Motivational, Cultural)
- Situation descriptor → Competency mapping tables
- Keyword → Competency mapping
- Confidence scoring rules
- Question sequence pattern analysis
- Full inference pipeline with example
- Edge case handling (technical questions, small talk, compound questions)
- JD requirement connection logic

---

## Theory Stack Status

| Document | Status | Content |
|----------|--------|---------|
| 01-JD-DECOMPOSITION | ✅ Complete | JD parsing rules, signal/noise separation |
| 02-COMPETENCY-ONTOLOGY | ✅ Complete | 60 competencies, 8 clusters, synonym resolution |
| 03-QUESTION-INFERENCE-RULES | ✅ Complete | Question→Competency inference, confidence scoring |
| coaching-reference.md | ✅ Complete | 6-part evaluation framework |

**All theory content is now complete.** Ready for implementation.

---

## Key Decisions Made

| Decision | Value | Rationale |
|----------|-------|-----------|
| JD field | **Required** | Dramatically improves analysis quality |
| Self-assessment | Free-form textarea | Captures nuance for calibration |
| Technical questions | Out of scope | Flagged, not evaluated |
| JD quality | Assessed and surfaced | Low-quality JDs get disclaimer |
| Gap analysis | Bidirectional | Both "what you missed" and "what they didn't ask" |

---

## V's Key Guidance (Quotes)

On gap analysis:
> "Was there an opportunity to illustrate those gaps? If the JD emphasized cross-functional leadership and no question was asked to demonstrate stakeholder management, then surface that."

On JD parsing:
> "Anything that's corporate speak just ignore... you can be honest and say how generic or informative it is. If it's super not informative, it can just be dropped."

On the goal:
> "Line it up with the interview and give them a sense of hey, did they even interview in accordance with what they said they care about."

---

## Background Worker Spawned

**Worker ID:** WORKER_zrsF_20260112_065411  
**Location:** `Records/Temporary/WORKER_ASSIGNMENT_20260112_065411_517923_zrsF.md`  
**Task:** Ingest all 23 coaching PDFs into `Knowledge/content-library/coaching/`  
**Status:** Pending execution (needs to be opened in new conversation)

---

## Next Steps (For Parent Conversation)

1. **Complete Theory Documents:**
   - Draft `02-COMPETENCY-ONTOLOGY.md`
   - Draft `03-QUESTION-INFERENCE-RULES.md`

2. **Update Form:**
   - Make JD field required (remove "optional" label, add validation)
   - Replace sentiment dropdown with selfAssessment textarea

3. **Implement Pipeline:**
   - Follow PRD phases 1-5
   - Stage 2 will consume the JD decomposition + competency ontology
   - Stage 3 will consume the coaching reference

4. **Execute Background Worker:**
   - Open worker assignment file in new conversation
   - This populates the long-term Knowledge library

---

## Files Changed This Session

```
Sites/interview-reviewer-staging/
├── src/
│   ├── index.tsx                    # Added JD field to form
│   ├── content/
│   │   └── coaching-reference.md    # MAJOR: Full framework (6 parts)
│   └── lib/
│       ├── openai.ts                # Updated prompts, JD support
│       └── session-store.ts         # (already supported JD)

N5/builds/interview-reviewer/
├── theory/
│   ├── 01-JD-DECOMPOSITION.md       # NEW: JD parsing rules
│   └── HANDOFF-con_UbZ5BSRD1yOMzrsF.md  # THIS FILE
├── STATUS.md                        # Updated to Phase 3 complete
└── PRD-MultiStage-Analysis.md       # (unchanged, referenced)
```

---

## How to Continue

To resume this work in a new conversation:

1. Reference this handoff document
2. Reference the PRD: `N5/builds/interview-reviewer/PRD-MultiStage-Analysis.md`
3. Reference the coaching reference: `Sites/interview-reviewer-staging/src/content/coaching-reference.md`
4. Continue with theory document #2 (Competency Ontology)

---

*Generated 2026-01-12 02:45 ET*


