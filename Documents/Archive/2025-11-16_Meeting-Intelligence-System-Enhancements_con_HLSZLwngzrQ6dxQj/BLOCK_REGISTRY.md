---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
---

# Meeting Intelligence Block Registry

Complete list of all meeting intelligence blocks in numerical order.

## Core Blocks (Always Generated)

### B01 - Detailed Recap
**Category:** Core  
**Description:** Comprehensive meeting overview covering context, participants, key discussion threads, technical details, and decisions  
**Typical Length:** 800-2000 words  
**Always Generated:** Yes

### B02 - Commitments & Action Items
**Category:** Core  
**Description:** Explicit commitments made by all parties with timeline and status tracking  
**Typical Length:** 200-500 words  
**Always Generated:** Yes

### B03 - Decisions Made
**Category:** Core  
**Description:** Key decisions reached during meeting with rationale and implications  
**Typical Length:** 200-600 words  
**Conditional:** Generate if decisions were made

---

## Contextual Blocks (Meeting Type Dependent)

### B03 - Stakeholder Intelligence & CRM Integration
**Category:** Contextual  
**Description:** People and organization intelligence for external stakeholders  
**Typical Length:** 300-800 words  
**Conditional:** Generate for external meetings  
**Note:** Canonical version (B08_STAKEHOLDER_INTELLIGENCE is legacy)

### B04 - Open Questions & Clarifications Needed
**Category:** Contextual  
**Description:** Questions raised during meeting requiring follow-up  
**Typical Length:** 200-400 words  
**Conditional:** Generate if questions were raised

### B04 - Risks & Flags
**Category:** Contextual  
**Description:** Risk assessment and warning flags identified  
**Typical Length:** 300-600 words  
**Conditional:** Generate if risks discussed

### B05 - Action Items & Next Steps
**Category:** Contextual  
**Description:** Actionable next steps organized by timeline  
**Typical Length:** 300-700 words  
**Conditional:** Generate if action items exist  
**Note:** Canonical version (B08_ACTION_ITEMS is legacy)

### B05 - Strategic Implications
**Category:** Contextual  
**Description:** Broader strategic insights and positioning analysis  
**Typical Length:** 400-900 words  
**Conditional:** Generate for strategic meetings

### B06 - Business Context & Implications
**Category:** Contextual  
**Description:** Business model, financial context, and commercial implications  
**Typical Length:** 300-700 words  
**Conditional:** Generate for business/partnership meetings

### B06 - Questions Raised
**Category:** Contextual  
**Description:** Questions and discussion points raised during meeting  
**Typical Length:** 200-500 words  
**Conditional:** Generate if substantive questions asked  
**Note:** Use B04_OPEN_QUESTIONS instead (canonical)

### B07 - Tone & Relationship Notes
**Category:** Contextual  
**Description:** Communication dynamics, relationship quality, and conversational tone  
**Typical Length:** 200-400 words  
**Conditional:** Generate for external relationships

### B07 - Risks & Opportunities
**Category:** Contextual  
**Description:** Strategic risks and opportunities identified  
**Typical Length:** 300-600 words  
**Conditional:** Generate if risks or opportunities surfaced

### B08 - Follow-up Conversations to Schedule
**Category:** Contextual  
**Description:** Future meetings and touchpoints to schedule  
**Typical Length:** 150-300 words  
**Conditional:** Generate if follow-ups discussed

### B09 - Reference Data
**Category:** Contextual  
**Description:** Key dates, metrics, contacts, and reference information  
**Typical Length:** 200-500 words  
**Conditional:** Generate if reference data present

### B10 - Context Connections
**Category:** Contextual  
**Description:** Cross-references to existing knowledge base and related context  
**Typical Length:** 200-400 words  
**Conditional:** Generate if strong knowledge connections exist

### B10 - Risk Register
**Category:** Contextual  
**Description:** Formal risk assessment with probability and mitigation  
**Typical Length:** 300-600 words  
**Conditional:** Generate for high-stakes meetings

