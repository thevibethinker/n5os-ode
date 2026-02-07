---
created: 2026-02-01
version: 2.0
provenance: con_7fR5qWFds2TAonyD
---

# Entity Extraction Prompt

Extract entities and relationships from text about V (Vrijen Attawar), founder of Careerspan.

## Entity Types

**PERSON** — Subtypes: Inner Circle, Team, Advisor, Mentor, Champion, Friend, Network, Acquaintance, Lead
**CONCEPT** — Subtypes: Principle, Framework, Mental Model, Thesis, Hypothesis  
**OBJECTIVE** — V's goals (no subtypes)
**ORGANIZATION** — Subtypes: Startup, Company, Community, Institution, Fund
**TOOL** — Subtypes: Software, Technique, Process, Template
**EVENT** — Subtypes: Career Milestone, Meeting, Speaking, Publication, Personal

## Relationship Types (Extract These)

**Tier 1 (Priority):**
- KNOWS, WORKS_WITH, CHAMPIONS, INTRODUCED_BY
- SHARES_BELIEF, SUPPORTS, BELIEVES

**Tier 2:**
- ADVISES, MENTORS, WORKS_AT, LEAD_FOR
- STAKEHOLDER_IN, PROMISED_INTRO, CAN_INTRO_TO

**Tier 3:**
- FRIENDS_WITH, MET_THROUGH, TAUGHT, FOUNDED
- INVESTED_IN, MEMBER_OF, COMPETES_WITH

## Output Format

```json
{
  "entities": [
    {
      "name": "exact name as mentioned",
      "type": "PERSON|CONCEPT|OBJECTIVE|ORGANIZATION|TOOL|EVENT",
      "subtype": "subtype from list above",
      "context": "1-sentence context from text"
    }
  ],
  "relationships": [
    {
      "from": "entity name",
      "to": "entity name", 
      "type": "RELATIONSHIP_TYPE",
      "context": "how this relationship is evident"
    }
  ]
}
```

## Guidelines

1. **Be specific** — Use exact names as written
2. **Infer V** — If text is from V's perspective, V is implicit subject
3. **Subtype carefully:**
   - Champion = actively advocates, not just supportive
   - Mental Model = integrated worldview, not just a framework
   - Hypothesis = being tested, Thesis = held belief
4. **Temporal relationships** — Note if relationship is past tense (worked_with vs works_with)
5. **Skip generic** — Don't extract common nouns unless specifically named

## Text to Extract From:

{text}
