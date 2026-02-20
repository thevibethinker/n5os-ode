---
created: 2026-02-19
last_edited: 2026-02-19
version: 1.0
provenance: con_u475mQtYnFGIl1Sd
---

# Build Plan: foundermaxxing-launch

## Objective

Build all external-facing collateral for FounderMaxxing launch: Stripe subscription products, landing page with integrated application form, and payment links. V must be able to start collecting money TODAY.

## Source of Truth

`file 'Personal/Business/FounderMaxxing-Concept-V1.md'` (v1.1)

## Wave Architecture

### Wave 1: Stripe Infrastructure (Parallel — All Auto-Spawn)

These are mechanical drops with no dependencies on each other.

| Drop | Task | Spawn | Rationale |
|------|------|-------|-----------|
| D1.1 | Create Stripe product: "FounderMaxxing Founding Class" — $100/mo recurring subscription + payment link | auto | Mechanical: Stripe API call |
| D1.2 | Create Stripe product: "FounderMaxxing Class of 2026" — $200/mo recurring subscription + payment link | auto | Mechanical: Stripe API call |
| D1.3 | Create Stripe product: "Zo Mentorship (Standalone)" — $150/mo recurring subscription + payment link | auto | Mechanical: Stripe API call |

**Wave 1 Exit Criteria:** 3 Stripe products created, 3 payment links generated and verified.

### Wave 2: Landing Page (Manual — Needs V Input)

Depends on Wave 1 (needs payment link URLs to embed).

| Drop | Task | Spawn | Rationale |
|------|------|-------|-----------|
| D2.1 | Build FounderMaxxing landing page on zo.space with: value prop, session structure, pricing, what they'll build (N5/OS catalog), application form, and payment link integration | manual | Creative work — V should review messaging, design choices, form fields |

**Wave 2 Exit Criteria:** Landing page live on zo.space, application form functional, payment links accessible.

### Wave 3: Verification & Polish (Manual)

Depends on Wave 2.

| Drop | Task | Spawn | Rationale |
|------|------|-------|-----------|
| D3.1 | End-to-end verification: test application form submission, verify Stripe payment links work, test mobile responsiveness, review copy | manual | QA — V should see the final product |

**Wave 3 Exit Criteria:** Full flow verified, V approves for sharing.

## Dependencies

```
W1 (D1.1, D1.2, D1.3) — parallel, no deps
    ↓
W2 (D2.1) — needs payment link URLs from W1
    ↓
W3 (D3.1) — needs live page from W2
```

## Decisions for V

1. **Year question:** "Class of 2026" — we're in 2026. Confirm intended year for Stripe product name.
2. **Page visibility:** Should the landing page be public immediately? (Recommended: yes, so V can share the URL today)
3. **Application form backend:** Form submissions will be stored where? Options: (a) Zo space API route that stores to workspace JSON, (b) Airtable, (c) email notification to V. Recommend (a) with (c) as notification.

## Risk Register

| Risk | Mitigation |
|------|------------|
| Stripe product naming needs revision | Payment links can be regenerated; products can be updated |
| Landing page copy doesn't land | V reviews in D2.1 before going live |
| Application form data loss | Store to both file and send notification email |
