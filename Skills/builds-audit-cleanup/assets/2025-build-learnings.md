# 2025 Stale Builds - Consolidated Learnings

**Extracted from:** 30 builds with no git activity since 2025
**Extraction Date:** 2026-02-01
**Purpose:** Preserve valuable patterns and architectural learnings before archival

---

## Architecture & Principles

### Three-Layer Persona Architecture (architectural-redesign-v1/v2)

**Pattern:** Personas → Pre-Flight → Prompts/Principles

**Key Insight:** Self-reinforcing cognitive bootstrap architecture where:
- Personas define domain and scope
- Pre-flight protocol loads relevant context
- Embedded principles guide execution decisions
- All layers cross-reference each other

**Implementation:**
```yaml
persona:
  name: Vibe Builder
  domain: Implementation
  pre_flight_protocol: |
    1. Load principles from N5/prefs/principles/
    2. Load context via n5_load_context.py
    3. Check BUILD_LESSONS.json
  relevant_principles:
    - P25 (Tool-First)
    - P35 (Version, Don't Overwrite)
```

**Success Metrics:** 37 principles codified, 8 personas enhanced, 100% cross-reference validation

---

### Principle Migration to YAML (architectural-redesign-v1)

**Pattern:** Convert markdown principles to structured YAML with schema

**Why:** Machine-readable principles enable:
- Automated validation
- Programmatic loading (n5_load_context.py)
- Versioning and provenance tracking
- Cross-reference checking

**Schema:**
```yaml
---
principle_id: P25
name: Tool-First
category: architectural
version: 1.0
created: 2025-11-01
description: |
  Prefer existing tools/integrations over building new ones.
  Scripts = mechanics, LLM = semantics.
anti_patterns:
  - Building scrapers when API exists
  - Regex when semantic parsing needed
examples:
  - Use use_app_gmail instead of parsing raw email
  - Use use_app_notion instead of scraping
---
```

**Learning:** Structured principles enable automation and prevent drift

---

### Terminology Cleanup: Persona vs Mode (mode-system-cleanup)

**Anti-Pattern:** "Activate Builder mode" or "Switch to Debugger mode"

**Correct Pattern:** "Switch to Vibe Builder persona" or "Route to Vibe Debugger"

**Why:** "Mode" implies temporary state changes; "persona" implies domain expertise and responsibility

**Resolution:** Updated 6 protocol files, replaced 17 instances of "mode" terminology

**Learning:** Consistent terminology prevents confusion about system architecture

---

## Orchestration & State Management

### Worker Orchestrator Pattern (orchestrator-enhancements-v1)

**Pattern:** Coordinator spawns specialist workers, tracks via SESSION_STATE

**Architecture:**
```
Orchestrator (con_ORCH)
├── SESSION_STATE.md (parent: none)
└── Spawns Workers (con_W1, con_W2, ...)
    ├── SESSION_STATE.md (parent: con_ORCH)
    └── Worker rubrics (con_W1_RUBRIC.md)
```

**Components:**
1. `session_state_manager.py` - State tracking
2. `cross_workspace_validator.py` - Safe artifact transfer
3. `orchestrator_title_generator.py` - Contextual naming
4. `orchestrator_rubric_generator.py` - Worker evaluation

**Learning:** Parent-child relationships in SESSION_STATE enable orchestrator visibility

---

### Cross-Workspace Safety (orchestrator-enhancements-v1)

**Pattern:** Validate before moving artifacts between workspaces

**Risk:** Conversation workspaces ephemeral; N5 persistent

**Solution:**
```python
from cross_workspace_validator import validate

if validate(source=worker_file, target=n5_scripts):
    # Safe to move
    cp worker_file /home/workspace/N5/scripts/
else:
    # Rollback or fix
    log_validation_error()
```

**Learning:** Always validate cross-boundary operations; don't trust relative paths

---

### Session State as SSOT (orchestrator-enhancements-v1)

**Pattern:** SESSION_STATE.md is single source of truth for conversation state

