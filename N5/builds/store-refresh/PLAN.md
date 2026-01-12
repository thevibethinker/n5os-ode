---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.1
type: build_plan
status: plan-ready
---

# Plan: Polish store landing

**Objective:** Deliver the richer store landing experience (higher-res cosmic hero, bold "N5 OS", and updated Latin tagline) on staging, then sync those assets to production so `store-va.zocomputer.io` reflects the new look.

**Trigger:** V asked for sharper backgrounds, typographic polish, and "Ad astra per machinam" copy, then requested that the refreshed landing go live.

**Key Design Principle:** Keep the hero simple and immersive—glassmorphic card floating over a single-tone nebula—to let the cosmic background carry the energy without adding multiple sections or animation.

---

## Open Questions
- [x] Are any other components (CTA, product grid, footer) supposed to change beyond the hero? → No, V only requested the hero polish.
- [x] Do we need a dedicated staging service before pushing to prod? → Not yet, but we will register one so V can preview.

---

## Checklist

### Phase 1: Lock down staging preview
- ☐ Confirm `Sites/store-va-staging` renders the new cosmic background, bold “N5 OS”, and the tagline `"Ad astra per machinam."` after a `bun run build`/`bun run prod` smoke test.
- ☐ Register a staging service if missing so there is a public URL to show V the hero.
- ☐ Test: `curl -fs` staging endpoint (once service exists) should return HTTP 200 within 10 seconds.

### Phase 2: Promote polished assets to production
- ☐ Run `promote_site.sh store-va` to sync files from staging into the production directory and reinstall/build on prod side.
- ☐ Restart the existing production service so it loads the new bundle, then smoke-test `https://store-va.zocomputer.io` for HTTP 200 and the updated hero.
- ☐ Test: Verify that the running prod service responds with the new background and tagline (visual confirmation via `curl` / manual preview).

---

## Phase 1: Lock down staging preview

### Affected Files
- `Sites/store-va-staging/src/pages/demos/blank-demo.tsx` - UPDATE - typography, tagline, and hero copy.
- `Sites/store-va-staging/public/bg.png` - REPLACE - higher-resolution cosmic background image (2048×2048) generated via Gemini.
- `N5/builds/store-refresh/PLAN.md` - UPDATE - planning metadata (this file).

### Changes
**1.1 Confirm hero assets on staging:** Ensure the updated hero file references the new background, bold/regular font weight combination for "N5 OS Store", and the Latin line. Smoke-run the staging build (`bun run build` then `bun run prod` if necessary) to catch any build issues.

**1.2 Provide staging visibility:** If `store-va-staging` is not already exposed, register a new HTTP user service (e.g., label `store-staging`) configured to `bun install && bun run prod` so there’s a published port for review.

### Unit Tests
- `bun run build` inside `Sites/store-va-staging`: must exit 0 and produce `dist/` assets.
- `curl -fs http://localhost:<staging-port>` after starting the staging service: should return HTTP status 200.

---

## Phase 2: Promote polished assets to production

### Affected Files
- `Sites/store-va/` directory (all files) - SYNC - staging becomes source of truth for `store-va`.
- `Sites/store-va/package.json` (implicitly touched via `bun install`/`bun run prod` when building).
- Registered service definition `store` - RESTART - existing service must reload the new bundle.

### Changes
**2.1 Sync staging into prod:** Run `/home/workspace/N5/scripts/promote_site.sh store-va` to Rsync stage → prod, respecting `.n5protected` and excluding `node_modules`. This keeps production aligned with the verified staging files.

**2.2 Rebuild & restart prod:** Inside `/home/workspace/Sites/store-va`, run `bun install` (if dependencies changed) and let the registered service restart by terminating its current `bun run prod` process; the Zo service manager will respawn it with the new code.

### Unit Tests
- `curl -fs https://store-va.zocomputer.io`: should return HTTP 200 and deliver the new hero copy (verifiable by checking for `Ad astra per machinam`).
- `ps`/`ss` check that the `store` service is listening on port 58665 after restart.

---

## Success Criteria
1. Staging exposes the new hero (new bg image, typography, tagline) at its public URL and returns HTTP 200.
2. Production at `https://store-va.zocomputer.io` shows the refreshed hero copy and imagery, and the service responds with HTTP 200.
3. The `store` service process runs the updated bundle without leaving orphaned older assets or failing builds.

---

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Production service continues serving cached old bundle because process never restarted. | Kill the `bun run prod` process after sync so Zo’s service manager relaunches it with new code. | 
| Staging service port conflicts or fails to start because dependencies are missing. | Run `bun install` before staging `bun run prod` and choose an unused port (58666) when registering the service. |
| rsync accidentally wipes prod config (e.g., custom env files). | Promote script excludes `node_modules/` and we have `.n5protected` checks; verify the `zosite.json` remains the same before/after. |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. Animate the hero background with a subtle parallax star field instead of a static image. (Would add overhead and require animation assets.)
2. Expand the landing into a multi-section explainer (features, CTA, footer) directly on the same page. (Escapes the simple hero focus V prefers.)

### Incorporated:
- None of the Level Upper suggestions were incorporated because V wanted a sharp, minimal hero without extra motion or sections.

### Rejected (with rationale):
- Animated parallax: rejected because the focus is on clarity and a static, high-resolution background already achieves the premium feel without extra complexity.
- Multi-section layout: rejected because it would derail the quick hero polish and introduce new copy decisions that haven’t been requested.


