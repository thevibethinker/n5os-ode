---
created: 2026-01-14
last_edited: 2026-01-14
version: 1.0
provenance: con_KGkdxFqpqncEQyuu
---

# Worker B: Content Library + Cleanup

**Project:** vrijenattawar-domain-transition
**Worker ID:** B-content-library-cleanup
**Estimated Time:** 40 minutes
**Dependencies:** None

---

## Objective

Enhance the Content Library to support "inspiration" as a content type, then properly ingest the NYSKI design inspiration, and clean up the mess created earlier.

---

## Context: Content Library Current State

The Content Library lives at `/home/workspace/Knowledge/content-library/` with these current types (from `N5/scripts/content_ingest.py`):

```python
TYPE_DIRECTORIES = {
    "article": "articles",
    "deck": "decks",
    "paper": "papers",
    "book": "books",
    "report": "reports",
    "framework": "frameworks",
    "tool": "tools",
    "social-post": "social-posts",
}
```

**V's insight:** The Content Library isn't just for reading material—it's for tracking *anything* V wants to stay on top of. Inspiration is a category of that.

---

## Task 1: Enhance Content Library

**Action:** Update `/home/workspace/N5/scripts/content_ingest.py`:

1. Add `"inspiration": "inspiration"` to `TYPE_DIRECTORIES`
2. Consider if sub-categories make sense (e.g., `inspiration/web-design/`, `inspiration/branding/`) — but keep it simple for now. A flat `inspiration/` folder is fine to start.

---

## Task 2: Ingest NYSKI Inspiration

**Source Files (created in error at wrong location):**
- `/home/workspace/N5/reference/design-inspiration/nyski-inspiration.jpg` (screenshot)
- `/home/workspace/N5/reference/design-inspiration/nyski-inspiration.html` (source HTML)
- `/home/workspace/N5/reference/design-inspiration/nyski-analysis.md` (analysis)

**Action:**
1. Create `/home/workspace/Knowledge/content-library/inspiration/` directory
2. Create a properly formatted inspiration entry:
   - Main file: `nyski-founders-club.md` with YAML frontmatter (created, source_url, tags, etc.)
   - Include the analysis content
   - Reference the screenshot and HTML as assets
3. Move/copy the screenshot to the inspiration folder
4. Use the content_ingest.py script if appropriate, OR manually create if the script needs the enhancement first

**Key details to capture about NYSKI:**
- Source: https://nyski.nycfounders.club/
- Design patterns: Full-bleed dark hero, glassmorphism CTA card, clean 3-column grid, testimonial with group photo
- Why inspirational: Professional founder aesthetic, good typography hierarchy, effective social proof

---

## Task 3: Delete the Mess

**Directories to remove (created in error):**
- `/home/workspace/N5/reference/design-inspiration/` (after content is moved)
- `/home/workspace/N5/skills/` (will be handled by Worker A, but verify it's gone)

**Note:** Check n5 protection before deleting:
```bash
python3 /home/workspace/N5/scripts/n5_protect.py check /home/workspace/N5/reference/design-inspiration
```

---

## Deliverables

- [ ] `content_ingest.py` updated with "inspiration" type
- [ ] `/home/workspace/Knowledge/content-library/inspiration/` exists
- [ ] `nyski-founders-club.md` properly formatted with frontmatter
- [ ] Screenshot saved alongside the markdown
- [ ] `/home/workspace/N5/reference/design-inspiration/` deleted

---

## Completion

When done, report back with:
1. Confirmation of Content Library enhancement
2. Path to the new NYSKI inspiration file
3. Confirmation of cleanup

