---
created: 2025-12-23
last_edited: 2025-12-23
version: 1.1
type: build_plan
status: approved
provenance: con_eCLbOiRyc7HgzEQp
---

# Plan: Unified Meeting Intake System

**Objective:** Standardize all meeting transcript ingestion (Fathom, Fireflies, Manual, Granola) through a single "Intake Kernel" that applies consistent date detection, deduplication, folder naming, and metadata generation.

**Trigger:** V requested a "Manual Pseudo-Webhook" for pasting transcripts from any source, and observed that Fathom/Fireflies currently have duplicated logic. V wants ONE standard for all sources.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

<!-- Surface unknowns HERE at the TOP. Resolve before proceeding. -->
- [x] Which architectural pattern to use? → **RESOLVED: Thin Adapter Pattern (Alternative A)**
- [x] Should the unified kernel live in `N5/scripts/utils/` or `N5/services/shared/`? → **RESOLVED:** `N5/services/intake/` as a new package (keeps services together, signals "this is infrastructure")
- [x] What is the canonical date detection order? → **RESOLVED:** (1) Semantic extraction from transcript, (2) Google Calendar lookup, (3) Default to today
- [x] Should we create a `POLICY.md` for `Personal/Meetings/`? → **RESOLVED:** Yes, Phase 0
- [x] Level Upper review complete? → **RESOLVED:** Yes, 4 recommendations incorporated

---

## Checklist

<!-- Concise one-liners. ☐ = pending, ☑ = complete. Zo updates as it executes. -->

### Phase 0: Safe Harbor (Registry & Protection)
- ☐ Create migration registry at `N5/logs/migration/unified-intake-registry.json`
- ☐ Inventory all existing scripts/services being shadowed
- ☐ Create `Personal/Meetings/POLICY.md` to document the standard
- ☐ Snapshot current state (no deletions until Phase 4 complete)

### Phase 1: The Unified Intake Kernel
- ☐ Create `N5/services/intake/` package structure
- ☐ Create `N5/services/intake/models.py` - UnifiedTranscript dataclass
- ☐ Create `N5/services/intake/date_detector.py` - V Priority Order logic
- ☐ Create `N5/services/intake/calendar_cache.py` - Calendar lookup caching (Level Upper)
- ☐ Create `N5/services/intake/deduplicator.py` - SQLite-indexed dedup (Level Upper)
- ☐ Create `N5/services/intake/validators.py` - Output validation layer (Level Upper)
- ☐ Create `N5/services/intake/folder_manager.py` - Naming & creation
- ☐ Create `N5/services/intake/intake_engine.py` - Orchestrator
- ☐ Create adapters: base, fathom, fireflies, manual
- ☐ Test: Unit tests for date detection with sample transcripts

### Phase 2: Manual Ingest Tool & Prompt
- ☐ Create `N5/scripts/manual_ingest.py` - CLI tool (requires --participants for manual)
- ☐ Create `Prompts/Manual Transcript Ingest.prompt.md` - Conversational wrapper
- ☐ Test: Integration test - real transcript → full validation pass (Level Upper)

### Phase 3: Service Migration (Fathom & Fireflies)
- ☐ Update `N5/services/fathom_webhook/transcript_processor.py` to use intake engine
- ☐ Update `N5/services/fireflies_webhook/transcript_processor.py` to use intake engine
- ☐ Test: Trigger a test webhook, verify it uses new kernel
- ☐ Mark old `DuplicateManager` classes as `# DEPRECATED - use intake.deduplicator`

### Phase 4: Cleanup & Finalization
- ☐ Update migration registry with `status: migrated`
- ☐ Add deprecation notices to old code paths
- ☐ Update STATUS.md with completion summary
- ☐ Return to Operator

---

## Phase 0: Safe Harbor (Registry & Protection)

### Affected Files
- `N5/logs/migration/unified-intake-registry.json` - CREATE - Migration tracking
- `Personal/Meetings/POLICY.md` - CREATE - System documentation
- `N5/builds/unified-meeting-intake/STATUS.md` - UPDATE - Progress tracking

