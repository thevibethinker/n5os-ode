---
created: 2026-02-20
last_edited: 2026-02-20
version: 1.0
provenance: con_az51K9yJBZEurSOZ
drop: D5 (reissue)
---

# FounderMaxxing Landing Page v4 — Design Brief

## Design Direction: Kill the Dark Luxury

The v3 page failed. Dark editorial luxury = black-on-black, invisible sections, generic "premium" energy that every AI course uses. The new direction is the opposite of that.

### Target Aesthetic
- **Bold, technical, clean, determined, aggressive**
- Light background (white/off-white primary canvas)
- High contrast — black type, structured grid, hard edges
- The FMXG helix logo IS the design language: geometric, woven, structural, precise
- NOT: dark mode, gold accents, whisper-quiet luxury, generic SaaS

### Primary Reference: GTE.xyz
What to steal from GTE:
- **Bento grid** — Feature cards in an asymmetric grid, each with subtle illustration/animation
- **Edge-to-edge feel** — Tight padding, wide content spans, content fills the viewport
- **Typography hierarchy** — Massive headlines, controlled body copy, clear section breaks
- **Animated elements** — Cards that reveal on scroll, subtle motion in illustrations
- **Light canvas** — White/light gray background with occasional dark contrast sections
- **Scrolling ticker strips** — Social proof as horizontal ticker (GTE uses "Funds / Traders / Angels")

What NOT to copy from GTE:
- The crypto/trading visual language
- The specific color palette (orange accents)
- The 3D coin hero animation

