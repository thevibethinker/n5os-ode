---
created: 2026-02-06
last_edited: 2026-02-06
version: 1
provenance: triage_learnings.py
category: system
---
# System Learning Promotion Review — 2026-02-06

## Instructions

Infrastructure, tooling, and API learnings → `SYSTEM_LEARNINGS.json`

Mark learnings to promote with `[x]`. Leave `[ ]` to skip.

When done, run:
```bash
python3 Skills/pulse/scripts/process_learning_review.py N5/review/learnings/2026-02-06_system-learnings-review.md
```

**Destination:** `N5/learnings/SYSTEM_LEARNINGS.json`

---

## Summary

- **Total unique learnings:** 34
- **Threshold:** 0.6
- **Generated:** 2026-02-06T20:20:23.553092

## High Confidence (0.8+) — 22 learnings

- [x] **memory-as-reasoning#0** (score: 0.90)
  > Batch API operations (migrations, bulk processing) run 3-4x slower than estimated due to API latency. Budget 3.5 items/sec for OpenAI calls, not theoretical throughput.
  - Sources: memory-as-reasoning
  - Tags: api, performance, estimation
  - Reasoning: Generalizable to any batch API work. Actionable planning guidance. Novel insight about real-world vs theoretical performance.

- [x] **consulting-zoffice-stack#7** (score: 0.90)
  > Temp directories get cleaned up before async operations complete. Use persistent storage paths (e.g., N5/data/) instead of temp directories for any data that must survive async processing.
  - Sources: consulting-zoffice-stack
  - Tags: async, filesystem, infrastructure
  - Reasoning: Generalizable infrastructure pattern. Highly actionable. Common pitfall with async workflows.

- [x] **memory-as-reasoning#2** (score: 0.90)
  > SQLite database initialization: Use Python's sqlite3 module directly (CREATE TABLE IF NOT EXISTS) rather than shell commands like 'sqlite3 < schema.sql'. Shell approach can leave empty DB files causing 'no such table' errors.
  - Sources: memory-as-reasoning
  - Tags: sqlite, database, initialization
  - Reasoning: Generalizable database pattern. Actionable fix for common failure mode. Clear do/don't guidance.

- [x] **meta-resume-v2#0** (score: 0.90)
  > Pipeline pre-flight validation: Validate data alignment BEFORE execution. Check that input data (e.g., decomposer output) matches target context (e.g., correct employer). Misalignment causes silent failures.
  - Sources: meta-resume-v2
  - Tags: pipeline, validation, data-integrity
  - Reasoning: Generalizable pipeline pattern. Actionable (add validation gate). Prevents costly rework from data misalignment.

- [x] **task-system-wiring#2** (score: 0.90)
  > gather_thread_context() is the single source of truth for context data. Wrapper scripts should only add presentation-layer flags for LLM consumption. Cleanly separates mechanics (data gathering) from semantics (interpretation).
  - Sources: task-system-wiring
  - Tags: architecture, context, separation-of-concerns
  - Reasoning: Strong architecture pattern. Generalizable to any context-gathering system. Clear separation of concerns guidance.

- [x] **b05-backfill-extended#1** (score: 0.85 ×8)
  > LLM responses via /zo/ask often include markdown code fences around JSON or truncate mid-object. Use robust regex extraction that handles triple-backtick wrappers, extra content after valid JSON, and attempts to close incomplete objects/arrays.
  - Sources: consulting-zoffice-stack, b05-backfill-extended
  - Tags: zo-api, json-parsing, error-handling
  - Reasoning: Highly generalizable to any /zo/ask usage, actionable with clear recovery patterns, strong API insight. Multiple drops encountered this independently.

- [x] **careerspan-pipeline-v2#0** (score: 0.85)
  > Airtable checkbox fields have parenthetical suffixes like 'Salary Range (Checkbox)' - use exact field names from schema documentation when building integrations.
  - Sources: careerspan-pipeline-v2
  - Tags: airtable, api, field-naming, integration
  - Reasoning: API-specific gotcha that will bite future integrations. Generalizable to all Airtable work. Clear actionable guidance.