### Changes

**0.1 Create Migration Registry:**
Create `N5/logs/migration/unified-intake-registry.json` with structure:
```json
{
  "build_id": "unified-meeting-intake",
  "created": "2025-12-23",
  "status": "in_progress",
  "legacy_artifacts": [
    {
      "path": "N5/services/fireflies_webhook/transcript_processor.py",
      "type": "service",
      "status": "legacy_active",
      "replacement": "N5/services/intake/intake_engine.py"
    },
    {
      "path": "N5/services/fathom_webhook/transcript_processor.py",
      "type": "service",
      "status": "legacy_active",
      "replacement": "N5/services/intake/intake_engine.py"
    }
  ],
  "new_artifacts": []
}
```

**0.2 Create Meetings POLICY.md:**
Document the standard folder structure, naming conventions, and state transitions:
- `[M]` = Manifest Generated (ready for processing)
- `[P]` = Processed (intelligence blocks complete)
- `[C]` = Complete (archived)
- Required files: `transcript.jsonl`, `metadata.json`, `manifest.json`
- Folder naming: `YYYY-MM-DD_participant-names_[STATE]`

**0.3 Inventory Current State:**
Record in registry:
- Fireflies service: running, port 8767
- Fathom service: running, port 8768
- Related prompts: `Prompts/Meeting Process.prompt.md`, etc.

### Unit Tests
- Verify registry JSON is valid
- Verify POLICY.md created at correct location

---

## Phase 1: The Unified Intake Kernel

### Affected Files
- `N5/services/intake/__init__.py` - CREATE - Package init
- `N5/services/intake/models.py` - CREATE - Data models
- `N5/services/intake/date_detector.py` - CREATE - Date extraction logic
- `N5/services/intake/calendar_cache.py` - CREATE - Calendar lookup caching (Level Upper)
- `N5/services/intake/deduplicator.py` - CREATE - SQLite-indexed dedup (Level Upper)
- `N5/services/intake/validators.py` - CREATE - Output validation (Level Upper)
- `N5/services/intake/folder_manager.py` - CREATE - Folder operations
- `N5/services/intake/intake_engine.py` - CREATE - Main orchestrator
- `N5/services/intake/adapters/` - CREATE - Source-specific adapters
- `N5/services/intake/adapters/fathom_adapter.py` - CREATE
- `N5/services/intake/adapters/fireflies_adapter.py` - CREATE
- `N5/services/intake/adapters/manual_adapter.py` - CREATE

### Changes

**1.1 Create Package Structure:**
```
N5/services/intake/
├── __init__.py
├── models.py           # UnifiedTranscript, UnifiedMetadata
├── date_detector.py    # V Priority Order
├── calendar_cache.py   # Cache calendar lookups (1hr TTL) - Level Upper
├── deduplicator.py     # SQLite-indexed dedup - Level Upper
├── validators.py       # Output validation layer - Level Upper
├── folder_manager.py   # Naming, creation, state markers
├── intake_engine.py    # Main entry point
├── adapters/
│   ├── __init__.py
│   ├── base.py         # Abstract base adapter
│   ├── fathom_adapter.py
│   ├── fireflies_adapter.py
│   └── manual_adapter.py
└── tests/
    ├── __init__.py
    └── test_date_detector.py
```

**1.2 Define UnifiedTranscript Model (`models.py`):**
```python
@dataclass
class UnifiedTranscript:
    """The canonical transcript shape all sources convert TO."""
    text: str                       # Full transcript text
    utterances: List[Utterance]     # Speaker-segmented entries
    source: str                     # "fathom", "fireflies", "manual", "granola"
    source_id: Optional[str]        # Original ID from source
    raw_date: Optional[str]         # Date string as found in source
    detected_date: Optional[datetime]  # Parsed/detected date
    participants: List[str]         # Participant names/emails
    title: Optional[str]            # Meeting title
    duration_seconds: Optional[int]
    extra: Dict[str, Any]           # Source-specific extras (summaries, etc.)

@dataclass
class Utterance:
    speaker: str
    text: str
    start_ms: Optional[int]
    end_ms: Optional[int]
```

