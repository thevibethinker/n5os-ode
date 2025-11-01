# Knowledge Lookup Guide

**Module:** Knowledge Management  
**Version:** 2.0.0  
**Date:** 2025-10-09

---

## Purpose

This guide directs where to search for canonical information before answering queries or making decisions.

**Principle:** Always check knowledge base first; prefer facts from there and update if gaps are found.

---

## Topic-Specific Knowledge

### Career Spans / Careerspan (Company)

**Always check first:**
1. `file 'Knowledge/stable/company/overview.md'` — Mission, product, philosophy
2. `file 'Knowledge/stable/company/strategy.md'` — GTM, positioning, wedge strategy
3. `file 'Knowledge/stable/company/history.md'` — Founding story, key events
4. `file 'Knowledge/stable/company/principles.md'` — Core principles and values
5. `file 'Knowledge/stable/careerspan-timeline.md'` — Historical timeline

**For terminology:**
- `file 'Knowledge/stable/glossary.md'` — Canonical definitions

---

### Personal (V / Vrijen Attawar)

**Always check first:**
1. `file 'Knowledge/stable/bio.md'` — Biographical info, background
2. `file 'Knowledge/stable/careerspan-timeline.md'` — Career milestones
3. `file 'Knowledge/context/howie_instructions/preferences.md'` — Scheduling, availability (reference only)

---

### System Operations (N5)

**Always check first:**
1. `file 'N5/prefs/prefs.md'` — Preference index
2. `file 'Knowledge/architectural/operational_principles.md'` — Core operational rules
3. `file 'Knowledge/architectural/ingestion_standards.md'` — What/how to ingest
4. `file 'N5/data/executables.db' (index only)` — Available commands (authoritative)

---

### Lists & Tracking

**Always check first:**
1. `file 'Lists/POLICY.md'` — How to interact with lists
2. `/home/workspace/Lists/` folder — Current list data
3. `file 'Lists/detection_rules.md'` — Email routing rules

**Available lists** (check folder for current):
- tasks
- ideas
- system-upgrades
- little-bird-functionality-updates
- social-media-ideas
- crm
- must-contact
- areas-for-exploration
- opportunity-calendar

---

## Lookup Workflow

### Step 1: Identify Topic Category

Categorize the query:
- **Company/product** → Careerspan knowledge
- **Personal** → Bio and preferences
- **System** → N5 operational docs
- **Lists** → Lists folder and policy
- **Communication** → Prefs communication modules

### Step 2: Check Canonical Sources

For each category, check the primary files listed above BEFORE answering.

### Step 3: Handle Gaps

If information is missing:

**Do NOT fabricate or assume.**

Instead:
1. **Flag the gap** — Note what's missing
2. **Search for sources** — Web search, user confirmation
3. **Update knowledge base** — Add verified information
4. **Document addition** — Log what was added and why

### Step 4: Cross-Reference

When answering, include references:
- Link to source files
- Cite specific sections
- Note confidence level (high/medium/low if uncertain)

---

## Knowledge Hierarchy

**Precedence for conflicting information:**

1. **User's direct statement** (in current conversation) — Highest authority
2. **Stable knowledge files** — Canonical, verified facts
3. **Evolving knowledge files** — Recently updated, may need verification
4. **Context files** — Reference material (e.g., Howie instructions)
5. **Training data** — Lowest authority, verify before using

---

## Update Protocol

When updating knowledge base:

### For Stable Knowledge
**Before editing:**
1. Check `file 'Knowledge/architectural/ingestion_standards.md'`
2. Verify information fits inclusion criteria
3. Confirm SSOT (Single Source of Truth) location
4. Check for duplicates across knowledge base

**When editing:**
1. Follow MECE principles (Mutually Exclusive, Collectively Exhaustive)
2. Add to existing file rather than create new
3. Update related cross-references
4. Add to glossary if new terminology

**After editing:**
1. Update `related_files` in frontmatter
2. Log change in file's change log section
3. Consider whether timeline entry needed

### For Evolving Knowledge
**More flexible:**
- Can create new files as needed
- Document source and confidence
- Move to stable/ when verified

---

## Schemas for Validation

When updating structured knowledge, validate against:

**Knowledge schemas:**
- `file 'Knowledge/schemas/knowledge.facts.schema.json'`

**List schemas:**
- `file 'Lists/schemas/lists.item.schema.json'`
- `file 'Lists/schemas/lists.registry.schema.json'`

**N5 schemas:**
- `file 'N5/schemas/index.schema.json'`
- `file 'N5/schemas/commands.schema.json'`

---

## Related Files

- **Ingestion Standards:** `file 'Knowledge/architectural/ingestion_standards.md'`
- **Operational Principles:** `file 'Knowledge/architectural/operational_principles.md'`
- **Glossary:** `file 'Knowledge/stable/glossary.md'`
- **Company Strategy:** `file 'Knowledge/stable/company/strategy.md'`
- **Lists Policy:** `file 'Lists/POLICY.md'`

---

## Change Log

### v2.0.0 — 2025-10-09
- Created from monolithic prefs.md knowledge lookup section
- Added topic-specific lookup tables
- Added lookup workflow steps
- Added knowledge hierarchy for conflicts
- Added update protocol aligned with ingestion standards
- Cross-referenced all stable knowledge files
