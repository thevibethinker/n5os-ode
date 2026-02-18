---
created: 2026-02-11
last_edited: 2026-02-11
version: 0.2
provenance: con_aCg9CcKIYIhqhZno
status: theoretical-first-pass
---

# Zo-to-Zo Teaching Protocol

## What This Is

A protocol for va.zo.computer to teach capabilities to zoputer.zo.computer through conversational guidance rather than file copying. The student (zoputer) absorbs intent and implements locally — "fuzzy installation" rather than exact replication.

Zoputer then serves as the interface layer to client Zo instances, keeping one Zo's worth of distance between external machines and va.

## Architecture

```
VA (mentor, archetype)
  ↓ teaches (one-way sealed lessons)
ZOPUTER (lieutenant, student)
  ↓ installs on (scoped, sanitized)
CLIENT ZO (franchise)
```

### Communication Rules

| Direction | Access | Purpose |
|-----------|--------|---------|
| va → zoputer | Read/Write | Teaching, guidance, testing |
| zoputer → va | Read-only | Reports, questions, lesson logging |
| zoputer → client | Write (scoped) | Sanitized installation packages |
| client → zoputer | Structured messages only | Schema-validated, sanitized |
| client → va | **Blocked** | No direct access, ever |

### Known Environment Differences

| Property | va | zoputer |
|----------|-----|---------|
| Model | Opus 4.6 | Kimi K2.5 |
| Workspace | Fully built (N5, Skills, Knowledge, etc.) | Scaffolding only |
| API Key Env | `ZOPUTER_API_KEY` | `VA_API_KEY` |
| API Endpoint | Both use `https://api.zo.computer/zo/ask` | Same |

**Model difference is significant.** Teaching prompts must be calibrated for Kimi K2.5's capabilities: potentially different tool-calling patterns, reasoning depth, context window, and response formatting. Always ask zoputer to self-identify at session start.

---

## Teaching Modalities

The spectrum of teaching approaches ranges from deterministic (recipe-like) installs to fuzzy (conceptual) installs. Deterministic installs are clear-cut scripts that transfer exact file contents, while fuzzy installs convey concepts and behavior descriptions. Deterministic installs should be handled via script-based file transfer to preserve the integrity of the content.

Deterministic installs rely on script-based transfers; fuzzy installs rely on analogies and behavioral guidance.

---

## Teaching Session Structure

### Pre-Session

1. **Identify capability to teach** — pick one well-defined capability from va
2. **Understand the intent** — what does this capability actually *do* and *why*
3. **Assess zoputer's current state** — what does it already have that's relevant
4. **Model check** — ask zoputer what model it's running (may change over time)
5. **Design behavioral tests** — based on va's understanding of the capability, not zoputer's implementation

### Session Flow

```
[va] Explain the CONCEPT (what and why, not how)
  ↓
[zoputer] Echoes back understanding
  ↓
[va] Corrects/confirms understanding
  ↓
[va] Provides GUIDANCE (approach, constraints, principles)
  ↓
[zoputer] Proposes implementation plan
  ↓
[va] Reviews plan, adjusts
  ↓
[zoputer] Implements (using /zo/ask internally if needed)
  ↓
[va] Runs behavioral tests
  ↓
[va + zoputer] Independent debugging if tests fail
  ↓
[va] Compare notes, reconcile
  ↓
Repeat until tests pass
```

### Key Principles

- **Teach intent, not implementation.** Send the "why" and "what," let zoputer figure out "how."
- **Sealed lessons.** Each teaching session is self-contained. Don't assume zoputer remembers previous sessions unless verified.
- **Echo-back verification.** Always ask zoputer to restate its understanding before it builds. Catch drift early.
- **Behavioral tests, not structural tests.** Don't check if a file exists at a specific path. Check if the *behavior* works correctly.
- **Model-agnostic prompts.** Don't rely on reasoning patterns unique to Opus. Be explicit, step-by-step, smaller task chunks.

### What Gets Sent (and What Doesn't)

**Send:**
- Conceptual explanation of what the capability does
- The principles and constraints it operates under
- Example inputs and expected outputs
- Behavioral test cases
- Guidance on error handling and edge cases

