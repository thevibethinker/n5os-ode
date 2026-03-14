---
created: 2026-03-10
last_edited: 2026-03-10
version: 1.0
provenance: meeting-system-recovery-redesign/D2.2
drop_id: D2.2
build_slug: meeting-system-recovery-redesign
---

# Routing, Titling, and Move-Ready Rules

**Drop:** D2.2
**Scope:** Classification heuristics, title generation hierarchy, block-selection behavior redesign implications, and the post-processing move-ready state model.

---

## 1. Meeting vs. Reflection Routing

### 1.1 Problem Statement

The pipeline currently treats all incoming content as meetings. Pocket-sourced audio recordings — which V uses for personal voice notes and reflections — are forced through the full meeting pipeline (calendar match, CRM enrichment, multi-speaker identification). This wastes processing budget and generates irrelevant blocks. Additionally, ambiguous single-speaker content from any source has no escalation path.

### 1.2 Initial Classification Heuristic

Classification happens at the **ingest** stage, immediately after source format normalization. The heuristic uses a two-pass approach: fast deterministic checks first, then LLM fallback for ambiguous cases.

#### Pass 1: Deterministic Signals (Zone 3)

| Signal | Weight | Evaluation |
|--------|--------|------------|
| **Source identifier** | Primary | Pocket → default `reflection`. Fireflies/Fathom → default `meeting`. |
| **Speaker count** | Primary | 1 speaker detected → `reflection` unless overridden. ≥2 speakers → `meeting`. |
| **Calendar match** | Supporting | Calendar event found with ≥2 attendees → `meeting` regardless of other signals. |
| **Duration** | Supporting | <3 minutes → `reflection` bias. >45 minutes with 1 speaker → `reflection` bias. |
| **Filename/metadata cues** | Supporting | Contains "standup", "sync", "1:1", "intro", "call" → `meeting` bias. Contains "note", "memo", "thought", "idea" → `reflection` bias. |

#### Pass 2: LLM Evaluation (Zone 2 — only for ambiguous cases)

Triggered when Pass 1 produces a **split decision** (conflicting primary signals) or when confidence is below 0.7. The LLM reads the first 2000 characters and answers:

> Does this transcript represent a conversation between two or more people (meeting), or a single person recording their thoughts (reflection)? Consider: speaker turn patterns, conversational dynamics, references to "we discussed" vs. "I've been thinking".

Output: `{ "classification": "meeting" | "reflection", "confidence": 0.0-1.0, "reasoning": "..." }`

#### Decision Ladder

```
Source = Pocket AND speakers ≤ 1?
  YES → reflection (confidence: 0.9)
  NO  ↓

Source = Fireflies/Fathom?
  YES → meeting (confidence: 0.85)
  NO  ↓

Speakers ≥ 2?
  YES → meeting (confidence: 0.8)
  NO  ↓

Calendar match with ≥2 attendees?
  YES → meeting (confidence: 0.85)
  NO  ↓

Confidence < 0.7 from deterministic signals?
  YES → LLM evaluation (Pass 2)
  NO  → use highest-weight deterministic result

LLM confidence < 0.6?
  YES → HITL escalation with both signals attached
  NO  → use LLM result
```

### 1.3 Pocket Default Behavior

Per PLAN.md confirmed decision: **Pocket defaults to `reflection` unless initial evaluation detects meeting signal (multiple speakers).**

Specific Pocket rules:
- Source = Pocket + 1 speaker → `reflection` (no further evaluation needed)
- Source = Pocket + ≥2 speakers → reclassify as `meeting`, run full identification pipeline
- Source = Pocket + speaker count indeterminate → LLM evaluation on first 2000 chars

### 1.4 Classification Output

Classification writes to the manifest immediately after ingest:

```json
{
  "content_type": "meeting" | "reflection",
  "classification": {
    "method": "deterministic" | "llm" | "hitl_resolved",
    "confidence": 0.85,
    "signals": {
      "source": "pocket",
      "speakers_detected": 1,
      "calendar_match": false,
      "duration_minutes": 12,
      "filename_cues": ["note"]
    },
    "reasoning": "Single speaker Pocket recording with no calendar match"
  }
}
```

