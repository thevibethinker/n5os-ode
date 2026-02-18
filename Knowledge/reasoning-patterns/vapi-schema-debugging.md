---
created: 2026-02-18
last_edited: 2026-02-18
version: 1.0
provenance: con_EHHcYV8gXu7Dk9Zb
---

# VAPI Schema Debugging Pattern

## When This Applies

After ANY change to the VAPI assistant-request response (webhook code changes, system prompt changes, tool additions, transcriber config changes).

## The Problem

VAPI validates the assistant object returned by the webhook. If ANY field is invalid, VAPI silently drops the entire assistant. The call connects but the caller hears nothing. There is no error in the webhook response — VAPI returns 200 and accepts the webhook payload, then rejects it internally.

## The Pattern

### Prevention (Before Deploy)

1. **Diff against last working version.** Extract the assistant-request handler from the current working code and the new code. Compare field by field.
2. **Flag any new fields.** For each new field added to the assistant config, verify it exists in the VAPI API reference AND is compatible with the specific provider/model version being used.
3. **Deepgram features are model-gated.** `keyterm` requires `nova-3` or `flux`. `smartFormat`, `language`, `model` may have different defaults per provider version. Check Deepgram docs, not just VAPI docs.

### Detection (After Deploy)

1. **Subscribe to `status-update` events** in `serverMessages`: `["end-of-call-report", "tool-calls", "status-update"]`
2. **Log the full status-update payload.** The error message is specific: `"assistant.transcriber.keyterm is not supported in nova-2"`.
3. **Check the webhook log immediately after a test call fails.** Don't guess at the problem — the status-update tells you exactly which field is invalid.

### Fix

1. Remove or correct the invalid field.
2. Restart the service.
3. Test again.
4. Confirm the status-update log shows no errors.

## History

- **V4 build (2026-02-18):** `analysisPlan` used deprecated flat format. VAPI rejected silently.
- **V5 build (2026-02-18):** `transcriber.keyterm` added for nova-2 (requires nova-3). VAPI rejected silently. Found by reading status-update payload after V pointed to it twice.
- **Pattern recognized:** This happens after every major version change because new fields get added without checking the VAPI schema constraints.
