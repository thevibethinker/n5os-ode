---
created: 2025-12-17
last_edited: 2025-12-17
version: 1.0
provenance: con_9dPA5Z6pH6Vb717j
---

# Knowledge/reference/

**Canonical location for evergreen reference documents**

---

## What Goes Here

| ✅ Include | ❌ Exclude |
|-----------|-----------|
| Research reports & statistics | Meeting notes |
| Industry primers & explainers | Drafts or WIP documents |
| Foundational company docs | Temporary analysis |
| Data compilations | Conversation artifacts |
| Strategic frameworks | Personal reflections |

## Guidelines

1. **Evergreen content only** — documents that remain useful over time
2. **High signal-to-noise** — curated, not dumped
3. **Structured markdown** — frontmatter required (created, version, tags, source)
4. **Clear naming** — descriptive slugs with year (e.g., `ta-tech-research-2025.md`)

## Frontmatter Template

```yaml
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
provenance: con_XXXXX  # conversation that created it
source: "Original source name/URL"
tags: [topic1, topic2, topic3]
---
```

## Current Contents

| File | Description |
|------|-------------|
| `ta-tech-research-2025.md` | TAtech/Aspect43 research on TA market segments |
| `career-development-statistics-v4-2025.md` | Comprehensive hiring/career stats compilation |
| `careerspan-tech-foundation-2025.md` | Careerspan platform architecture & differentiators |
| `how-ats-systems-work-2025.md` | ATS parsing, scoring, and optimization guide |
| `vrijens-pov-careerspan-future-2025.md` | Founder vision for Careerspan's strategic direction |

## How This Integrates with Semantic Memory

Files in this directory are automatically indexed into `brain.db` when the semantic reindex runs. They become searchable via RAG queries.

**To add a new document:**
1. Create markdown file with proper frontmatter
2. Run `python3 /home/workspace/N5/scripts/semantic_reindex_service.py` (or wait for scheduled reindex)
3. Verify with: `sqlite3 /home/workspace/N5/cognition/brain.db "SELECT path FROM resources WHERE path LIKE '%reference%';"`

**To remove a document:**
1. Delete the file
2. Run reindex (stale entries are cleaned up automatically)

