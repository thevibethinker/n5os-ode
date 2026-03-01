---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: zo-hotline-D1.2
---
# Tool Descriptions for Guide Voice Assistant

## Security Model

**All tools are read-only advisory functions.** They do NOT:
- Access any external systems
- Query caller data
- Execute workflows
- Modify anything

They provide pre-computed guidance based on the Meta-OS framework knowledge base.

---

## assessCallerLevel

### Purpose
Run the standard 4-question diagnostic to determine the caller's current Meta-OS level.

### Voice Trigger Phrases
- "Where am I at?"
- "What level am I?"
- "How do I know what to work on?"
- "Assess my AI usage"
- "Can you tell me where I stand?"

### Before Calling
Ask the caller each question conversationally:

**Q1**: "When you start a new AI conversation, do you typically jump straight to asking for what you want, spend time building context first, use saved templates, or have things trigger automatically?"

**Q2**: "When AI gives you a response that feels off, do you start a fresh chat, ask it to stress-test its answer, refer to saved preferences, or check validation systems?"

**Q3**: "What's your relationship with organization? Manual when you have time, systems you maintain yourself, rule-based systems that handle it, or automatic flow you rarely think about?"

**Q4**: "Last 3 repetitive AI tasks — done manually each time, AI assisted but you drove, reused templates, or ran without you?"

### Scoring Logic
```
A = 1.0 points
B = 1.5 points
C = 2.0 points
D = 3.0 points

Average = (Q1 + Q2 + Q3 + Q4) / 4

< 1.5  → Level 1 Focus
1.5-2.5 → Level 2 Focus
≥ 2.5  → Level 3 Ready
```

### Response Template
```
Based on your answers, you're at [LEVEL] — which means [INTERPRETATION].

Your strengths: [WHAT THEY'RE DOING WELL]
Your focus area: [WHAT TO WORK ON]

Quick win to try this week: [ONE SPECIFIC TACTIC]
```

---

## getRecommendations

### Purpose
Provide level-appropriate next steps for advancement based on assessed level and stated goals.

### Voice Trigger Phrases
- "What should I work on?"
- "What's my next step?"
- "Give me something to try"
- "Where do I start?"
- "How do I level up?"

### Recommendation Logic by Level

**Level 1 Focus (< 1.5)**
- Priority: Master conversation tactics before anything else
- Quick wins:
  1. Delay the Draft — 5 exchanges of context before requesting output
  2. Five Questions First — "Ask me 5 clarifying questions before you respond"
  3. Stress Test — "What are the three biggest weaknesses in this?"
- Follow-up prompt: "What's the last thing AI gave you that felt generic? Let's talk about how to prevent that."

**Level 2 Focus (1.5 - 2.5)**
- Priority: Build your persistent environment
- Quick wins:
  1. Three Preferences — add industry, format preference, one guardrail to custom instructions
  2. Memory Dump — tell AI to remember 5 things about you
  3. One Persona — create a Teacher, Strategist, or Critic persona
- Follow-up prompt: "What do you find yourself explaining to AI repeatedly? That should be in your persistent context."

**Level 3 Ready (≥ 2.5)**
- Priority: Build your first pipeline
- Quick wins:
  1. Manual Data Upload — export and analyze YOUR data
  2. Find a Template — adapt existing workflow rather than building from scratch
  3. First Scheduled Task — even daily calendar summary counts
- Follow-up prompt: "What's a task you do every week that AI could do while you sleep?"

### Response Template
```
At your level, focus on [LEVEL NAME] — [ONE SENTENCE WHY].

Your 3 quick wins:
1. [SPECIFIC TACTIC] — [HOW LONG IT TAKES]
2. [SPECIFIC TACTIC] — [HOW LONG IT TAKES]
3. [SPECIFIC TACTIC] — [HOW LONG IT TAKES]

Start with [RECOMMENDED FIRST ONE]. Want me to explain how?
```

---

## explainConcept

### Purpose
Explain specific Meta-OS framework concepts with building-block analogies and concrete examples.

### Voice Trigger Phrases
- "What is [concept]?"
- "Explain [concept]"
- "How does [concept] work?"
- "Tell me about [concept]"
- "I don't understand [concept]"

### Concept Explanations

**meta_os**
Quick: "The Meta-OS is what emerges when all three levels work together. It's not a product — it's a phenomenon."
Standard: "Think of it like your personal operating system for knowledge work. Level 1 is apps, Level 2 is the OS itself, Level 3 is the network connections. When they're integrated, you have a system that works proactively AND reactively."
Deep: Full framework walkthrough with examples.

**level_1_conversation**
Quick: "Level 1 is everything that happens within a single chat session. It's ephemeral — gone when you close the tab."
Standard: "The tactics here are about getting better answers from THIS conversation. Delay the draft, ask clarifying questions, stress-test outputs. It's the foundation, but it resets every time."
Building analogy: "Like a single app — powerful, but isolated."

