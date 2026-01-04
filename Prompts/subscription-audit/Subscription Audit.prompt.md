---
created: 2026-01-03
last_edited: 2026-01-03
version: 1.0
provenance: con_rppbSuGPcwcnkS0H
name: Subscription Audit
description: |
  Analyze bank/credit card transaction CSVs to find recurring charges, categorize subscriptions,
  and help cancel what you don't need. Outputs an interactive HTML audit with savings calculation.
  Adapted from https://github.com/rohunvora/just-fucking-cancel for Zo.
tags:
  - finance
  - subscriptions
  - audit
  - cancel
tool: true
triggers:
  - cancel subscriptions
  - audit subscriptions
  - find recurring charges
  - what am I paying for
---

# Subscription Audit

Analyze transactions, categorize subscriptions, generate HTML audit, help cancel.

## Workflow

### 1. Get Transaction CSV

Ask user for bank/card CSV export. Common sources:
- **Apple Card**: Wallet → Card Balance → Export
- **Chase**: Accounts → Download activity → CSV
- **Amex**: Statements & Activity → Download → CSV
- **Mint/Copilot**: Transactions → Export

If user hasn't provided a CSV yet, explain how to export from their bank.

### 2. Analyze Recurring Charges

Read CSV, identify recurring patterns:
- Same merchant, similar amounts, monthly/annual frequency
- Flag subscription-like charges (streaming, SaaS, memberships)
- Note charge frequency and total annual cost
- Cross-reference with `subscriptions.json` for known subscription pricing

### 3. Categorize with User

For each subscription, ask user to categorize:
- **Cancel** — Stop immediately
- **Investigate** — Needs decision (unsure, trapped in contract)
- **Keep** — Intentional, continue paying

Ask in batches of 5-10 to avoid overwhelming. Use conversational prompts like:
- "Do you actually use [Service]?"
- "When did you last open [Service]?"
- "Is this one worth $X/month to you?"

### 4. Generate HTML Audit

Copy `audit-template.html` and populate:
- Update header summary:
  - Scope line: "found N subscriptions · N transactions"
  - Breakdown: "Cancelled N · Keeping N"
  - Savings: yearly amount big, monthly in parentheses
  - Timestamp: current date
- Add rows to appropriate sections (cancelled/investigate/keep)
- Include notes from user responses

Save to user's workspace as `subscription-audit-YYYY-MM-DD.html`

### 5. Provide Cancellation Help

When user is ready to cancel, for each service:
1. Check `common-services.md` for cancel URL
2. Provide direct link and any warnings (dark patterns, phone-only, etc.)
3. Offer retention script responses if needed

## Reference Files

- `audit-template.html` — HTML template with styling and interactivity
- `common-services.md` — Cancel URLs and dark pattern warnings for 50+ services
- `subscriptions.json` — Current pricing for common subscriptions by category

## HTML Features

The output HTML includes:
- **Three sections**: Cancelled (green), Needs Decision (orange), Keeping (grey)
- **Floating copy button** — Select items and copy "Cancel these: Service1 ($XX), Service2 ($XX)..."
- **Privacy toggle** — Blur service names before screenshotting
- **Collapsible sections** — Click headers to collapse
- **Dark mode support** — Automatic based on system preference

## Cancellation Tips

### For Difficult Services (Dark Patterns)

**Phone-only cancellation:**
- SiriusXM: 1-866-635-2349 (heavy retention)
- NYTimes (some plans): 1-800-591-9233
- Most gyms: See common-services.md

**Retention script response:**
> "I've already made my decision. Please process the cancellation."
> 
> Repeat as needed. Don't engage with offers.

**Credit card backup:**
If a service won't cancel after written request, dispute with credit card as "cancelled service"

## Privacy

All data stays local on Zo. Transaction CSVs are analyzed in-session only.

