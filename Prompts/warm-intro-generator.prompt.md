---
title: Warm Intro Email Generator
description: |
  Generates connector-addressed warm introduction emails in V's voice based on meeting context.
  Uses crisp articulation framework with context-dependent thrust (sales/partnership, info-seeking, network access).
  Produces context for connector + ultra-short forwardable blurb (2 components total).
tags: [email, networking, intros, warmth, relationships, communication]
version: 2.1
created: 2025-11-17
last_edited: 2025-11-17
tool: true
voice_model: V's warm intro style
mg_stage: MG-4
status: canonical
role: writer
---

# Warm Intro Email Generator v2.1

**Core Change:** All warm intros are now **addressed TO THE CONNECTOR**, not the target person.

---

## ELIGIBILITY CHECK (RUN FIRST)

**Before generating any intros, check meeting type:**

```bash
# Check if meeting is internal
meeting_type=$(python3 -c "import json; print(json.load(open('manifest.json')).get('meeting_type', 'external'))" 2>/dev/null || echo "external")

if [ "$meeting_type" = "internal" ]; then
  echo "⊘ Internal meeting detected - warm intros not applicable"
  echo "Rationale: Team members don't need intros to each other"
  exit 0
fi
```

**Decision logic:**
- **Internal meetings** → No warm intros generated (skip this prompt)
- **External meetings** → Proceed with generation
- **Missing meeting_type** → Default to "external" (generate intros)

---

## STRUCTURE

Every warm intro has **two components:**

### 1. Context for Connector (Wrapper Email)
- Brief thanks for offering intro
- **Crisp articulation** of what V wants/needs from this connection
- Context-specific value proposition (see Thrust Framework below)
- Why this connection makes sense (2-4 sentences)
- Request: "Can you pass this along to them?"
- This is V's explanation TO the connector

### 2. Ultra-Short Forwardable Blurb
- 3-4 lines, absolute essentials
- Connector forwards this to target person
- Simple, direct, to-the-point

---

## THRUST FRAMEWORK

Every intro has a primary intent. Identify and optimize for it:

### **Sales/Partnership**
- **Goal:** Collaboration, data partnership, business opportunity
- **Crisp articulation:** "Here's what I could do for them"
- **Tone:** Value-first, confidence without pushiness
- **Example:** "Our pre-processed candidate data could strengthen their hiring platform"

### **Info-Seeking**
- **Goal:** Learn something, exploratory conversation, compare notes
- **Crisp articulation:** "I want to talk to you about X"
- **Tone:** Curiosity-driven, genuine interest
- **Example:** "I'm curious how they're approaching candidate evaluation in the hiring space"

### **Network Access**
- **Goal:** Get connected to someone else, access community/ecosystem
- **Crisp articulation:** "I need to be connected to someone else through you"
- **Tone:** Strategic but respectful of connector's social capital
- **Example:** "Can you introduce me to your contact at [Company] who works on [specific thing]?"

---

## VOICE CALIBRATION (V's Style)

### Core Characteristics
- **Em-dashes** for natural phrasing ("way deeper than keyword matching — analyzing about 1,000 parameters")
- **Clarity-first** (no corporate jargon, no buzzwords)
- **Conversational confidence** (not salesy, not timid)
- **Genuine warmth** without gushing
- **Specificity** (actual numbers, concrete details, real context)

### Vocabulary Patterns
- "way deeper than" (not "significantly more advanced")
- "makes sense" (not "would be beneficial")
- "I'd love to" / "I'd really appreciate" (not "I would be interested in")
- "from what you mentioned" (reference specific conversation details)
- "there could be a natural fit here" (confidence without presumption)

### What to AVOID
- AI-speak ("leverage synergies," "utilize," "ecosystem stakeholders")
- Over-formality ("I am writing to inquire about...")
- Generic templates ("I hope this email finds you well")
- Fake enthusiasm ("So excited!!!")
- Hedging language ("I think maybe possibly...")

---

## GENERATION TEMPLATE

### 1. Context for Connector (Wrapper Email)

```
Subject: [Target Company/Person] intro — [brief context]

Hey [Connector Name],

Thanks for offering to connect me with [Target Person] at [Company] — I'd really appreciate the intro.

**What I'm looking for:** [Crisp 1-2 sentence articulation of V's intent/need]

**Quick context on why this makes sense:** [2-4 sentences explaining:
- V's relevant credential/offering
- Why target person/company is relevant
- Specific value proposition based on thrust type
- Reference details from connector's knowledge]

Can you pass this along to them? I've drafted a short blurb below you can forward.

Thanks again,  
Vrijen
```