- [x] **careerspan-pipeline-v2#1** (score: 0.85)
  > When integrating Zo app tools (Airtable, Google Drive, Gmail), scripts should output instructions/logs for the tools rather than directly calling them. The orchestrator executes tool calls. This decouples skills from app tool implementation details.
  - Sources: careerspan-pipeline-v2
  - Tags: zo-skills, architecture, decoupling, app-tools
  - Reasoning: Architecture pattern for Zo skill development. Generalizable to all app integrations. Clear separation of concerns principle.

- [x] **zo-task-system#3** (score: 0.85)
  > Cannot JOIN across SQLite databases. When working with multiple .db files, query each separately and merge results in Python.
  - Sources: zo-task-system
  - Tags: sqlite, database, architecture
  - Reasoning: Highly generalizable SQLite constraint, actionable workaround, applies to any multi-database architecture.

- [x] **zo-task-system#4** (score: 0.85)
  > Scheduled agents needing reply handling require dual trigger design: (1) scheduled run for initial action, (2) SMS/email reply trigger for follow-up processing. Same prompt handles both based on context detection (has reply content or not).
  - Sources: zo-task-system
  - Tags: scheduled-agents, sms, architecture
  - Reasoning: Generalizable agent architecture pattern, actionable design approach, novel insight about scheduled agent capabilities.

- [x] **store-v2#3** (score: 0.85)
  > Image generation alignment: Inspect tailwind.config/CSS variables for specific color names (e.g., 'zinc-900', 'sky-400') to align generated image aesthetics with UI theme.
  - Sources: store-v2
  - Tags: image-generation, design, tailwind
  - Reasoning: Generalizable media generation pattern. Actionable technique for visual consistency. Useful for any image generation + UI work.

- [x] **perf-dashboard-v2#0** (score: 0.85)
  > ZO_CLIENT_IDENTITY_TOKEN may not be available in all execution contexts (e.g., scheduled agents, certain API calls). Add fallback error handling for integrations requiring this token.
  - Sources: perf-dashboard-v2
  - Tags: zo-api, authentication, error-handling
  - Reasoning: Generalizable Zo API pattern. Actionable error handling guidance. Important for production reliability.

- [x] **vibeteacher-integration#2** (score: 0.80 ×2)
  > Pulse deposit learnings can have multiple formats - list of objects with 'text' field, list of strings, or single strings. Extraction code must handle all three formats and skip malformed JSON gracefully.
  - Sources: vibeteacher-integration
  - Tags: pulse, deposits, json-parsing, error-handling
  - Reasoning: Pulse-specific but critical for any code processing deposits. Defensive coding pattern. Prevents silent failures in build pipelines.

- [x] **careerspan-pipeline-v2#2** (score: 0.80)
  > Code output format and schema must be designed together - mismatches (e.g., flat array vs wrapped object) cause integration failures. Validate schema compatibility before implementation.
  - Sources: careerspan-pipeline-v2
  - Tags: schema, integration, validation, api-design
  - Reasoning: Generalizable integration principle. Actionable checkpoint for any multi-component build. Prevents late-stage debugging.

- [x] **careerspan-pipeline-v2#4** (score: 0.80)
  > Making schema fields nullable allows graceful migration of legacy data without breaking existing records.
  - Sources: careerspan-pipeline-v2
  - Tags: database, schema, migration, backwards-compatibility
  - Reasoning: Database migration pattern. Generalizable to any schema evolution. Actionable default for new field additions.

- [x] **b05-backfill-extended#6** (score: 0.80 ×2)
  > Zo API calls can timeout at 120s during long extractions. Use 180s timeout with retry mechanism for content-heavy requests.
  - Sources: b05-backfill-extended
  - Tags: zo-api, timeout, error-handling
  - Reasoning: Generalizable to any heavy /zo/ask usage, actionable timeout recommendation, clear infrastructure pattern.

