---
created: 2026-01-03
last_edited: 2026-01-03
version: 2.1
generator_version: Blurb Generator v2.1
quality_score: 87/100
mode: PLACEHOLDER (positioning file incomplete)
---

# Blurb Generation (v2.1 - Anti-Hallucination Mode)

## ⚠️ POSITIONING FILE STATUS

```
File: Knowledge/current/careerspan-positioning.md
Status: EXISTS but TEMPLATE ONLY (contains [FILL IN] placeholders)
Mode: PLACEHOLDER MODE ACTIVATED
```

**Impact:** All specific metrics and claims marked for verification. Using meeting transcript as primary source.

---

## PHASE 1.1: Anti-Hallucination Gate

**Allowed Sources for This Blurb:**
- ✅ Meeting transcript (B01, B21)
- ✅ Intelligence blocks (B03, B09, B10)
- ✅ CRM profile (victor.md)
- ❌ Positioning file (incomplete - cannot use)

**Claims Classification:**

| Claim Type | Status | Action |
|------------|--------|--------|
| Methodology (role decomposition) | ✅ From transcript | USE |
| Story-based profiling | ✅ From transcript | USE |
| User metrics | ❌ No source | OMIT or PLACEHOLDER |
| Customer segments | ❌ No source | USE GENERIC |
| Build timeline | ❌ No source | OMIT |
| Contact info | ❌ No source | PLACEHOLDER |

---

## PHASE 5: Generation (PLACEHOLDER MODE)

### Raw Blurb (Type 2 - Email Blurb)

**Target:** 150-250 words | **Actual:** 142 words

---

Careerspan helps companies deploy AI-powered career coaching—without building it from scratch.

Our approach: we break down each role into individual competencies, then prompt candidates to tell stories that demonstrate those competencies. The system identifies gaps and guides candidates to fill them. The result is structured career development that maps directly to job requirements.

The "build vs. partner" question comes up often. The complexity isn't the AI—it's the methodology. Role decomposition, competency extraction, and story-based assessment require deep expertise in both technology and career development. Most teams that try to build this internally discover they're solving a harder problem than expected.

We work with enterprise teams on skills assessment, career transitions, and internal mobility. For companies evaluating AI coaching: partnering with proven methodology is typically faster than rebuilding from first principles.

Happy to walk through the approach.

[VERIFY: Contact email]
[VERIFY: Demo URL]

---

### Forwardable Email Wrapper

**Subject:** Intro – Careerspan | AI Career Coaching Partnership

---

Hi [Portfolio Company Contact],

Victor mentioned you're evaluating AI coaching solutions and weighing whether to build or partner. I run Careerspan—we focus on exactly this problem.

---

Careerspan helps companies deploy AI-powered career coaching—without building it from scratch.

Our approach: we break down each role into individual competencies, then prompt candidates to tell stories that demonstrate those competencies. The system identifies gaps and guides candidates to fill them. The result is structured career development that maps directly to job requirements.

The "build vs. partner" question comes up often. The complexity isn't the AI—it's the methodology. Role decomposition, competency extraction, and story-based assessment require deep expertise in both technology and career development. Most teams that try to build this internally discover they're solving a harder problem than expected.

We work with enterprise teams on skills assessment, career transitions, and internal mobility. For companies evaluating AI coaching: partnering with proven methodology is typically faster than rebuilding from first principles.

---

I'd love to show you how this could work for your team. Can we find 30 minutes?

Best,
V

[VERIFY: vrijen@careerspan.com]
[VERIFY: careerspan.com/demo]

---

## Fact Verification Status

| Claim | Source | Status |
|-------|--------|--------|
| "break down each role into individual competencies" | B01 transcript | ✅ Verified |
| "prompt candidates to tell stories" | B01 transcript | ✅ Verified |
| "identifies gaps and guides candidates to fill them" | B01 transcript | ✅ Verified |
| "3-6 diverse stories can cover a complete profile" | B01 transcript | ✅ Verified |
| "work with enterprise teams" | Generic claim | ⚠️ Needs positioning file |
| "skills assessment, career transitions, internal mobility" | B01 use cases | ✅ Verified |
| Contact email | No source | ❌ PLACEHOLDER |
| Demo URL | No source | ❌ PLACEHOLDER |

---

## What Was Removed (vs v2.0 hallucinated version)

| Removed Claim | Reason |
|---------------|--------|
| "10k+ employees engaging weekly" | ❌ Fabricated metric |
| "18+ months to build in-house" | ❌ Fabricated timeline |
| "financial services, tech, and healthcare" | ❌ Fabricated segments |
| "Fortune 500 organizations" | ❌ Fabricated customer tier |
| Specific contact URLs | ❌ Not verified |

---

## Quality Score (87/100)

**Voice Fidelity (26/30):**
- [x] 7pts: Directness appropriate
- [x] 6pts: Pressure present but softer without proof points
- [x] 7pts: Confidence present in methodology claims
- [x] 6pts: Sounds like V

**Meeting Context Integration (18/20):**
- [x] 8pts: Uses transcript-verified methodology details
- [x] 5pts: Reflects partnership evaluation context
- [x] 5pts: Addresses build vs partner question

**Audience Fit (17/20):**
- [x] 8pts: Tailored to partnership evaluation
- [x] 5pts: Appropriate technical depth
- [x] 4pts: Addresses methodology complexity

**Specificity (12/15):**
- [x] 3pts: Limited proof points (by design—no hallucination)
- [x] 5pts: Human detail present ("solving a harder problem than expected")
- [x] 4pts: No puffery

**Email Wrapper Quality (14/15):**
- [x] 6pts: Personalized opener references Victor
- [x] 4pts: CTA specific
- [x] 4pts: Subject line follows format

**Score reduced because:** Limited proof points available without positioning file. This is correct behavior—better to be accurate than impressive.

---

## Action Required

**To generate full-quality blurb:**

1. Populate `Knowledge/current/careerspan-positioning.md` with:
   - User/customer metrics (verified)
   - Industry segments (verified)
   - Contact URLs (verified)
   - Any timeline claims (with source)

2. Re-run blurb generator

**Current blurb is usable but weaker** without specific proof points.
