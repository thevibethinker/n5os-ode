---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_LvWKuTp6TaZnJV5g
---

# Plaid Personal Financial Management Integration Prep

## Overview

This document consolidates Plaid API documentation for the three Personal Financial Management (PFM) products:
1. **Transactions** — spending data, categorization, recurring transactions
2. **Investments** — holdings, positions, investment transactions  
3. **Liabilities** — credit cards, student loans, mortgages

---

## Core Integration Flow (All Products)

All Plaid products share the same authentication and Item creation flow:

```
┌─────────────────────────────────────────────────────────────────┐
│  1. SERVER: Create link_token                                   │
│     POST /link/token/create                                     │
│     - client_id, secret                                         │
│     - products: ["transactions", "investments", "liabilities"]  │
│     - country_codes: ["US"]                                     │
│     - user: { client_user_id: "unique-user-id" }               │
│     - webhook: "https://yourapp.com/plaid/webhook"             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. CLIENT: Initialize Plaid Link with link_token               │
│     - User selects institution, authenticates                   │
│     - Link handles MFA, OAuth, errors                          │
│     - onSuccess callback returns public_token                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. SERVER: Exchange public_token for access_token              │
│     POST /item/public_token/exchange                            │
│     - public_token → access_token + item_id                    │
│     - Store access_token securely (per-user, per-institution)  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. SERVER: Use access_token to call product endpoints          │
│     - /transactions/sync                                        │
│     - /investments/holdings/get                                 │
│     - /liabilities/get                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Transactions API

### Purpose
Retrieve up to **24 months** of historical transaction data including:
- Date, amount, merchant name
- Geolocation (when available)
- Category (Plaid's taxonomy)
- Recurring transaction detection

### Key Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/transactions/sync` | **Primary** — Get transactions with incremental updates via cursor |
| `/transactions/get` | Legacy — Fetch by date range (deprecated, migrate to sync) |
| `/transactions/recurring/get` | Identify recurring transactions (subscriptions, bills) |
| `/transactions/refresh` | Force a refresh of transaction data |
| `/categories/get` | Get all Plaid transaction categories |

### Recommended: `/transactions/sync`

Uses cursor-based pagination for efficient incremental updates:

```javascript
// Node.js example
let cursor = database.getLatestCursorOrNull(itemId);
let added = [], modified = [], removed = [];
let hasMore = true;

while (hasMore) {
  const response = await client.transactionsSync({
    access_token: accessToken,
    cursor: cursor,
  });
  
  added = added.concat(response.data.added);
  modified = modified.concat(response.data.modified);
  removed = removed.concat(response.data.removed);
  
  hasMore = response.data.has_more;
  cursor = response.data.next_cursor;
}

// Persist cursor and updated data
database.applyUpdates(itemId, added, modified, removed, cursor);
```

### Transaction Object (Key Fields)

| Field | Type | Description |
|-------|------|-------------|
| `transaction_id` | string | Unique identifier |
| `account_id` | string | Which account this belongs to |
| `amount` | number | Positive = money out, negative = money in |
| `date` | string | Posted date (YYYY-MM-DD) |
| `authorized_date` | string | When transaction was initiated |
| `name` | string | Merchant or transaction description |
| `merchant_name` | string | Clean merchant name (when available) |
| `category` | array | Plaid category hierarchy |
| `personal_finance_category` | object | Enhanced categorization |
| `location` | object | Address, city, region, lat/lon |
| `pending` | boolean | Whether transaction is pending |
| `iso_currency_code` | string | Currency code (USD, etc.) |

### Webhooks

| Webhook | When Fired |
|---------|------------|
| `SYNC_UPDATES_AVAILABLE` | New updates ready for `/transactions/sync` |
| `INITIAL_UPDATE` | First batch of transactions ready (~minutes) |
| `HISTORICAL_UPDATE` | Full 24-month history ready (~hours) |
| `DEFAULT_UPDATE` | New daily transactions available |
| `TRANSACTIONS_REMOVED` | Transactions deleted by institution |
| `RECURRING_TRANSACTIONS_UPDATE` | Recurring patterns updated |

### Supported Account Types
- `credit` (credit cards)
- `depository` (checking, savings)
- `loan` (student loans only via transactions/sync)

**Note:** For investment account transactions, use `/investments/transactions/get` instead.

---

## 2. Investments API

### Purpose
Access investment account data:
- **Holdings** — Current positions (stocks, bonds, ETFs, crypto, etc.)
- **Transactions** — Buys, sells, dividends, transfers (up to 24 months)

### Key Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/investments/holdings/get` | Get current holdings and securities |
| `/investments/transactions/get` | Get investment transactions (trades, dividends) |
| `/investments/refresh` | Force refresh of investment data |

