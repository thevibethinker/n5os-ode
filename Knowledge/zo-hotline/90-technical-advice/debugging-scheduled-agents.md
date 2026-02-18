---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: con_0Ql8WKEVvqDsDWEp
---

# Debugging Scheduled Agents: When Automation Stops

## Decision Rule
- Agent not running → Check status and delivery method
- Getting errors → Check agent logs and instructions
- Wrong output → Review instructions and test manually

## The 3-Step Setup

**Check Status:** Go to Scheduled Tasks, find your agent, verify "Active" toggle is on.

**Check Delivery:** Ensure delivery method (email/SMS) is configured and account connected.

**Check Instructions:** Click agent to view instructions. Test the same prompt manually in chat first.

**Check Logs:** Look for error messages in agent execution history.

## A Tiny Example

Agent supposed to send daily summary but stops working:
1. Go to Scheduled Tasks → Find "Daily Summary" 
2. Check Active=Yes, Delivery=Email, Connected=Gmail
3. Test prompt: "Summarize today's events" in regular chat

## If It Breaks
- Still not running? Delete and recreate with same schedule
- Getting spam? Adjust frequency or add "if there's new content" condition