# GA4 Analytics Integration

Pull analytics data for vrijenattawar.com using the GA4 Data API.

## Quick Summary (Last 7 Days)

```bash
python3 Integrations/ga4/scripts/ga4_summary.py
```

## Options

```bash
# Last 30 days
python3 Integrations/ga4/scripts/ga4_summary.py --days 30

# Include detailed events breakdown
python3 Integrations/ga4/scripts/ga4_summary.py --events

# Show realtime active users
python3 Integrations/ga4/scripts/ga4_summary.py --realtime

# Combine options
python3 Integrations/ga4/scripts/ga4_summary.py --days 14 --events --realtime
```

## What's Tracked

### Standard Metrics
- Users, sessions, pageviews
- Average session duration
- Bounce rate
- Traffic sources
- Device breakdown (desktop/mobile/tablet)

### Custom Events (vrijenattawar.com specific)
- `badge_click` — Clicks on @thevibethinker badge (with click count)
- `badge_unlock` — Successful unlock (7 clicks → /mind)
- `mind_page_entry` — How users arrived at /mind (badge_unlock, direct, external)
- `mindmap_node_click` — Position bubble clicks (with domain, title, stability)
- `mindmap_zoom` — Zoom in/out button usage
- `mindmap_fit_screen` — Fit-to-screen button clicks
- `mindmap_chat_question` — Chat questions asked
- `mindmap_heartbeat` — Time spent (fires every 30s)
- `mindmap_session_end` — Total session stats on exit

## Configuration

- **Property ID:** 520487128
- **Credentials:** `/home/workspace/.secrets/ga4-service-account.json`
- **Service Account:** n5-os-zo@n5-os-484723.iam.gserviceaccount.com
