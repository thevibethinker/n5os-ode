---
created: 2025-12-22
last_edited: 2025-12-22
version: 1.0
provenance: con_BUKdDymWjbg7w2rj
---

# ZoWrapped 2025: Build Plan

A wrapped-themed end-of-year celebration of workspace growth, technical boundary-pushing, and AI collaboration.

## Open Questions
- **Billing Data:** Is there a canonical location for raw token usage/cost data? (Hypothesis: Estimate from `conversations.db` if not found).
- **Time Window:** Focus exclusively on 2025? (Yes, implied by "end-of-year").
- **Visual Style:** Should it mimic Spotify Wrapped (slides) or a more standard dashboard (like Productivity Dashboard)? (Recommendation: Slide-based celebration).

## Checklist
- [ ] Phase 1: Deterministic Extraction Engine ☐
- [ ] Phase 2: Semantic Synthesis (The "Vibe" Layer) ☐
- [ ] Phase 3: celebration-site-staging Scaffold ☐
- [ ] Phase 4: Data Binding & Animation ☐
- [ ] Phase 5: Promotion to Production ☐

## Success Criteria
- **Fidelity:** Metrics (LoC, Files, Tokens) are accurate and verifiable.
- **Narrative:** The data tells a story of "Technical pushing of boundaries."
- **Performance:** Interactive dashboard loads < 2s.
- **Persistence:** Metrics stored in `N5/data/zo_wrapped_2025.json`.

---

## Phase 1: Deterministic Extraction Engine
**Affected Files:**
- `N5/scripts/zo_wrapped/extract_stats.py` (New)
- `N5/data/zo_wrapped_raw.json` (New)

**Changes:**
1.  **Git Auditor:** Script to walk `Sites/`, `N5/`, and `Projects/` to extract `git log --shortstat` data.
2.  **DB Librarian:** Query `conversations.db` for thread counts, persona distribution, and time-of-day activity.
3.  **FS Surveyor:** Map growth of `Knowledge/`, `Records/`, and `Prompts/`.
4.  **Capability Map:** Identify unique "Command" invocations from `@` prompt usage.

**Unit Tests:**
- Verify LoC totals match a manual `cloc` check.
- Verify thread count matches UI listing.

## Phase 2: Semantic Synthesis
**Affected Files:**
- `N5/scripts/zo_wrapped/synthesize_vibe.py` (New)
- `N5/data/zo_wrapped_metrics.json` (Final schema)

**Changes:**
1.  **Trend Analysis:** Identify "The Month of [X]" (e.g., October was the month of CRM rebuild).
2.  **Persona Profile:** Classify V's main collaborator role (e.g., "The Architectural Purist").
3.  **Milestone Extraction:** Pull major build completions from `STATUS.md` files.

**Unit Tests:**
- JSON schema validation.

## Phase 3: Visual Celebration Site
**Affected Files:**
- `Sites/zo-wrapped-2025/` (New project)
- `Sites/zo-wrapped-2025/src/pages/Wrapped.tsx`

**Changes:**
1.  Scaffold Hono/Bun app using `create-website`.
2.  Implement slide-based UI (Framer Motion for "Wrapped" feel).
3.  Bind extracted JSON to visual components.

**Unit Tests:**
- Check for responsive mobile/desktop layout.

## Phase 4: Refinement & Deploy
**Affected Files:**
- `N5/scripts/promote_site.sh`

**Changes:**
1.  Final asset polish (emojis, food items per user rule).
2.  Register user service `zo-wrapped-2025`.

---

## Risks & Mitigations
- **Data Volume:** Scanning every file in `/home/workspace` could be slow.
    - *Mitigation:* Limit depth and focus on canonical directories (Sites, N5, Personal).
- **Token Accuracy:** LLMs are squishy with token counts.
    - *Mitigation:* Use `tiktoken` in the extraction script for deterministic count.
- **Trap Door:** Hardcoding the metrics schema early.
    - *Mitigation:* Use a flexible YAML-to-JSON pipeline until Phase 3.

