---
drop_id: D3
build_slug: fohe-newsletter-q1-2026
title: HTML Email Template Design
type: code_build
persona: Builder
spawn_mode: auto
---

# Drop 3: Email Template Design

## Task
Create a reusable, responsive HTML email template for FOHE NYC newsletters.

## Design Reference
- **Logo:** Purple gradient FOHE (see `/home/.z/chat-images/image (562).png`)
- **Primary color:** Purple/violet (#8B5CF6 or similar gradient)
- **Background:** White (#FFFFFF)
- **Text:** Dark gray (#1F2937)
- **Accent:** Light purple background for highlights (#F3E8FF)

## Requirements

### Technical
- Gmail-compatible (table-based layout, inline styles)
- Max width: 600px
- Responsive (mobile-friendly)
- Valid HTML

### Sections
1. **Header**
   - FOHE logo (placeholder img with purple background)
   - Newsletter title: "FOHE NYC {{QUARTER}} Newsletter"
   - Subtitle: "The Future of Higher Education"

2. **Intro Section**
   - "A note from your co-leads"
   - {{INTRO_TEXT}} placeholder

3. **Community Highlights**
   - Section title: "What's Been Happening"
   - 3 highlight cards with {{HIGHLIGHT_1_TITLE}}, {{HIGHLIGHT_1_TEXT}}, etc.

4. **Survey Insights**
   - Section title: "What You Told Us"
   - {{SURVEY_STATS}}, {{SURVEY_QUOTE}}

5. **Upcoming Events**
   - Section title: "Coming Up"
   - 3 event cards with: date, title, description, CTA button
   - {{EVENT_1_DATE}}, {{EVENT_1_TITLE}}, {{EVENT_1_LOCATION}}, {{EVENT_1_CTA}}

6. **Footer**
   - Join Slack CTA
   - Social links placeholder
   - FOHE NYC branding
   - Unsubscribe placeholder

### Template Variables (use {{VAR}} syntax)
```
{{QUARTER}}
{{CO_LEAD_NAMES}}
{{INTRO_TEXT}}
{{HIGHLIGHT_1_TITLE}}
{{HIGHLIGHT_1_TEXT}}
{{HIGHLIGHT_2_TITLE}}
{{HIGHLIGHT_2_TEXT}}
{{HIGHLIGHT_3_TITLE}}
{{HIGHLIGHT_3_TEXT}}
{{SURVEY_HEADLINE}}
{{SURVEY_INSIGHT_1}}
{{SURVEY_INSIGHT_2}}
{{SURVEY_QUOTE}}
{{EVENT_1_DATE}}
{{EVENT_1_TITLE}}
{{EVENT_1_LOCATION}}
{{EVENT_1_CTA}}
{{EVENT_1_URL}}
{{EVENT_2_DATE}}
{{EVENT_2_TITLE}}
{{EVENT_2_LOCATION}}
{{EVENT_2_CTA}}
{{EVENT_3_DATE}}
{{EVENT_3_TITLE}}
{{EVENT_3_LOCATION}}
{{EVENT_3_CTA}}
```

## Deliverable
Create `/home/workspace/N5/builds/fohe-newsletter-q1-2026/artifacts/newsletter_template.html`

## Success Criteria
- Renders correctly in Gmail
- Mobile responsive
- Purple branding consistent
- All sections have clear placeholders
- Ready for Drop 5 to populate
