# Prefs Optimization Summary

**Date:** 2025-10-10  
**Task:** Modularize prefs.md into a lightweight index with distributed content

---

## Results

### File Size Reduction
- **Old prefs.md:** 542 lines (monolithic)
- **New prefs.md:** 284 lines (47% reduction, now an index)
- **Backed up to:** `prefs.md.v2_monolithic_backup`

### Actions Taken

1. ✅ Backed up original `prefs.md` to `prefs.md.v2_monolithic_backup`
2. ✅ Archived old `index.md` to `index.md.deprecated`
3. ✅ Created new streamlined `prefs.md` as the main index
4. ✅ Created new focused modules:
   - `operations/careerspan.md` — Organization identity, aliases, email domains
   - `communication/executive-snapshot.md` — High-level style summary
   - `communication/nuances.md` — Fine-tuning and safeguards
   - `communication/general-preferences.md` — Operating rules and metrics
   - `communication/compatibility.md` — Cheat-sheet for other AIs
   - `system/commands.md` — Command index quick reference

---

## New Structure

```
N5/prefs/
├── prefs.md (NEW: lightweight index, 284 lines)
├── system/
│   ├── file-protection.md
│   ├── git-governance.md
│   ├── folder-policy.md
│   ├── safety.md
│   └── commands.md (NEW)
├── operations/
│   ├── scheduling.md
│   ├── resolution-order.md
│   ├── conversation-end.md
│   └── careerspan.md (NEW)
├── communication/
│   ├── executive-snapshot.md (NEW)
│   ├── voice.md
│   ├── templates.md
│   ├── meta-prompting.md
│   ├── nuances.md (NEW)
│   ├── general-preferences.md (NEW)
│   ├── compatibility.md (NEW)
│   └── email.md
├── integration/
│   ├── google-drive.md
│   └── coding-agent.md
├── knowledge/
│   └── lookup.md
├── naming-conventions.md
└── engagement_definitions.md
```

---

## Key Features

### Context-Aware Loading
The new `prefs.md` includes a **Context-Aware Loading Guide** that specifies which modules to load for different task types:

- **System operations** → Load system/file-protection, system/git-governance, system/safety
- **Knowledge ingestion** → Load knowledge ingestion standards, operational principles
- **Communication tasks** → Load communication modules (ONLY for distributed output/on-behalf-of writing)
- **Strategic work** → Load company strategy, glossary, timeline
- **List operations** → Load Lists/POLICY.md
- **Careerspan context** → Load operations/careerspan

### Critical Communication Rule
**⚠️ IMPORTANT:** Communication/voice modules should ONLY be loaded when generating **distributed output** or communicating **on V's behalf** (emails, documents, external communications). **NOT** for direct conversation with V.

This is clearly documented in:
- The main prefs.md index
- Each communication module header

---

## Module Summaries

### operations/careerspan.md
- Company name (Careerspan, legacy: Apply AI)
- Email domains (mycareerspan.com, theapply.ai — both internal)
- Employee canonicalization
- Downstream effects (scheduling, digests, CRM)

### communication/executive-snapshot.md
- Quick reference for tone weights (warmth: 0.80-0.85, confidence: 0.72-0.80, humility: 0.55-0.65)
- Anti-patterns (ambiguous timing, vague asks)
- Pointers to detailed modules

### communication/nuances.md
- Toggles (ClarityOverVerbosity, Reversible-First Decisions, Candidate-First)
- Adaptive interrogatory behaviors
- User-value features (web search + citations, output polish, diagrams)

### communication/general-preferences.md
- Operating rules (3 clarifiers, facilitation preference)
- Writing metrics (FK 10-12, sentence length 16-22 words)
- Micro-optimizations (headings, version tags, example-first)

### communication/compatibility.md
- Quick reference for other AI systems
- Do's and Don'ts
- Formatting and tone defaults

### system/commands.md
- Quick reference to most-used commands
- Points to authoritative source (commands.jsonl)
- Points to auto-generated docs

---

## Validation

All content from the original monolithic `prefs.md` has been:
- ✅ Preserved in focused modules
- ✅ Cross-referenced in the new index
- ✅ Categorized by context (system, operations, communication, integration, knowledge)
- ✅ Tagged with loading contexts (when to load each module)

**No functionality lost.** All rules, preferences, and guidance remain accessible through the modular structure.

---

## Benefits

1. **Faster loading:** Only relevant modules loaded per context
2. **Clearer organization:** Related preferences grouped together
3. **Easier maintenance:** Edit focused modules without navigating massive file
4. **Better discoverability:** Index provides clear pointers to each preference type
5. **Reduced token usage:** Load only what's needed for the task at hand

---

## Next Steps (Optional)

Consider future enhancements:
- Add schema validation for module structure
- Create automated index generator (like docgen for commands)
- Add inter-module dependency tracking
- Create module usage analytics (which modules loaded most often)
