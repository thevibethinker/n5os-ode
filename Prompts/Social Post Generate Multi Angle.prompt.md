---
description: 'Command: social-post-generate-multi-angle'
tool: true
tags:
- social
- content
- linkedin
- reflection
- knowledge-enrichment
---
# Social Post Generation (Multi-Angle)

**Purpose:** Generate LinkedIn posts that explore distinct angles from source material (reflections, meeting notes, etc.) with light-touch knowledge enrichment.

**Key principle:** Generate **one angle per execution** (not 3 variants in one go) to preserve full attention and quality per post.

---

## Workflow

### Step 1: Source Material Selection

Identify source:
- Reflection: `N5/records/reflections/outputs/{date}_{topic}/detail.md`
- Meeting: `N5/records/meetings/{date}_{name}/B01_DETAILED_RECAP.md`
- Digest: `N5/digests/{type}-{date}.md`
- Ad-hoc note: `Documents/` or `Records/Temporary/`

### Step 2: Angle Identification

Analyze source and **propose 3-5 distinct angles**:

**Angle types:**
1. **Founder pain point** — Lead with relatable struggle, show solution
2. **Technical differentiation** — "Here's how we solved X differently"
3. **Behind-the-scenes build** — Process/learning from building the thing
4. **ROI/outcome story** — Concrete before/after with metrics
5. **Contrarian take** — Challenge conventional wisdom in the space
6. **Meta-observation** — Pattern you've noticed across clients/industry

**Example (Zo GTM reflection):**
- Angle 1: Founder pain → "Tool sprawl is killing your context"
- Angle 2: Technical → "Why files beat databases for personal automation"
- Angle 3: Build story → "I built my own AI OS instead of using Notion AI"
- Angle 4: ROI → "I saved 8 hours/week by automating my reflection pipeline"

### Step 3: Knowledge Enrichment Scan (Light-Touch)

Before generating, scan stable knowledge for enrichment details:

**Sources:**
- `Knowledge/personal-brand/` — Bio, positioning, experience markers
- `N5/prefs/communication/voice.md` — Tone dials, style patterns
- `Knowledge/crm/individuals/` — Client/stakeholder context (anonymize if public)
- Recent outputs (`N5/digests/`, `N5/records/reflections/outputs/`) — Fresh examples

**What to extract:**
- Specific credentials ("decade of coaching" not "years of experience")
- Concrete examples ("77 stakeholder profiles in Knowledge/" not "I track relationships")
- Named tools/systems ("N5 OS" not "my system")
- Quantified outcomes ("8 hours/week saved" not "more productive")

**Light-touch rule:** Extract 3-5 enrichment details max. Don't overload.

### Step 4: Generate Post (One Angle, Full Focus)

**Execution:**
```bash
# Option A: Using script (if working)
python3 N5/scripts/n5_linkedin_post_generate.py \
  --seed "$(cat path/to/source.md)" \
  --mode thought-leadership \
  --target-length 250

# Option B: Direct generation via Zo chat
command 'N5/commands/social-post-generate-multi-angle.md' with:
- Source: {file path}
- Angle: {selected angle}
- Enrichment: {3-5 knowledge details}
```

**Post structure:**
1. **Hook** (1-2 sentences) — Angle-driven opener
2. **Body** (3-5 bullets or short paragraphs) — Core insight + enrichment
3. **Proof** (1 concrete example) — From your actual work/system
4. **CTA** (1 sentence) — Aligned with angle + objective

**Length targets:**
- Thought leadership: 200-300 words
- Quick insight: 100-150 words
- Story/case study: 300-400 words

### Step 5: Save + Document Angle

**Naming convention:**
```
Documents/Social/LinkedIn/{date}_{topic}_{angle-slug}_post.md
```

**Example:**
```
Documents/Social/LinkedIn/2025-10-20_zo-gtm_founder-pain_post.md
Documents/Social/LinkedIn/2025-10-20_zo-gtm_technical-diff_post.md
Documents/Social/LinkedIn/2025-10-20_zo-gtm_build-story_post.md
```

**Metadata block (add to each post):**
```markdown
<!-- Metadata
Source: {file path}
Angle: {angle type}
Enrichment: {knowledge sources used}
Generated: {timestamp}
Intent: {aligned objective}
-->
```

---

## Quality Checklist

- [ ] Hook is angle-specific (not generic)
- [ ] At least 1 enrichment detail from Knowledge/ used
- [ ] At least 1 concrete example from actual work
- [ ] No clichés/stop-verbs (paradigm, deep dive, game-changer)
- [ ] CTA matches intent (demo booking, conversation starter, thought leadership)
- [ ] Length within target (200-300 for thought leadership)
- [ ] Metadata block complete

---

## Anti-Patterns

**❌ Don't:** Generate 3 variants in one execution (splits attention)
**✅ Do:** Generate 1 post per angle, sequentially

**❌ Don't:** Use generic credentials ("experienced founder")
**✅ Do:** Use specific enrichment ("decade coaching founders, 4 years in tech")

**❌ Don't:** Invent examples ("helped a client save time")
**✅ Do:** Use actual artifacts ("file 'N5/digests/daily-meeting-prep-2025-10-20.md' auto-generated daily")

**❌ Don't:** Ignore the objective (why are you posting this?)
**✅ Do:** Align CTA with intent (demo booking, thought leadership, community building)

---

## Example Execution

**Source:** `N5/records/reflections/outputs/2025-10-20_zo-system-gtm/detail.md`

**Proposed angles:**
1. Founder pain point (tool sprawl)
2. Technical differentiation (files > databases)
3. Build story (why I built my own AI OS)

**Selected angle for this execution:** #1 (Founder pain point)

**Knowledge enrichment scan:**
- Bio: "decade of career coaching, 4 years Careerspan founder"
- System: "N5 OS, 77 stakeholder profiles, 11 automated agents"
- Example: "voice memo → auto-processed into Knowledge/ in <5 min"

**Output:** `Documents/Social/LinkedIn/2025-10-20_zo-gtm_founder-pain_post.md`

**Next execution:** Repeat workflow with angle #2 in fresh session.

---

## Integration Notes

**For demo sync:** When creating posts to support demos, include angle that teases demo content (e.g., "Here's what I'll show you" → drive bookings)

**For campaigns:** Generate 3-5 posts over 3-5 days, each exploring different angle, to maximize reach across audience segments

**For knowledge building:** Each post becomes training data for voice/style evolution (save to `Knowledge/personal-brand/social-content/linkedin/`)

---

**Version:** 1.0  
**Created:** 2025-10-20  
**Owner:** V (Careerspan)
