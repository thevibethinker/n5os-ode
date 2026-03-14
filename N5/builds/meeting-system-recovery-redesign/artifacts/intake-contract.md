---
created: 2026-03-10
last_edited: 2026-03-10
version: 1.0
provenance: meeting-system-recovery-redesign/D2.1
---

# Unified Intake Contract

**Purpose:** Define the canonical landing shape that normalizes all meeting and reflection sources into one ready-to-process format in `Personal/Meetings/Inbox/`.

**Scope:** Fireflies, Fathom, Pocket, and recovered historical content. Future sources must conform to this contract or provide an adapter.

---

## 1. Core Principle

Every item that lands in `Personal/Meetings/Inbox/` MUST arrive as a **normalized folder** with a manifest and transcript. Raw files (loose `.md`, `.jsonl`, `.json`) are staging artifacts, not ready-to-process state. The pipeline does not process raw files — it processes folders that satisfy this contract.

**Landing invariant:** If it's in `Personal/Meetings/Inbox/<folder>/` and has a `manifest.json` with `status: ingested`, it is ready-to-process. Everything else is pre-intake noise.

---

## 2. Content Types

### DP-1 Resolution: Single schema with content_type discriminator

One intake schema covers both meetings and reflections. The `content_type` field determines which downstream processing path applies. This avoids maintaining parallel schemas for content that shares 80%+ of landing structure.

| Content Type | Description | Routing Trigger |
|---|---|---|
| `meeting` | Multi-party conversation with transcript | Default for Fireflies and Fathom; Pocket when multi-speaker signals detected |
| `reflection` | Single-party voice note, dictation, or monologue | Default for Pocket; any single-speaker source |

**Discriminator field:** `manifest.content_type` (required, enum: `meeting`, `reflection`)

### Content type routing rules

**Fireflies:** Always `meeting`. Fireflies records scheduled calls between two or more parties. No ambiguity.

**Fathom:** Always `meeting`. Fathom is a video call notetaker that joins scheduled meetings. No ambiguity.

**Pocket:** Default `reflection` unless initial evaluation detects meeting signals:
- **Meeting signals (override to `meeting`):**
  - 2+ distinct speaker labels in transcript
  - Transcript metadata contains `participants` array with length > 1
  - Duration > 5 minutes AND multiple speaker turns detected
- **Reflection signals (keep as `reflection`):**
  - Single speaker or no speaker labels
  - Source metadata `type` field contains "note", "memo", "dictation"
  - Duration < 3 minutes with single voice

**Recovered historical content:** Content type inferred from restore-map artifact family and manifest evidence. Week-folder and archive content → `meeting`. Items with single-speaker transcripts or no participant roster → evaluate individually; default `reflection` when ambiguous.

---

## 3. Canonical Folder Structure

Every intake folder MUST conform to this layout:

```
Personal/Meetings/Inbox/<item-id>/
├── manifest.json          # REQUIRED — contract metadata
├── transcript.md          # REQUIRED — normalized readable transcript
├── transcript.jsonl       # OPTIONAL — structured speaker-turn transcript (Fireflies)
└── metadata.json          # OPTIONAL — raw source metadata preserved verbatim
```

### 3.1 Folder naming convention

Format: `YYYY-MM-DD_<Descriptive-Slug>`

| Content Type | Naming Pattern | Examples |
|---|---|---|
| `meeting` | `YYYY-MM-DD_Participant-Name` or `YYYY-MM-DD_Participant-x-Participant` | `2026-03-10_Nick-Freund-Vrijen-Attawar_Intro-Chat` |
| `reflection` | `YYYY-MM-DD_Reflection-Topic-Slug` | `2026-03-10_Reflection-Product-Roadmap-Thoughts` |

Rules:
- Date is the meeting/recording date, not the ingest date
- Slug is kebab-case, derived from title or participants
- No filesystem state suffixes (`_[P]`, `_[M]`, `_[C]`) — state lives in the manifest only
- No special characters beyond hyphens and underscores

---

## 4. Manifest Schema (Intake Subset)

At intake time, the manifest MUST contain these fields. Later pipeline stages (identify, gate, process) add additional fields — the full post-processing schema is defined in `manifest-v3.schema.json`.

