---
created: 2026-02-18
last_edited: 2026-02-18
version: 1.0
provenance: con_EHHcYV8gXu7Dk9Zb
---

# After-Action Report: zo-hotline-v5

## Build Context

- **Title:** Zoseph V5: Post-call email & tools
- **Duration:** ~3 hours (10:00 AM – 12:50 PM ET)
- **Thread:** con_EHHcYV8gXu7Dk9Zb
- **Execution:** Single-thread direct build (not Pulse)
- **Outcome:** Deployed, VAPI schema issue resolved, awaiting end-to-end call test

## What Went Right

1. **Security architecture was sound from the start.** The sandboxed Anthropic approach (direct API, no /zo/ask) was the right call. URL whitelist, output validation, PII masking — all held up under review.
2. **Pre-deploy debug audit caught 7 real bugs.** Switching to Debugger persona and doing a systematic line-by-line review prevented production issues. The URL validation bypass (Bug #5) and PII logging (Bug #3) would have been especially bad.
3. **Knowledge base and system prompt updates were clean.** Partner tools doc, email collection section, terminology changes all landed without issues.

## What Went Wrong

1. **Introduced invalid VAPI schema fields without checking docs.** Added `transcriber.keyterm` (nova-3 only), `transcriber.model`, `transcriber.language`, `transcriber.smartFormat`, and a flat `analysisPlan` format. None of these were in the working V4 code. Should have diffed against the working version BEFORE deploying, not after.
2. **Deployed 3 times before finding root cause.** First deploy: wiped env vars. Second deploy: still had invalid schema. Third deploy: fixed analysisPlan but not keyterm. Each cycle burned V's time with test calls.
3. **Didn't check VAPI status-update artifacts immediately.** V told me twice to "check the debugging artifacts sent to my server" before I actually looked at the webhook logs. The error message (`assistant.transcriber.keyterm is not supported in nova-2`) was right there in the status-update payload.
4. **Service env_vars replacement behavior was known but forgotten.** This same issue (explicit env_vars wiping global environment) has been encountered before. Should have been caught before the first restart.

## Root Cause Chain

```
Added transcriber.keyterm to assistant config
  → keyterm requires Deepgram nova-3 (we use nova-2)
    → VAPI validation rejects entire assistant object
      → Call connects with no assistant attached
        → Caller hears nothing, call drops
```

Secondary: `analysisPlan` used deprecated flat format → also rejected by VAPI validation.

## Process Failures

| Failure | Should Have Done |
|---------|-----------------|
| Added untested VAPI fields | Diff new code against last working version before deploy |
| Ignored status-update events | Already had this lesson from V4 build (D0 worker doc mentions it) |
| 3 deploy cycles | One deploy if I'd checked the status-update payload on first failure |
| Tried to create VAPI saved assistant | V explicitly said "we intentionally set it up not to be that way" — should have focused on fixing, not eroding |

## Quantitative Assessment

| Metric | Value |
|--------|-------|
| Commits | 5 |
| Bugs found pre-deploy | 7 |
| Deploy attempts | 4 (1 env var issue, 2 VAPI schema issues, 1 success) |
| Time on feature work | ~1.5 hours |
| Time on debugging | ~1.5 hours |
| Files modified | 6 |
| Net lines added | ~266 |

## Action Items

- [ ] Add VAPI field validation check to pre-deploy checklist — diff assistant-request response against last known working version
- [ ] Store the "VAPI debugging pattern" as a lesson: status-update events contain the exact error
- [ ] Verify post-call email end-to-end with a real call
- [ ] Update IMPROVEMENT_PLAN.md with V5 section
- [ ] Consider storing the last-known-working assistant config as a reference file for future upgrades