**Fields:**
- `conversation_id` - Unique identifier
- `type` - build/research/discussion/planning
- `parent_conversation_id` - For worker orchestrator tracking
- `focus` - Current objective
- `objective` - Overall goal
- `artifacts_created` - Files to manage at close

**Learning:** Centralized state prevents orphaned conversations and loose threads

---

### Arrest Mechanism for Runaway Costs (cost-guard)

**Pattern:** System-wide brake for misconfigured scheduled agents

**Components:**
1. `N5/flags/ARREST_SYSTEM.json` - Arrest flag
2. `cost_sentinel.py` - Velocity monitoring
3. `n5_schedule_wrapper.py` - Arrest check on execution

**Thresholds:**
- Global velocity: >60 executions/hour
- Task velocity: >12 executions/hour
- Failure storm: >80% failure rate

**Learning:** Always include safety brakes in automation systems

---

## Data Architecture & Storage

### Hybrid JSONL + Markdown Pattern (lists-storage-standards)

**Problem:** JSONL for structured data, but complex content needs rich markdown

**Solution:**
```jsonl
{
  "id": "c58cc6dd",
  "title": "Spaghetti Carbonara",
  "tags": ["dinner", "italian"],
  "links": [
    {"type": "file", "value": "Lists/content/recipes/c58cc6dd-spaghetti-carbonara.md"}
  ]
}
```

**Markdown file:** `Lists/content/recipes/c58cc6dd-spaghetti-carbonara.md`
```yaml
---
created: 2025-12-24
difficulty: medium
---
# Spaghetti Carbonara
## Ingredients
- Pasta
- Eggs
- Pecorino Romano
## Instructions
...
```

**Content Classification:**
- **Atomic:** Simple entries, JSONL-only (title, tags, notes)
- **Reference:** Structured data + linked markdown (recipes, procedures)
- **External:** URLs to external resources (articles, videos)

**Learning:** Hybrid pattern balances structured query with rich content

---

### Lists Validation with Orphan Detection (lists-storage-standards)

**Pattern:** Validate JSONL → Markdown links, detect broken references

**Script:** `n5_lists_validate.py`

**Checks:**
1. Schema validation (required fields)
2. Link path resolution (file exists?)
3. Orphan detection (linked file has no JSONL entry)
4. Duplicate detection (same title in same list)

**Learning:** Validation prevents data rot in hybrid systems

---

### Personal/Knowledge vs Knowledge/ Distinction (knowledge-realignment-v1)

**Problem:** Two `Knowledge/` directories with unclear responsibilities

**Resolution:**
- `Personal/Knowledge/` - SSOT for human-facing knowledge
- `Knowledge/` - Compatibility shell (deprecated), points to Personal

**Subtrees in Personal/Knowledge:**
- `Canon/` - Stable, timeless insights
- `Frameworks/` - Conceptual models and patterns
- `ContentLibrary/` - Curated articles and media
- `CRM/` - Stakeholder intelligence
- `MarketIntelligence/` - GTM and competitive intel
- `Architecture/` - System design and principles
- `Wisdom/` - Meta-learnings and AARs
- `Logs/` - Operational history
- `Archive/` - Deprecated but worth keeping

**Learning:** Single source of truth prevents duplication and confusion

---

### Knowledge → N5 Flow (knowledge-realignment-v1)

**Pattern:** N5 as system lens, not primary storage

```
Personal/Knowledge/ (Human-facing)
    ↓ Read by
N5/ (System lens)
    ↓ Writes digests to
Personal/Knowledge/Canon/ (Promoted insights)
```

**Roles:**
- N5 reads from Personal/Knowledge/ for context
- N5 writes digests, logs, DBs to system areas
- Only curated insights promoted back to Personal/Knowledge/

**Learning:** System processes don't pollute human-facing knowledge

---

## Tool Integration & Architecture

### Tool-First Enrichment (crm-v3-enrichment)

**Principle:** Use existing tools before building new integrations

**Pattern:**
```
Profile → Queue → Enrichment Worker
                          ↓
                    [Aviato API]  ← Existing SDK
                    [Gmail Tool]   ← use_app_gmail
                    [LinkedIn]       ← Via Aviato
                          ↓
                  Append to YAML (append-only)
                          ↓
                    Update Database
```

