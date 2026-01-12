---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_UbZ5BSRD1yOMzrsF
---

# JD Decomposition Theory

**Purpose:** Define how Stage 2 parses a Job Description into structured requirements.

---

## The Anatomy of a JD

Every JD contains signal and noise. Our job is to extract the signal.

### Signal Layers (What We Extract)

| Layer | Description | Example |
|-------|-------------|---------|
| **Hard Requirements** | Non-negotiable skills, tools, certifications | "5+ years Python", "CPA required", "AWS certified" |
| **Soft Requirements** | Interpersonal and cognitive competencies | "Strong communicator", "Problem solver", "Team player" |
| **Experience Requirements** | Context, industry, or domain exposure | "Experience in fintech", "Managed teams of 10+" |
| **Outcome Expectations** | What they expect you to have *achieved* | "Delivered products from 0→1", "Grew revenue" |
| **Implied Qualities** | Traits inferred from language/context | Startup JD implies scrappiness; Enterprise implies process |

### Noise Layers (What We Ignore or Flag)

| Layer | Description | How to Handle |
|-------|-------------|---------------|
| **Boilerplate** | Legal disclaimers, EEO statements | Ignore completely |
| **Aspirational Fluff** | "World-class", "Rockstar", "Ninja" | Ignore — no signal |
| **Generic Culture Speak** | "Fast-paced", "Collaborative environment" | Note but don't weight |
| **Kitchen Sink Lists** | 20+ bullet points of nice-to-haves | Focus on first 5-7 |

---

## Extraction Rules

### Rule 1: Priority by Position
Requirements listed earlier are more important. The first 3-5 bullets under "Responsibilities" or "Requirements" typically contain 80% of the signal.

### Rule 2: Verb Analysis
- **Action verbs** (lead, build, design, manage) → Outcome expectations
- **Have verbs** (possess, have, bring) → Hard requirements
- **Be verbs** (is, are) → Soft requirements or culture fit

### Rule 3: Quantifier Detection
Anything with numbers is concrete and assessable:
- "5+ years" → Experience requirement (high confidence)
- "Managed teams of 10+" → Outcome expectation
- "Bachelor's degree" → Hard requirement (often waivable)

### Rule 4: Synonym Normalization
Map JD language to canonical competencies:

| JD Phrase | Canonical Competency |
|-----------|---------------------|
| "Cross-functional collaboration" | Stakeholder Management |
| "Drive results" | Execution / Accountability |
| "Strategic thinker" | Strategic Planning |
| "Strong communicator" | Communication |
| "Comfortable with ambiguity" | Adaptability |
| "Data-driven" | Analytical Thinking |
| "Customer obsessed" | Customer Focus |
| "Roll up sleeves" | Hands-on / Scrappiness |

### Rule 5: Implicit Extraction
Some requirements are never stated but always present:
- Leadership roles → Conflict resolution, delegation, feedback
- Customer-facing → Empathy, patience, de-escalation
- Startup → Resourcefulness, wearing multiple hats
- Enterprise → Process adherence, documentation, stakeholder alignment

---

## Output Schema

After decomposition, the JD becomes:

```typescript
interface DecomposedJD {
  hardRequirements: Requirement[];
  softRequirements: Requirement[];
  experienceRequirements: Requirement[];
  outcomeExpectations: Requirement[];
  impliedQualities: Requirement[];
  jdQuality: 'high' | 'medium' | 'low'; // How informative was the JD?
  notes: string; // Any observations about JD quality
}

interface Requirement {
  text: string;           // Original phrasing
  canonical: string;      // Normalized competency name
  priority: 'critical' | 'important' | 'nice-to-have';
  assessable: boolean;    // Can this be tested in an interview?
}
```

---

## JD Quality Assessment

Not all JDs are equal. Assess and note:

| Quality | Indicators | Implications |
|---------|------------|--------------|
| **High** | Specific outcomes, clear priorities, reasonable length | Analysis will be precise |
| **Medium** | Mix of specific and generic, some prioritization | Analysis will be useful but has gaps |
| **Low** | All generic, kitchen-sink list, no prioritization | Flag to user: "This JD is vague — our analysis is limited by its quality" |

---

## Example Decomposition

**Input JD Snippet:**
> We're looking for a Senior Product Manager to lead our B2B platform. You'll work cross-functionally with engineering, design, and sales to deliver features that drive ARR growth. Requirements: 5+ years PM experience, experience with enterprise SaaS, strong SQL skills, excellent communication.

**Output:**
```json
{
  "hardRequirements": [
    {"text": "5+ years PM experience", "canonical": "Experience", "priority": "critical"},
    {"text": "strong SQL skills", "canonical": "Technical Skills", "priority": "important"}
  ],
  "softRequirements": [
    {"text": "excellent communication", "canonical": "Communication", "priority": "critical"}
  ],
  "experienceRequirements": [
    {"text": "experience with enterprise SaaS", "canonical": "Domain Experience", "priority": "important"}
  ],
  "outcomeExpectations": [
    {"text": "deliver features that drive ARR growth", "canonical": "Revenue Impact", "priority": "critical"}
  ],
  "impliedQualities": [
    {"text": "lead our B2B platform", "canonical": "Leadership", "priority": "critical"},
    {"text": "work cross-functionally", "canonical": "Stakeholder Management", "priority": "important"}
  ],
  "jdQuality": "high",
  "notes": "Clear role, specific requirements, outcome-oriented."
}
```