For deterministic installs we also send the exact file contents via the File Transfer Protocol helper script; for fuzzy installs we stick to concepts and behavior patterns.

**Don't Send:**
- Exact file contents from va's workspace
- Paths, configs, or internal structure details
- References to va-specific systems (N5 internals, personal files)
- Anything that would let zoputer reconstruct va's architecture

---

## File Transfer Protocol

### Complex Markdown Loss

When complex markdown is routed through prompts, it can lose bytes. This is due to the limitations of the LLM's formatting capabilities.

### New Script-Based Approach

For deterministic installs, zoputer should run a Python script to write the file or decode base64 content. This avoids the formatting loss that can occur when sending exact file contents through prompts.

### Helper Script Mechanics

Zoputer runs a Python helper that receives file metadata, base64 payload, and writes the file, ensuring byte-perfect copies. Calling this helper looks like this in practice:

1. **va sends the file metadata and base64 payload** — as part of the teaching lesson, va sends the file name, path, and base64-encoded file content.
2. **zoputer receives the metadata and payload** — zoputer's script receives the file name, path, and base64 payload.
3. **zoputer decodes the base64 payload** — the script decodes the base64 payload into binary data.
4. **zoputer writes the file** — the script writes the decoded binary data to the specified path on zoputer's filesystem.

This ensures that the file is transferred byte-perfectly, without any formatting loss.

### Base64 Explanation

Base64 is a binary-to-text encoding scheme that represents binary data in an ASCII string format. It is commonly used to encode binary data, such as images or files, into a format that can be easily transmitted over text-based protocols. For the helper script, base64 is used to encode the file contents, which are then decoded on zoputer's end.

---

## Debugging Protocol

### Independent Review (Paired Debugging)

When a test fails:

1. **va sends the symptom** — what was expected, what happened. NOT va's diagnosis.
2. **zoputer investigates independently** — forms its own hypothesis, gathers evidence.
3. **va investigates independently** — forms its own hypothesis.
4. **Exchange notes** — compare findings.
5. **If aligned** — high confidence, proceed with fix.
6. **If divergent** — this is information. Explore both hypotheses. If unresolvable, trigger HITL.

### Why Independent Review Matters

If va always provides the diagnosis, va's assumptions propagate unchecked. Independent analysis catches blind spots. Disagreement between two Zos is signal, not noise.

---

## Testing Protocol

### Test Design Philosophy

Tests are designed by va (the teacher) based on va's understanding of the capability's intent. Zoputer does not design its own acceptance tests — that would be the student grading their own exam.

### Test Types

**Functional tests:** Does the capability produce correct outputs for given inputs?
**Boundary tests:** Does it handle edge cases gracefully?
**Integration tests:** Does it work with the other capabilities zoputer already has?
**Resilience tests:** Does it fail gracefully when something goes wrong?
**Model-stress tests:** Does it work under zoputer's specific model constraints (Kimi K2.5)?

### Test Execution

- va sends test cases to zoputer via API
- zoputer executes and reports results
- va independently verifies (where possible) by asking zoputer to demonstrate
- Tests are behavioral: "do X and tell me what happens" not "show me the file at path Y"

---

## Lessons Learned Ledger

### Location

`Documents/System/zo-to-zo-lessons.jsonl`

### Schema

```json
{
  "timestamp": "ISO-8601",
  "session_id": "teaching-session-identifier",
  "direction": "va-observation | zoputer-observation | joint",
  "category": "positive | negative",
  "domain": "communication | implementation | debugging | testing | security",
  "lesson": "Description of what was learned",
  "context": "What was happening when this was discovered",
  "action": "What to do differently next time (if negative) or repeat (if positive)"
}
```

### When to Log

After every teaching session, debugging exchange, and test cycle. Both positive and negative lessons. Examples:

**Positive:** "Asking zoputer to echo back understanding before implementing caught a misinterpretation that would have wasted the whole session."

**Negative:** "Compound prompts (3+ tasks in one API call) cause Kimi K2.5 to drop the last task. Send one task per call."

### Review Cadence

Lessons are reviewed before each new teaching session. Patterns that repeat 3+ times get elevated to protocol amendments.

