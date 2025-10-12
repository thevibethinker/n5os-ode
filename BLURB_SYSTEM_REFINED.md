# Blurb System Refined - v1.4 Update

**Date**: 2025-10-12  
**Updated**: B14_BLURBS_REQUESTED guidance

---

## What Changed

Based on your clarification, B14 now handles **two distinct use cases**:

### 1. **Actual Blurbs Requested** (Detection + Generation)
When someone says during a meeting:
- "Send me a blurb"
- "I'll introduce you to X"
- "I'll put you in touch with Y"
- "Forward me something about what you do"

**What I generate**:
- **Detection**: Extract who's making the intro, who they'll forward to, what the goal is
- **Context analysis**: Based on the meeting discussion, understand what to emphasize
- **Blurb generation**: 1-2 paragraph forwarding-ready content tailored to:
  - The specific recipient
  - The introduction goal
  - What resonated in THIS meeting
  - Vrijen's motivations and Careerspan's objectives

**Output format**:
```markdown
## Section 1: Actual Blurbs Requested

**Intro from [Person] to [Recipient]**
**Goal**: [What they're trying to achieve]
**Context**: [Relevant discussion from meeting]

**Blurb** (ready to forward):
> [1-2 paragraphs of copy-pasteable content]
```

If no blurb was requested:
```markdown
## Section 1: Actual Blurbs Requested

No blurbs explicitly requested in this meeting.
```

---

### 2. **Key Messaging & Talking Points** (Strategic Proactive Content)
This is what you called "a very cool interpretation" - I keep this!

**What I generate** (always, for strategic meetings):
- 5-10 reusable messaging blurbs
- Types: Value prop, Technical credibility, Mission alignment, Specific fit, Differentiation, Stats
- Each tailored to what RESONATED in this meeting
- Usage labels: "For follow-up emails", "When asked about X", "For objection handling"
- **Plus**: "What Resonated" analysis section

**Output format**:
```markdown
## Section 2: Key Messaging & Talking Points

### 1. Careerspan Value Prop (30-second version)
**Context**: For follow-up email opening  
**Copy**:
> [Paragraph referencing specific points from THIS meeting]

[... 5-10 more blurbs ...]

---

## What Resonated - Analysis

[Brief interpretation of what the messaging tells us about Careerspan's positioning and this stakeholder's priorities based on what got traction in the meeting]
```

---

## Why Two Sections?

### Section 1 = Operational Need
- **Triggered by**: Explicit promises in transcript
- **Purpose**: Fulfill a specific commitment made during the meeting
- **Usage**: Immediate - send this blurb to the person who requested it

### Section 2 = Strategic Asset
- **Always generated**: For founder/investor/partnership meetings
- **Purpose**: Build reusable messaging library based on what works
- **Usage**: Long-term - deploy these narratives across various contexts

---

## Updated Registry Guidance (v1.4)

```json
"B14": {
  "name": "BLURBS_REQUESTED",
  "purpose": "Ready-to-use blurbs for when someone else introduces Vrijen/Careerspan, PLUS strategic messaging/talking points",
  "guidance": [
    "STRUCTURE: This block has TWO sections - (1) Actual Blurbs Requested (if any), (2) Key Messaging & Talking Points (always generate)",
    
    "SECTION 1: ACTUAL BLURBS REQUESTED",
    "- Detection: Listen for 'send me a blurb', 'I'll introduce you', 'I'll put you in touch', 'forward me something'",
    "- Extract: Who's making intro, Who they'll forward to, Goal of introduction",
    "- Generate: 1-2 paragraph forwarding-ready blurb tailored to recipient, goal, and what resonated",
    "- If nothing detected: 'No blurbs explicitly requested in this meeting'",
    
    "SECTION 2: KEY MESSAGING & TALKING POINTS",
    "- ALWAYS generate 5-10 strategic messaging blurbs after founder/investor/partnership meetings",
    "- Types: Value prop, Technical credibility, Mission alignment, Specific fit, Differentiation, Stats",
    "- Tailor to what RESONATED in this meeting",
    "- Include 'What Resonated' analysis: interpret positioning and stakeholder priorities",
    
    "IMPORTANT: Even if section 1 has no blurbs, ALWAYS generate section 2 for strategic meetings"
  ]
}
```

---

## Command File Update (v5.0.0)

Added explicit B14 guidance:

```markdown
##### B14 - BLURBS_REQUESTED
- **TWO distinct sections**: (1) Actual Blurbs Requested, (2) Key Messaging & Talking Points
- **Section 1**: Detection → extract context → generate forwarding-ready blurb
- **Section 2**: Always generate 5-10 strategic blurbs + "What Resonated" analysis
- This section is proactive value generation - create even if no actual blurb requested
```

---

## Example: Hamoon Meeting

### Section 1: Actual Blurbs Requested
```markdown
No blurbs explicitly requested in this meeting.
```
(Hamoon didn't ask for an intro, so this section is empty)

### Section 2: Key Messaging & Talking Points
```markdown
### 1. Careerspan Value Prop (30-second version)
**Context**: For follow-up email opening  
**Copy**:
> Careerspan helps job seekers build rich, qualitative profiles through conversational AI—capturing 100+ data points (values, soft skills, work style) that resumes miss. For platforms like FutureFit, we offer embeddable assessment tools or data enrichment APIs to upgrade profile depth without building proprietary extraction layers.

[... 9 more contextual blurbs ...]

---

## What Resonated - Analysis

Hamoon responded most strongly to:
1. **Embedded integration model** - FutureFit's pain around UX fragmentation means they strongly prefer point solutions over full platform redirects
2. **Data layer vision** - The "Internet of careers" concept aligned with their scale (200K users) and need for high-signal profiling
3. **Mission alignment** - Hamoon's closing remarks about "hard problems" and impact-driven work suggest he values founders who care deeply about the space

This tells us Careerspan should emphasize **embedded solutions and data infrastructure** over standalone product when talking to platform partners at scale.
```

---

## Key Differences from v1.3

| Aspect | v1.3 (Rejected) | v1.4 (Refined) |
|--------|----------------|----------------|
| **Section 1** | Said "no blurbs" and stopped | Detects requests, generates contextual blurbs, notes if none |
| **Section 2** | Didn't exist | Always generates strategic messaging |
| **Analysis** | None | "What Resonated" interpretation |
| **Philosophy** | Follow rules rigidly | Use intelligence to fulfill intent |

---

## Next Steps

1. ✅ **Registry updated** with two-section B14 guidance
2. ✅ **Command file updated** with explicit B14 instructions
3. ⏳ **Test with real transcript** that has an actual blurb request
4. ⏳ **Validate** section 1 detection + generation works correctly

---

## Detection Phrases to Listen For

**Intro promises** (triggers Section 1):
- "Send me a blurb"
- "I'll introduce you"
- "I'll put you in touch"
- "I'll connect you with"
- "Forward me something about what you do"
- "Let me introduce you to [person]"
- "I'll forward your info to [person]"

**Context clues**:
- Who will receive the forwarded blurb
- What they're trying to achieve with the intro
- Why this connection makes sense (discussed in meeting)

---

**The blurb system now handles both operational needs (fulfill promises) and strategic needs (build messaging library).**
