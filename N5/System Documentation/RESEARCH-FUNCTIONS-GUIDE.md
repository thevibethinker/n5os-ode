# Research Intelligence Functions - User Guide

**Version:** 1.0.1  
**Date:** 2025-10-09  
**Status:** Production-Ready

---

## Overview

Three integrated commands for your research intelligence workflow:

1. **meeting-prep-digest** - Daily automated meeting prep
2. **research-prompt-generator** - Generate deep research prompts
3. **extract-careerspan-insights** - Extract strategic insights

---

## Quick Start

### Daily Meeting Prep (Automated)

**Runs automatically at 06:00 ET every morning.**

```bash
# Manual trigger
meeting-prep-digest

# For specific date
meeting-prep-digest --date 2025-10-10

# Preview first
meeting-prep-digest --dry-run
```

**Output:** `N5/digests/daily-meeting-prep-YYYY-MM-DD.md`

**What you get:**
- External meetings only (filters out internal)
- Email history summary (past 90 days)
- Quick research (LinkedIn, company, news)
- Auto-detected entity types
- Context from meeting titles
- Clarification prompts for unclear attendees

---

### Deep Research Workflow (Manual)

**Step 1: Generate Research Prompt**

```bash
# Basic usage
research-prompt-generator --entity "Jane Doe" --type person

# With context and depth
research-prompt-generator \
  --entity "Sequoia Capital" \
  --type vc \
  --depth deep \
  --context "Series A investor evaluation"

# Topic research
research-prompt-generator \
  --entity "AI agent orchestration" \
  --type topic
```

**Entity Types:**
- `person` - Individual (executive, expert, contact)
- `company` - Business entity
- `nonprofit` - NGO, foundation
- `vc` - Venture capital firm
- `topic` - General-purpose research

**Depth Levels:**
- `light` - Quick overview (15-30 min, 500-1000 words)
- `standard` - Comprehensive (45-90 min, 1500-2500 words) **[default]**
- `deep` - Exhaustive (2-4 hours, 3000-5000 words)

**Step 2: Run Research Off-Platform**
1. Copy generated prompt (automatically copied to clipboard)
2. Paste into ChatGPT or Claude
3. Save research results to file

**Step 3: Extract Strategic Insights**

```bash
# Basic usage
extract-careerspan-insights --input research-results.txt

# With full context
extract-careerspan-insights \
  --input sequoia-research.txt \
  --entity "Sequoia Capital" \
  --analysis-type investment \
  --output Careerspan/Fundraising/sequoia-insights.md
```

**Analysis Types:**
- `partnership` - Partnership evaluation
- `investment` - Investor due diligence
- `customer` - Customer fit assessment
- `general` - Comprehensive assessment **[default]**

---

## Common Workflows

### Workflow 1: Meeting Prep
```bash
# Automated daily
06:00 ET → meeting-prep-digest runs
         → Check N5/digests/daily-meeting-prep-{today}.md
         → Review before meetings
```

### Workflow 2: Partnership Research
```bash
# Generate prompt
research-prompt-generator \
  --entity "Acme Corp" \
  --type company \
  --context "Q1 2026 partnership evaluation"

# Run on ChatGPT/Claude → save results

# Extract insights
extract-careerspan-insights \
  --input acme-research.txt \
  --analysis-type partnership
```

### Workflow 3: VC Fundraising Prep
```bash
# Generate deep research prompt
research-prompt-generator \
  --entity "Sequoia Capital" \
  --type vc \
  --depth deep

# Run on ChatGPT/Claude → save results

# Extract insights
extract-careerspan-insights \
  --input sequoia-research.txt \
  --entity "Sequoia Capital" \
  --analysis-type investment
```

### Workflow 4: Topic Exploration
```bash
# Generate topic research prompt
research-prompt-generator \
  --entity "AI coaching effectiveness" \
  --type topic \
  --depth standard

# Run on ChatGPT/Claude → save results

# Extract insights
extract-careerspan-insights \
  --input topic-research.txt \
  --analysis-type general
```

---

## Tips & Best Practices

### Meeting Prep Digest
- Review digest before your first meeting
- Flag unclear attendees immediately
- Add manual notes to digest as needed
- Keep digests for reference (automatically saved)

### Research Prompt Generator
- Use `--dry-run` to preview before copying
- Add specific context for better research
- Standard depth is usually sufficient
- Save prompts if you'll reuse them

### Insights Extractor
- Always provide entity name (even if obvious)
- Choose correct analysis type for focused insights
- Use `--dry-run` to preview before saving
- Save to descriptive paths for organization

### General Tips
- All commands support `--dry-run` for safe testing
- ET timezone used throughout (matches your preferences)
- Error messages are informative - read them
- Commands registered in N5 system (tab completion works)

---

## Troubleshooting

### "Entity name cannot be empty"
**Solution:** Provide a valid entity name (min 2 characters)

### "Invalid date format"
**Solution:** Use YYYY-MM-DD format or "today"

### "Input file not found"
**Solution:** Check file path, use absolute or correct relative path

### "Clipboard copy unavailable"
**Solution:** Install pyperclip (`pip install pyperclip`) or copy from stdout

### "Using mock data" warnings
**Expected:** API integrations are stubbed, will use real data when integrated

---

## Current Limitations (With Workarounds)

### Meeting Prep Digest Uses Mock Data
**Status:** Functional workflow, mock data  
**Workaround:** Review format and structure now, real data coming  
**Timeline:** API integration when needed (~2-3 hours)

### Insight Extraction Uses Heuristics
**Status:** Produces structured output, simplified analysis  
**Workaround:** Works for basic categorization, upgrade for deeper analysis  
**Timeline:** LLM integration when needed (~1 hour)

---

## Files Reference

**Commands:**
- `file 'N5/commands/meeting-prep-digest.md'`
- `file 'N5/commands/research-prompt-generator.md'`
- `file 'N5/commands/extract-careerspan-insights.md'`

**Scripts:**
- `file 'N5/scripts/meeting_prep_digest.py'`
- `file 'N5/scripts/research_prompt_generator.py'`
- `file 'N5/scripts/careerspan_insights_extractor.py'`

**Configuration:**
- `file 'N5/config/commands.jsonl'` (registered)

**Output:**
- `N5/digests/` (meeting prep digests)
- Various (insights extracted to specified locations)

---

## Support

**For issues:** Check `file 'N5/System Documentation/RESEARCH-FUNCTIONS-GUIDE.md'` (this file)

**For enhancements:** Update scripts in `N5/scripts/` or commands in `N5/commands/`

**For scheduling:** Use `list_scheduled_tasks` to view/manage

---

**Last Updated:** 2025-10-09  
**Version:** 1.0.1  
**Maintained by:** N5 OS