### Holdings Response Structure

```javascript
const response = await client.investmentsHoldingsGet({
  access_token: accessToken,
});

// Response contains:
// - accounts: investment account info
// - holdings: position data
// - securities: security metadata
```

### Holdings Object (Key Fields)

| Field | Type | Description |
|-------|------|-------------|
| `account_id` | string | Account this holding belongs to |
| `security_id` | string | Links to security object |
| `quantity` | number | Shares/units held |
| `institution_price` | number | Price per share (institution's value) |
| `institution_value` | number | Total value |
| `cost_basis` | number | Original purchase cost |
| `vested_quantity` | number | Vested shares (for equity plans) |

### Securities Object (Key Fields)

| Field | Type | Description |
|-------|------|-------------|
| `security_id` | string | Unique identifier |
| `name` | string | Security name |
| `ticker_symbol` | string | Trading symbol |
| `type` | string | cash, cryptocurrency, derivative, equity, etf, fixed income, loan, mutual fund, other |
| `close_price` | number | Last close price |
| `close_price_as_of` | string | Date of close price |
| `sector` | string | Sector classification |
| `industry` | string | Industry classification |

### Investment Transaction Object

| Field | Type | Description |
|-------|------|-------------|
| `investment_transaction_id` | string | Unique identifier |
| `account_id` | string | Account |
| `security_id` | string | Security involved |
| `date` | string | Transaction date |
| `type` | string | buy, sell, dividend, transfer, etc. |
| `subtype` | string | More specific type |
| `quantity` | number | Shares/units |
| `amount` | number | Dollar amount |
| `price` | number | Price per share |
| `fees` | number | Transaction fees |

### Webhooks

| Webhook | When Fired |
|---------|------------|
| `HOLDINGS: DEFAULT_UPDATE` | Holdings data updated |
| `INVESTMENTS_TRANSACTIONS: DEFAULT_UPDATE` | New investment transactions |
| `INVESTMENTS_TRANSACTIONS: HISTORICAL_UPDATE` | Historical data ready |

### Supported Account Types
- Brokerage
- 401(k), IRA, Roth IRA
- 529 education savings
- HSA
- Crypto exchanges
- And many more investment account types

---

## 3. Liabilities API

### Purpose
Access debt/liability information:
- **Credit Cards** — balances, APRs, minimum payments, due dates
- **Student Loans** — balances, interest rates, servicer info, payment plans
- **Mortgages** — loan details, property info, escrow

### Key Endpoint

| Endpoint | Purpose |
|----------|---------|
| `/liabilities/get` | Get all liability data for an Item |

### Usage

```javascript
const response = await client.liabilitiesGet({
  access_token: accessToken,
});

// Response contains:
// - accounts: liability account info
// - liabilities: {
//     credit: [...],    // Credit card liabilities
//     student: [...],   // Student loan liabilities
//     mortgage: [...],  // Mortgage liabilities
//   }
```

### Credit Card Liability (Key Fields)

| Field | Type | Description |
|-------|------|-------------|
| `account_id` | string | Account identifier |
| `aprs` | array | Array of APR objects (purchase, cash, balance transfer) |
| `is_overdue` | boolean | Payment overdue flag |
| `last_payment_amount` | number | Most recent payment |
| `last_payment_date` | string | Date of last payment |
| `last_statement_balance` | number | Statement balance |
| `minimum_payment_amount` | number | Minimum due |
| `next_payment_due_date` | string | Next due date |

### APR Object

| Field | Type | Description |
|-------|------|-------------|
| `apr_percentage` | number | APR rate |
| `apr_type` | string | purchase_apr, cash_apr, balance_transfer_apr, special |
| `balance_subject_to_apr` | number | Balance this APR applies to |
| `interest_charge_amount` | number | Interest charged |

### Student Loan Liability (Key Fields)

| Field | Type | Description |
|-------|------|-------------|
| `account_id` | string | Account identifier |
| `account_number` | string | Loan account number |
| `disbursement_dates` | array | When funds were disbursed |
| `expected_payoff_date` | string | Projected payoff date |
| `guarantor` | string | Loan guarantor |
| `interest_rate_percentage` | number | Current interest rate |
| `is_overdue` | boolean | Overdue flag |
| `last_payment_amount` | number | Last payment |
| `last_payment_date` | string | Date of last payment |
| `minimum_payment_amount` | number | Minimum due |
| `next_payment_due_date` | string | Next due date |
| `origination_date` | string | Loan origination |
| `origination_principal_amount` | number | Original loan amount |
| `outstanding_interest_amount` | number | Accrued interest |
| `payment_reference_number` | string | Payment reference |
| `repayment_plan` | object | Repayment plan details |
| `servicer_address` | object | Servicer contact info |

### Mortgage Liability (Key Fields)

| Field | Type | Description |
|-------|------|-------------|
| `account_id` | string | Account identifier |
| `account_number` | string | Mortgage account number |
| `current_late_fee` | number | Any late fees due |
| `escrow_balance` | number | Escrow account balance |
| `has_pmi` | boolean | Private mortgage insurance |
| `has_prepayment_penalty` | boolean | Prepayment penalty exists |
| `interest_rate` | object | Rate type and percentage |
| `loan_term` | string | Loan term (e.g., "360 months") |
| `loan_type_description` | string | Fixed, ARM, etc. |
| `maturity_date` | string | Loan maturity |
| `next_monthly_payment` | number | Next payment amount |
| `next_payment_due_date` | string | Next due date |
| `origination_date` | string | Loan origination |
| `origination_principal_amount` | number | Original loan amount |
| `property_address` | object | Property address |
| `ytd_interest_paid` | number | Year-to-date interest |
| `ytd_principal_paid` | number | Year-to-date principal |

### Webhook

| Webhook | When Fired |
|---------|------------|
| `DEFAULT_UPDATE` | Liabilities data updated |

### Supported Account Types
- Credit cards (account type: `credit`, subtype: `credit card`)
- Student loans (account type: `loan`, subtype: `student`)
- Mortgages (account type: `loan`, subtype: `mortgage`)
- PayPal credit (account type: `credit`, subtype: `paypal`)

### Data Refresh
Liabilities data is refreshed approximately **once per day**.

---

## Implementation Checklist

### Phase 1: Setup
- [ ] Create Plaid developer account at dashboard.plaid.com
- [ ] Get Sandbox API keys (client_id + secret)
- [ ] Clone Plaid Quickstart for reference
- [ ] Install Plaid SDK (`npm install plaid` or equivalent)

### Phase 2: Link Integration
- [ ] Implement `/link/token/create` endpoint
- [ ] Integrate Plaid Link on frontend (web/mobile)
- [ ] Implement `/item/public_token/exchange` endpoint
- [ ] Securely store access_tokens (encrypted, per-user)

### Phase 3: Transactions
- [ ] Implement `/transactions/sync` with cursor management
- [ ] Set up webhook endpoint for `SYNC_UPDATES_AVAILABLE`
- [ ] Handle initial vs. historical data loading
- [ ] Implement category mapping for your app's taxonomy

### Phase 4: Investments
- [ ] Implement `/investments/holdings/get`
- [ ] Implement `/investments/transactions/get`
- [ ] Build security → holding relationship mapping
- [ ] Set up holdings/transactions webhooks

### Phase 5: Liabilities
- [ ] Implement `/liabilities/get`
- [ ] Parse credit, student loan, and mortgage objects
- [ ] Build debt tracking/visualization
- [ ] Set up liabilities webhook

### Phase 6: Production
- [ ] Apply for Production access in Plaid Dashboard
- [ ] Complete Plaid's security questionnaire
- [ ] Test with real institutions in Development
- [ ] Implement Update Mode for re-authentication
- [ ] Set up error handling and monitoring

---

## API Environments

| Environment | Purpose | Base URL |
|-------------|---------|----------|
| Sandbox | Testing with fake data | `https://sandbox.plaid.com` |
| Development | Testing with real institutions (100 Items max) | `https://development.plaid.com` |
| Production | Live production | `https://production.plaid.com` |

### Sandbox Test Credentials
```
username: user_good
password: pass_good
MFA code: 1234
```

---

## SDK Installation

```bash
# Node.js
npm install plaid

# Python
pip install plaid-python

# Ruby
gem install plaid
```

### Client Initialization (Node.js)

```javascript
const { Configuration, PlaidApi, PlaidEnvironments } = require('plaid');

const configuration = new Configuration({
  basePath: PlaidEnvironments.sandbox,
  baseOptions: {
    headers: {
      'PLAID-CLIENT-ID': process.env.PLAID_CLIENT_ID,
      'PLAID-SECRET': process.env.PLAID_SECRET,
    },
  },
});

const client = new PlaidApi(configuration);
```

---

## Key Resources

- [Plaid Dashboard](https://dashboard.plaid.com)
- [API Reference](https://plaid.com/docs/api/)
- [Quickstart Repo](https://github.com/plaid/quickstart)
- [Postman Collection](https://github.com/plaid/plaid-postman)
- [Link Documentation](https://plaid.com/docs/link/)
- [Webhooks Guide](https://plaid.com/docs/api/webhooks/)