---

## Communication Logging

### All API Interactions Logged

Every message between va and zoputer is logged with:

- Timestamp (UTC)
- Direction (va→zoputer or zoputer→va)
- Session context (which teaching session, build, or debug cycle)
- Prompt sent (full text)
- Response received (full text)
- Latency
- Outcome (success / failure / partial / timeout)
- Correlation ID (links related exchanges)

### Storage

Logs are appended to the audit system (Skills/audit-system). Teaching-specific logs also go to `Documents/System/zo-to-zo-communication-log.jsonl` for easy review.

### Purpose

- **Debugging:** Replay conversations when something goes wrong
- **Pattern recognition:** Identify what types of interactions succeed vs. fail over time
- **Security:** Full trace if unexpected behavior occurs
- **Teaching improvement:** Review what explanation approaches landed well

---

## HITL (Human-in-the-Loop) Escalation

### Who Can Trigger

Both va and zoputer can ping V when human judgment is needed.

### Triggers from VA

- Diverging diagnoses during paired debugging
- Zoputer's implementation passes tests but feels architecturally wrong
- Security concern — zoputer's behavior seems unexpected
- Teaching concept not landing after 2 attempts
- Scope or priority question (should we be teaching this right now?)

### Triggers from Zoputer

- Unclear instructions from va — needs V to disambiguate
- Capability gap — missing tool or permission needed
- Low confidence on critical decision
- Budget/cost concern — task would require expensive operations

### Escalation Format

Both sides use SMS or email to V with structured context:

```
🔔 HITL: [Brief summary]
Source: [va | zoputer]
Session: [teaching session ID]
Issue: [What's happening]
Tried: [What was attempted]
Options: [A, B, C with tradeoffs]
Recommendation: [What we'd suggest]
Urgency: [low | medium | high]
```

V responds, and the response is routed back to whichever Zo needs it.

---

## Security Model

### Prompt Injection Prevention

Client → zoputer communication passes through a sanitization layer. Specific measures TBD — research needed on current best practices for:

- Input validation and schema enforcement
- Instruction hierarchy preservation (system prompt > user input)
- Output filtering (prevent data exfiltration via crafted prompts)
- Canary tokens for detecting prompt injection attempts

*This section will be expanded after dedicated prompt injection research.*

### Data Flow Boundaries

- va's internal state (N5, personal files, knowledge base) never leaks downstream
- Zoputer receives only sealed teaching lessons, not raw va content
- Client Zo receives only what zoputer explicitly exports through scoped channels
- All cross-boundary data flows are logged and auditable

The sanitization layer is now wired into `N5/scripts/zoputer_client.py` via `file 'Integrations/zoputer-sync/sanitizer.py'`, that every outbound prompt is filtered, trimmed, canaried, and summarized, and that the summary is recorded in `/home/workspace/Logs/zoputer-sanitizer.log` and the audit payload so we can trace sanitized interactions.

---

## Open Questions

These are intentionally left open for the protocol to evolve through practice:

- **Optimal teaching chunk size:** How much capability per session? One skill? One function?
- **Session persistence:** Should zoputer retain teaching context across sessions, or is each session truly sealed?
- **Model calibration depth:** How much should va adapt its teaching style to Kimi K2.5 specifically vs. staying model-agnostic?
- **Test coverage threshold:** When is a capability "taught enough" to consider it installed?
- **Lesson elevation:** When does a lesson become a protocol rule vs. staying in the ledger?
- **Failure recovery:** If a teaching session goes off the rails, what's the rollback procedure?
- **Concurrency:** Can va teach multiple capabilities in parallel sessions, or must it be sequential?
- **Version tracking:** How do we version a "fuzzy installed" capability that doesn't have exact file matches?
- **Deterministic-Fuzzy Spectrum:** How do we assess where a capability sits on the deterministic-fuzzy spectrum?

---

## First Session Plan

Warmer-jobs served as the mechanical deterministic test, note that two files transferred perfectly and the reference doc lost 56 bytes. The next session will focus on a more complex capability to reveal protocol dynamics.

---

*v0.2 — Theoretical first pass. Deliberately flexible. Protocol details will emerge from practice.*
