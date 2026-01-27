---
created: 2026-01-25
last_edited: 2026-01-25
version: 1.0
provenance: con_6OdklGGnWvmwq961
---

# Dynamic Survey Analyzer

Automated survey analysis system that triggers when new Fillout form submissions arrive, runs multi-stage analysis, and produces ongoing insights with visual dashboards.

## Purpose

Transform raw Fillout survey responses into actionable intelligence through:
- Automated interpretation framework generation
- Statistical analysis of response patterns
- Divergent thinking via Level Upper review
- Synthesis of findings with visualizations
- Ongoing tracking via scheduled updates

## When to Use

### Manual Trigger
When you have a Fillout form with responses and want comprehensive analysis:
```bash
# Run full analysis on a form
python3 Skills/dynamic-survey-analyzer/scripts/analyze.py --form-id <form_id>

# Generate just the dashboard
python3 Skills/dynamic-survey-analyzer/scripts/generate_dashboard.py --form-id <form_id>
```

### Auto-Trigger (Webhook)
The system automatically triggers analysis when:
1. First submission arrives for a new Fillout form
2. Threshold number of new submissions accumulate (configurable)

## Architecture

### Workers (Drops)
1. **D1.1 - Context & Hypothesis** (Researcher)
   - Ingests survey structure
   - Creates interpretation framework
   - Classifies questions (high-signal, demographic, open-ended)
   - Generates analysis hypotheses

2. **D1.2 - Analysis** (Builder)
   - Fetches all submissions via Fillout API
   - Computes response distributions
   - Identifies patterns and correlations
   - Extracts qualitative insights from open-ended text

3. **D1.3 - Level Upper** (Level Upper)
   - Reviews analysis for blind spots
   - Proposes counterintuitive insights
   - Challenges assumptions from D1.1's hypotheses

4. **D2.1 - Synthesis & Dashboard** (Builder)
   - Aggregates findings from D1.2 and D1.3
   - Generates ongoing analysis document (Markdown)
   - Creates Plotly interactive dashboard

### Output Artifacts
- `<form-id>_analysis.md` - Synthesized findings document
- `<form-id>_dashboard.py` - Plotly dashboard script
- `<form-id>_framework.json` - Interpretation framework (reusable)

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/fillout_client.py` | Multi-account Fillout API client with CLI |
| `scripts/generate_dashboard.py` | Create Plotly interactive dashboards |
| `scripts/level_upper_prompts.py` | Reusable divergent analysis prompt templates |
| `scripts/create_analysis_agent.py` | Helper to create scheduled analysis agents |

### fillout_client.py Usage
```bash
# List all forms from both accounts
python3 Skills/dynamic-survey-analyzer/scripts/fillout_client.py --list-forms

# Get form structure
python3 Skills/dynamic-survey-analyzer/scripts/fillout_client.py --form-structure <formId>

# Get all submissions
python3 Skills/dynamic-survey-analyzer/scripts/fillout_client.py --submissions <formId>

# Run full analysis with screening filter
python3 Skills/dynamic-survey-analyzer/scripts/fillout_client.py --analyze <formId> --screening <questionId> --screening-exclude "No"
```

### generate_dashboard.py Usage
```bash
# Generate dashboard from existing data.json
python3 Skills/dynamic-survey-analyzer/scripts/generate_dashboard.py <formId>

# Custom output path
python3 Skills/dynamic-survey-analyzer/scripts/generate_dashboard.py <formId> --output /path/to/dashboard.html
```

## Configuration

### Environment Variables
- `FILLOUT_SECRET_CAREERSPAN` - Fillout API secret (required)
- `ANALYSIS_THRESHOLD` - Submissions needed to trigger auto-analysis (default: 5)

### Form Configuration
Per-form overrides can be set in `config/forms/<form-id>.json`:
```json
{
  "exclude_questions": ["dGZw"],
  "custom_correlations": [
    {"q1": "sLMq", "q2": "qurD", "expected": "positive"}
  ],
  "theme_keywords": {
    "productivity": ["task", "workflow", "efficient", "save time"]
  }
}
```

## Integration Points

### Webhook Endpoint
`https://fillout-webhook-va.zocomputer.io/webhooks/fillout` receives Fillout submission notifications.

When a **new form** (not seen before) submits its first response:
1. Webhook detects new formId
2. Spawns background thread calling `/zo/ask` API
3. Analysis pipeline runs automatically
4. Results saved to `Datasets/survey-analyses/<formId>/`
5. V receives SMS summary when complete

Known forms are tracked in `Personal/Integrations/fillout/known_forms.json`.

### Scheduled Agents
A 30-day agent runs daily to:
- Check for new submissions on tracked forms
- Update analysis documents
- Refresh dashboard data

## Outputs

### Analysis Document Format
```markdown
# Survey Analysis: [Form Name]

**Analysis Date:** [Date]
**Submissions:** [N]

## Executive Summary
[3-5 bullet key takeaways]

## Response Demographics
[Profile of respondents]

## Key Findings
- [Finding 1]
- [Finding 2]

## Patterns & Correlations
[Statistical insights]

## Open-Ended Themes
[Qualitative analysis]

## Recommendations
[Actionable suggestions based on data]

## Appendix
- Full methodology
- Raw data summaries
```

### Dashboard Components
- Response funnel (completion rates)
- Question distribution charts
- Sentiment analysis (for emotional questions)
- Cross-tabulation heatmaps
- Theme word clouds
- Time-series trends

## References

- Fillout API: https://developer.fillout.com/
- Pulse build system: `Skills/pulse/SKILL.md`
