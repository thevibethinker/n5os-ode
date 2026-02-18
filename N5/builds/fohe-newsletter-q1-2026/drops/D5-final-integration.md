---
drop_id: D5
build_slug: fohe-newsletter-q1-2026
title: Final HTML Integration
type: code_build
persona: Builder
spawn_mode: manual
dependencies:
  - D3
  - D4
---

# Drop 5: Final Integration

## Task
Merge the HTML template with the content to create the final newsletter.

## Inputs to Read
1. `/home/workspace/N5/builds/fohe-newsletter-q1-2026/artifacts/newsletter_template.html` (Drop 3)
2. `/home/workspace/N5/builds/fohe-newsletter-q1-2026/artifacts/newsletter_content.md` (Drop 4)

## Deliverable
Create `/home/workspace/N5/builds/fohe-newsletter-q1-2026/artifacts/FOHE_NYC_Q1_2026_Newsletter.html`

## Instructions

1. **Copy the template** as your starting point

2. **Replace all template variables** with actual content:

| Variable | Content Source |
|----------|----------------|
| {{QUARTER}} | "Q1 2026" |
| {{CO_LEAD_NAMES}} | "Anna & Vrijen" |
| {{INTRO_TEXT}} | From newsletter_content.md section 3 |
| {{HIGHLIGHT_1_TITLE}} | From newsletter_content.md |
| {{HIGHLIGHT_1_TEXT}} | From newsletter_content.md |
| {{HIGHLIGHT_2_TITLE}} | From newsletter_content.md |
| {{HIGHLIGHT_2_TEXT}} | From newsletter_content.md |
| {{HIGHLIGHT_3_TITLE}} | From newsletter_content.md |
| {{HIGHLIGHT_3_TEXT}} | From newsletter_content.md |
| {{SURVEY_HEADLINE}} | From newsletter_content.md |
| {{SURVEY_INSIGHT_1}} | From newsletter_content.md |
| {{SURVEY_INSIGHT_2}} | From newsletter_content.md |
| {{SURVEY_QUOTE}} | From newsletter_content.md |
| {{EVENT_1_DATE}} | "Thursday, February 26" |
| {{EVENT_1_TITLE}} | "Happy Hour at The Half Pint" |
| {{EVENT_1_LOCATION}} | "76 West 3rd Street, NYC" |
| {{EVENT_1_CTA}} | "RSVP on Luma" |
| {{EVENT_1_URL}} | "https://luma.com/wzol16m6" |
| {{EVENT_2_DATE}} | "March 2026" |
| {{EVENT_2_TITLE}} | "Community Debate" |
| {{EVENT_2_LOCATION}} | "Details coming soon" |
| {{EVENT_2_CTA}} | "Stay tuned" |
| {{EVENT_3_DATE}} | "April 2026" |
| {{EVENT_3_TITLE}} | "FOHE NYC Hackathon" |
| {{EVENT_3_LOCATION}} | "Details coming soon" |
| {{EVENT_3_CTA}} | "Stay tuned" |

3. **Quality checks:**
- [ ] All placeholders replaced
- [ ] Feb 26 RSVP link is correct: https://luma.com/wzol16m6
- [ ] Purple branding consistent throughout
- [ ] HTML is valid (no unclosed tags)
- [ ] Mobile-responsive (test by resizing browser)
- [ ] Gmail-compatible (inline styles, table layout)

4. **Final polish:**
- Ensure subject line options are in HTML comments
- Add FOHE NYC logo reference (can use placeholder with purple background)
- Make CTA buttons prominent

## Success Criteria
- Single HTML file with all content integrated
- Renders beautifully in Gmail
- All event details accurate
- Template is reusable (variables can be swapped for Q2)
- Ready to send via Gmail

## Final Output
The HTML file at `/home/workspace/N5/builds/fohe-newsletter-q1-2026/artifacts/FOHE_NYC_Q1_2026_Newsletter.html` is the deliverable.
