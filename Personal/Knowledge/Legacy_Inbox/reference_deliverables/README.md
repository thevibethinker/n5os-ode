# Reference Deliverables

**Purpose:** Approved examples of proposals, pitch decks, one-pagers, and other deliverables that have successfully closed deals or advanced relationships.

**Usage:** When generating new deliverables, the system references similar approved examples to improve quality and consistency.

---

## Structure

### Organization by Type

```
Knowledge/reference_deliverables/
├── partnership_proposals/       ← Community, channel, strategic partnerships
├── sales_proposals/            ← Customer-facing proposals (founders, recruiting leads)
├── pitch_decks/                ← Investor presentations
├── one_pagers/                 ← Product sheets, case studies, overviews
├── integration_guides/         ← Technical documentation for partners/customers
├── messaging_templates/        ← Email templates, community communications
└── _index.md                   ← Master searchable index
```

### Files are Stored in Two Places

**1. Original Location:**
```
Careerspan/Meetings/2025-10-09_0445_community-partnerships_theresa/
└── OUTPUTS/deliverable_partnership_proposal.md
```

**2. Reference Copy (when approved):**
```
Knowledge/reference_deliverables/partnership_proposals/
└── community_partnerships_remotelygood_2025-09-29.md
```

The reference copy is either:
- A duplicate file (for stability - original may be edited)
- A symlink (to save space - but reference stays tied to original)

---

## File Naming Convention

**Format:** `{type}_{organization}_{date}.md`

**Examples:**
- `community_partnerships_remotelygood_2025-09-29.md`
- `sales_proposal_acme_corp_2025-08-15.md`
- `pitch_deck_series_a_2025-10-01.md`
- `integration_guide_slack_2025-07-20.md`

**Why this format:**
- Type first = easy to scan by category
- Organization = quickly identify which deal
- Date = version control, see evolution over time

---

## Frontmatter Schema

**Every reference deliverable must include:**

```yaml
---
# Classification
deliverable_type: partnership_proposal | sales_proposal | pitch_deck | one_pager | integration_guide | messaging_template
stakeholder_type: community_manager | customer_founder | customer_recruiting_lead | vc | investor | channel_partner
business_relationship: community_partnerships | sales | fundraising | channel | strategic_partnership
deal_stage: pilot_kickoff | demo | proposal | negotiation | closed | ongoing

# Context
organization: "Remotely Good"
stakeholder_name: "Theresa Anoje"
meeting_date: 2025-09-29
meeting_id: "46a9c7"
industry_context: ["social_impact", "nonprofit", "tech_for_good"]
geography: "San Francisco, CA"

# Success Data
status: approved | in_use | closed_deal | did_not_close
approved_date: 2025-10-05
approved_by: vrijen | logan | team
outcome: "Partnership pilot launched, code activated"

# Learning
what_worked:
  - "Mission alignment emphasized heavily throughout"
  - "Light on pricing details - trust-first approach"
  - "Flexibility on premium vs. all-member access built trust"
  
what_didnt_work:
  - "N/A - first community partnership"

key_decisions:
  - "Revenue share: 20%"
  - "Pilot duration: 3 months"
  
similar_use_cases:
  - "Other micro-community partnerships"
  - "Mission-driven organization sales"

avoid_for:
  - "Enterprise sales (too informal)"
  - "Investor pitches (wrong format)"

# Metadata
version: 1.0
original_location: "Careerspan/Meetings/.../deliverable_partnership_proposal.md"
---
```

---

## Current State

**As of:** October 9, 2025

**Files in reference pool:** 0 (just set up)

**Next to add:**
1. Theresa partnership proposal (once finalized and approved)
2. Community messaging template (once used successfully)

**First priority:** Get 2-3 examples per major type to establish patterns