---
created: 2026-01-12
provenance: linkedin_voice_extractor
status: pending_review
---

# LinkedIn Voice Primitives Review

**Generated:** 2026-01-12T03:32:32.612157  
**Total Primitives:** 20  
**Meta-Patterns:** 6

## Instructions

Review each primitive. Mark with:
- `[x]` — Approve for import to voice library
- `[ ]` — Reject (not distinctive enough, too generic, etc.)
- `[?]` — Needs refinement (edit the text in place)

---

## Meta-Patterns Detected

### META-001: The Em-Dash Pivot: V uses em-dashes (--) to qualify, reframe, or contrast a statement, often moving from a general claim to a specific, often counter-intuitive truth.
- **Type:** structural
- **Frequency:** 15x
- **Examples:** resumes are fundamentally terrible -- they're one-dimensional...,  authenticity is the only way out -- be that in the materials..., Using ChatGPT poorly is just as bad... - if not worse - than not using it at all.

### META-002: Economic/Technical Reframe: V applies technical or economic terminology (ROI, telemetry, arms race, marginal cost, clock speed) to human/career problems to add weight and analytical clarity.
- **Type:** rhetorical
- **Frequency:** 12x
- **Examples:** talent telemetry, marginal cost of fraud is approaching $0, professional ROI

### META-003: The 'Not X, but Y' Reframe: A binary structure used to shift the reader's perspective from a legacy/mechanical understanding to a human/strategic one.
- **Type:** rhetorical
- **Frequency:** 14x
- **Examples:** Not for off-loading decision-making but rather as a way to ensure consistency, Not just machines! Hiring is broken..., Not every founder optimizes for exits. Some optimize for impact.

### META-004: Parenthetical Snark/Asides: Using parentheses or em-dashes to inject a dry, humorous, or self-deprecating internal monologue.
- **Type:** stylistic
- **Frequency:** 8x
- **Examples:** (spoiler alert y'all: it's not), (read: screed), (yes—I said it)

### META-005: The Punchy Opening: Starting a post with a blunt, often provocative 2-4 word declarative followed by a colon or newline.
- **Type:** structural
- **Frequency:** 9x
- **Examples:** Real talk:, Look:, Plot twist:

### META-006: The Socratic Bridge: Using open-ended questions to invite the reader into a new paradigm before presenting the solution.
- **Type:** rhetorical
- **Frequency:** 7x
- **Examples:** What does it mean to be "happily employed"?, So what's the answer?, But what if that wasn't the case?

---

## Primitives to Review

### [ ] VP-009: qualities - not keywords

| Field | Value |
|-------|-------|
| **Type** | metaphor |
| **Extractable Form** | [qualities/attributes/mentality] - not keywords |
| **Distinctiveness** | 0.90 |
| **Utility** | 0.80 |
| **Score** | 0.72 |
| **Frequency** | 5x |
| **Domains** | hiring, product |
| **Contexts** | The central thesis of Careerspan: human traits over automated matching |

---

### [ ] VP-003: advocate for themselves

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | [better/effectively] advocate for [themselves/oneself] |
| **Distinctiveness** | 0.80 |
| **Utility** | 0.80 |
| **Score** | 0.64 |
| **Frequency** | 8x |
| **Domains** | career, philosophy |
| **Contexts** | Reframing job searching/networking as a skill of self-advocacy |

---

### [ ] VP-004: 3D vs 2D

| Field | Value |
|-------|-------|
| **Type** | metaphor |
| **Extractable Form** | 3D [individual/sense/talent graph] vs 2D [piece of paper/document/resume] |
| **Distinctiveness** | 0.90 |
| **Utility** | 0.70 |
| **Score** | 0.63 |
| **Frequency** | 6x |
| **Domains** | hiring, product |
| **Contexts** | Contrasting holistic human assessment with the 'flattened' nature of resumes |

---

### [ ] VP-013: world authority on yourself

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | the world authority on yourself |
| **Distinctiveness** | 1.00 |
| **Utility** | 0.60 |
| **Score** | 0.60 |
| **Frequency** | 2x |
| **Domains** | career, philosophy |
| **Contexts** | Empowerment mantra for candidates to own their narrative |

---

### [ ] VP-006: skill unto itself

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | [Job hunting/Self-advocacy] is a skill [unto itself/in itself] |
| **Distinctiveness** | 0.70 |
| **Utility** | 0.80 |
| **Score** | 0.56 |
| **Frequency** | 5x |
| **Domains** | career, philosophy |
| **Contexts** | Emphasizing that the process of finding work is a distinct craft to be mastered |

---

### [ ] VP-007: wrong time

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | [focus on careers/network] at the [exact] wrong time |
| **Distinctiveness** | 0.80 |
| **Utility** | 0.70 |
| **Score** | 0.56 |
| **Frequency** | 5x |
| **Domains** | career, strategy |
| **Contexts** | Critiquing reactive career management vs. proactive maintenance |

---

### [ ] VP-016: arms race

