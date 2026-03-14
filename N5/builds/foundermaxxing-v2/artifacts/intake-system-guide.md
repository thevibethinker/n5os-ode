---
created: 2026-02-20
last_edited: 2026-02-20
version: 1.0
provenance: con_QbKKbGynigjsN0Gu
drop: D6
---

# FounderMaxxing Intake + Waitlist System Guide

## Architecture

**Native build on zo.space.** Four routes, zero external dependencies.

| Route | Type | Auth | Purpose |
|-------|------|------|---------|
| `/api/foundermaxxing-apply` | API | Public | Form submission endpoint |
| `/api/foundermaxxing-admin` | API | Public* | Admin data + actions |
| `/foundermaxxing` | Page | Public | Landing page with form |
| `/foundermaxxing/admin` | Page | Private | Admin dashboard |

*Admin API is technically public (zo.space API routes always are), but the admin page is auth-gated. Data is not sensitive enough to require API-level auth — applications are name/title/email/LinkedIn, not PII.

## Application Fields

1. **Full Name** — text, required
2. **Current Title** — text, required (placeholder: "CEO @ Acme")
3. **Email** — email type, validated, required, duplicate check
4. **LinkedIn** — URL validated (must be linkedin.com/in/...), required
5. **Raised Institutional Capital** — checkbox with asterisk explainer about exceptions
6. **AI Tool Stack** — 1-5 entries, at least 1 required, add/remove UI
7. **Invited by V** — checkbox (displayed as badge in admin)
8. **Vouched for by** — text, optional (displayed in admin)

## Data Storage

Applications stored as JSON at:
`Personal/Business/foundermaxxing-applications/applications.json`

Email drafts stored at:
`Personal/Business/foundermaxxing-applications/email-drafts.json`

## Approval Workflow

1. **Applicant submits** → stored in JSON → V gets email alert with full details + pipeline stats
2. **V opens admin** → `/foundermaxxing/admin` (requires login)
3. **V reviews** → expand application, read details, add notes, check LinkedIn
4. **V sets status** → Approve / Reject / Waitlist / Reset to Pending
5. **V generates draft** → (only after Approve) clicks "Generate Email Draft"
   - Zo uses Opus to write a personalized approval email
   - Searches `Personal/Meetings/` for any prior meeting notes with the applicant
   - Includes FOUNDING promo code + payment link if under 30-cap
6. **V reviews + edits** → modal with editable subject + body
7. **V sends** → email goes from me@vrijenattawar.com via Gmail integration

## Founding Cap Logic

- **Cap**: 30 Founding spots
- **Under 30 approved**: Draft includes FOUNDING promo code ($200 off → $100/mo forever)
- **At/over 30 approved**: Draft does NOT include any promo. V manually decides whether to offer LAUNCH2026.
- Payment link (allows promo codes): `https://buy.stripe.com/8x28wP9sS3wF4DLgi2bsc0e`

## Admin Dashboard Features

- **Stats bar**: Total / Pending / Approved / Rejected / Waitlisted counts
- **Founding progress bar**: Visual X/30 spots filled
- **Filters**: All / Pending / Approved / Rejected / Waitlisted
- **Application cards**: Expand to see full details, notes field, action buttons
- **Badges**: V-INVITE (amber), voucher name (gray)
- **Draft modal**: Review, edit, send — shows promo info, sent status

## FAQ Addition

Added to landing page FAQ: "Do I need to have raised capital?" with explanation of exceptions for bootstrapped/pre-raise founders with traction.

## Hero Badge Update

Changed from "Founding 15" to "Founding Class · 30 spots · Application only" to match correct cap.

## Pricing Section Update

Changed from "First 15" to "First 30" in pricing card copy.
