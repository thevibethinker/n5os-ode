---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
provenance: con_kWyRIcEV0FcShrUf
---

# Store Enhancements: Export Pipeline + UX

## Components

1. **Skill Export Pipeline** — Automated sanitize → package → list workflow
2. **Product Thumbnails** — Symbolic visual language, generated per-skill
3. **SEO + GA4** — Meta tags, OG images, analytics integration
4. **Email Capture** — "Get notified" signup with simple backend
5. **Testimonials Section** — Social proof display
6. **GitHub Private Repo Delivery** — Premium delivery mechanism

---

## Open Questions

None — V has confirmed all components.

---

## Checklist

### Phase 1: Skill Export Pipeline (Core Infrastructure)
- [ ] Create `Skills/skill-export/SKILL.md` with workflow
- [ ] Create `scripts/sanitize.py` — Remove personal paths, secrets, internal refs
- [ ] Create `scripts/generate_listing.py` — Extract metadata for store catalog
- [ ] Create `scripts/package.py` — Create zip + optional Claude Code version
- [ ] Create `data/catalog.json` schema for store products
- [ ] Wire pipeline: `skill-export run <skill-slug>` does full flow
- [ ] Test: Export pulse skill through pipeline

### Phase 2: Product Thumbnails + Visual Language
- [ ] Define symbolic aesthetic (dark bg, geometric symbols, zinc/sky accents)
- [ ] Generate thumbnail for Pulse (orchestration/parallel symbol)
- [ ] Generate thumbnail for Survey Analyzer (data/insight symbol)
- [ ] Add `thumbnail` field to catalog.json schema
- [ ] Update ProductCard to display real thumbnails
- [ ] Update ProductDetail hero image

### Phase 3: SEO + GA4 Integration
- [ ] Add react-helmet-async for dynamic meta tags
- [ ] Create SEO component with title, description, OG tags
- [ ] Add OG image generation (or use thumbnails)
- [ ] Integrate GA4 tracking (reuse pattern from vrijenattawar site)
- [ ] Track: page views, product clicks, purchase button clicks

### Phase 4: Email Capture + Testimonials
- [ ] Create EmailCapture component (email input + submit)
- [ ] Create `/api/subscribe` endpoint in server.ts
- [ ] Store subscribers in SQLite (subscribers.db)
- [ ] Create Testimonials component (quote, name, role)
- [ ] Add testimonials data to catalog or separate file
- [ ] Add both components to StoreLanding

### Phase 5: GitHub Private Repo Delivery
- [ ] Create webhook endpoint `/api/webhooks/stripe`
- [ ] Handle `checkout.session.completed` event
- [ ] Extract buyer email from Stripe session
- [ ] GitHub API: invite collaborator to skill repo
- [ ] Send confirmation email via Gmail integration
- [ ] Update Stripe products with webhook URL
- [ ] Create skill repos: `pulse-skill`, `survey-analyzer-skill`

---

## Phase Details

### Phase 1: Skill Export Pipeline

**Affected Files:**
- `Skills/skill-export/SKILL.md` (new)
- `Skills/skill-export/scripts/sanitize.py` (new)
- `Skills/skill-export/scripts/generate_listing.py` (new)
- `Skills/skill-export/scripts/package.py` (new)
- `Skills/skill-export/scripts/export.py` (new — orchestrator)
- `Sites/store-va/data/catalog.json` (new)

**Changes:**

1. **Sanitize script** removes:
   - Absolute paths containing `/home/workspace`
   - References to `N5/` internal systems
   - API keys, tokens, secrets
   - Personal identifiers (email, phone)
   - Zo-specific webhook URLs
   
2. **Generate listing** extracts:
   - Name, description from SKILL.md frontmatter
   - Features list from SKILL.md body
   - Compatibility info
   - Suggested price, badges
   
3. **Package script** creates:
   - `<skill>-zo.zip` — Zo-optimized version
   - `<skill>-claude-code.zip` — Adapted for Claude Code (optional)
   - Copies to `Sites/store-va/public/downloads/`
   
4. **Catalog schema:**
```json
{
  "products": [
    {
      "id": "pulse",
      "name": "Pulse: Build Orchestration",
      "tagline": "...",
      "description": "...",
      "price_cents": 500,
      "stripe_payment_link": "...",
      "thumbnail": "/images/pulse-thumb.png",
      "download_zo": "/downloads/pulse-zo.zip",
      "download_claude": "/downloads/pulse-claude-code.zip",
      "badges": ["zo-optimized", "claude-code"],
      "features": ["...", "..."],
      "github_repo": "vrijenattawar/pulse-skill"
    }
  ]
}
```

**Unit Tests:**
- [ ] Sanitize removes `/home/workspace` paths
- [ ] Sanitize removes API key patterns
- [ ] Generate listing extracts name/description
- [ ] Package creates valid zip files
- [ ] Full pipeline completes without error

---

### Phase 2: Product Thumbnails