**1.3 Implement Date Detector (`date_detector.py`):**
V Priority Order:
1. **Semantic Extraction:** Scan first 2000 chars of transcript for date patterns
   - ISO dates: `2025-12-23`
   - Natural language: "December 23rd, 2025", "today", "yesterday"
   - Relative: "last Tuesday" (requires current date context)
2. **Calendar Lookup:** Use cached calendar client to find matching events
   - Match by: participants AND time window (±2 hours from now if no date found)
3. **Default to Today:** If neither works, use `datetime.now()`

Return: `DetectionResult(date: datetime, method: str, confidence: float)`

**1.4 Implement Calendar Cache (`calendar_cache.py`) - Level Upper:**
```python
class CalendarCache:
    """Cache Google Calendar lookups to prevent rate limiting at scale."""
    
    def __init__(self, ttl_seconds: int = 3600):  # 1 hour TTL
        self.cache: Dict[str, Tuple[datetime, List[dict]]] = {}
        self.ttl = ttl_seconds
    
    def get_events(self, date: datetime, force_refresh: bool = False) -> List[dict]:
        """Get events for date, using cache if available."""
        cache_key = date.strftime("%Y-%m-%d")
        
        if not force_refresh and cache_key in self.cache:
            cached_at, events = self.cache[cache_key]
            if (datetime.now() - cached_at).seconds < self.ttl:
                return events
        
        # Fetch from Google Calendar
        events = self._fetch_from_calendar(date)
        self.cache[cache_key] = (datetime.now(), events)
        return events
```

**1.5 Implement Deduplicator (`deduplicator.py`) - Level Upper:**
Use SQLite index instead of filesystem scanning:
```python
class Deduplicator:
    """SQLite-indexed duplicate detection for O(1) lookups."""
    
    DB_PATH = Path("/home/workspace/N5/data/intake_dedup.db")
    
    def __init__(self):
        self._init_db()
    
    def _init_db(self):
        """Create dedup index table if not exists."""
        conn = sqlite3.connect(self.DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meeting_index (
                id INTEGER PRIMARY KEY,
                source TEXT,
                source_id TEXT,
                date TEXT,
                participant_hash TEXT,
                folder_path TEXT,
                created_at TEXT,
                UNIQUE(source, source_id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON meeting_index(date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_participant ON meeting_index(participant_hash)")
        conn.commit()
        conn.close()
    
    def find_duplicate(self, unified: UnifiedTranscript) -> Optional[Path]:
        """Check if meeting already exists. Returns existing folder or None."""
        # 1. Check by source_id (exact match)
        # 2. Check by date + participant_hash (±45 min window)
        pass
    
    def register(self, unified: UnifiedTranscript, folder: Path):
        """Register new meeting in index."""
        pass
```

**1.6 Implement Validators (`validators.py`) - Level Upper:**
```python
@dataclass
class ValidationError:
    field: str
    message: str
    severity: str  # "error" | "warning"

def validate_meeting_folder(folder: Path) -> List[ValidationError]:
    """Validate folder structure matches POLICY.md standard."""
    errors = []
    
    # Required files
    required = ["transcript.jsonl", "metadata.json"]
    for req in required:
        if not (folder / req).exists():
            errors.append(ValidationError(req, f"Missing required file: {req}", "error"))
    
    # Folder naming pattern
    name = folder.name
    if not re.match(r"^\d{4}-\d{2}-\d{2}_", name):
        errors.append(ValidationError("folder_name", "Folder must start with YYYY-MM-DD_", "error"))
    
    # transcript.jsonl structure
    transcript_file = folder / "transcript.jsonl"
    if transcript_file.exists():
        try:
            data = json.loads(transcript_file.read_text())
            if "text" not in data:
                errors.append(ValidationError("transcript.jsonl", "Missing 'text' field", "error"))
            if "utterances" not in data:
                errors.append(ValidationError("transcript.jsonl", "Missing 'utterances' field", "warning"))
        except json.JSONDecodeError as e:
            errors.append(ValidationError("transcript.jsonl", f"Invalid JSON: {e}", "error"))
    
    return errors

def validate_unified_transcript(unified: UnifiedTranscript) -> List[ValidationError]:
    """Validate UnifiedTranscript before ingestion."""
    errors = []
    
    if not unified.text or len(unified.text.strip()) < 50:
        errors.append(ValidationError("text", "Transcript text too short (<50 chars)", "error"))
    
    if not unified.participants:
        errors.append(ValidationError("participants", "No participants detected", "warning"))
    
    if unified.source not in ["fathom", "fireflies", "manual", "granola"]:
        errors.append(ValidationError("source", f"Unknown source: {unified.source}", "error"))
    
    return errors
```

