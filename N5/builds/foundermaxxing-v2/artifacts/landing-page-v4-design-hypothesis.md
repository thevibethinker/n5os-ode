---
created: 2026-02-20
last_edited: 2026-02-20
version: 1
provenance: con_az51K9yJBZEurSOZ
drop: D5 (reissue)
---
# The Vibe Pill — Landing Page v4 Design Hypothesis

## Reference Artifacts

- **Copy doc:** `landing-page-v4-copy.md` (v3.1)
- **Wireframe:** `Images/vibe-pill-wireframe-final.png`
- **Hero concept:** `Images/vibe-pill-hero-concept.png`
- **Mood board:** `Images/vibe-pill-mood.png`
- **FMXG helix logo:** chat-attached (black line-art helix, "FMXG", "@thevibethinker community")
- **Primary reference site:** gte.xyz — bento grid, mixed light/dark sections, technical illustration, edge-to-edge
- **Secondary references:** Mobbin features sections (bento cards with illustrations), Ramp-style metric callouts

---

## 1. Design System

### Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--white` | `#FFFFFF` | Primary background |
| `--off-white` | `#F8F8F8` | Card backgrounds, alternating sections |
| `--black` | `#0A0A0A` | Primary text, dark sections |
| `--dark` | `#111111` | Card backgrounds in dark sections |
| `--gray-100` | `#F0F0F0` | Subtle borders, bento card fills |
| `--gray-300` | `#D4D4D4` | Borders, dividers |
| `--gray-500` | `#737373` | Secondary text, captions |
| `--accent` | `#FF6B00` | Single accent (CTA hover, highlight moments) — borrowed from GTE's orange. Used SPARINGLY. 90% of the page is black/white. |

No gradients. No shadows. No blur effects. Hard edges only.

### Typography

| Role | Font | Weight | Size (desktop) |
|------|------|--------|----------------|
| Hero headline | Condensed grotesque sans (e.g., `Bebas Neue`, `Oswald`, or `Anton`) | 700/900 | 72-96px |
| Section headers | Same condensed sans | 700 | 48-56px |
| Subheadlines | Neutral sans (`Inter`, `Geist Sans`) | 500 | 20-24px |
| Body text | Same neutral sans | 400 | 16-18px |
| Card titles | Condensed sans | 700 | 24-28px |
| Captions/labels | Neutral sans, uppercase tracking | 500 | 12-14px, letter-spacing 0.1em |

The headline font does the heavy lifting. It should feel like it was stamped, not typed. The condensed width creates visual density — more information per line, more aggressive.

### Spacing & Layout

- **Max content width:** 1280px, centered
- **Section padding:** 120px vertical (desktop), 80px (mobile)
- **Edge-to-edge:** Dark sections break out of content max-width and span full viewport
- **Grid:** 12-column base. Bento cards use asymmetric column spans.
- **Card border-radius:** 12px (not zero — zero feels brutalist, we want technical-clean)
- **Card borders:** 1px solid `--gray-300` on light bg, 1px solid `#333` on dark bg

---

## 2. Section-by-Section Layout

### Section 1: HERO

**Layout:** Two-column split. Left 60%, Right 40%.

- **Left:** Headline stacked vertically, each word/phrase on its own line for maximum visual weight. Below: subline in lighter weight. Below: pill-shaped black CTA button with white text.
- **Right:** FMXG helix illustration. **Implementation: SVG with stroke-dashoffset animation** — the helix draws itself line by line on page load over ~2 seconds. This is the signature moment. The helix should extend beyond its container slightly (overflow visible) to create that edge-to-edge aggressive feel.
- **Nav bar:** Thin black bar at top. "The Vibe Pill" left (condensed sans, white on black). "Apply" right (small pill button, white outline).
- **Background:** Pure white. Let the type and helix do all the work.

**Animation:** Helix draws on load. Headline fades up with slight Y-translate (subtle, 20px, 0.6s ease-out).

### Section 2: V'S STORY (dark section)

**Layout:** Full-viewport-width black background. Content centered within max-width.

- **Top:** The opening statement. Left-aligned. White text on black. The narrative builds line by line. Each paragraph appears with a slight stagger on scroll (intersection observer, 0.1s delays).
- **Bullet list:** The three pain points (dependent, clueless, trapped) rendered as a styled list with subtle left-border accent in `--accent` orange.
- **The line:** "I've gotten pretty f*cking good at engineering agentic systems." — This line gets slightly larger type (24px vs 18px body), maybe with a faint glow or the accent color on "f*cking good" (subtle, not garish).
- **Venn diagram:** Three overlapping circles, CSS-drawn. Labels: Teaching background, Founder pedigree, Technical intuition. Circles are outlined (not filled), with the intersection zones subtly highlighted. Animate: circles slide into overlap on scroll.

### Section 3: SOCIAL PROOF

**Layout:** Back to white/off-white background. Full-width header, then two-column gallery.

- **Header:** "FROM THOSE WHO KNOW V" in condensed sans, centered. Below: horizontal rule.
- **Left column:** "BUILDERS YOU LOVE" — label in small caps with tracking. 5 quote cards stacked vertically. Each card: avatar (small circle), name + title, quote in italics, → @handle link. Cards have subtle border, white fill, slight hover lift.
- **Right column:** "FOUNDERS YOU ADMIRE" — same structure, "The empathy." as subtitle.
- **Between columns:** Thin vertical divider line.

**Animation:** Cards fade-up sequentially as they enter viewport. Left column animates first, right follows with 0.2s delay.

### Section 4: THE VIBE PILL — Bento Grid

**Layout:** Off-white background. Section header centered, then the grid.

