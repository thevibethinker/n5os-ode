---
created: 2025-12-22
last_edited: 2025-12-27
version: 2.0
type: build_plan
status: in_progress
provenance: con_uvuYqpsPTqWJCJOM
---

# Plan: N5 to Airtable Acquisition Tracking System

**Objective:** Create a seamless bridge that automatically syncs acquisition deal intelligence from N5 meeting transcripts to the "Tracking Acquisition Deals" Airtable base.

**Trigger:** V wants to track Teamwork Online, FutureFit, and Ribbon deals automatically based on meeting identifying markers.

**Key Design Principles:**
1. **Qualitative over Quantitative**: Focus on relationship signals, strategic fit, and conversational intelligence—not financials.
2. **Append-Only**: Each meeting adds to existing intelligence fields rather than overwriting. Build cumulative context.
3. **Hybrid Detection**: Manual V-trigger + Semantic pattern sensing in B-blocks.

---

## Open Questions
- [x] Do we want separate tables for "Deals" and "Contacts"? -> YES: Organizations, Contacts, Deals, and Meeting Audit.
- [x] What fields should we track? -> Qualitative, append-only (see Phase 1 below).
- [ ] What is the exact trigger for "acquisition for Careerspan"? -> Hybrid: Manual V-trigger + Semantic pattern sensing.

---

## Checklist

### Phase 1: Relational Schema Build ✅ COMPLETE
- [x] Create Organizations Table.
- [x] Create Contacts Table (Linked to Orgs).
- [x] Create Deals Table (Linked to Orgs/Contacts).
- [x] Create Meeting Audit Table (Tracks con_ID and ingestion date).
- [x] Seed initial data: Teamwork Online, FutureFit, Ribbon.
- [ ] Update field structure to match qualitative/append-only spec (see below).

### Phase 2: Ingestion & Sensing Logic (IN PROGRESS)
- [ ] Update Airtable fields to match new qualitative spec.
- [ ] Create `airtable_deal_sync.py` - Script to process a specific meeting folder.
- [ ] Define "Acquisition Signal" detection logic.
- [ ] Create `acquisition_deal_scanner.py` - Orchestrator that scans for unprocessed meetings.
- [ ] Test: Manually trigger ingestion of one Ribbon meeting.

---

## Phase 1: Qualitative Field Structure (Updated)

### Organizations Table (`tbll78YaQL4SyJtFn`)
| Field | Type | Purpose |
|-------|------|---------|
| Name | Single Line | Company name |
| Website | URL | Company website |
| Industry | Single Line | Industry/vertical |
| Company Context | Long Text (Append) | Cumulative intel about the company from meetings |
| Total Meetings | Number | Count of meetings with this org |
| Last Meeting Date | Date | Most recent interaction |

### Contacts Table (`tbl67Zvy7bFQJwft3`)
| Field | Type | Purpose |
|-------|------|---------|
| Name | Single Line | Person's name |
| Title | Single Line | Job title |
| Email | Email | Contact email |
| Organization | Link | Link to Organizations |
| Role in Deal | Single Line | Champion, Decision-Maker, Influencer, etc. |
| Relationship Notes | Long Text (Append) | Cumulative notes on the relationship |

### Deals Table (`tblVvlBtY4QtmA7ss`)
| Field | Type | Purpose |
|-------|------|---------|
| Deal Name | Single Line | e.g., "Ribbon Acquisition" |
| Organization | Link | Link to Organizations |
| Main Contact | Link | Link to Contacts |
| Status | Single Select | Pre-talk, Active, Due Diligence, Closed-Won, Closed-Lost |
| **Strategic Fit Summary** | Long Text (Append) | Why this deal makes sense for Careerspan. Append each meeting's insights. |
| **Key Moments Log** | Long Text (Append) | Chronological log of pivotal moments from B21 blocks. |
| **Risks & Blockers** | Long Text (Append) | Accumulated risks and concerns from B13 blocks. |
| **Opportunities & Synergies** | Long Text (Append) | Accumulated opportunities from B13 blocks. |
| **Deliverables & Next Steps** | Long Text (Append) | Action items and deliverables from B25 blocks. |
| **Stakeholder Map** | Long Text (Append) | Key people involved from B08 blocks. |
| Total Meetings | Number | Count of meetings related to this deal |
| Last Meeting Date | Date | Most recent meeting |

### Meeting Audit Trail (`tbl2mFQSHP5bOIus4`)
| Field | Type | Purpose |
|-------|------|---------|
| Meeting ID | Single Line | Folder name (e.g., `2025-12-22_Christine-Song-Ribbon-Partnership-Sync`) |
| Meeting Title | Single Line | Human-readable title |
| Associated Deal | Link | Link to Deals |
| Intelligence Extracted | Checkbox | Whether B-blocks were processed |
| Notes | Long Text | Any issues or special notes |

---

## Phase 2: Listening Agent Design

### Detection Logic (Hybrid)

**Method 1: Explicit Trigger (Manual)**
- V tells Zo: "This meeting is an acquisition meeting for [Company]"
- Agent immediately processes and syncs to Airtable

**Method 2: Semantic Sensing (Automatic)**
The agent scans meeting B-blocks for acquisition signals:

