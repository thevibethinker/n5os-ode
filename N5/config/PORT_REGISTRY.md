---
created: 2026-01-14
last_edited: 2026-01-14
version: 1.1
provenance: con_UFjyhy1uUH8jHz31
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
| 8000 | n5-metrics-collector | http | service | N5 metrics collection |
| 8010 | workout-dashboard | http | service | Workout tracker dashboard |
| 8080 | conversation-installer | http | service | Conversational API package |
| 8081 | fitbit-legal | http | service | Fitbit legal page |
| 8123 | va-http | http | service | General HTTP file server |
| 8384 | syncthing | http | service | Syncthing sync service |
| 8420 | fireflies-webhook | http | service | Fireflies meeting webhook |
| 8421 | fireflies-poller | http | service | Fireflies API poller |
| 8763 | fathom-webhook | http | service | Fathom meeting webhook |
| 8765 | kondo-linkedin-webhook | http | service | Kondo LinkedIn webhook |
| 8766 | n5-bootstrap-support | http | service | N5 bootstrap support |
| 8767 | crm-webhook-health | tcp | service | CRM calendar health monitor |
| 8768 | n5-advisor | http | service | N5 bootstrap advisor |
| 8769 | n5-conversation-api | http | service | N5 conversational API |
| 8770 | zo-n8n-api | http | service | Zo-n8n integration API |
| 8771 | action-approvals-monitor | http | service | Action approvals monitor |
| 8772 | task-completion-detector | http | service | Task completion detector |
| 8775 | slack-bot | http | service | Slack bot receiver |
| 8778 | crm-calendar-webhook | http | service | CRM calendar webhook handler |
| 8790 | position-viz | http | service | Position visualization |
| 8845 | fillout-webhook | http | service | Fillout form webhook |
| 8900 | zapier-webhook | http | service | Zapier webhook receiver |
| 9090 | prometheus | http | service | Prometheus monitoring |
| 19999 | semantic-reindex | tcp | service | Semantic reindex service |
| 50000 | vrijenattawar-staging | http | zosite | Personal site staging |
| 50100 | vrijenattawar-staging | http | zosite | Personal site staging (alt) |
| 50129 | travel-wrapped-2025 | http | service | Travel Wrapped 2025 |
| 50140 | meeting-health-dashboard | http | service | Meeting health dashboard |
| 50172 | fabregas-cannon-staging | http | service | Fabregas Cannon staging |
| 50529 | n5-waitlist | http | service | N5 waitlist page |
| 50838 | store-va | http | zosite | Store (prod) |
| 50839 | store-va-staging | http | zosite | Store (staging) |
| 51999 | zobridge-poller | http | service | ZoBridge poller |
| 52125 | vrijenattawar | http | service | Personal site (prod) |
| 52154 | zo-stream | http | service | Zo streaming player |
| 54179 | wheres-v | http | service+zosite | Where's V dashboard |
| 54591 | obsidian-web | http | service | Obsidian web interface |
| 54966 | x-radar | http | zosite | X Radar site |
| 57121 | zo-wrapped-2025 | http | zosite | Zo Wrapped 2025 |
| 58123 | zobridge-processor | http | service | ZoBridge processor |
| 58124 | zobridge-health | http | service | ZoBridge health monitor |
| 58222 | zobridge-relay | http | service | ZoBridge relay |
| 58477 | streaming-player-setup | http | service | Streaming player setup |
| 58665 | store | http | service | Store site |

## Next Available Ports by Range

- **n5-services (8763-8844)** — next: 8791
- **webhooks (8845-8899)** — next: 8846
- **mid-ephemeral (50000-51999)** — next: 50530
- **high-ephemeral (52000-58999)** — next: 52155

## Conflict History

| Date | Ports | Services | Resolution |
|------|-------|----------|------------|
| 2026-01-14 | 8765 | position-viz vs kondo-linkedin-webhook | Moved position-viz to 8790 |
| 2026-01-14 | 8766 | n5-bootstrap-support vs crm-webhook-renewal | Removed duplicate entry (crm-webhook-renewal retired) |

---

**CLI Commands:**
```bash
python3 N5/scripts/port_registry.py check <port>    # Check if port is available
python3 N5/scripts/port_registry.py next [range]   # Get next available port
python3 N5/scripts/port_registry.py list           # List all allocated ports  
python3 N5/scripts/port_registry.py sync           # Sync from services + zosites
```


