---
description: 'Command: sync-to-drive'
tool: true
tags:
- sync
- drive
- knowledge
- external
- automation
---
# Sync Knowledge to Google Drive

Sync all Careerspan and Vrijen-related knowledge files to Google Drive for use with external AI tools (Zapier, Make, etc.).

## What It Does

Syncs the following knowledge to a "Careerspan Knowledge Sync" folder on Google Drive:

**Stable Knowledge:**
- Biographical info (bio.md)
- Company timeline
- Company information (overview, history, strategy, principles, pricing)
- Glossary

**Semi-Stable Knowledge:**
- Current metrics
- Product state
- Team composition
- Positioning

**Strategic Knowledge:**
- Market hypotheses
- Product hypotheses
- GTM hypotheses
- Business model hypotheses
- Fundraising hypotheses

**Market Intelligence:**
- Community-driven hiring analysis
- Recruiting industry analysis

**Operational:**
- Company identity and aliases

## Sync Strategy

- **Delete & Recreate:** Each sync deletes the entire Drive folder and rebuilds it
- **Exact Mirror:** Folder structure matches local organization
- **Markdown Format:** All files remain as `.md` for universal compatibility
- **23 Files Total:** ~148KB of knowledge

## Usage

```bash
# Dry run (preview only)
python3 /home/workspace/N5/scripts/sync_to_drive.py

# Execute sync
python3 /home/workspace/N5/scripts/sync_to_drive.py --execute
```

## Drive Folder Structure

```
Careerspan Knowledge Sync/
├── stable/
│   ├── bio.md
│   ├── careerspan-timeline.md
│   ├── company.md
│   ├── glossary.md
│   ├── sources.md
│   ├── zodrops-index.md
│   └── company/
│       ├── overview.md
│       ├── principles.md
│       ├── strategy.md
│       ├── history.md
│       └── pricing.md
├── semi_stable/
│   ├── current_metrics.md
│   ├── positioning_current.md
│   ├── product_current.md
│   └── team_current.md
├── hypotheses/
│   ├── market_hypotheses.md
│   ├── fundraising_hypotheses.md
│   ├── gtm_hypotheses.md
│   ├── business_model_hypotheses.md
│   └── product_hypotheses.md
├── market/
│   ├── community_driven_hiring.md
│   └── recruiting_industry.md
└── company_ops/
    └── careerspan.md
```

## Automation Integration

This sync is designed to be triggered:
1. **Manual:** Via this command
2. **On-demand:** After significant knowledge updates
3. **Conversation-end:** Integrated into conversation-end workflow (future)
4. **Git operations:** Integrated into git-check workflow (future)

## Using with Zapier/External AI

Once synced, the Drive folder can be used as a knowledge source in:
- Zapier AI Actions (custom prompts with knowledge base)
- Make.com scenarios
- Custom GPT configurations
- Any tool that supports Drive folder knowledge sources

The "delete & recreate" approach ensures external tools always have the latest, clean version of your knowledge without stale file issues.

## Configuration

Edit `/home/workspace/N5/config/drive_sync.json` to:
- Add/remove directories to sync
- Change folder name
- Modify include/exclude patterns
- Adjust safety limits

## Maintenance

**When to sync:**
- After updating company strategy docs
- After major changes to stable knowledge
- Before building external automations that need current data
- Monthly as part of knowledge hygiene

**What's NOT synced:**
- N5 OS system files
- Architectural principles
- Personal notes
- CRM data
- Meeting records (unless explicitly added to config)

---

**Version:** 1.0  
**Created:** 2025-10-16  
**Drive Folder:** [Careerspan Knowledge Sync](https://drive.google.com/drive/folders/1xCg5XPFScVoneqZK0GRvURkzvKFV0AcW)
