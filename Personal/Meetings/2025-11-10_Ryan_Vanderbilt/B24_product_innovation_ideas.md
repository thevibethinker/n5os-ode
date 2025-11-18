---
created: 2025-11-12
last_edited: 2025-11-12
version: 1.0
---

# B24 - Product Innovation Ideas

## Ideas Explicitly Mentioned

### Idea 1: Mood-Based Prompt Adaptation

**Source**: Ryan's observation that achievement prompts work "depending on my mood"

**The Problem**: 
Users arrive at Careerspan in vastly different emotional states - excited about new opportunity, exhausted from job search, anxious about self-promotion, reflective and curious, or defensive and skeptical. Current prompt assumes single emotional starting point.

**Potential Solutions**:

**Option A: Explicit Mood Check**
- Opening question: "How are you feeling about reflecting on your career today?"
- Routes to different conversation styles based on answer:
  - Energized/Confident → Achievement-first, ambitious framing
  - Uncertain/Anxious → Start with easier questions (what environments do you thrive in?)
  - Exhausted/Overwhelmed → Minimal friction, accept short answers, build slowly
  - Reflective/Curious → Deeper philosophical questions about values and meaning

**Option B: Shuffle/Guide Options**
- Instead of single first prompt, offer 3-4 entry points:
  - "Tell me about a time you were proud of your work"
  - "What kind of work environment brings out your best?"
  - "Walk me through a recent project"
  - "What are colleagues likely to remember about working with you?"
- User chooses based on what feels accessible in the moment

**Option C: Colleague Feedback Primer**
- Before asking user to talk about achievements, prompt them to get external validation:
- "Before we start, reach out to 2-3 people you've worked with and ask: 'What are 3 moments where I impressed you or knocked it out of the park?' Come back with their responses."
- This gives users permission to talk about achievements because someone else named them first

**Implementation Complexity**: Medium (Option A), Low (Option B), Medium-High (Option C requires async flow)

**Strategic Value**: High - addresses core conversion friction identified by experienced UX practitioner

---

### Idea 2: Lifestyle-Based Career Discovery ("Blend" Concept)

**Source**: Ryan's previous project that used "embedded prompts" about lifestyle preferences

**The Problem**:
Direct questions about skills and achievements trigger performance anxiety. People know themselves better through their preferences and behaviors than through self-assessment.

**Potential Approach**:
- Capture career preferences indirectly through lifestyle observations:
  - "Where do you like to work?" → "I like isolation but being surrounded by people" → Suggests remote work with coworking space
  - "What time of day are you most creative?" → Reveals energy patterns
  - "What kind of conversations energize vs. drain you?" → Reveals social preferences
- Build career profile from accumulated preferences rather than direct skill claims

**Careerspan Integration**:
- Could be a supplementary profile-building mode alongside achievement storytelling
- Or an alternative entry point for users who hit achievement-prompt friction
- Data enriches how we help users articulate what environments they thrive in

**Implementation Complexity**: High (requires new conversation design and inference logic)

**Strategic Value**: Medium - interesting differentiation but may distract from core job search outcome

---

## Ideas Implicit in Conversation

### Idea 3: Temporal Career Data Journaling

**Source**: V's "wrong time" problem + Ryan's observation about forgetting achievements

**The Problem**:
People build career data in crisis mode when they've already forgotten the details. By the time they need to represent themselves, the richest context is lost.

**Potential Solution**: 
- Lightweight continuous journaling prompts (weekly/monthly check-ins)
- "What did you work on this week that felt meaningful?"
- "What feedback did you get that surprised you?"
- "What problem did you solve that you're proud of?"
- Accumulates data when memory is fresh, available instantly when needed

**Activation Hooks**:
- Calendar reminder integration (Howie)
- Slack bot for weekly prompts
- Email digest with single reflection question
- Post-meeting capture (after important conversations)

**Implementation Complexity**: Medium (requires engagement/retention strategy)

**Strategic Value**: Very High - transforms from transactional tool to infrastructure, increases data quality

---

### Idea 4: The "Humble Expert" Persona Mode

**Source**: Ryan's articulation of epistemic humility as distinct from shyness

**The Problem**:
Current coaching/prompting assumes confidence deficiency. But humble experts don't lack confidence - they have high standards for certainty and resist making strong claims without sufficient evidence.

**Potential Solution**:
- Create persona-specific conversation mode that respects intellectual humility
- Frame prompts as "What would colleagues say?" instead of "What are you great at?"
- Use hedging language: "Based on this project, it seems like you might be strong at X - does that sound right?"
- Provide evidence thresholds: "How many times have you done this before you'd feel comfortable claiming expertise?"
- Celebrate nuance and caveats rather than treating them as obstacles

**Implementation Complexity**: Medium (requires prompt engineering and persona detection)

**Strategic Value**: High - serves underserved, high-value user segment (senior ICs, academics, technical experts)

---

### Idea 5: Progressive Disclosure of Achievement Prompts

**Source**: Ryan's comfort after doing first story vs. friction on second attempt

**The Problem**:
First achievement prompt is high-stakes, makes users feel evaluated. Once they've done one successfully, subsequent ones feel easier.

**Potential Solution**:
- Radically reduce pressure on first interaction
- Start with something easy and non-threatening: "Tell me about a project you worked on recently"
- Don't label it as "achievement" or "success" initially
- After they tell the story, AI reflects back: "That sounds like it required [skill X]. Want to tell me about another time you used that skill?"
- Gradually introduce achievement framing once user has evidence they can do this

**Implementation Complexity**: Low (conversation design, no new tech)

**Strategic Value**: High - addresses acute conversion friction with minimal engineering

---

## Feature Ideas from Comparison Points

### From Google Career Dreamer

**What Ryan Liked**: "Reflection back to you" - seeing yourself through AI's eyes

**Careerspan Implication**:
- Could we create a "career mirror" mode that just shows user their own story reshaped?
- Not for job applications, just for self-understanding
- "Here's how I would describe you based on our conversations"
- Makes the reflection experience more explicit and valuable even when not job searching

---

## Prioritization Recommendation

**Ship First** (Next 3 Months):
1. **Mood-based prompt adaptation** (Option B: Shuffle/Guide) - Low complexity, high impact
2. **Progressive disclosure of achievement prompts** - Immediate conversion improvement

**Build Medium-Term** (3-6 Months):
1. **Temporal career data journaling** - Core infrastructure for lifelong tool vision
2. **Humble Expert persona mode** - Serves high-value segment with clear differentiation

**Explore Long-Term** (6-12 Months):
1. **Lifestyle-based career discovery** - Requires significant investment, unclear ROI
2. **Career mirror mode** - Nice-to-have, not critical path

---

## Open Questions for Product Team

1. Do we have data on user drop-off at first prompt? Does it validate Ryan's mood-friction hypothesis?
2. What percentage of users are likely "humble experts" vs. other self-advocacy barriers?
3. Could we A/B test prompt variations (achievement vs. project vs. colleague-validated) with small sample?
4. Is temporal journaling technically feasible with current architecture?
5. What's the smallest version of mood adaptation we could ship this quarter?