### FMXG Brand Language
The helix logo (double-strand, line-art, black on white, geometric) should inspire:
- Section dividers or background motifs that echo the woven line pattern
- A signature illustration style: line-art, structural, maybe parametric
- Character avatars derived from the helix aesthetic (like Notion's team illustrations but geometric/structural)
- Use sparingly — helix as accent, not wallpaper

### Typography
- Mixed: Serif headlines (editorial authority) + condensed geometric sans body (technical precision)
- Headlines: Large, bold, high contrast
- Think: crisp, punchy, epithetic lines — one sentence that hits hard per section
- Body: Clean sans, generous line height, readable

### Color
- Primary: White/off-white canvas
- Text: Near-black (#0A0A0A or similar)
- Accent: Derived from or complementary to the helix (could be a single bold color — needs testing)
- Occasional dark section for contrast breaks (e.g., social proof gallery on dark bg)

### Animation
- Scroll-triggered reveals (sections fade/slide in)
- Possible: parallax on hero elements, motion typography on key lines
- Bento cards: subtle hover states, maybe micro-animations in illustrations
- Keep classy — no bouncing, no gratuitous motion

### Layout: Edge-to-Edge
- Tighter padding, wider content spans
- Content nearly fills viewport width (not narrow centered column)
- Bento grid sections span full width
- Generous vertical breathing room between sections

---

## Information Architecture: The Story Arc

### Section 1: HERO — The Gut Punch
**Purpose:** Name the fear every founder feels. Stop the scroll.

**Key line (prominent, not necessarily the hero headline):**
> "In your rush to keep your company ahead, you risk falling behind on AI."

**Hero approach options:**
- Option A: The line IS the hero, full-bleed, massive type
- Option B: A bolder, shorter opening ("You're stuck.") with the key line as the immediate follow
- Option C: Motion typography that builds the line word by word

**Above the fold:** The problem statement + one CTA. Minimal. No clutter.

**CTA:** "See if you qualify" → scrolls or links to intake

### Section 2: THE PROOF — Who Is V?
**Purpose:** Immediately establish credibility. Pound with signal.

**Key proof points (in order of impact):**
1. "I read zero lines of code. 416+ commits on GitHub, none of them code."
2. "10 years teaching people how to think" (career coaching → AI coaching pipeline)
3. "Building Careerspan — in the arena, not the commentary booth"
4. "The best non-technical coder most people have met"

**Design:** Could be a bold statement section with the Venn diagram visualization, or a personal/founder letter format. This is the "non-technical messiah" moment — the reader should think "holy shit, this person gets it AND does it."

**Social proof gallery — DUAL SIDED:**

Two distinct galleries, side by side or stacked:

**Gallery A: Technical People** (engineers, CTOs, technical founders)
- 5 placeholder slots
- Each: Avatar, Name, Title/Company, 2-3 line quote, link to Twitter/socials
- Signal: "Even technical people respect V's approach"

**Gallery B: Non-Technical People** (operators, founders, executives)
- 5 placeholder slots
- Same format
- Signal: "People like you have transformed their relationship with AI through V"

**Design for social proof:**
- Make credibility easy to scan — prominent name/title, social link visible
- Avatar style: Could use FMXG helix-inspired character illustrations (like Notion's team art)
- Scrolling ticker or grid layout

### Section 3: THE SOLUTION — What Is FounderMaxxing?
**Purpose:** Concrete answer to "what do I actually get?"

**GTE-style bento grid for the value stack:**
- Weekly sessions (Phase 1: demo, Phase 2: build-along, Phase 3: variance)
- "Every week you leave with something working" (bold, repeated)
- The curated room (application-only, V interviews everyone)
- F1 analogy: "Your setup is your competitive advantage"
- Zo infrastructure: credits, AI proxy, co-building hotline, Zo-to-Zo mentorship

**Each bento card:** Title + 1-2 line description + subtle illustration/icon

### Section 4: OBJECTION HANDLING — Why You're Stuck Without This
**Purpose:** Address the internal monologue that prevents action.

**Key objections to surface and crush:**

| Objection | Response |
|-----------|----------|
| "I don't have time for this" | "That's exactly why you need it. You're spending 10x the time on a local optimum." |
| "My current system works fine" | "Fine isn't a competitive advantage. You're optimized for yesterday." |
| "I'm already good at AI" | "Good at which AI? The landscape shifts every 6 months. Are you good at the meta-layer?" |
| "I can figure this out myself" | "You can. It'll take you 18 months. Or you can get there in 8 weeks with someone who's already mapped the territory." |

**Design:** Could be an accordion, a bold statement wall, or a conversational Q&A format. The tone should be direct — not defensive, not apologetic. Aggressive but respectful.

### Section 5: THE ASK — Dual CTA
**Purpose:** Convert.

**Primary CTA: Hotline Intake**
> "Text or call [number] to see if you're a fit"
- This IS the intake. No form. A conversation.
- Prominent, visually distinct, the clear recommended action
- Subtext: "Takes 5 minutes. We'll tell you if FounderMaxxing is right for you."

**Secondary CTA: Direct Apply**
> "Ready now? Apply directly"
- For people who want to skip the conversation
- Links to existing application flow (D6)

**Tertiary (future): Pricing preview**
- Not on v4 launch, but leave structural room for it

### Section 6: FOOTER
- FMXG logo
- "A @thevibethinker community"
- Minimal links

---

## Technical Constraints

### What exists and must integrate:
- `/api/foundermaxxing-apply` — Application API (SQLite backend)
- `/api/foundermaxxing-coupons` — Promo code system
- `/api/foundermaxxing-admin` — Admin dashboard API
- `/foundermaxxing/admin` — Admin dashboard (auth-gated)
- Stripe payment link: `https://buy.stripe.com/8x28wP9sS3wF4DLgi2bsc0e`
- Promo codes: FOUNDING (15 cap, $100/mo), LAUNCH2026 (100 cap, $150/mo x3)
- Images: foundermaxxing-og.png, foundermaxxing-session.png, foundermaxxing-venn-v2.png

### What's new:
- D9 hotline intake will provide a phone number for the primary CTA (placeholder for now)
- Social proof placeholders (V will provide names/quotes tomorrow)
- New visual assets needed: bento card illustrations, helix-derived motifs

### Platform:
- zo.space route: `/foundermaxxing` (React + Tailwind, public)
- All animations via CSS or lightweight JS (no heavy libraries)
- Must be fast — no layout shift, minimal JS bundle

---

## What "WOW" Looks Like

The visitor should think:
1. "This person has built something incredible with vibe coding" (quality of the page itself is proof)
2. "These thoughts are unusually sharp for someone in this space" (the copy hits different)
3. "I need to be in this room" (social proof + scarcity + the intake conversation as a draw)

The page itself is a portfolio piece. The design quality IS the argument.
