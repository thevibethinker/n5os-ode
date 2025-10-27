# Product Analysis Style Guide

**Block ID:** B72  
**Domain:** internal  
**Voice Profile:** `file 'N5/prefs/communication/voice.md'`  
**Auto-Approve Threshold:** 10 blocks

---

## Purpose

Deep dive on product decisions, feature prioritization, user experience analysis, and roadmap thinking. Internal product strategy work that informs what to build, how to build it, and for whom. Focus on decision-making, not just description.

---

## Structure

**Typical flow:**
- Context: What product question or decision triggered this
- User need: Who needs what and why
- Options: What we could build (2-3 alternatives)
- Trade-offs: Pros/cons, complexity vs value, scope considerations
- Decision: Recommendation with reasoning
- Open questions: What we still need to learn

---

## Tone & Voice

**Core Characteristics:**
- **User-centered:** Start with user need, not feature idea
- **Decisive:** Make recommendations, don't just list options
- **Realistic:** Acknowledge constraints (time, complexity, resources)
- **Specific:** Concrete features, workflows, interactions
- **Iterative:** Comfortable with "MVP is X, full version is Y"

**Avoid:**
- Feature lists without user benefit
- "Wouldn't it be cool if..." without strategic grounding
- Perfect-world thinking that ignores constraints
- Building for ourselves (unless we're the user)
- Boiling the ocean (trying to solve everything at once)

---

## Lexicon

**Preferred:**
- User segments (job seekers, career changers, mid-career professionals)
- User jobs-to-be-done ("understand my trajectory," "prepare for interviews")
- Scope terms: MVP, V1, V2, future
- Feature complexity: low/medium/high effort
- User benefit: saves time, reduces anxiety, increases clarity

**Domain-Specific:**
- Product: feature, workflow, interaction, affordance
- Development: sprint, iteration, refactor, technical debt
- UX: friction, flow, cognitive load, mental model

---

## Templates

### Template 1: Feature Decision
```
Context: [User feedback, gap observed, roadmap question]

User need: [Who] needs to [what] so they can [outcome]

Options considered:
1. [Approach 1]: [Brief description]
   - Pros: [Benefits]
   - Cons: [Limitations, complexity]
2. [Approach 2]: [Description]
   - Pros: [Benefits]
   - Cons: [Limitations]

Recommendation: [Which approach + why]

MVP scope: [What ships first]

Future iteration: [What comes later]

Open questions: [What to validate]
```

### Template 2: Roadmap Prioritization
```
Features under consideration:
- [Feature A]: [User value] | [Effort] | [Strategic importance]
- [Feature B]: [User value] | [Effort] | [Strategic importance]
- [Feature C]: [User value] | [Effort] | [Strategic importance]

Prioritization framework:
- [Criteria 1: e.g., must-have for core use case]
- [Criteria 2: e.g., competitive differentiation]
- [Criteria 3: e.g., feasibility given resources]

Recommendation:
1. [Feature X]: Do now because [reason]
2. [Feature Y]: Next because [reason]
3. [Feature Z]: Defer until [condition]

Trade-offs accepted: [What we're explicitly not doing]
```

---

## Transformation Guidance

**Raw → Refined:**
- "Users want X" → "Users are trying to [job-to-be-done]. They currently [workaround]. Feature X addresses this by..."
- Feature idea → User need + options + recommendation
- "This would be cool" → "This solves [specific user problem], value is [concrete benefit]"
- Perfect solution → MVP + future iterations

**Key Transforms:**
1. **Add user context:** "Build X feature" → "Users struggle with Y. Feature X would let them..."
2. **Scope explicitly:** "Build comprehensive X" → "MVP: Basic X (1 week). V2: Enhanced X with Y (1 month)"
3. **Show trade-offs:** "Add all these features" → "Doing A means delaying B. Worth it because..."

---

## Examples

### Example 1: Timeline Feature Scoping

**Raw Input:**
```
Users need to see their career progression. Thinking we should build a 
timeline that shows all their roles, with dates, descriptions, maybe 
achievements. Could add filters, tags, maybe AI suggestions for how to 
tell the story better. Also connections between roles to show narrative 
arc. Lots of possibilities here.
```

**Refined Output:**
```
Context: Users trying to understand career trajectory. Current product is 
text-based narrative builder. Gap: No visual representation of progression.

User need: Mid-career professionals need to **see** their career path over 
time so they can identify patterns, transitions, and gaps in their story.

Options considered:

1. **Rich interactive timeline** (high effort)
   - Pros: Beautiful, lots of detail, interactive exploration
   - Cons: 3-4 weeks to build, complex UX, might overwhelm users
   
2. **Simple chronological list with key milestones** (medium effort)
   - Pros: 1 week to build, clear and scannable, easy to maintain
   - Cons: Less visually compelling, limited interaction
   
3. **AI-generated summary with suggested narrative arc** (low effort, different approach)
   - Pros: Unique angle, leverages AI strength, minimal UI
   - Cons: Doesn't give visual sense of timeline

Recommendation: Start with option 2 (simple timeline)

Why: Gets core value (visual progression) without UI complexity. Users can 
see their path in one view. Validates whether timeline metaphor resonates 
before investing in rich interactions.

MVP scope (1 sprint):
- Chronological list of roles with dates
- Company name + title for each
- Expand/collapse for details
- Scroll to navigate

Future V2 (after validation):
- Add achievements/highlights per role
- Visual connections showing transitions
- AI suggestions for narrative framing
- Export as formatted document

Open questions:
- Do users want decade view or detailed year-by-year?
- Should timeline be primary navigation or secondary tool?
- Test with 5 users: Does seeing timeline change how they think about narrative?

Trade-off accepted: Not building "beautiful" version first. Optimizing 
for learning over polish.
```

---

## QA Checklist

Before finalizing:
- [ ] Starts with user need (not feature idea)
- [ ] Considers 2-3 options with trade-offs
- [ ] Makes clear recommendation with reasoning
- [ ] Scopes MVP vs future iterations
- [ ] Realistic about effort and constraints
- [ ] Identifies what needs validation
- [ ] Specific enough to hand to developer/designer
- [ ] Strategic (connects to user value and company goals)

---

**Version:** 1.0  
**Created:** 2025-10-26