**1.7 Implement Folder Manager (`folder_manager.py`):**
- `generate_folder_name(date, participants, source) -> str`
- `create_meeting_folder(inbox_path, folder_name) -> Path`
- `save_transcript_jsonl(folder, unified_transcript)`
- `save_metadata_json(folder, metadata)`
- `generate_manifest(folder)` - Reuse existing `generate_manifest.py` logic

**1.8 Implement Intake Engine (`intake_engine.py`):**
Main orchestrator class with validation:
```python
class IntakeEngine:
    def __init__(self, inbox_path=Path("/home/workspace/Personal/Meetings/Inbox")):
        self.date_detector = DateDetector()
        self.deduplicator = Deduplicator()
        self.folder_manager = FolderManager(inbox_path)
    
    def ingest(self, unified: UnifiedTranscript) -> IntakeResult:
        """Main entry point. Returns folder path or error."""
        # 0. Validate input (Level Upper)
        input_errors = validate_unified_transcript(unified)
        if any(e.severity == "error" for e in input_errors):
            return IntakeResult(status="validation_error", errors=input_errors)
        
        # 1. Check for duplicates
        existing = self.deduplicator.find_duplicate(unified)
        if existing:
            return IntakeResult(status="duplicate", existing_folder=existing)
        
        # 2. Detect/confirm date
        if not unified.detected_date:
            detection = self.date_detector.detect(unified)
            unified.detected_date = detection.date
        
        # 3. Create folder
        folder = self.folder_manager.create(unified)
        
        # 4. Save files
        self.folder_manager.save_transcript(folder, unified)
        self.folder_manager.save_metadata(folder, unified)
        self.folder_manager.generate_manifest(folder)
        
        # 5. Validate output (Level Upper)
        output_errors = validate_meeting_folder(folder)
        if any(e.severity == "error" for e in output_errors):
            return IntakeResult(status="output_validation_error", folder=folder, errors=output_errors)
        
        # 6. Register in dedup index
        self.deduplicator.register(unified, folder)
        
        return IntakeResult(status="success", folder=folder)
```

**1.9 Implement Adapters:**
Each adapter implements `adapt(source_data: dict) -> UnifiedTranscript`:
- `fathom_adapter.py`: Convert Fathom webhook payload → UnifiedTranscript
- `fireflies_adapter.py`: Convert Fireflies API response → UnifiedTranscript
- `manual_adapter.py`: Convert raw text + optional metadata → UnifiedTranscript

### Unit Tests
- `test_date_detector.py`:
  - Test: "December 23, 2025" → `datetime(2025, 12, 23)`
  - Test: "2025-12-23T10:00:00" → `datetime(2025, 12, 23, 10, 0)`
  - Test: No date found → returns `None` (triggers calendar lookup)
- Test Fathom adapter with sample payload
- Test Fireflies adapter with sample payload
- Test validators with valid/invalid folders
- Test deduplicator SQLite operations

---

## Phase 2: Manual Ingest Tool & Prompt

### Affected Files
- `N5/scripts/manual_ingest.py` - CREATE - CLI tool
- `Prompts/Manual Transcript Ingest.prompt.md` - CREATE - Conversational prompt

### Changes