| Field | Value |
|-------|-------|
| **Type** | metaphor |
| **Extractable Form** | [applicant/hiring] arms race |
| **Distinctiveness** | 0.70 |
| **Utility** | 0.80 |
| **Score** | 0.56 |
| **Frequency** | 3x |
| **Domains** | hiring, market |
| **Contexts** | Describing the escalation of AI tools in job applications |

---

### [ ] VP-020: mutually assured destruction

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | mutually assured destruction [at the scale of/for both sides] |
| **Distinctiveness** | 0.80 |
| **Utility** | 0.70 |
| **Score** | 0.56 |
| **Frequency** | 2x |
| **Domains** | market, hiring |
| **Contexts** | Describing the broken equilibrium between candidates and employers |

---

### [ ] VP-008: warmed up and ready to go

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | [network/assets] warmed up and ready to go |
| **Distinctiveness** | 0.80 |
| **Utility** | 0.60 |
| **Score** | 0.48 |
| **Frequency** | 3x |
| **Domains** | career, networking |
| **Contexts** | Describing a state of constant professional readiness |

---

### [ ] VP-010: spray-and-pray

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | spray-and-pray [approach/tools] |
| **Distinctiveness** | 0.60 |
| **Utility** | 0.80 |
| **Score** | 0.48 |
| **Frequency** | 4x |
| **Domains** | hiring, career |
| **Contexts** | Dismissive term for high-volume, low-intent job application strategies |

---

### [ ] VP-019: Sisyphean

| Field | Value |
|-------|-------|
| **Type** | metaphor |
| **Extractable Form** | Sisyphean [advice/hell] |
| **Distinctiveness** | 0.80 |
| **Utility** | 0.60 |
| **Score** | 0.48 |
| **Frequency** | 3x |
| **Domains** | career, market |
| **Contexts** | Describing repetitive, futile tasks in the job search process |

---

### [ ] VP-002: that's why

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | That's [precisely/actually] why [Solution/Action] |
| **Distinctiveness** | 0.50 |
| **Utility** | 0.90 |
| **Score** | 0.45 |
| **Frequency** | 10x |
| **Domains** | career, product, sales |
| **Contexts** | Connecting a systemic pain point to a specific product solution or company mission |

---

### [ ] VP-011: career companion

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | world's first career companion |
| **Distinctiveness** | 0.90 |
| **Utility** | 0.50 |
| **Score** | 0.45 |
| **Frequency** | 3x |
| **Domains** | product, branding |
| **Contexts** | Primary category descriptor for Careerspan |

---

### [ ] VP-014: table stakes

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | [Hard skills/Credentials] are table stakes |
| **Distinctiveness** | 0.50 |
| **Utility** | 0.90 |
| **Score** | 0.45 |
| **Frequency** | 3x |
| **Domains** | hiring, strategy |
| **Contexts** | Relegating standard requirements to make room for unique differentiators |

---

### [ ] VP-005: bring to the table

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | [all of/what you] bring to the table |
| **Distinctiveness** | 0.40 |
| **Utility** | 0.90 |
| **Score** | 0.36 |
| **Frequency** | 6x |
| **Domains** | career, hiring |
| **Contexts** | Describing the total value or qualities a candidate offers |

---

### [ ] VP-012: moved the needle

| Field | Value |
|-------|-------|
| **Type** | metaphor |
| **Extractable Form** | move[s/d] the needle |
| **Distinctiveness** | 0.40 |
| **Utility** | 0.90 |
| **Score** | 0.36 |
| **Frequency** | 3x |
| **Domains** | career, strategy |
| **Contexts** | Describing impactful actions or specific achievements |

---

### [ ] VP-015: if they're the right

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | if they're the right [recruiter/one/person] |
| **Distinctiveness** | 0.40 |
| **Utility** | 0.80 |
| **Score** | 0.32 |
| **Frequency** | 3x |
| **Domains** | career, hiring |
| **Contexts** | Adding a quality gate to a broad recommendation |

---

### [ ] VP-001: couldn't agree more

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | [I/We] couldn't agree more |
| **Distinctiveness** | 0.30 |
| **Utility** | 1.00 |
| **Score** | 0.30 |
| **Frequency** | 11x |
| **Domains** | general, engagement |
| **Contexts** | Standard high-alignment opener in comment sections |

---

### [ ] VP-017: a lot of

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | a lot of [people/folks/career coaches/BS jobs] |
| **Distinctiveness** | 0.20 |
| **Utility** | 1.00 |
| **Score** | 0.20 |
| **Frequency** | 5x |
| **Domains** | general, observations |
| **Contexts** | Informal quantification of industry participants or problems |

---

### [ ] VP-018: one of the

| Field | Value |
|-------|-------|
| **Type** | signature_phrase |
| **Extractable Form** | one of the [non-technical folks/central questions/central/key] |
| **Distinctiveness** | 0.20 |
| **Utility** | 1.00 |
| **Score** | 0.20 |
| **Frequency** | 4x |
| **Domains** | general, identity |
| **Contexts** | Locating himself or an idea within a larger group |

---

