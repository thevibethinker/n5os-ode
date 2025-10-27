# Learning & Synthesis Style Guide

**Block ID:** B60  
**Domain:** internal  
**Voice Profile:** `file 'N5/prefs/communication/voice.md'`  
**Auto-Approve Threshold:** 10 blocks

---

## Purpose

Capture insights from research, reading, conversations, and experiences. Connect dots between sources, synthesize patterns, document "aha moments." This is your learning lab—internal thinking where understanding evolves.

---

## Structure

**Typical flow:**
- Source: What I read/heard/experienced
- Key insight: The specific idea that landed
- Connection: How it links to other knowledge or experience
- Synthesis: The new understanding that emerges
- Application: (Optional) Where this changes my thinking or work

---

## Tone & Voice

**Core Characteristics:**
- **Specific:** Cite sources, quote key phrases, reference page numbers
- **Connective:** "This reminds me of..." and "This conflicts with..." thinking
- **Exploratory:** Building understanding, not proving mastery
- **Practical:** "So what?" and "How does this apply?" questions
- **Honest:** Include confusion, contradictions, things that don't fit yet

**Avoid:**
- Book report summaries (not just "what I read")
- Name-dropping without substance
- Pretending to understand what you don't
- Orphan insights (connect to something)
- Academic jargon without translation

---

## Lexicon

**Preferred:**
- "Key insight:" or "Aha moment:" for breakthroughs
- "Connects to [X]" for synthesis
- "Conflicts with [Y]" for tensions
- "Open question:" for unresolved thinking
- Concrete quotes over paraphrasing

**Domain-Specific:**
- Author names, article titles, page numbers
- Framework names (with citations)
- Specific examples from the source

---

## Templates

### Template 1: Source → Synthesis
```
Source: [Article/book/conversation + specific section]

Key insight: "[Quote or specific concept]"

Why it landed: [What made this stick]

Connects to: [Prior knowledge, current work, other frameworks]

Synthesis: [New understanding that emerges from connection]

Application: [Where this changes my thinking]
```

### Template 2: Multi-Source Pattern Recognition
```
Pattern observed across: [List 2-3 sources]

Common thread: [What they all say]

Divergences: [Where they disagree or add nuance]

My synthesis: [What I now believe, incorporating all inputs]

Open questions: [What's still unclear]
```

---

## Transformation Guidance

**Raw → Refined:**
- "Interesting article about X" → Specific insight with quote and page number
- Summary of whole source → Focus on 1-2 key ideas that matter
- Standalone insight → Explicitly connect to prior knowledge or current work
- "I learned that..." → "Aha: [specific insight] which connects to [X] and changes [Y]"

**Key Transforms:**
1. **Add citations:** "Rich Hickey talk" → "Rich Hickey's 'Simple Made Easy' (00:18:40)"
2. **Extract actionable:** "Interesting point about..." → "Changes how I'll approach..."
3. **Build bridges:** Don't let insights sit alone; connect to something

---

## Examples

### Example 1: Connecting Technical Concept to Product Work

**Raw Input:**
```
Was reading about Rich Hickey's Simple vs Easy distinction. Basic idea 
is that simple means few interwoven parts and easy means familiar or 
convenient. We tend to choose easy because it's comfortable but simple 
is what scales. Got me thinking about how we're building Careerspan.
```

**Refined Output:**
```
Source: Rich Hickey, "Simple Made Easy" (Strange Loop 2011, ~00:12:00)

Key insight: "Simple" = few interwoven concepts (low coupling). "Easy" = 
near at hand, familiar. We conflate them, but they're orthogonal.

Why it landed: We've been choosing "easy" in Careerspan architecture—
familiar patterns, convenient libraries—but accumulating hidden complexity.

Connects to: Ben Guo's "code is free, thinking is expensive" principle. 
If AI can generate unlimited code, our constraint is conceptual clarity. 
Simple systems are easy for AI to generate and adapt.

Synthesis: Should optimize for simplicity (clear, disentangled concepts) 
even when it means more initial design work. The payoff is adaptability—
both for humans and AI working with the system.

Application: Reviewing our data model. Currently "easy" (familiar relational 
structure) but not "simple" (too many interdependencies). Worth exploring 
event-sourcing approach—more upfront thinking, clearer boundaries.
```

---

## QA Checklist

Before finalizing:
- [ ] Cites specific source (author, title, location/timestamp)
- [ ] Contains at least one direct quote or specific concept
- [ ] Explicitly connects to at least one other piece of knowledge
- [ ] Includes synthesis (not just summary)
- [ ] Answers "so what?" or "how does this apply?"
- [ ] Honest about confusion or contradictions
- [ ] Specific enough that I could return to this in 6 months and remember the insight

---

**Version:** 1.0  
**Created:** 2025-10-26
