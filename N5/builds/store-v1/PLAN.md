---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.1
provenance: con_kWyRIcEV0FcShrUf
---

# V's Prompt & Skill Store (Gumroad-Style)

## Decisions (Locked In)

| Decision | Choice |
|----------|--------|
| Pricing model | Direct purchase (no credits) |
| Delivery | Markdown zip file download |
| Pricing | $5 per skill |
| Initial products | Pulse (build orchestration), Dynamic Survey Analyzer |
| User accounts | None - email at checkout, Stripe receipts |
| Positioning | "Zo-optimized skills, adaptable to Claude Code" |

---

## Checklist

### Phase 1: Store UI (Gumroad-Style)
- ☑ Create ProductCard component (thumbnail, title, price, description)
- ☑ Create ProductGrid component (responsive 2-3 column layout)
- ☑ Create ProductDetail page (hero, description, features, buy button)
- ☑ Style with V's aesthetic (dark theme, zinc grays, sky-400 accents)
- ☑ Create store landing page with V's branding + product grid
- ☑ Add filter tabs: All / Skills / Bundles (future)
- ☑ Responsive mobile layout

### Phase 2: Products & Stripe Integration  
- ☑ Package Pulse skill as downloadable zip
- ☑ Package Dynamic Survey Analyzer as downloadable zip
- ☑ Create Stripe products + payment links ($5 each)
- ☑ Wire "Buy Now" buttons to Stripe payment links
- [ ] Create product database (products.json or SQLite) — deferred, using inline data

### Phase 3: Delivery & Polish
- ☑ Configure Stripe hosted confirmation page with download link
- ☑ Create static download URLs for product zips
- ☑ Add "Zo-optimized, Claude Code adaptable" badges
- ☑ Footer: "Built on Zo.computer"
- [ ] Test end-to-end purchase flow
- [ ] Promote staging → production

---

## Phase 1: Store UI

**Affected Files:**
- `Sites/store-va-staging/src/pages/StoreLanding.tsx` (new)
- `Sites/store-va-staging/src/components/store/ProductCard.tsx` (new)
- `Sites/store-va-staging/src/components/store/ProductGrid.tsx` (new)
- `Sites/store-va-staging/src/pages/ProductDetail.tsx` (new)
- `Sites/store-va-staging/src/App.tsx` (routes)
- `Sites/store-va-staging/src/styles.css` (dark theme if not already)

**Gumroad Layout Pattern (from research):**
- Creator profile header (avatar, name, bio, social links)
- Product grid below with cover images
- Product cards: 16:9 or 1:1 thumbnail, title, price, one-liner
- Click → dedicated product page with full description
- Clean whitespace, minimal chrome

**V's Aesthetic (from vrijenattawar):**
- `bg-black` background
- `text-zinc-100` / `text-zinc-400` / `text-zinc-600` text hierarchy
- `border-zinc-700/50` / `border-zinc-800` borders
- `hover:text-sky-400` accent on links
- `hover:border-sky-500/50` accent on interactive elements
- Rounded pills for badges
- V insignia logo
- Font: system sans-serif, antialiased

**Changes:**
1. **StoreLanding.tsx**: 
   - Hero with V insignia, "@thevibethinker" badge, brief store intro
   - "Zo-optimized skills for AI-native workflows"
   - ProductGrid with initial 2 products

2. **ProductCard.tsx**:
   - Cover image (default placeholder or skill-specific)
   - Title, price ($5), one-liner description
   - "Zo Skill" badge
   - Hover: border-sky-500/50, slight scale

3. **ProductDetail.tsx**:
   - Breadcrumb: Store > Product Name
   - Hero with product title + price
   - Description section (markdown rendered)
   - Features list
   - "Buy Now" button (→ Stripe)
   - "Zo-optimized • Claude Code adaptable" note

**Unit Tests:**
- [ ] ProductCard renders title, price, description
- [ ] ProductGrid responsive breakpoints
- [ ] StoreLanding renders without errors

---

## Phase 2: Products & Stripe

**Affected Files:**
- `Sites/store-va-staging/data/products.json` (new)
- `Sites/store-va-staging/public/downloads/` (new directory)
- `Skills/pulse/` → packaged zip
- `Skills/dynamic-survey-analyzer/` → packaged zip

**Product Data Structure:**
```json
{
  "products": [
    {
      "id": "pulse",
      "name": "Pulse: Build Orchestration",
      "tagline": "Automated parallel build system for complex Zo projects",
      "description": "...",
      "price_cents": 500,
      "stripe_payment_link": "https://buy.stripe.com/...",
      "download_path": "/downloads/pulse-skill.zip",
      "badges": ["zo-optimized", "claude-code-ready"],
      "features": [
        "Spawn parallel workers via /zo/ask",
        "Automatic health monitoring",
        "SMS escalation for dead workers",
        "Built-in safety layer with snapshots"
      ]
    }
  ]
}
```

**Packaging Script:**
```bash
# Create clean skill zips
cd Skills/pulse && zip -r ../../Sites/store-va-staging/public/downloads/pulse-skill.zip . -x "*.pyc" -x "__pycache__/*"
```

**Stripe Setup:**
- Create 2 products via create_stripe_product
- $5 each (500 cents)
- Hosted confirmation message with download instructions
- Payment link URLs stored in products.json

**Unit Tests:**
- [ ] products.json validates against schema
- [ ] Zip files exist and are non-empty
- [ ] Payment links are active

---

## Phase 3: Delivery & Polish

**Affected Files:**
- `Sites/store-va-staging/server.ts` (static file serving for /downloads/)
- Stripe product confirmation messages

**Delivery Flow:**
1. User clicks "Buy Now" → Stripe Checkout
2. After payment → Stripe hosted confirmation page
3. Confirmation shows: "Thank you! Download your skill: [link]"
4. Link points to `https://store-va.zocomputer.io/downloads/pulse-skill.zip`

**Polish Items:**
- Add V insignia favicon
- Footer: "Prompts & skills built on Zo.computer"
- "Questions? @thevibethinker on X"
- Mobile: stack product grid to 1 column

**Unit Tests:**
- [ ] Download URLs return 200
- [ ] Stripe payment links active

---

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Stripe webhook not set up | Low | Use hosted confirmation page + static downloads (no webhook needed v1) |
| Skill packaging incomplete | Medium | Verify both skills have all necessary files before zipping |
| Dark theme conflicts | Low | Copy styles directly from vrijenattawar |

---

## Success Criteria

1. Store live at store-va.zocomputer.io with 2 products
2. Each product has working Stripe payment link
3. Post-purchase, buyer can download zip
4. Aesthetic matches vrijenattawar.com (dark, minimal, sky accents)
5. Mobile responsive

---

## Alternatives Considered

1. **Credit system** — Rejected: adds complexity (user accounts, balance tracking) for v1
2. **GitHub private repo access** — Deferred: good idea but complex (token generation, expiry). Could add in v2.
3. **Gumroad embed** — Rejected: lose control over aesthetic, takes fees

---

## Trap Doors

- **None identified** — All decisions are reversible. Can add credits later, can move to GitHub delivery later.
