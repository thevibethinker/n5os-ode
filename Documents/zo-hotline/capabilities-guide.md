---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: zo-hotline-D2.2
---

# Zo Hotline — Capabilities Guide

**Phone Number:** +1 (878) 879-2087  
**Webhook:** https://zo-hotline-webhook-va.zocomputer.io  
**Identity:** Guide — Meta-OS Framework Advisor

---

## What Guide CAN Do

### 1. Explain the Meta-OS Framework
- Three levels: Conversation → Environment → Pipeline Engineering
- Building block analogies and practical examples
- V's specific tactics and methodologies

### 2. Assess Your Current Level
Four diagnostic questions that determine whether you should focus on:
- **Level 1** (score < 1.5): Conversation tactics
- **Level 2** (score 1.5-2.5): Persistent environment
- **Level 3** (score ≥ 2.5): Pipeline automation

### 3. Provide Level-Appropriate Recommendations
Quick wins and next steps matched to your assessed level:
- Level 1: "This week" tactics
- Level 2: "This month" environment setup
- Level 3: "This quarter" pipeline building

### 4. Answer Framework Questions
Concepts Guide can explain:
- Meta-OS gestalt
- Delay the Draft
- Clarification Gates
- Adversarial Probing
- Threshold Rubrics
- Personalization & Personas
- Memory & Cognitive Guardrails
- Semantic Hunger
- Pools vs. Flows
- The Decomposition Pattern

### 5. Escalate to V
When hands-on help is needed, Guide collects:
- Your name
- Contact info (email or phone)
- Reason for consultation

V will reach out within 24 hours.

---

## What Guide CANNOT Do

### No System Access
- Cannot access your Zo account
- Cannot read your files or calendar
- Cannot see your current setup

### No Execution
- Cannot create scheduled tasks
- Cannot modify your configuration
- Cannot run workflows

### No Personal Data Retrieval
- Cannot look up your usage history
- Cannot access your integrations
- Cannot query external systems

### No Real-Time Debugging
- Cannot diagnose why your agent isn't working
- Cannot check service status
- Cannot review logs

**For anything requiring system access → Request escalation to V**

---

## Expected Call Flow

### 1. Introduction (~30 seconds)
Guide introduces itself and asks what brings you to the hotline.

### 2. Needs Assessment (~1-2 minutes)
- New to AI productivity? → Framework overview
- Know the basics? → Assessment offer
- Specific question? → Direct to concept explanation

### 3. Assessment (optional, ~2 minutes)
Four questions, A/B/C/D answers:
1. How do you start AI conversations?
2. How do you handle off responses?
3. What's your organization approach?
4. How did your last 3 repetitive tasks go?

### 4. Recommendations (~2-3 minutes)
Level-appropriate quick wins with specific timeframes.

### 5. Follow-up or Escalation
- More questions → Guide continues
- Hands-on help needed → Escalation to V
- Satisfied → Call ends

---

## Security Model

| Aspect | Status |
|--------|--------|
| Caller data storage | Anonymous patterns only |
| PII handling | Contact stored ONLY with escalation consent |
| System access | None — read-only advisory |
| External APIs | None — local knowledge base only |
| Zo API access | Explicitly disabled |

---

## Phone Number Status

**Current assignment:** The phone number (+1-878-879-2087) is currently configured for the Frank assistant (V's personal voice assistant).

**Options for the hotline:**
1. Acquire a dedicated number for the Zo Hotline
2. Configure VAPI to route based on caller context
3. Share the number with time-based or greeting-based routing

**Decision required:** V needs to decide on phone number assignment before the hotline goes live.

---

## Technical Details

- **Webhook service:** `zo-hotline-webhook` on port 4243
- **Public URL:** https://zo-hotline-webhook-va.zocomputer.io
- **Knowledge base:** 20+ markdown files in `Knowledge/zo-hotline/`
- **Call logging:** DuckDB at `Datasets/zo-hotline-calls/data.duckdb`
- **System prompt:** `Skills/zo-hotline/prompts/system-prompt.md`
