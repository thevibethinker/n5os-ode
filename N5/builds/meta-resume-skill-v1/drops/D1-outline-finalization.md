---
drop_id: D1
build_slug: meta-resume-skill-v1
spawn_mode: auto
created: 2026-01-29
---

# D1: Finalize Meta Resume Outline Structure

## Objective

Produce the canonical Meta Resume document structure — section by section, with clear purpose, content specs, and anti-patterns for each.

## Context from V

**Reader:** Technical hiring manager or technical founder
**Alternative they're comparing to:** Standard recruiter pitch + resume + LinkedIn
**Careerspan's job:** Prove the candidate is worth paying attention to via unique, meaningful analysis

**3-page format:**
- **Page 1:** 30-second decision (bottom line, what's clear/not clear, decision matrix)
- **Page 2:** Depth (what you're getting, gaps, how they think, candidate context)
- **Page 3:** "[Candidate] By The Numbers" — GitHub stats, quantitative data visualization, links

**LinkedIn:** Just a link, drop it in.
**GitHub:** Essential — commit history snapshot, contribution calendar, languages, activity level.

## Key Decisions Already Made

- Visual confidence indicator (emoji) + percentage + threshold explanation
- "What's Clear / What's Not Clear" as INDEX (binary signals, no evidence)
- "Decision Matrix" moved to Page 1 (self-select out fast)
- "What You're Getting" as BODY for positive signals (evidence-backed)
- NEW: "How They Think" section — problem-solving style from story data
- NEW: "Candidate's Context" — 3-4 lines, candidate's gap explanations

**Overlap concern to resolve:**
"What's Clear" and "What You're Getting" must not duplicate. Solution: What's Clear = binary assertions only (✓ / ?). What You're Getting = evidence for the ✓ items.

## Deliverables

1. **Section-by-section spec** in `artifacts/META-RESUME-STRUCTURE-v2.md`:
   - Section name
   - Purpose (what question does it answer?)
   - Content format (table, prose, list)
   - Word/row limits
   - Data sources (which decomposed files feed it)
   - Anti-patterns (what NOT to include)

2. **Page layout sketch** — rough wireframe of 3-page structure

3. **Tone guide** — 5-7 bullet points on voice, framing, language patterns

## Reference Files

- Example output (current best): `file 'N5/builds/careerspan-profile-output-v1/output/hardik-profile-v5.md'`
- Framework doc: `file 'N5/builds/careerspan-profile-output-v1/output/ANTI-RESUME-OUTPUT-FRAMEWORK-v1.md'`
- Decomposed data sample: `file 'Careerspan/meta-resumes/inbox/hardik-flowfuse/'`

## Quality Gates

- [ ] No section overlap (each has unique purpose)
- [ ] Every section maps to specific decomposed data files
- [ ] Page 1 enables 30-second yes/no decision
- [ ] Page 2 adds depth without redundancy
- [ ] Page 3 houses all quantitative data, GitHub snapshot, and links
- [ ] Tone is founder-facing, objective, "truffle pig" aesthetic
