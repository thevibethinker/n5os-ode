# Technical Requirements: Demonstrator Account & Cloning Protocol

**Reflection ID:** 2025-10-20_zo-system-gtm\
**Status:** Draft for review\
**Scope:** Define demonstrator configuration, Zo Bridge requirements, and cloning steps

---

## 1) Demonstrator Account: Target State

### 1.1 Core Components (Must be present)

- Reflection ingestion pipeline: email + manual staging → processing → proposal
- Meeting ingestion pipeline: calendar integration (Google Calendar) → summary/notes → storage
- Knowledge base structure: Records/, Knowledge/ (sequester until promoted)
- Lists subsystem: ideas, system-upgrades, output_reviews, etc.
- Commands registry: commands.jsonl and key commands enabled (reflection-ingest, auto-process-meetings, thread-export)
- Session state management: session_state_manager wired for new conversations

### 1.2 Required Integrations

- Gmail (Zo app tools) for ingestion (read-only)
- Google Drive (optional) for Drive-based reflection sources
- Calendar (Google) for meeting ingestion

### 1.3 Environment

- Debian 12 base, Python 3.12, ffmpeg, pandoc installed
- Zo scripts and N5 folder structure present

---

## 2) Zo Bridge Functionality (Blocking)

### 2.1 Definition

Zo Bridge = minimal, reliable glue that:

- Normalizes external inputs (email/drive/audio/text)
- Ensures transcripts exist for audio/text
- Routes reflections to pipeline with correct metadata (classification tags)
- Updates registry and proposes outputs without side effects

### 2.2 Requirements

- Text reflections: auto-wrap to `file .transcript.jsonl`  (now implemented in reflection_worker)
- Audio reflections: enforce transcription via transcribe_audio or ingest command
- Error handling: idempotent re-runs; safe on duplicates
- Logging: INFO-level with file paths; errors with context

---

## 3) Cloning Protocol (Demonstrator → Customer)

### 3.1 Pre-Clone Checklist

- [ ]   Demonstrator passes self-test (ingestion, outputs, lists write)

- [ ]   Integrations prepared (customer Gmail/Drive/Calendar auth steps documented)

- [ ]   Customer folders created: Records/, Knowledge/, Lists/

### 3.2 Clone Steps

1. Snapshot demonstrator configuration (scripts, prefs, commands, structure)
2. Programmatically copy to customer workspace (excluding personal data, logs, convo workspaces)
3. Run post-clone initializer: 
   - Reset state files (.state.json, registries)
   - Rebuild commands registry
   - Prompt for integration auth (gmail/drive/calendar)
4. Validate with automated smoke test command: reflection test file → pipeline → outputs

### 3.3 Post-Clone

- Provide onboarding script for Week 1-2 usage
- Optional training modules

---

## 4) Security & Safety

- No automatic sends; all external interactions require explicit approval
- Sequester outputs by default; promote to Knowledge/stable only on approval
- Commands-first enforcement in prefs (completed)

---

## 5) Open Items

- Define exact integration auth flow for customer environments
- Document environment variables/config points (if any)
- Add dedicated smoke test command

---

## 6) Next Actions

1. Implement smoke test command and script
2. Write post-clone initializer script
3. Document customer integration onboarding
4. Dry-run a full clone into a sandbox workspace