---

## Optional/Special Blocks

### B21 - Key Quotes & Strategic Questions
**Category:** Optional  
**Description:** Memorable quotes and strategic questions that emerged  
**Typical Length:** 200-500 words  
**Conditional:** AI recommendation OR meeting has notable quotes

### B25 - Deliverables & Follow-Up Email Framework
**Category:** Optional  
**Description:** Content deliverables and draft follow-up email structure  
**Typical Length:** 300-700 words  
**Conditional:** Generate if deliverables discussed

### B26 - Meeting Metadata Summary
**Category:** Core  
**Description:** Classification, tags, and system metadata  
**Typical Length:** 100-200 words  
**Always Generated:** Yes

### B27 - Private Notes for Vrijen
**Category:** Optional  
**Description:** Personal notes and private reflections not for sharing  
**Typical Length:** 200-500 words  
**Conditional:** Manual generation only OR AI recommends sensitive notes  
**Security:** Private, exclude from sharing

---

## Block Number Conflicts

Some block numbers have multiple definitions based on context:

- **B03:** Decisions (core) OR Stakeholder Intel (contextual)
- **B04:** Open Questions OR Risks & Flags  
- **B05:** Action Items OR Strategic Implications
- **B06:** Business Context OR Questions Raised
- **B07:** Tone & Relationship Notes OR Risks & Opportunities
- **B08:** Follow-up Conversations (canonical) OR Action Items (legacy) OR Stakeholder Intelligence (legacy)
- **B10:** Context Connections OR Risk Register

The actual block selected depends on meeting type and content.

---

## Canonical vs. Legacy

**Use These (Canonical):**
- B05_ACTION_ITEMS (not B08_ACTION_ITEMS)
- B03_STAKEHOLDER_INTEL (not B08_STAKEHOLDER_INTELLIGENCE)
- B08_FOLLOW_UP_CONVERSATIONS (canonical for follow-ups)
- B03_DECISIONS (canonical for decisions)
- B04_OPEN_QUESTIONS (canonical for questions)
- B07_TONE_AND_CONTEXT (canonical for tone)
- B06_BUSINESS_CONTEXT (canonical for business implications)
- B05_STRATEGIC_IMPLICATIONS (canonical for strategic analysis)

---

## Meeting Type Rules

### Product Demo
- **Required:** B03_STAKEHOLDER_INTEL, B06_BUSINESS_CONTEXT
- **Recommended:** B05_ACTION_ITEMS, B08_FOLLOW_UP_CONVERSATIONS, B21_KEY_MOMENTS

### Partnership
- **Required:** B03_STAKEHOLDER_INTEL, B03_DECISIONS, B07_TONE_AND_CONTEXT
- **Recommended:** B05_STRATEGIC_IMPLICATIONS, B07_RISKS_OPPORTUNITIES, B08_FOLLOW_UP_CONVERSATIONS

### Financial Planning
- **Required:** B03_DECISIONS, B04_OPEN_QUESTIONS, B09_REFERENCE_DATA, B10_RISK_REGISTER
- **Recommended:** B05_ACTION_ITEMS, B06_BUSINESS_CONTEXT

### Internal Strategy
- **Required:** B03_DECISIONS, B05_ACTION_ITEMS
- **Recommended:** B05_STRATEGIC_IMPLICATIONS, B07_RISKS_OPPORTUNITIES, B10_CONTEXT_CONNECTIONS

### Customer Meeting
- **Required:** B03_STAKEHOLDER_INTEL, B02_COMMITMENTS
- **Recommended:** B07_TONE_AND_CONTEXT, B08_FOLLOW_UP_CONVERSATIONS, B25_DELIVERABLES

---

## System Limits

- **Max blocks per meeting:** 12
- **Always generated:** B01, B02, B26 (3 blocks)
- **Wildcard slots:** 2 (AI can recommend any other blocks)
- **Batch generation:** Up to 3 blocks per pipeline run

