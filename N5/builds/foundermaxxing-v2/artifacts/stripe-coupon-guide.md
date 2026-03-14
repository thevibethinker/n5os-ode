---
created: 2026-02-20
last_edited: 2026-02-20
version: 1.3
provenance: con_TFvxUuj5NUrYhYCP
---

# FounderMaxxing — Stripe Coupon & Promo Code Guide

## Overview

Two coupon systems are active on the **Standard** product ($300/mo, `prod_U0mBG5x8TQwOcl`):

| Code | Discount | Duration | Max Uses | Restriction |
|------|----------|----------|----------|-------------|
| `FOUNDING` | $200 off → **$100/mo** | Forever | 15 | First-time customers only |
| `LAUNCH2026` | 50% off → **$150/mo** | First 3 months | 100 | First-time only, expires Dec 31 2026 |

After LAUNCH2026's 3 months, the subscription automatically reverts to $300/mo.

## How It Works

### Stripe Hierarchy

```
Coupon (discount definition)
  └── Promotion Code (customer-facing code string)
        ├── max_redemptions (total cap)
        ├── restrictions (first-time only, etc.)
        └── linked to one Coupon
```

- **Coupons** define the math (amount off, percent off, duration)
- **Promotion Codes** are what customers type at checkout

### Coupons Created

| Coupon ID | Name | Type | Amount |
|-----------|------|------|--------|
| `FOUNDING_200OFF` | FounderMaxxing Founding 15 | Fixed ($200 off) | Forever |
| `LAUNCH2026_50OFF` | FounderMaxxing Launch 2026 | Percent (50% off) | 3 months repeating |

Note: The coupons themselves are not product-restricted at the Stripe level. However, only the Standard payment link has promo codes enabled, so in practice they can only be used on Standard ($300/mo) checkouts.

### Promotion Codes Created

| Code | Coupon | Promo ID | Max | First-time | Expires |
|------|--------|----------|-----|------------|---------|
| `FOUNDING` | `FOUNDING_200OFF` | `promo_1T2lR2HQ08I7w6YsAapTD6Re` | 15 | Yes | Never |
| `LAUNCH2026` | `LAUNCH2026_50OFF` | `promo_1T2mLnHQ08I7w6Yst1P37nRq` | 100 | Yes | Dec 31, 2026 |

## Payment Links

### Active (Promo-Enabled)

| Product | Link | Promo Codes |
|---------|------|-------------|
| **Standard** ($300/mo) | https://buy.stripe.com/8x28wP9sS3wF4DLgi2bsc0e | ✅ Enabled |
| **Founding 15** ($100/mo) | https://buy.stripe.com/3cI00jeNcffnc6d6Hsbsc0d | ❌ (fixed price, no promo needed) |
| **Zo-to-Zo** ($150/mo) | https://buy.stripe.com/00w6oHgVk9V31rz8PAbsc0c | ❌ |

The old Standard link (without promo support) has been **deactivated**.

### Customer Flow

1. Customer clicks the Standard payment link
2. At checkout, they see a "Add promotion code" field
3. They type `FOUNDING` or `LAUNCH2026`
4. Stripe validates: correct product, first-time customer, under max redemptions
5. Discount applies to their subscription

## Admin API

**Endpoint:** `https://va.zo.space/api/foundermaxxing-coupons`

### Authentication

All requests require the admin token via **custom header** (zo.space strips the standard `Authorization` header):

```bash
-H 'X-Admin-Token: $FOUNDERMAXXING_ADMIN_TOKEN'
```

Alternatively, pass as a query parameter: `?token=$FOUNDERMAXXING_ADMIN_TOKEN`

The token is stored as the `FOUNDERMAXXING_ADMIN_TOKEN` secret in Zo Settings > Advanced.

### List Active Promo Codes
```bash
curl -H 'X-Admin-Token: $FOUNDERMAXXING_ADMIN_TOKEN' \
  https://va.zo.space/api/foundermaxxing-coupons
```

### List Coupons
```bash
curl -H 'X-Admin-Token: $FOUNDERMAXXING_ADMIN_TOKEN' \
  'https://va.zo.space/api/foundermaxxing-coupons?action=coupons'
```

### Create a New Promo Code
```bash
curl -X POST https://va.zo.space/api/foundermaxxing-coupons \
  -H 'X-Admin-Token: $FOUNDERMAXXING_ADMIN_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "coupon_id": "FOUNDING_200OFF",
    "code": "FOUNDING-SARAH",
    "max_redemptions": 1,
    "first_time_only": true
  }'
```

This creates a **per-person code** linked to the same FOUNDING coupon but limited to 1 use.

## Creating Per-Person Founding Codes

For maximum security (preventing code sharing):

1. Use the admin API to create individual codes: `FOUNDING-NAME` with `max_redemptions: 1`
2. Share only that specific code with the intended person
3. The master `FOUNDING` code (15 uses) is a fallback for quick invites

## Checking Redemptions

The admin API returns `times_redeemed` for each code. You can also check in:
- [Stripe Dashboard → Coupons](https://dashboard.stripe.com/coupons)
- [Stripe Dashboard → Promotion Codes](https://dashboard.stripe.com/promotion_codes)

## Adding New Coupon Types Later

1. **Create a coupon** in Stripe Dashboard (Products → Coupons → + New)
   - Set amount/percent, duration, product restrictions
2. **Create a promotion code** via the admin API or Dashboard
   - Link it to the new coupon
   - Set max redemptions and restrictions
3. The promo-enabled payment link already accepts any valid code

## Safeguards

- **First-time only:** Both codes require `first_time_transaction=true` — prevents existing customers from stacking
- **Max redemptions:** FOUNDING capped at 15, LAUNCH2026 at 100
- **Payment link scope:** Only the Standard payment link has promo codes enabled, so codes can only be entered there. The coupons themselves are not product-restricted — if you enable promo codes on other payment links later, these coupons would work there too.
- **Permanent attachment:** Once a FOUNDING subscriber signs up, the $200 off coupon stays on their subscription forever (Stripe `duration: forever`)
- **Admin API auth:** All admin API endpoints require a Bearer token (`FOUNDERMAXXING_ADMIN_TOKEN`)

## Audit Cleanup (Feb 20 2026)

The following items were removed during QA:
- **v-discount coupon** — Deleted. Was 100% off forever with no product restriction (from Jan 12 build, 0 redemptions).
- **vlovesyou promo code** — Deactivated (linked to deleted coupon).
- **FOUNDING-TEST-DEBUG** — Deactivated (debug artifact).
- **Old LAUNCH2026 (no expiry)** — Replaced with expiring version above.
- **3 v1 products** — Archived (Zo-to-Zo v1, Founding Class v1, Class of 2026 v1). Payment links were already inactive.