**2.1 Create CLI Tool (`N5/scripts/manual_ingest.py`):**
```bash
python3 N5/scripts/manual_ingest.py --file transcript.txt --participants "John, Sarah"
python3 N5/scripts/manual_ingest.py --text "Paste raw text here" --participants "John, Sarah"
python3 N5/scripts/manual_ingest.py --file transcript.txt --date 2025-12-20 --title "Team Sync" --participants "John, Sarah"
```

Features:
- Accept file path OR stdin text
- **REQUIRED for manual source:** `--participants` flag (Level Upper recommendation)
- Optional flags: `--date`, `--title`
- If `--participants` missing for manual source, exit with error and prompt
- Use IntakeEngine to save

**2.2 Create Prompt (`Prompts/Manual Transcript Ingest.prompt.md`):**
```yaml
---
title: Manual Transcript Ingest
description: Process a manually provided transcript through the unified intake system
tags: [meetings, intake, transcript]
tool: true
---
```

Prompt behavior:
1. Accept transcript from user (paste or file mention)
2. Attempt date detection
3. If date uncertain, ask: "When was this meeting recorded? I see [X] in the transcript."
4. If participants unclear, ask: "Who was in this meeting? I detected [names]."
5. Confirm before saving: "I'll save this as: `2025-12-20_john-sarah/`. Proceed?"
6. Run manual_ingest.py
7. Report: "✓ Created `Personal/Meetings/Inbox/2025-12-20_john-sarah/`"

**2.3 Integration Test (Level Upper):**
```bash
# Test: Real transcript → full validation pass
python3 N5/scripts/manual_ingest.py --file /path/to/real/transcript.txt --participants "Test User"
python3 -c "
from N5.services.intake.validators import validate_meeting_folder
from pathlib import Path
folder = Path('/home/workspace/Personal/Meetings/Inbox/').glob('*Test*').__next__()
errors = validate_meeting_folder(folder)
assert not any(e.severity == 'error' for e in errors), f'Validation failed: {errors}'
print('✓ Integration test passed')
"
```

### Unit Tests
- Test CLI with sample transcript file
- Test CLI with missing --participants (should exit with error)
- Test prompt flow with mocked user responses
- Integration test: real transcript → folder validates against POLICY.md

---

## Phase 3: Service Migration (Fathom & Fireflies)

### Affected Files
- `N5/services/fathom_webhook/transcript_processor.py` - UPDATE - Use intake engine
- `N5/services/fireflies_webhook/transcript_processor.py` - UPDATE - Use intake engine
- `N5/logs/migration/unified-intake-registry.json` - UPDATE - Mark migrated

### Changes

**3.1 Update Fathom Processor:**
Replace `save_transcript_to_inbox()` method body:
```python
from N5.services.intake import IntakeEngine
from N5.services.intake.adapters import FathomAdapter

def save_transcript_to_inbox(self, payload: Dict[str, Any]) -> Optional[str]:
    adapter = FathomAdapter()
    unified = adapter.adapt(payload)
    
    engine = IntakeEngine()
    result = engine.ingest(unified)
    
    if result.status == "success":
        return result.folder.name
    elif result.status == "duplicate":
        return result.existing_folder.name
    else:
        return None
```

**3.2 Update Fireflies Processor:**
Same pattern as Fathom, using `FirefliesAdapter`.

**3.3 Deprecation Comments:**
Add to old `DuplicateManager` class:
```python
# DEPRECATED: Use N5.services.intake.deduplicator instead
# Kept for reference until Phase 4 cleanup (unified-meeting-intake build)
```

**3.4 Service Restart:**
After code changes:
```bash
# Restart Fathom webhook service
# (via user service restart or manual process restart)
```

### Unit Tests
- Trigger test Fathom webhook → verify folder created via new kernel
- Trigger test Fireflies webhook → verify folder created via new kernel
- Verify duplicate detection still works

---

## Phase 4: Cleanup & Finalization

### Affected Files
- `N5/logs/migration/unified-intake-registry.json` - UPDATE - Final status
- `N5/builds/unified-meeting-intake/STATUS.md` - UPDATE - Completion
- Various deprecated code - UPDATE - Add removal timeline

### Changes

**4.1 Update Registry:**
Mark all legacy artifacts as `status: migrated`. Add `migrated_date`.

