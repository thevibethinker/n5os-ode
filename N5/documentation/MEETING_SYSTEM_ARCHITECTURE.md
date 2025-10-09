# Meeting Processing System — Complete Architecture

**Version:** 2.0  
**Last Updated:** 2025-10-09  
**Status:** Active Development

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Commands & Entry Points](#commands--entry-points)
3. [Core Scripts & Orchestration](#core-scripts--orchestration)
4. [Block Generators](#block-generators)
5. [Schemas & Data Models](#schemas--data-models)
6. [Processing Workflows](#processing-workflows)
7. [Integration Points](#integration-points)
8. [Output Structure](#output-structure)
9. [Examples](#examples)

---

## System Overview

The N5 Meeting Processing System transforms raw meeting transcripts into **actionable intelligence** through a modular, block-based architecture. It automatically generates follow-up emails, extracts action items, identifies risks/opportunities, and integrates with your knowledge management system.

### Key Capabilities

- **Multi-source ingestion**: Google Drive, local files, email attachments
- **Context-aware processing**: Enriches analysis with meeting history and email threads
- **Adaptive output**: Generates different blocks based on meeting type (sales, coaching, networking, etc.)
- **Smart integration**: Auto-populates N5 lists, CRM data, and knowledge base
- **Approval workflow**: Review-first architecture with granular approval controls

### Architecture Principles

1. **Modular blocks**: Each intelligence type (action items, risks, insights) is a separate block
2. **Graceful degradation**: System continues even if optional components fail
3. **Idempotent operations**: Safe to re-run processing without duplicates
4. **Audit trail**: Complete metadata and error logging for every meeting

---

## Commands & Entry Points

### Primary Commands

#### `meeting-process`
**Location:** `file 'N5/commands/meeting-process.md'`  
**Script:** `file 'N5/scripts/meeting_orchestrator.py'`  
**Purpose:** Main entry point for processing meeting transcripts

**Usage:**
```bash
N5: meeting-process <transcript_source> \
  --type <meeting_type> \
  --stakeholder <stakeholder_type> \
  [--mode full|essential|quick] \
  [--output-format markdown|gmail-draft]
```

**Parameters:**
- `transcript_source`: Google Drive ID, local file path, or email attachment
- `--type`: Meeting classification (sales, community_partnerships, coaching, networking, fundraising)
- `--stakeholder`: Stakeholder role (customer_founder, vc, community_manager, etc.)
- `--mode`: Processing depth (full, essential, quick)
- `--output-format`: Output format (markdown, gmail-draft, json)

**Example:**
```bash
N5: meeting-process /path/to/transcript.txt \
  --type sales,community_partnerships \
  --stakeholder customer_founder \
  --mode full
```

#### `transcript-ingest`
**Location:** `file 'N5/commands/transcript-ingest.md'`  
**Purpose:** Batch ingest transcripts from Google Drive folders

**Usage:**
```bash
N5: transcript-ingest <gdrive_folder_id> \
  --auto-classify \
  --batch-size 5
```

---

## Core Scripts & Orchestration

### Main Orchestrator

#### `meeting_orchestrator.py`
**Location:** `file 'N5/scripts/meeting_orchestrator.py'`  
**Class:** `MeetingOrchestrator`  
**Version:** 2.0.0

**Pipeline Steps:**
1. **Fetch transcript** from source (local/GDrive)
2. **Extract meeting metadata** (participants, date, duration)
3. **Create output directory** with structured naming
4. **Save transcript** to output location
5. **Lookup meeting history** with stakeholder
6. **Fetch email history** with participants
7. **Generate blocks** (conditional based on mode & type)
8. **Generate dashboard** (REVIEW_FIRST.md)
9. **Integrate with lists** (action items, warm intros, etc.)
10. **Save metadata** (_metadata.json)

**Key Methods:**
- `process()` - Main pipeline execution
- `_fetch_transcript()` - Multi-source transcript retrieval
- `_extract_meeting_info()` - Metadata extraction
- `_generate_blocks()` - Orchestrates block generation
- `_integrate_lists()` - N5 lists integration

**Error Handling:**
- Graceful degradation for optional components
- All errors logged to `errors` array in metadata
- Non-critical failures don't block pipeline

### Legacy Workflows

#### `consolidated_workflow.py`
**Location:** `file 'N5/scripts/consolidated_workflow.py'`  
**Status:** Legacy (v1.x)  
**Purpose:** Original transcript processing workflow

**Key Features:**
- Content mapping (deliverables, CTAs, decisions)
- Ticket generation for deliverables
- Email thread integration

**Migration Note:** v2.0 orchestrator supersedes this but retains compatibility with content_map format.

#### `gdrive_transcript_workflow.py`
**Location:** `file 'N5/scripts/gdrive_transcript_workflow.py'`  
**Purpose:** Google Drive batch processing
**Status:** Active

---

## Block Generators

Blocks are modular intelligence extraction components. Each block focuses on a specific type of insight.

### Universal Blocks
*Generated for all meetings regardless of type*

#### 1. Meeting Info Extractor
**Location:** `file 'N5/scripts/blocks/meeting_info_extractor.py'`  
**Function:** `extract_meeting_info(transcript) -> Dict`

**Extracts:**
- Date & time
- Participants list
- Duration
- Primary stakeholder
- Organization

**Methods:**
- `_extract_participants()` - Parse speaker patterns
- `_extract_datetime()` - Find date/time in transcript
- `_estimate_duration()` - Calculate from timestamps
- `_determine_primary_stakeholder()` - Identify main external party

#### 2. Follow-Up Email Generator
**Module:** `blocks.follow_up_email_generator`  
**Command:** `file 'N5/commands/follow-up-email-generator.md'`  
**Function:** `generate_follow_up_email()`

**Inputs:**
- Transcript content
- Meeting info metadata
- Email history (optional)
- Meeting history (optional)
- Meeting types

**Outputs:**
- `OUTPUTS/follow_up_email.md` - Ready-to-send email draft
- Context-aware: References previous conversations and commitments

**Features:**
- Tone adaptation by stakeholder type
- Incorporates relationship history
- Action item summaries
- Next step proposals

#### 3. Action Items Extractor
**Module:** `blocks.action_items_extractor`  
**Function:** `generate_action_items()`

**Outputs:**
- `INTELLIGENCE/action_items.md`
- Structured list with:
  - Item description
  - Owner (you/them)
  - Deadline (if mentioned)
  - Priority
  - Dependencies

**List Integration:**
- Auto-adds your action items to `N5/lists/action-items.jsonl`
- Tags with meeting_id for traceability

#### 4. Decisions Extractor
**Module:** `blocks.decisions_extractor`  
**Function:** `generate_decisions()`

**Captures:**
- What was decided
- Who made the decision
- Why (rationale)
- Impact/implications
- Reversibility

#### 5. Key Insights Extractor
**Module:** `blocks.key_insights_extractor`  
**Function:** `generate_key_insights()`

**Identifies:**
- Resonance moments (emotional engagement)
- Realizations/breakthroughs
- Pattern matches (connections to other knowledge)
- Strategic implications

#### 6. Stakeholder Profile Generator
**Module:** `blocks.stakeholder_profile_generator`  
**Function:** `generate_stakeholder_profile()`

**CRM Enrichment:**
- Communication style
- Priorities/pain points
- Decision-making patterns
- Relationship health indicators
- Historical context from previous meetings

### Conditional Blocks
*Generated only when relevant content is detected*

#### 7. Warm Intro Detector
**Module:** `blocks.warm_intro_detector`  
**Function:** `generate_warm_intros() -> int`

**Triggers:** Mentions of introductions, connections, networking

**Outputs:**
- `OUTPUTS/warm_intro_<name>.md` (one per intro)
- Structured format:
  - Who to intro
  - Context/relevance
  - Suggested approach
  - Urgency

**List Integration:**
- Adds to `N5/lists/warm-intros.jsonl`

#### 8. Risks Detector
**Module:** `blocks.risks_detector`  
**Function:** `generate_risks() -> int`

**Identifies:**
- Blockers
- Concerns raised
- Timeline risks
- Resource constraints
- Misalignment signals

#### 9. Opportunities Detector
**Module:** `blocks.opportunities_detector`  
**Function:** `generate_opportunities() -> int`

**Detects:**
- Upsell possibilities
- Partnership opportunities
- Feature requests
- Market insights

#### 10. User Research Extractor
**Module:** `blocks.user_research_extractor`  
**Function:** `generate_user_research() -> int`

**Captures:**
- Pain points (verbatim quotes)
- Jobs-to-be-done
- Workflow descriptions
- Tool mentions
- Desired outcomes

#### 11. Competitive Intel Extractor
**Module:** `blocks.competitive_intel_extractor`  
**Function:** `generate_competitive_intel() -> int`

**Tracks:**
- Competitors mentioned
- Alternatives being evaluated
- Feature comparisons
- Pricing discussions

### Category-Specific Blocks

#### 12. Deal Intelligence (Sales)
**Module:** `blocks.deal_intelligence_generator`  
**Triggers:** `meeting_type == "sales"`

**Analysis:**
- Buying signal strength (0-10)
- Decision-makers identified
- Budget/authority/need/timeline (BANT)
- Next steps required
- Deal stage assessment

#### 13. Career Insights (Coaching/Networking)
**Module:** `blocks.career_insights_generator`  
**Triggers:** `meeting_type in ["coaching", "networking"]`

**Extracts:**
- Career goals
- Skill development needs
- Job search strategies
- Industry insights
- Networking opportunities

#### 14. Investor Thesis (Fundraising)
**Module:** `blocks.investor_thesis_generator`  
**Triggers:** `meeting_type == "fundraising"`

**Captures:**
- Investment criteria
- Portfolio fit
- Due diligence questions
- Timeline/process
- Decision factors

#### 15. Partnership Scope (Community Partnerships)
**Module:** `blocks.partnership_scope_generator`  
**Triggers:** `meeting_type == "community_partnerships"`

**Defines:**
- Partnership objectives
- Resource commitments
- Success metrics
- Governance structure
- Timeline

### Supporting Modules

#### Meeting History Lookup
**Module:** `blocks.meeting_history_lookup`  
**Function:** `lookup_meeting_history(stakeholder) -> List[Dict]`

**Searches:**
- Previous meetings with stakeholder
- Returns metadata + key insights
- Used to enrich context for follow-ups

#### Email History Fetcher
**Module:** `blocks.email_history_fetcher`  
**Function:** `fetch_email_history(participants) -> List[Dict]`

**Retrieves:**
- Email threads with participants
- Integrates with Gmail API (if connected)
- Used for relationship continuity

#### Dashboard Generator
**Module:** `blocks.dashboard_generator`  
**Function:** `generate_dashboard()`

**Creates:** `REVIEW_FIRST.md`

**Contents:**
- Executive summary
- Priority actions
- Key metrics (risks, opportunities, etc.)
- Quick links to all blocks
- Processing metadata

#### List Integrator
**Module:** `blocks.list_integrator`  
**Function:** `integrate_with_lists()`

**N5 List Operations:**
- Adds action items → `N5/lists/action-items.jsonl`
- Adds warm intros → `N5/lists/warm-intros.jsonl`
- Adds follow-ups → `N5/lists/must-contact.jsonl` (if urgent)
- Tags all items with `meeting_id`

---

## Schemas & Data Models

### Meeting Metadata Schema
**Location:** `file 'N5/schemas/meeting-metadata.schema.json'`  
**Version:** 2.0

**Required Fields:**
```json
{
  "meeting_id": "a83f92",          // 6-char unique ID
  "date": "2025-10-09",            // YYYY-MM-DD
  "meeting_type": ["sales"],       // Array (multi-classification)
  "stakeholder_primary": "logan-currie",
  "processing": {
    "version": "2.0.0",
    "mode": "full",
    "timestamp": "2025-10-09T14:45:00Z"
  }
}
```

**Optional Fields:**
- `time`, `timezone`
- `stakeholders_all` (array of all participants)
- `stakeholder_types` (role classifications)
- `organization`
- `participants_count`, `duration_minutes`
- `previous_meetings_count`, `previous_meeting_ids`
- `email_history_found`, `email_thread_count`

**Intelligence Metrics:**
```json
"intelligence": {
  "buying_signal": 7,              // 0-10 (sales only)
  "risks_count": 2,
  "opportunities_count": 1,
  "warm_intros_count": 1,
  "decisions_count": 3,
  "action_items_count": 5,
  "insights_count": 4
}
```

**Processing Metadata:**
```json
"processing": {
  "version": "2.0.0",
  "mode": "full",                  // full|essential|quick
  "duration_seconds": 222,
  "blocks_generated": 10,
  "timestamp": "2025-10-09T14:45:00Z",
  "errors": []                     // Array of error objects
}
```

**Transcript Source:**
```json
"transcript_source": {
  "type": "local_file",            // local_file|google_drive|email_attachment
  "identifier": "/path/to/file",
  "sha256": "abc123...",            // Content hash
  "size_bytes": 12543,
  "line_count": 450
}
```

**Approval Status:**
```json
"approval": {
  "status": "pending_review",      // pending_review|approved|needs_revision
  "approved_at": "2025-10-09T15:00:00Z",
  "approved_blocks": ["follow_up_email", "action_items"]
}
```

### Content Map Schema (Legacy)
**Format:** JSON  
**Example Location:** `file 'Careerspan/Meetings/sample_meeting_20250915/content_map.json'`

**Structure:**
```json
{
  "meeting_datetime": "2025-09-15T00:00:00",
  "deliverables": ["deliverable 1", "deliverable 2"],
  "ctas": ["call to action 1"],
  "decisions": ["decision 1", "decision 2"],
  "resonance_details": ["key moment 1", "key moment 2"],
  "speaker_quotes": []
}
```

### N5 Lists Integration Schemas

**Action Items:**
```jsonl
{"id": "act_abc123", "text": "...", "owner": "vrijen", "deadline": "2025-10-15", "meeting_id": "a83f92", "status": "pending"}
```

**Warm Intros:**
```jsonl
{"id": "intro_xyz789", "intro_to": "Shujaat Ahmad", "context": "...", "meeting_id": "a83f92", "status": "pending"}
```

**Must Contact:**
```jsonl
{"id": "contact_def456", "person": "Logan Currie", "reason": "...", "urgency": "high", "meeting_id": "a83f92"}
```

---

## Processing Workflows

### Mode Comparison

| Mode | Blocks Generated | Duration | Use Case |
|------|-----------------|----------|----------|
| **quick** | Action items only | ~30s | Rapid extraction for busy days |
| **essential** | Follow-up email, action items, decisions | ~1-2 min | Standard post-meeting workflow |
| **full** | All applicable blocks | ~3-5 min | Complete intelligence extraction |

### Full Mode Block Selection Logic

```python
# Universal blocks (always generated)
blocks = [
    "follow_up_email",
    "action_items", 
    "decisions",
    "key_insights",
    "stakeholder_profile"
]

# Conditional blocks (generated if content detected)
blocks += [
    "warm_intros",      # Confidence threshold: 70%
    "risks",            # Confidence threshold: 70%
    "opportunities",    # Confidence threshold: 70%
    "user_research",    # Confidence threshold: 80%
    "competitive_intel" # Confidence threshold: 80%
]

# Category-specific blocks
if "sales" in meeting_types:
    blocks.append("deal_intelligence")
    
if any(t in ["coaching", "networking"] for t in meeting_types):
    blocks.append("career_insights")
    
if "fundraising" in meeting_types:
    blocks.append("investor_thesis")
    
if "community_partnerships" in meeting_types:
    blocks.append("partnership_scope")
```

### Processing Timeline

```
[Start] meeting-process command invoked
  ↓
[0s] Fetch transcript from source
  ↓
[5s] Extract meeting metadata
  ↓
[10s] Create output directory
  ↓
[12s] Lookup meeting history
  ↓
[15s] Fetch email history (if Gmail connected)
  ↓
[20s] Generate universal blocks (parallel)
  ├─ Follow-up email (45s)
  ├─ Action items (20s)
  ├─ Decisions (25s)
  ├─ Key insights (30s)
  └─ Stakeholder profile (35s)
  ↓
[65s] Generate conditional blocks (parallel)
  ├─ Warm intros (15s)
  ├─ Risks (20s)
  ├─ Opportunities (20s)
  ├─ User research (25s)
  └─ Competitive intel (25s)
  ↓
[90s] Generate category-specific blocks
  └─ Deal intelligence (30s)
  ↓
[120s] Generate dashboard
  ↓
[125s] Integrate with N5 lists
  ↓
[130s] Save metadata
  ↓
[135s] Complete
```

### Error Recovery

**Graceful Degradation:**
- Gmail API unavailable → Continue without email history (note in dashboard)
- Block generation fails → Log error, continue with other blocks
- List integration fails → Log warning, blocks still saved to files

**Retry Logic:**
- LLM extraction failures: 2 retries with exponential backoff
- API timeouts: 3 retries with fallback

**Logging:**
- All errors → `N5/logs/meeting-process/YYYY-MM-DD.log`
- Error summary → `_metadata.json` → `processing.errors[]`

---

## Integration Points

### Google Drive
**Commands:** `transcript-ingest`, `meeting-process`  
**Functions:** Auto-fetch transcripts from shared folders

**Setup:**
- Requires Google Drive app connection
- Uses `use_app_google_drive` tool
- File ID format: `1A2B3C4D5E6F7G8H9I0J`

### Gmail
**Purpose:** Email history enrichment, follow-up draft creation

**Functions:**
- `_fetch_email_history()` - Pull thread history
- `--output-format gmail-draft` - Auto-create draft

**Setup:**
- Requires Gmail app connection
- Uses `use_app_gmail` tool

### N5 Lists
**Lists Updated:**
- `N5/lists/action-items.jsonl`
- `N5/lists/warm-intros.jsonl`
- `N5/lists/must-contact.jsonl`

**Integration Function:** `integrate_with_lists()`

**Tagging:**
- All items tagged with `meeting_id`
- Enables cross-referencing

### Knowledge Base
**Future:** Auto-ingest key insights → `N5/knowledge/facts.jsonl`

**Planned Integration:**
- Stakeholder profiles → CRM enrichment
- Decision patterns → Strategic knowledge
- Market intelligence → Competitive tracking

### Calendar (Future)
**Planned:** Auto-schedule follow-ups based on commitments

---

## Output Structure

### Directory Naming Convention
```
Careerspan/Meetings/YYYY-MM-DD_HHMM_<type>_<stakeholder>/
```

**Example:**
```
Careerspan/Meetings/2025-10-09_1430_sales_logan-currie/
```

**Collision Handling:**
- If directory exists, append `_<meeting_id_prefix>`
- Example: `2025-10-09_1430_sales_logan-currie_a83f/`

### Complete Output Structure
```
2025-10-09_1430_sales_logan-currie/
│
├── REVIEW_FIRST.md                    # ⭐ START HERE - Executive dashboard
├── transcript.txt                     # Original transcript
├── _metadata.json                     # Structured metadata
│
├── OUTPUTS/                           # 📧 Ready-to-use outputs
│   ├── follow_up_email.md            # Email draft (ready to send)
│   └── warm_intro_shujaat.md         # Intro email template
│
└── INTELLIGENCE/                      # 📊 Analysis & insights
    ├── action_items.md               # Your tasks + their tasks
    ├── decisions.md                  # What was decided & why
    ├── key_insights.md               # Strategic takeaways
    ├── stakeholder_profile.md        # CRM enrichment data
    ├── meeting_history_context.md    # Previous meeting refs
    │
    ├── risks.md                      # ⚠️ Conditional blocks
    ├── opportunities.md              # (generated if detected)
    ├── user_research.md
    ├── competitive_intel.md
    │
    └── deal_intelligence.md          # 🎯 Category-specific
```

### File Formats

**Markdown Files:**
- GitHub-flavored markdown
- Structured sections with headers
- Lists, tables, quotes as appropriate
- Citations for context

**JSON Files:**
- Pretty-printed (indent=2)
- UTF-8 encoding
- Schema-validated

**JSONL Files (Lists):**
- One JSON object per line
- Append-only for new items
- Deduplicated by ID

---

## Examples

### Example 1: Quick Sales Meeting

**Command:**
```bash
N5: meeting-process gdrive_file_id_here \
  --type sales \
  --stakeholder customer_founder \
  --mode essential
```

**Generated:**
- `OUTPUTS/follow_up_email.md`
- `INTELLIGENCE/action_items.md`
- `INTELLIGENCE/decisions.md`
- `REVIEW_FIRST.md`

**Processing Time:** ~90 seconds

---

### Example 2: Full Coaching Session

**Command:**
```bash
N5: meeting-process /home/workspace/Document\ Inbox/coaching_transcript.txt \
  --type coaching \
  --stakeholder candidate_job_seeker \
  --mode full
```

**Generated:**
- All universal blocks
- `career_insights.md` (category-specific)
- `opportunities.md` (detected warm intros)
- `REVIEW_FIRST.md`

**Processing Time:** ~4 minutes

---

### Example 3: Multi-Type Partnership Meeting

**Command:**
```bash
N5: meeting-process transcript.txt \
  --type sales,community_partnerships \
  --stakeholder vc,customer_channel_partner \
  --mode full
```

**Generated:**
- All universal blocks
- `deal_intelligence.md` (sales)
- `partnership_scope.md` (community_partnerships)
- `investor_thesis.md` (VC stakeholder detected)
- `REVIEW_FIRST.md`

---

### Example 4: Batch Processing

**Command:**
```bash
N5: transcript-ingest <gdrive_folder_id> \
  --auto-classify \
  --batch-size 5
```

**Behavior:**
- Fetches all transcripts from folder
- Auto-classifies meeting type/stakeholder (LLM)
- Processes 5 at a time (parallel)
- Generates summary report

---

## System Status

### Implemented ✅
- Core orchestrator (`meeting_orchestrator.py`)
- Meeting metadata extraction
- Universal blocks (follow-up, action items, decisions, insights, stakeholder profile)
- Metadata schema & validation
- Output directory structure
- Error handling & logging

### In Development 🚧
- Block generators (individual modules)
- Gmail integration
- Google Drive integration
- List integration logic
- Dashboard generator
- Meeting approval workflow

### Planned 📋
- Auto-classification from transcript content
- Cross-meeting intelligence aggregation
- Calendar integration
- Knowledge base auto-ingestion
- Meeting search & analytics
- CRM sync (HubSpot, Salesforce)

---

## Related Documentation

- **Commands:** `file 'N5/commands/meeting-process.md'`, `file 'N5/commands/transcript-ingest.md'`
- **Schemas:** `file 'N5/schemas/meeting-metadata.schema.json'`
- **Scripts:** `file 'N5/scripts/meeting_orchestrator.py'`
- **Examples:** `file 'Careerspan/Meetings/External/2025-09-19_logan-currie_shujaat-ahmad_vrijen-attawar/'`

---

## Maintenance Notes

**Version History:**
- v2.0.0 (2025-10-09): Complete redesign with block-based architecture
- v1.0.0 (2025-09-20): Initial implementation (deprecated)

**Breaking Changes from v1.x:**
- Output structure completely redesigned
- Metadata format changed
- Block-based vs. monolithic generation

**Migration Path:**
- v1.x meetings remain compatible (read-only)
- Use v2.0 for all new processing
- Historical data preserved in original format
