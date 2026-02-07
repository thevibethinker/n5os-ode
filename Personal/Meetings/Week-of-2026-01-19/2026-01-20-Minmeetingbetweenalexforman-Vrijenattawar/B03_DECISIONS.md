---
created: 2026-02-02
last_edited: 2026-02-02
version: 1.0
provenance: con_cmOleZMC25ltvgFF
block_type: B03
---

# B03_DECISIONS

## Decision 1: Move to Usage-Based Pricing Model

**DECISION:** Parse will transition from monthly credit buckets to usage-based pricing this week.

**CONTEXT:** The current monthly bucket model doesn't align well with diverse customer usage patterns. Some users only need to fetch data once (e.g., getting all products from Walmart) and don't want to pay for ongoing monthly access. Additionally, Parse faces highly variable costs (bandwidth, anti-bot measures) that differ significantly per website and even per query on the same API, making flat monthly pricing difficult to justify.

**DECIDED BY:** Alex Forman (Parse Founder)

**IMPLICATIONS:** Pricing will become more equitable for customers with sporadic or one-time needs. Parse will likely need to develop a system to track and bill usage dynamically rather than via fixed monthly allocations.

**ALTERNATIVES CONSIDERED:** Monthly credit buckets (current model, being retired)