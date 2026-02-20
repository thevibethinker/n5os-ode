---
created: 2026-02-19
drop_id: D2
stream: S2
title: Co-Build Diagnostic Flow
status: pending
depends_on: []
provenance: con_tdpDMlVT0VZmXDPS
---

# D2: Co-Build Diagnostic Flow

## Objective

Add a co-build mode to Zoseph where the assistant asks targeted diagnostic questions to gather enough context for generating high-quality, implementation-ready Zo prompts. This mode is offered as an option, not forced.

## Deliverables

1. **System prompt additions** — New section in `prompts/zoseph-system-prompt.md`:
   - Co-build mode trigger: Zoseph offers "Want me to help you build something specific? I can ask a few questions and send you a ready-to-paste prompt."
   - Diagnostic question tree covering:
     - What they want to automate/build (use case)
     - What tools/services they already use (integrations context)
     - How often this should happen (scheduling context)
     - Who it's for (audience/persona context)
     - What the output should look like (deliverable context)
   - Smooth exit: "I've got what I need. Check your texts in 2-3 minutes — I'll send you everything you need to get started."
   - Keep diagnostic to 3-5 questions MAX to avoid dragging out the call

2. **New tool: `startCoBuild`** — VAPI tool handler in `hotline-webhook.ts`:
   - Zoseph calls this to signal co-build mode is active for the call
   - Stores diagnostic answers as structured data on the call
   - Returns confirmation to Zoseph

3. **New tool: `submitDiagnostic`** — VAPI tool handler:
   - Called when Zoseph has gathered enough info
   - Accepts structured diagnostic data: `{ useCase, integrations, frequency, audience, outputFormat, additionalContext }`
   - Stores in memory (Map keyed by callId) for pickup by prompt generator at end-of-call

## Constraints

- Co-build questions should feel conversational, not like a form
- 3-5 questions max, then wrap up
- Zoseph should NOT try to generate the prompt live on the call — that burns VAPI minutes
- Diagnostic data must survive until end-of-call-report fires

## Deposit

`deposits/D2-co-build-diagnostic.json` with:
- `system_prompt_additions`: word count of new prompt content
- `tools_added`: list of new tool names
- `diagnostic_fields`: list of fields collected
- `files_modified`: list of changed files
