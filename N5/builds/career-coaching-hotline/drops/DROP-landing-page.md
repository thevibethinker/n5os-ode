# DROP: Career Coaching Hotline Landing Page

## Context

The Careerspan Career Coaching Hotline is an AI-powered career coaching phone line. Callers talk to **Zozie** (Z-O-Z-I-E), an AI career coach built on a decade of real coaching expertise from Vrijen Attawar, founder of Careerspan.

- **Phone number:** +1 (857) 444-7531
- **Free tier:** 15 minutes lifetime per phone number
- **Paid credits:** Pay-as-you-go credit packs (Stripe payment links TBD — being built in a parallel thread)

## What Needs to Be Built

A landing page at `va.zo.space/hotline` (or a better path — V is open to renaming).

**Naming note:** V wants this more clearly branded as the "Career Coaching Hotline" or "Careerspan Career Coaching Hotline" — not just "hotline."

### Page Content

The page should cover:

1. **Hero / Header**
   - Name: Careerspan Career Coaching Hotline
   - Tagline: Something like "Free AI career coaching. Call anytime." or "Career advice from an AI coach built on a decade of real expertise."
   - Phone number prominently displayed: +1 (857) 444-7531
   - CTA: "Call Now" (tel: link for mobile)

2. **What It Is**
   - AI career coach named Zozie
   - Built on Vrijen Attawar's career coaching methodology
   - Available 24/7, no appointment needed
   - First 15 minutes free

3. **What Zozie Can Help With**
   - Resume strategy & optimization
   - Interview preparation
   - Job search strategy
   - Career pivots & transitions
   - Salary negotiation
   - LinkedIn optimization
   - Understanding how hiring actually works

4. **How It Works**
   - Call the number
   - Talk to Zozie — she'll diagnose your situation and give actionable advice
   - 15 minutes free, then purchase credits for more time

5. **Pricing Section**
   - Free: 15 minutes (lifetime per phone number)
   - Starter: $15 for 30 minutes
   - Standard: $30 for 60 minutes
   - Pro: $50 for 120 minutes
   - Stripe payment link buttons (URLs will be provided from the parallel Stripe thread)
   - Note: Credits are tied to your phone number

6. **About Careerspan**
   - Brief mention of Vrijen Attawar and Careerspan
   - Link to mycareerspan.com for deeper coaching
   - "Want hands-on coaching? Book at mycareerspan.com"

7. **Footer**
   - Careerspan branding
   - Links: mycareerspan.com, Twitter @thevibethinker

### Design Direction

- Clean, modern, professional
- Dark or light — V's call (check existing va.zo.space pages for design language)
- Mobile-first (people will click from their phones)
- The phone number should be tappable on mobile
- Don't overdesign — let the content breathe

### Identity Guidelines

- The AI is **Zozie**, not V, not Vrijen
- Zozie is female
- Zozie is an AI career coach — don't hide this, lean into it
- Vrijen Attawar is the founder of Careerspan, referenced as the source of expertise
- Tone: direct, practical, no-BS — matches Zozie's voice

## Technical Notes

- This is a zo.space page (use `update_space_route`)
- Route: `/hotline` (or suggest a better path)
- Should be **public** (no auth required)
- Payment link URLs are placeholders until the Stripe thread delivers them — use `#starter`, `#standard`, `#pro` as placeholder hrefs

## Deliverables

1. Live page at the chosen route
2. Mobile-friendly with tappable phone number
3. Placeholder payment buttons (to be wired up with real Stripe links)
4. Clean design consistent with va.zo.space
