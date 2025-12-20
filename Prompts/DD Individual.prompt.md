---
created: 2025-12-17
last_edited: 2025-12-17
version: 1.0
provenance: con_8fSBkRPMwtmGxawq
title: DD Individual
description: |
  Purpose-driven deep research on an individual before high-stakes interaction.
  Not routine enrichment - this is conscious, thesis-driven investigation.
  Outputs structured DD report linked to CRM profile.
tags:
  - due-diligence
  - research
  - crm
  - individuals
tool: true
---

# Due Diligence: Individual

## What This Is

**DD ≠ Enrichment**. Enrichment is automatic, accumulative. DD is:
- Consciously triggered with a specific thesis/question
- Investigative (prove/disprove something)
- High-stakes (acquisition, investment, partnership, advisory, employment)
- Multi-source deep research

## When to Use

Use DD when V says things like:
- "Do a DD on [person] - they want to [acquire us / invest / partner / advise]"
- "I need to know if I should [work with / trust / accept offer from] [person]"
- "Research [person] before my meeting - this is a big deal"

## Protocol

### Step 1: Frame the Thesis

Before any research, establish:

```
THESIS FRAMING
==============
Subject: [Full Name]
Organization: [Their company]
Interaction Type: [acquisition | investment | partnership | employment | advisory | vendor | customer | networking]
Question: [The specific question we're answering]
Context: [Why this DD was triggered]
Stakes: [What's at risk if we get this wrong]
```

**Ask V if thesis is unclear.** DD without a thesis is just expensive enrichment.

### Step 2: Pull Existing Intelligence

1. Check CRM profile exists: `python3 N5/scripts/crm_cli.py find --name "[name]"`
2. If exists, read the profile YAML for baseline intel
3. Check if Aviato enrichment already done
4. Check for existing meeting notes with this person

### Step 3: Deep Research

Execute in parallel where possible:

**Source 1: Aviato (if not already enriched)**
```bash
python3 Integrations/Aviato/example_enrichment.py --name "[Full Name]" --company "[Company]"
```

**Source 2: Web Search - Professional**
- Search: "[Name] [Company] announcement OR interview OR profile"
- Search: "[Name] LinkedIn career"
- Search: "[Name] [previous companies]"

**Source 3: Web Search - Reputation**
- Search: "[Name] [Company] review OR controversy OR lawsuit"
- Search: "[Name] fired OR resigned OR scandal" (if high stakes)
- News search: "[Name]" filtered to past 2 years

**Source 4: Gmail History**
```
use_app_gmail("gmail-search-email", {"q": "from:[email] OR to:[email]", "maxResults": 20})
```

**Source 5: Network Intel**
- LinkedIn shared connections (via Aviato or manual)
- CRM query for mutual contacts: `python3 N5/scripts/crm_cli.py find --org "[their org]"`

### Step 4: Synthesize with WIIFM Lens

Structure findings around:

1. **Evidence FOR proceeding** - What supports working with this person?
2. **Evidence AGAINST proceeding** - Red flags, concerns, risks?
3. **UNKNOWN** - What couldn't we answer?

Then explicitly analyze:

**For V personally:**
- Opportunities (career, network, learning)
- Risks (reputation, time, energy)
- Leverage points (what do we bring they need?)

**For Careerspan:**
- Opportunities (customers, tech, market access)
- Risks (distraction, misalignment, dependencies)
- Strategic fit (does this advance Careerspan's mission?)

### Step 5: Produce Output

Create DD report at: `Knowledge/market and competitor intel/due-diligence/[slug]/DD_[Name]_[Date].md`

Follow schema: `N5/schemas/dd_individual.schema.json`

**Required sections:**
- Meta (subject, CRM link, interaction type, date)
- Thesis (question, context, stakes)
- Summary (recommendation, confidence, one-liner, key findings)
- Evidence (for, against, unknown)
- WIIFM (for_v, for_careerspan)
- Network Intel (shared connections, reputation signals)
- Profile Snapshot (from enrichment sources)
- Raw Sources (audit trail)
- Next Actions

### Step 6: Link to CRM

Update CRM profile with DD pointer:
```yaml
## Due Diligence
- 2025-12-17: [DD_[Name]_20251217.md](../../../Knowledge/market%20and%20competitor%20intel/due-diligence/[slug]/DD_[Name]_20251217.md) - [interaction_type]
```

## Output Schema

See `file 'N5/schemas/dd_individual.schema.json'` for full schema.

## Example Invocation

```
V: "Do a DD on Adam Alpert from Pangea - they want to acquire us"

Zo: 
THESIS: Should Careerspan accept acquisition interest from Pangea via Adam Alpert?
STAKES: Major company trajectory decision, V's future role, team outcomes
INTERACTION TYPE: acquisition_inbound

[Proceeds with protocol...]
```

## Integration Points

- **CRM**: DD creates/updates profile, adds DD link
- **Meeting Prep**: DD findings auto-surface when meeting with DD'd individuals
- **Semantic Memory**: DD doc indexed with pointer (not full content)

