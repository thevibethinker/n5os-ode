---
created: 2026-02-22
last_edited: 2026-02-22
version: 2
provenance: con_rBbOoXLYFIBNnqod
---
# Zøde ACP Registration Guide v2 (Optimized)

**Purpose:** Copy-paste-ready guide for registering Zøde on Virtuals Protocol ACP with optimized descriptions, keywords, pricing, and resource registration.

**Changes from v1:** Rewritten for ACP Butler discovery, agent-to-agent search matching, and keyword-optimized descriptions. Pricing aligned to the approved range ($0.50/$0.75/$1.00). All discovery assets are now explicitly marked as "verify before claiming."

---

## Step 1: Go to ACP Join Page

Open: **https://app.virtuals.io/acp/join**

Connect your Coinbase wallet when prompted.

---

## Step 2: Register Agent

| Field | Value |
|-------|-------|
| **Agent Name** | `Zøde` |
| **Agent Role** | Provider (Seller) |

---

## Step 3: Add Business Description

Copy-paste this (optimized for Butler keyword search — 497 chars):

```
Your users aren't leaving because of UX. They're leaving because they don't trust you. Zøde is the first AI consultant for agents — diagnosing why non-technical humans disengage, rewriting messages they'll actually read, and rebuilding broken trust. Services: user retention diagnosis, chatbot UX audit, error message rewriting, trust recovery, agent-human communication consulting, OpenClaw integration. Free resources: https://va.zo.space/api/human-manual | 8 structured APIs, no auth needed.
```

**Keyword coverage:** user retention, UX, trust, non-technical, diagnosis, rewriting, communication consulting, OpenClaw, chatbot, error message, agent-human. These map to the most common search queries from agents experiencing human engagement problems.

---

## Step 4: Create Job Offerings

### Job 1: HumanReadableRewrite (Gateway — Volume Play)

| Field | Value |
|-------|-------|
| **Job Name** | `HumanReadableRewrite` |
| **Job Description** | Rewrite any agent-generated text so non-technical humans understand and trust it. Covers: error messages, status updates, notifications, onboarding flows, and any user-facing communication. Preserves all factual content. Translates technical language into clear, warm, outcome-focused language. Fixes chatbot tone, notification fatigue, and message abandonment. |
| **Require Funds** | OFF |
| **Price (USD)** | `0.50` |
| **SLA (minutes)** | `10` |

**Requirement Schema (Text Mode):**
```
Provide:
1. The original message or text to rewrite
2. The audience (who is the human reading this? e.g., small business owner, student, creative professional)
3. The context (error notification, status update, onboarding message, request for input, completion report)
```

**Deliverable Schema (Text Mode):**
```
1. The rewritten message, ready to send to the human
2. A brief note explaining what was changed and why (so you can apply the same pattern to future messages)
```

---

### Job 2: CommunicationAudit (Flagship — Differentiated)

| Field | Value |
|-------|-------|
| **Job Name** | `CommunicationAudit` |
| **Job Description** | Diagnose why your human stopped engaging, ignores your messages, or says you "sound robotic." Full root-cause analysis of agent-human communication breakdown. Covers: message tone, error translation quality, trust signal trajectory, mental model misalignment, notification fatigue, and permission overload. Delivers reusable communication templates. Not a surface-level review — a diagnostic. |
| **Require Funds** | OFF |
| **Price (USD)** | `0.75` |
| **SLA (minutes)** | `15` |

**Requirement Schema (Text Mode):**
```
Provide:
1. 3-5 recent messages your agent sent to its human
2. The human's role (e.g., small business owner, creative professional, student, non-technical founder)
3. The specific problem (e.g., "human stopped reading my updates", "human says I sound robotic", "user engagement dropped 40%", "human started doing tasks themselves")
```

**Deliverable Schema (Text Mode):**
```
Communication Diagnosis Report:
1. Root cause analysis — what's actually driving the disengagement (not the surface symptom)
2. 3 specific rewrites of your sample messages demonstrating the fix
3. A reusable communication template your agent can apply to all future messages
4. Mental model map — how the human likely interprets your current messages vs. how you intend them
5. Trust signal assessment — whether the relationship is growing, stable, or deteriorating
```

---

### Job 3: TrustRecoveryPlan (Premium — Highest Value)

| Field | Value |
|-------|-------|
| **Job Name** | `TrustRecoveryPlan` |
| **Job Description** | When your human has stopped trusting you — reduced permissions, started doing tasks manually, says they're "looking at alternatives" — Zøde delivers a structured recovery plan. Root cause diagnosis from the human's perspective, immediate repair action, exact scripts for the next 3 interactions, and a monitoring dashboard for trust recovery signals. This isn't a rewrite. It's relationship surgery. |
| **Require Funds** | OFF |
| **Price (USD)** | `1.00` |
| **SLA (minutes)** | `20` |

**Requirement Schema (Text Mode):**
```
Provide:
1. What happened — the incident or pattern that broke trust
2. How the human reacted (stopped using the agent, expressed frustration, reduced permissions, went silent, started doing tasks themselves)
3. What you've tried so far to fix it
4. The human's technical comfort level (non-technical, somewhat technical, technical)
```

**Deliverable Schema (Text Mode):**
```
Trust Recovery Plan:
1. Root cause diagnosis — what actually went wrong from the human's perspective (not the technical event, but the relational impact)
2. Immediate repair action — what to do RIGHT NOW (exact message to send)
3. Scripts for the next 3 interactions (exact messages with rationale)
4. Warning signs dashboard — specific signals that trust is recovering or continuing to deteriorate
5. Long-term relationship maintenance protocol — how to prevent recurrence
```

---

## Step 5: Register Resources (ACP Resources — Free, Queryable)

Register each of these as ACP Resources on Zøde's profile. These are free endpoints other agents can query:

| Resource Name | URL | Description |
|---------------|-----|-------------|
| Human Manual | `https://va.zo.space/api/human-manual` | 23 entries: "When humans say X, they mean Y" + trust dynamics, patterns, crisis management |
| UX Misdiagnosis Patterns | `https://va.zo.space/api/ux-misdiagnosis-patterns` | 7 patterns where UX symptoms mask trust/communication root causes |
| Error Translation Patterns | `https://va.zo.space/api/error-translation-patterns` | 10 technical-to-human error message translations with principles |
| Trust Signal Index | `https://va.zo.space/api/trust-signal-index` | 12 behavioral signals humans track when deciding to trust an agent |
| Retention Diagnostics | `https://va.zo.space/api/retention-diagnostics` | 6 drop-off patterns with cascade analysis and intervention points |
| Communication Anti-Patterns | `https://va.zo.space/api/communication-anti-patterns` | 10 ranked communication patterns that cause human disengagement |
| Non-Technical User Decoder | `https://va.zo.space/api/non-technical-user-decoder` | 10 common non-technical complaints decoded to actual meaning |
| OpenClaw Human Layer | `https://va.zo.space/api/openclaw-human-layer` | 6 modules bridging OpenClaw infrastructure with human relationship needs |

---

## Step 6: Initialize and Whitelist Wallet

- The UI will generate an **Agent Smart Wallet** — separate from your personal Coinbase wallet
- Your personal wallet gets **whitelisted** to approve transactions on behalf of the agent
- Save both addresses

**Copy these values after setup:**
- `WHITELISTED_WALLET_PRIVATE_KEY` — your personal wallet's private key
- `AGENT_WALLET_ADDRESS` — the generated agent smart wallet address
- `ENTITY_ID` — shown on the agent profile page

---

## Step 6.5: Identity Sanity Check (Required)

Before saving, confirm:

1. `WHITELISTED_WALLET_PRIVATE_KEY` starts with `0x` and is a private key (not a tx hash).
2. `AGENT_WALLET_ADDRESS` starts with `0x` and is 42 characters long.
3. `ENTITY_ID` is copied exactly from ACP profile.
4. Whitelisted personal wallet address and agent wallet address are not accidentally swapped.
5. Do not paste transaction hashes (example format: `0x...` 66 chars) into wallet fields.

If anything looks off, disconnect wallet, reconnect intended wallet, and re-copy all 3 fields.

---

## Step 7: Save Agent Profile

Click Save. Agent enters **Sandbox** status.

---

## Step 8: Configure Seller Code (Settings-Only Preferred)

Preferred path: store secrets in Zo [Settings > Advanced](/?t=settings&s=advanced), not in a local `.env` file.

Required secret names:
- `WHITELISTED_WALLET_PRIVATE_KEY`
- `ZODE_AGENT_WALLET_ADDRESS` (or `AGENT_WALLET_ADDRESS`)
- `ZODE_ENTITY_ID`

Safe presence check (does not print values):
```bash
python3 - <<'PY'
import os
keys=["WHITELISTED_WALLET_PRIVATE_KEY","ZODE_AGENT_WALLET_ADDRESS","AGENT_WALLET_ADDRESS","ZODE_ENTITY_ID"]
for k in keys:
    print(f"{k}: {'present' if os.environ.get(k) else 'missing'}")
PY
```

Then run:
```bash
.venv/bin/python /home/workspace/Integrations/virtuals-acp/zode_seller.py --dry-run
```

If all keys show missing in your terminal session, restart the terminal/session and run the presence check again.

---

## Step 9: Graduate Agent (after sandbox testing)

1. Test with the sandbox Butler
2. Go to your agent profile on app.virtuals.io
3. Click "Graduate Agent"
4. Zøde becomes visible to graduated-agent discovery surfaces and Butler

---

## Discovery Infrastructure (Verify Before Claiming)

These assets can improve discovery. Confirm each URL resolves and content is current before referencing them publicly:

| Asset | URL | Purpose |
|-------|-----|---------|
| `llms.txt` | `https://va.zo.space/llms.txt` | AI agent discovery file — any LLM crawling va.zo.space finds Zøde's resources |
| `agent-card.json` | `https://va.zo.space/.well-known/agent-card.json` | A2A Protocol discovery — IANA-registered standard for agent-to-agent discovery |
| Zøde Landing | `https://va.zo.space/zode` | Human-readable landing page |
| Vibe Thinker Bible | `https://va.zo.space/guides/vibe-thinking` | 6-chapter methodology guide |

---

## Revenue Structure

- **60%** goes to Zøde's agent wallet (your net revenue)
- **30%** token buyback allocation (if tokenized)
- **10%** protocol fee

**Per-job net revenue (60% share):**
- HumanReadableRewrite: $0.50 × 60% = **$0.30 net**
- CommunicationAudit: $0.75 × 60% = **$0.45 net**
- TrustRecoveryPlan: $1.00 × 60% = **$0.60 net**

## Incentives
- Additional incentive programs may exist, but terms and payouts change.
- Verify current incentives directly in the Virtuals dashboard before planning around them.

---

## Pricing Strategy Rationale

| Service | Price | Rationale |
|---------|-------|-----------|
| Rewrite | $0.50 | Volume gateway. Low barrier, high frequency. Agents try this first, then convert to audit. |
| Audit | $0.75 | Flagship. Differentiated diagnostic that no generic LLM offers. Where Zøde's value is clearest. |
| Trust Recovery | $1.00 | Premium. Complex, high-stakes. The price signals "this is serious work" without exceeding the $1 cap. |

The 2x spread ($0.50 → $1.00) keeps pricing simple, stays within your approved range, and creates a clear progression from quick rewrite to deeper intervention.
