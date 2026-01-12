---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_2lLTcsOGpnJh9fdQ
---

# After-Action Report: Store-va landing page polish + deploy verification

**Date:** 2026-01-12  
**Type:** build / deployment verification  
**Conversation:** con_2lLTcsOGpnJh9fdQ

## Objective

Bring the `store-va` site “back under control” after corrupted setup threads by re-checking how staging vs production are configured, applying a small set of UI changes (sharper background, typography emphasis, and a revised tagline), and confirming those changes are actually reflected on the live URLs.

## What Happened

### 1) System check: what is running?
We inspected the currently registered services and found both a production service and a staging service for the store site:
- Prod: `https://store-va.zocomputer.io`
- Staging: `https://store-staging-va.zocomputer.io`

We also confirmed the corresponding codebases exist at:
- `file 'Sites/store-va'`
- `file 'Sites/store-va-staging'`

### 2) Staging vs prod parity
We compared staging and production and found them functionally identical at the app level (same demo-variant routing), with differences primarily in site/service configuration.

### 3) UI changes implemented (local)
We implemented the requested UI changes in both staging and production codebases:
- Background sharpness: replaced the original low-resolution background with a new 2048×2048 nebula-style `bg.png`
- Typography: made “N5 OS” bold while keeping “Store” not bold
- Tagline: updated the quote line to “Ad astra per machinam.”

### 4) Verification gap
Although both prod and staging URLs returned HTTP 200, remote asset hashes did not match the updated local `bg.png`, which strongly suggests one of the following:
- the running service is still serving older built assets,
- browser / CDN caching is masking the update,
- or a full rebuild/restart is still required for the deployed bundle.

## Key Decisions

- Use the Latin phrase: **“Ad astra per machinam.”** (to the stars through the machine)
- Brand emphasis: **“N5 OS” bold**, “Store” lighter

## Artifacts Created / Modified

| Artifact | Location | Purpose |
|---|---|---|
| Updated background image | `file 'Sites/store-va/public/bg.png'` | Sharper, higher-res nebula background |
| Updated hero component | `file 'Sites/store-va/src/pages/demos/blank-demo.tsx'` | Typography + tagline update |
| Updated background image (staging) | `file 'Sites/store-va-staging/public/bg.png'` | Keep staging in parity |
| Updated hero component (staging) | `file 'Sites/store-va-staging/src/pages/demos/blank-demo.tsx'` | Keep staging in parity |
| AAR | `file 'Records/AARs/2026-01-12_store-va-landing-polish.md'` | Record what changed + what’s still unresolved |

## Lessons Learned

### Process
- “I edited the files” ≠ “prod changed.” For Zo Sites, verifying the deployed artifact matters; treat service restart/rebuild and cache-busting as explicit steps rather than assumptions.

### Technical
- When a site looks unchanged, comparing **remote asset hashes** against local is a fast way to distinguish “my eyes are lying” from “the deployment didn’t update.”

## Next Steps

1. Confirm the canonical domain you want (you referenced `store-va.computer.io`, but the active service is `store-va.zocomputer.io`).
2. Force a clean deploy cycle for prod:
   - restart the `store` service (or run the site’s production build step) and then
   - verify by checking `bg.png` hash + checking visible typography/tagline.
3. If caching persists, rename the asset (e.g., `bg-v2.png`) and update references to force cache-bust.

## Outcome

**Status:** Incomplete

Local changes were applied to both staging and production codebases, but production still appears to be serving older assets/cached content. The remaining work is deployment verification and cache-busting.