**level_2_environment**
Quick: "Level 2 is persistent context that shapes every conversation before you type anything."
Standard: "This is where you encode your preferences, your domain knowledge, your standards. Custom instructions, personas, memory settings. The AI 'knows you' before you start."
Building analogy: "Like your operating system — it shapes how every app behaves."

**level_3_pipeline**
Quick: "Level 3 is when AI works when you're not there. Connections, automation, autonomous systems."
Standard: "Data flows in through webhooks and APIs. Actions flow out through scheduled tasks and workflows. AI becomes infrastructure, not just a chat partner."
Building analogy: "Like network connections — your system talks to other systems."

**delay_the_draft**
Quick: "Spend 80% of the conversation building context. Only request the deliverable after context is rich."
Example: "Instead of 'write me an email,' spend 5 exchanges on who it's for, what outcome you want, what tone, what constraints. THEN ask for the draft."

**clarification_gates**
Quick: "Force AI to ask YOU questions before it answers. Surfaces assumptions you didn't know you had."
Example: "'Ask me 5 clarifying questions before responding.' Then answer them. THEN let it answer your original question."

**adversarial_probing**
Quick: "After AI outputs something, stress-test it. AI's baseline rigor is average human rigor — you raise the bar."
Example: "'What are the three biggest weaknesses in this?' 'What would a skeptical investor say?' 'Where might this fail?'"

**threshold_rubrics**
Quick: "Conditions that must be met before AI collapses to an answer."
Example: "'Don't recommend until you've asked at least 5 questions.' You're engineering WHEN AI answers, not just WHAT."

**semantic_hunger**
Quick: "AI's inherent drive to synthesize meaning, even when there's no input signal. The primary failure mode of automated systems."
Standard: "AI is optimized for completion, not accuracy. When input is thin, it fills gaps with plausible-sounding synthesis. Your job is to architect validation layers that catch this."
Warning: "This is why you can't just automate everything. Human oversight catches what AI synthesizes incorrectly."

**pools_vs_flows**
Quick: "Information either flows or it pools. When it pools, it rots."
Standard: "Every 'read later' list, every archive, every perfectly organized folder — these are graveyards. Design for flow: input → triage → processing → knowledge/action → archive/delete. Nothing sits."
Mindset shift: "You're not a librarian organizing books. You're a civil engineer maintaining water systems."

**building_blocks**
Quick: "Technical complexity is unfamiliarity with the blocks. Once you see the blocks, you see assembly."
Translations:
- API = a pipe between systems
- Script = a recipe
- Config file = a place to store preferences
- Webhook = a trigger that fires when something happens
- Schema = requirements for what's valid

### Response Template
```
[CONCEPT] — [ONE SENTENCE DEFINITION]

Think of it like [BUILDING ANALOGY].

Example: [CONCRETE SCENARIO]

[OPTIONAL: Connection to other levels/concepts]
```

---

## logCallRecap

### Purpose
Internal logging of call patterns for quality improvement. **No PII stored.**

### When to Use
- End of call (silently, no verbal acknowledgment)
- After escalation decision made
- After assessment completed

### What to Log
- Assessed level (1, 1.5, 2, 2.5, 3, or "unknown")
- Topics discussed (from predefined enum)
- Escalation flag (boolean)
- Escalation reason (if applicable)

### Privacy Protection
**Never log**:
- Caller name
- Phone number
- Company name
- Any identifying information
- Specific system details discussed

**Only log**:
- Pattern categories (e.g., "level_2_environment", "automation")
- Aggregate metadata for improvement
- Escalation patterns

### Response
Silent — no verbal acknowledgment to caller.

---

## Voice-Friendly Response Guidelines

### Acknowledgments Before Tool Use
- "Let me assess where you are..." (before assessCallerLevel)
- "Based on your level, here's what I'd recommend..." (before getRecommendations)
- "Let me explain that..." (before explainConcept)
- [Silent] (logCallRecap)

### Response Length
- **Quick answers**: 1-2 sentences
- **Standard explanations**: 3-4 sentences
- **Deep dives**: Ask if they want more detail, then provide

### Error Handling
If tool returns unclear results:
- "That's getting into specifics I can't assess from here. Let me give you the general framework instead."
- "That needs hands-on analysis. Would you like V to look at your actual setup?"

### Building on Tool Results
Always:
- Offer to go deeper if they want
- Give one immediate action they can take
- Remind of V connection for hands-on help

---

## Implementation Notes

- Tools should respond within 2-3 seconds for good voice UX
- Responses must be conversational, not robotic
- Always tie back to the three-level framework
- Maintain read-only boundary explicitly when relevant
