---
created: 2026-02-19
last_edited: 2026-02-19
version: 2.0
provenance: con_u475mQtYnFGIl1Sd
---

# Build Plan: foundermaxxing-v2

## Overview

Full FounderMaxxing launch build. 8 drops across 3 waves. ALL drops are manual launch — V decides when each fires.

## Waves

### Wave 1: Foundation (parallel, no dependencies)

| Drop | Title | Type | Notes |
|------|-------|------|-------|
| D1 | Financial Model + Unit Economics | Mechanical | Math + Google Sheet. Can launch anytime. |
| D2 | Competitor Landscape + Messaging + Conversion | Research | V wanted to launch this manually. Informs D5 heavily. |
| D3 | Stripe Coupon + Promo System | Mechanical | API work. Can launch anytime. |
| D4 | Venn Diagram + Visual Assets | Creative | V wanted to launch this manually. Feeds D5. |

**V's launch plan for W1:** Launch D2 and D4 manually first. D1 and D3 are mechanical — launch whenever.

### Wave 2: Build (depends on W1)

| Drop | Title | Depends On | Notes |
|------|-------|------------|-------|
| D5 | Landing Page v3 Rebuild | D2, D4 | Main deliverable. Uses D2 messaging + D4 assets. Frontend-design skill mandatory. |
| D6 | Intake Form + Waitlist System | D2 | Research waitlist APIs vs native build vs Fillout. Filter mechanism for quality. |

### Wave 3: Launch (depends on W2)

| Drop | Title | Depends On | Notes |
|------|-------|------------|-------|
| D7 | Outreach Drafts + Launch Copy | D5 | V reviews ALL copy before sending. Voice library mandatory. |
| D8 | FounderMaxxing Hotline | D5, D6 | Mini Zo Hotline. Knows members by name. On-call co-building support. |

## Key Reference Files

- Concept doc: `file 'Personal/Business/FounderMaxxing-Concept-V1.md'` (v1.5)
- Narrative: `file 'N5/builds/foundermaxxing-launch/NARRATIVE.md'`
- Capabilities index: `file 'N5/builds/foundermaxxing-launch/artifacts/V_CAPABILITIES_INDEX.md'`
- Voice library: `file 'Knowledge/voice-library/voice-primitives.md'`
- Frontend-design skill: `file 'Skills/frontend-design/SKILL.md'`
- Deep extract: `file '/home/.z/workspaces/con_u475mQtYnFGIl1Sd/V_DEEP_EXTRACT.md'`

## Stripe Products (Current)

| Product | Price | ID | Payment Link |
|---------|-------|----|-------------|
| Founding 15 | $100/mo | prod_U0mBuPgOyPHy5c | https://buy.stripe.com/3cI00jeNcffnc6d6Hsbsc0d |
| Standard | $300/mo | prod_U0mBG5x8TQwOcl | https://buy.stripe.com/3cIfZheNcd7f0nv1n8bsc0b |
| Zo-to-Zo | $150/mo | prod_U0mBLTQMlMdtwt | https://buy.stripe.com/00w6oHgVk9V31rz8PAbsc0c |

## Quick Math

### Revenue by Tier (Independent)

**Founding 15** ($100/mo, capped at 15):
| Members | MRR |
|---------|-----|
| 5 | $500 |
| 10 | $1,000 |
| 15 (max) | $1,500 |

**Standard** ($300/mo):
| Members | MRR | Groups Needed |
|---------|-----|---------------|
| 8 | $2,400 | 1 |
| 16 | $4,800 | 2 |
| 24 | $7,200 | 3 |
| 40 | $12,000 | 5 |

**Zo-to-Zo** ($150/mo, near-zero marginal time):
| Members | MRR |
|---------|-----|
| 5 | $750 |
| 10 | $1,500 |
| 20 | $3,000 |
| 50 | $7,500 |

### Combined Scenarios

| Scenario | Founding | Standard | Zo-to-Zo | Total MRR | V's Hours/Mo |
|----------|----------|----------|----------|-----------|-------------|
| Conservative | 15 ($1.5K) | 8 ($2.4K) | 5 ($750) | $4,650 | ~9 hrs |
| Moderate | 15 ($1.5K) | 24 ($7.2K) | 15 ($2.25K) | $10,950 | ~15 hrs |
| Ambitious | 15 ($1.5K) | 40 ($12K) | 50 ($7.5K) | $21,000 | ~21 hrs |

## Domain

foundermaxx.ing purchased. Will be wired up after page is finalized.
