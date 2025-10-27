# Records/Surveys - Tally Survey Data Storage

**Created:** 2025-10-26  
**Purpose:** Storage and staging for Tally survey-related data  
**System:** N5 OS / Records Layer

---

## Overview

This directory serves as the **staging and working area** for Tally survey operations, following N5's Records layer philosophy: raw intake → process → Knowledge.

---

## Directory Structure

```
Records/Surveys/
├── README.md           # This file
├── incoming/           # New survey specifications and imports
├── drafts/             # Draft survey metadata before publication
├── published/          # Metadata for published surveys
├── responses/          # Downloaded response data (CSV, JSON)
└── exports/            # Generated reports and analyses
```

---

## Data Flow

### 1. Incoming (Specifications)
**Purpose:** Store survey requirements before creation

**Format:** Markdown files with YAML frontmatter
```yaml
---
title: Customer Feedback Survey
status: pending
requested: 2025-10-26T15:00:00Z
fields:
  - name: required
  - email: required
  - rating: 1-5
  - comments: optional
---

Additional context and requirements...
```

**When to use:** Before creating survey, capture requirements here

---

### 2. Drafts (Unpublished)
**Purpose:** Metadata for surveys created but not yet published

**Format:** JSON snapshot
```json
{
  "form_id": "abc123",
  "title": "Test Survey",
  "status": "DRAFT",
  "created": "2025-10-26T15:00:00Z",
  "edit_url": "https://tally.so/forms/abc123/edit",
  "public_url": "https://tally.so/r/abc123",
  "specification": "incoming/customer-feedback-spec.md"
}
```

---

### 3. Published (Active Surveys)
**Purpose:** Metadata for live surveys collecting responses

**Format:** JSON with tracking data
```json
{
  "form_id": "wdeWZD",
  "title": "Future of Careertech Cartel Interest Form",
  "status": "PUBLISHED",
  "created": "2025-07-24T06:51:43Z",
  "published": "2025-07-24T07:00:00Z",
  "public_url": "https://tally.so/r/wdeWZD",
  "edit_url": "https://tally.so/forms/wdeWZD/edit",
  "submissions_count": 8,
  "last_checked": "2025-10-26T20:00:00Z",
  "specification": "../incoming/careertech-spec.md",
  "purpose": "Collect interest for Future of Careertech Cartel initiative"
}
```

---

### 4. Responses (Downloaded Data)
**Purpose:** Store downloaded response data for analysis

**Formats:**
- `{form-id}_responses_{timestamp}.csv` - Raw CSV export
- `{form-id}_responses_{timestamp}.json` - API response data
- `{form-id}_responses_latest.csv` - Symlink to latest

**Organization:**
```
responses/
├── wdeWZD/
│   ├── wdeWZD_responses_2025-10-26.csv
│   ├── wdeWZD_responses_2025-10-26.json
│   └── wdeWZD_responses_latest.csv -> wdeWZD_responses_2025-10-26.csv
└── 3x8yoy/
    ├── 3x8yoy_responses_2025-10-26.csv
    └── 3x8yoy_responses_latest.csv -> ...
```

---

### 5. Exports (Analysis & Reports)
**Purpose:** Generated analyses, summaries, and reports from survey data

**Examples:**
- `customer-feedback-summary-2025-10.md` - Monthly summary
- `nps-analysis-q4.md` - Quarterly NPS analysis
- `satisfaction-trends.csv` - Trend analysis
- `top-complaints.md` - Thematic analysis

---

## Processing Workflow

### Standard Flow
```
1. Specification → incoming/
2. Create via API → Draft snapshot → drafts/
3. Publish → Move to published/
4. Monitor → Update submission count
5. Download responses → responses/{form-id}/
6. Analyze → Generate reports → exports/
7. Final insights → Promote to Knowledge/integrations/tally/
```

### Retention Policy

**Incoming:** Delete after survey created  
**Drafts:** Delete after published OR archived if abandoned  
**Published:** Keep while survey is active  
**Responses:** Keep 90 days, then archive or promote to Knowledge  
**Exports:** Keep 90 days, archive or promote valuable analyses

---

## Integration with N5

### Knowledge Layer
After analysis, promote to:
- `Knowledge/integrations/tally/` - System knowledge about Tally operations
- `Knowledge/insights/` - Insights derived from survey data
- `Knowledge/customer/` - Customer intelligence from surveys

### Lists Layer
Track survey-related actions:
- `Lists/surveys.jsonl` - Active survey tracking
- `Lists/follow-ups.jsonl` - Response follow-ups needed

### Commands
Access via registered commands:
- `tally-create` - Create from specification
- `tally-list` - List all surveys
- `tally-get` - Get survey details
- `tally-submissions` - Download responses
- `tally-analyze` - Generate analysis (future)

---

## File Naming Conventions

**Specifications:** `{purpose}-spec.md` (e.g., `customer-feedback-spec.md`)  
**Metadata:** `{form-id}.json` (e.g., `wdeWZD.json`)  
**Responses:** `{form-id}_responses_{YYYY-MM-DD}.{ext}`  
**Exports:** `{purpose}-{type}-{YYYY-MM}.md` (e.g., `feedback-summary-2025-10.md`)

---

## Common Operations

### Create Survey from Spec
```bash
# 1. Write spec to incoming/
# 2. Create via Zo conversation or:
python3 N5/scripts/tally_manager.py create \
  --title "Survey Title" \
  --spec incoming/spec.md

# 3. Metadata automatically saved to drafts/
```

### Download Responses
```bash
python3 N5/scripts/tally_manager.py submissions \
  --form-id wdeWZD \
  --output responses/wdeWZD/wdeWZD_responses_$(date +%Y-%m-%d).csv
```

### List Active Surveys
```bash
python3 N5/scripts/tally_manager.py list \
  --status PUBLISHED
```

---

## Backup & Recovery

**API Key:** Stored securely in `N5/config/tally_api_key.env` (git-ignored)  
**Metadata:** JSON files in published/ serve as backup  
**Responses:** Keep local copies in responses/  
**Recovery:** Use metadata files to reconstruct if needed

---

## Security

- ✅ API key git-ignored
- ✅ Response data not committed
- ✅ Personal data in responses/ (local only)
- ⚠️ Export files may contain sensitive data (review before committing)

---

## See Also

- `file 'Documents/tally-system-overview.md'` - Complete system guide
- `file 'Knowledge/integrations/tally-integration.md'` - Integration knowledge
- `file 'N5/scripts/tally_manager.py'` - Main tool
- `file 'N5/config/commands.jsonl'` - Registered commands

---

**Status:** Active  
**Maintainer:** N5 OS  
**Last Updated:** 2025-10-26
