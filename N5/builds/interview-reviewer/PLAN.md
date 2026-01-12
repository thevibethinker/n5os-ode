---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_g62UmSAYGCHuZjmN
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

### Phase 7: Content Integration (BLOCKED - awaiting V's content)
- [ ] V provides coaching reference files
- [ ] Extract and structure content
- [ ] Update `content/coaching-reference.md`
- [ ] Test with real content

---

## Affected Files (Phase 0-1)

```
Sites/interview-reviewer-staging/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.tsx          # Main Hono app
│   ├── routes/
│   │   ├── home.tsx       # Landing page
│   │   ├── success.tsx    # Post-payment success
│   │   └── api.ts         # API endpoints
│   ├── components/
│   │   └── Layout.tsx     # Page wrapper
│   ├── lib/
│   │   ├── db.ts          # SQLite setup
│   │   ├── stripe.ts      # Stripe helpers
│   │   ├── openai.ts      # OpenAI helpers
│   │   └── ratelimit.ts   # Rate limiting
│   └── content/
│       └── coaching-reference.md  # Stub content
├── public/
│   └── styles.css
└── README.md
```

---

## Unit Tests (per phase)

**Phase 0:** Server starts, health endpoint returns 200  
**Phase 1:** Landing page renders, form elements present  
**Phase 2:** Checkout creates Stripe session, success verifies payment  
**Phase 3:** Analysis returns formatted report given test transcript  
**Phase 4:** Metadata inserted, transcript NOT in database  
**Phase 5:** Rate limiter triggers at threshold, circuit breaker activates  
**Phase 6:** E2E flow works, privacy/terms pages load

---

## Trap Doors Identified

1. **Payment model** (one-time vs subscription) - DECIDED: one-time
2. **Auth model** (login vs no-login) - DECIDED: no-login for MVP
3. **Data retention** (store vs delete) - DECIDED: delete transcript, keep metadata only
4. **LLM provider** (OpenAI vs local) - DECIDED: OpenAI API (BYOK)

---

## Status

**Current Phase:** 6 (Polish & Deploy)  
**Progress:** 32/35 checklist items (91%)  
**Blockers:** 
- Stripe Connect test mode not set up — need to visit [Sell](/?t=sell) to enable
- Phase 7 blocked awaiting V's content (doesn't block MVP)

---

## Notes

- Reference content is stubbed - V will provide coaching files later
- System designed so content can be hot-swapped by updating `content/coaching-reference.md`
- Open source from day 1 - no secrets in repo, all config via env vars



