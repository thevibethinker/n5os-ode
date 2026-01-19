---
created: 2026-01-19
last_edited: 2026-01-19
version: 2.0
type: build_plan
status: complete
provenance: con_RY6xUcEGGrtqqyiu
---

# Plan: VrijenAttawar.com Background Fix (v2 - Foolproof Edition)

## Problem Diagnosis (VERIFIED)

**Root Cause:** The `body::before` and `body::after` pseudo-elements in `src/styles.css` are NOT compiling into the production CSS. The build outputs a direct `background-image` on `body` at **100% opacity** instead of the intended 25% opacity pseudo-element with vignette.

**Evidence:**
- Source CSS has `body::before { opacity: 0.25; ... }`
- Compiled CSS shows `body { background-image: url(/background-lines.png); }` with NO opacity
- Live site screenshot confirms background at ~100% opacity (unreadable text)

**Secondary Issue:** The background asset is 1024x1024 — should be 3840+ for crisp display on modern screens.

---

## Target State (Reference Image)

The target is the screenshot V provided showing:
1. V pattern visible but **subdued** (~25-35% opacity)
2. Text "Vrijen Attawar" is **crisp white and fully legible**
3. Subtle **vignette** (edges darker than center)
4. No floating insignia image
5. Pattern fills viewport without tiling

---

## Execution Plan

This is a **TWO-TASK** plan. Each task is independent and has binary pass/fail criteria.

---

## TASK 1: Fix the CSS Build Issue (CODE WORK)

**Owner:** Code-capable AI (Builder)
**Dependency:** None
**Duration:** ~10 minutes

### Problem
Tailwind CSS 4's `@layer base` is not correctly compiling `::before` and `::after` pseudo-elements when they use raw CSS (not `@apply` directives).

### Solution
Move the background styling OUT of `@layer base` and use a dedicated CSS block that Vite will preserve verbatim.

### Exact Changes to `src/styles.css`

**Step 1:** Remove the background-related code from `@layer base`. Delete these lines:

```css
/* DELETE FROM @layer base: */
body::before {
  content: "";
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-image: url('/background-lines.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 0.25;
  z-index: -2;
  filter: contrast(1.2) brightness(0.8);
}

body::after {
  content: "";
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: radial-gradient(circle at center, transparent 0%, rgba(0,0,0,0.8) 100%);
  z-index: -1;
  pointer-events: none;
}
```

**Step 2:** Add a NEW section AFTER `@layer base { ... }` with this exact CSS:

```css
/* V Background - Outside @layer to ensure compilation */
body::before {
  content: "";
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  background-image: url('/background-lines.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 0.3;
  z-index: -2;
  filter: contrast(1.15) brightness(0.85);
  pointer-events: none;
}

body::after {
  content: "";
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  background: radial-gradient(ellipse at center, transparent 0%, transparent 30%, rgba(0,0,0,0.7) 100%);
  z-index: -1;
  pointer-events: none;
}
```

**Step 3:** Rebuild and deploy:
```bash
cd /home/workspace/Sites/vrijenattawar
rm -rf dist node_modules/.vite
bun run build
```

### Verification (Binary Pass/Fail)

Run these checks. ALL must pass:

```bash
# Check 1: Compiled CSS contains opacity for ::before
grep -q "opacity:" /home/workspace/Sites/vrijenattawar/dist/assets/*.css && echo "PASS: opacity found" || echo "FAIL: opacity missing"

# Check 2: Compiled CSS contains ::before or :before pseudo-element
cat /home/workspace/Sites/vrijenattawar/dist/assets/*.css | tr '}' '\n' | grep -q "::before\|:before" && echo "PASS: pseudo-element found" || echo "FAIL: pseudo-element missing"

# Check 3: Build succeeded
[ -f /home/workspace/Sites/vrijenattawar/dist/index.html ] && echo "PASS: build exists" || echo "FAIL: no build"
```

### Restart Service
```bash
# After build succeeds:
# The site service auto-restarts on file changes, but force restart if needed
```

---

## TASK 2: Upscale Background Asset (IMAGE WORK)

**Owner:** Image-generation AI
**Dependency:** None (can run in parallel with Task 1)
**Duration:** ~5 minutes

### Input
The existing V pattern at `file 'Sites/vrijenattawar/public/background-lines.png'` (1024x1024)

