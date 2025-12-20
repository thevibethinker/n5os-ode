---
created: 2025-12-17
last_edited: 2025-12-17
version: 1.0
provenance: con_8fSBkRPMwtmGxawq
title: DD Organization
description: |
  Purpose-driven deep research on an organization before high-stakes interaction.
  Covers company intel, financials, leadership, market position, and strategic fit.
  Outputs structured DD report linked to CRM.
tags:
  - due-diligence
  - research
  - crm
  - organizations
tool: true
---

# Due Diligence: Organization

## What This Is

Organization-level DD for evaluating companies in high-stakes contexts:
- Acquisition (inbound or outbound)
- Investment (receiving from or making into)
- Partnership
- Vendor/Customer evaluation
- Competitor analysis

## When to Use

Use DD when V says things like:
- "Do a DD on [Company] - they want to [acquire us / invest / partner]"
- "Research [Company] - considering them as [vendor / partner / acquisition target]"
- "What do we know about [Company]? This could be big for Careerspan"

## Protocol

### Step 1: Frame the Thesis

```
THESIS FRAMING
==============
Organization: [Company Name]
Domain: [company.com]
Interaction Type: [acquisition_inbound | acquisition_outbound | investment_from | investment_into | partnership | vendor | customer | competitor_analysis]
Key Contact: [Primary person, if known]
Question: [The specific question we're answering]
Context: [Why this DD was triggered]
Stakes: [What's at risk if we get this wrong]
Decision Timeline: [When does V need to decide?]
```

### Step 2: Pull Existing Intelligence

1. Check if org exists in CRM
2. Check `Knowledge/market and competitor intel/` for existing research
3. Pull any meeting notes with people from this org
4. Check if key contacts have individual DDs

### Step 3: Deep Research

**Source 1: Company Overview**
- Web search: "[Company] about founded headquarters"
- Crunchbase / PitchBook (via web search if no API)
- LinkedIn Company page
- Company website analysis

**Source 2: Financials**
- Search: "[Company] funding round series"
- Search: "[Company] revenue valuation"
- Search: "[Company] layoffs OR hiring freeze OR runway" (health signals)
- If public: SEC filings
- Investor list and quality assessment

**Source 3: Leadership**
- Identify C-suite and key executives
- Cross-reference with individual DD if exists
- Search: "[CEO name] interview OR profile"
- Background check on founders' track record

**Source 4: Product & Market**
- G2/Capterra reviews (if B2B SaaS)
- Search: "[Company] vs [competitor]"
- Search: "[Company] customer review"
- Product demo/website analysis

**Source 5: Reputation & Risk**
- Glassdoor signals (culture, leadership ratings)
- Search: "[Company] lawsuit OR controversy OR scandal"
- News search: last 12 months
- Search: "[Company] acquired by" (acquisition history)

**Source 6: Network Intel**
- CRM query: who do we know there?
- LinkedIn connections at company
- Backdoor references (people who left)

### Step 4: Synthesize with WIIFM Lens

**Evidence Framework:**
1. **FOR proceeding** - Strategic fit, financial health, aligned incentives
2. **AGAINST proceeding** - Red flags, misalignment, risks
3. **UNKNOWN** - Gaps in our intelligence

**WIIFM Analysis:**

**For V personally:**
- Opportunities (role in combined entity, network expansion, learning)
- Risks (reputation, golden handcuffs, culture mismatch)
- Leverage points (what's unique about V they need?)
- Exit scenarios (if acquisition: what happens to V in 1/2/3 years?)

**For Careerspan:**
- Opportunities (capital, customers, tech, market access)
- Risks (distraction, loss of control, culture dilution)
- Strategic fit (does this accelerate or derail the mission?)
- Product synergies (what could we build together?)
- Customer overlap (complementary or cannibalistic?)

### Step 5: Produce Output

Create DD report at: `Knowledge/market and competitor intel/due-diligence/[company-slug]/DD_[Company]_[Date].md`

Follow schema: `N5/schemas/dd_organization.schema.json`

**Required sections:**
- Meta (org name, domain, interaction type, key contact, date)
- Thesis (question, context, stakes, timeline)
- Summary (recommendation, confidence, one-liner, key findings)
- Evidence (for, against, unknown)
- WIIFM (for_v, for_careerspan)
- Company Intel (overview, financials, leadership, product, market position, reputation)
- Network Intel (shared connections, people at org, backdoor refs)
- Raw Sources (audit trail)
- Next Actions

### Step 6: Link to CRM

If org record exists in CRM, add DD link.
If key contact exists, cross-link individual and org DD.

## Company Intel Deep Dive

### Financial Health Signals

| Signal | Where to Find | Red Flag | Green Flag |
|--------|---------------|----------|------------|
| Last funding | Crunchbase | >24 mo ago + no revenue growth | Recent round or profitable |
| Runway | News + layoff signals | Layoffs, hiring freeze | Hiring, expanding |
| Investor quality | Crunchbase | Unknown/shady investors | Tier 1 VCs |
| Revenue | News, estimates | Declining/flat | Growing, diversified |

### Leadership Assessment

For each key executive, note:
- Track record (previous exits, failures)
- Tenure (how long at company)
- Reputation signals
- Red flags (fraud, lawsuits, pattern of short tenures)

### Market Position

- Who are the top 3 competitors?
- What's their differentiation?
- Are they winning or losing deals? To whom?
- Market timing (growing market or saturated?)

## Output Schema

See `file 'N5/schemas/dd_organization.schema.json'` for full schema.

## Example Invocation

```
V: "Do DD on Pangea - Adam says they want to acquire Careerspan"

Zo:
THESIS: Is Pangea a credible and aligned acquirer for Careerspan?
STAKES: Company trajectory, V's future, team outcomes, mission continuity
INTERACTION TYPE: acquisition_inbound
DECISION TIMELINE: [Ask V]

[Proceeds with protocol...]
```

## Integration Points

- **CRM**: Updates org record, links to key contact profiles
- **Individual DD**: Cross-links if key contact has individual DD
- **Meeting Prep**: Org DD surfaces when meeting with anyone from that org
- **Semantic Memory**: DD doc indexed with pointer