**Affected Files:**
- `Sites/store-va/public/images/pulse-thumb.png` (new)
- `Sites/store-va/public/images/survey-analyzer-thumb.png` (new)
- `Sites/store-va/src/components/store/ProductCard.tsx`
- `Sites/store-va/src/pages/ProductDetail.tsx`
- `Sites/store-va/data/catalog.json`

**Visual Language:**
- Dark background (#09090b / zinc-950)
- Geometric symbol per skill (abstract, not literal)
- Subtle glow effect (sky-500 at low opacity)
- Consistent sizing (1200x630 for OG, 400x300 for cards)

**Symbol concepts:**
- Pulse: Concentric ripples / wave interference pattern (parallel execution)
- Survey Analyzer: Lens/prism refracting into spectrum (insight extraction)

**Unit Tests:**
- [ ] Thumbnails load without 404
- [ ] ProductCard displays thumbnail
- [ ] ProductDetail displays hero image

---

### Phase 3: SEO + GA4

**Affected Files:**
- `Sites/store-va/package.json` (add react-helmet-async)
- `Sites/store-va/src/components/SEO.tsx` (new)
- `Sites/store-va/src/pages/StoreLanding.tsx`
- `Sites/store-va/src/pages/ProductDetail.tsx`
- `Sites/store-va/index.html` (GA4 script)

**Changes:**
- Wrap app in HelmetProvider
- Each page sets title, description, OG tags
- GA4: Track pageview, `product_view`, `purchase_click` events

**Unit Tests:**
- [ ] Document title changes per page
- [ ] OG tags present in head
- [ ] GA4 events fire on click

---

### Phase 4: Email Capture + Testimonials

**Affected Files:**
- `Sites/store-va/src/components/store/EmailCapture.tsx` (new)
- `Sites/store-va/src/components/store/Testimonials.tsx` (new)
- `Sites/store-va/server.ts` (add /api/subscribe)
- `Sites/store-va/subscribers.db` (new, auto-created)
- `Sites/store-va/src/pages/StoreLanding.tsx`
- `Sites/store-va/data/testimonials.json` (new)

**Email Capture:**
- Simple form: email + "Notify Me" button
- POST to `/api/subscribe`
- Store in SQLite: email, subscribed_at, source
- Success toast: "You're on the list!"

**Testimonials:**
- Initially empty or placeholder
- Structure: quote, name, role, avatar (optional)
- Display as horizontal scroll or grid

**Unit Tests:**
- [ ] Subscribe endpoint returns 200
- [ ] Duplicate email handled gracefully
- [ ] Testimonials render from JSON

---

### Phase 5: GitHub Private Repo Delivery

**Affected Files:**
- `Sites/store-va/server.ts` (add webhook endpoint)
- `Sites/store-va/src/lib/github.ts` (new — GitHub API client)
- `Sites/store-va/src/lib/stripe-webhook.ts` (new — webhook handler)
- Environment: `GITHUB_TOKEN`, `STRIPE_WEBHOOK_SECRET`

**Flow:**
1. Stripe webhook hits `/api/webhooks/stripe`
2. Verify signature with `STRIPE_WEBHOOK_SECRET`
3. Extract `customer_email` and `product_id` from session
4. Map product_id → GitHub repo name
5. GitHub API: `PUT /repos/{owner}/{repo}/collaborators/{username}`
   - Note: Need username, not email. Options:
     a. Ask buyer for GitHub username at checkout (custom field)
     b. Send email with "claim access" link where they enter username
6. Send confirmation email

**Trap Door:** GitHub invites require username, not email. Simplest: Option (b) — post-purchase flow where buyer enters GitHub username.

**Unit Tests:**
- [ ] Webhook validates signature
- [ ] Invalid signature returns 401
- [ ] Valid event triggers invite flow
- [ ] Missing GitHub username triggers claim email

---

## Success Criteria

1. `skill-export run pulse` creates sanitized zip + catalog entry
2. Store displays real thumbnails with consistent visual language
3. GA4 tracks product views and purchase clicks
4. Email signup works and stores in DB
5. Testimonials section renders (even if empty initially)
6. GitHub delivery flow works end-to-end (manual test)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| GitHub username vs email mismatch | High | Use post-purchase claim flow |
| Stripe webhook signature issues | Medium | Test with Stripe CLI locally first |
| Thumbnail generation takes time | Low | V generates via separate image model session |

---

## Alternatives Considered

1. **GitHub delivery via email-only** — Rejected: GitHub requires username for collaborator invite
2. **Gumroad embed instead of custom** — Rejected: Loses aesthetic control, fees
3. **Credits system** — Deferred: Premature at current scale

---

## Execution Order

Recommend: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5

Phase 1 is foundational (export pipeline enables future skills).
Phase 2 can happen in parallel if V generates thumbnails manually.
Phases 3-4 are straightforward UI.
Phase 5 is most complex, do last.

---

## Handoff Ready

Plan complete. Ready to hand off to Builder for Phase 1.
