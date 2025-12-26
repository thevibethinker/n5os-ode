---
created: 2025-12-22
last_edited: 2025-12-22
version: 1.0
type: build_plan
status: draft
provenance: con_uvuYqpsPTqWJCJOM
---

# Plan: N5 to Airtable Acquisition Tracking System

**Objective:** Create a seamless bridge that automatically syncs acquisition deal intelligence from N5 meeting transcripts to the "Tracking Acquisition Deals" Airtable base.

**Trigger:** V wants to track Teamwork Online, FutureFit, and Ribbon deals automatically based on meeting identifying markers.

**Key Design Principle:** Plans are FOR AI execution. This plan enables Zo (Builder) to populate the base and configure the "listening" logic for future meetings.

---

## Open Questions
- [x] Do we want separate tables for "Deals" and "Contacts" in the new base? -> YES: Organizations, Contacts, Deals, and Meeting Audit.
- [ ] What is the exact trigger for "acquisition for Careerspan"? (Hybrid: Manual V-trigger + Semantic pattern sensing in B-blocks).

---

## Checklist

### Phase 1: Relational Schema Build
- ☐ Create Organizations Table.
- ☐ Create Contacts Table (Linked to Orgs).
- ☐ Create Deals Table (Linked to Orgs/Contacts).
- ☐ Create Meeting Audit Table (Tracks con_ID and ingestion date).
- ☐ Seed initial data: Teamwork Online, FutureFit, Ribbon.
- ☐ Test: Verify relational links work (e.g., linked Contact shows up in Deal).

### Phase 2: Ingestion & Sensing Logic
- ☐ Create `airtable_ingest_meeting.py` - Script to process a specific con_ID.
- ☐ Define "Acquisition Signal" prompt for intelligence extraction.
- ☐ Create `acquisition_deal_tracker.py` - Orchestrator that scans for unprocessed meetings.
- ☐ Test: Manually trigger ingestion of one recent acquisition meeting.

---

## Phase 1: Relational Schema Build

### Affected Files
- `Airtable: appL2OJHiwBmOoU8z` - RESTRUCTURE - Create 4 tables and establish links.

### Changes

**1.1 Organizations Table:**
- Fields: `Name`, `Website`, `Industry`, `Total Meetings`.

**1.2 Contacts Table:**
- Fields: `Name`, `Title`, `Email`, `Organization` (Link), `Last Contacted`.

**1.3 Deals Table:**
- Fields: `Deal Name`, `Organization` (Link), `Main Contact` (Link), `Status` (Pre-talk, Active, Due Diligence, Closed), `Intelligence Summary`, `Estimated Value`.

**1.4 Meeting Audit Table:**
- Fields: `Meeting ID` (con_ID), `Meeting Title`, `Date Ingested`, `Associated Deal` (Link).

**1.5 Initial Seeding:**
- Map the initial companies and key folks identified in the conversation.

### Unit Tests
- `Relational Integrity`: Creating a deal for "Ribbon" correctly pulls in "Ribbon" as the Organization.
- `Audit Trail`: Manually adding an entry to the Audit table correctly links to a dummy Deal.

---

## Phase 2: Intelligence Integration

### Affected Files
- `N5/scripts/airtable_deal_sync.py` - CREATE - Logic to parse B-blocks and update Airtable.
- `Prompts/Meeting Process.prompt.md` - UPDATE - Add hook for acquisition deal sync.

### Changes

**2.1 Detection Logic:**
- Create a list of "Watched Entities": Teamwork Online, FutureFit, Ribbon.
- Logic: If transcript mentions these OR meeting metadata contains `topic: acquisition`, trigger sync.

**2.2 Mapping B-Blocks:**
- Map `B01` (Recap) -> `Interaction Summary`.
- Map `B08` (Stakeholders) -> `Key Person`.
- Map current date -> `Last Meeting Date`.

### Unit Tests
- `Mock Run`: Use an existing meeting folder to trigger a manual sync.
- `Verification`: Check if "Interaction Summary" in Airtable matches the B01 block.

---

## Success Criteria
1. Initial 3 deals are tracked in Airtable.
2. New meetings mentioning these companies automatically update the "Interaction Summary".
3. A clear "Status" is visible in Airtable for each acquisition deal.

---

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Duplicate records | Use "Company Name" as a unique identifier/lookup before creating. |
| Noise in detection | Use high-confidence keyword matching + manual verification if needed. |

---

## Level Upper Review
(To be invoked before finalization)


