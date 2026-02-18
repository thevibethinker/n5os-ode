---
created: 2026-02-12
last_edited: 2026-02-12
version: 1
type: build_plan
status: draft
---
# Plan: Zo Hotline Knowledge Expansion

**Objective:** Expand Zoseph’s hotline knowledge base with high-signal patterns, use cases, anti-patterns, and technical advice, then wire them into the hotline’s concept mapping + prompt so callers can reliably access the new material.

**Trigger:** V requested launching the knowledge expansion worker based on `hotline-knowledge-expansion-brief.md` (prior conversation workspace).

**Key Design Principle:** Simple > easy. Add knowledge in small, voice-optimized files and expose them via a curated concept map (stable interface) rather than building a “smart” retrieval system.

---

## Open Questions

- [x] **How much to add?** Target ~18 new files total, each <1500 chars, to keep the hotline crisp and avoid knowledge sprawl.
- [x] **How should it be exposed?** Use the existing `explainConcept` → `conceptFiles` mapping (curated keys + aliases) instead of adding dynamic retrieval.

---

## Nemawashi (Alternatives Considered)

1. **A: Add files only; no webhook/prompt wiring**
   - Pros: Lowest risk, zero code changes.
   - Cons: New knowledge is hard to access; Zoseph won’t reliably reference it.

2. **B (Chosen): Add files + curated concept map + prompt section updates**
   - Pros: Simple, deterministic, caller-friendly. Clear “API” (concept keys) for knowledge access.
   - Cons: Requires ongoing curation of keys.

