---
name: skill-export
description: |
  Export skills for distribution with proper separation between source (working) and export (distributable) versions.
  Generates bootloaders, config templates, webhook scaffolding, and pushes to GitHub.
  Source stays in Skills/, export goes to Projects/zo-<skill>, GitHub as vrijenattawar/zo-<skill>.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "2.0.0"
---

# Skill Export Pipeline

Export skills for sharing while maintaining clean separation between your working version and the distributable version.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SKILL EXPORT FLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   SOURCE (Working)              EXPORT (Distributable)          │
│   Skills/<skill>/         →     Projects/zo-<skill>/            │
│   ├── SKILL.md                  ├── README.md                   │
│   ├── scripts/                  ├── SKILL.md (sanitized)        │
│   └── (your configs)            ├── bootloader.py ★             │
│         │                       ├── config/                     │
│         │                       │   ├── settings.yaml.example   │
│         │                       │   └── webhook.yaml.example    │
│         │                       └── scripts/ (sanitized)        │
│         │                             │                         │
│         │ NEVER                       │                         │
│         │ MODIFIED                    ▼                         │
│         │                       GitHub: vrijenattawar/zo-<skill>│
│         │                                                       │
│         ▼                                                       │
│   Your actual working      Friend clones → runs bootloader →    │
│   skill with your          bootloader surveys their Zo →        │
│   personal configs         proposes plan → installs safely      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Full export: analyze → sanitize → bootloader → configs → GitHub
python3 Skills/skill-export/scripts/export_v2.py <skill-slug>

# Preview what would happen
python3 Skills/skill-export/scripts/export_v2.py <skill-slug> --dry-run

# Just analyze (see what would be extracted/templated)
python3 Skills/skill-export/scripts/export_v2.py <skill-slug> --analyze-only

# Export without pushing to GitHub
python3 Skills/skill-export/scripts/export_v2.py <skill-slug> --no-github
```

## What Gets Generated

### 1. Bootloader (`bootloader.py`)

A respectful installer that:
- **Surveys** the target Zo environment first
- **Detects** existing skills, folder conventions, potential conflicts
- **Proposes** an installation plan
- **Executes** only with explicit approval
- **Backs up** existing versions before installing

### 2. Config Templates

Extracted from hardcoded values in your source:

| Template | Contains |
|----------|----------|
| `settings.yaml.example` | Paths, integrations, general settings |
| `webhook.yaml.example` | Webhook config (if skill uses webhooks) |
| `blocks.yaml.example` | Custom processing options (if applicable) |

### 3. Sanitized Code

Automatic replacements:
- `/home/workspace/` → `./`
- `N5/` references → generic paths
- Email addresses → `<YOUR_EMAIL>`
- API keys → `<YOUR_API_KEY>`
- Zo webhook URLs → `<YOUR_WEBHOOK_URL>`
- `va.zo.computer` → `<YOUR_DOMAIN>`

### 4. Generated README

Auto-generated with:
- Installation instructions
- Required secrets list
- Required integrations list
- Webhook setup (if applicable)

## Analyze Mode

See what the export will extract without making changes:

```bash
python3 Skills/skill-export/scripts/export_v2.py meeting-ingestion --analyze-only
```

Output:
```
📊 ANALYSIS RESULTS
============================================================

Configurable Paths (12):
   • /home/workspace/Personal/Meetings/Inbox
   • /home/workspace/N5/config/drive_locations.yaml
   ...

Secrets/Env Vars (3):
   • ZO_CLIENT_IDENTITY_TOKEN
   • MEETING_WEBHOOK_SECRET
   • GOOGLE_DRIVE_FOLDER_ID

Integrations (2):
   • google_drive
   • google_calendar

Webhook Support: Yes
```

## Legacy Export (v1)

The original export script is still available for simple zip packaging:

```bash
python3 Skills/skill-export/scripts/export.py <skill-slug> --output-dir ./packages
```

This creates a sanitized zip but doesn't generate bootloaders or push to GitHub.

## Directory Convention

| Layer | Location | Purpose |
|-------|----------|---------|
| Source | `Skills/<skill>/` | Your working version (never touched) |
| Export | `Projects/zo-<skill>/` | Distributable version |
| GitHub | `vrijenattawar/zo-<skill>` | Public repo for sharing |

## For Recipients

When someone receives an exported skill:

```bash
# Clone
cd /home/workspace/Skills
git clone https://github.com/vrijenattawar/zo-<skill>.git <skill>

# Run bootloader (surveys environment first)
python3 <skill>/bootloader.py

# Or survey only
python3 <skill>/bootloader.py --survey

# Or preview installation
python3 <skill>/bootloader.py --execute --dry-run

# Actually install
python3 <skill>/bootloader.py --execute
```

The bootloader:
1. Scans their existing skills
2. Checks folder conventions
3. Detects potential conflicts
4. Shows recommendations
5. Only installs after approval

## Script Reference

| Script | Purpose |
|--------|---------|
| `export_v2.py` | Full export pipeline (recommended) |
| `export.py` | Legacy zip packaging |
| `sanitize.py` | Content sanitization |
| `generate_listing.py` | Store listing generation |
| `package.py` | Zip packaging |