- **Header:** "This isn't a course." on one line. "It's a room." on the next, slightly larger or bolder. Below: one-line room description.
- **Bento grid (GTE-inspired):**

```
┌────────────────────────┬───────────────┐
│                        │               │
│   Weekly Sessions      │   The Stack   │
│   (2 cols, tall)       │   (1 col)     │
│                        ├───────────────┤
│                        │  The Hotline  │
│                        │   (1 col)     │
├────────────┬───────────┴───────────────┤
│            │                           │
│  Zo-to-Zo  │   Productivity Cockpit    │
│  (1 col)   │   (2 cols, dark bg)       │
│            │                           │
├────────────┤                           │
│ The Archive│                           │
│ (1 col,    │                           │
│  dark bg)  │                           │
└────────────┴───────────────────────────┘
```

- **Card style:** White fill with 1px border on light cards. `--black` fill with white text on dark cards (Archive, Productivity Cockpit). Each card has a title in condensed sans and 2-3 lines of body text.
- **Illustrations:** Each card gets a small geometric line-art illustration (helix motif variations — curves, lines, intersections) in the top-right or as a background watermark. These should feel like technical diagrams, not clip art. Drawn in the same style as the FMXG helix.

**Animation:** Grid cards fade-up with stagger. Dark cards animate last for emphasis.

### Section 5: OBJECTIONS (dark section)

**Layout:** Full-viewport-width black background. 2×2 grid of cards.

- **Header:** "The reasons you won't do this are the reasons you should." — centered, condensed sans, white on black.
- **Cards:** Dark gray fill (`--dark`), 1px border `#333`. Each card has the objection in quotes as the title (condensed sans, white, 24px), followed by the response in body text (gray-300, 16px).
- **Interaction:** Cards could have a subtle expand/collapse — objection visible by default, response reveals on click/hover. OR all visible (simpler, more aggressive — "we already know your excuses").

**Recommendation:** All visible. No hide-and-seek. The confidence of showing all the objections AND all the answers simultaneously is part of the brand.

### Section 6: THE ASK — CTA

**Layout:** White background. Split layout or stacked.

- **Option A (split):** Left side: "Reach out." headline, body text, phone/SMS link with phone icon. Right side: black card with "Already know you want in? Apply now →" button.
- **Option B (stacked, centered):** "Reach out." as a massive centered headline (96px+). Body text centered below. Two buttons side by side: [Call/Text] and [Apply now →].

**Recommendation:** Option A (split). The asymmetry creates visual interest and gives both CTAs equal weight without competing.

- **Phone/SMS link:** Styled as a monospace-ish element, like a terminal command. Makes it feel technical and direct.

### Section 7: FOOTER

**Layout:** Minimal. White or very light gray background.

- Left: Helix logo mark (small) + "The Vibe Pill"
- Right: "A @thevibethinker community" with link
- Possibly: a thin line-art helix running the full footer width as a decorative element

---

## 3. Animation Philosophy

| Pattern | Where | Implementation |
|---------|-------|----------------|
| **Helix line-draw** | Hero (load), footer (scroll) | SVG `stroke-dasharray` + `stroke-dashoffset` |
| **Fade-up** | All text blocks on scroll | Intersection Observer, translateY(20px) → 0, opacity 0→1 |
| **Stagger** | Card grids, social proof cards | Sequential delay (0.05-0.1s per card) |
| **Venn overlap** | V's Story section | Circles translate from spread to overlapping |
| **Counter** | If any metric callouts added | countUp.js style number animation |

**Rules:**
- Duration: 0.4-0.8s. Nothing slower.
- Easing: `cubic-bezier(0.16, 1, 0.3, 1)` — fast start, gentle land.
- Trigger: once only (no re-animation on scroll back up).
- No bounce. No wobble. No spring physics. This isn't playful — it's engineered.

---

## 4. Mobile Adaptation

- Hero: Stack vertically (headline → helix → subline → CTA). Helix scales down but stays prominent.
- Bento grid: Collapse to single column, maintain card order (Weekly Sessions first).
- Social proof: Stack columns (Builders above Founders).
- Objections: Stack to single column.
- CTA: Stack vertically (Reach Out above Apply Now).
- Nav: Hamburger not needed — just logo left, "Apply" button right. Page is a single scroll.

---

## 5. Technical Implementation Notes

- **Framework:** React (zo.space page route). Single file, all sections as components.
- **Fonts:** Load via Google Fonts link in a style tag. Recommend: `Bebas Neue` (headlines) + `Inter` (body). Both free, well-optimized.
- **SVG Helix:** Hand-code a simplified helix SVG based on the FMXG logo. ~20-30 curved paths with stroke animation. This is the hardest part of the build and the most important.
- **Intersection Observer:** Native browser API, no library needed. Custom hook `useInView`.
- **Images:** Social proof avatars as placeholder circles. Venn as CSS circles. All illustrations as inline SVGs.
- **No external dependencies** beyond React (already in zo.space).

---

## 6. What This Is NOT

- ❌ Dark mode luxury (the old page)
- ❌ Soft/rounded/friendly (that's a course landing page)
- ❌ Minimal to the point of emptiness (content-rich, but tight)
- ❌ Decorated (no ornamental elements — every pixel earns its place)
- ❌ Generic SaaS template (bento grid done with intention, not template)

## What This IS

- ✅ Technical and engineered — the page feels like it was built by someone who builds
- ✅ Confident to the point of aggressive — the typography alone makes a claim
- ✅ High contrast — black/white with one accent, hard edges, no ambiguity
- ✅ The page IS the portfolio piece — visiting it should make someone think "this person operates at a different level"
- ✅ GTE's layout intelligence + FMXG's visual DNA + V's voice
