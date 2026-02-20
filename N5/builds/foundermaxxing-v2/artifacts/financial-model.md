---
created: 2026-02-20
last_edited: 2026-02-20
version: 4.0
provenance: con_th4MbHhwqlyuEOhE
---

# FounderMaxxing Financial Model v4 — 24-Month Cohort Simulation

**Period:** April 2026 – March 2028
**Target:** 50 concurrent live members + 50 Zo-to-Zo members by ~Month 18
**Allocations:** 20% COGS (Zoputer compute) + 20% Value-Add Reserve off the top

---

## Input Assumptions

### Pricing (2026)
| Tier | Price | Notes |
|------|-------|-------|
| Founding 15 | $100/mo | Locked forever, loss leader |
| Standard Phase 1 | $200/mo | First 10, locked at signup rate |
| Standard Phase 2 | $300/mo | Next 10, locked at signup rate |
| Standard Full | $400/mo | All subsequent 2026 signups |
| Zo-to-Zo | $150/mo | Office hours included |
| 1-on-1 Booking | $50/hr | Founding + Standard, max 3 hrs/mo |

### Pricing (2027)
- New Standard signups: **$600/mo**
- Existing Standard: **discount expires → $400/mo** (locked at 2026 full rate)
- Founding: stays $100 forever

### Churn Model
| Parameter | Standard | Founding (50% lower) |
|-----------|----------|---------------------|
| Graduation month | 3 | 3 |
| → Downgrade to ZtZ | 60% | 30% |
| → Leave entirely | 15% | 10% |
| → Stay (sticky) | 25% | 60% |
| Ongoing churn (sticky) | 4%/mo | 2%/mo |

| Zo-to-Zo Tenure | Monthly Churn |
|-----------------|---------------|
| Months 1-3 | 8% |
| Months 4-6 | 5% |
| Months 7+ | 2% |

### Cost Structure
| Item | Amount | When |
|------|--------|------|
| Part-time hire | $2,000/mo | Month 2 onward |
| Contractor (onboarding) | $30/hr × 10 hrs/wk | 2027 onward |
| V's time | $150/hr imputed | Always |
| Zo credits | $100/member one-time | New signups |
| Stripe | 2.9% + $0.30 | Always |
| COGS | 20% of gross | Always |
| Value-Add Reserve | 20% of gross | Always |

---

## 24-Month Projection — Key Milestones

| Month | Label | Live | ZtZ | Total | Groups | Gross MRR | Net After Reserve |
|-------|-------|------|-----|-------|--------|-----------|-------------------|
| 1 | Apr 2026 | 11 | 0 | 11 | 2 | $1,895 | $-1,522 |
| 2 | May 2026 | 22 | 0 | 22 | 3 | $3,890 | $-3,137 |
| 3 | Jun 2026 | 23 | 4 | 27 | 3 | $5,275 | $-1,848 |
| 4 | Jul 2026 | 23 | 8 | 31 | 3 | $6,807 | $-974 |
| 5 | Aug 2026 | 24 | 11 | 35 | 3 | $8,447 | $-40 |
| 6 | Sep 2026 | 25 | 14 | 39 | 4 | $9,909 | $44 |
| 7 | Oct 2026 | 28 | 17 | 45 | 4 | $11,851 | $951 |
| 8 | Nov 2026 | 31 | 19 | 50 | 4 | $13,678 | $1,992 |
| 9 | Dec 2026 | 33 | 23 | 56 | 5 | $14,976 | $1,982 |
| 10 | Jan 2027 | 34 | 26 | 60 | 5 | $16,224 | $2,692 |
| 11 | Feb 2027 | 36 | 29 | 65 | 5 | $17,424 | $3,376 |
| 12 | Mar 2027 | 37 | 32 | 70 | 5 | $18,577 | $4,033 |
| 13 | Apr 2027 | 38 | 36 | 73 | 5 | $21,176 | $4,317 |
| 14 | May 2027 | 38 | 39 | 76 | 5 | $23,182 | $5,461 |
| 15 | Jun 2027 | 39 | 41 | 80 | 5 | $24,344 | $6,124 |
| 16 | Jul 2027 | 40 | 43 | 83 | 5 | $25,471 | $6,767 |
| 17 | Aug 2027 | 40 | 46 | 86 | 6 | $26,565 | $6,640 |
| 18 | Sep 2027 | 41 | 48 | 89 | 6 | $27,626 | $7,245 |
| 19 | Oct 2027 | 40 | 50 | 90 | 6 | $27,363 | $7,295 |
| 20 | Nov 2027 | 39 | 52 | 91 | 5 | $27,068 | $7,876 |
| 21 | Dec 2027 | 39 | 53 | 92 | 5 | $27,528 | $8,138 |
| 22 | Jan 2028 | 39 | 54 | 94 | 5 | $27,983 | $8,398 |
| 23 | Feb 2028 | 40 | 55 | 95 | 5 | $28,433 | $8,654 |
| 24 | Mar 2028 | 40 | 56 | 96 | 5 | $28,877 | $8,907 |

---

## Annual Summaries

### 2026 (April–December, 9 months)
| Metric | Value |
|--------|-------|
| Gross Revenue | $76,727 |
| Total Costs | $63,935 |
| Reserve Banked | $15,345 |
| **Net After Reserve** | **$-2,553** |
| Peak Members | 56 |
| V hrs/mo (Dec) | 25 |

### 2027–Q1 2028 (January 2027 – March 2028, 15 months)
| Metric | Value |
|--------|-------|
| Gross Revenue | $367,839 |
| Total Costs | $198,347 |
| Reserve Banked | $73,568 |
| **Net After Reserve** | **$95,924** |
| Peak Members | 96 |

### Full 24 Months
| Metric | Value |
|--------|-------|
| Total Gross Revenue | $444,566 |
| Total Net (after reserve) | $93,371 |
| Total Reserve Banked | $88,913 |

---

## Key Insights

1. **2026 is an investment year.** Net −$2.5K after reserve — by design. Founding 15 is the loss leader.
2. **Break-even month: ~September 2026 (Month 6).** Net flips positive as Standard members accumulate.
3. **2027 is the payoff.** $600 Standard price + accumulated ZtZ base = $96K net after reserve.
4. **Reserve war chest:** ~$89K banked over 24 months for future enrichment/value-adds.
5. **V's time caps at ~25 hrs/mo (5 groups × 5 sessions).** Manageable alongside Careerspan.
6. **ZtZ is the flywheel.** Standard churn feeds ZtZ → sticky revenue at near-zero marginal time cost.
7. **Contractor in 2027 ($1,300/mo)** absorbs onboarding load as pipeline thickens.
