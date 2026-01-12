---
created: 2026-01-11
last_edited: 2026-01-11
version: 1.0
provenance: con_67oC7ulMHENUObH6
---

# WORKER ASSIGNMENT: Build the v1 list of ~50 strategic acquirer companies for Careerspan

## Objective
Produce a **high-confidence list of ~50 strategic acquirer candidates** for Careerspan.

This list will seed the Notion SSOT databases:
- **Careerspan – Acquirer Targets** (companies)
- **Careerspan – Leadership Targets** (people)

This worker should focus on **strategic acquirers** (not financial buyers).

## Constraints / Guardrails
- Prefer **credible sources**: company websites, product pages, reputable directories, reputable tech news, well-known market maps.
- Avoid speculative “could be acquirers” without at least one concrete rationale.
- Do not scrape or automate against X/Twitter.

## Output format (required)
Return a single table with **~50 rows**.

Columns:
1) **Company**
2) **Website** (URL)
3) **Category (simple)** — pick ONE:
   - ATS
   - HRIS
   - Recruiting marketplace
   - Career platform
   - Staffing tech
   - Verification tech
   - Other
4) **HR stack stage (V taxonomy)** — pick 1–3:
   - Sourcing
   - Matching
   - Verification
   - Vetting
   - Negotiation
   - Onboarding
   - Post-onboarding (retention/performance)
5) **Why plausible acquirer** (1–2 sentences)
6) **Evidence links** (2–4 URLs)

## Inclusion heuristics (what counts as a plausible strategic acquirer)
Pick companies that:
- Sell into recruiting / talent / HR workflows
- Already acquire adjacent tools, or have platform strategy
- Would benefit from Careerspan’s capabilities as a product line, distribution channel, or moat extension

## Exclusion heuristics
Avoid:
- Pure financial firms (PE, holding companies) unless they also operate as strategic builders
- Companies with no recruiting/talent adjacency

## Helpful starting buckets (use these to diversify the 50)
- HR suites / platforms
- ATS vendors
- Recruiting marketplaces
- Background check / identity verification / I-9 / work authorization
- Interviewing + assessment platforms
- Hiring analytics / talent intelligence
- Staffing platforms / modern agencies
- Career services platforms (B2B or B2C) with enterprise distribution

## Success criteria
- List is **diverse** across categories (not 35 ATSs)
- Each company has a clear rationale + evidence links
- It is straightforward to paste the rows into Notion

