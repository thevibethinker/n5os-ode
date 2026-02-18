---
created: 2026-02-18
last_edited: 2026-02-18
version: 1.0
type: build_plan
status: draft
provenance: con_WqixWLkGYg48Os4p
---

# Plan: Zo Hotline V6 — Post-Call Experience + Voice Polish

**Objective:** Fix production bugs (analysisPlan, tool logging, interruptions), redesign follow-up flow from email→SMS+zo.space page, and polish conversation design based on Amanda's call feedback.

**Trigger:** Amanda's call (019c730d) exposed: 6 interruptions, no email collection, no follow-up sent, broken analysisPlan in post-v5 builds, and Explorer pathway rushing non-pain-point callers. Plus 7 more improvements from triage.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

- [x] What is VAPI's correct analysisPlan schema for v2? → Must check VAPI docs during D1.1. If nested format doesn't work, revert to flat.
- [x] Can zo.space API routes be called from the webhook directly? → Yes, `update_space_route` creates routes programmatically, but the webhook should use HTTP fetch to a Zo API endpoint that generates the page. Simpler: webhook calls `/zo/ask` which creates the zo.space page.
- [x] SMS sending from webhook — use Zo SMS tool or direct Twilio? → Use `/zo/ask` with instruction to send SMS. Keeps it simple, no new dependencies.

---

## Checklist

### Phase 1: Bug Fixes + Voice Tuning (Wave 1)
- ☐ Fix analysisPlan v2 schema (revert to working format or fix nested format)
- ☐ Fix tool_usage logging (trackToolUsage/persistToolUsage broken)
- ☐ Tune interruption parameters (stopSpeakingPlan, startSpeakingPlan)
- ☐ Add graceful silence handler (pre-wrap before timeout)
- ☐ Harden Zo/Zoho transcription (Deepgram keyword boosting)
- ☐ Test: All 5 fixes verified via webhook restart + inspection

### Phase 2: SMS Follow-Up System (Wave 2)
- ☐ Create zo.space page template route (`/hotline/:slug`)
- ☐ Build page generation logic in webhook (LLM generates content, creates page)
- ☐ Replace collectEmail tool with sendFollowUp tool
- ☐ Update system prompt: remove email collection, add SMS follow-up offer
- ☐ Add graceful wrap ("want me to text you these steps?")
- ☐ Test: End-to-end — call → page generated → SMS sent with link

### Phase 3: Conversation Design Polish (Wave 1, parallel)
- ☐ Explorer pathway: add capability-showcase sub-branch for non-pain-point callers
- ☐ System prompt: strengthen "listen longer" guidance
- ☐ Update IMPROVEMENT_PLAN.md with v6 section
- ☐ Test: Scenario walkthrough of Explorer sub-branch

---

## Phase 1: Bug Fixes + Voice Tuning

### Affected Files
- `Skills/zo-hotline/scripts/hotline-webhook.ts` — UPDATE — Fix analysisPlan, tool logging, interruption params, silence handler, transcription keywords
- `Skills/zo-hotline/IMPROVEMENT_PLAN.md` — UPDATE — V6 section

### Changes