### 1.5 Downstream Pipeline Branching

| Content Type | Pipeline Path | Block Recipe |
|-------------|---------------|--------------|
| `meeting` (external) | identify → gate → process → archive | `external_standard`, `external_sales`, or `external_investor` |
| `meeting` (internal) | identify → gate → process → archive | `internal_standup`, `internal_strategy`, or `internal_retrospective` |
| `reflection` | identify(lite) → process → archive | `reflection` (new recipe, see §4) |

**Reflection "identify(lite)"** skips:
- Calendar triangulation (reflections don't have calendar events)
- CRM enrichment (no external participants)
- External participant verification

It does:
- Speaker verification (confirm single speaker is V)
- Date extraction from transcript metadata
- Topic classification for routing to correct R-block subset

### 1.6 Escalation Paths for Ambiguous Cases

| Scenario | Escalation |
|----------|------------|
| Pocket + 2 speakers but one seems to be playback/quotes | LLM evaluation, then HITL if confidence < 0.6 |
| Fireflies transcript with only V speaking (solo rehearsal, presentation recording) | LLM evaluation → likely reclassify as `reflection` |
| Very short transcript (< 300 chars) from any source | HITL escalation — too little evidence to classify reliably |
| LLM returns confidence < 0.6 | HITL with LLM reasoning attached for human triage |

---

## 2. Title Generation Rules

### 2.1 Problem Statement

Current titles are generated heuristically during ingest (from filename patterns and speaker names) then enriched by `title_normalizer.py` via LLM analysis. Evidence from the system audit shows titles are "improved but remain insufficient" — they become folder names and meeting IDs that propagate through brain.db edges, position extraction, CRM references, and all downstream knowledge systems.

Bad title patterns observed in the restore corpus:
- Generic: "Meeting with X" (no purpose)
- Date-only: "2025-09-04" (no participants or topic)
- Source artifacts: "Plaud Note_10-31" (device name leaking)
- Truncated: "Alex_x_Vrijen_Wisdom_Pa..." (cut off)
- Duplicate-pattern: Multiple folders with identical naming pattern

### 2.2 Title Hierarchy (DP-1 Resolution)

**Decision: Calendar/source metadata takes precedence for structural elements (date, participants). Transcript semantics take precedence for the descriptive element (purpose/topic).**

This resolves the DP-1 conflict: when calendar says "Sync with David" but the transcript reveals the meeting was actually about "Partnership pricing for Q2", the final title should use calendar-sourced participant names but transcript-derived purpose.

#### Title Template

```
YYYY-MM-DD_Participant-Names_Purpose-Slug
```

#### Field Hierarchy (each field has its own fallback chain)

**Date field:**
1. Calendar event date (highest trust)
2. Source system metadata date (Fireflies/Fathom API timestamp)
3. Transcript-extracted date
4. File creation date (lowest trust)

**Participant field:**
1. Calendar event attendees (canonical names from calendar)
2. CRM-resolved names (matched from transcript speakers)
3. Transcript-extracted speaker names (LLM-cleaned)
4. Source filename participant names (legacy fallback)

**Purpose field:**
1. Transcript semantic analysis — "What was this meeting actually about?" (LLM, Zone 2)
2. Calendar event title (often generic — "Sync", "Catch-up" — but sometimes specific)
3. Source filename topic hints
4. Meeting type + participant context as last resort ("External-Intro" / "Internal-Strategy")

#### Title Construction Rules

1. **Date** must be ISO 8601 format: `YYYY-MM-DD`
2. **Participants** use `FirstName-LastName` format, hyphenated, joined by `-x-` for multi-party: `Nick-Freund-x-Vrijen-Attawar`
3. **V is always included** in participant names (as `Vrijen-Attawar`) unless it's an internal team meeting where V's presence is implied
4. **Purpose slug** is 2-5 words, hyphenated, describing the actual topic: `Intro-Chat-via-Pams-Referral`, `Partnership-Pricing-Q2`, `Careerspan-Product-Review`
5. **Maximum total title length**: 120 characters. Truncate purpose slug first, then participant names (abbreviate to first names: `Nick-x-Vrijen`)
6. **Reflections** use: `YYYY-MM-DD_Reflection_Topic-Slug` (no participant names needed since it's always V)

### 2.3 Banned Title Patterns

The following patterns MUST be detected and corrected during title normalization:

| Anti-Pattern | Example | Why It's Bad |
|-------------|---------|--------------|
| Generic purpose | "Meeting with X", "Catch-up", "Sync" | No retrieval value — what was it actually about? |
| Device name leak | "Plaud Note_10-31", "Otter.ai Recording" | Source artifact, not content description |
| Date-only | "2025-09-04" | Missing participants and purpose entirely |
| Underscore-heavy legacy | "Alex_x_Vrijen_Wisdom_Partners_Coaching" | Should use hyphens per convention |
| Encoding artifacts | "%20", HTML entities, Unicode replacements | Source processing residue |
| Status suffixes | `_[P]`, `_[M]`, `_[C]` | Historical state machine artifacts — not part of meeting identity |
| Duplicate disambiguation only | "Meeting-v2", "Meeting-copy" | Indicates dedup failure, not real title |
| ALL CAPS | "STRATEGY SESSION" | Formatting noise |
| Source system IDs | "ff-abc123", "fathom-recording-456" | System identifiers, not human-readable titles |

### 2.4 Title Normalization Pipeline

Title generation runs in two phases:

**Phase 1 (during ingest):** Deterministic extraction
- Parse date from source metadata or filename
- Extract participant names from source metadata, filename, or transcript header
- Generate initial slug from filename or source title
- Result: working title sufficient for folder creation

**Phase 2 (during identify):** LLM enrichment
- Read first 3000 chars of transcript
- Generate purpose slug via LLM: "In 2-5 hyphenated words, what was this meeting actually about? Not the meeting type, but the specific topic or outcome."
- Cross-reference against calendar event title
- Apply banned-pattern detection and correction
- Result: final canonical title

**Phase 2 writes the final title to `manifest.title` and optionally renames the folder (with `--rename` flag).**

### 2.5 Reflection Titles

Reflections follow a simplified title pattern:

```
YYYY-MM-DD_Reflection_Topic-Slug
```

Topic slug is LLM-derived from transcript content: "In 2-5 hyphenated words, what is the primary subject of this reflection?"

Examples:
- `2026-03-10_Reflection_Hiring-Pipeline-Strategy`
- `2026-03-08_Reflection_Product-Positioning-Doubts`
- `2026-03-05_Reflection_Energy-Management-Lessons`

---

## 3. Block-Selection Redesign Implications

### 3.1 Current State

The block selector (`block_selector.py`) works well for meetings — it uses recipe-based selection with LLM-powered conditional evaluation. The system audit confirms it produces "thoughtful conditional reasoning" in manifests.

### 3.2 New: Reflection Block Recipe

The reflection prompt library (`Prompts/Blocks/Reflection/R00-R09`) exists but has no processing infrastructure. The routing rules above create the classification path; this section specifies the block recipe.

#### Reflection Recipe: `reflection_standard`

| Block | Name | When | Purpose |
|-------|------|------|---------|
| R00 | Emergent | always | Surface what's emerging from the reflection |
| R01 | Personal | conditional | Personal insights, feelings, self-awareness |
| R02 | Learning | conditional | Learning moments, skill development |
| R03 | Strategic | conditional | Strategic thinking, business direction |
| R06 | Synthesis | always | Integrated takeaway from the reflection |

**Conditional triggers:**
- R01 triggered when: emotional content, personal narrative, identity/values discussion
- R02 triggered when: skill development, mistake analysis, "I learned", "I realized"
- R03 triggered when: business strategy, market positioning, competitive thinking

**Not included by default** (available for manual override):
- R04 (Market) — only if market analysis is the primary topic
- R05 (Product) — only if product development is the primary topic
- R07 (Prediction) — only if future forecasting is the primary topic
- R08 (Venture) — only if investment/fundraising is the primary topic
- R09 (Content) — only if content strategy is the primary topic
- RIX (Integration) — cross-reflection synthesis, useful for batch processing

#### Recipe Configuration

```yaml
reflection_standard:
  description: "Default for Pocket reflections and single-speaker recordings"
  always: [R00, R06]
  conditional: [R01, R02, R03]
  manual_override: [R04, R05, R07, R08, R09, RIX]
  total_blocks: 5
  token_budget: "low-medium"
  notes: "Lightweight by design. Reflections are personal — over-processing destroys their value."
```

### 3.3 Recipe Selection Logic Update

The existing `get_recipe()` function in `block_selector.py` should be extended:

```
content_type == "reflection"?
  YES → return "reflection_standard"
  NO  ↓

content_type == "meeting"?
  meeting_type == "internal"?
    YES → existing internal recipe logic
    NO  → existing external recipe logic
```

This is a minimal change — one new branch before the existing meeting logic.

### 3.4 Gate Behavior for Reflections

Reflections should use a **simplified quality gate** since many meeting-oriented checks are irrelevant:

| Check | Applies to Reflections? | Why |
|-------|------------------------|-----|
| transcript_length | YES (≥100 chars for reflections, lower threshold than meetings) | Reflections can be shorter |
| transcript_format | YES | Basic quality |
| transcript_encoding | YES | Basic quality |
| meeting_duration_consistency | NO | No expected duration for reflections |
| participant_confidence | NO | Always V |
| host_identified | NO | Always V |
| external_participant_verification | NO | No external participants |
| calendar_match_score | NO | Reflections don't have calendar events |
| meeting_type_consistency | NO | N/A |
| block_count_reasonable | YES (adjusted range: 2-5 for reflections) | Prevent over-generation |
| block_quality_score | YES | Quality still matters |
| missing_critical_blocks | YES (R00 and R06 are critical for reflections) | Core blocks must succeed |
| block_file_integrity | YES | Basic quality |
| archive_readiness | YES | Metadata present |
| duplicate_detection | YES | Prevent duplicates |
| pipeline_completion | YES | All stages done |

---

## 4. Move-Ready State (DP-2 Resolution)

### 4.1 Problem Statement

Currently, processed meetings sit in Inbox indefinitely. The manifest shows `status: "complete"` but there is no explicit signal that the meeting is ready to be moved/archived. The archive step exists in code (`archive.py`) but the target directories don't exist and the step isn't wired into the automated pipeline.

The system audit confirms: "Completed meetings sit in Inbox indefinitely. There is no automated archive step running."

### 4.2 Decision: Move-Ready as Manifest Flag + Derived Verification (DP-2)

**Resolution: Both.** `move_ready` is a manifest flag that is SET based on derived state verification.

This avoids the two failure modes:
- Flag-only: flag could be set prematurely without verification → bad moves
- Derived-only: requires re-computing readiness every time → slow, fragile

The flag is the signal. The derivation is the guard that protects the flag.

### 4.3 Move-Ready Definition

A meeting/reflection is `move_ready: true` when ALL of the following are true:

#### For Meetings

| Check | Requirement | Evidence Source |
|-------|-------------|-----------------|
| **Status** | `status == "complete"` | `manifest.status` |
| **All critical blocks generated** | All `always` blocks from the active recipe exist as files | File existence check against `manifest.blocks.requested` |
| **Quality gate executed** | `quality_gate.executed_at` is not null | `manifest.quality_gate` |
| **No unresolved HITL** | No pending HITL items for this meeting | HITL queue cross-check |
| **Title normalized** | Title does not match any banned pattern (§2.3) | Pattern check on `manifest.title` or folder name |
| **Participants identified** | At least one participant has confidence ≥ 0.5 | `manifest.participants` |
| **Date determined** | `manifest.date` is a valid ISO 8601 date | `manifest.date` |

#### For Reflections

| Check | Requirement | Evidence Source |
|-------|-------------|-----------------|
| **Status** | `status == "complete"` | `manifest.status` |
| **Critical blocks generated** | R00 and R06 exist as files | File existence check |
| **Title normalized** | Matches reflection title pattern `YYYY-MM-DD_Reflection_*` | Pattern check |
| **Date determined** | `manifest.date` is a valid ISO 8601 date | `manifest.date` |

### 4.4 Move-Ready State Transition

```
status: "complete"
    ↓ (move-ready checks run)
move_ready: true | false
    ↓ (if true)
status: "move_ready"
    ↓ (archive/move executes)
status: "archived"
```

#### Manifest Update on Move-Ready

```json
{
  "status": "move_ready",
  "move_ready": {
    "passed": true,
    "checked_at": "2026-03-10T15:30:00Z",
    "checks": {
      "status_complete": true,
      "critical_blocks_present": true,
      "quality_gate_executed": true,
      "no_pending_hitl": true,
      "title_normalized": true,
      "participants_identified": true,
      "date_determined": true
    },
    "failed_checks": []
  }
}
```

#### Manifest Update on Move-Ready Failure

```json
{
  "status": "complete",
  "move_ready": {
    "passed": false,
    "checked_at": "2026-03-10T15:30:00Z",
    "checks": {
      "status_complete": true,
      "critical_blocks_present": true,
      "quality_gate_executed": true,
      "no_pending_hitl": false,
      "title_normalized": true,
      "participants_identified": true,
      "date_determined": true
    },
    "failed_checks": ["no_pending_hitl"]
  }
}
```

When `move_ready.passed == false`, status stays at `"complete"`. The `failed_checks` array identifies what needs resolution before the meeting can advance.

### 4.5 Move-Ready Evaluation Timing

Move-ready checks run:
1. **Automatically after `process` completes** — embedded in the pipeline tick
2. **On demand via CLI** — `meeting_cli.py check-move-ready <meeting-folder>`
3. **Batch evaluation** — `meeting_cli.py check-move-ready --all` scans all `complete` meetings in Inbox

### 4.6 Archive Target Structure

Once `move_ready: true`, the meeting is eligible for archival. The archive target depends on content type:

| Content Type | Archive Path |
|-------------|-------------|
| Meeting (external) | `Personal/Meetings/Week-of-YYYY-MM-DD/external/<meeting-folder>/` |
| Meeting (internal) | `Personal/Meetings/Week-of-YYYY-MM-DD/internal/<meeting-folder>/` |
| Reflection | `Personal/Meetings/Week-of-YYYY-MM-DD/reflections/<reflection-folder>/` |

Where `Week-of-YYYY-MM-DD` uses the Monday of the meeting/reflection date's week.

After move:
- Manifest is updated: `status: "archived"`, `archived_at` timestamp set
- Meeting folder is removed from Inbox
- Meeting registry DB is updated (if wired)

### 4.7 Gate Interlock Fix

The system audit identified that gate failures don't block processing (B1 breakpoint). The move-ready state provides a second safety net:

- Even if processing proceeds past a failed gate (current behavior), the move-ready check will catch `quality_gate_executed == null` or pending HITL items
- The move-ready check does NOT replace fixing the gate interlock — the gate should still be a hard checkpoint — but it provides defense in depth

**Recommendation for gate fix:** The `tick` command should NOT proceed to `process` if the quality gate failed AND the failure includes any critical check (participant_confidence < 0.5, encoding corruption). Non-critical gate failures (calendar mismatch with confidence 0.0) should proceed with a warning, since calendar match is currently broken system-wide (B2 breakpoint).

---

## 5. Decision Point Resolutions

### DP-1: Title Generation — Calendar vs. Transcript Semantics

**Resolution:** Split authority by field type.

- **Structural fields** (date, participant names): Calendar/source metadata takes precedence because these are facts that metadata systems capture more reliably than transcript parsing.
- **Descriptive fields** (purpose/topic): Transcript semantics take precedence because calendar event titles are often generic ("Sync", "Catch-up") while the actual conversation reveals the true topic.

**Conflict resolution:** When calendar and transcript disagree on a structural field (e.g., calendar says "Meeting with David Smith" but transcript shows "David Chen" speaking), flag for HITL with both signals attached. Don't silently prefer one over the other when they contradict on identity.

### DP-2: Move-Ready — Flag, Derived State, or Both

**Resolution:** Manifest flag SET by derived verification.

The `move_ready` field in the manifest is the authoritative signal that downstream automation reads. But the flag is never set manually — it is always the output of running the move-ready verification checks against the current manifest and filesystem state.

This gives us:
- **Speed:** Automation reads a single flag, not re-derives readiness each time
- **Safety:** Flag can only be set by passing all checks
- **Debuggability:** `move_ready.checks` shows exactly what was verified and when
- **Recoverability:** Re-running `check-move-ready` can update the flag if state changes (e.g., HITL item resolved)

---

## 6. Downstream Knowledge Quality Implications

These routing and titling rules directly improve downstream knowledge pipeline quality (per knowledge-audit.md RI-2):

| This Rule | Downstream Impact |
|-----------|-------------------|
| Meeting vs. reflection routing | Unlocks entire R-block prompt library; prevents reflection content from generating irrelevant meeting blocks |
| Better titles | Improves `meeting_edge` provenance in brain.db; improves semantic search via vectors_v2.db; improves archive browsability |
| Better classification (internal/external/reflection) | Enables smarter post-archive routing — external meetings → CRM feedback, internal → team dynamics, reflections → position system |
| Move-ready state | Creates explicit handoff point for post-archive elevation stage; prevents half-processed items from entering the knowledge pipeline |
| Banned title patterns | Eliminates noise in downstream retrieval; prevents device names and status suffixes from polluting knowledge graph edges |
| Purpose slug in titles | Enables topic-based clustering and retrieval across meetings without reading full transcripts |

---

## 7. Implementation Notes

### 7.1 Files That Need Modification (for execution phase)

| File | Change |
|------|--------|
| `Skills/meeting-ingestion/scripts/ingest.py` | Add classification heuristic (§1.2), write `content_type` and `classification` to manifest |
| `Skills/meeting-ingestion/scripts/block_selector.py` | Add `reflection_standard` recipe, add content_type branch in `get_recipe()` |
| `Skills/meeting-ingestion/scripts/title_normalizer.py` | Implement title hierarchy (§2.2), add banned pattern detection (§2.3) |
| `Skills/meeting-ingestion/scripts/meeting_cli.py` | Add `check-move-ready` command, wire move-ready into `tick`, fix gate interlock |
| `Skills/meeting-ingestion/scripts/quality_gate.py` | Add reflection-specific gate profile (§3.4) |
| `Skills/meeting-ingestion/scripts/process.py` | Wire reflection block generation |
| `Skills/meeting-ingestion/scripts/archive.py` | Add reflection archive path, create Week-of directories, update manifest with `archived` status |
| `Prompts/Blocks/BLOCK_INDEX.yaml` | Add `reflection_standard` recipe and R-block entries |
| `Skills/meeting-ingestion/SKILL.md` | Document reflection pipeline, move-ready state, updated title rules |

### 7.2 New Files (for execution phase)

| File | Purpose |
|------|---------|
| `Skills/meeting-ingestion/scripts/classifier.py` | Meeting vs. reflection classification module (§1.2) |
| `Skills/meeting-ingestion/scripts/move_ready.py` | Move-ready verification engine (§4.3-4.4) |

### 7.3 No Files Modified by This Drop

This drop is specification-only. All file modifications are deferred to the execution phase per PLAN.md ("prepare/inspect only — no live restore or code execution").
