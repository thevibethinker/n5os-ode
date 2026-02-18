---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: con_lUAmO8hsfnmiy3xh
---

# Webhook Agent Notification Pattern

## What It Is

- Webhook receives external events, triggers Zo agent for immediate response
- Creates real-time reaction loop between world and your AI

## When to Use

- Payment confirmations need instant processing
- Form submissions require immediate follow-up
- API events need human notification
- External systems must trigger Zo actions

## Minimal Build Recipe

- Create webhook API in zo.space: `update_space_route("/api/webhook", "api", code)`
- Add agent creation: `create_agent("FREQ=DAILY", "Check webhook queue and respond")`  
- Store events in simple file: append to `/home/workspace/webhook-events.log`
- Agent processes queue, clears handled events
- Use `send_email_to_user` or `send_sms_to_user` for notifications

## Example Prompts

- "Set up webhook that texts me when Stripe payments arrive"
- "Create system that notifies me of new form submissions within 5 minutes"

## Common Failure Modes

- No event deduplication causes spam
- Missing signature verification allows fake events  
- Agent runs too frequently, wastes resources