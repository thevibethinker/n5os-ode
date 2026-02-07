---
created: 2026-02-06
last_edited: 2026-02-06
version: 1.0
provenance: con_6I5fKoKfq0TzVlzw
---

# Frontend Design Skill

**Build Slug:** `frontend-skill`
**Status:** Planning
**Architect:** Vibe Architect

## Summary

Create a flexible frontend design skill that generates high-quality landing pages and websites from varying input (vibes → assets → content), with a template capture system to reliably reproduce successful designs.

## Open Questions

- [x] Platform targets? → **Multi-platform** (Zo.space, standalone HTML, Next.js)
- [x] Option selection? → **Option B** (Skill + Template Library)
- [x] Multi-variation default? → **Opt-in** (`--variants N`)
- [x] Asset handling? → **LLM analysis** (simpler, no extraction scripts)

## Research Inputs

**Anthropic frontend-design skill** (the one Theo praised):
- Anti-patterns: purple/blue gradients, excessive animations, generic stock imagery, "AI slop" aesthetics
- Pro-patterns: Intentional whitespace, typography hierarchy, color restraint, real imagery
- Key insight: 5-variant generation lets you pick the best direction

**Vercel web-design-guidelines**:
- Focus on code quality and UX compliance
- Accessibility, semantic HTML, performance
- Complementary to aesthetic guidance

## Architecture

```
Skills/frontend/
├── SKILL.md              # Core generation instructions
├── templates/            # Captured design DNA
│   ├── _TEMPLATE.yaml    # Template format spec
│   └── *.yaml            # Individual templates
└── references/
    └── anti-patterns.md  # What to avoid (AI slop catalog)
```

## Checklist

### Phase 1: Core Skill
- [ ] Create SKILL.md with multi-platform generation instructions
- [ ] Define input spectrum (vibes → swatches → images → content)
- [ ] Write platform-specific output sections (Zo.space, HTML, Next.js)
- [ ] Include anti-pattern guardrails from research

### Phase 2: Template System
- [ ] Design template YAML schema
- [ ] Create _TEMPLATE.yaml format spec
- [ ] Write template capture instructions (how to extract DNA from a page)
- [ ] Create 1-2 seed templates from known good designs

### Phase 3: Validation
- [ ] Test: Generate Zo.space page from vibe description
- [ ] Test: Generate standalone HTML from color swatch + content
- [ ] Test: Capture template from existing page
- [ ] Test: Generate new page from captured template

## Phases

### Phase 1: Core Skill Creation

**Affected Files:**
- `Skills/frontend/SKILL.md` (create)
- `Skills/frontend/references/anti-patterns.md` (create)

**Changes:**

1. **SKILL.md** — Main skill file with:
   - Frontmatter (name, description, compatibility)
   - Input spectrum section (what the skill accepts)
   - Generation workflow (how to process inputs)
   - Platform-specific output formats:
     - Zo.space: React/Tailwind/Hono via `update_space_route`
     - Standalone HTML: Single file with inline Tailwind CDN
     - Next.js: App router page component
   - Anti-slop guardrails (what to avoid)
   - Multi-variation mode (opt-in)
   - Template application section (when a template is provided)

2. **anti-patterns.md** — Catalog of AI design slop to avoid:
   - Visual clichés (purple gradients, generic illustrations)
   - Layout sins (too much symmetry, no visual hierarchy)
   - Typography crimes (too many fonts, poor contrast)
   - Animation excess

**Unit Tests:**
- Invoke skill with minimal input ("a landing page for a consulting firm")
- Verify output includes platform selection prompt
- Verify anti-pattern language is present in generation

### Phase 2: Template System

**Affected Files:**
- `Skills/frontend/templates/_TEMPLATE.yaml` (create)
- `Skills/frontend/templates/minimal-saas.yaml` (create - seed template)
- `Skills/frontend/SKILL.md` (update - add template capture section)

**Changes:**

1. **_TEMPLATE.yaml** — Format specification:
   ```yaml
   name: template-slug
   description: What this template is good for
   source: URL or description of origin
   
   # Design DNA
   palette:
     primary: "#hex"
     secondary: "#hex"
     accent: "#hex"
     background: "#hex"
     text: "#hex"
   
   typography:
     heading_font: "Font Name"
     body_font: "Font Name"
     scale: "tight | normal | loose"
   
   layout:
     max_width: "narrow | standard | wide | full"
     spacing: "compact | balanced | airy"
     sections: ["hero", "features", "testimonials", "cta"]
   
   style_notes: |
     Freeform description of the aesthetic feel,
     specific techniques, what makes it distinctive.
   
   # Optional: Reference assets
   reference_images: []
   ```

2. **minimal-saas.yaml** — Seed template based on good SaaS landing pages

3. **SKILL.md update** — Add "Template Capture" section:
   - How to analyze an existing page
   - How to extract the design DNA
   - How to format as template YAML

**Unit Tests:**
- Parse _TEMPLATE.yaml and validate schema
- Generate page using minimal-saas template
- Verify template values appear in output

## Success Criteria

1. **Input flexibility**: Skill accepts vibes, colors, images, or full content—and produces coherent output from any starting point
2. **Platform coverage**: Can generate for Zo.space, standalone HTML, or Next.js
3. **Anti-slop**: Generated pages avoid common AI design clichés
4. **Template capture**: Can extract design DNA from any page into reusable template
5. **Template application**: Applying a template produces consistent aesthetic across different content

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Templates too rigid → boring output | Include `style_notes` freeform field for nuance |
| Templates too loose → inconsistent | Require specific palette/typography values |
| Multi-platform instructions too complex | Clear section headers, platform detection prompt |
| Anti-patterns become dated | Reference file is easily updatable |

## Trap Doors

- **Template schema**: Once templates exist, changing the schema requires migration. Design carefully.
  - Mitigation: Version field in schema, keep it minimal initially

## Handoff

Ready for Pulse orchestration:
- **Stream 1**: D1.1 (Core Skill), D1.2 (Anti-patterns reference)
- **Stream 2**: D2.1 (Template schema), D2.2 (Seed template), D2.3 (Skill update for capture)
- **Stream 3**: D3.1 (Validation tests)

Sequential dependency: Stream 2 depends on Stream 1 completion. Stream 3 depends on Stream 2.
