---
created: 2026-02-18
last_edited: 2026-02-18
version: 1.0
provenance: con_EHHcYV8gXu7Dk9Zb
---

# Build Close: zo-hotline-v5

## Summary

Single-thread build (not Pulse-orchestrated). 5 commits across 4 workstreams, 7 pre-deploy bugs caught and fixed, 1 VAPI schema root cause identified through systematic debugging.

## Decisions (6)

- **Anthropic direct API over /zo/ask for email generation**: Sandboxes the output — no tool access, no file access. Cheaper ($0.001/email vs ~$0.02), faster (no Zo overhead), and the security boundary is cleaner. The email generator can't do anything except generate text.
- **URL whitelist with strict hostname parsing**: Initially used `url.includes(domain)` which could be bypassed with `evil-zocomputer.com`. Fixed to use `new URL()` hostname extraction. Only 4 domains allowed: zocomputer.com, support.zocomputer.com, discord.gg, agentmail.to.
- **In-memory Map + DB persistence for email collection**: Map provides fast lookup during the call lifecycle. DB persistence on collection (not just end-of-call) ensures email survives crashes. Belt and suspenders.
- **Empty env_vars on registered service**: Service inherits all global env vars. Setting explicit env_vars replaces the entire environment, which wiped ANTHROPIC_API_KEY on first deploy attempt.
- **"Builder" not "creator" terminology**: V's preference — "creator" is emotionally loaded, "builder" is more neutral for the Zo context.
- **Status-update webhook subscription**: VAPI sends validation errors as status-update events. Without subscribing, schema errors are completely invisible — the assistant just silently fails to attach.

## Learnings (5)

1. **VAPI schema validation is silent and destructive.** When `assistant-request` returns any invalid field, VAPI drops the entire assistant — no error to the webhook, no error to the caller. The call connects but has no assistant. The ONLY signal is a `status-update` event with the error payload. This has happened after every major version change.
2. **Deepgram feature availability is model-gated.** `keyterm` requires `nova-3` or `flux`. Adding it to `nova-2` config makes the entire transcriber (and therefore the assistant) invalid. Must check Deepgram docs before adding transcriber features.
3. **Pre-deploy debug audits are high-ROI.** 7 bugs found before any caller hit them: PII logging to console, email not persisted to DB, URL validation bypass, CallerProfile interface mismatch, buildCallerContext not surfacing recommendations, SMS ordering bug, and a race condition between async profile upsert and recommendation update.
4. **Service env_vars are full replacements.** The `update_user_service` `env_vars` field replaces (not merges) the inherited environment. Setting even one key wipes all global vars like ANTHROPIC_API_KEY and ZO_CLIENT_IDENTITY_TOKEN.
5. **V's debugging pattern for VAPI issues**: When the hotline breaks after a version change, check the status-update artifacts VAPI sends to the webhook. The error message tells you exactly which field is invalid.

## Concerns (2)

1. **analysisPlan v2 format is untested in production.** Converted from deprecated flat format to nested `summaryPlan`/`structuredDataPlan`/`successEvaluationPlan`. Compiles and VAPI accepts it, but post-call analysis quality hasn't been verified with real calls yet.
2. **Post-call email not yet tested end-to-end.** The Anthropic → AgentMail pipeline compiles and individual components work (AgentMail API tested, Anthropic API verified), but no real call has triggered the full flow yet.

## Position Candidates (2)

1. **"Always subscribe to status-update events in VAPI webhooks."** — Every version change has caused silent assistant failures. The status-update payload is the only way to see VAPI's validation errors. This should be a standing rule for any VAPI webhook.
2. **"Debug audits before deploy are non-negotiable for production voice services."** — Voice services have zero error tolerance from the caller's perspective. A silent failure means a dead call. The 7-bug audit prevented real user impact.

## Content Library Candidates (1)

- `Knowledge/zo-hotline/50-use-case-inspiration/partner-tools-v-uses.md` — Partner tools knowledge doc. Reusable for any context where V needs to explain the tools behind Zo/hotline.

## Artifacts Produced

| File | Type | Lines |
|------|------|-------|
| `Skills/zo-hotline/scripts/hotline-webhook.ts` | Modified | 1532 (+266) |
| `Skills/zo-hotline/prompts/zoseph-system-prompt.md` | Modified | ~360 |
| `Knowledge/zo-hotline/50-use-case-inspiration/partner-tools-v-uses.md` | New | ~80 |
| `Knowledge/zo-hotline/00-knowledge-index.md` | Modified | +7 entries |
| `Skills/zo-hotline/scripts/package.json` | Modified | +@anthropic-ai/sdk |
