---
created: 2026-02-19
drop_id: D5
stream: S1+S2
title: Integration & Wiring
status: pending
depends_on: [D1, D2, D3]
provenance: con_tdpDMlVT0VZmXDPS
---

# D5: Integration & Wiring

## Objective

Wire together all v7 components: co-build diagnostic data flows into the Sonnet prompt generator which uses the meta-prompter context, the enhanced page template renders the results, and the end-of-call handler orchestrates it all with a smooth Zoseph handoff.

## Deliverables

1. **Updated end-of-call-report handler** in `hotline-webhook.ts`:
   - Detect co-build diagnostic data from D2's `submitDiagnostic` tool
   - Pass diagnostic data to upgraded `generateFollowUpContent` from D3
   - Route to Sonnet or Haiku based on co-build flag
   - Pass enhanced page data to redesigned `generateFollowUpPageSource` from D4

2. **Updated assistant-request handler**:
   - Add `startCoBuild` and `submitDiagnostic` to the tools list returned to VAPI
   - Tool definitions with proper parameter schemas for VAPI

3. **Updated tool-calls handler**:
   - Route `startCoBuild` and `submitDiagnostic` tool calls to their handlers from D2

4. **Zoseph handoff flow**:
   - System prompt: When co-build is complete OR call is ending naturally with good signal, Zoseph says: "I've got everything I need. Check your texts in 2-3 minutes — I'll send you a page with everything we talked about plus prompts you can paste right into Zo."
   - Call `sendFollowUp({ confirmed: true })` to signal follow-up should be sent

5. **VAPI assistant config updates**:
   - Add new tools to the tools array
   - Ensure analysisPlan structured data captures co-build flag

6. **End-to-end verification**:
   - Test with mock end-of-call-report payload containing co-build diagnostic data
   - Test with mock standard call (no co-build)
   - Verify page generation, SMS send, DB logging

## Constraints

- Must not break existing standard call flow
- Co-build is additive — all existing functionality preserved
- Service restart required after integration

## Deposit

`deposits/D5-integration-wiring.json` with:
- `tools_registered`: list of VAPI tools in assistant config
- `flow_paths_tested`: list of tested code paths
- `files_modified`: list of changed files
- `breaking_changes`: any backwards-incompatible changes (should be none)