**1.1 Fix analysisPlan (Item #3):**
The nested `summaryPlan`/`structuredDataPlan`/`successEvaluationPlan` format introduced in v5 is producing zero analysis on post-v5 calls. Two approaches:
- **Option A (safe):** Revert to flat analysisPlan format that worked in v4 (summary + structuredData + successEvaluation as top-level keys)
- **Option B (correct):** Check VAPI docs for the exact nested schema and fix field names

Worker must check VAPI's current API docs to determine correct format. If docs are ambiguous, use Option A (revert). The status-update webhook logs may contain the validation error.

**1.2 Fix tool_usage logging (Item #9):**
`trackToolUsage()` and `persistToolUsage()` functions exist in webhook but `tool_usage.jsonl` is never created and there's no DuckDB table. Debug the persistence path — likely a missing `initDb()` DDL or file path issue.

**1.3 Tune interruption parameters (Item #2):**
Current values cause 6 interruptions on Amanda's call:
```
stopSpeakingPlan: { numWords: 1, voiceSeconds: 0.3, backoffSeconds: 1.0 }
startSpeakingPlan.transcriptionEndpointingPlan: { onPunctuationSeconds: 0.3, onNoPunctuationSeconds: 1.0, onNumberSeconds: 0.4 }
```
New values (less aggressive):
```
stopSpeakingPlan: { numWords: 2, voiceSeconds: 0.5, backoffSeconds: 1.5 }
startSpeakingPlan.transcriptionEndpointingPlan: { onPunctuationSeconds: 0.5, onNoPunctuationSeconds: 1.5, onNumberSeconds: 0.6 }
startSpeakingPlan.waitSeconds: 0.8 (up from 0.6)
```

**1.4 Graceful silence handler (Item #5):**
Amanda's call ended with `silence-timed-out` after Zoseph delivered prompt instructions. Add to system prompt:
- After delivering a long or complex response (prompt instructions, multi-step guidance), always follow up with: "Take your time with that. Want me to text you these steps so you have them?"
- This bridges into the SMS follow-up naturally.

**1.5 Transcription hardening (Item #6):**
Amanda's call had "ZOOM computer" for "Zo Computer." Add/strengthen Deepgram keywords config. Check if `nova-3` is now available (it supports `keyterm` better). Add common misheard terms: Zo→Zo (boost), Zoho→Zo (boost), Zoom→Zo (boost), Zelle→Zo (boost).

### Unit Tests
- Restart webhook, make test call, verify analysis data populates (summary + structuredData non-null)
- Check tool_usage.jsonl exists after a tool-calls webhook event
- Verify status-update logs show no validation errors
- Manual test call verifying fewer interruptions (subjective but observable)

---

## Phase 2: SMS Follow-Up System

### Affected Files
- `Skills/zo-hotline/scripts/hotline-webhook.ts` — UPDATE — New `sendFollowUp` tool, SMS dispatch, page generation trigger
- `Skills/zo-hotline/prompts/zoseph-system-prompt.md` — UPDATE — Replace email collection with SMS follow-up, add graceful wrap
- zo.space route: `/hotline/[slug]` — CREATE — Dynamic page for caller follow-ups

### Changes

**2.1 zo.space Follow-Up Page (Item #1 + #8):**
Create a zo.space API route at `/api/hotline/create-page` that:
- Accepts POST with: callId, summary, pathway, level, primaryInterest, callerName, prompt(s), nextSteps
- Generates a unique slug (e.g., `amanda-climate-policy-feb18`)
- Creates a PUBLIC zo.space page route at `/hotline/<slug>` containing:
  - Header: "Your Vibe Thinker Hotline Follow-Up"
  - Section 1: "What We Talked About" — conversation summary
  - Section 2: "Try This on Zo" — ready-to-paste prompt(s) with copy button
  - Section 3: "Your First 15 Minutes" — step-by-step guide tailored to their use case
  - Section 4: "Keep Going" — links to Discord, support docs, relevant community examples
  - Footer: "Built on Zo Computer — this page was generated in real-time after your call"
- Returns the public URL

Design: Clean, minimal, mobile-first. The page IS the demo — a caller who just learned about Zo gets to see Zo's output immediately.

**Alternative considered:** Static HTML file hosted as asset vs. dynamic zo.space page.
- Static HTML: simpler, no route management, but can't be updated or tracked
- Dynamic zo.space page: showcases the product, can be updated, each page is a route
- **Decision: zo.space page** — the meta-demonstration value is too high to pass up

**2.2 Replace collectEmail with sendFollowUp tool (Item #4):**
Remove `collectEmail` tool definition from VAPI assistant config. Add new `sendFollowUp` tool:
```
name: sendFollowUp
description: "Send the caller a text message with a link to their personalized follow-up page. Call this when the caller agrees to receive a text follow-up, or at the end of a substantive conversation (2+ min) when offered."
parameters: { confirmed: boolean (caller said yes to follow-up) }
```

When `sendFollowUp` is called:
1. Generate page content using Anthropic API (same pattern as email generation)
2. Call `/zo/ask` to create the zo.space page
3. Call `/zo/ask` to send SMS to the caller's phone number with the page link
4. Log to DuckDB: `followup_sent = TRUE, followup_url = <url>, followup_sent_at = <timestamp>`

**2.3 Update system prompt for SMS flow (Items #4 + #5):**
Replace the "Email Collection" section with:
```
## Follow-Up

After a substantive conversation (2+ min), before winding down, offer once:
"Before you go — want me to text you a follow-up? It'll have everything we talked about, 
plus a ready-to-paste prompt you can try on Zo. I can send it to this number."

If yes: call sendFollowUp with confirmed=true.
If no: move on. One ask only.

After delivering a long response (prompt instructions, multi-step plan):
"Take your time. Want me to text you all of this so you have it?"
```

### Unit Tests
- Create test page via API endpoint, verify page renders at `/hotline/<slug>`
- Verify `sendFollowUp` tool processes correctly in tool-calls webhook
- Verify SMS send path works (mock or real test number)
- Verify DuckDB columns exist: `followup_sent`, `followup_url`, `followup_sent_at`

---

## Phase 3: Conversation Design Polish

### Affected Files
- `Skills/zo-hotline/prompts/zoseph-system-prompt.md` — UPDATE — Explorer sub-branch
- `Knowledge/zo-hotline/97-conversational-playbook/explorer-pathway.md` — UPDATE — Capability showcase variant
- `Skills/zo-hotline/IMPROVEMENT_PLAN.md` — UPDATE — V6 section

### Changes

**3.1 Explorer pathway: capability showcase sub-branch (Item #7):**
Amanda said "I'm looking for something more complicated" — she wasn't struggling, she was exploring. Current Explorer path assumes pain-point → pivot. Add:

After "What does your average workday look like?", if caller responds with something like:
- "I'm not looking to fix something specific"
- "I'm curious what it can really do"
- "I'm looking for something more advanced"
- "I already have my workflow handled"

→ Pivot to **Capability Showcase**:
"Got it — you've got your basics covered. Let me show you the stuff that surprises people. What kind of work do you do?"

Then use profession pivot but lead with the ADVANCED capabilities:
- Scheduled agents that run while you sleep
- Multi-step workflows (email → extract → spreadsheet → alert)
- Custom websites and APIs in minutes
- Integration with 500+ tools
- Full Linux server with SSH access

This is the "power user explorer" — they don't need convincing AI is useful, they need to see the ceiling.

**3.2 Listen longer guidance:**
Add to Voice Rules: "When a caller is mid-thought (listing tools, describing their work, explaining what they've tried), DO NOT interject with 'Makes sense' or pivot. Wait for a full natural pause (2+ seconds of silence after a complete thought)."

### Unit Tests
- Scenario test: "I'm just checking out what Zo can do, I already use AI tools" → verify Zoseph pivots to capability showcase, not pain-point mining
- Verify system prompt voice rules include "listen longer" guidance

---

## MECE Validation

### Drop Decomposition

The 9 items decompose into **4 Drops across 2 Waves:**

| Drop | Name | Wave | Items Covered | Rationale |
|------|------|------|---------------|-----------|
| D1.1 | Webhook Bug Fixes + Voice Tuning | W1 | #2, #3, #5, #6, #9 | All webhook.ts modifications that don't depend on the new follow-up system. Groups config fixes (interruptions, transcription, silence) with code fixes (analysisPlan, tool logging). Single file owner. |
| D1.2 | Conversation Design Polish | W1 | #7 | System prompt + knowledge base changes only. No webhook code. Parallel with D1.1. |
| D2.1 | Zo.space Follow-Up Page | W2 | #8 (partial #1) | Creates the zo.space page template and API route. Needs clean webhook from D1.1 to integrate. |
| D2.2 | SMS Follow-Up Integration | W2 | #1, #4 | Wires sendFollowUp tool into webhook, updates system prompt for SMS flow, connects to zo.space page from D2.1. Capstone drop. |

### Scope Coverage Matrix

| Scope Item | Drop | Status |
|------------|------|--------|
| `Skills/zo-hotline/scripts/hotline-webhook.ts` (bug fixes) | D1.1 | ✓ |
| `Skills/zo-hotline/scripts/hotline-webhook.ts` (sendFollowUp tool + integration) | D2.2 | ✓ |
| `Skills/zo-hotline/prompts/zoseph-system-prompt.md` (voice rules, silence handler) | D1.2 | ✓ |
| `Skills/zo-hotline/prompts/zoseph-system-prompt.md` (SMS follow-up section) | D2.2 | ✓ |
| `Knowledge/zo-hotline/97-conversational-playbook/explorer-pathway.md` | D1.2 | ✓ |
| zo.space `/api/hotline/create-page` route | D2.1 | ✓ |
| zo.space `/hotline/[slug]` page route | D2.1 | ✓ |
| `Skills/zo-hotline/IMPROVEMENT_PLAN.md` | D2.2 | ✓ |
| DuckDB schema changes (followup columns) | D2.2 | ✓ |

### MECE Check

**Overlaps:** `hotline-webhook.ts` is touched by both D1.1 (bug fixes) and D2.2 (new tool). This is safe because:
- D1.1 modifies existing code (analysisPlan, tool logging, config params)
- D2.2 adds new code (sendFollowUp handler, new DDL, new end-of-call logic)
- Wave barrier ensures D2.2 starts from D1.1's clean output

**Similarly:** `zoseph-system-prompt.md` is touched by D1.2 (Explorer pathway, voice rules, silence handler) and D2.2 (SMS follow-up section replacement). Wave barrier makes this safe.

**Gaps:** None. All 9 items are covered.

### MECE Validation Result

- [x] All scope items assigned to exactly ONE drop (no overlaps within waves)
- [x] All plan deliverables covered (no gaps)
- [x] All drops within 40% token budget (webhook.ts is ~1500 lines but each drop touches different sections)
- [x] Wave dependencies are valid (W2 depends on W1, no circular)

---

## Worker Briefs

| Wave | Drop | Title | Brief File |
|------|------|-------|------------|
| 1 | D1.1 | Webhook Bug Fixes + Voice Tuning | `drops/D1.1-webhook-fixes.md` |
| 1 | D1.2 | Conversation Design Polish | `drops/D1.2-conversation-design.md` |
| 2 | D2.1 | Zo.space Follow-Up Page | `drops/D2.1-zospace-page.md` |
| 2 | D2.2 | SMS Follow-Up Integration (Capstone) | `drops/D2.2-sms-followup.md` |

---

## Success Criteria

1. **analysisPlan working:** Next 3 substantive calls have non-null summary + structuredData
2. **Interruptions reduced:** stopSpeakingPlan.numWords >= 2, voiceSeconds >= 0.5
3. **Tool logging working:** tool_usage.jsonl populated after tool-calls events
4. **SMS follow-up delivered:** Test call → zo.space page created → SMS sent with link
5. **zo.space page renders:** `/hotline/<slug>` shows personalized content, mobile-responsive
6. **Explorer sub-branch works:** "I'm not here to fix something" → capability showcase pivot
7. **Silence timeout graceful:** Zoseph offers text follow-up before silence kills the call

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| VAPI analysisPlan schema uncertain | Worker checks VAPI docs first; falls back to v4 flat format if nested doesn't work |
| zo.space page creation from webhook adds latency to end-of-call | Page generation is async (happens after call ends, not during) |
| SMS sending requires phone number extraction from VAPI payload | Phone already extracted in end-of-call-report handler; same path used for caller profiles |
| Deepgram nova-3 may not be available on VAPI | Check first; fall back to keyword boosting on nova-2 |
| System prompt getting too long (already 2231 words) | D1.2 replaces email section with shorter SMS section; net neutral |

---

## Trap Doors

🚪 **zo.space page URLs are permanent.** Once a page is created at `/hotline/<slug>`, that URL is live. If we change the schema later, old pages still need to work. **Mitigation:** Use versioned page templates. The page route reads content from stored data, not hardcoded layout.

🚪 **Removing collectEmail tool breaks any existing VAPI assistant config that references it.** The tool removal in D2.2 means any in-flight call that tries to collect email will get an error. **Mitigation:** Keep collectEmail as a deprecated alias that internally triggers sendFollowUp instead.

---

## Nemawashi (Alternatives Considered)

### Follow-up delivery: Email vs SMS vs Page
1. **Email only (current v5 approach):** Spelling over phone is terrible UX. Amanda never got asked. Low conversion.
2. **SMS only:** We have the number. Simple. But SMS is text-limited — can't fit prompt instructions, steps, links nicely.
3. **SMS + zo.space page (chosen):** Best of both. SMS is the delivery vehicle (instant, no spelling). Page is the content vehicle (rich, shareable, demo of product). The page itself is a Zo showcase.

### Page technology: Static HTML asset vs zo.space route
1. **Static HTML uploaded as asset:** Simpler. But can't be dynamic, can't use React, can't showcase Zo capabilities.
2. **zo.space page route (chosen):** Each follow-up is a real zo.space page. This IS the product demo. Callers see what Zo built for them.

### SMS sending: Direct Twilio vs /zo/ask
1. **Direct Twilio API:** Lower latency, more control. But adds a dependency and credential management.
2. **/zo/ask with SMS instruction (chosen):** Uses existing Zo SMS capability. No new dependencies. Simple.

---

## Learning Landscape

### Build Friction Recommendation
**Recommended:** minimal
**Rationale:** V is familiar with hotline architecture from v4/v5 builds. All concepts are known. The novel piece (zo.space page generation) is a creative application of known primitives, not a new concept.

### Technical Concepts in This Build

| Concept | V's Current Level | Domain | Pedagogical Value |
|---------|-------------------|--------|-------------------|
| VAPI webhook schemas | Intermediate | Voice AI | Low (known from v4/v5) |
| zo.space route creation | Intermediate | Zo platform | Low (used before) |
| Deepgram transcription config | Beginner | Speech-to-text | Medium |
| Voice UX turn-taking | Beginner | Voice AI | ★ High |

### Decision Points

| ID | Question | Options | Value | Related Drop |
|----|----------|---------|-------|--------------|
| DP-1 | analysisPlan: fix nested or revert to flat? | 2 | Low | D1.1 |
| DP-2 | Page design: minimal or rich? | 2 | Medium | D2.1 |

### Drop Engagement Tags

| Drop | Tag | Rationale |
|------|-----|-----------|
| D1.1 | mechanical | Bug fixes, config changes. Known patterns. |
| D1.2 | mechanical | Prompt editing. V's domain expertise. |
| D2.1 | pedagogical | zo.space page design is creative. Worth seeing. |
| D2.2 | mechanical | Integration wiring. Known patterns from v5 email flow. |
