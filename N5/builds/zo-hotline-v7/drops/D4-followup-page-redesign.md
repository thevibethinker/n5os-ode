---
created: 2026-02-19
drop_id: D4
stream: S3
title: Follow-Up Page Redesign
status: pending
depends_on: []
provenance: con_tdpDMlVT0VZmXDPS
---

# D4: Follow-Up Page Redesign

## Objective

Enhance the follow-up page template to be a real product touchpoint — branded, community-connected, with V's personal presence. Make callers feel like they're joining something, not just getting a summary.

## Deliverables

1. **Updated `generateFollowUpPageSource`** in `hotline-webhook.ts`:
   - **Header**: Vibe Thinker Hotline branding with V's insignia logo (asset: `/images/logo-v-white-insignia.png` already in zo.space)
   - **Community section**: Discord CTA ("Join the Zo Community" → https://discord.gg/zocomputer) with description of what they'll find there
   - **Social links footer**: V's presence:
     - X/Twitter: https://x.com/vibethinker (or V's handle — need to confirm)
     - LinkedIn: https://linkedin.com/in/vrijenattawar
     - Personal site: https://vrijenattawar.com
     - Zo Computer: https://zocomputer.com
   - **Footer note**: Keep the "This page was built by Zo Computer after your call — in real-time" but make it more impactful
   - **Call-back CTA**: "Call back: +1 (857) 317-8492" as a clickable tel: link
   - **Visual polish**: Warm amber accent theme, clean sections, mobile-first

2. **Data structure update** — Add to `FollowUpPageData` interface:
   - `socialLinks`: array of { platform, url, label }
   - `communityLinks`: already exists, enhance defaults
   - `showLogo`: boolean (default true)
   - `callbackNumber`: string

## Constraints

- Page must work on mobile (callers get this via SMS)
- Logo loaded from zo.space asset (already uploaded)
- Keep page fast — no external font loads, no heavy assets
- All URLs must be in the existing EMAIL_WHITELIST or added to it

## Questions for V (to be answered during build or defaulted)

- V's X handle — defaulting to @vibethinker, needs confirmation
- Any other socials to include?

## Deposit

`deposits/D4-followup-page-redesign.json` with:
- `sections_added`: list of new page sections
- `social_links`: list of included social links
- `files_modified`: list of changed files
- `preview_url`: URL of test page on zo.space
