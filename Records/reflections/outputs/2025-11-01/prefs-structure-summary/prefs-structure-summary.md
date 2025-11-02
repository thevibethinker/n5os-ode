# Executive Memo — Reflection Synthesis
**Date:** 2025-11-01

## Context
N5 PREFERENCES SYSTEM v2.0 - Structure Overview
================================================

OLD STRUCTURE (v1):
------------------
N5/prefs/prefs.md (monolithic, ~650 lines, ~5-6K tokens)
├── System Governance
├── Operational Framework  
├── Personal Communication
├── Prompt Engineering
└── Compatibility Notes

NEW STRUCTURE (v2):
------------------
N5/prefs/index.md (lightweight, ~1-2K tokens)
├── Critical always-load rules
├── Module directory
└── Context-aware loading guide

MODULES:
--------

📁 system/
   ├── file-protection.md       [File classification, overwrite protection, recovery]
   ├── git-governance.md         [Tracked paths, ignore patterns, commit guidelines]
   ├── folder-policy.md          [POLICY.md precedence, creation protocol]
   └── safety.md                 [Consent requirements, dry-run, protocol search]

📁 operations/
   ├── scheduling.md             [Config, retry policy, timezone handling]
   └── resolution-order.md       [Precedence hierarchy, conflict resolution]

📁 communication/
   ├── voice.md                  [Tone, formality, lexicon, relationship depth]
   ├── templates.md              [Micro-templates, CTAs, file naming, safeguards]
   ├── meta-prompting.md         [Outcome-first, enhancement passes, nuances]
   └── email.md                  [Processing, detection rules, Howie status]

📁 integration/
   ├── google-drive.md           [Access workflow, MIME types, fallback]
   └── coding-agent.md           [When to use, decision tree, rationale]

📁 knowledge/
   └── lookup.md                 [Where to search first, topic guide, update protocol]

STABLE FILES (unchanged):
-------------------------
├── naming-conventions.md        [File/folder naming rules]
└── engagement_definitions.md    [Load up / prime protocols]

SYNCHRONIZED WITH KNOWLEDGE BASE:
---------------------------------

📚 Knowledge/stable/
   ├── bio.md                    [V & Logan biographical info]
   ├── glossary.md               [Careerspan terminology]
   ├── careerspan-timeline.md    [Company history]
   └── company/
       ├── overview.md           [Mission, product, philosophy]
       ├── strategy.md           [GTM, positioning, wedge]
       ├── history.md            [Founding story]
       └── principles.md         [Core values]

📚 Knowledge/architectural/
   ├── operational_principles.md [Rule-of-Two, SSOT, voice policy]
   └── ingestion_standards.md    [What to ingest, MECE principles]

📚 Knowledge/context/
   └── howie_instructions/
       └── preferences.md        [Howie scheduling reference]

📋 Lists/
   ├── POLICY.md                 [List interaction rules]
   └── detection_rules.md        [Email routing patterns]

🗂️  Schemas/
   ├── N5/schemas/*.json         [System schemas]
   ├── Knowledge/schemas/*.json  [Knowledge schemas]
   └── Lists/schemas/*.json      [List schemas]

LOADING STRATEGY:
----------------
Context                  → Load These Modules
-------                    -----------------
System operations        → system/*, safety
Knowledge ingestion      → architectural/*, knowledge/lookup
Communication tasks      → communication/*, bio
Strategic work           → company/*, glossary, timeline
List operations          → Lists/POLICY.md

BENEFITS:
---------
✓ 60-70% reduction in token overhead
✓ Context-aware loading (only what's needed)
✓ Easier maintenance (edit specific modules)
✓ No duplication (references stable knowledge)
✓ Better discoverability (clear module names)
✓ Single source of truth (SSOT enforced)

TOKEN COMPARISON:
----------------
Old: Load entire prefs.md every time = ~5-6K tokens
New: Load index + selective modules = ~1-2K base + ~1K per module as needed

Example conversations:
- Simple file operation: ~1.5K tokens (index only)
- Email writing: ~3K tokens (index + voice + templates)
- Knowledge ingestion: ~4K tokens (index + architectural + lookup)
- Full context: ~8K tokens (all modules) — still less than old + better organized

## Initial Classification
- product_strategy, ops_process

## Next
- Draft decisions/options
- Risks + counterfactuals
- Actions and owners