**4.2 Add Removal Timeline:**
In deprecated code comments:
```python
# DEPRECATED: Safe to remove after 2026-01-15 if no issues reported
```

**4.3 Update STATUS.md:**
Document:
- What was built
- What was migrated
- Any lessons learned
- Links to new artifacts

**4.4 Handoff to Operator:**
Switch back to Vibe Operator persona.

### Unit Tests
- Verify registry shows all items migrated
- Verify STATUS.md is complete

---

## Success Criteria

1. **Manual Ingest Works:** V can paste any transcript → folder created with correct structure
2. **Fathom Uses Kernel:** Real Fathom webhooks create folders via IntakeEngine
3. **Fireflies Uses Kernel:** Real Fireflies webhooks create folders via IntakeEngine
4. **Date Detection Works:** V Priority Order (semantic → calendar → today) is applied
5. **Deduplication Works:** Duplicate transcripts are caught via SQLite index
6. **Validation Works:** All folders pass `validate_meeting_folder()` (Level Upper)
7. **POLICY.md Exists:** `Personal/Meetings/POLICY.md` documents the standard
8. **No Disruption:** Existing services continue running throughout migration

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking live Fathom/Fireflies during migration | Phase 3 is last; kernel validated with Manual first |
| Date detection fails on edge cases | Socratic clarification in prompt as fallback |
| Import path errors when services import intake package | Test imports before committing changes |
| Duplicate logic has subtle bugs | SQLite index with explicit tests |
| Google Calendar API rate limits during date lookup | CalendarCache with 1hr TTL (Level Upper) |
| Output folders don't match standard | validators.py catches this before completion (Level Upper) |

---

## Trap Doors (Irreversible Decisions)

⚠️ **Trap Door 1: Package Location**
Once we create `N5/services/intake/`, other code will import from it. Changing location later is painful.
**Decision:** `N5/services/intake/` is correct (keeps services together).

⚠️ **Trap Door 2: UnifiedTranscript Schema**
Once adapters convert to this shape, changing it requires updating all adapters.
**Decision:** Keep schema minimal. Use `extra: Dict` for source-specific fields.

⚠️ **Trap Door 3: Date Detection Order**
Changing the priority order later may produce inconsistent folder names.
**Decision:** V's order (semantic → calendar → today) is final.

⚠️ **Trap Door 4: SQLite Dedup Index**
Once we start using SQLite for dedup, we need to backfill existing meetings.
**Decision:** Acceptable. Run one-time backfill script after Phase 1.

---

## Level Upper Review

*Completed 2025-12-23*

### Counterintuitive Suggestions Received:
1. **Output Validation Layer** - Add validators.py to catch adapter bugs regardless of shared code
2. **SQLite Dedup Index** - Use database instead of O(n) filesystem scans
3. **Calendar Lookup Cache** - Prevent rate limits at scale (1hr TTL)
4. **Integration Test** - Real transcript → full validation pass in Phase 2
5. **Required --participants for CLI** - Don't guess for non-interactive use
6. **Prompt-first approach** - Could ship prompt without Python script (considered)

### Incorporated:
- ✅ Output validation layer (`validators.py`)
- ✅ SQLite dedup index (`deduplicator.py` with SQLite)
- ✅ Calendar lookup cache (`calendar_cache.py`)
- ✅ Integration test in Phase 2
- ✅ Required `--participants` flag for manual CLI

### Rejected (with rationale):
- ❌ **"Decentralized validators instead of unified kernel"** - V explicitly requested ONE standard, not N validators
- ❌ **"Prompt-only solution without Python script"** - Need CLI for potential automated batch processing later

---

## Architect Self-Check

- [x] Build workspace initialized with `init_build.py`
- [x] Open questions surfaced at TOP
- [x] Checklist has all phases with ☐ items
- [x] Each phase has: Affected Files, Changes, Unit Tests
- [x] 2-3 alternatives considered (Nemawashi)
- [x] Trap doors identified and flagged
- [x] Success criteria are measurable
- [x] Level Upper review documented
- [x] Plan is executable by AI without clarification