**Division of Labor:**
- Scripts: API calls, file operations, queue processing
- LLM: Gmail thread analysis, intelligence formatting
- Semantic validation: Profile quality (not automated tests)

**Learning:** Tools = mechanics, LLM = semantics (don't mix concerns)

---

### CRM Unification with Multiple Data Sources (crm-v3-unified)

**Pattern:** Merge 3 legacy CRM systems into unified database

**Legacy Sources:**
1. `N5/stakeholders/*.yaml` - Flat YAML files
2. `Personal/Knowledge/CRM/` - Enriched profiles
3. `N5/data/crm_legacy.db` - Old SQLite

**Unified Schema:**
- `profiles` table with deduplication
- `interactions` table for communications
- `enrichment_queue` for pending jobs
- Foreign keys with CASCADE deletes

**Migration Approach:**
1. `--dry-run` mode to preview changes
2. Idempotent scripts (re-runnable)
3. Git snapshots before execution
4. Validation after each phase

**Learning:** Phased migration with rollback capability prevents data loss

---

### LLM-Over-Regex Principle (llm-extraction-integration)

**Anti-Pattern:** Hardcoded regex patterns for semantic tasks

**Example (Bad):**
```python
tool_patterns = [
    (r'\b(YC|Y\s*Combinator)\b.*\b(founder|match)', "YC Founder Match"),
    (r'\b(calendly|schedule|book)\b', "calendly"),
]
```

**Pattern (Good):**
```python
from llm_extractor import LLMExtractor

result = extractor.extract_resources(
    transcript=transcript_text,
    library_items=library_items
)

resources = [
    ResourceReference(
        title=r.get("title"),
        url=r.get("url"),
        confidence=r.get("confidence")
    )
    for r in result["resources"]
]
```

**When to Use Regex:**
- Structured data (JSON, CSV)
- Pattern matching on STRUCTURED content
- File paths, URLs, IDs

**When to Use LLM:**
- Extract meaning from text
- Classify content
- Parse unstructured data
- Natural language pattern matching

**Learning:** LLMs > Regex for semantic tasks; Regex for structured data

---

### Script-as-Zo-Agent Pattern (meeting-pipeline-v2-BUILD)

**Pattern:** Python script orchestrates Zo agent for complex workflows

**Architecture:**
```
transcript_processor.py (Python)
    ↓ Phase 1
Detects new transcripts
    ↓ Phase 2
Calls Zo agent to analyze + select blocks
    ↓ Phase 3
Python queues blocks to DB
    ↓ Phase 4
Calls Zo agent to generate blocks one-by-one
    ↓ Phase 5
Python finalizes + notifies
```

**Two Databases:**
- `meeting_pipeline.db` - Meeting lifecycle tracking
- `block_registry.db` - Block queue + completed blocks

**Learning:** Hybrid Python+Zo agent pattern leverages both strengths

---

## Event Discovery & Processing

### Tiered Event Discovery (smart-event-detector + email-allowlist)

**Pattern:** High-precision allowlist + high-recall smart detector

**Architecture:**
```
Tier 1: Allowlist (High Precision)
┌─────────────────────────────────┐
│ Gmail: from:(allowlist)       │
│ newer_than:2d                │
│ → Extract URLs → Score         │
│ → Recommend                   │
└─────────────────────────────────┘
            ↓
Tier 2: Smart Detector (High Recall)
┌─────────────────────────────────┐
│ Gmail: ("lu.ma" OR "partiful")│
│ newer_than:2d                │
│ -from:(allowlist)             │
│ → Flag for Review             │
│ → Auto-add to allowlist*      │
└─────────────────────────────────┘
```

**URL Patterns (5 Platforms):**
- Luma: `lu.ma/[a-zA-Z0-9_-]+`, `luma.com/join/[id]`
- Partiful: `partiful.com/e/[a-zA-Z0-9]+`
- Supermomos: `supermomos.com/events/[slug]`
- Eventbrite: `eventbrite.com/e/[name]-[id]`
- Meetup: `meetup.com/[group]/events/[id]`

**Auto-Allowlist Logic:** Same sender 2+ times → auto-add

**Learning:** Tiered pattern balances precision and recall

---

### Email Allowlist Management (email-allowlist)

**Pattern:** Forward-based allowlist management

**User Action:** Forward invite to `va@zo.computer` with subject `n5:allowlist`

**System Action (Hourly Agent):**
1. Scan Gmail for `subject:"n5:allowlist" newer_than:2h`
2. Extract original sender from forwarded body
3. Update `N5/config/event_sources.json`
4. Archive email

**Discovery Workflow:**
1. Agent reads `event_sources.json`
2. Constructs query: `from:(sender1 OR sender2...) newer_than:2d`
3. Fetches emails via `use_app_gmail`
4. Parses via `luma_orchestrator.py`

**Learning:** Manual curation + automated discovery reduces noise

---

## Semantic Indexing & Cleanup

### Semantic Duplicate Detection (semantic-cleanup-v1)

**Pattern:** Use embedding similarity to identify near-duplicate content

**Approach:**
```python
for resource in all_resources:
    similar = client.search(
        query=resource.content,
        limit=5,
        min_similarity=0.85  # High threshold
    )

    if len(similar) > 1:
        cluster = create_cluster(resource, similar)
        rank_by_date(cluster)
        mark_canonical(cluster[0])  # Newest
        mark_stale(cluster[1:])
```

**Output:** `DUPLICATE_CLUSTERS.md` with canonical/stale designations

**Learning:** Semantic similarity finds duplicates keyword search misses

---

### Staleness Signals (semantic-cleanup-v1)

**Pattern:** Multi-factor staleness detection

| Signal | Weight | Example |
|--------|--------|---------|
| Newer doc with same topic | High | v2 exists, v1 is stale |
| References removed system | High | Mentions "mode system" (deprecated) |
| No modifications 60+ days | Medium | Last edit Oct 2025 |
| Low semantic uniqueness | Medium | Content exists elsewhere |

**Output:** `STALE_DOCS_REPORT.md` with confidence levels

**Learning:** Staleness requires multiple signals, not just timestamps

---

### Consolidation Opportunities (semantic-cleanup-v1)

**Pattern:** Find semantically related but fragmented content

**Example:**
```
Topic: "CRM System"
Currently spread across 6 files:
- N5/docs/crm_interface_guide.md (800 words)
- N5/prefs/communication/crm_protocols.md (400 words)
- Documents/CRM_Consolidation_Final.md (1200 words)
- ...

Recommendation: Merge into single N5/docs/crm_system_guide.md
Estimated reduction: 6 files → 1 file
```

**Learning:** Semantic clustering reveals consolidation opportunities

---

## Media & Document Management

### Unified Media/Document Tracking (media-documents-system)

**Pattern:** Single system for external media + internal documents

**Architecture:**
```
N5/data/media_documents.db
├── media (videos, images, audio)
├── documents (PDFs, DOCX, slides)
└── integrations (YouTube, Google Drive, etc.)

Workflows:
├── ingest/     - Add new items to system
├── organize/    - Tag, classify, deduplicate
├── search/      - Find by content/metadata
└── export/      - Generate views/reports
```

**Taxonomy:**
- Type: video, image, audio, document, presentation
- Source: local, YouTube, Drive, Slack, email
- Status: unprocessed, tagged, archived

**Learning:** Unified tracking prevents media fragmentation across systems

---

## Anti-Patterns

### Regex for Semantic Tasks (llm-extraction-integration)

**Anti-Pattern:**
```python
# Trying to detect YC founder matches with regex
(r'\b(YC|Y\s*Combinator)\b.*\b(founder|match)', "YC Founder Match")
```

**Problems:**
- Fails on variations ("YC Combinator", "Y Combinator")
- Can't handle context ("not YC related")
- Misses semantic matches ("W23 batch")

**Pattern:** Use LLM with semantic extraction prompt

---

### Mode vs Persona Confusion (mode-system-cleanup)

**Anti-Pattern:** "Activate Builder mode", "Switch to Debugger mode"

**Problems:**
- Implies temporary state change
- Unclear who's responsible
- Inconsistent with system architecture

**Pattern:** "Switch to Vibe Builder persona", "Route to Vibe Debugger"

---

### Knowledge/ Pollution (knowledge-realignment-v1)

**Anti-Pattern:** N5 writes operational files to Knowledge/

**Problems:**
- Human-facing knowledge polluted with system artifacts
- Hard to distinguish curated content vs. system output
- Breaks SSOT principle

**Pattern:** N5 reads from Personal/Knowledge, writes to N5, promotes curated insights back

---

## Implementation Patterns

### Phased Migration with Rollback (crm-v3-unified, knowledge-realignment-v1)

**Pattern:**
1. `--dry-run` mode to preview
2. Idempotent scripts (re-runnable)
3. Git snapshots before changes
4. Validate after each phase
5. Rollback capability via `.n5protected` + git

**Example:**
```bash
# Preview
python3 migrate_crm.py --dry-run

# If OK, snapshot
git add . && git commit -m "Pre-migration snapshot"

# Execute
python3 migrate_crm.py --execute

# Validate
python3 validate_crm.py

# If issues, rollback
git reset --hard HEAD
```

**Learning:** Never execute without preview and rollback path

---

### Safety Guardrails for Bulk Operations (lists-storage-standards)

**Pattern:**
1. `.n5protected` on critical directories
2. `--dry-run` flag for all scripts
3. Confirmation prompts for >5 files
4. Validation scripts before/after
5. Manifest of all changes

**Example:**
```python
def move_files(files, target):
    if len(files) > 5:
        print(f"Moving {len(files)} files:")
        for f in files:
            print(f"  - {f}")
        if not confirm("Proceed?"):
            return

    for f in files:
        validate_safe_to_move(f, target)
        shutil.move(f, target)

    log_manifest(files, target)
```

**Learning:** Always validate, dry-run, and log destructive operations

---

## Testing & Validation

### Orphan Detection in Hybrid Systems (lists-storage-standards)

**Pattern:** Validate JSONL → Markdown links in both directions

**Checks:**
1. JSONL `links[*].value` → File exists?
2. Markdown file → Referenced by JSONL entry?
3. Circular references → Infinite loop prevention

**Script:** `n5_lists_validate.py`

**Learning:** Hybrid systems require bidirectional validation

---

### Semantic Validation for Architectural Principles (crm-v3-unified)

**Pattern:** Use LLM to verify principles, not unit tests

**Why:** Principles are semantic judgments, not boolean assertions

**Example:**
```python
# Semantic validation (correct)
validate_principles = """
Review this CRM system and verify:
1. Tool-First: Are we using existing tools?
2. SSOT: Is there one source of truth?
3. Append-only: Are we mutating records?
"""

# Unit test (incorrect for this)
def test_tool_first():
    assert len(integrations) > 0  # Too shallow
```

**Learning:** Semantic validation requires LLM judgment, not code tests

---

## Summary

**Key Patterns to Preserve:**
1. Three-layer persona architecture (Personas → Pre-Flight → Principles)
2. Hybrid JSONL + markdown storage for complex data
3. Tool-first enrichment (use existing tools, don't build scrapers)
4. LLM-over-regex for semantic tasks
5. Tiered discovery (high-precision + high-recall)
6. Script-as-Zo-agent for complex workflows
7. Phased migration with rollback capability
8. Session state as SSOT for orchestration
9. Personal/Knowledge vs Knowledge/ distinction
10. Arrest mechanisms for runaway automation

**Anti-Patterns:**
1. Regex for semantic parsing
2. "Mode" vs "persona" terminology confusion
3. Knowledge/ pollution by system artifacts
4. Destructive operations without dry-run

**Success Factors:**
- Clear SSOT (Personal/Knowledge for humans, N5 for system)
- Principle-driven decisions
- Safety guardrails for all automation
- Semantic validation over unit tests for principles

---

**Generated:** 2026-02-01 by Drop D1.2 (builds-audit-cleanup)
