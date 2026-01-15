---
created: 2026-01-14
last_edited: 2026-01-14
version: 1.0
provenance: con_KGkdxFqpqncEQyuu
---

# Worker C: Sites Preparation

**Project:** vrijenattawar-domain-transition
**Worker ID:** C-sites-preparation
**Estimated Time:** 60 minutes
**Dependencies:** None

---

## Objective

Clean up misfiled site directories and scaffold the new vrijenattawar.com landing page site.

---

## Task 1: Delete Misfiled Sites

### 1a: `/home/workspace/events-calendar/` (at workspace root)

**Background:** This is a site-shaped folder that was created at the workspace root instead of under `Sites/`. There's already a proper version at `Sites/events-calendar/` and `Sites/events-calendar-staging/`.

**Verification:** The root version has different content (Vite-based with index.html) vs the Sites version (server.ts based). The Sites version is the active one.

**Action:**
1. Check protection: `python3 /home/workspace/N5/scripts/n5_protect.py check /home/workspace/events-calendar`
2. Delete: `rm -rf /home/workspace/events-calendar`

### 1b: `/home/workspace/Inbox/20251027-132318_n5-waitlist/`

**Background:** Stale snapshot from October. The real n5-waitlist is at `Sites/n5-waitlist/`.

**Action:**
1. Check protection: `python3 /home/workspace/N5/scripts/n5_protect.py check /home/workspace/Inbox/20251027-132318_n5-waitlist`
2. Delete: `rm -rf /home/workspace/Inbox/20251027-132318_n5-waitlist`

---

## Task 2: Scaffold vrijenattawar-staging

**Action:** Use the `create_website` tool:

```
create_website(
  name="vrijenattawar-staging",
  parent_path_parts=["Sites"],
  variant="marketing"
)
```

This creates `/home/workspace/Sites/vrijenattawar-staging/` with the marketing template as a starting point.

---

## Task 3: Document DNS Requirements

After scaffolding, create a brief DNS instructions document at `/home/workspace/Sites/vrijenattawar-staging/DNS_SETUP.md` containing:

1. **What V needs to do in Squarespace:**
   - Log into Squarespace domain management
   - Find DNS settings for vrijenattawar.com
   - Add a CNAME record pointing to Zo infrastructure

2. **Zo infrastructure details:**
   - The site will be published as a User Service
   - Once published, it will get a URL like `https://vrijenattawar-va.zocomputer.io`
   - The custom domain will need to point to this

3. **Long-term recommendation:**
   - Transfer domain from Squarespace to Cloudflare ($10.44/year for .com)
   - Cloudflare provides free SSL, better DNS management, and no markup

**Note:** Don't actually publish the service yet—just document what will be needed.

---

## Deliverables

- [ ] `/home/workspace/events-calendar/` deleted
- [ ] `/home/workspace/Inbox/20251027-132318_n5-waitlist/` deleted
- [ ] `/home/workspace/Sites/vrijenattawar-staging/` created with marketing variant
- [ ] `DNS_SETUP.md` created with instructions for V

---

## Completion

When done, report back with:
1. Confirmation of deletions
2. Path to new site scaffold
3. Summary of DNS setup requirements

