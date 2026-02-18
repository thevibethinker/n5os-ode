# DROP: Stripe Payment Links for Career Coaching Hotline

## Context

The Careerspan Career Coaching Hotline is a VAPI-powered AI career coaching phone line. It has a **free tier of 15 minutes lifetime per phone number**. After that, callers need to purchase credit packs to continue using the service.

The webhook is at `Skills/career-coaching-hotline/scripts/hotline-webhook.ts` and tracks caller balances in a DuckDB table (`caller_balances`) at `Datasets/career-hotline-calls/data.duckdb`.

## What Needs to Be Built

### 1. Create Three Stripe Products + Payment Links

Credit packs (usage-based, NOT subscription):

| Pack | Price | Minutes | Per-Minute Rate |
|------|-------|---------|-----------------|
| Starter | $15 | 30 min | $0.50/min |
| Standard | $30 | 60 min | $0.50/min |
| Pro | $50 | 120 min | $0.42/min |

Use **live mode** (not test mode) for Stripe.

Each product should:
- Have a clear name like "Careerspan Coaching Credits — 30 Minutes"
- Have a description mentioning the Career Coaching Hotline
- Generate a payment link

### 2. Stripe Webhook for Credit Fulfillment

When a payment completes, we need to credit the caller's balance. This requires:

**Option A (Preferred): Metadata-based**
- Payment link checkout collects the caller's phone number (required field)
- On `checkout.session.completed`, read the phone number + purchased minutes
- Update `caller_balances` in DuckDB: add purchased seconds to `total_seconds_purchased`

**Option B: Manual fulfillment**
- V manually credits callers after payment confirmation

For Option A, you'll need:
- A Stripe webhook endpoint (could be a new route or added to the existing webhook)
- The webhook needs to verify Stripe signatures
- It needs to write to the same DuckDB at `Datasets/career-hotline-calls/data.duckdb`

### 3. Wire Up the Purchase URL

The webhook currently has `PURCHASE_URL` env var defaulting to `https://mycareerspan.com/coaching-credits`. Once the landing page is live at `va.zo.space/hotline`, update the service env var:

```
CAREER_HOTLINE_PURCHASE_URL=https://va.zo.space/hotline
```

## Key Files

- `Skills/career-coaching-hotline/scripts/hotline-webhook.ts` — main webhook, has balance tracking logic
- `Datasets/career-hotline-calls/data.duckdb` — DuckDB with `caller_balances` table
- `N5/builds/career-coaching-hotline/artifacts/` — build artifacts
- `N5/config/PORT_REGISTRY.md` — if you need a new port for a Stripe webhook

## DuckDB Schema (caller_balances)

```sql
CREATE TABLE IF NOT EXISTS caller_balances (
    phone TEXT PRIMARY KEY,
    total_seconds_used INTEGER DEFAULT 0,
    total_seconds_purchased INTEGER DEFAULT 0,
    last_call_at TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now'))
);
```

Free tier = 900 seconds (15 min). Balance = 900 + total_seconds_purchased - total_seconds_used.

## Stripe Tools Available

You have MCP tools for Stripe:
- `create_stripe_product` — create products
- `create_stripe_price` — create prices with payment links
- `create_stripe_payment_link` — create payment links
- `list_stripe_payment_links` — list existing links
- `list_stripe_orders` — check orders

## Deliverables

1. Three Stripe products with payment links (live mode)
2. A plan for credit fulfillment (webhook or manual)
3. Payment link URLs to embed on the landing page
4. Updated `CAREER_HOTLINE_PURCHASE_URL` env var once landing page is ready
