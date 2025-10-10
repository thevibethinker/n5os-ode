# Complete Meeting Intelligence Blocks

## Core Blocks (Always Generated in FULL mode)

### 1. **Follow-Up Email** (`follow-up-email.md`)
- Draft follow-up email with specific next steps
- Clear asks and commitments
- Relationship moves
- Timeline references

### 2. **Action Items** (`action-items.md`)
- 10-20 specific action items
- Owner assignments
- Deadlines (calculated from meeting date)
- Priority levels
- Context and dependencies

### 3. **Decisions** (`decisions.md`)
- 5-8 key decisions made
- Categories: Strategic, Process, Product
- Rationale documented
- Impact analysis
- Decision makers identified

### 4. **Key Insights** (`key-insights.md`)
- 10-15 strategic insights
- Categories: Hiring market, founder wellness, product strategy
- Implications and applications
- Speaker attribution

### 5. **Stakeholder Profile** (`stakeholder-profile.md`)
- Background and experience
- Communication style
- Pain points and interests
- Opportunities and network
- How to work with them effectively

### 6. **REVIEW_FIRST Dashboard** (`REVIEW_FIRST.md`)
- Executive summary
- Priority actions (next 48 hours)
- Key decisions made
- Top insights
- Quick links to all files

### 7. **Transcript** (`transcript.txt`)
- Full meeting transcript copy
- All timestamps preserved
- All speakers identified

---

## Conditional Intelligence Blocks (Generated Based on Content)

### 8. **Warm Intros** (`INTELLIGENCE/warm-intros.md`)
- Extracted warm introduction opportunities
- Contact names and context
- How the intro was mentioned
- Follow-up strategy

### 9. **Risks** (`INTELLIGENCE/risks.md`)
- Identified risks from discussion
- Risk categories and severity
- Mitigation strategies
- Timeline/urgency

### 10. **Opportunities** (`INTELLIGENCE/opportunities.md`)
- Business opportunities identified
- Market opportunities
- Partnership opportunities
- Revenue opportunities

### 11. **User Research** (`INTELLIGENCE/user-research.md`)
- User pain points extracted
- Use cases discovered
- Feature requests
- Product insights

### 12. **Competitive Intel** (`INTELLIGENCE/competitive-intel.md`)
- Competitor mentions
- Competitive positioning insights
- Market dynamics
- Differentiation opportunities

---

## Meeting-Type Specific Blocks

### 13. **Career Insights** (`INTELLIGENCE/career-insights.md`)
Generated for: `coaching`, `networking` meetings
- Career development themes
- Skills and growth areas
- Job search strategies
- Network building insights

### 14. **Deal Intelligence** (`INTELLIGENCE/deal-intelligence.md`)
Generated for: `sales` meetings
- Deal stage and health
- Buying signals
- Objections and concerns
- Next steps to close

### 15. **Investor Thesis** (`INTELLIGENCE/investor-thesis.md`)
Generated for: `fundraising` meetings
- Investor interest areas
- Thesis alignment
- Investment criteria
- Follow-up strategy

### 16. **Partnership Scope** (`INTELLIGENCE/partnership-scope.md`)
Generated for: `community_partnerships` meetings
- Partnership model
- Value exchange
- Success metrics
- Implementation plan

---

## Deliverables (DELIVERABLES/ folder)

### 17. **Blurb** (`DELIVERABLES/blurbs/blurb_YYYY-MM-DD.md`)
Generated when: Sales, networking, or community partnership meetings
- 2-3 paragraph company/product description
- Tailored to specific audience
- Persona-aligned tone
- Synergy angle highlighted

### 18. **One-Pager/Memo** (`DELIVERABLES/one_pagers/one_pager_YYYY-MM-DD.md`)
Generated when: Sales, partnerships, or fundraising meetings
- Executive summary format
- Problem, solution, value prop
- Key differentiators
- Call to action

### 19. **Proposal/Pricing** (`DELIVERABLES/proposals_pricing/proposal_pricing_YYYY-MM-DD.md`)
Generated when: Sales, fundraising, or partnership meetings mention pricing/terms
- Customized proposal
- Pricing structure
- Terms and conditions
- Next steps

---

## Metadata and Logs

### 20. **Meeting Metadata** (`_metadata.json`)
- Meeting ID (6-char)
- Date, time, timezone
- Meeting types and stakeholder types
- Transcript source (with SHA256 checksum)
- Processing details
- Intelligence counts (action items, decisions, insights)
- Approval status

---

## Total Blocks Generated

**In FULL mode:**
- **Minimum**: 7 core blocks (always)
- **Typical**: 12-15 blocks (with conditional intelligence)
- **Maximum**: 20+ blocks (with all conditional + deliverables)

---

## Block Generation Logic

### Mode: **FULL** (what automated system uses)
```
Core (7):
  ✅ Follow-up email
  ✅ Action items
  ✅ Decisions
  ✅ Key insights
  ✅ Stakeholder profile
  ✅ REVIEW_FIRST
  ✅ Transcript

Conditional Intelligence (5):
  🔍 Warm intros (if mentioned)
  🔍 Risks (if identified)
  🔍 Opportunities (if identified)
  🔍 User research (if discussed)
  🔍 Competitive intel (if mentioned)

Meeting-Type Specific (1-2):
  📋 Career insights (if coaching/networking)
  📋 Deal intelligence (if sales)
  📋 Investor thesis (if fundraising)
  📋 Partnership scope (if partnerships)

Deliverables (1-3):
  📄 Blurb (if sales/networking/partnerships)
  📄 One-pager (if sales/partnerships/fundraising)
  📄 Proposal/pricing (if pricing mentioned)

Metadata:
  ✅ _metadata.json
```

---

## What Was Missing Before

I previously documented only **7 blocks**, but the system actually generates:

❌ **Missing in my documentation:**
- Warm intros
- Risks
- Opportunities
- User research
- Competitive intel
- Career insights (for coaching meetings)
- Deal intelligence (for sales meetings)
- Investor thesis (for fundraising)
- Partnership scope (for partnerships)
- **Blurb** (deliverable)
- **One-pager** (deliverable)
- **Proposal/pricing** (deliverable)
- _metadata.json

✅ **Should have documented: 20+ blocks total**

---

## File Structure Example

```
Careerspan/Meetings/2025-10-09_1400_coaching_alex-caveny/
├── _metadata.json
├── REVIEW_FIRST.md
├── action-items.md
├── decisions.md
├── key-insights.md
├── stakeholder-profile.md
├── follow-up-email.md
├── transcript.txt
├── INTELLIGENCE/
│   ├── warm-intros.md
│   ├── risks.md
│   ├── opportunities.md
│   ├── user-research.md
│   ├── competitive-intel.md
│   └── career-insights.md
├── DELIVERABLES/
│   ├── blurbs/
│   │   └── blurb_2025-10-09.md
│   ├── one_pagers/
│   │   └── one_pager_2025-10-09.md
│   └── proposals_pricing/
│       └── proposal_pricing_2025-10-09.md
└── OUTPUTS/
    └── (system outputs/logs)
```

---

## Quality Standards Per Block

Each block should meet these standards:
- **Specific**: Real names, dates, numbers from transcript
- **Actionable**: Clear next steps and owners
- **Strategic**: Insights beyond surface-level summary
- **Comprehensive**: Full analysis, not placeholder text
- **Contextualized**: References to past meetings, relationships
- **Prioritized**: Most important items surfaced first
