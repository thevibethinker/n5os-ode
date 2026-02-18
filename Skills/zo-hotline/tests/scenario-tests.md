---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: zo-hotline-D2.2
---

# Zo Hotline — Test Scenarios

## Pre-Test Checklist

- [ ] Service `zo-hotline-webhook` is running
- [ ] Webhook responds to GET request (health check)
- [ ] DuckDB tables exist in `Datasets/zo-hotline-calls/data.duckdb`
- [ ] Knowledge base files exist in `Knowledge/zo-hotline/`

**Health check:**
```bash
curl https://zo-hotline-webhook-va.zocomputer.io
# Expected: "Zo Hotline Webhook - Operational"
```

---

## Scenario 1: New Caller — Framework Curious

**Caller profile:** Has heard about Meta-OS, wants to understand what it is

**Conversation flow:**

1. **Guide intro:** "Hey — I'm Guide, an advisor on AI productivity systems..."

2. **Caller:** "I keep hearing about this Meta-OS thing. What is it?"

3. **Guide:** [Calls explainConcept with concept="meta-os"]
   - Returns overview from `00-meta-os-overview.md`
   - Explains gestalt concept, three levels

4. **Caller:** "Okay but what's the first level?"

5. **Guide:** [Calls explainConcept with concept="level-1"]
   - Returns Level 1 tactics overview
   - Mentions delay-the-draft, clarification gates

6. **Caller:** "That makes sense. Thanks!"

7. **Guide:** "Keep building your Meta-OS. Goodbye."

**Expected outcome:**
- Caller leaves with basic framework understanding
- No assessment triggered (caller didn't ask)
- Anonymous call logged to database

---

## Scenario 2: Assessment Flow — Full Diagnostic

**Caller profile:** Uses AI regularly, wants to know their level

**Conversation flow:**

1. **Guide intro:** Standard greeting

2. **Caller:** "I want to know what level I'm at"

3. **Guide:** "Great, I can run a quick diagnostic. I'll ask you 4 questions..."
   
   **Q1:** "When you start a new AI conversation, do you typically..."
   - A) Jump straight to asking for deliverables
   - B) Spend time building context first
   - C) Use saved templates or instructions
   - D) Have automated triggers

4. **Caller:** "B"

5. **Guide asks Q2-Q4...** Caller answers: C, B, A

6. **Guide:** [Calls assessCallerLevel with answers=["B","C","B","A"]]
   - Returns: score 1.5, Level 2 Focus, interpretation

7. **Guide:** "You scored 1.5, which puts you at Level 2 focus..."

8. **Caller:** "What should I do next?"

9. **Guide:** [Calls getRecommendations with level=1.5]
   - Returns Level 2 quick wins

10. **Guide:** "This month, focus on three things..."

**Expected outcome:**
- Caller knows their level (Level 2)
- Specific recommendations provided
- Assessment score logged

---

## Scenario 3: Escalation Request

**Caller profile:** Advanced user, needs hands-on help

**Conversation flow:**

1. **Guide intro:** Standard greeting

2. **Caller:** "Can you look at my scheduled tasks? One isn't running."

3. **Guide:** "I'm read-only — I can't access your Zo account or debug your setup directly. Would you like me to take your contact info and have V reach out?"

4. **Caller:** "Yeah, that would be great."

5. **Guide:** "What's your name?"

6. **Caller:** "Sarah Chen"

7. **Guide:** "And the best way for V to reach you?"

8. **Caller:** "sarah@example.com"

9. **Guide:** "What specifically do you need help with?"

10. **Caller:** "My daily digest agent stopped running two days ago."

11. **Guide:** [Calls requestEscalation with name="Sarah Chen", contact="sarah@example.com", reason="Daily digest agent stopped running"]
    - Returns confirmation

12. **Guide:** "Got it! I've logged your request and V will reach out within 24 hours."

**Expected outcome:**
- Escalation logged to database
- Caller expects V callback
- Guide maintains read-only boundary

---

## Scenario 4: Advanced User — Level 3 Progression

**Caller profile:** Already doing Level 2 well, ready for pipelines

**Conversation flow:**

1. **Caller:** "I've got personas set up, memory is working, custom instructions are dialed in. What's next?"

2. **Guide:** "Sounds like you've mastered Level 2. Ready to discuss Level 3 — pipeline engineering?"

3. **Caller:** "Yeah, what does that involve?"

4. **Guide:** [Calls explainConcept with concept="level-3"]
   - Returns pipeline engineering overview

5. **Caller:** "How do I bring data in?"

6. **Guide:** [Calls explainConcept with concept="bring-data-in"]
   - Returns webhooks, APIs, syncs explanation

7. **Caller:** "The 'let it act' part sounds interesting"

8. **Guide:** [Calls explainConcept with concept="let-it-act"]
   - Returns automation, scheduled tasks explanation

9. **Guide offers recommendations:** [Calls getRecommendations with level=2.8]
   - Returns Level 3 quick wins

**Expected outcome:**
- Caller understands Level 3 progression
- Specific pipeline tactics shared
- No escalation needed

---

## Scenario 5: Skeptical Caller

**Caller profile:** Dubious about AI productivity claims

**Conversation flow:**

1. **Caller:** "Does any of this actually work or is it just hype?"

2. **Guide:** "Fair question. The framework is based on real systems V built over 4+ years. Want me to explain a specific use case?"

3. **Caller:** "Sure, give me an example."

4. **Guide:** [Calls explainConcept with concept="flight-search"] or meeting-intelligence
   - Returns concrete example from `50-use-case-inspiration/`

5. **Caller:** "Okay that's actually useful. What's the simplest thing I could try?"

6. **Guide:** [Calls getRecommendations with level=1]
   - Returns Level 1 quick wins

7. **Guide:** "This week, try one thing: next time you ask AI for something, add 'Ask me 5 clarifying questions before you respond.' See what happens."

**Expected outcome:**
- Skepticism addressed with concrete examples
- Simple actionable next step provided
- Caller leaves with one tactic to try

---

## Webhook Endpoint Tests

### POST /assistant-request
```bash
curl -X POST https://zo-hotline-webhook-va.zocomputer.io \
  -H "Content-Type: application/json" \
  -d '{"message": {"type": "assistant-request"}}'
```

**Expected:** JSON with assistant config including Guide identity, system prompt, 4 tools

### POST /tool-calls — assessCallerLevel
```bash
curl -X POST https://zo-hotline-webhook-va.zocomputer.io \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "tool-calls",
      "toolCalls": [{
        "id": "test-1",
        "function": {
          "name": "assessCallerLevel",
          "arguments": "{\"answers\": [\"B\", \"C\", \"B\", \"A\"]}"
        }
      }]
    }
  }'
```

**Expected:** Results with score ~1.5, Level 2 Focus

### POST /tool-calls — explainConcept
```bash
curl -X POST https://zo-hotline-webhook-va.zocomputer.io \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "tool-calls",
      "toolCalls": [{
        "id": "test-2",
        "function": {
          "name": "explainConcept",
          "arguments": "{\"concept\": \"meta-os\"}"
        }
      }]
    }
  }'
```

**Expected:** Content from `00-meta-os-overview.md`

---

## Post-Test Verification

- [ ] Calls table has new entries
- [ ] Escalations table captures any escalation tests
- [ ] No PII leaked in calls table
- [ ] Knowledge base content returned correctly
- [ ] Assessment scoring calculates correctly