- [x] **zo-task-system#5** (score: 0.80)
  > SMS interface cannot handle complex multi-option selection (domain/project pickers) due to character limits. Solution: mark items as 'pending_review' status and require browser-based completion for complex workflows.
  - Sources: zo-task-system
  - Tags: sms, channel-constraints, ux
  - Reasoning: Generalizable channel constraint, actionable fallback pattern, applies to any SMS-based interaction design.

- [x] **watts-principles#4** (score: 0.80)
  > Contradiction detector: single-sided negation detection (one text has 'never/not/no' while semantically similar text doesn't) catches contradictions that paired patterns miss. Use similarity threshold of 0.7+ to avoid false positives.
  - Sources: watts-principles
  - Tags: quality-gates, nlp, contradiction-detection
  - Reasoning: Generalizable NLP technique for quality gates, actionable threshold recommendation, novel detection approach.

- [x] **memory-as-reasoning#1** (score: 0.80)
  > SQLite embeddings stored as BLOB in vectors table (not separate embeddings table). Migration scripts must decode/encode float32 arrays, not just copy rows. Schema: block_id TEXT PRIMARY KEY, embedding BLOB NOT NULL.
  - Sources: memory-as-reasoning
  - Tags: sqlite, embeddings, schema
  - Reasoning: Useful database pattern for embedding storage. Actionable schema guidance. Prevents migration failures.

- [x] **store-v2#2** (score: 0.80)
  > Path sanitization patterns must account for: end of string ($), various separators (/\s), and quoted contexts ("'). Use character class like ([/\s"'\)]|$) to capture and preserve context.
  - Sources: store-v2
  - Tags: parsing, regex, paths
  - Reasoning: Generalizable parsing pattern. Actionable regex guidance. Prevents edge case failures in path handling.

- [x] **consulting-zoffice-stack#5** (score: 0.80)
  > When executing a Drop, extract build_slug and drop_id from drop brief frontmatter and pass to session_state_manager.py via --build and --worker-num flags. Without these, router misroutes to thread-close instead of drop-close.
  - Sources: consulting-zoffice-stack
  - Tags: pulse, drops, session-state
  - Reasoning: Critical Pulse system pattern. Actionable routing fix. Prevents misrouted closures.

- [x] **task-system-wiring#1** (score: 0.80)
  > Meeting folder state: [R] marker is NOT in folder names. State tracked in manifest.json (status field). Scripts should check manifest.json['status'] instead of folder name patterns.
  - Sources: task-system-wiring
  - Tags: n5, meetings, manifest
  - Reasoning: N5 system-specific but important pattern. Actionable correction to common assumption. Prevents broken meeting detection.

## Medium Confidence (0.6–0.8) — 12 learnings

- [x] **recall-calendar#3** (score: 0.75)
  > Verify existing implementations match architecture requirements before starting work - existing code may use different patterns (e.g., SQLite vs JSON state file) requiring overwrite rather than extension.
  - Sources: recall-calendar
  - Tags: pulse, verification, architecture, drops
  - Reasoning: Build process lesson. Generalizable to any multi-drop work. Prevents wasted effort on incompatible foundations.

- [x] **dynamic-survey-analyzer#0** (score: 0.75 ×3)
  > Fillout API stores emoji-labeled responses as full text strings (e.g., '5 = 🚀 Excited / All-in'). Parse with pattern 'N = emoji Text' to extract numeric scores. Also: screening questions may not filter API responses - filter ineligible responses manually.
  - Sources: dynamic-survey-analyzer
  - Tags: fillout, api, parsing
  - Reasoning: Generalizable for Fillout integration, actionable parsing pattern, API-specific quirk knowledge.

- [x] **watts-principles#8** (score: 0.75)
  > Pulse safety checks (impossibility audit, prompt lint, contradiction detection, plateau detection) must use try/except for graceful fallback - detectors may not be available in all environments.
  - Sources: watts-principles
  - Tags: pulse, error-handling, safety-checks
  - Reasoning: Generalizable defensive coding pattern for Pulse, actionable error handling approach, process pattern for build safety.

- [x] **careerspan-profile-output-v1#5** (score: 0.75 ×3)
  > Build deposits must verify ALL artifacts listed in drop spec exist before marking complete. Missing artifacts discovered later require rework. Quality gate should check content existence, not just brief presence.
  - Sources: careerspan-profile-output-v1, consulting-zoffice-stack
  - Tags: pulse, deposits, verification
  - Reasoning: Generalizable build verification pattern. Actionable quality gate. Prevents incomplete deposits.

- [x] **careerspan-pipeline-v2#3** (score: 0.70)
  > Field naming inconsistencies (name vs skill_name, level_required vs required_level) should be caught by validation tests early in the pipeline, not at integration time.
  - Sources: careerspan-pipeline-v2
  - Tags: testing, validation, schema, naming-conventions
  - Reasoning: Testing pattern for schema work. Generalizable. Actionable: add field name validation to test suites.

- [x] **zo-task-system#0** (score: 0.70)
  > task_registry.py is the canonical interface for N5/task-system - all code should import from it rather than direct SQL access. Domain and project auto-creation happens automatically when creating tasks.
  - Sources: zo-task-system
  - Tags: task-system, architecture, canonical-interface, n5
  - Reasoning: Architecture documentation for task system. Specific but important for future task system work. Clear directive.

- [x] **zo-task-system#1** (score: 0.70 ×2)
  > Pattern matching for work completion detection works better with standalone word patterns ('drafted', 'saved', 'created', 'built') than complex noun-dependent patterns. Use flexible word boundary detection.
  - Sources: zo-task-system
  - Tags: pattern-matching, close-hooks, nlp
  - Reasoning: Generalizable to close hooks and completion detection, actionable pattern design guidance.

- [x] **consulting-zoffice-stack#4** (score: 0.70)
  > Pulse learnings CLI: use 'list <build_slug>' to read build learnings. There is no 'read' subcommand despite documentation references.
  - Sources: consulting-zoffice-stack
  - Tags: pulse, cli, commands
  - Reasoning: Pulse CLI quirk. Actionable command correction. Related to existing CLI syntax learning but different command.

- [x] **zo-task-system#2** (score: 0.65)
  > SQLite column types matter for cross-table operations. INTEGER IDs must be converted to TEXT strings when storing in tables with TEXT ID columns, and vice versa when querying.
  - Sources: zo-task-system
  - Tags: sqlite, database, type-conversion
  - Reasoning: Generalizable SQLite gotcha, actionable type handling guidance, moderate scope.

- [x] **vibe-teacher#1** (score: 0.65)
  > Word overlap matching for imprecision detection: 40% threshold on expanded word sets works better than direct substring matching which is too rigid.
  - Sources: vibe-teacher
  - Tags: parsing, matching, thresholds
  - Reasoning: Extends existing VibeTeacher pattern matching learning with specific threshold. Actionable tuning guidance.

- [x] **ode-cleanup#0** (score: 0.60 ×2)
  > GitHub force-push preserves content but destroys history. Always verify existing directory structure before copying. Consider workflow warnings on low commit count detection.
  - Sources: ode-cleanup
  - Tags: git, version-control, history
  - Reasoning: Generalizable version control pattern. Actionable verification step. Prevents history loss issues.

- [x] **consulting-zoffice-stack#8** (score: 0.60)
  > Git-based change detection works well for incremental exports but requires tracking state (last_export.json) to identify what changed since last run.
  - Sources: consulting-zoffice-stack
  - Tags: git, incremental, state-tracking
  - Reasoning: Useful pattern for incremental processing. Actionable state tracking approach.

---

**Processed:** 2026-02-07T11:24:52.469310
**Promoted:** 34
**Skipped:** 0
