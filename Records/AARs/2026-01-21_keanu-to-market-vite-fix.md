---
created: 2026-01-21
last_edited: 2026-01-21
version: 1.0
provenance: con_nY1vnzj9LnrLGEUG
type: aar
---

# After-Action Report: Keanu-to-Market Vite HMR Fix

**Date:** 2026-01-21  
**Duration:** ~90 minutes  
**Outcome:** ✅ Success

## Summary

The Keanu-to-Market site went completely blank due to a Vite 7 configuration issue that bundled HMR (Hot Module Replacement) client code into the production build. After extensive debugging that initially went in circles, the Level Upper persona was invoked to break the pattern. The solution was simple: clean git restore to the committed baseline, which had working Vite config. Features were then re-implemented incrementally.

## What Happened

1. **Initial Task:** Worker W4.2 brief to fix image loading reliability and transcendence progression
2. **First Attempt:** Modified Home.tsx and quotes.ts with new image preloading logic
3. **Site Broke:** Page went completely blank (white screen)
4. **Debug Spiral:** Tried multiple approaches:
   - Checked service logs (nothing useful)
   - Tried downgrading Vite (5, 6) - still broken
   - Removed plugins one by one - still broken
   - Added `__DEFINES__` to vite config manually - revealed more missing globals
5. **Level Upper Intervention:** Stepped back and asked "was this code EVER working?"
6. **Root Cause Found:** git status showed vite.config.ts was modified - the committed version was clean
7. **Solution:** `git checkout -- vite.config.ts` and clean rebuild
8. **Feature Recovery:** Re-implemented improvements on working baseline

## Root Cause

The Vite 7 HMR client contains runtime placeholders (`__DEFINES__`, `__HMR_CONFIG_NAME__`, `__BASE__`) that should be replaced during build. When vite.config.ts was modified during debugging, something caused the HMR client to be bundled wholesale into production code without placeholder replacement.

**Key signal that would have caught this earlier:** The JS bundle grew from ~297KB to ~316KB - the extra ~19KB was the HMR client code.

## Lessons Learned

| Lesson | Application |
|--------|-------------|
| **Check git status early** | When debugging build issues, first verify working tree matches known-good state |
| **Bundle size changes are signals** | A 6% bundle size increase should trigger investigation |
| **Vite config is fragile** | Small changes can have cascading effects on what gets bundled |
| **Level Upper breaks loops** | When stuck in circular debugging, invoke meta-cognitive review |

## Artifacts

- `file 'Sites/keanu-to-market/src/pages/Home.tsx'` — Enhanced with transcendence progression
- `file 'Sites/keanu-to-market/src/data/quotes.ts'` — Added getQuotesByLevel, getRandomQuoteByLevelAvoidingImages
- `file 'Sites/keanu-to-market/src/data/chapters.ts'` — Added getTranscendenceLevel
- `file 'N5/builds/keanu-to-market/completions/W4.2.json'` — Worker completion report

## Recommendations

1. **Add bundle size monitoring** to site builds - alert if production bundle changes by >5%
2. **Document vite.config.ts** changes in commit messages explicitly
3. **Test production build locally** before deploying when modifying build config

## Tags

#keanu-to-market #vite #debugging #hmr #level-upper
