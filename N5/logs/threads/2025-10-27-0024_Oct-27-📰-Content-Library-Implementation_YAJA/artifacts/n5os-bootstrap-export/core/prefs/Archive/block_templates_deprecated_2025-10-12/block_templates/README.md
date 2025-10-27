# Block Templates

Templates for generating core meeting intelligence blocks.

## Structure

```
block_templates/
├── internal/      # Templates for internal-only meetings
│   ├── action-items.template.md
│   ├── decisions.template.md
│   ├── key-insights.template.md
│   ├── debate-points.template.md
│   ├── memo.template.md
│   └── REVIEW_FIRST.template.md
└── external/      # Templates for meetings with external stakeholders
    ├── action-items.template.md
    ├── decisions.template.md
    ├── key-insights.template.md
    ├── stakeholder-profile.template.md
    ├── follow-up-email.template.md
    └── REVIEW_FIRST.template.md
```

## Usage

Templates use placeholder variables in `{{VARIABLE_NAME}}` format.

The `meeting_core_generator.py` script:
1. Loads appropriate template based on meeting type (internal/external)
2. Uses LLM to extract content from transcript
3. Generates final markdown files with real content

## Template Variables

Common variables across templates:
- `{{DATE}}` - Meeting date (YYYY-MM-DD)
- `{{PARTICIPANTS}}` - Participant names/emails
- `{{MEETING_TYPE}}` - internal or external
- `{{STAKEHOLDER_NAME}}` - Primary external stakeholder name
- `{{GENERATED_TIMESTAMP}}` - ISO timestamp of generation

Block-specific variables defined in each template file.
