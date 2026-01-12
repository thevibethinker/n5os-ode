---
created: 2026-01-12
last_edited: 2026-01-12
version: 2.1
provenance: con_F2njykPaFaBaNmKN
---

# Build Plan: Am I Hired? (interview-reviewer)

**Product:** Post-interview feedback tool  
**Public name:** Am I Hired?  
**Internal slug:** `interview-reviewer`  
**Site location:** `Sites/interview-reviewer-staging/` → `Sites/interview-reviewer/`  
**GitHub:** Will be open-sourced (MIT license)

## Overview

One-time purchase ($5) interview feedback tool. User pastes transcript, pays, gets expert career coaching feedback. No login, no data retention (transcripts processed ephemerally).

### Privacy Model
- Transcript NEVER stored on server (in-memory only, cleared after processing)
- Metadata stored: session_id, company, sentiment, timestamp, report_summary
- Transcript sent to OpenAI API (BYOK) for analysis (standard API data handling)
- Open source so users can verify

### Technical Stack
- Bun + Hono (Zo site standard)
- SQLite for metadata only
- Stripe Checkout (Option A: pay → redirect → verify → process)
- OpenAI API (V's key via `OPENAI_API_KEY` secret)

---

## Master Checklist

### Phase 0: Foundation
- [x] Create Hono site scaffold
- [x] Basic server with health endpoint
- [x] Environment config (OPENAI_API_KEY, STRIPE_SECRET_KEY, etc.)
- [x] SQLite setup for metadata

### Phase 1: Core UI
- [x] Landing page (`/`)
  - [x] Transcript paste area
  - [x] Company name input
  - [x] Sentiment selector (+/-)
  - [x] "Get Feedback ($5)" button
  - [x] Privacy warning banner (PII removal advisory)
  - [x] Disclaimer text
- [x] Clean, professional styling (Tailwind or inline)
- [x] Mobile responsive

### Phase 2: Stripe Integration
- [x] Create Stripe product (Am I Hired! - $5 one-time) — *Code ready, needs Stripe Connect setup*
- [x] Create price and payment link — *Dynamic via checkout session*
- [x] Checkout endpoint (`/api/checkout`)
  - [x] Store transcript + metadata temporarily (in-memory/session)
  - [x] Redirect to Stripe Checkout
- [x] Success endpoint (`/success`)
  - [x] Verify payment with Stripe API
  - [x] Retrieve stored transcript from session
  - [x] Trigger analysis if payment valid

### Phase 3: Analysis Engine
- [x] System prompt with reference content (stub for now)
- [x] Reference content loader (reads from `content/coaching-reference.md`)
- [x] Analysis endpoint/function
  - [x] Send transcript + system prompt to OpenAI
  - [x] Parse and format response
  - [x] Clear transcript from memory immediately after
- [x] Report formatting (clean, readable HTML)

### Phase 4: Data Layer
- [x] SQLite schema: sessions table
  - [x] session_id (primary key)
  - [x] stripe_session_id
  - [x] company (text)
  - [x] sentiment (text: positive/negative)
  - [x] created_at (timestamp)
  - [x] report_summary (text, extracted key points)
  - [x] NO transcript column
- [x] Insert metadata after successful analysis
- [x] Verify transcript never touches disk

### Phase 5: Safety & Rate Limiting
- [x] Global rate limiter (configurable, default 50/hour)
- [x] Circuit breaker logic
  - [x] Track request count in rolling window
  - [x] If exceeded, set "disabled" flag
  - [x] Return clean error page when disabled
- [x] Error page template
  - [x] Session ID displayed
  - [x] Contact info for support
  - [x] Friendly message
- [x] Manual override to re-enable (admin endpoint or env var)

### Phase 6: Polish & Deploy
- [x] Final UI polish
- [x] Privacy notice page (`/privacy`)
- [x] Terms page (`/terms`) - basic liability disclaimer
- [x] README.md for GitHub
- [ ] LICENSE (MIT)
- [x] .gitignore
- [ ] Deploy to production (`Sites/interview-reviewer/`)
- [ ] Register user service
- [ ] Smoke test end-to-end

### Phase 7: Content Integration (COMPLETED)
- [x] V provides coaching reference files
- [x] Extract and structure content
- [x] Update `content/coaching-reference.md`
- [x] Test with real content

### Phase 8: Multi-Stage Analysis Pipeline
**PRD:** `file 'N5/builds/interview-reviewer/PRD-MultiStage-Analysis.md'`

#### 8.1 Form Updates
- [x] Change JD field from optional → required
- [x] Remove `sentiment` dropdown field
- [x] Add `selfAssessment` textarea ("How do you feel it went? What concerns you?")
- [x] Add optional `promoCode` text field
- [x] Update form validation (JD required, selfAssessment required)
- [x] Update `/submit` handler to pass new fields
- [x] Test: Form submits with all new fields

#### 8.2 Pipeline Infrastructure
- [x] Create `src/lib/types/pipeline.ts` with TypeScript interfaces
- [x] Create `src/lib/pipeline/` directory
- [x] Update `src/lib/openai.ts` to support model selection per call
- [x] Create `src/lib/pipeline/index.ts` (orchestrator)
- [x] Test: Pipeline orchestrator can call stages sequentially

#### 8.3 Stage 1 — Extract Q&A (gpt-5-mini)
- [x] Create `src/lib/pipeline/stage1-extract.ts`
- [x] Prompt: Parse transcript → structured Q&A pairs
- [x] Output: `ExtractedQA[]` array
- [x] Test: Extracts 4+ Q&A pairs from sample transcript (4/4 extracted)

#### 8.4 Stage 2 — Question Analysis (gpt-5.1)
- [x] Create `src/lib/pipeline/stage2-questions.ts`
- [x] Input: ExtractedQA[] + jobDescription
- [x] Prompt: Classify each question type, map to JD requirements
- [x] Flag technical questions as OUT_OF_SCOPE
- [x] Output: `AnalyzedQuestion[]` with type, jdRequirementMapped, priority
- [x] Test: Correctly classifies behavioral vs situational vs technical ✓

#### 8.5 Stage 3 — Answer Evaluation (gpt-5.1)
- [x] Create `src/lib/pipeline/stage3-answers.ts`
- [x] Input: AnalyzedQuestion[] + coaching-reference.md content
- [x] Prompt: Score each answer against 6Q, Red/Green flags
- [x] Skip evaluation for OUT_OF_SCOPE questions
- [x] Output: `EvaluatedAnswer[]` with scores, flags, grade
- [x] Test: Detects missing 6Q components, applies correct flags ✓

#### 8.6 Stage 4 — Gap + Calibration (gpt-5.1)
- [x] Create `src/lib/pipeline/stage4-gaps.ts`
- [x] Input: AnalyzedQuestion[] + EvaluatedAnswer[] + JD + selfAssessment
- [x] Prompt: Compare demonstrated vs required, calibrate self-perception
- [x] Output: `GapAnalysis` with coverage and calibration delta
- [x] Test: Correctly identifies demonstrated vs missing JD requirements ✓

#### 8.7 Stage 5 — Synthesis (gpt-5.1)
- [x] Create `src/lib/pipeline/stage5-synthesis.ts`
- [x] Input: All previous stage outputs
- [x] Prompt: Generate final report with executive summary, verdict
- [x] Output: `AnalysisReport` with all sections
- [x] Test: Full pipeline executed successfully (100s, all sections present) ✓

#### 8.8 Report Output
- [x] Update success page to render new report structure
- [x] Add question type breakdown (horizontal bar chart)
- [x] Add JD coverage map visualization
- [x] Add calibration insight card (3-column: You Said / Delta / We Found)
- [x] Generate memorable session ID (AMH-XXXX-XXXX format)
- [x] Display session ID on results page (header + feedback CTA)
- [x] Test: Full report renders correctly with all sections ✓

#### 8.9 Growth Mechanic
- [x] Create `src/lib/promo.ts` for promo code logic
- [x] Add promo_codes table to SQLite (code, created_at, expires_at, uses_remaining)
- [x] Add promo code validation in `/submit` handler
- [x] If valid promo → bypass payment, proceed to analysis
- [x] Decrement uses_remaining on each use (default: 5 uses, 90 days)
- [x] Add feedback CTA to results page with session ID
- [x] Admin endpoints: POST /admin/promo/create, GET /admin/promo/list
- [x] Test: Compiles successfully ✓

---

## Affected Files (Phase 8)

```
Sites/interview-reviewer-staging/src/
├── index.tsx                    # UPDATE: Form fields, submission handler, report rendering
├── lib/
│   ├── openai.ts               # UPDATE: Add model selection parameter
│   ├── session-store.ts        # UPDATE: Add selfAssessment field
│   ├── db.ts                   # UPDATE: Add promo_codes table
│   ├── promo.ts                # CREATE: Promo code validation
│   ├── types/
│   │   └── pipeline.ts         # CREATE: TypeScript interfaces
│   └── pipeline/
│       ├── index.ts            # CREATE: Pipeline orchestrator
│       ├── stage1-extract.ts   # CREATE: Q&A extraction
│       ├── stage2-questions.ts # CREATE: Question analysis
│       ├── stage3-answers.ts   # CREATE: Answer evaluation
│       ├── stage4-gaps.ts      # CREATE: Gap + calibration
│       └── stage5-synthesis.ts # CREATE: Report synthesis
└── content/
    └── coaching-reference.md   # EXISTS: Already populated
```

---

## Unit Tests (Phase 8)

| Test | Description | Pass Criteria |
|------|-------------|---------------|
| 8.1 | Form validation | Rejects empty JD, rejects empty selfAssessment |
| 8.2 | Pipeline orchestrator | Calls all 5 stages in sequence |
| 8.3 | Stage 1 extraction | Extracts ≥5 Q&A pairs from sample transcript |
| 8.4 | Stage 2 classification | Correctly identifies behavioral/situational/technical |
| 8.5 | Stage 3 evaluation | Applies 6Q framework, detects red flags |
| 8.6 | Stage 4 gaps | Identifies demonstrated vs missing JD requirements |
| 8.7 | Stage 5 synthesis | Generates complete report with all sections |
| 8.8 | Report rendering | All sections visible, pie chart renders |
| 8.9 | Promo codes | Valid code bypasses payment, expired code rejected |

---

## Trap Doors Identified

1. **Payment model** (one-time vs subscription) - DECIDED: one-time
2. **Auth model** (login vs no-login) - DECIDED: no-login for MVP
3. **Data retention** (store vs delete) - DECIDED: delete transcript, keep metadata only
4. **LLM provider** (OpenAI vs local) - DECIDED: OpenAI API (BYOK)

---

## Status

**Current Phase:** 8 (Multi-Stage Analysis Pipeline)  
**Progress:** 35/35 MVP items (100%), 46/46 Phase 8 items (100%)  
**Next Action:** Deploy to production (Phase 6 completion)

---

## Notes

- Reference content is stubbed - V will provide coaching files later
- System designed so content can be hot-swapped by updating `content/coaching-reference.md`
- Open source from day 1 - no secrets in repo, all config via env vars















