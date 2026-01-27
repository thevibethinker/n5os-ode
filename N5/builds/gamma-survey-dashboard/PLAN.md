---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_8niRcrOEmKFqImvb
---

# Build Plan: Gamma Survey Dashboard

## Objective
Create a Gamma-powered dashboard displaying the "Next Play: Fundamentals of AI Productivity" survey analysis, with automated daily regeneration through Jan 30.

## Checklist

### Phase 1: Infrastructure Setup
- [ ] D1.1: Create Gamma generation script that transforms analysis.md → Gamma input
- [ ] D1.2: Test initial Gamma generation with survey data

### Phase 2: Scheduled Regeneration
- [ ] D2.1: Create scheduled agent for daily Gamma regeneration (runs through Jan 30)
- [ ] D2.2: Set up URL tracking system (since each generation creates new URL)

### Phase 3: Documentation & Handoff
- [ ] D3.1: Document the system, create usage guide

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Data Source                                                 │
│ Datasets/survey-analyses/jPQRwpT4nGus/analysis.md           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Transformation Script                                        │
│ N5/scripts/gamma_survey_generator.py                        │
│ - Reads analysis.md                                          │
│ - Extracts key metrics + visualizations                      │
│ - Formats for Gamma inputText with data tables              │
│ - Calls Gamma API → returns URL                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Output                                                       │
│ - Gamma webpage URL (changes each regeneration)             │
│ - URL history tracked in artifacts/url_history.json         │
│ - Latest URL emailed to V after each regeneration           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Scheduled Agent (Daily 8am ET through Jan 30)               │
│ - Runs gamma_survey_generator.py                             │
│ - Emails V the new dashboard URL                             │
│ - Stops after Jan 30                                         │
└─────────────────────────────────────────────────────────────┘
```

## Gamma Best Practices for Data Dashboards

Based on API capabilities:

1. **Format**: `webpage` — best for dashboard-style continuous scroll
2. **Text Mode**: `preserve` — keep exact data/numbers from analysis
3. **Amount**: `detailed` — include all metrics
4. **Card Dimensions**: `fluid` — adapt to content
5. **Images**: `pictographic` — clean icons for data visualization
6. **Theme**: Professional/minimal (e.g., `default-light` or `blue-steel`)

## Input Text Strategy

The `inputText` should be structured markdown that Gamma can transform into cards:

```markdown
# Survey Dashboard: AI Productivity Workshop
**Last Updated:** [timestamp]
**Total Responses:** [N]

## Executive Summary
[Key findings as bullet points]

## Key Metrics
| Metric | Value |
|--------|-------|
| ... | ... |

## AI Tool Adoption
[Chart-friendly data]

## Biggest Challenges
[Percentages with context]

## Recommendations
[Actionable items]

## Methodology
[Data source attribution]
```

## Affected Files

### Created
- `N5/scripts/gamma_survey_generator.py` — Main transformation + generation script
- `N5/builds/gamma-survey-dashboard/artifacts/url_history.json` — URL tracking
- Scheduled agent for daily regeneration

### Read
- `Datasets/survey-analyses/jPQRwpT4nGus/analysis.md` — Source data

## Streams

### Stream 1: Core Build (Parallel)
- **D1.1**: Transformation script (Python)
- **D1.2**: Initial generation test

### Stream 2: Automation (Sequential after S1)
- **D2.1**: Scheduled agent setup
- **D2.2**: URL tracking + notification system

### Stream 3: Documentation (After S2)
- **D3.1**: Usage documentation

## Success Criteria

1. ✅ Gamma webpage generated with all survey data
2. ✅ Data tables display correctly
3. ✅ Daily regeneration works
4. ✅ V receives email with latest URL
5. ✅ System stops after Jan 30

## Notes

- **URL Changes**: Each Gamma regeneration creates a new URL. We'll track history and always email the latest.
- **Alternative**: Could use `from-template` if we create a template first, but `generate` is simpler for this use case.
- **Credits**: Each generation costs credits. Daily for 5 days = 5 generations.
