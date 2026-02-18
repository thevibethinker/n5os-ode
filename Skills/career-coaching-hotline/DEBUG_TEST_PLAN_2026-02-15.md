---
created: 2026-02-15
last_edited: 2026-02-15
version: 1.0
provenance: con_fTIsb06uuRCMKsSM
---

# Career Hotline Resume Ingest Debug + Test Plan

## Objective
Stabilize and verify the resume intake pipeline for real Fillout-origin traffic:
1. Fillout submission
2. `intake-webhook.ts` parsing
3. `caller_lookup` insert
4. `resume_ingest.py` trigger
5. `caller_resumes` write with parsed decomposition when available

## Tradeoff Decision
1. Fix intake schema compatibility first.
- Why: If real Fillout payloads are dropped, no downstream memory/profile logic receives data.
- Cost: short-term focus on transport/parsing before richer coaching/profile features.

2. Build cross-call profile memory second.
- Why: Depends on reliable intake + resume persistence first.
- Cost: caller intelligence remains fragmented until stage 1 is stable.

## Root Cause Investigated
Real Fillout webhook payloads arrived in nested schema:
- `payload.submission.questions`
- `payload.submission.submissionTime`

Webhook previously expected:
- `payload.questions`
- `payload.submissionTime`

Result before fix: real Fillout-origin submissions logged as received but skipped as "no questions found".

## Implemented Fixes
1. `file 'Skills/career-coaching-hotline/scripts/intake-webhook.ts'`
- Added schema fallback order:
  - `payload.questions`
  - `payload.submission?.questions`
  - `payload.responses?.[0]?.questions`
- Added submitted time fallback:
  - `payload.submissionTime`
  - `payload.submission?.submissionTime`
  - now

2. `file 'Skills/career-coaching-hotline/scripts/intake-webhook.ts'`
- Replaced fragile resume ingest stdout parsing (`last line JSON`) with robust JSON extraction helper that handles:
  - full JSON output
  - prefixed log lines + trailing JSON object
  - brace-bounded fallback parsing

## Test Plan
### A. Automated (local simulation)
1. Run `bun run test-hotline.ts --only Intake`
2. Expect:
- Intake health check pass
- Simulated payload accepted
- DB lookup entry appears
- Cleanup removes test scaffolding rows

### B. Real Fillout-origin verification
1. Submit live public form: `https://forms.fillout.com/t/v39TcXUcw1us`
2. Include:
- Name/email/phone
- LinkedIn
- Resume upload
- Required matrix + consent fields
3. Verify evidence:
- Webhook log includes nested schema event + processing line
- `caller_lookup` row inserted for test phone
- `caller_resumes` row inserted for test phone

### C. Regression checks
1. Ensure existing top-level simulated schema still works
2. Verify no crashes in intake service after schema handling change
3. Verify resume processing callback no longer emits parse-failure for valid JSON outputs

## Execution Log (This Pass)
1. Patched schema parsing + JSON parsing fallback in intake webhook
2. Restarted intake webhook service
3. Ran automated intake tests (pass)
4. Submitted live Fillout form (real upstream event)
5. Confirmed webhook processed nested payload and inserted rows into both tables for the live test phone

## Remaining Work
1. Idempotency hardening for duplicate Fillout deliveries
- Current behavior can insert duplicate `caller_lookup` and `caller_resumes` rows for repeated submission events

2. Cross-call semantic profile consolidation
- Add a canonical caller profile layer that merges intake + resume + call history across sessions

3. Decomposition reliability metrics
- Distinguish "resume stored" vs "resume fully decomposed" with explicit status fields

## Success Criteria
1. Real Fillout submissions consistently produce:
- one durable intake record
- one resume record
- decomposition status explicitly tracked
2. Duplicate webhook events do not create duplicate user-facing records
3. Debug logs clearly show where failure occurred if any stage fails
