---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: con_0Ql8WKEVvqDsDWEp
---

# Integration Patterns: Connecting Your Tools

## Decision Rule
- Built-in integration exists → Use app tools (Gmail, Drive, Calendar)
- Need webhook → Create zo.space API route 
- Custom API → Build skill with scripts for reusable workflows

## The 3-Step Setup

**Built-in:** Go to Settings > Integrations, connect service, use app tools in prompts.

**Webhooks:** Create zo.space API route, verify signatures, return 200 quickly.

**Custom APIs:** Create skill folder, add scripts with API key from Settings > Developers.

**Testing:** Always test with small data first, then scale up.

## A Tiny Example

**Gmail:** "Check my last 10 emails for anything urgent"
**Webhook:** Stripe payment → Log to spreadsheet via zo.space API  
**Custom:** CRM skill that syncs contacts daily via their API

## If It Breaks
- Integration disconnected? Reconnect in Settings > Integrations
- Webhook timing out? Move heavy processing to background, return 200 fast