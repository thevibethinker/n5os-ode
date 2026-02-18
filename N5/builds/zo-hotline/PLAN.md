---
created: 2026-02-12
last_edited: 2026-02-12
version: 2
type: build_plan
status: ready
---
# Plan: Zo Hotline - Meta-OS Leveling Framework

**Objective:** Create a voice-accessible advisory hotline (+1-878-879-2087) that helps callers understand and advance through the Meta-OS leveling framework — moving from Conversation Engineering (Level 1) through Environment Engineering (Level 2) to Pipeline Engineering (Level 3).

**Trigger:** V wants a voice channel that embodies his "Fundamentals of AI Productivity" framework from the NextPlay presentation — helping people build their personal Meta-OS through assessment, advice, and creative recommendations based on V's patterns and tactics.

**Key Design Principle:** The hotline is an *advisory* system — read-only, no execution. It assesses caller level, explains the framework, suggests tactics, and inspires with what's possible. No access to caller's actual Zo data or ability to modify anything.

---

## Clarifying Questions (RESOLVED)

1. **Top 10 things people call about?** → RESOLVED: Meta-OS conceptual questions, leveling assessment, tactics for advancing, creative workflow ideas

2. **Caller authentication?** → RESOLVED: Not needed — read-only advisory only, no execution or data access

3. **What number to use?** → RESOLVED: Zoeputer's number (separate Zo instance), not V's main Zo

4. **Target audience?** → RESOLVED: People who already know Zo and want to level up their usage

---

## Core Framework Reference

### The Three Levels (Meta-OS)

| Level | Name | What You Engineer | Persistence |
|-------|------|-------------------|-------------|
| **1** | Conversation | Context within a single chat | Ephemeral |
| **2** | Environment | Persistent personalization | Durable |
| **3** | Pipeline | Connections to external world | Living |

### V's Key Tactics
- **Delay the Draft** — Build context before requesting deliverables
- **Clarification Gates** — Force AI to ask questions first
- **Adversarial Probing** — Stress-test outputs
- **Threshold Rubrics** — Define conditions before answers
- **Offensive/Defensive Modes** — Signal expansion vs. synthesis

---

## Build Phases

### Wave 1: Foundation
- **W1.1:** Knowledge Base — Meta-OS framework docs, V's tactics, assessment questions
- **W1.2:** Voice Agent Config — Hotline assistant with read-only system prompt

### Wave 2: Integration & Launch
- **W2.1:** Webhook Server — Read-only assistant-request handler, no Zo API tools
- **W2.2:** Polish & Documentation — Testing, SKILL.md, export to Zoeputer

---

## Security Model (CRITICAL)

**READ-ONLY ARCHITECTURE:**
- ✅ Webhook reads from local knowledge files only
- ✅ No Zo API tools registered
- ✅ No ability to query caller's data
- ✅ No execution of workflows
- ✅ Pure advisory/advocacy role

**Tools available to voice agent:**
- `assessCallerLevel` — Optional 3-4 question assessment
- `getRecommendations` — Pull from knowledge base based on level
- `explainConcept` — Retrieve framework explanations
- `logCallRecap` — (Internal) Save transcript for V's review

---

## Success Metrics

1. Callers can complete optional assessment and get level determination
2. Callers receive relevant Meta-OS tactics for their level
3. Voice agent correctly explains the three-level framework
4. System runs read-only (verified: no data access, no execution)
5. Successfully exported to Zoeputer

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OPSEC — caller asks agent to modify V's Zo | No Zo API tools; webhook is read-only |
| Knowledge base becomes stale | Version with build; update quarterly |
| VAPI costs | Monitor usage; implement caps |
| Voice agent hallucinates V's patterns | Ground in documented tactics from knowledge base |

---

## Level Upper Review (COMPLETE)

Key insights incorporated:
1. **Counterintuitive capability:** Voice is actually BETTER for conceptual explanation than text — people process frameworks differently when hearing them
2. **Riskiest assumption:** That people want assessment; making it optional preserves agency
3. **Delight factor:** The assessment feels like a personalized diagnostic, not a survey — "Here's where you are, and here's what opens up next"