1. **Entity Match**: Does B01/B08 mention a "Watched Entity"? (Teamwork Online, FutureFit, Ribbon, or any org in Deals table)
2. **Topic Signal**: Does B01 contain acquisition-related language?
   - Keywords: "acquisition", "partnership", "integration", "merge", "buy", "acquire", "deal", "strategic fit", "synergy"
   - Context: Discussion of company structure, ownership, or strategic alignment
3. **Meeting Type**: Is `manifest.json` → `meeting_type` set to "partnership", "strategic", "acquisition", or "M&A"?

**Confidence Threshold:**
- Entity Match + Topic Signal = AUTO-SYNC (high confidence)
- Entity Match only = PROMPT V for confirmation
- Topic Signal only = LOG for review, don't auto-sync

### B-Block to Airtable Field Mapping

| B-Block | Airtable Field | Extraction Logic |
|---------|----------------|------------------|
| B01 (Detailed Recap) | Strategic Fit Summary | Extract sections on partnership/integration value |
| B08 (Stakeholder Intel) | Stakeholder Map | Append key people and their roles |
| B13 (Risks & Opportunities) | Risks & Blockers, Opportunities & Synergies | Split by risk vs. opportunity |
| B21 (Key Moments) | Key Moments Log | Append timestamped moments |
| B25 (Deliverables) | Deliverables & Next Steps | Append action items |

### Append-Only Update Pattern

When syncing a new meeting to an existing deal:

```
[2025-12-22] Christine Song Sync
- Key insight: Ribbon interested in "Iron Triangle" integration
- Christine offered intro to Ribbon leadership
- Next step: Send demo account and blurb

[2025-12-23] Follow-up Call
- New insight: ...
```

Each update is prepended with a date header and appended to the existing field content.

---

## Affected Files

### Phase 2 Scripts
- `N5/scripts/airtable_deal_sync.py` - CREATE - Process a single meeting folder and sync to Airtable
- `N5/scripts/acquisition_deal_scanner.py` - CREATE - Scan for unprocessed meetings matching watched entities
- `N5/scripts/airtable_config.py` - CREATE - Configuration for Airtable IDs and watched entities

---

## Success Criteria
1. Initial 3 deals are tracked in Airtable with proper relational links.
2. Running `acquisition_deal_scanner.py` finds unprocessed Ribbon/Teamwork meetings and syncs them.
3. Each sync appends to existing fields rather than overwriting.
4. Meeting Audit Trail shows which meetings have been processed.
5. V can manually trigger sync for any meeting.

---

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Duplicate records | Lookup by Meeting ID before creating audit entries |
| Over-detection (false positives) | High confidence threshold, prompt V for ambiguous cases |
| Append fields get too long | Summarize older entries periodically (future enhancement) |
| B-blocks missing | Graceful degradation—sync what exists, log gaps |

---

## Current State (2025-12-27)
- Phase 1: ✅ Complete (tables created, seed data in place)
- Phase 2: ✅ Complete (scripts built, initial syncs done)
- Phase 3: 🔄 In Progress (deal progression + context-aware analysis)

---

## Phase 3: Deal Progression & Context-Aware Analysis

### New Fields for Deals Table
| Field | Type | Purpose |
|-------|------|---------|
| Last Meeting Date | Text (YYYY-MM-DD) | Most recent meeting date |
| Meeting Count | Number | Total meetings for this deal |
| Momentum | Select | Accelerating / Steady / Stalling / Stalled |
| Next Steps | Long Text | What's supposed to happen next? |
| Open Action Items | Long Text | Unresolved commitments from B05 |
| Blockers | Long Text | What's preventing progress? |
| Deal Health | Select | 🟢 Healthy / 🟡 Needs Attention / 🔴 At Risk |

### B-Block Mapping (Expanded)
| Block | Field | Purpose |
|-------|-------|---------|
| B01 | Intelligence Summary | Strategic insights (append) |
| B02 | Open Action Items | Commitments to track |
| B05 | Open Action Items | Action items (unchecked = open) |
| B08 | Stakeholder Map | Key people |
| B13 | Blockers | Risks that could stall deal |
| B21 | Intelligence Summary | Pivotal moments |
| B25 | Next Steps | Deliverables → what's next |

### Context-Aware Sync Logic
1. **Before appending**, read current deal state:
   - Previous Intelligence Summary
   - Previous Next Steps
   - Previous Open Action Items
   
2. **Compare** new meeting to previous state:
   - Did promised actions get completed?
   - Are we making progress on Next Steps?
   - New blockers vs. resolved blockers?
   
3. **Calculate Momentum**:
   - `Accelerating`: Multiple meetings in past 2 weeks, action items completing
   - `Steady`: Regular cadence, progress on commitments
   - `Stalling`: 1+ weeks since contact, open action items piling up
   - `Stalled`: 3+ weeks since contact, no recent progress
   
4. **Generate Deal Health**:
   - 🟢 Healthy: Momentum is Accelerating/Steady, no major blockers
   - 🟡 Needs Attention: Stalling or blockers emerging
   - 🔴 At Risk: Stalled, unresolved blockers, ghosting signals

### Scheduled Agent Design
- **Frequency**: Daily at 8 AM ET
- **Tasks**:
  1. Run discovery scanner for new opportunities
  2. For each tracked deal, check for new meetings to ingest
  3. Sync new meeting intelligence with context-aware analysis
  4. Update Momentum and Deal Health based on time-since-contact
  5. Generate digest of changes (email to V if significant)



