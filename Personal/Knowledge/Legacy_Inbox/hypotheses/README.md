# Careerspan Hypotheses

**Purpose:** Track core business assumptions and validate/invalidate them through evidence from meetings, data, and market feedback.

**Philosophy:** As founders, we make assumptions constantly. This system makes them explicit, trackable, and falsifiable.

---

## How Hypotheses Work

### Lifecycle
```
Proposed → Testing → Supporting Evidence → Validated → Proven
                  ↓
              Invalidated → Pivot Required
```

**Proposed:** New hypothesis, no evidence yet  
**Testing:** Actively gathering evidence (experiments running)  
**Supporting Evidence:** Some validation, but need more data points  
**Validated:** Strong evidence from multiple sources  
**Proven:** Overwhelming evidence, becomes operating assumption  
**Invalidated:** Evidence contradicts, need to pivot

### Structure
Each hypothesis includes:
- **ID:** Unique identifier (H-XXX)
- **Category:** Product | GTM | Business Model | Market | Fundraising
- **Stakeholder(s):** Who this relates to
- **Statement:** Clear, falsifiable claim
- **Why it matters:** Strategic implications
- **How to test:** What evidence would validate/invalidate
- **Status:** Current lifecycle stage
- **Evidence:** Data points with sources and dates
- **Last updated:** When hypothesis was last reviewed

---

## Taxonomy

### By Category

**Product Hypotheses** (`product_hypotheses.md`)
- Features, capabilities, UX
- Value propositions
- Product-market fit assumptions

**Go-to-Market Hypotheses** (`gtm_hypotheses.md`)
- Distribution channels
- Positioning and messaging
- Sales motion and cycles
- Customer acquisition

**Business Model Hypotheses** (`business_model_hypotheses.md`)
- Pricing and packaging
- Revenue models
- Unit economics
- Monetization strategies

**Market Hypotheses** (`market_hypotheses.md`)
- TAM/SAM/SOM sizing
- Market trends and dynamics
- Competitive positioning
- Buyer behavior

**Fundraising Hypotheses** (`fundraising_hypotheses.md`)
- What investors care about
- Valuation drivers
- Defensibility claims
- Growth trajectories

### By Stakeholder

Hypotheses are tagged with relevant stakeholders:
- `[job_seekers]` - Candidates using platform
- `[employers]` - Companies hiring
- `[community_partners]` - Community leaders we partner with
- `[investors]` - VCs and angels
- `[channel_partners]` - Distribution partnerships

Allows filtering: "Show all hypotheses related to community partners"

---

## Adding New Hypotheses

### From Meetings (Automatic)
System proposes new hypotheses when extracting learnings. Must:
1. Check against existing hypotheses first (avoid duplicates)
2. Map to existing category
3. Require human approval before adding

### Manual Addition
When you identify new assumption to track:
1. Pick appropriate category file
2. Assign next available ID in that category
3. Fill out structure (statement, why it matters, how to test)
4. Set status to "Proposed"
5. Leave evidence section empty until data arrives

---

## Updating Hypotheses

### Status Changes
Require **3+ independent data points** to move from:
- Proposed → Testing (first evidence)
- Testing → Supporting Evidence (2+ confirmations)
- Supporting Evidence → Validated (5+ strong confirmations)
- Validated → Proven (overwhelming evidence, no contradictions)

### Invalidation
Even **1 strong contradiction** triggers review:
- Does evidence truly contradict, or is hypothesis too broad?
- Need to refine hypothesis or pivot strategy?
- Document what we learned from being wrong

### Evidence Addition
Each meeting can add evidence to existing hypotheses:
- Reference meeting ID and date
- Quote or summarize relevant observation
- Note confidence level of this data point
- Update "last updated" date

---

## File Protection

**Backup before modification:**
```bash
Knowledge/hypotheses/.backups/YYYY-MM-DD_HHMM/
```

**Retention:** 30 days, then auto-delete old backups

**Conflict detection:** If file modified since meeting extraction, warn before applying updates

**Change log:** All updates logged to `Knowledge/_update_log.jsonl`

---

## Usage

### For Strategic Planning
- Review hypotheses quarterly
- Identify which are validated (double down)
- Identify which are invalidated (pivot)
- Identify which need more testing (run experiments)

### For Pitching
- Lead with validated hypotheses (de-risked)
- Be transparent about testing hypotheses (honest)
- Show learning velocity (how fast you validate/invalidate)

### For Product/GTM Decisions
- Check: What hypothesis does this decision test?
- Ensure: We have way to measure outcome
- Document: Result as evidence for/against hypothesis

---

## Current Files

- `product_hypotheses.md` - Product and features
- `gtm_hypotheses.md` - Go-to-market and distribution
- `business_model_hypotheses.md` - Pricing and revenue
- `market_hypotheses.md` - Market size and dynamics
- `fundraising_hypotheses.md` - Investor perspectives

---

## Maintenance

**Monthly:** Review all "Testing" hypotheses - do we have new evidence?  
**Quarterly:** Review all hypotheses - status changes? Pivots needed?  
**After major meetings:** Extract learnings and map to hypotheses  
**After product launches:** Gather evidence on product hypotheses

---

## Meta-Learning

Track our hypothesis testing velocity:
- How many hypotheses validated per quarter?
- How many invalidated (and how fast did we pivot)?
- Which categories have most uncertainty?
- Are we testing the right things?

**Founder discipline:** Make assumptions explicit, test them systematically, pivot when wrong.