3. **C: Replace concept map with dynamic semantic retrieval over Knowledge/**
   - Pros: No key curation; more flexible.
   - Cons (Trap Door): More runtime complexity, higher failure surface, harder to debug, and risk of pulling the wrong snippet under voice constraints.

---

## Checklist

### Phase 1: Create Knowledge Packs (Wave W1)
- ☐ D1.1 Create Architectural Patterns knowledge pack
- ☐ D1.2 Create Use Cases & Stories knowledge pack
- ☐ D1.3 Create Lessons Learned / Anti-Patterns knowledge pack
- ☐ D1.4 Create Technical Advice knowledge pack
- ☐ Test: All new files exist and each is <1500 characters

### Phase 2: Integrate + Verify Reachability (Wave W2)
- ☐ D2.1 Update `conceptFiles` mapping + tool description + system prompt
- ☐ Test: Every `conceptFiles` entry resolves to an existing file/dir in `Knowledge/zo-hotline/`

---

## Phase 1: Create Knowledge Packs (Wave W1)

### Affected Files
- `Knowledge/zo-hotline/70-architectural-patterns/webhook-agent-notification.md` - CREATE - Pattern blueprint
- `Knowledge/zo-hotline/70-architectural-patterns/dataset-scheduled-agent-dashboard.md` - CREATE - Pattern blueprint
- `Knowledge/zo-hotline/70-architectural-patterns/email-intake-pipeline-output.md` - CREATE - Pattern blueprint
- `Knowledge/zo-hotline/70-architectural-patterns/multi-persona-routing.md` - CREATE - Pattern blueprint
- `Knowledge/zo-hotline/70-architectural-patterns/skills-as-executable-memory.md` - CREATE - Pattern blueprint

- `Knowledge/zo-hotline/50-use-case-inspiration/daily-briefing-agent.md` - CREATE - Use case story
- `Knowledge/zo-hotline/50-use-case-inspiration/content-pipeline.md` - CREATE - Use case story
- `Knowledge/zo-hotline/50-use-case-inspiration/crm-automation.md` - CREATE - Use case story
- `Knowledge/zo-hotline/50-use-case-inspiration/health-tracking-alerts.md` - CREATE - Use case story

- `Knowledge/zo-hotline/80-lessons-anti-patterns/over-engineering-day-1.md` - CREATE - Anti-pattern
- `Knowledge/zo-hotline/80-lessons-anti-patterns/skipping-level-1.md` - CREATE - Anti-pattern
- `Knowledge/zo-hotline/80-lessons-anti-patterns/no-bio-no-memory.md` - CREATE - Anti-pattern
- `Knowledge/zo-hotline/80-lessons-anti-patterns/agent-sprawl.md` - CREATE - Anti-pattern
- `Knowledge/zo-hotline/80-lessons-anti-patterns/skipping-verification.md` - CREATE - Anti-pattern

- `Knowledge/zo-hotline/90-technical-advice/rules-vs-personas-vs-skills.md` - CREATE - How-to guide
- `Knowledge/zo-hotline/90-technical-advice/debugging-scheduled-agents.md` - CREATE - How-to guide
- `Knowledge/zo-hotline/90-technical-advice/zo-space-best-practices.md` - CREATE - How-to guide
- `Knowledge/zo-hotline/90-technical-advice/integration-patterns.md` - CREATE - How-to guide

### Changes

**1.1 Voice-optimized knowledge files:**
- Each new file has YAML frontmatter.
- Each file is <1500 characters.
- Each file uses a consistent, skimmable structure (bullets, short sections).

**1.2 Caller usefulness bias:**
- Prefer concrete “build recipes” and “first version” over broad explanation.
- Include failure modes so Zoseph can quickly diagnose what’s wrong.

### Unit Tests
- File existence: all paths above exist after Wave W1 completes.
- Size bound: each created file is <1500 characters.

---

## Phase 2: Integrate + Verify Reachability (Wave W2)

### Affected Files
- `Skills/zo-hotline/scripts/hotline-webhook.ts` - UPDATE - Expand `conceptFiles` mapping and `explainConcept` tool description
- `Skills/zo-hotline/prompts/zoseph-system-prompt.md` - UPDATE - Expand “What You Advise On” to include the new categories

### Changes

**2.1 Curated concept map expansion:**
- Add stable concept keys + aliases (hyphen + underscore variants) that map to new knowledge files and folders.
- Keep the mapping curated (avoid hundreds of keys).

**2.2 Prompt surface area update:**
- Add short bullets to the system prompt so Zoseph proactively offers the new categories.

**2.3 Sanity verification:**
- Run a small deterministic check (python) to ensure every `conceptFiles` entry points to an existing file or directory.

### Unit Tests
- Mapping verification: every mapped file/dir exists.

---

## Trap Doors (Irreversible / High Cost to Reverse)

1. **Switching from curated map → dynamic retrieval** (Alternative C)
   - Cost to reverse: medium-high (code, prompts, latency tuning, debugging).
   - We are explicitly NOT doing this in this build.

2. **Exploding the public concept-key surface**
   - Once callers learn keys, renaming keys breaks usability.
   - Mitigation: add aliases instead of renaming; keep keys stable.

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Drop | Status |
|------------|------|--------|
| `Knowledge/zo-hotline/70-architectural-patterns/*` (create) | D1.1 | ☐ |
| `Knowledge/zo-hotline/50-use-case-inspiration/*.md` (new files only) | D1.2 | ☐ |
| `Knowledge/zo-hotline/80-lessons-anti-patterns/*` (create) | D1.3 | ☐ |
| `Knowledge/zo-hotline/90-technical-advice/*` (create) | D1.4 | ☐ |
| `Skills/zo-hotline/scripts/hotline-webhook.ts` (update) | D2.1 | ☐ |
| `Skills/zo-hotline/prompts/zoseph-system-prompt.md` (update) | D2.1 | ☐ |

### Token Budget Summary

| Drop | Brief (tokens) | Expected file context | Total % | Status |
|------|----------------|-----------------------|---------|--------|
| D1.1 | low | low | <10% | ✓ |
| D1.2 | low | low | <10% | ✓ |
| D1.3 | low | low | <10% | ✓ |
| D1.4 | low | low | <10% | ✓ |
| D2.1 | low | medium | <15% | ✓ |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE Drop (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All Drops within 40% token budget (expected)
- [x] Wave dependencies are valid (Wave W2 waits on Wave W1)
- [x] `python3 N5/scripts/mece_validator.py zo-hotline-knowledge-expansion` passes (nice-to-have; build uses Pulse Drops, not legacy workers)

---

## Drops

| Wave | Drop | Title | Brief File |
|------|------|-------|------------|
| W1 | D1.1 | Architectural patterns knowledge pack | `drops/D1.1-architectural-patterns.md` |
| W1 | D1.2 | Use cases & stories knowledge pack | `drops/D1.2-use-cases.md` |
| W1 | D1.3 | Lessons learned & anti-patterns knowledge pack | `drops/D1.3-anti-patterns.md` |
| W1 | D1.4 | Technical advice knowledge pack | `drops/D1.4-technical-advice.md` |
| W2 | D2.1 | Integrate mapping + prompt | `drops/D2.1-integrate-mapping-and-prompt.md` |

---

## Success Criteria

1. 18 new knowledge files exist under `Knowledge/zo-hotline/` across the new categories, each with YAML frontmatter and <1500 chars.
2. `Skills/zo-hotline/scripts/hotline-webhook.ts` includes concept keys that map to the new knowledge packs.
3. `Skills/zo-hotline/prompts/zoseph-system-prompt.md` references the new categories under “What You Advise On.”
4. A deterministic sanity check confirms every concept map entry resolves to an existing file/dir.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| New content is too verbose for voice | Enforce <1500 chars per file, include char-count check in Drops |
| Concept map becomes unmanageable | Keep it curated; prefer folder-level entries + aliases |
| Integration drop adds keys that point to missing files | Run existence check and report in deposit |

---

## Level Upper Review

_Not invoked for this build._