### 4.1 Required fields at intake

```json
{
  "$schema": "manifest-v3",
  "meeting_id": "2026-03-10_Nick-Freund-Vrijen-Attawar",
  "content_type": "meeting",
  "status": "ingested",
  "status_history": [
    {"status": "ingested", "at": "2026-03-10T22:00:00Z"}
  ],
  "source": {
    "type": "fireflies",
    "original_filename": "Nick Freund x Vrijen Attawar - 2026-03-10.jsonl",
    "ingested_at": "2026-03-10T22:00:00Z",
    "adapter": "fireflies_v1"
  },
  "meeting": {
    "date": "2026-03-10",
    "title": "Nick Freund x Vrijen Attawar Intro Chat",
    "type": "external",
    "summary": "Introductory call between V and Nick Freund via Pam's referral."
  },
  "timestamps": {
    "created_at": "2026-03-10T22:00:00Z",
    "ingested_at": "2026-03-10T22:00:00Z"
  }
}
```

### 4.2 Field specifications

| Field | Type | Required at Intake | Notes |
|---|---|---|---|
| `$schema` | string | YES | Always `"manifest-v3"` |
| `meeting_id` | string | YES | Matches folder name. Pattern: `YYYY-MM-DD_Slug` |
| `content_type` | enum | YES | `"meeting"` or `"reflection"` |
| `status` | enum | YES | Must be `"ingested"` at intake landing |
| `status_history` | array | YES | At least one entry with `status: "ingested"` |
| `source.type` | enum | YES | `"fireflies"`, `"fathom"`, `"pocket"`, `"manual"`, `"recovered"` |
| `source.original_filename` | string | YES | Original filename before normalization |
| `source.ingested_at` | datetime | YES | ISO 8601 UTC timestamp |
| `source.adapter` | string | YES | Adapter version that performed normalization (see §6) |
| `meeting.date` | date | YES | `YYYY-MM-DD` — the actual meeting/recording date |
| `meeting.title` | string | YES | Human-readable title |
| `meeting.type` | enum | Meetings only | `"external"` or `"internal"` — omit for reflections |
| `meeting.summary` | string | YES | One-paragraph summary generated during ingest |
| `meeting.time_utc` | time | NO | `HH:MM:SS` — set when extractable from source |
| `meeting.duration_minutes` | integer | NO | Set when extractable from source |
| `participants.identified` | array | Meetings only | At least one participant for meetings; omit for reflections |
| `participants.unidentified` | array | NO | Speaker labels not yet matched to identities |
| `participants.confidence` | number | NO | 0.0–1.0, set during identification stage |
| `provenance` | object | For recovered items | Recovery lineage (see §5) |

### 4.3 Reflection-specific manifest shape

Reflections use the same schema but with relaxed requirements:

```json
{
  "$schema": "manifest-v3",
  "meeting_id": "2026-03-10_Reflection-Product-Roadmap",
  "content_type": "reflection",
  "status": "ingested",
  "status_history": [
    {"status": "ingested", "at": "2026-03-10T22:00:00Z"}
  ],
  "source": {
    "type": "pocket",
    "original_filename": "voice_note_2026-03-10_14-22.m4a.md",
    "ingested_at": "2026-03-10T22:00:00Z",
    "adapter": "pocket_v1"
  },
  "meeting": {
    "date": "2026-03-10",
    "title": "Product Roadmap Thoughts",
    "summary": "V's reflections on Q2 product roadmap priorities and feature sequencing."
  },
  "timestamps": {
    "created_at": "2026-03-10T22:00:00Z",
    "ingested_at": "2026-03-10T22:00:00Z"
  }
}
```

