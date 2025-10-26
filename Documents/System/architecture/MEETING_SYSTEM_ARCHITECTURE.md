# Meeting Processing System — Complete Architecture

**Version:** 3.0 (Registry-Based + Zo LLM Integration)  
**Last Updated:** 2025-10-10  
**Status:** Production Active

---

## Table of Contents

1. [Overview & Problem Statement](#overview--problem-statement)
2. [System Overview](#system-overview)
3. [Architecture — Three-Component System](#architecture--three-component-system)
4. [Registry-Driven Design (v3.0)](#registry-driven-design-v30)
5. [Commands & Entry Points](#commands--entry-points)
6. [Core Scripts & Orchestration](#core-scripts--orchestration)
7. [Block Generators](#block-generators)
8. [Implementation Options](#implementation-options)
9. [Processing Workflows](#processing-workflows)
10. [Schemas & Data Models](#schemas--data-models)
11. [Output Structure](#output-structure)
12. [Benefits & Rationale](#benefits--rationale)
13. [Integration Points](#integration-points)
14. [Troubleshooting](#troubleshooting)
15. [Migration Notes](#migration-notes)
16. [Related Documentation](#related-documentation)

---

## Overview & Problem Statement

### The Problem (What We Solved)

**Before:**
- `meeting_intelligence_orchestrator.py` tried to call external LLM APIs
- APIs weren't configured → all extractions failed
- Fell back to simulation with placeholder content (wrong names, generic data)
- Result: **Unusable output**

**After:**
- Integrated Zo's LLM (direct processing) instead of external APIs
- Generated comprehensive, accurate meeting intelligence blocks
- Result: **Excellent quality output**

### The Question

**"Why can't we do this automatically every time?"**

**Answer: We can!** The solution integrates Zo's LLM directly into the workflow instead of calling external APIs.

### Key Insight

Instead of trying to call external LLM APIs that might fail, we use **Zo's built-in LLM capabilities** which are always available and provide higher quality, more contextualized output.

---

## System Overview

The N5 Meeting Processing System transforms raw meeting transcripts into **actionable intelligence** through a modern, registry-driven, Zo-integrated architecture.

### Key Capabilities

- **Multi-source ingestion**: Google Drive, local files, email attachments
- **Zo LLM Integration**: Direct processing without external API dependencies
- **Registry-driven**: All intelligence blocks defined in JSON configuration
- **Context-aware processing**: Enriches analysis with meeting history and email threads
- **Adaptive output**: Generates different blocks based on meeting type (sales, coaching, networking, etc.)
- **Smart integration**: Auto-populates N5 lists, CRM data, and knowledge base
- **Automated detection**: Watches for new transcripts and queues processing
- **Simulation mode**: Test without real LLM calls
- **Approval workflow**: Review-first architecture with granular approval controls

### Architecture Principles

1. **Modular blocks**: Each intelligence type (action items, risks, insights) is a separate block
2. **Graceful degradation**: System continues even if optional components fail
3. **Idempotent operations**: Safe to re-run processing without duplicates
4. **Decoupled processing**: Detection → Queue → Processing separation
5. **Self-contained**: No external module dependencies
6. **Audit trail**: Complete metadata and error logging for every meeting

---

## Architecture — Three-Component System

The system uses a three-layer architecture that separates detection, queuing, and processing:

```
┌─────────────────────────────────────────────────────────────────┐
│  1. DETECTION (meeting_auto_processor.py)                       │
│     Watches Document Inbox for new transcripts                  │
│     Creates processing requests                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. QUEUE (N5/inbox/meeting_requests/)                          │
│     Stores pending processing requests as JSON files            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. PROCESSOR (Zo - via command or scheduled task)              │
│     Processes requests using Zo's LLM capabilities              │
│     Generates intelligence blocks                               │
│     Saves to N5/records/meetings/                               │
└─────────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Detection Layer
**Script:** `meeting_auto_processor.py`  
**Purpose:** Monitors Document Inbox for new meeting transcripts

**Functions:**
- Watches for files matching patterns (`*-transcript-*.docx`, `*-transcript-*.txt`)
- Creates processing request JSON files
- Logs detected transcripts to `N5/logs/processed_meetings.jsonl`
- Runs continuously or on-demand

#### 2. Queue Layer
**Location:** `N5/inbox/meeting_requests/`  
**Purpose:** Stores pending processing requests

**Structure:**
- One JSON file per meeting request
- Contains transcript path, meeting ID, and metadata
- Enables async, batch, and scheduled processing

#### 3. Processor Layer
**Integration:** Zo's LLM  
**Purpose:** Generates intelligence blocks using direct LLM processing

**Trigger Options:**
- Manual: User says "Process pending meeting requests"
- Command: `command 'N5/commands/auto-process-meetings.md'`
- Scheduled: Every 10-30 minutes via scheduled task

---

## Registry-Driven Design (v3.0)

### Overview

Version 3.0 introduces a registry-driven architecture where all intelligence blocks are defined in JSON configuration rather than hardcoded in Python.

### Key Features

- **Registry-Driven:** All intelligence blocks defined in `block_type_registry.json`
- **Extraction Requests:** LLM processing via structured request files
- **Batch Processing:** Efficient async extraction with queuing
- **Simulation Mode:** Test without real LLM calls
- **Self-Contained:** No external module dependencies
- **Comprehensive Logging:** Full audit trail for debugging

### Block Registry System

**Registry Location:** `N5/prefs/block_type_registry.json`

**Registry Structure:**
```json
{
  \"blocks\": {
    \"B01\": {
      \"name\": \"DETAILED_RECAP\",
      \"purpose\": \"Comprehensive meeting summary\",
      \"format\": \"markdown\",
      \"variables\": [\"outcome\", \"rationale\", \"mutual_understanding\", \"next_step\"]
    },
    \"B08\": {
      \"name\": \"RESONANCE_POINTS\",
      \"purpose\": \"Moments that generated energy\",
      \"format\": \"markdown\",
      \"variables\": [\"moment\", \"why_it_mattered\"]
    }
    // ... more blocks
  }
}
```

### Block Types (v3.0)

| Block ID | Name | Purpose |
|----------|------|---------|\n| B01 | DETAILED_RECAP | Key decisions and agreements |
| B08 | RESONANCE_POINTS | High-engagement moments |
| B21 | SALIENT_QUESTIONS | Critical questions raised |
| B22 | DEBATE_TENSION_ANALYSIS | Areas of disagreement |
| B24 | PRODUCT_IDEA_EXTRACTION | Feature/product ideas |
| B25 | DELIVERABLE_CONTENT_MAP | Promised deliverables |
| B26 | MEETING_METADATA_SUMMARY | Meeting classification |
| B28 | FOUNDER_PROFILE_SUMMARY | Founder/company info |
| B29 | KEY_QUOTES_HIGHLIGHTS | Notable verbatim quotes |
| B30 | INTRO_EMAIL_TEMPLATE | Introduction email draft |

### Extraction Request Pattern

Instead of making synchronous LLM calls, the system creates **extraction request files** that can be processed in batches by Zo.

**Request File Structure:**
```json
{
  \"request_id\": \"20251010_140530_123456\",
  \"system_prompt\": \"You are an expert at analyzing meeting transcripts...\",
  \"user_prompt\": \"Analyze this meeting transcript and extract...\\n\\nTRANSCRIPT:\\n...\",
  \"json_mode\": true,
  \"timestamp\": \"2025-10-10T14:05:30Z\",
  \"response_file\": \"/path/to/response_file.json\"
}
```

**Benefits:**
- **Decoupled Processing:** Requests created independently of LLM availability
- **Batch Processing:** Multiple requests processed together by Zo
- **Caching:** Responses reused if already processed
- **Debugging:** Full audit trail of requests and responses
- **Testing:** Easy to simulate with pre-generated responses

### Architecture Evolution

**V1 (Deprecated):** Monolithic orchestrator with CRM integration  
**V2 (Deprecated):** Phased workflow with `llm_utils` module  
**V3 (Current):** Registry-driven extraction system + Zo integration ✅

**Key Improvements in v3.0:**
- Eliminated hardcoded block generation
- Removed external dependencies
- Added simulation mode for testing
- Implemented batch extraction pattern
- Integrated Zo LLM directly (no external APIs)
- Improved modularity and maintainability

---

## Commands & Entry Points

### Primary Commands

#### `meeting-process`
**Location:** `file 'N5/commands/meeting-process.md'`  
**Script:** `file 'N5/scripts/meeting_intelligence_orchestrator.py'`  
**Purpose:** Main entry point for processing meeting transcripts

**Usage:**
```bash
# Direct script usage
python3 /home/workspace/N5/scripts/meeting_intelligence_orchestrator.py \\
  --transcript_path <path> \\
  --meeting_id <id>
```

**Parameters:**
- `transcript_source`: Google Drive ID, local file path, or email attachment
- `--type`: Meeting classification (sales, community_partnerships, coaching, networking, fundraising)
- `--stakeholder`: Stakeholder role (customer_founder, vc, community_manager, etc.)
- `--mode`: Processing depth (full, essential, quick)
- `--output-format`: Output format (markdown, gmail-draft, json)
- `--use-simulation`: Enable simulation mode for testing

**Example:**
```bash
N5: meeting-process /path/to/transcript.txt \\
  --type sales,community_partnerships \\
  --stakeholder customer_founder \\
  --mode full
```

#### `transcript-ingest`
**Location:** `file 'N5/commands/transcript-ingest.md'`  
**Purpose:** Batch ingest transcripts from Google Drive folders

**Usage:**
```bash
N5: transcript-ingest <gdrive_folder_id> \\
  --auto-classify \\
  --batch-size 5
```

#### `auto-process-meetings`
**Location:** `file 'N5/commands/auto-process-meetings.md'`  
**Purpose:** Process pending meeting requests from queue

**Usage:**
```bash
# Via user command
N5: Process pending meeting requests

# Via command reference
command 'N5/commands/auto-process-meetings.md'
```

---

## Core Scripts & Orchestration

### Main Orchestrator (v3.0)

#### `meeting_intelligence_orchestrator.py`
**Location:** `file 'N5/scripts/meeting_intelligence_orchestrator.py'`  
**Class:** `MeetingIntelligenceOrchestrator`  
**Version:** 3.0.0 (Registry-based extraction system)

**Pipeline Steps:**
1. **Load configuration** (block registry, essential links)
2. **Read transcript** from file
3. **Create extraction requests** for Zo LLM processing
4. **Generate intelligence blocks** based on registry
5. **Write outputs** to meeting directory
6. **Log processing** for debugging

**Output Location:** `/home/workspace/N5/records/meetings/{meeting_id}/`

**Constructor:**
```python
MeetingIntelligenceOrchestrator(
    transcript_path: str,
    meeting_id: str,
    essential_links_path: str,
    block_registry_path: str,
    use_simulation: bool = False
)
```

**Key Methods:**
- `async load()` - Loads transcript, essential links, and block registry
- `async run()` - Executes full processing pipeline
- `_is_granola() -> bool` - Detects Granola format (Me:/Them: tags)
- `_emit(block_id: str, variables: dict) -> str` - Generates formatted output for a specific block

### Detection Script

#### `meeting_auto_processor.py`
**Location:** `file 'N5/scripts/meeting_auto_processor.py'`  
**Purpose:** Auto-detection of new transcripts

**Functions:**
- Monitors `Document Inbox/` for new transcript files
- Creates processing request JSON files
- Logs detected transcripts
- Can run continuously or on-demand (`--once`)

**Usage:**
```bash
# Run continuously in background
cd /home/workspace/N5/scripts
nohup python3 meeting_auto_processor.py > /tmp/meeting_watcher.log 2>&1 &

# One-time check
python3 meeting_auto_processor.py --once
```

**Transcript Detection Patterns:**
```python
transcript_patterns = [
    \"*-transcript-*.docx\",
    \"*-transcript-*.txt\",
    \"*meeting-notes*.docx\",
]
```

### Legacy Workflows

#### `consolidated_workflow.py`
**Location:** `file 'N5/scripts/consolidated_workflow.py'`  
**Status:** Legacy (v1.x)  
**Purpose:** Original transcript processing workflow

**Key Features:**
- Content mapping (deliverables, CTAs, decisions)
- Ticket generation for deliverables
- Email thread integration

**Migration Note:** v3.0 orchestrator supersedes this but retains compatibility with content_map format.

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
**Function:** `extract_meeting_info(transcript) -> Dict`

**Extracts:**
- Date & time
- Participants list
- Duration
- Primary stakeholder
- Organization

#### 2. Follow-Up Email Generator
**Command:** `file 'N5/commands/follow-up-email-generator.md'`  
**Function:** `generate_follow_up_email()`

**Outputs:** `OUTPUTS/follow_up_email.md` - Ready-to-send email draft

**Features:**
- Tone adaptation by stakeholder type
- Incorporates relationship history
- Action item summaries
- Next step proposals

#### 3. Action Items Extractor
**Function:** `generate_action_items()`

**Outputs:** `INTELLIGENCE/action_items.md`

**List Integration:**
- Auto-adds your action items to `N5/lists/action-items.jsonl`
- Tags with meeting_id for traceability

#### 4. Decisions Extractor
**Function:** `generate_decisions()`

**Captures:**
- What was decided
- Who made the decision
- Why (rationale)
- Impact/implications
- Reversibility

#### 5. Key Insights Extractor
**Function:** `generate_key_insights()`

**Identifies:**
- Resonance moments (emotional engagement)
- Realizations/breakthroughs
- Pattern matches (connections to other knowledge)
- Strategic implications

#### 6. Stakeholder Profile Generator
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
**Triggers:** Mentions of introductions, connections, networking

**List Integration:**
- Adds to `N5/lists/warm-intros.jsonl`

#### 8. Risks Detector
**Identifies:**
- Blockers
- Concerns raised
- Timeline risks
- Resource constraints
- Misalignment signals

#### 9. Opportunities Detector
**Detects:**
- Upsell possibilities
- Partnership opportunities
- Feature requests
- Market insights

#### 10. User Research Extractor
**Captures:**
- Pain points (verbatim quotes)
- Jobs-to-be-done
- Workflow descriptions
- Tool mentions
- Desired outcomes

#### 11. Competitive Intel Extractor
**Tracks:**
- Competitors mentioned
- Alternatives being evaluated
- Feature comparisons
- Pricing discussions

### Category-Specific Blocks

#### 12. Deal Intelligence (Sales)
**Triggers:** `meeting_type == \"sales\"`

**Analysis:**
- Buying signal strength (0-10)
- Decision-makers identified
- Budget/authority/need/timeline (BANT)
- Next steps required
- Deal stage assessment

#### 13. Career Insights (Coaching/Networking)
**Triggers:** `meeting_type in [\"coaching\", \"networking\"]`

**Extracts:**
- Career goals
- Skill development needs
- Job search strategies
- Industry insights
- Networking opportunities

#### 14. Investor Thesis (Fundraising)
**Triggers:** `meeting_type == \"fundraising\"`

**Captures:**
- Investment criteria
- Portfolio fit
- Due diligence questions
- Timeline/process
- Decision factors

#### 15. Partnership Scope (Community Partnerships)
**Triggers:** `meeting_type == \"community_partnerships\"`

**Defines:**
- Partnership objectives
- Resource commitments
- Success metrics
- Governance structure
- Timeline

---

## Implementation Options

### Option A: **Semi-Automatic** (Easiest to start)

1. Auto-detector runs in background
2. User manually triggers processing: *\"Process pending meetings\"*
3. Zo generates intelligence blocks

**Pros:** Simple, reliable, user keeps control  
**Cons:** Requires manual trigger

**Setup:**
```bash
# Start auto-detector
cd /home/workspace/N5/scripts
nohup python3 meeting_auto_processor.py > /tmp/meeting_watcher.log 2>&1 &
```

### Option B: **Fully Automatic** (Recommended)

1. Auto-detector runs in background
2. Scheduled task checks inbox every 10-30 minutes
3. Zo automatically processes new requests
4. User gets notification when complete

**Pros:** Zero manual work  
**Cons:** Requires scheduled task setup

**Setup:**
```bash
# Via Zo scheduled tasks (https://va.zo.computer/schedule)
# Schedule: Every 10 minutes
# Instruction: \"Check for and process any pending meeting requests in N5/inbox/meeting_requests/\"
```

### Option C: **Google Drive Integration** (Advanced)

1. Monitor Google Drive folder directly
2. Auto-download new Fireflies transcripts
3. Process immediately upon detection
4. Fully automated end-to-end

**Pros:** Completely hands-off from Fireflies upload to intelligence blocks  
**Cons:** Requires Google Drive API setup

---

## Processing Workflows

### Mode Comparison

| Mode | Blocks Generated | Duration | Use Case |
|------|-----------------|----------|----------|
| **quick** | Action items only | ~30s | Rapid extraction for busy days |
| **essential** | Follow-up email, action items, decisions | ~1-2 min | Standard post-meeting workflow |
| **full** | All applicable blocks | ~3-5 min | Complete intelligence extraction |

### How Zo Processing Works

When processing meeting requests, Zo:

1. **Scans inbox**: `/home/workspace/N5/inbox/meeting_requests/`
2. **For each pending request**:
   - Read request JSON (has transcript path, meeting ID)
   - Load transcript file (convert from .docx if needed)
   - Read FULL transcript into context
   - Generate intelligence blocks based on registry
   - Save to: `N5/records/meetings/{meeting-id}/blocks.md`
   - Mark request as completed
3. **Reports results**: \"Processed 2 meetings: Carly (2025-09-23), John (2025-10-08)\"

### Full Mode Block Selection Logic

```python
# Universal blocks (always generated)
blocks = [
    \"follow_up_email\",
    \"action_items\", 
    \"decisions\",
    \"key_insights\",
    \"stakeholder_profile\"
]

# Conditional blocks (generated if content detected)
blocks += [
    \"warm_intros\",      # Confidence threshold: 70%
    \"risks\",            # Confidence threshold: 70%
    \"opportunities\",    # Confidence threshold: 70%
    \"user_research\",    # Confidence threshold: 80%
    \"competitive_intel\" # Confidence threshold: 80%
]

# Category-specific blocks
if \"sales\" in meeting_types:
    blocks.append(\"deal_intelligence\")
    
if any(t in [\"coaching\", \"networking\"] for t in meeting_types):
    blocks.append(\"career_insights\")
    
if \"fundraising\" in meeting_types:
    blocks.append(\"investor_thesis\")
    
if \"community_partnerships\" in meeting_types:
    blocks.append(\"partnership_scope\")
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

## Schemas & Data Models

### Meeting Metadata Schema
**Location:** `file 'N5/schemas/meeting-metadata.schema.json'`  
**Version:** 2.0

**Required Fields:**
```json
{
  \"meeting_id\": \"a83f92\",          // 6-char unique ID
  \"date\": \"2025-10-09\",            // YYYY-MM-DD
  \"meeting_type\": [\"sales\"],       // Array (multi-classification)
  \"stakeholder_primary\": \"logan-currie\",
  \"processing\": {
    \"version\": \"3.0.0\",
    \"mode\": \"full\",
    \"timestamp\": \"2025-10-09T14:45:00Z\"
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
\"intelligence\": {
  \"buying_signal\": 7,              // 0-10 (sales only)
  \"risks_count\": 2,
  \"opportunities_count\": 1,
  \"warm_intros_count\": 1,
  \"decisions_count\": 3,
  \"action_items_count\": 5,
  \"insights_count\": 4
}
```

### N5 Lists Integration Schemas

**Action Items:**
```jsonl
{\"id\": \"act_abc123\", \"text\": \"...\", \"owner\": \"vrijen\", \"deadline\": \"2025-10-15\", \"meeting_id\": \"a83f92\", \"status\": \"pending\"}
```

**Warm Intros:**
```jsonl
{\"id\": \"intro_xyz789\", \"intro_to\": \"Shujaat Ahmad\", \"context\": \"...\", \"meeting_id\": \"a83f92\", \"status\": \"pending\"}
```

**Must Contact:**
```jsonl
{\"id\": \"contact_def456\", \"person\": \"Logan Currie\", \"reason\": \"...\", \"urgency\": \"high\", \"meeting_id\": \"a83f92\"}
```

---

## Output Structure

### File Structure Diagram

```
/home/workspace/
├── Document Inbox/
│   └── *-transcript-*.docx          ← New transcripts arrive here
│
├── N5/
│   ├── inbox/
│   │   └── meeting_requests/
│   │       └── {meeting-id}_request.json  ← Pending processing requests
│   │
│   ├── records/
│   │   └── meetings/
│   │       └── {meeting-id}/
│   │           ├── blocks.md        ← Generated intelligence
│   │           └── extraction_requests/  ← LLM request/response files
│   │
│   └── logs/
│       └── processed_meetings.jsonl ← Tracking log
```

### Complete Meeting Output Structure
```
{meeting-id}/
│
├── blocks.md                          # All intelligence blocks
├── extraction_requests/               # LLM request/response files
│   ├── request_{timestamp}.json
│   └── response_{timestamp}.json
│
└── (Legacy v2.0 structure retained for compatibility)
    ├── REVIEW_FIRST.md               
    ├── transcript.txt                
    ├── _metadata.json                
    │
    ├── OUTPUTS/                      
    │   ├── follow_up_email.md       
    │   └── warm_intro_*.md          
    │
    └── INTELLIGENCE/                 
        ├── action_items.md          
        ├── decisions.md             
        ├── key_insights.md          
        └── stakeholder_profile.md   
```

### blocks.md Format (v3.0)

```markdown
# Meeting Intelligence: {meeting_id}

## Meeting Detection
- Granola Diarization: true/false
- Processing Mode: simulation/production

---

### MEETING_METADATA_SUMMARY
---
**Feedback**: [Useful/Not Useful]
---
* **Generated Title**: Sales Call - Logan Currie
* **Subject Line**: \"Following Up: Next Steps\"
* **Delay Sensitivity**: MEDIUM
* **Stakeholder Type**: business_partner
* **Confidence Score**: 85%

---

### DETAILED_RECAP
---
**Feedback**: [Useful/Not Useful]
---
Key decisions and agreements:
• We aligned on sourcing-led GTM strategy
• You confirmed addressing unreliable inbound
• Both sides agreed that community partnerships are key
• Next critical step is to outline 3-step pilot

---

// ... more blocks
```

---

## Benefits & Rationale

### Why Zo Integration vs. External LLM APIs

| Feature | External LLM API | Zo-Integrated |
|---------|------------------|---------------|
| **Setup complexity** | High (keys, config) | None |
| **API costs** | Per-token charges | Included |
| **Context window** | Limited (8K-128K) | Unlimited* |
| **Customization** | Via prompt engineering | Interactive + learning |
| **Error handling** | Silent failures | I can ask questions |
| **Quality consistency** | Variable | Consistent (same LLM) |
| **Processing speed** | API latency | Direct processing |
| **Failure fallback** | Placeholder content | Always high quality |

*Practically unlimited for meeting transcripts (<100K tokens)

### Key Architectural Benefits

1. **Reliability:** No external API dependencies = zero configuration issues
2. **Quality:** Full transcript context available, no truncation
3. **Flexibility:** Can ask clarifying questions mid-processing
4. **Cost:** No per-token API charges
5. **Speed:** Direct processing without network latency
6. **Debugging:** Can explain reasoning and adjust approach
7. **Learning:** Improves with user feedback over time

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

### Knowledge Base (Future)
**Planned:** Auto-ingest key insights → `N5/knowledge/facts.jsonl`

### Calendar (Future)
**Planned:** Auto-schedule follow-ups based on commitments

---

## Troubleshooting

### Detection Issues

**\"No new transcripts found\"**
- Check file naming matches patterns (`*-transcript-*`)
- Verify files are in `/home/workspace/Document Inbox/`
- Check processed log: `cat /home/workspace/N5/logs/processed_meetings.jsonl`

**\"Processing request created but not processed\"**
- Manually trigger: *\"Process pending meeting requests\"*
- Check scheduled task is running
- Verify request JSON is valid

### Processing Issues

**\"Transcript File Not Found\"**
- Verify file path is correct
- Use absolute path instead of relative
- Check file permissions

**\"Configuration File Missing\"**
- Check default paths exist:
  - `/home/workspace/N5/prefs/communication/essential-links.json`
  - `/home/workspace/N5/prefs/block_type_registry.json`
- Use `--essential_links_path` and `--block_registry_path` arguments

**\"No Blocks Generated\"**
- Check log file: `cat /home/workspace/N5/logs/orchestrator_{meeting_id}.log`
- Verify extraction requests created: `ls extraction_requests/`
- Try simulation mode: `--use-simulation`

**\"Output quality is poor\"**
- Ensure full transcript is being read
- Check transcript format (clean text vs. complex formatting)
- Provide feedback: Zo can improve based on your preferences

### Debug Commands

```bash
# View recent logs
tail -n 50 /home/workspace/N5/logs/orchestrator_{meeting_id}.log

# Check for errors
grep -i \"error\" /home/workspace/N5/logs/orchestrator_{meeting_id}.log

# Validate JSON files
find /home/workspace/N5/prefs/ -name \"*.json\" -exec jq . {} \\;

# Check extraction requests
ls -la /home/workspace/N5/records/meetings/{meeting_id}/extraction_requests/
```

---

## Migration Notes

### From V2 (Deprecated)

**Key Changes:**
- Script renamed: `meeting_orchestrator.py` → `meeting_intelligence_orchestrator.py`
- No more `llm_utils` module dependency
- New extraction request pattern
- Registry-based block system
- Simulation mode added
- Zo LLM integration

**Migration Steps:**
1. Update script references in documentation
2. Use new script path in automation
3. Remove references to `llm_utils`
4. Test with simulation mode first
5. Configure block registry if customized

### From V1 (Archived)

**Major Breaking Changes:**
- Complete architecture redesign
- No CRM integration
- No deliverable orchestrator
- Different output structure
- New metadata format

**Not Backwards Compatible:** V1 meetings remain as-is, use V3 for new processing.

### What's New in v3.0

1. **Registry-Driven Architecture:** Blocks defined in JSON configuration
2. **Zo LLM Integration:** Direct processing without external APIs
3. **Extraction Request Pattern:** Batch processing capability
4. **Simulation Mode:** Testing without real LLM calls
5. **Three-Component System:** Detection → Queue → Processing separation
6. **Automated Detection:** Watches for new transcripts automatically
7. **Implementation Options:** Semi-automatic, fully automatic, or Google Drive integration

---

## Related Documentation

- **Quick Reference:** `file 'N5/System Documentation/MEETING_SYSTEM_QUICK_REFERENCE.md'`
- **Changelog:** `file 'N5/System Documentation/MEETING_PROCESS_CHANGELOG.md'`
- **Commands:** `file 'N5/commands/meeting-process.md'`, `file 'N5/commands/auto-process-meetings.md'`
- **Schemas:** `file 'N5/schemas/meeting-metadata.schema.json'`
- **Scripts:** `file 'N5/scripts/meeting_intelligence_orchestrator.py'`, `file 'N5/scripts/meeting_auto_processor.py'`

---

## Maintenance Notes

**Version History:**
- v3.0.0 (2025-10-10): Registry-driven + Zo LLM integration, three-component architecture
- v2.0.0 (2025-10-09): Block-based architecture redesign
- v1.0.0 (2025-09-20): Initial implementation (deprecated)

**Breaking Changes from v2.x:**
- Zo LLM integration (no external APIs)
- Registry-driven block generation
- Extraction request pattern
- Three-component architecture

**Breaking Changes from v1.x:**
- Output structure completely redesigned
- Metadata format changed
- Block-based vs. monolithic generation

**Migration Path:**
- v1.x meetings remain compatible (read-only)
- v2.x functionality retained in v3.0
- Use v3.0 for all new processing
- Historical data preserved in original format

---

**Last Updated:** 2025-10-10  
**Maintainer:** N5 Meeting Processing System  
**Version:** 3.0.0  
**Status:** ✅ Production Active
