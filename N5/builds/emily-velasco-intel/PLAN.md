---
created: 2025-12-26
last_edited: 2025-12-26
version: 1.0
type: build_plan
status: draft
---

# Plan: Meeting Intelligence Blocks: Emily Velasco

**Objective:** Generate 11 standardized intelligence blocks for the meeting transcript between Vrijen Attawar and Emily Velasco.

**Trigger:** User request to generate intelligence blocks based on provided transcript.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

- [ ] Does the meeting directory exist and contain a manifest or transcript file? (Transcript was provided in prompt, directory is `/home/workspace/Personal/Meetings/Week-of-2025-11-10/2025-11-14_Vrijen-Attawar-And-Emily-Velasco`)
- [ ] Are there specific templates for B32 or B03_DECISIONS? (Standard blocks usually follow N5 structure; I will use standard high-fidelity analysis for these).

---

## Checklist

### Phase 1: Context Extraction & Mapping
- ☐ Verify directory exists
- ☐ Map transcript content to intelligence blocks
- ☐ Test: Directory structure is valid

### Phase 2: Block Generation
- ☐ Generate B01, B03 (Stakeholder), B03 (Decisions), B05, B06
- ☐ Generate B07, B14, B21, B25, B26, B32
- ☐ Test: All files exist with correct YAML frontmatter and provenance

---

## Phase 1: Context Extraction & Mapping

### Affected Files
- `/home/workspace/Personal/Meetings/Week-of-2025-11-10/2025-11-14_Vrijen-Attawar-And-Emily-Velasco/` - LIST - check directory contents

### Changes

**1.1 Verify and Prepare:**
Check for the existence of the meeting folder and ensure it is ready for block generation.

### Unit Tests
- Directory existence check: `/home/workspace/Personal/Meetings/Week-of-2025-11-10/2025-11-14_Vrijen-Attawar-And-Emily-Velasco` should exist.

---

## Phase 2: Block Generation

### Affected Files
- `B01_DETAILED_RECAP.md` - CREATE
- `B03_STAKEHOLDER_INTELLIGENCE.md` - CREATE
- `B03_DECISIONS.md` - CREATE
- `B05_ACTION_ITEMS.md` - CREATE
- `B06_BUSINESS_CONTEXT.md` - CREATE
- `B07_TONE_AND_CONTEXT.md` - CREATE
- `B14_BLURBS_REQUESTED.md` - CREATE
- `B21_KEY_MOMENTS.md` - CREATE
- `B25_DELIVERABLES.md` - CREATE
- `B26_MEETING_METADATA.md` - CREATE
- `B32_THOUGHT_PROVOKING_IDEAS.md` - CREATE

### Changes

**2.1 Block Content Generation:**
Each block will be generated based on the semantic analysis of the transcript.
- **B01**: Chronological recap of the conversation.
- **B03 (Stakeholder)**: Profile details for Emily Nelson de Velasco (Founder, job search coach focusing on discovery/alignment/execution).
- **B03 (Decisions)**: Key decisions made (e.g., Emily joining the Slack group).
- **B05**: Tasks for V (add to Slack, find guest) and Emily (send link/questions).
- **B06**: Careerspan business context, focus on AI job search and community building.
- **B07**: Tone analysis (warm, collaborative, mutual admiration).
- **B14**: Explicit blurb requests (Emily mentioned a guy for the group).
- **B21**: Timestamps for specific topic shifts.
- **B25**: Deliverables identified (podcast recording, guest suggestions).
- **B26**: Metadata (Participants: Vrijen Attawar, Emily Nelson de Velasco; Date: 2025-11-14).
- **B32**: Strategic ideas (Stage 1/2/3 framework for job search, collaborating with "competitors").

### Unit Tests
- File existence check: 11 files created in target directory.
- YAML validation: All files contain created, last_edited, version, and provenance.

---

## Success Criteria

1. 11 markdown files created in the specified directory.
2. Content reflects high-fidelity analysis of the provided transcript.
3. YAML frontmatter is correctly applied to all files.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Missing context from short transcript | Infer from established Careerspan/V context |
| Filename collisions | Check directory first before writing |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. Merge B03_DECISIONS and B05_ACTION_ITEMS if they overlap heavily. (Kept separate as per specific request).
2. Use JSONL for B14 if intended for pipeline processing. (Sticking to MD as requested for "markdown files").

### Incorporated:
- Separation of B03 Stakeholder and B03 Decisions.

### Rejected (with rationale):
- JSONL for B14: User specifically asked for markdown files.