Key differences from meeting manifests:
- `content_type` is `"reflection"` (drives downstream processing path)
- `meeting.type` is omitted (internal/external distinction doesn't apply)
- `participants` section is omitted entirely (single speaker assumed)
- Later pipeline stages may add a lighter block set (no stakeholder intelligence, no action items with multiple owners)

---

## 5. Provenance Fields

### 5.1 For live-ingested items (standard pipeline)

The `source` block is sufficient provenance. The `source.adapter` field records which adapter version performed normalization.

### 5.2 For recovered historical items

Recovered items MUST carry an additional `provenance` block:

```json
{
  "provenance": {
    "recovery_source": "Zo Meetings copy-e49d20a9b948.zip",
    "recovery_drop": "D3.1",
    "original_zip_path": "Week-of-2025-09-01/2025-09-04_Jacob-bank-relay-Educational/",
    "original_state_family": "week",
    "original_state_marker": "_[P]",
    "restored_at": "2026-03-10T22:00:00Z",
    "restored_by_build": "meeting-system-recovery-redesign"
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `recovery_source` | string | YES | Zip filename or recovery corpus identifier |
| `recovery_drop` | string | YES | Build drop that performed the restore |
| `original_zip_path` | string | YES | Exact path within the zip |
| `original_state_family` | enum | YES | `"week"`, `"archive"`, `"inbox"`, `"quarantine"` |
| `original_state_marker` | string | YES | Historical suffix (`"_[P]"`, `"_[M]"`, `".processed"`, `"none"`) |
| `restored_at` | datetime | YES | ISO 8601 timestamp of restore execution |
| `restored_by_build` | string | YES | Build slug that performed the restore |

Provenance is append-only. Once written, provenance fields are never overwritten by later pipeline stages.

---

## 6. Source Adapters

Each source system has a dedicated adapter that transforms raw input into the canonical landing shape. Adapters are deterministic: same raw input always produces same normalized output.

### 6.1 Fireflies Adapter (`fireflies_v1`)

**Input formats:** `.jsonl` (speaker-turn structured transcript) and/or `.md` (markdown summary)

**Normalization steps:**
1. Detect input format (JSONL vs markdown vs both)
2. If JSONL present: preserve as `transcript.jsonl`, generate `transcript.md` from speaker turns
3. If markdown only: use as `transcript.md` directly
4. Extract meeting date from filename pattern or transcript header
5. Extract participants from speaker labels in transcript
6. Extract duration from JSONL metadata or transcript timestamps
7. If raw `metadata.json` exists in source: preserve verbatim as `metadata.json`
8. Generate `manifest.json` with `source.type: "fireflies"`, `source.adapter: "fireflies_v1"`, `content_type: "meeting"`
9. Create folder with naming convention, move all normalized files into it

**Content type:** Always `meeting` (Fireflies only records multi-party calls)

### 6.2 Fathom Adapter (`fathom_v1`)

**Input formats:** `.md` (transcript with AI-generated summary sections)

**Normalization steps:**
1. Parse Fathom markdown format (typically includes summary, action items, and full transcript sections)
2. Extract full transcript section as `transcript.md`
3. Extract meeting date from filename or transcript header
4. Extract participants from speaker labels
5. If Fathom-specific metadata sections exist: extract to `metadata.json`
6. Generate `manifest.json` with `source.type: "fathom"`, `source.adapter: "fathom_v1"`, `content_type: "meeting"`
7. Create folder with naming convention

**Content type:** Always `meeting` (Fathom only records scheduled video calls)

### 6.3 Pocket Adapter (`pocket_v1`)

**Input formats:** `.md` (transcribed voice note) or `.m4a.md` (transcribed audio)

**Normalization steps:**
1. Parse transcript content
2. Evaluate content type using meeting signal detection (see §2):
   - Count distinct speaker labels
   - Check for multi-party conversation indicators
   - Default to `reflection` unless meeting signals exceed threshold
3. Normalize transcript as `transcript.md`
4. Extract date from filename or file creation metadata
5. Generate title from first ~100 words of content (via LLM summarization during ingest)
6. Generate `manifest.json` with `source.type: "pocket"`, `source.adapter: "pocket_v1"`, `content_type` per evaluation result
7. Create folder with naming convention

**Content type:** Default `reflection`. Override to `meeting` only when meeting signals detected per §2 rules.

### 6.4 Recovery Adapter (`recovery_v1`)

**Input formats:** Meeting folders from historical zip corpus (mixed layouts)

**Normalization steps:**
1. Identify source family from restore-map classification (`week`, `archive`, `inbox`, `quarantine`)
2. Locate transcript file (look for `transcript.md`, `transcript.jsonl`, or `.md` files matching transcript patterns)
3. If processed blocks exist (B01, B03, etc.): preserve them in the normalized folder (they represent completed work)
4. If historical `manifest.json` exists: read it, extract usable fields, discard v2-era status fields
5. Infer `source.type` from evidence:
   - Fireflies JSONL header present → `"fireflies"`
   - Fathom markdown format detected → `"fathom"`
   - Otherwise → `"manual"`
6. Strip historical state suffixes from folder name (`_[P]`, `_[M]`, `_[C]`, `_[B]`)
7. Generate `manifest.json` with `source.type` per inference, `source.adapter: "recovery_v1"`, plus `provenance` block (see §5.2)
8. Set content type from evidence (participant count, transcript structure)
9. Set status based on existing processed state:
   - Has generated blocks → `"processed"` (skip re-processing)
   - Has transcript only → `"ingested"` (needs full pipeline)
   - Has identification data but no blocks → `"identified"` (needs gate + process)

**Content type:** Inferred from transcript evidence and historical metadata.

### 6.5 Manual Adapter (`manual_v1`)

**Input formats:** Any `.md` or `.txt` transcript file manually placed in Inbox

**Normalization steps:**
1. Parse content, detect format
2. Evaluate content type using meeting signal detection (same as Pocket)
3. Extract date from filename or content
4. Generate title via LLM summarization
5. Create normalized folder with manifest

**Content type:** Inferred from content analysis. Default `meeting` if multi-speaker; `reflection` if single-speaker.

---

## 7. Ready-to-Process Definition

### DP-2 Resolution: Minimum required assets

An intake folder is **ready-to-process** when ALL of the following are true:

| Check | Requirement | Rationale |
|---|---|---|
| Folder exists | `Personal/Meetings/Inbox/<item-id>/` is a directory | Physical container |
| Manifest exists | `manifest.json` is present and valid JSON | Contract anchor |
| Schema version | `$schema` is `"manifest-v3"` | Forward compatibility |
| Content type set | `content_type` is `"meeting"` or `"reflection"` | Routing discriminator |
| Status is ingested | `status` is `"ingested"` (or later stage for recovered items) | Pipeline entry point |
| Transcript exists | `transcript.md` exists and has ≥300 characters of content | Minimum processable content |
| Meeting date set | `meeting.date` is a valid `YYYY-MM-DD` date | Chronological anchor |
| Title set | `meeting.title` is non-empty | Human-readable identifier |
| Source recorded | `source.type` and `source.adapter` are set | Lineage tracking |

### What is NOT required at intake (populated by later stages)

- `participants` details (populated by `identify` stage)
- `calendar_match` (populated by `identify` stage)
- `quality_gate` (populated by `gate` stage)
- `blocks` (populated by `process` stage)
- `meeting.time_utc` (best-effort at intake, refined by `identify`)
- `meeting.duration_minutes` (best-effort at intake, refined by `identify`)

### Ready-to-process validation

A simple check script should be able to validate readiness:

```python
def is_ready_to_process(folder_path: Path) -> tuple[bool, list[str]]:
    """Return (ready, list_of_failures)."""
    failures = []
    manifest_path = folder_path / "manifest.json"
    transcript_path = folder_path / "transcript.md"

    if not folder_path.is_dir():
        failures.append("folder does not exist")
    if not manifest_path.exists():
        failures.append("manifest.json missing")
    else:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("$schema") != "manifest-v3":
            failures.append("schema version is not manifest-v3")
        if manifest.get("content_type") not in ("meeting", "reflection"):
            failures.append("content_type missing or invalid")
        if manifest.get("status") not in ("ingested", "identified", "gated", "processed"):
            failures.append("status is not a valid pipeline state")
        if not manifest.get("meeting", {}).get("date"):
            failures.append("meeting.date missing")
        if not manifest.get("meeting", {}).get("title"):
            failures.append("meeting.title missing")
        if not manifest.get("source", {}).get("type"):
            failures.append("source.type missing")
        if not manifest.get("source", {}).get("adapter"):
            failures.append("source.adapter missing")
    if not transcript_path.exists():
        failures.append("transcript.md missing")
    elif transcript_path.stat().st_size < 300:
        failures.append("transcript.md too short (<300 chars)")

    return (len(failures) == 0, failures)
```

---

## 8. Landing States

### 8.1 Raw landed state (pre-intake)

Raw files may appear in `Personal/Meetings/Inbox/` as loose files before adapter processing:

- `*.jsonl` — Fireflies raw transcript
- `*.md` — Fathom/Pocket/manual transcript
- `metadata.json` — Source system metadata

**Raw files are NOT ready-to-process.** They must pass through an adapter (§6) to become normalized folders.

### 8.2 Normalized landed state (ready-to-process)

After adapter processing, the folder satisfies all §7 checks. This is the intake contract boundary — everything downstream (identify, gate, process, archive) operates on normalized folders only.

### 8.3 State transitions after intake

```
[raw files]  →  adapter  →  [ingested]  →  identify  →  [identified]  →  gate  →  [gated]  →  process  →  [processed/complete]  →  archive  →  [archived]
                              ↑
                        CONTRACT BOUNDARY
                   (this document defines this shape)
```

The intake contract governs everything up to and including the `ingested` state. Subsequent states are governed by the pipeline's own state machine (documented in SKILL.md and manifest-v3.schema.json).

---

## 9. Transcript Normalization Rules

Regardless of source, `transcript.md` MUST conform to these rules:

### 9.1 Format requirements

- **Encoding:** UTF-8, no BOM
- **Speaker labels:** `Speaker Name:` prefix on new lines when multiple speakers present
- **Timestamps:** Optional inline timestamps in `[HH:MM:SS]` format if available from source
- **No HTML or source-specific markup** — clean markdown only
- **Minimum length:** 300 characters of actual content (excluding headers/metadata)

### 9.2 For meetings (multi-speaker)

```markdown
**Speaker A:** Opening remarks and context setting for the conversation.

**Speaker B:** Response and discussion of main topics.

**Speaker A:** Follow-up questions and exploration of key points.
```

### 9.3 For reflections (single-speaker)

```markdown
Reflections on the product roadmap discussion from earlier today. Three key themes emerged...
```

No speaker labels needed for reflections (single voice assumed).

### 9.4 Source-specific cleanup

| Source | Cleanup Rules |
|---|---|
| Fireflies | Strip JSONL metadata from markdown output; preserve speaker labels; remove Fireflies header/footer boilerplate |
| Fathom | Extract transcript section from full Fathom output (skip AI summary sections — those are Fathom's work, not ours); preserve speaker labels |
| Pocket | Strip audio transcription artifacts (filler words like "um", "uh" are acceptable but encoding glitches should be removed); normalize speaker label if present |
| Recovered | Preserve existing transcript as-is if it's already clean markdown; strip historical pipeline annotations if present |

---

## 10. Schema Extension Points

This contract is designed for extension without breaking existing adapters:

### 10.1 Adding a new source

1. Create a new adapter function following §6 patterns
2. Add the source type to `source.type` enum (`"newsource"`)
3. Define adapter version string (`"newsource_v1"`)
4. Document normalization steps
5. Existing manifests and pipeline stages are unaffected

### 10.2 Adding a new content type

1. Add to `content_type` enum (e.g., `"workshop"`, `"interview"`)
2. Define required vs optional fields for the new type
3. Define downstream processing path (which blocks apply)
4. Update content type routing rules in §2
5. Existing content types are unaffected

### 10.3 Adding new manifest fields

- New optional fields can be added without schema version bump
- New required fields require schema version bump (`manifest-v4`)
- Adapters should tolerate and preserve unknown fields (forward compatibility)

---

## 11. Contract Verification Checklist

For any source adapter implementation, verify:

- [ ] Output folder name matches `YYYY-MM-DD_Slug` pattern
- [ ] `manifest.json` passes ready-to-process validation (§7)
- [ ] `transcript.md` exists with ≥300 characters of content
- [ ] `content_type` is correctly classified per §2 routing rules
- [ ] `source.type` and `source.adapter` are set
- [ ] For Pocket: default is `reflection` unless meeting signals detected
- [ ] For recovered items: `provenance` block is present and complete
- [ ] No historical state suffixes in folder names
- [ ] No raw-only state persists in Inbox (raw files are transient staging)
- [ ] Transcript conforms to §9 normalization rules
