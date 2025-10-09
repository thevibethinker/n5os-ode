# Meeting & Transcript Ingestion: Complete System Map

**Generated:** 2025-10-09  
**Purpose:** Comprehensive mapping of all N5 OS functionality for ingesting, analyzing, and processing meeting transcripts

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Commands](#commands)
3. [Core Scripts & Workflows](#core-scripts--workflows)
4. [Schemas & Data Structures](#schemas--data-structures)
5. [Storage Locations](#storage-locations)
6. [Processing Pipeline](#processing-pipeline)
7. [Output Artifacts](#output-artifacts)
8. [Integration Points](#integration-points)
9. [Example Meeting Bundles](#example-meeting-bundles)
10. [Related Systems](#related-systems)

---

## System Overview

The N5 OS meeting ingestion system transforms raw transcripts into structured, actionable intelligence through:

- **Multi-source ingestion** (local files, Google Drive)
- **LLM-powered extraction** (speaker-aware parsing, time-anchored content mapping)
- **Structured output generation** (content maps, core maps, operational maps)
- **Downstream automation** (email generation, ticketing, knowledge ingestion)
- **Safety & audit trails** (checksums, manifests, version control)

### Key Principles
- **Time-anchored**: Every actionable item rooted in transcript timestamp
- **Pointer-addressable**: JSON Pointer (RFC 6901) navigation
- **Speaker-aware**: Prevents cross-contamination between speakers
- **Audit-first**: Build evidence maps before generating outputs
- **Voice-faithful**: Apply MasterVoiceSchema for all communications

---

## Commands

### Primary Commands

#### `transcript-ingest`
**Location:** `file 'N5/commands/transcript-ingest.md'`  
**Version:** 1.0.0  
**Purpose:** Ingest and process transcripts from files or Google Drive folders

```bash
# Local file ingestion
N5: transcript-ingest /path/to/transcript.txt

# Google Drive folder ingestion
N5: transcript-ingest folder_id --gdrive
```

**Side Effects:**
- Writes files
- External API calls (TMDB, OpenAI)

**Permissions Required:**
- `external_api`

---

#### `follow-up-email-generator`
**Location:** `file 'N5/commands/follow-up-email-generator.md'`  
**Version:** 10.6  
**Purpose:** Generate send-ready follow-up emails from meeting transcripts

**Key Features:**
- Audit-First Structuring (Missing-Content Map, Resonance Pool, Link Map, SpeakerQuoteMap)
- Socratic Expansion Layer (iterative refinement)
- Delay-Sensitivity (auto-detect elapsed days, prepend apology if > 2 days)
- Voice Fidelity (MasterVoiceSchema ≥ 1.2)
- Map-Archive Integration (distilled insights auto-pushed)

**Inputs:**
- Meeting transcript or notes (required)
- Master Voice Companion File (v ≥ 1.2)
- Essential Links Companion File (latest)
- Optional: Dial overrides

**Output Objects:**
- `subjectLine` (pattern: `Follow-Up Email – <RecipientFirstName> x Careerspan [kw1 • kw2]`)
- `draftEmail`
- `voiceConfigUsed`
- `dialInferenceReport`
- Missing-Content Map
- Link Map
- Resonance Pool
- SpeakerQuoteMap
- DiffCorrectionLog
- revisionHistory
- daysElapsed

**Commands:**
```
/approve maps        # Proceed to drafting
/iterate parsing     # Rerun Steps 1-3 with corrections
/show diff          # Display DiffCorrectionLog
/publish archive    # Send payload to Map-Archive
/draft email        # Bypass confirmation step
/reset              # Restart function
```

---

#### `pr-intel-extractor`
**Location:** `file 'N5/commands/pr-intel-extractor.md'`  
**Purpose:** Extract press-ready intelligence from meeting transcripts

**Input:** Meeting transcript (plain text or timestamped .vtt/.srt)  
**Output:** Press-ready brief

---

#### `conversation-end`
**Location:** `file 'N5/commands/conversation-end.md'`  
**Relevance:** Handles routing of meeting files to appropriate destinations

**Meeting-Specific Routing:**
```
meeting*.md, transcript*.md → Records/Company/meetings/
```

**Example:**
```
✓ meeting_notes.md → Records/Company/meetings/2025-10-08-board-meeting.md
✓ board_meeting_transcript.md → Records/Company/meetings/2025-10-08-board-meeting-transcript.md
✓ board_meeting_summary.md → Meetings/2025-10-08-Board-Meeting-Summary.md
```

---

## Core Scripts & Workflows

### 1. Consolidated Transcript Workflow
**Location:** `file 'N5/scripts/consolidated_transcript_workflow.py'`  
**Size:** 62,500 bytes  
**Purpose:** N5OS-aligned module for parsing transcripts, mapping content, and generating follow-up emails

**Key Classes:**

#### `ContentMapper`
Extracts structured insights from transcripts with speaker-aware parsing.

**Key Methods:**
- `extract_key_elements(transcript: str) -> Dict[str, Any]`
  - Extracts: CTAs, deliverables, decisions, resonance details, speaker quotes
  - Returns: meeting_datetime, participants, duration_seconds, content maps

**Features:**
- Time-anchored extraction (mm:ss format)
- Speaker attribution to prevent cross-contamination
- Verbatim quote preservation
- Link token detection (e.g., "meeting_booking", "careerspan_site")

#### `TranscriptWorkflow`
Main orchestrator with multiple operation modes.

**Modes:**
- `load` - Import transcript only
- `map` - Load + extract content map
- `tickets` - Load + map + generate tickets
- `email` - Load + map + generate follow-up email
- `full` - Complete processing pipeline

**Key Methods:**
- `load_transcript(path)` - Parse and validate transcript
- `map_content(path)` - Extract structured content map
- `generate_tickets(path)` - Create action item tickets
- `generate_email(path, voice_context)` - Generate follow-up email
- `process_transcript(path, voice_context)` - Full pipeline

**Telemetry:**
- Input size tracking
- Processing step logging
- Timing measurements

---

### 2. Consolidated Transcript Workflow v2
**Location:** `file 'N5/scripts/consolidated_transcript_workflow_v2.py'`  
**Size:** 29,418 bytes  
**Purpose:** Enhanced workflow with improved speaker attribution

**Key Improvements:**
- `TranscriptParser` class for speaker-attributed statements
- `_extract_meeting_info()` method for metadata extraction
- Enhanced decision tracking with speaker context
- Warm intro opportunity detection

---

### 3. Google Drive Transcript Workflow
**Location:** `file 'N5/scripts/gdrive_transcript_workflow.py'`  
**Size:** 24,869 bytes  
**Purpose:** Extended N5OS-aligned module for ingesting transcripts from Google Drive

**Key Classes:**

#### `GoogleDriveConnector`
Handles Google Drive integration.

**Methods:**
- `list_transcript_files(folder_id, file_pattern)` - List files in folder
- `download_transcript(file_id, local_path)` - Download transcript file

#### `GoogleDriveTranscriptWorkflow`
Main orchestrator for Google Drive ingestion.

**Methods:**
- `process_folder(folder_id, file_pattern)` - Process all transcripts in folder
- `process_transcript(file_id, file_name, output_base_dir)` - Process single transcript

**Output Directory Structure:**
```
/home/workspace/Meetings/gdrive_{date}_{filename}/
├── content_map.json
├── blurb_ticket_*.json
├── email_draft.md
├── blurbs_summary.md
└── workflow_summary.md
```

---

### 4. Consolidated Workflow (Orchestrator)
**Location:** `file 'N5/scripts/consolidated_workflow.py'`  
**Size:** 11,206 bytes  
**Purpose:** Orchestrates transcript processing, content mapping, and output generation

**Key Methods:**
- `process_transcript(path)` - Step 1: Process transcript into segments
- `run_full_pipeline(path, metadata)` - Execute complete workflow

---

### 5. Blurb Ticket Generator
**Location:** `file 'N5/scripts/blurb_ticket_generator.py'`  
**Purpose:** Generate concise blurbs and tickets from content maps

**Key Classes:**

#### `BlurbTicketGenerator`
LLM-powered content generation.

**Methods:**
- `detect_warm_intro_opportunities(content_map)` - Find connection opportunities
- `generate_blurb(content)` - Create 2-3 sentence summaries
- `generate_follow_up_email(content_map, recipient_context)` - Email generation
- `generate_warm_intro_email(opportunity)` - Warm introduction emails
- `create_ticket(type, content, priority)` - Standardized ticket format
- `process_content_map(content_map, output_dir, dry_run)` - Full processing

**Voice Config:**
```python
VOICE_CONFIG = {
    "blurb_tone": "concise",
    "ticket_formality": "balanced", 
    "cta_style": "soft",
    "warm_intro_tone": "connector-style"
}
```

---

### 6. Supporting Scripts

#### `summarize_segments.py`
**Location:** `file 'N5/scripts/summarize_segments.py'`  
**Purpose:** Chunk transcript and summarize segments using LLM

```bash
python summarize_segments.py <input_transcript.txt> <output_segments.json> [--dry-run]
```

#### `gdrive_integration_example.py`
**Location:** `file 'N5/scripts/gdrive_integration_example.py'`  
**Purpose:** Demonstrates Google Drive integration patterns

#### `n5_conversation_end.py`
**Location:** `file 'N5/scripts/n5_conversation_end.py'`  
**Purpose:** Automated file routing at conversation end

**Meeting Detection Logic:**
```python
# Meeting transcripts
if any(x in name for x in ['transcript', 'meeting']):
    dest = DOCUMENT_INBOX.parent / "Company/meetings" / filepath.name
    return (dest, "move", "Meeting transcript for processing")
```

---

## Schemas & Data Structures

### Content Map Schema (v1.1.0)

**Core Fields:**
- `source_file` - Relative path to canonical transcript
- `meeting_datetime` - ISO8601 UTC timestamp
- `participants` - Array of participant names
- `duration_seconds` - Integer
- `deliverables` - Array of promised outputs
- `ctas` - Array of Call-to-Actions with owner, time, text, verbatim
- `decisions` - Array with time/range, speaker, decision, verbatim
- `resonance_details` - Array of high-impact moments
- `speaker_quotes` - Array of notable verbatim quotes
- `warm_intro_opportunities` - Array of connection opportunities
- `topics` - Array with id, title, time_range, evidence
- `risks` - Array of identified risks
- `opportunities` - Array of business opportunities
- `key_facts` - Array of factual statements

**Metadata Fields:**
- `schema` - "n5os.content_map"
- `schema_version` - "1.1.0"
- `generated_at` - ISO8601 timestamp
- `processing.method` - "LLM-guided (time-anchored)"
- `processing.anchoring` - "timecodes + verbatim quotes"

**Index Structures:**
- `cta_index` - Pointers to all CTAs with owner, time, summary
- `decision_index` - Pointers to all decisions
- `topic_index` - Pointers to all topics
- `quote_index` - Pointers to all quotes
- `risk_index` - Pointers to all risks
- `opportunity_index` - Pointers to all opportunities
- `fact_index` - Pointers to all facts

**Speaker Index:**
Per-speaker pointers to their CTAs, resonance moments, quotes

**Timeline:**
Chronologically sorted CTAs/decisions with JSON Pointers

**Field Index:**
Programmatic field → JSON Pointer map for navigation

**Table of Contents (TOC):**
Human-readable navigation → JSON Pointers

---

### Core Map Schema

Split from content map for focused strategic information.

**Key Fields:**
- `source_file` - Reference to transcript
- `meeting_datetime` - ISO8601 UTC
- `participants` - Array with roles
- `attachments` - Array of source files with checksums
- `metadata` - Schema info, processing method
- `roles_policy` - Per-participant role assignments
- `lessons_learned` - Process improvements
- `summary` - High-level meeting summary

---

### Operational Map Schema

Tactical action items and follow-ups.

**Key Fields:**
- `action_items` - Concrete next steps with owners/deadlines
- `commitments` - Promises made during meeting
- `decisions` - Tactical decisions with context
- `follow_up_items` - Post-meeting tasks

---

### Segments Schema

Time-bounded chunks of the transcript with pointers back to content map.

**Structure:**
```json
{
  "schema": "n5os.segments",
  "schema_version": "1.0",
  "source_content_map": "content_map.json",
  "source_transcript": "attachments/transcript.txt",
  "segments": [
    {
      "id": "seg_00",
      "time_range": ["00:00", "05:30"],
      "seconds_range": [0, 330],
      "speakers": ["Logan", "Vrijen"],
      "excerpts": {
        "head": "First 50 chars...",
        "tail": "Last 50 chars..."
      },
      "pointers": {
        "ctas": [{"pointer": "#/ctas/0", "time": "02:15", "owner": "Logan"}],
        "decisions": [{"pointer": "#/decisions/0", "time": "04:30"}],
        "topics": [{"pointer": "#/topics/0", "title": "ICP Discussion"}]
      },
      "summary": "Segment overview...",
      "key_points": ["Point 1", "Point 2"],
      "notable_quotes": ["Quote 1"]
    }
  ]
}
```

---

### Manifest Schema

Bundle-level metadata.

**Structure:**
```json
{
  "kind": "external_meeting_bundle",
  "created_at": "2025-09-20T22:37:35Z",
  "meeting_datetime": "2025-09-19T19:20:31Z",
  "participants": ["Name 1", "Name 2"],
  "paths": {
    "root": "Meetings/External/2025-09-19_...",
    "content_map": "content_map.json",
    "attachments": {
      "transcript": "attachments/transcript.txt",
      "source_url": "attachments/source.url",
      "checksums": "attachments/checksums.sha256"
    }
  },
  "transcript": {
    "sha256": "...",
    "bytes": 41404,
    "lines": 1054,
    "words": 7581
  },
  "notes": "Bundle description"
}
```

---

### Ticket Schema

**Location:** `file 'projects/ticketing_system/schema.json'`

**Structure:**
```json
{
  "ticket_id": "abc123",
  "type": "follow_up|warm_intro|deliverable",
  "priority": "high|medium|low",
  "created": "2025-10-09T...",
  "status": "pending_approval|approved|completed",
  "meeting_metadata": {
    "participants": [...],
    "roles": {...},
    "deliverables": [...]
  },
  "content": {...},
  "voice_config": {...}
}
```

---

## Storage Locations

### Primary Locations

#### Records (Staging Layer)
**Path:** `/home/workspace/Records/Company/meetings/`  
**Purpose:** Raw transcripts awaiting processing  
**Retention:** Process within 48 hours, archive externally after 30 days  
**Naming:** `YYYY-MM-DD-topic-description.txt`

**Example:**
```
Records/Company/meetings/2025-10-08-board-meeting-transcript.md
```

---

#### Careerspan Meetings (Processed Company)
**Path:** `/home/workspace/Careerspan/Meetings/`  
**Purpose:** Processed company meeting notes and bundles  
**Structure:**
```
Careerspan/Meetings/
├── External/
│   └── YYYY-MM-DD_participant-names/
│       ├── manifest.json
│       ├── content_map.json
│       ├── core_map.json
│       ├── operational_map.json
│       ├── segments.json
│       ├── schema_guide.md
│       ├── README.md
│       ├── attachments/
│       │   ├── transcript.txt
│       │   ├── source.url
│       │   └── checksums.sha256
│       ├── outputs/
│       │   ├── follow_up_email_*.md
│       │   ├── topic_blurbs.md
│       │   ├── calendar_followups_llm.json
│       │   └── warm_intro_tickets_llm.json
│       ├── scripts/
│       │   └── compose_followup_email.py
│       ├── dryruns/
│       └── logs/
└── gdrive_YYYY-MM-DD_filename/
    ├── content_map.json
    ├── email_draft.md
    ├── blurb_ticket_*.json
    ├── blurbs_summary.md
    └── workflow_summary.md
```

---

#### Personal Meetings
**Path:** `/home/workspace/Personal/Meetings/`  
**Purpose:** Personal meeting notes  

---

#### Document Inbox
**Path:** `/home/workspace/Document Inbox/Company/meetings/`  
**Purpose:** Temporary holding area for incoming transcripts  
**Current Files:**
- sample_transcript_realistic.txt
- sample_transcript.txt
- sample_transcript_with_warm_intro.txt
- Carly x Careerspan-transcript-2025-09-23T21-04-28.138Z.docx
- Rajesh_Meeting_Summary.md
- transcript.txt

---

### Archive Locations

**Path:** `/home/workspace/Documents/Archive/`  
**Purpose:** Historical transcripts and obsolete data  

---

## Processing Pipeline

### Full Pipeline Flow

```
┌─────────────────────┐
│  INGESTION SOURCES  │
└──────────┬──────────┘
           │
           ├── Local File Upload
           ├── Google Drive Folder
           └── Direct Paste
           │
           ▼
┌─────────────────────┐
│   STAGING LAYER     │
│  Records/Company/   │
│     meetings/       │
└──────────┬──────────┘
           │
           │ [Trigger: transcript-ingest command]
           │
           ▼
┌─────────────────────┐
│  PARSE & VALIDATE   │
│                     │
│ • Speaker detection │
│ • Time extraction   │
│ • Metadata harvest  │
│ • SHA256 checksum   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  LLM EXTRACTION     │
│                     │
│ • CTAs + owners     │
│ • Decisions         │
│ • Deliverables      │
│ • Resonance details │
│ • Speaker quotes    │
│ • Topics + evidence │
│ • Warm intros       │
│ • Risks/opps/facts  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  STRUCTURED MAPS    │
│                     │
│ • content_map.json  │
│ • core_map.json     │
│ • operational_map   │
│ • segments.json     │
└──────────┬──────────┘
           │
           ├────────────────────┐
           │                    │
           ▼                    ▼
┌─────────────────┐   ┌─────────────────┐
│  BUNDLE ASSEMBLY│   │  ARTIFACT GEN   │
│                 │   │                 │
│ • Create folder │   │ • Follow-up     │
│ • Generate      │   │   emails        │
│   manifest      │   │ • Blurb tickets │
│ • Add checksums │   │ • Calendar      │
│ • Schema guide  │   │   follow-ups    │
│ • README        │   │ • Warm intros   │
└────────┬────────┘   └────────┬────────┘
         │                     │
         └──────────┬──────────┘
                    │
                    ▼
┌─────────────────────────────┐
│   DOWNSTREAM INTEGRATION    │
│                             │
│ • Knowledge base update     │
│ • Lists (must-contact, etc) │
│ • Email queue               │
│ • Calendar scheduling       │
│ • Ticketing system          │
│ • Git commit                │
└─────────────────────────────┘
```

---

### Processing Steps Detail

#### Step 1: Transcript Parsing
**Script:** ContentMapper.extract_key_elements()  
**Input:** Raw transcript text  
**Output:** Structured statements with speaker attribution

**Operations:**
1. Split by newlines
2. Detect speaker patterns (e.g., "Alice:", "John [12:34]:")
3. Extract timestamps (mm:ss format)
4. Build statement objects: `{speaker, time, content}`
5. Filter out metadata/header lines

---

#### Step 2: Meeting Metadata Extraction
**Script:** ContentMapper._extract_datetime()  
**Input:** Parsed statements  
**Output:** meeting_datetime, participants, duration

**Operations:**
1. LLM-guided date/time extraction (no regex)
2. Participant list compilation
3. Duration calculation from first/last timestamps
4. Metadata validation

---

#### Step 3: Content Mapping
**Script:** ContentMapper.extract_key_elements()  
**Input:** Parsed statements, meeting metadata  
**Output:** Comprehensive content map

**Key Extractions:**

**CTAs (Call-to-Actions):**
- Pattern: "I will...", "Can you...", "Let's..."
- Fields: owner, time, text, verbatim
- Example: `{"owner": "Logan", "time": "18:56", "text": "Send self-determination theory paper to group"}`

**Decisions:**
- Pattern: "We decided...", "Agreed that...", "Going with..."
- Fields: time/range, speaker, decision, verbatim
- Example: `{"time": "22:45", "speaker": "Vrijen", "decision": "ICP focus on product leaders, not founders"}`

**Deliverables:**
- Pattern: Concrete outputs promised
- Fields: description, owner, deadline (if mentioned)
- Example: `{"deliverable": "Partnership agreements", "owner": "Alice"}`

**Resonance Details:**
- Pattern: High-impact moments, insights, breakthroughs
- Fields: speaker, time, text
- Example: `{"speaker": "Logan", "time": "15:30", "text": "International experience as base athleticism for PMs"}`

**Speaker Quotes:**
- Pattern: Memorable verbatim statements
- Fields: speaker, quote, time
- Example: `"It's like meeting your spouse - life-changing matchmaking"`

**Topics:**
- Pattern: Discussion themes with evidence
- Fields: id, title, time_range, evidence array
- Example: `{"id": "topic_01", "title": "ICP Definition", "time_range": ["20:00", "25:00"], "evidence": [...]}`

**Warm Intro Opportunities:**
- Pattern: Mentioned connections, shared interests
- Fields: person_a, person_b, rationale, priority, context
- Example: `{"person_a": "Logan", "person_b": "Shujaat", "rationale": "Both interested in PM career development"}`

---

#### Step 4: Link Token Detection
**Script:** ContentMapper._detect_link_tokens()  
**Input:** Content map  
**Output:** Array of detected link tokens

**Common Tokens:**
- meeting_booking
- careerspan_site
- essential_links
- calendar_link

**Mapping to Essential Links:**
Uses `file 'N5/knowledge/context/Companion [05] - Essential Links'` to resolve tokens to actual URLs.

---

#### Step 5: Map Splitting
**Purpose:** Separate strategic (core) from tactical (operational)

**Core Map Contains:**
- Meeting overview
- Participants + roles
- Key decisions (strategic)
- Lessons learned
- Source attachments with checksums

**Operational Map Contains:**
- Action items with owners/deadlines
- Commitments
- Tactical decisions
- Follow-up items

---

#### Step 6: Segment Generation
**Script:** Custom segmentation logic  
**Input:** Transcript, content map  
**Output:** segments.json with time-bounded chunks

**Operations:**
1. Chunk transcript by time intervals (e.g., 5-minute segments)
2. For each segment, find overlapping CTAs/decisions/topics from content map
3. Create JSON Pointers to content map elements
4. Generate segment summary and key points
5. Extract notable quotes from segment

---

#### Step 7: Bundle Assembly
**Script:** External meeting bundle generator  
**Input:** All maps, transcript, metadata  
**Output:** Complete meeting bundle folder

**Creates:**
- `manifest.json` - Bundle metadata
- `content_map.json` - Full content map
- `core_map.json` - Strategic information
- `operational_map.json` - Tactical items
- `segments.json` - Time-bounded chunks
- `schema_guide.md` - Consumer documentation
- `README.md` - Human overview
- `attachments/` folder:
  - `transcript.txt` - Canonical transcript
  - `source.url` - Original source link
  - `checksums.sha256` - File integrity

---

#### Step 8: Artifact Generation

**Follow-Up Emails:**
- **Script:** FollowUpEmailGenerator
- **Inputs:** content_map, recipient context, voice config
- **Process:**
  1. Extract meeting date/time
  2. Calculate days elapsed
  3. Build resonance pool (top 2-3 moments)
  4. Extract CTAs for recipient
  5. Select 1 speaker quote
  6. Apply MasterVoiceSchema
  7. Generate subject line (pattern: "Follow-Up Email – [Recipient] x Careerspan [kw1 • kw2]")
  8. Draft email (greeting → optional apology → resonance → recap bullets → next steps → sign-off)
- **Output:** `outputs/follow_up_email_[recipient].md`

**Blurb Tickets:**
- **Script:** BlurbTicketGenerator
- **Inputs:** content_map, topic
- **Process:**
  1. Extract topic with evidence
  2. LLM generate 2-3 sentence blurb
  3. Create ticket with metadata
- **Output:** `blurb_ticket_[type]_[id].json`

**Calendar Follow-Ups:**
- **Script:** Calendar follow-up generator
- **Inputs:** content_map CTAs
- **Process:**
  1. For each CTA with owner
  2. Generate scheduling prompt
  3. Suggest 2-3 meeting windows
  4. Include brief agenda
- **Output:** `outputs/calendar_followups_llm.json`

**Warm Intro Emails:**
- **Script:** BlurbTicketGenerator.generate_warm_intro_email()
- **Inputs:** warm_intro_opportunity
- **Process:**
  1. For each party (person_a, person_b)
  2. Brief intro of both parties
  3. Clear connection rationale
  4. Soft CTA encouraging connection
  5. Apply warm_intro_tone from voice config
- **Output:** `outputs/warm_intro_[person_a]_[person_b].md`

---

## Output Artifacts

### Meeting Bundle (Complete)

**Structure:**
```
Meetings/External/2025-09-19_logan-currie_shujaat-ahmad_vrijen-attawar/
├── manifest.json                    # Bundle metadata, checksums, stats
├── content_map.json                 # Full content map (25KB+)
├── content_map.before_split.json   # Pre-split version (archive)
├── core_map.json                   # Strategic information (16KB)
├── operational_map.json            # Tactical items (19KB)
├── segments.json                   # Time-bounded chunks (9KB)
├── schema_guide.md                 # Consumer documentation
├── README.md                       # Human overview
│
├── attachments/
│   ├── transcript.txt              # Canonical transcript (41KB, 1054 lines)
│   ├── source.url                  # Google Doc link
│   └── checksums.sha256           # File integrity hashes
│
├── outputs/
│   ├── follow_up_email_logan.md
│   ├── follow_up_email_shujaat.md
│   ├── topic_blurbs.md
│   ├── calendar_followups_llm.json
│   └── warm_intro_tickets_llm.json
│
├── scripts/
│   └── compose_followup_email.py  # Custom email generator
│
├── dryruns/                        # Test outputs
│
└── logs/                           # Processing logs
```

---

### Individual Artifact Examples

#### Content Map (content_map.json)
```json
{
  "source_file": "Meetings/External/.../attachments/transcript.txt",
  "meeting_datetime": "2025-09-19T19:20:31Z",
  "participants": ["Logan Currie", "Shujaat Ahmad", "Vrijen Attawar"],
  "duration_seconds": 2322,
  "ctas": [
    {
      "owner": "Logan Currie",
      "time": "18:56",
      "text": "Send self-determination theory paper to the group",
      "verbatim": "I'll send you guys that paper..."
    }
  ],
  "decisions": [
    {
      "time": "22:45",
      "speaker": "Vrijen",
      "decision": "Focus ICP on product leaders, not founders",
      "verbatim": "We're going after product leaders..."
    }
  ],
  "resonance_details": [
    {
      "speaker": "Logan",
      "time": "15:30",
      "text": "International experience as 'base athleticism' for PMs",
      "verbatim": "It's like base athleticism for product managers..."
    }
  ],
  "topics": [
    {
      "id": "topic_01",
      "title": "ICP Definition & Product-Market Fit",
      "time_range": ["20:00", "25:00"],
      "evidence": [
        {
          "time": "22:45",
          "speaker": "Vrijen",
          "quote": "We're targeting product leaders who feel stuck..."
        }
      ]
    }
  ],
  "warm_intro_opportunities": [
    {
      "person_a": "Logan Currie",
      "person_b": "Shujaat Ahmad",
      "connection_rationale": "Both deeply interested in PM development and international experience",
      "priority": "high",
      "intro_context": "Shared perspective on career development frameworks"
    }
  ],
  "indices": {
    "cta_index": [
      {"pointer": "#/ctas/0", "owner": "Logan", "time": "18:56", "summary": "Send paper"}
    ],
    "topic_index": [
      {"pointer": "#/topics/0", "title": "ICP Definition", "time_range": ["20:00", "25:00"]}
    ]
  },
  "timeline": [
    {"time": "18:56", "type": "cta", "pointer": "#/ctas/0"},
    {"time": "22:45", "type": "decision", "pointer": "#/decisions/0"}
  ]
}
```

#### Follow-Up Email (outputs/follow_up_email_logan.md)
```markdown
Subject: Follow-Up Email – Logan x Careerspan [PM Development • Involvement Tiers]

Hi Logan,

Thanks for the conversation today. I really appreciated your insight about international experience as "base athleticism" for PMs—it's a compelling lens for thinking about career development.

**Quick recap:**
• You'll send the self-determination theory paper to the group by end of week
• We discussed involvement tier options for your engagement with Careerspan
• Agreed to plan a follow-up conversation to explore collaboration depth

**Next steps:**
Could you share 2-3 windows next week for a 30-minute call to discuss involvement options? I'll send over the tier breakdown before then.

Looking forward to continuing the conversation.

Best,
Vrijen
```

#### Blurb Ticket (blurb_ticket_cta_1.json)
```json
{
  "ticket_id": "a3f8b2c1",
  "type": "cta",
  "priority": "medium",
  "created": "2025-09-20T23:00:00Z",
  "status": "pending_approval",
  "content": {
    "cta": {
      "owner": "Logan Currie",
      "time": "18:56",
      "text": "Send self-determination theory paper to the group",
      "verbatim": "I'll send you guys that paper on self-determination theory..."
    },
    "blurb": "Logan will share academic paper on self-determination theory with the group to inform framework discussions around PM career development.",
    "context": "Discussion about theoretical foundations for Careerspan's approach",
    "related_topics": ["#/topics/0"]
  },
  "voice_config": {
    "blurb_tone": "concise",
    "ticket_formality": "balanced"
  }
}
```

---

## Integration Points

### 1. Google Drive Integration

**Tool:** `use_app_google_drive`  
**Workflow:** `file 'N5/scripts/gdrive_transcript_workflow.py'`

**Process:**
1. **List files in folder:**
   ```python
   tool_name = "google_drive-list-files"
   configured_props = {
       "folderId": "1A2B3C4D5E6F7G8H9I0J",
       "filterText": "transcript"  # Optional
   }
   ```

2. **Download transcript:**
   ```python
   tool_name = "google_drive-download-file"
   configured_props = {
       "fileId": "abc123...",
       "filePath": "/tmp/meeting_transcript.txt",
       "mimeType": "text/plain"
   }
   ```

3. **Process transcript:**
   ```bash
   python N5/scripts/gdrive_transcript_workflow.py <folder_id>
   ```

**Outputs:**
- Downloaded to `/tmp/`
- Processed to `/home/workspace/Meetings/gdrive_{date}_{filename}/`
- Automatic cleanup after processing

---

### 2. Knowledge Base Integration

**Target:** `file 'Knowledge/'` directory  
**Format:** JSONL files

**Ingestion Flow:**
```
content_map.json
    ↓
[Extract key_facts + decisions]
    ↓
Knowledge/facts.jsonl (append)
```

**Example Entry:**
```json
{
  "fact": "Careerspan ICP: Product leaders feeling stuck in their careers",
  "source": "Meeting with Logan Currie",
  "date": "2025-09-19",
  "confidence": "high",
  "tags": ["icp", "target_persona"],
  "evidence_pointer": "Meetings/External/2025-09-19.../content_map.json#/decisions/0"
}
```

---

### 3. Lists Integration

**Tool:** `lists-add` command  
**Target:** `file 'N5/lists/'` directory

**Integration Points:**

**must-contact.jsonl:**
- Source: CTAs with owner = external party
- Trigger: CTA with time commitment
- Example: `{"person": "Logan Currie", "reason": "Follow up on involvement tiers", "deadline": "2025-09-26", "source": "Meeting 2025-09-19"}`

**action-items.jsonl:**
- Source: CTAs with owner = Vrijen
- Trigger: Deliverable with deadline
- Example: `{"task": "Send involvement tier options to Logan", "deadline": "2025-09-25", "priority": "high"}`

**warm-intros.jsonl:**
- Source: warm_intro_opportunities
- Trigger: High priority intro detected
- Example: `{"person_a": "Logan", "person_b": "Shujaat", "context": "PM development interest", "status": "pending"}`

---

### 4. Email Queue Integration

**Tool:** `use_app_gmail`  
**Workflow:** Follow-up email generator → Gmail draft

**Process:**
1. Generate email via follow-up-email-generator
2. Review and approve draft
3. Queue to Gmail:
   ```python
   tool_name = "gmail-create-draft"
   configured_props = {
       "to": "logan@example.com",
       "subject": "Follow-Up Email – Logan x Careerspan [PM Development]",
       "body": "<email_content>"
   }
   ```

---

### 5. Calendar Integration

**Tool:** `use_app_google_calendar`  
**Workflow:** Calendar follow-up generator → Event creation

**Process:**
1. Extract CTAs requiring scheduling
2. Generate calendar prompts
3. Create events:
   ```python
   tool_name = "google_calendar-quick-add-event"
   configured_props = {
       "calendarId": "primary",
       "text": "30min call with Logan re: Careerspan involvement options on 2025-09-26 at 2pm"
   }
   ```

---

### 6. Ticketing System Integration

**System:** `file 'projects/ticketing_system/'`  
**Workflow:** Meeting data → Ticket generation

**Process:**
1. Read content_map.json
2. Generate ticket via pipeline:
   ```python
   from pipeline import generate_ticket
   
   meeting_data = {
       "content_map": "Discussion about...",
       "core_map": "Key strategic decisions...",
       "operations_map": "Action items...",
       "metadata": {
           "participants": ["Alice", "John"],
           "deliverables": [...]
       }
   }
   
   ticket = generate_ticket(meeting_data)
   ```

3. Ticket types determined by LLM:
   - `follow_up` - Requires email/call
   - `warm_intro` - Connection opportunity
   - `deliverable` - Concrete output needed
   - `research` - Information gathering
   - `decision` - Approval/choice required

**Ticket Enhancement:**
- Knowledge base lookup for context
- Related participant history
- Priority scoring
- Output type suggestion (email, report, call)

---

### 7. Git Integration

**Workflow:** Automatic version control for meeting bundles

**Process:**
```bash
cd /home/workspace
git add Careerspan/Meetings/External/2025-09-19_*/
git commit -m "Add meeting bundle: Logan Currie x Shujaat Ahmad x Vrijen (2025-09-19)"
```

**Tracked Files:**
- content_map.json
- core_map.json
- operational_map.json
- segments.json
- manifest.json
- schema_guide.md
- attachments/transcript.txt
- outputs/*.md

**Ignored:**
- logs/
- dryruns/
- .temp files

---

## Example Meeting Bundles

### Example 1: External Stakeholder Meeting
**Path:** `file 'Careerspan/Meetings/External/2025-09-19_logan-currie_shujaat-ahmad_vrijen-attawar/'`

**Participants:**
- Logan Currie (Product leader, potential advisor)
- Shujaat Ahmad (PM, potential collaborator)
- Vrijen Attawar (Careerspan founder)

**Key Artifacts:**
- `manifest.json` - 763 bytes
- `content_map.json` - 25,753 bytes (before split)
- `core_map.json` - 16,165 bytes
- `operational_map.json` - 19,430 bytes
- `segments.json` - 9,422 bytes
- `attachments/transcript.txt` - 41,404 bytes, 1,054 lines

**Key Extractions:**
- 6 CTAs with owners/times
- 4 major decisions
- 12 topics with evidence
- 3 warm intro opportunities
- 8 resonance details
- 15 speaker quotes

**Outputs Generated:**
- Follow-up emails for Logan and Shujaat
- Topic blurbs (12 items)
- Calendar follow-up prompts (6 items)
- Warm intro tickets (3 items)

---

### Example 2: Client Introduction Meeting
**Path:** `file 'Careerspan/Meetings/External/2025-09-20_northwell_health_intro/'`

**Participants:**
- Brian (Northwell Health representative)
- Kamina Singh (Connector)
- Vrijen Attawar (Careerspan founder)

**Key Artifacts:**
- `manifest.json`
- `core_map.json`
- `operational_map.json`
- `attachments/transcript.txt`

**Key Extractions:**
- Meeting type: external_intro
- Primary CTA: "Stick to the 26th meeting date"
- Deliverable: Partnership discussion
- Follow-up: Schedule detailed meeting by Sept 27

**Outputs Generated:**
- Follow-up email to Brian
- Internal notes on partnership opportunity
- Calendar scheduling prompt

---

### Example 3: Google Drive Processed Meeting
**Path:** `file 'Careerspan/Meetings/gdrive_2025-09-15_meeting_transcript_2025-09-15_txt/'`

**Key Artifacts:**
- `content_map.json`
- `email_draft.md`
- `blurb_ticket_cta_1.json`
- `blurb_ticket_deliverable_1.json`
- `workflow_summary.md`

**Processing Notes:**
- Ingested from Google Drive folder
- Automatic delay detection: "I apologize for the delay in following up—it's been 5 days since our meeting."
- Generated 2 blurb tickets
- Draft email ready for review

---

## Related Systems

### 1. Ticketing System
**Location:** `file 'projects/ticketing_system/'`  
**Purpose:** Convert meeting data into actionable tickets

**Key Files:**
- `schema.json` - Ticket schema
- `pipeline.py` - Core generation logic
- `cli.py` - Command-line interface
- `api.py` - Flask endpoint
- `automation.py` - Directory watcher
- `prompts.py` - LLM prompt templates

**Integration:**
```python
# Generate ticket from meeting
python projects/ticketing_system/cli.py meeting.json ticket.json

# Auto-process meetings in folder
nohup python projects/ticketing_system/automation.py &
```

---

### 2. Function Library
**Location:** `file 'Careerspan/Product/Functions/'`

**Relevant Functions:**
- `Function [01] - PR Intel Extractor v1.1` - Meeting transcript → press brief
- `Function [02] - Follow-Up Email Generator v10.6` - Meeting → email

**Integration:**
Shared voice configuration and processing logic with N5 transcript workflows.

---

### 3. Knowledge Base
**Location:** `file 'Knowledge/'`

**Relevant Directories:**
- `Knowledge/context/` - Essential links, companion files
- `Knowledge/stable/sources.md` - Source references
- `Knowledge/architectural/` - System principles
- `Knowledge/logs/Email/` - Email processing logs

**Integration:**
Meeting facts → `Knowledge/facts.jsonl`

---

### 4. Master Voice Engine
**Location:** Referenced in voice config files

**Schema:** MasterVoiceSchema ≥ 1.2

**Voice Parameters:**
- Warmth: 0.80-0.85
- Confidence: 0.72-0.80
- Humility: 0.55-0.65
- Formality: Balanced baseline (shifts formal for external/policy)
- CTA Rigor: Balanced to Direct (increases with stakes/time pressure)

**Integration:**
Applied to all generated emails, blurbs, and communications.

---

## Workflows Summary

### Workflow 1: Local Transcript Processing
```bash
# Upload transcript to staging
cp transcript.txt Records/Company/meetings/2025-10-09-client-meeting.txt

# Process transcript
N5: transcript-ingest Records/Company/meetings/2025-10-09-client-meeting.txt

# Outputs created in:
# - Careerspan/Meetings/2025-10-09-client-meeting/
```

---

### Workflow 2: Google Drive Batch Processing
```bash
# Trigger Google Drive workflow
python N5/scripts/gdrive_transcript_workflow.py <folder_id>

# Automatically:
# 1. Lists all transcript files in folder
# 2. Downloads to /tmp/
# 3. Processes each transcript
# 4. Creates meeting bundles
# 5. Generates artifacts
# 6. Cleans up temp files
```

---

### Workflow 3: Follow-Up Email Generation
```bash
# Option A: Via command
N5: follow-up-email-generator --transcript Records/Company/meetings/2025-10-09-*.txt

# Option B: Via Python script
python N5/scripts/consolidated_transcript_workflow.py path/to/transcript.txt --mode email

# Outputs:
# - Draft email in outputs/
# - Content maps
# - Voice config used
# - Resonance pool
# - CTA extraction
```

---

### Workflow 4: Ticket Generation from Meeting
```bash
# Process meeting bundle into tickets
python projects/ticketing_system/cli.py \
    Careerspan/Meetings/External/2025-09-19_*/content_map.json \
    ticket_output.json

# Ticket types generated:
# - Follow-up emails (CTA-based)
# - Warm introductions (opportunity-based)
# - Deliverables (promised outputs)
```

---

### Workflow 5: End-of-Conversation Routing
```bash
# At conversation end
N5: conversation-end

# Automatically routes:
# - transcript*.md → Records/Company/meetings/
# - meeting*.md → Records/Company/meetings/
# - Processed bundles → Careerspan/Meetings/
```

---

## Command Reference Quick Guide

```bash
# Core Commands
N5: transcript-ingest <path_or_folder_id> [--gdrive]
N5: follow-up-email-generator --transcript <path>
N5: pr-intel-extractor --transcript <path>
N5: conversation-end

# Script Execution
python N5/scripts/consolidated_transcript_workflow.py <transcript> [--mode load|map|tickets|email|full]
python N5/scripts/gdrive_transcript_workflow.py <folder_id>
python N5/scripts/blurb_ticket_generator.py <content_map.json>
python N5/scripts/summarize_segments.py <transcript> <output.json>

# Ticketing
python projects/ticketing_system/cli.py <meeting.json> <ticket.json>
python projects/ticketing_system/automation.py  # Watch mode

# Supporting Commands
N5: lists-add --item "Contact Logan" --list must-contact --priority high
N5: knowledge-add --fact "..." --source "Meeting 2025-10-09"
N5: git-check  # Verify meeting bundle files tracked
```

---

## File Naming Conventions

### Transcripts (Raw)
**Pattern:** `YYYY-MM-DD-topic-description.txt`  
**Location:** `Records/Company/meetings/`  
**Examples:**
- `2025-10-09-board-meeting-transcript.txt`
- `2025-10-09-client-intro-northwell.txt`

### Meeting Bundles
**Pattern:** `YYYY-MM-DD_participant-names/`  
**Location:** `Careerspan/Meetings/External/`  
**Examples:**
- `2025-09-19_logan-currie_shujaat-ahmad_vrijen-attawar/`
- `2025-09-20_northwell_health_intro/`

### Google Drive Imports
**Pattern:** `gdrive_YYYY-MM-DD_original-filename/`  
**Location:** `Careerspan/Meetings/`  
**Examples:**
- `gdrive_2025-09-15_meeting_transcript_2025-09-15_txt/`

---

## Safety & Quality Controls

### 1. File Protection
- **Checksums:** SHA256 for all transcripts
- **Manifests:** Bundle-level integrity tracking
- **Version Control:** Git tracking for all processed meetings

### 2. Speaker Attribution
- **Parser:** Dedicated speaker detection logic
- **Validation:** Prevent cross-contamination between speakers
- **Audit Trail:** Verbatim quotes preserved with speaker tags

### 3. Time Anchoring
- **Format:** mm:ss consistently
- **Validation:** All CTAs/decisions/topics have timestamps
- **Evidence:** Every claim points to specific time in transcript

### 4. LLM Extraction Quality
- **Method:** LLM-guided (not regex/keyword)
- **Validation:** Manual spot-checks against transcript
- **Logging:** Processing steps tracked
- **Fallback:** Graceful degradation if LLM unavailable

### 5. Output Review
- **Socratic Expansion:** User approval before final outputs
- **Diff Tracking:** Version changes logged
- **Dry Run Mode:** Test outputs before committing

---

## Troubleshooting

### Common Issues

#### Issue: Transcript not detected
**Symptoms:** File in staging but not processed  
**Solution:**
1. Check filename matches pattern: `*transcript*.txt` or `*meeting*.txt`
2. Verify file location: `Records/Company/meetings/`
3. Run manually: `N5: transcript-ingest <path>`

#### Issue: Speaker attribution errors
**Symptoms:** Mixed quotes, wrong owners  
**Solution:**
1. Check transcript format - ensure clear speaker labels
2. Use pattern: `SpeakerName:` or `SpeakerName [timestamp]:`
3. Verify no nested conversations in transcript

#### Issue: Google Drive download fails
**Symptoms:** Empty files, missing transcripts  
**Solution:**
1. Verify Google Drive app connected: `list_app_tools(app_slug="google_drive")`
2. Check file permissions in Drive
3. Confirm file ID is correct
4. Try manual download to test access

#### Issue: No CTAs extracted
**Symptoms:** Empty CTA list in content map  
**Solution:**
1. Check transcript contains actionable language
2. Verify LLM API key present: `echo $OPENAI_API_KEY`
3. Review logs: `tail -f Knowledge/logs/Email/*.log`
4. Try v2 workflow: `consolidated_transcript_workflow_v2.py`

#### Issue: Email generation missing context
**Symptoms:** Generic email, no specific details  
**Solution:**
1. Verify content_map.json has resonance_details
2. Check Link Map populated from Essential Links
3. Ensure voice_config loaded
4. Use `/iterate parsing` command to refine extraction

---

## Future Enhancements

### Planned Improvements
- [ ] Automated topic clustering across multiple meetings
- [ ] Sentiment analysis for decision confidence scoring
- [ ] Multi-language transcript support
- [ ] Real-time processing webhook for instant post-meeting artifacts
- [ ] Meeting series linking (track topics across recurring meetings)
- [ ] Auto-detection of unresolved CTAs from previous meetings
- [ ] Integration with calendar for auto-scheduling follow-ups
- [ ] Voice-to-text pipeline for audio recordings

### Under Consideration
- [ ] Meeting effectiveness scoring
- [ ] Participant engagement metrics
- [ ] Custom extraction rules per meeting type
- [ ] Integration with project management tools
- [ ] Meeting template library

---

## References

### Key Files Documented
- `file 'N5/commands/transcript-ingest.md'`
- `file 'N5/commands/follow-up-email-generator.md'`
- `file 'N5/commands/pr-intel-extractor.md'`
- `file 'N5/scripts/consolidated_transcript_workflow.py'`
- `file 'N5/scripts/gdrive_transcript_workflow.py'`
- `file 'N5/scripts/blurb_ticket_generator.py'`
- `file 'Careerspan/Meetings/External/2025-09-19_logan-currie_shujaat-ahmad_vrijen-attawar/schema_guide.md'`
- `file 'projects/ticketing_system/README.md'`

### Related Documentation
- `file 'Documents/N5.md'` - N5 OS overview
- `file 'N5/prefs/prefs.md'` - System preferences
- `file 'Records/README.md'` - Staging layer guide
- `file 'Documents/System/gdrive_transcript_ingestion_guide.md'` - Google Drive integration

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-09  
**Maintained By:** N5 OS