### Output Requirements
A new PNG file with these EXACT specifications:
- **Resolution:** 3840×3840 pixels (minimum)
- **Content:** The same V line pattern - white lines on pure black (#000000)
- **Format:** PNG, 8-bit, sRGB
- **Filename:** `background-lines-4k.png`
- **Save location:** `/home/workspace/Sites/vrijenattawar/public/background-lines-4k.png`

### Constraints (DO NOT VIOLATE)
- ❌ Do NOT add any new elements (no text, no watermarks, no extra shapes)
- ❌ Do NOT change the line pattern geometry
- ❌ Do NOT change the color scheme (must be white on black)
- ✅ DO preserve the exact line structure and spacing
- ✅ DO ensure crisp, anti-aliased lines

### Method Options (choose one)
1. **AI upscale:** Use image generation to upscale/recreate at higher resolution
2. **ImageMagick upscale:** `convert background-lines.png -filter Lanczos -resize 3840x3840 background-lines-4k.png`
3. **Regenerate:** Generate a new V pattern matching the original at 3840x3840

### After Generating

**Step 1:** Verify the output:
```bash
identify /home/workspace/Sites/vrijenattawar/public/background-lines-4k.png
# Must show: PNG 3840x3840 (or larger)
```

**Step 2:** Update the CSS to use the new file. In `src/styles.css`, change:
```css
background-image: url('/background-lines.png');
```
To:
```css
background-image: url('/background-lines-4k.png');
```

**Step 3:** Rebuild:
```bash
cd /home/workspace/Sites/vrijenattawar
bun run build
```

### Verification (Binary Pass/Fail)
```bash
# Check: Image is at least 3200px wide
WIDTH=$(identify -format "%w" /home/workspace/Sites/vrijenattawar/public/background-lines-4k.png 2>/dev/null)
[ "$WIDTH" -ge 3200 ] && echo "PASS: resolution OK ($WIDTH px)" || echo "FAIL: resolution too low ($WIDTH px)"
```

---

## Final Verification Checklist

After BOTH tasks complete, verify:

| Check | Command | Expected |
|-------|---------|----------|
| Build exists | `ls Sites/vrijenattawar/dist/index.html` | File exists |
| CSS has opacity | `grep opacity Sites/vrijenattawar/dist/assets/*.css \| head -1` | Contains `opacity:0.3` or similar |
| Hi-res image exists | `identify Sites/vrijenattawar/public/background-lines-4k.png` | Shows 3840x3840+ |
| Service is running | `curl -s -o /dev/null -w "%{http_code}" https://vrijenattawar-va.zocomputer.io` | Returns 200 |

---

## What NOT to Do (Anti-Patterns)

These are the mistakes that caused previous AIs to loop:

1. ❌ **Do NOT keep adjusting opacity values** trying to find the "right" one. The value 0.3 is correct. Stop.
2. ❌ **Do NOT try SVG conversion** unless explicitly asked. PNG is fine.
3. ❌ **Do NOT modify PersonalLanding.tsx** — the component is correct.
4. ❌ **Do NOT add drop shadows to text** — the vignette handles contrast.
5. ❌ **Do NOT create multiple asset variants** — one 4K PNG is enough.
6. ❌ **Do NOT keep rebuilding** hoping for different results — if build fails, diagnose the error.

---

## Success Criteria

The task is DONE when:
1. ✅ Live site at `https://vrijenattawar-va.zocomputer.io` shows V pattern at ~30% opacity
2. ✅ Text "Vrijen Attawar" is fully legible (white on dark background)
3. ✅ Vignette visible (edges darker than center)
4. ✅ Background image is crisp (not pixelated) on 4K displays
5. ✅ No floating insignia image visible

Visual comparison: Site should look like the TARGET screenshot (file 58aa5c / image 390), not the BROKEN screenshot (file f7d754).

---

## Handoff Notes

**For the executing AI:**
- Task 1 is the critical fix. If you only do one thing, do Task 1.
- Task 2 is a nice-to-have improvement.
- The core bug is that Tailwind's `@layer base` isn't compiling pseudo-elements correctly. Moving the CSS outside the layer fixes it.
- After making changes, REBUILD and verify. Don't assume the old build is current.
