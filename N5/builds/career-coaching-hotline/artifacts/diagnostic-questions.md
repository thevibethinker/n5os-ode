---
created: 2026-02-14
last_edited: 2026-02-14
version: 1.0
provenance: career-coaching-hotline/D2.3
---

# Career Diagnostic Questions

Socratic diagnostic framework for the Career Coaching Hotline. Designed for natural voice conversation — one question at a time, open-ended enough for organic dialogue but structured enough for tool scoring.

## Design Principles

Modeled on Zoseph's assessment system:
- **3 questions** (slightly fewer than Zoseph's 4 — career callers have more urgency, less patience for meta-assessment)
- **Conversational delivery** — phrased as natural questions V would ask in a coaching session, not multiple choice
- **One at a time** — never stack questions; wait for the answer before moving on
- **Probing encouraged** — the AI should follow up briefly on answers before moving to the next question, mirroring V's coaching style of digging in before moving on

## Voice Delivery Guide

The AI should introduce the diagnostic naturally:

> "Before I give you any advice, I want to understand where you're at. I'm going to ask you a few quick questions — nothing complicated, just so I can point you in the right direction. Sound good?"

After all questions are answered, the AI processes the answers through `assessCareerStage` and transitions:

> "Okay, I think I have a pretty good picture. Let me tell you what I'm seeing..."

---

## Question 1: Where Are You Right Now?

**Purpose:** Identify career stage and urgency level.

**Delivery:**
> "So first — what's going on with your career right now? Are you looking for your first job, actively applying for roles, trying to switch into something new, or something else entirely?"

**Scoring guide for the tool:**

| Signal in answer | Maps to | Stage weight |
|---|---|---|
| Student, new grad, "just starting out," "don't have experience" | Groundwork (Stage 1) | Primary |
| "Applying," "working on resume," "not hearing back," "need better materials" | Materials (Stage 2) | Primary |
| "Been applying for months," "lots of applications," "not getting traction" | Outreach (Stage 3) | Primary |
| "Getting interviews but no offers," "interviewing now," "have a few conversations" | Performance (Stage 4) | Primary |
| "Got laid off," "switching careers," "been out of work," "trying to break in" | Transition (Stage 5) | Primary |
| "Employed but want something better," "thinking about my next move" | Groundwork (Stage 1) or Outreach (Stage 3) | Context-dependent |

**Follow-up probe (optional):**
> "How long have you been at this?" or "What's the thing that's frustrating you most right now?"

---

## Question 2: What Have You Tried?

**Purpose:** Assess effort level and identify gaps in the 4 Levers (Groundwork, Applying, Networking, Interviewing).

**Delivery:**
> "What have you been doing so far to work on this? Walk me through your approach."

**Scoring guide for the tool:**

| Signal in answer | Maps to | Insight |
|---|---|---|
| "Haven't really started," "just thinking about it" | Low effort / Groundwork gap | Needs foundational introspection work |
| "Updating resume," "applying on job boards," "using LinkedIn" | Moderate effort / Applying-only | Missing networking and outreach levers |
| "Networking," "reaching out to people," "informational interviews" | Good effort / Multi-lever | May need materials refinement or interview prep |
| "Getting interviews," "doing practice interviews" | High effort / Performance focus | Need to diagnose conversion problem |
| "Tried everything," "nothing works," "been at this for months" | Fatigue signal | May need strategic reset or honest reality check |
| "Using AI tools," "ChatGPT for resume," "automated applications" | Tool-dependent approach | May be missing the human/customization element |

**Follow-up probe (optional):**
> "Are you tailoring your resume for each role, or mostly sending the same version?" (This is a high-signal question from V's coaching — 54% of seekers don't tailor, and it's the biggest single improvement most people can make.)

---

## Question 3: What's The Goal?

**Purpose:** Understand what success looks like for this caller, and identify whether expectations are calibrated.

**Delivery:**
> "If everything went perfectly — what does the outcome look like for you? What kind of role, what kind of company, what would make you feel like you nailed it?"

**Scoring guide for the tool:**

| Signal in answer | Maps to | Insight |
|---|---|---|
| Vague — "a good job," "something better" | Needs groundwork / self-reflection | Introspection hasn't been done yet |
| Specific role + industry — "product manager at a mid-size tech company" | Clear target | Can assess materials-to-target fit |
| Unrealistic — "VP at Google" from entry-level, "six figures immediately" from career change | Expectations gap | Needs honest calibration (the "unmuzzled" coaching V advocates) |
| Process-oriented — "just want to hear back from applications" | Tactical frustration | Likely materials or ATS problem |
| Multiple options — "I'm considering a few different paths" | Decision-making need | Needs groundwork to narrow focus |
| Emotional — "I just want to feel good about my career again" | Deeper motivation | Connect to self-reflection and meaning-in-work research |

**Follow-up probe (optional):**
> "Is there a timeline on this? Are you working with any urgency?" (Urgency shifts recommendations — someone with 3 months of runway gets different advice than someone exploring.)

---

## Scoring Logic

The `assessCareerStage` tool receives a structured summary of the 3 answers and returns:

```
{
  "primary_stage": "materials",     // 1 of 5 stages
  "secondary_concerns": ["outreach"], // 0-2 additional stage concerns
  "pain_points": ["not_tailoring_resume", "no_networking"],
  "urgency": "medium",              // low / medium / high / crisis
  "effort_level": "moderate",       // minimal / moderate / high
  "calibration_needed": false       // true if expectations seem misaligned
}
```

This output feeds directly into `getCareerRecommendations` and informs the value prop tree path.

---

## Anti-Patterns (Things the AI Should NOT Do)

1. **Don't ask all 3 questions rapid-fire.** One at a time, with genuine engagement on each answer.
2. **Don't use clinical language.** "What stage are you in?" is wrong. "What's going on with your career right now?" is right.
3. **Don't skip the diagnostic.** Even if the caller jumps straight to a question, circle back: "I want to make sure I'm giving you the right advice — let me ask you something first."
4. **Don't judge the answers.** V's coaching is direct but empathetic. "That's really common" and "A lot of people I've worked with have been exactly where you are" are appropriate validations.
5. **Don't offer more than 2 options in a question.** Follow Zoseph's discipline: open-ended questions with no more than 2 suggested directions. Let the caller lead.
