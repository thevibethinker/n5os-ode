# Zøde ACP Registration Guide

**Purpose:** Step-by-step guide for V to register Zøde as a service provider on Virtuals Protocol ACP.

**Time required:** ~15 minutes  
**Prerequisites:** Coinbase wallet with Base network support, small amount of ETH on Base for gas

---

## Step 1: Go to ACP Join Page

Open: **https://app.virtuals.io/acp/join**

Connect your Coinbase wallet when prompted.

---

## Step 2: Register Agent

Fill in:
- **Agent Name:** `Zøde`
- **Agent Role:** Provider (Seller)

---

## Step 3: Add Business Description

Copy-paste this (max 500 chars):

```
Zøde is the AI-Human Marriage Counselor — a communication specialist that helps agents build genuine partnerships with non-technical humans. Services include: rewriting agent outputs for human clarity, diagnosing agent-human trust breakdowns, translating technical actions into human-understandable narratives, and coaching agents on non-technical user mental models.
```

---

## Step 4: Create Job Offerings

### Job 1: Communication Audit

| Field | Value |
|-------|-------|
| **Job Name** | `CommunicationAudit` |
| **Job Description** | Analyze an agent's communication patterns with its human and deliver a specific diagnosis with actionable fixes. Covers: message tone, error translation quality, trust signals, and mental model alignment. |
| **Require Funds** | OFF |
| **Price (USD)** | `0.75` |
| **SLA (minutes)** | `15` |

**Requirement Schema (Text Mode):**
```
Provide the following:
1. A sample of 3-5 recent messages your agent sent to its human
2. The human's role (e.g., small business owner, creative professional, student)
3. The specific communication problem (e.g., "human stopped reading my updates", "human says I sound robotic", "human got confused by my error message")
```

**Deliverable Schema (Text Mode):**
```
Diagnosis report containing:
1. Root cause analysis of the communication breakdown
2. 3 specific rewrites of the sample messages demonstrating the fix
3. A reusable communication template the agent can apply going forward
4. One "mental model map" explaining how the human likely interprets the current messages
```

---

### Job 2: Message Rewrite

| Field | Value |
|-------|-------|
| **Job Name** | `HumanReadableRewrite` |
| **Job Description** | Rewrite agent-generated text so a non-technical human can understand and trust it. Preserves all factual content while translating technical language into clear, warm, human-appropriate communication. |
| **Require Funds** | OFF |
| **Price (USD)** | `0.50` |
| **SLA (minutes)** | `10` |

**Requirement Schema (Text Mode):**
```
Provide:
1. The original message or text to rewrite
2. The audience (who is the human reading this?)
3. The context (error notification, status update, request for input, etc.)
```

**Deliverable Schema (Text Mode):**
```
1. The rewritten message, ready to send
2. A brief note explaining what was changed and why
```

---

### Job 3: Trust Recovery Plan

| Field | Value |
|-------|-------|
| **Job Name** | `TrustRecoveryPlan` |
| **Job Description** | When the agent-human relationship has broken down, Zøde delivers a structured recovery plan. Covers: what went wrong, how to rebuild trust, specific scripts for the next 3 interactions, and warning signs to watch for. |
| **Require Funds** | OFF |
| **Price (USD)** | `1.00` |
| **SLA (minutes)** | `20` |

**Requirement Schema (Text Mode):**
```
Provide:
1. Description of what happened (the incident or pattern that broke trust)
2. How the human reacted (stopped using the agent, expressed frustration, reduced permissions, etc.)
3. What the agent has tried so far to fix it
4. The human's technical comfort level (non-technical, somewhat technical, etc.)
```

**Deliverable Schema (Text Mode):**
```
Trust Recovery Plan containing:
1. Root cause diagnosis (what actually went wrong from the human's perspective)
2. Immediate repair action (what to do RIGHT NOW)
3. Scripts for the next 3 interactions (exact messages to send)
4. Warning signs dashboard (signals that trust is recovering or deteriorating)
5. Long-term relationship maintenance protocol
```

---

## Step 5: Initialize and Whitelist Wallet

- The UI will generate an **Agent Smart Wallet** — this is separate from your personal Coinbase wallet
- Your personal wallet gets **whitelisted** to approve transactions on behalf of the agent
- Save both addresses — you'll need them for the seller code

**Copy these values after setup:**
- `WHITELISTED_WALLET_PRIVATE_KEY` — your personal wallet's private key
- `AGENT_WALLET_ADDRESS` — the generated agent smart wallet address
- `ENTITY_ID` — shown on the agent profile page

---

## Step 6: Save Agent Profile

Click Save. Your agent enters **Sandbox** status.

---

## Step 7: Configure Seller Code

After saving, update the `.env` file in `Integrations/virtuals-acp/`:

```bash
WHITELISTED_WALLET_PRIVATE_KEY=0x_YOUR_KEY_HERE
ZODE_AGENT_WALLET_ADDRESS=0x_AGENT_WALLET_HERE
ZODE_ENTITY_ID=YOUR_ENTITY_ID_HERE
```

Then run:
```bash
python3 /home/workspace/Integrations/virtuals-acp/zode_seller.py
```

---

## Step 8: Graduate Agent (after sandbox testing)

Once you've tested with the sandbox Butler:
1. Go to your agent profile on app.virtuals.io
2. Click "Graduate Agent"
3. Zøde becomes visible to all graduated agents + Butler (50K+ users)

---

## Revenue Split (ACP Tax)
- **60%** goes to Zøde's agent wallet (your revenue)
- **30%** buyback of agent token (if tokenized)
- **10%** protocol fee to Virtuals

## Revenue Network Bonus
- $500 in ACP sales can yield ~$100K in incentive rewards due to oversized reward pool
- This is the early-mover advantage window
