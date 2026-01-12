---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
type: build_plan
status: draft
provenance: con_3GQi1WkfJCvt2lOh
---

# Plan: Store VA Coming Soon Landing

**Objective:** Ship a minimal, polished “N5 OS Store coming soon” landing page served at store-va.zocomputer.io so Stripe has a reliable storefront URL.

**Trigger:** V asked for confirmation that `store-va.zocomputer.io` could have a live landing page, and we already created a placeholder that needs cleanup, stabilization, and proper routing.

**Key Design Principle:** Simple > easy; keep the landing page lean (static hero card + generated background) and gate infrastructure decisions so the production service uses the correct slug and entrypoint.

---

## Open Questions

- [ ] Should the canonical production site stay under `store-va` or be scoped to a namespaced subdomain (e.g., `store-va-va`) once we re-register the service with the correct label?
- [ ] Do we want to keep the current Bun dev entrypoint (`bun run dev`) for Stripe validation, or build/prod bundle it once the design is finalized?
- [ ] Is there any additional metadata Stripe requires (custom favicon, OG tags, copy) beyond the simple “coming soon” card?

---

## Checklist

### Phase 1: Visual card & asset polish
- ☐ Replace the temporary demo with the custom landing layout that layers the background image, icon, and messaging.
- ☐ Ensure the generated background image lives in `public/bg.png` and is referenced via CSS so the card overlays correctly on all breakpoints.
- ☐ Test: Run `bun run dev` locally and hit `/` to confirm the design renders with the imported asset and typography.

### Phase 2: Infrastructure alignment & domain wiring
- ☐ Update `Sites/store-va/zosite.json` and the registered service so the published hostname is `store-va.zocomputer.io` and the entrypoint runs the production bundle (`bun run prod`).
- ☐ If the service label needs renaming, stop/remove the `store-va` service and re-register with the desired slug; re-sync the `site-promote` workflow to copy the staging build.
- ☐ Test: Curl `https://store-va.zocomputer.io` and verify the landing copy appears without the extra `-va` duplication; confirm the service uses the published Bun prod build.

---

## Phase 1: Visual card & asset polish

### Affected Files
- `Sites/store-va-staging/src/pages/demos/blank-demo.tsx` - UPDATE - replace demo content with custom landing layout/typography and copy.
- `Sites/store-va-staging/public/bg.png` - CREATE - store the generated background image from Gemini for the hero.
- `Sites/store-va-staging/src/styles.css` - UPDATE - add utility styles (e.g., min-height, background positioning) if needed to keep layout centered.

### Changes

**1.1 Landing layout:** Harden the card component inside `blank-demo.tsx` with a centered main, gradient glows, icon, and the N5 OS copy so the page feels finished even without product details.

**1.2 Background asset:** Save the generated PNG to `public/bg.png`, reference it via inline style or CSS variable, and ensure it is bundled in both dev/prod builds.

### Unit Tests
- Visual smoke test: `bun run dev` → visit `/` in browser to confirm the card, text, and optional animation display correctly.
- Accessibility check: ensure there is a `main` landmark and text contrast is readable over the background.

---

## Phase 2: Infrastructure alignment & domain wiring

### Affected Files
- `Sites/store-va/zosite.json` - UPDATE - align `name`, entrypoint, and env vars with the production bundle and correct slug.
- `N5/scripts/promote_site.sh` (implicit workflow) - EXECUTE - run with `store-va` once the prod directory exists.

### Changes

**2.1 Entrypoint polish:** Switch the registered service entrypoint to `bun run prod` (or `bun run dev` only if Stripe strictly needs dev) and ensure `VITE_ZO_SITE_DEMO_VARIANT=blank` survives in production so the landing component renders.

**2.2 Service registration:** Delete/re-register the `store-va` user service (if necessary) so the human-facing host is `https://store-va.zocomputer.io` rather than `store-va-va.zocomputer.io`; keep the port consistent with the promoted prod directory.

### Unit Tests
- `curl -I https://store-va.zocomputer.io` → expect 200 with Hono/Bun response and landing HTML.
- Post-promotion sanity: Visit the URL in a browser or via `curl https://store-va.zocomputer.io` to confirm the generated HTML loads from `prod` instead of dev.

---

## Success Criteria

1. The landing page renders at `https://store-va.zocomputer.io` with the glassmorphism card, “N5 OS Store coming soon” message, and Gemini-generated background.
2. The published service is running `bun run prod` from `Sites/store-va`, so Stripe can rely on a stable, production-facing endpoint (no `store-va-va` host).
3. Both dev (`store-va-staging`) and prod directories stay in sync via the `promote_site` workflow without breaking other sites.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Promoting while `store-va` production directory is empty will misalign the registered service | Create `/home/workspace/Sites/store-va` before running `promote_site.sh` and re-run the sync until the copy succeeds. |
| Re-registering the service could temporarily drop the endpoint during Stripe checks | Schedule the re-registration during a low-traffic window, and keep the existing service ready to revert if Stripe cache needs clearing. |

---

## Nemawashi / Alternatives considered

1. Build a single static `index.html` served via a simple HTTP server.
   - **Reason:** Fastest path, avoids Bun tooling. Rejected because we already have the Bun-based boilerplate and prefer consistency with other Zo sites.
2. Keep the dev server (`bun run dev`) as the production entrypoint.
   - **Reason:** Minimizes configuration changes. Rejected because Stripe should hit a production build (`bun run prod`) that mirrors a real storefront.
3. Use a Serverless function to render the landing page (e.g., Vercel-style). Rejected since Zo services prefer direct Bun deploys for controllable routing.

---

## Level Upper Review

### Counterintuitive Suggestions Received
1. Ship the landing page as a single static asset served via the `public/` directory and use Zo’s built-in static server instead of Bun.
2. Delay Service re-registration until after Stripe confirms the landing page works on the first dev host, then flip the alias.

### Incorporated
- Incorporated the idea of keeping the landing page extremely simple (single card + static overlay) so the produced page could be served anywhere.

### Rejected (with rationale)
- Serving the page as static files only: rejected because the existing starter already bundles assets via Bun, and rewriting the flow into a separate static host would take longer than updating the demo component.
- Delaying service re-registration: rejected because Stripe already has the temporary `store-va-va` host; we need to resolve it promptly so the `store-va` domain points to a production-ready endpoint.

