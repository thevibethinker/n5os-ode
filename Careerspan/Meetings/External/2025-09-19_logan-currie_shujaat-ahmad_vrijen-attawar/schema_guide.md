# External Meeting Bundle — Consumer Schema Guide (v1.1)

This guide explains how downstream workflows should read this bundle and which JSON Pointers to use.

Bundle layout
- content_map.json — authoritative structured map for this meeting
- segments.json — time‑bounded segment summaries that reference content_map.json
- attachments/
  - transcript.txt — canonical transcript copy (time‑anchored)
  - source.url — original Google Doc link
  - checksums.sha256 — sha256 for transcript.txt
- manifest.json — creation metadata, paths, counts
- README.md — human overview

Core principles
- Time‑anchored: every actionable/decisional item is rooted in a timestamp.
- Pointer‑addressable: use JSON Pointers (RFC 6901‑style, starting with `#/`) to locate content.
- Stable contracts: fields and indices below are designed for programmatic consumption.

content_map.json (top‑level)
- source_file: relative path to canonical transcript
- meeting_datetime: ISO8601 UTC
- participants: [string]
- duration_seconds: int
- deliverables: [string | object]
- ctas: [{ owner, time, text, verbatim }]
- decisions: [{ time (or range), speaker, decision, verbatim }]
- resonance_details: [{ speaker, time, text }]
- speaker_quotes: [string]
- warm_intro_opportunities: [object]
- metadata, lessons_learned, entities, summary
- topics: [{ id, title, time_range:[start,end], evidence:[{time,speaker,quote}] }]
- risks, opportunities, key_facts
- speaker_index: per‑speaker pointers to CTAs/resonance/quotes
- timeline: chronologically sorted CTAs/decisions with pointers
- indices: pointer indexes (cta_index, decision_index, quote_index, topic_index, risk_index, opportunity_index, fact_index)
- toc: table of contents → JSON Pointers
- field_index: programmatic field → JSON Pointer map
- attachments: canonical transcript and origin URL

segments.json (top‑level)
- schema, schema_version, generated_at
- source_content_map: "content_map.json"
- source_transcript: "attachments/transcript.txt"
- segments: [{
  id, time_range:[start,end], seconds_range:[a,b], speakers:[...],
  excerpts:{head,tail},
  pointers:{ ctas:[{pointer,time,owner}], decisions:[{pointer,time}], topics:[{pointer,title}] },
  summary, key_points:[...], notable_quotes:[...]
}]

JSON Pointers (how to use)
- Pointers start from the root of content_map.json.
- Example addresses:
  - CTAs: `#/ctas/0`, `#/ctas/1`, …
  - Decisions: `#/decisions/0`
  - Topics: `#/topics/3`
  - Quotes: `#/speaker_quotes/2`
  - Risks: `#/risks/1`
  - Opportunities: `#/opportunities/0`
  - Facts: `#/key_facts/4`
- Index helpers:
  - `#/indices/cta_index` → array of `{ pointer, owner, time, summary }`
  - `#/indices/decision_index` → array of `{ pointer, time, summary }`
  - `#/indices/topic_index` → array of `{ pointer, title, time_range }`

Downstream workflow recipes
- Follow‑up email
  - Read CTAs via `#/indices/cta_index` (prioritize owner=Logan Currie).
  - Pull 1–2 resonance details `#/resonance_details` and one quote `#/speaker_quotes`.
  - If helpful, frame with `#/decisions` (ICP, buyers) and `#/summary`.
- Warm intro ticketing
  - Use `#/warm_intro_opportunities` (if empty, scan `#/topics` for collab cues like involvement tiers).
  - Include participants `#/participants`.
- Blurb generation
  - Iterate `#/topics`, produce 1–3 sentence blurbs, anchor with a `#/speaker_quotes/*` and optional `#/resonance_details/*`.
- Knowledge ingestion
  - Consume `#/key_facts`, `#/decisions`, `#/deliverables` (preserve anchors/time).
- Calendar follow‑ups
  - From `#/ctas`, map owner + time to scheduling prompts.

Contracts & invariants
- Arrays are append‑only; indices remain stable within a bundle version.
- Times are mm:ss; ranges use an en dash (e.g., "22:52–23:30").
- All pointers in `segments.json` must resolve within `content_map.json`.
- attachments/transcript.txt is the canonical text used for extraction; sha256 in checksums.sha256 must match.

Minimal pointer resolver (pseudocode)
- Split pointer by `/`; iterate keys/indices from the JSON root.
- Fail fast if any key/index is missing; treat as schema violation.

Changelog
- v1.1: Added attachments, risks/opportunities/key_facts, indices for risks/opportunities/facts, speaker_index, timeline, field_index, segments.json schema, and this guide.