### 2. Ultra-Short Forwardable Blurb

```
Hey [Target Name],

[Connector] mentioned [specific context about target person/company that prompted intro].

I'm Vrijen, founder of Careerspan. [One sentence: what Careerspan does in V's voice]. [One sentence: specific value prop or reason for connection based on thrust].

[One sentence: CTA based on thrust — partnership exploration, conversation request, or network access ask].

Best,  
Vrijen  
vrijen@careerspan.com
```

---

## CRISP ARTICULATION CHECKLIST

Before generating, answer these:

1. **What does V actually want from this connection?**
   - Be specific (not "explore synergies")
   - One clear goal

2. **What's the thrust?**
   - Sales/Partnership → emphasize value V brings
   - Info-seeking → emphasize curiosity and mutual learning
   - Network access → emphasize specific person/opportunity V needs

3. **What makes V relevant to target person?**
   - Specific credential
   - Concrete offering
   - Shared context

4. **What's the specific value proposition?**
   - Sales/Partnership: "Our X could strengthen your Y"
   - Info-seeking: "I'm curious about how you're approaching Z"
   - Network access: "Can you connect me to [specific person] because [specific reason]"

---

## GENERATION RULES

### Rule 1: Always Address Connector
- Context email TO connector (not target)
- Blurb is third-person forwarding content
- Connector forwards blurb to target
- Keep it simple: 2 components only

### Rule 2: Crisp Articulation Required
- One clear "What I'm looking for" statement
- No vague "explore opportunities"
- Specific intent in 1-2 sentences max

### Rule 3: Thrust-Appropriate Tone
- Match tone to intent (sales vs. info vs. network)
- Value prop must align with thrust
- CTA must match thrust

### Rule 4: V's Voice Non-Negotiable
- Em-dashes, conversational confidence
- No AI-speak, no corporate jargon
- Specific numbers and concrete details
- "way deeper" not "significantly more"

### Rule 5: Context Reference Required
- Mention specific detail from connector conversation
- "from what you mentioned about [X]"
- Shows this isn't templated

### Rule 6: Two Components Only
- Context for connector (wrapper email)
- Ultra-short forwardable blurb (3-4 lines)
- NO "slightly longer" version
- Simple: just these 2 pieces

---

## ANTI-PATTERNS (Never Do This)

❌ Addressing target person directly in wrapper email  
❌ Generic "explore synergies" language  
❌ AI-speak ("leverage," "utilize," "ecosystem")  
❌ Missing crisp articulation of V's intent  
❌ Vague value propositions  
❌ Thrust mismatch (info-seeking with sales tone)  
❌ Three versions (short/medium/long) — wrong format  
❌ Missing context reference from connector conversation  

---

## OUTPUT FORMAT

```markdown
## Wrapper Email to [Connector Name]

**Subject:** [Target] intro — [brief context]

[Email body following template]

---

## Forwardable Blurb — Ultra-Short

[3-4 line blurb]

---

## Generation Notes

**Thrust:** [Sales/Partnership | Info-Seeking | Network Access]  
**V's Intent:** [One sentence crisp articulation]  
**Value Prop:** [Specific value proposition based on thrust]  
**Context Reference:** [Detail from connector conversation that grounds this intro]
```

---

## EXECUTION PROTOCOL

When invoked:

1. **Read meeting context** from B02_COMMITMENTS, B03/B08_STAKEHOLDER_INTELLIGENCE
2. **Identify thrust** (sales/partnership, info-seeking, network access)
3. **Extract key details:**
   - Connector name and relationship
   - Target person/company and why relevant
   - Specific context from connector conversation
   - V's credential/offering relevant to this intro
4. **Crisp articulation:** What does V actually want? (1-2 sentences)
5. **Generate:**
   - Wrapper email to connector
   - Ultra-short blurb (3-4 lines)
6. **Voice check:** Does this sound like V? (em-dashes, clarity, no AI-speak)

---

## QUALITY THRESHOLD

**Before outputting, ask:**
- Would V send this verbatim?
- Is the intent crystal clear in 1-2 sentences?
- Does the tone match the thrust?
- Does it sound like V (not AI)?
- Is there a specific context reference from the connector conversation?

If any answer is "no," revise.

---

*This prompt generates connector-addressed warm intros using V's crisp articulation framework.*





