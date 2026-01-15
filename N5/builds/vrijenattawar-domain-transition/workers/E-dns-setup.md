---
created: 2026-01-14
last_edited: 2026-01-14
version: 1.0
provenance: con_KGkdxFqpqncEQyuu
---

# Worker E: DNS Setup Guide

**Project:** vrijenattawar-domain-transition
**Component:** DNS configuration assistance
**Dependencies:** None (can run in parallel with design)

---

## Objective

Help V configure DNS to point vrijenattawar.com to their Zo-hosted site. Provide clear, step-by-step guidance with screenshots/instructions for Squarespace DNS panel.

---

## Context

V owns vrijenattawar.com through Squarespace. The Squarespace site has expired (no longer paying for hosting), but V still owns the domain registration.

**Goal:** Point the domain to Zo infrastructure so the new landing page is accessible at vrijenattawar.com

**Current state:**
- Domain: vrijenattawar.com (owned via Squarespace)
- Site: staged at `Sites/vrijenattawar-staging/`
- Zo service URL pattern: `<label>-va.zocomputer.io`

---

## Tasks

### 1. Research Squarespace DNS Management

Use Zo's browser to:
1. Navigate to Squarespace's DNS documentation
2. Understand how to add CNAME records for domains managed by Squarespace
3. Check if Squarespace supports CNAME flattening for root domains (@ record)

### 2. Determine Exact Zo Target

Check what the published service URL will be:
- Run `list_user_services` to see existing services
- The site will be published as a user service
- Typical pattern: `<label>-va.zocomputer.io`

For vrijenattawar, the target will likely be:
- `vrijenattawar-va.zocomputer.io` (if label is "vrijenattawar")

### 3. Create Step-by-Step DNS Guide

Write a clear guide with:

**For www subdomain (CNAME):**
- Host: www
- Type: CNAME
- Value: vrijenattawar-va.zocomputer.io

**For root domain (@):**
Squarespace may not allow CNAME on root. Options:
- If Squarespace supports ALIAS/ANAME: use that
- Otherwise: set up a redirect from @ to www
- Or: recommend Cloudflare transfer for proper CNAME flattening

### 4. Cloudflare Transfer Recommendation

If V wants to transfer to Cloudflare (cheaper, better):
1. Research Squarespace domain transfer process
2. Document the unlock + auth code retrieval steps
3. Explain Cloudflare's domain transfer flow
4. Note the ~$10.44/year cost vs Squarespace's ~$20/year

---

## Deliverables

1. Updated `Sites/vrijenattawar-staging/DNS_SETUP.md` with:
   - Exact step-by-step Squarespace DNS instructions
   - Screenshots or detailed navigation paths
   - Root domain handling options
   - Cloudflare transfer guide (optional section)

2. Brief summary for V of:
   - What DNS changes are needed
   - Any limitations with Squarespace
   - Recommendation on whether to transfer to Cloudflare

---

## Important Notes

- Do NOT make any actual DNS changes — V will do this manually
- Do NOT try to log into V's Squarespace account
- Focus on providing clear, actionable documentation
- Use web research to get current Squarespace DNS interface details

