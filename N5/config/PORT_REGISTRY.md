---
created: 2026-01-14
last_edited: 2026-02-16
version: 1.5
provenance: con_xMvzWKgpZHS5XdCn
---

# N5 Port Registry

**Single Source of Truth for all port allocations on this Zo.**

## Rules
1. **NEVER assign a port without checking this registry first**
2. **ALWAYS update this registry when creating a new service**
3. **Reserved ranges exist** — respect them

## Reserved Port Ranges

| Range | Purpose |
|-------|---------|
| 3000-3499 | Zo Sites (production and staging) |
| 5678 | n8n (reserved) |
| 8000-8100 | N5 metrics/monitoring |
| 8123 | HTTP file server (reserved) |
| 8384 | Syncthing (reserved) |
| 8420-8499 | Meeting pipeline services |
| 8763-8844 | N5 core services |
| 8845-8899 | Webhook receivers |
| 8900-8999 | Zapier/automation |
| 9090 | Prometheus (reserved) |
| 19999 | Background workers |
| 50000-51999 | Mid-range ephemeral (Sites staging, dashboards) |
| 52000-58999 | High-range ephemeral |

## Active Port Allocations

| Port | Service Label | Protocol | Source | Purpose |
|------|---------------|----------|--------|---------|
| 3000 | did-i-get-it | http | service | Did I Get It app |
| 3001 | productivity-dashboard-staging | http | service | Productivity dashboard staging |
| 3047 | events-calendar | http | service | Events calendar |
| 3461 | ir-staging | http | service | Interview Reviewer staging |
| 5678 | n8n | http | service | n8n automation platform |
| 8010 | workout-dashboard | http | service | Workout tracker dashboard |
| 8080 | conversation-installer | http | service | Conversation API installer |
| 8081 | fitbit-legal | http | service | Fitbit legal page |
| 8123 | va-http | http | service | General HTTP file server |
| 8384 | syncthing | http | service | Syncthing sync service |
| 8420 | fireflies-webhook | http | service | Fireflies meeting webhook |
| 8421 | fireflies-poller | tcp | service | Fireflies API poller |
| 8422 | fathom-poller | tcp | service | Fathom meeting poller |
| 8763 | fathom-webhook | http | service | Fathom meeting webhook |
| 8764 | umami | http | service | Umami analytics |
| 8765 | kondo-linkedin-webhook | http | service | Kondo LinkedIn webhook |
| 8766 | n5-bootstrap-support | http | service | N5 bootstrap server |
| 8767 | crm-webhook-health | tcp | service | CRM webhook health monitor |
| 8768 | n5-advisor | http | service | N5 bootstrap advisor |
| 8769 | n5-conversation-api | http | service | N5 conversational API |
| 8770 | zo-n8n-api | http | service | Zo-n8n bridge API |
| 8771 | action-approvals-monitor | http | service | Action approvals monitor |
| 8772 | task-completion-detector | http | service | Task completion detector |
| 8775 | slack-bot | http | service | Slack bot receiver |
| 8778 | crm-calendar-webhook | http | service | CRM calendar webhook handler |
| 8780 | did-i-get-it | http | service | Did I Get It production |
| 8790 | position-viz | http | service | Position visualization |
| 8791 | agentmail-webhook | http | service | AgentMail Svix receiver with inbox firewall |
| 8845 | fillout-webhook | http | service | Fillout form webhook |
| 8847 | careerspan-webhook | http | service | Careerspan data webhook |
| 8848 | career-coaching-hotline | http | service | Career Coaching Hotline (Zozie) VAPI webhook |
| 8900 | zapier-webhook | http | service | Zapier webhook receiver |
| 9090 | prometheus | http | service | Prometheus monitoring |
| 19999 | semantic-reindex | tcp | service | Semantic reindex service |
| 50000 | vrijenattawar-staging | http | zosite | Personal site staging |
| 50001 | calendly-auth | http | service | Calendly OAuth + webhook receiver |
| 50002 | build-tracker | http | zosite | Build Tracker dashboard |
| 50003 | vrijenattawar-staging | http | service | Personal site staging |
| 50004 | keanu-to-market | http | service | Keanu to Market (prod) |
| 50005 | build-tracker | http | service | Build Tracker dashboard |
| 50007 | vrijenattawar | http | service | Personal site (prod) |
| 50008 | thevibepill | http | service | The Vibe Pill (prod) |
| 50023 | product-walken-fit-staging | http | zosite | Walken Fit staging |
| 50100 | vrijenattawar-staging | http | zosite | Personal site staging (alt) |
| 50129 | travel-wrapped-2025 | http | service | Travel Wrapped 2025 |
| 50172 | fabregas-cannon-staging | http | service | Fabregas Cannon staging |
| 50215 | plaid-pfm | http | service | Plaid PFM dashboard |
| 50529 | n5-waitlist | http | service | N5 waitlist page |
| 50838 | store-va | http | zosite | Store (prod) |
| 50839 | store-va-staging | http | zosite | Store (staging) |
| 50840 | store-va | http | zosite | Store VA zosite |
| 51999 | zobridge-poller | http | service | Zobridge poller |
| 52125 | vrijenattawar | http | service | Personal site (prod) |
| 53828 | keanu-to-market | http | zosite | Keanu to Market zosite |
| 54179 | wheres-v | http | service+zosite | Where's V dashboard |
| 54591 | obsidian-web | http | service | Obsidian web interface |
| 54966 | x-radar | http | zosite | X Radar site |
| 57121 | zo-wrapped-2025 | http | zosite | Zo Wrapped 2025 |
| 58123 | zobridge-processor | http | service | Zobridge processor |
| 58124 | zobridge-health | http | service | Zobridge health monitor |
| 58222 | zobridge-relay | http | service | Zobridge relay |
| 58477 | streaming-player-setup | http | service | Streaming player setup |
| 58665 | store | http | service | Store site |
| 58667 | store-va | http | service | Store VA production |

## Next Available Ports by Range

- **n5-services (8763-8844)** — next: 8773
- **webhooks (8845-8899)** — next: 8849
- **mid-ephemeral (50000-51999)** — next: 50841
- **high-ephemeral (52000-58999)** — next: 53829

## Conflict History

| Date | Ports | Services | Resolution |
|------|-------|----------|------------|
| 2026-01-14 | 8765 | position-viz vs kondo-linkedin-webhook | Moved position-viz to 8790 |
| 2026-01-14 | 8766 | n5-bootstrap-support vs crm-webhook-renewal | Removed duplicate entry (crm-webhook-renewal retired) |
| 2026-01-30 | 8766 | n5-bootstrap-support vs crm-webhook-renewal | Deleted crm-webhook-renewal (svc_YLj0UE0nhUE) |
| 2026-01-30 | 8847 | careerspan-webhook vs careerspan-wh | Deleted careerspan-wh (svc_TArEMhXNEcI) |

---

**CLI Commands:**
```bash
python3 N5/scripts/port_registry.py check <port>    # Check if port is available
python3 N5/scripts/port_registry.py next [range]   # Get next available port
python3 N5/scripts/port_registry.py list           # List all allocated ports  
python3 N5/scripts/port_registry.py sync           # Sync from services + zosites
```
| 2026-02-20 | 8773 | zoseph-hotline-webhook | Zoseph (Vibe Thinker) hotline webhook — dedicated service, split from zo-hotline-webhook |
| 2026-02-20 | 4243 | zoren-hotline-webhook (relabeled) | Formerly zo-hotline-webhook → renamed for clarity |
