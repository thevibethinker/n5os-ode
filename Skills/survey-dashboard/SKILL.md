---
name: survey-dashboard
description: |
  Generate live-updating Gamma dashboards from Fillout survey data. 
  Fetches responses, analyzes patterns, creates branded webpages with 
  configurable aesthetics. Supports scheduled regeneration and URL tracking.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: 1.0.0
---

# Survey Dashboard Skill

Generate beautiful, auto-updating dashboards from Fillout survey responses using Gamma's AI.

## Quick Start

```bash
# Generate a dashboard from a Fillout survey
python3 Skills/survey-dashboard/scripts/generate.py \
  --form-id jPQRwpT4nGus \
  --config Skills/survey-dashboard/assets/configs/zo-style.json

# Check current dashboard state
python3 Skills/survey-dashboard/scripts/generate.py --form-id jPQRwpT4nGus --status

# Force regeneration even if no new responses
python3 Skills/survey-dashboard/scripts/generate.py --form-id jPQRwpT4nGus --force
```

## Configuration

Each dashboard config is a JSON file in `assets/configs/`:

```json
{
  "name": "My Survey Dashboard",
  "theme": "breeze",
  "format": "webpage",
  "dimensions": "fluid",
  "images": "noImages",
  "survey_link": "https://short.link/my-survey",
  "branding": {
    "title_prefix": "Live Insights",
    "cta_text": "Take the Survey"
  },
  "question_mapping": {
    "tools": "question_id_for_tools",
    "challenge": "question_id_for_challenge",
    "sentiment": "question_id_for_sentiment"
  }
}
```

## Aesthetic Presets

| Preset | Theme | Style | Best For |
|--------|-------|-------|----------|
| `zo-style.json` | breeze | Soft blue, sky, white, minimal | Tech/SaaS audiences |
| `corporate.json` | chimney-smoke | Gray, professional, clean | Enterprise surveys |
| `vibrant.json` | gamma | Colorful, playful, bold | Consumer/B2C |
| `dark.json` | default-dark | Dark mode, modern | Developer audiences |

## Gamma Themes for Different Brands

The skill uses Gamma themes to match brand aesthetics:

| Brand Style | Recommended Themes |
|-------------|-------------------|
| **Zo Computer** | `breeze`, `dawn`, `commons` |
| **Minimalist** | `dawn`, `editoria`, `finesse` |
| **Corporate** | `chimney-smoke`, `blue-steel`, `founder` |
| **Playful** | `gamma`, `cornflower`, `electric` |
| **Elegant** | `creme`, `dune`, `cigar` |

## Scheduling Auto-Updates

Create a scheduled agent to regenerate dashboards:

```
RRULE: FREQ=HOURLY;INTERVAL=12;UNTIL=20260130T120000Z
Delivery: email

Instruction:
Run: python3 Skills/survey-dashboard/scripts/generate.py --form-id <FORM_ID> --config <CONFIG_PATH>
Email me the new dashboard URL and response count.
After the UNTIL date, delete this agent.
```

## How It Works

1. **Fetch** — Pulls responses from Fillout API
2. **Analyze** — Computes statistics, cross-tabs, identifies patterns
3. **Generate** — Creates markdown content from template
4. **Render** — Calls Gamma API to create branded webpage
5. **Track** — Stores URL history in state file

## State Management

Each form has a state file at `N5/data/survey_dashboard_<form_id>.json`:

```json
{
  "last_update": "2026-01-27T04:00:00",
  "last_gamma_url": "https://gamma.app/docs/abc123",
  "response_count": 12,
  "history": [...]
}
```

## Files

```
Skills/survey-dashboard/
├── SKILL.md              # This file
├── scripts/
│   └── generate.py       # Main generator script
├── assets/
│   └── configs/          # Aesthetic configuration presets
│       ├── zo-style.json
│       ├── corporate.json
│       └── vibrant.json
└── references/
    └── gamma-themes.md   # Theme reference guide
```

## Environment Variables

- `FILLOUT_SECRET_<ACCOUNT>` — Fillout API key (per account)
- `GAMMA_API_KEY` — Gamma API key

## Limitations

- **New URL each generation** — Gamma creates new URLs; can't update in place
- **Workaround**: Use short.io redirect that gets updated, or email latest URL
- **Fillout-specific** — Currently only supports Fillout surveys
