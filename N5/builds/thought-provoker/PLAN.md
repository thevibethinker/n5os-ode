---
created: 2025-12-18
last_edited: 2025-12-18
version: 1.0
type: build_plan
status: draft
---

# Plan: Daily Thought Provoker Session

**Objective:** Implement a system that identifies challenging themes from V's inbox and facilitates a daily Socratic session to develop thinking and generate content fodder.

**Trigger:** V requested a "thought provoker" feature to develop thinking based on inbox content for content generation.

**Key Design Principle:** Simple > Easy. Leverage existing inbox scan data (`email_scan_temp.json`) to minimize new infrastructure. Focus on the *quality* of the challenge rather than the complexity of the delivery.

---

## Open Questions

- [ ] Should the session happen via SMS, Email, or an interactive Zo thread? (Proposal: Interactive Zo thread triggered by notification).
- [ ] Where should the "fodder" be canonically stored? (Proposal: `N5/data/content_fodder.jsonl` and mirrored to Content Library).
- [ ] How do we define "provocative" for the LLM? (Proposal: Contrarian views, complex problems, significant market shifts, or conflicting data points).

---

## Checklist

### Phase 1: Intelligence Extraction
- ☐ Create `N5/scripts/thought_provoker_scan.py` to identify provocation candidates.
- ☐ Create `N5/data/provocation_candidates.json` schema.
- ☐ Test: Run scan on current `email_scan_temp.json` and verify 3 high-quality candidates.

### Phase 2: Session Orchestration
- ☐ Create `Prompts/Thought Provoker Session.prompt.md`.
- ☐ Implement "Fodder Capture" logic to summarize and store session insights.
- ☐ Test: Manual session run with V using one candidate.

### Phase 3: Scheduling & Loop
- ☐ Create a scheduled task `agent_thought_provoker_scan` (daily).
- ☐ Implement notification (SMS) to V when candidates are ready.
- ☐ Link session output to Content Library system.
- ☐ Test: End-to-end flow from scan to fodder storage.

---

## Phase 1: Intelligence Extraction

### Affected Files
- `N5/scripts/thought_provoker_scan.py` - CREATE - Scans inbox data for provocative themes.
- `N5/data/provocation_candidates.json` - CREATE - Storage for daily session triggers.

### Changes

**1.1 Extraction Logic:**
Develop a script that reads the latest inbox scan (`N5/data/email_scan_temp.json`). It will send the top 20 snippets to an LLM with a specialized rubric:
- **Cross-Pollination (Level Upper suggestion):** Find 2 disparate threads and force a connection/tension.
- **Contradiction:** Ideas that conflict with V's stated positions or Careerspan's mission.
- **Signal:** Significant market shifts or competitor moves.
- **Truth Anchor:** Every provocation MUST be rooted in a verifiable inbox quote.

**1.2 Candidate Storage:**
Store 1-3 candidates per day. Each candidate includes: `thread_ids` (can be multiple), `subject`, `provocation_prompt`, and `direct_quote`.

### Unit Tests
- `test_extraction`: Run script, ensure output JSON is valid and contains at least 1 candidate.

---

## Phase 2: Session Orchestration

### Affected Files
- `Prompts/Thought Provoker Session.prompt.md` - CREATE - The interactive session handler.
- `N5/scripts/fodder_collector.py` - CREATE - Appends session insights to content fodder list.
- `Lists/unresolved-contradictions.jsonl` - CREATE - Registry for ongoing tensions (Level Upper suggestion).

### Changes

**2.1 Session Modes:**
- **Mode A (Nucleus):** A single high-signal "What if?" sent via SMS. Raw reply is captured.
- **Mode B (Socratic):** Interactive session in Zo thread. AI plays Devil's Advocate (forcing V to attack his own safe positions).

**2.2 Fodder & Tension Capture:**
Store results as "Nucleus" (short developed thought) or "Tension" (unresolved contradiction).

### Unit Tests
- `test_session_flow`: Verify prompt can load candidates and call collector with summary.

---

## Phase 3: Scheduling & Loop

### Affected Files
- `N5/config/scheduled_tasks.jsonl` - UPDATE - Register daily scan.
- `N5/scripts/notify_v.py` - UPDATE/USE - Send SMS when candidates are ready.

### Changes

**3.1 Scheduled Agent:**
Register a task that runs `thought_provoker_scan.py` every morning at 8:00 AM.

**3.2 Notification:**
If candidates are found, send an SMS: "🧠 3 thought-provokers ready from your inbox. Type '@Thought Provoker Session' when you're ready to engage."

---

## Success Criteria

1. Daily scan successfully identifies themes from 100% of inbox data.
2. Socratic sessions result in at least one "content fodder" entry or "unresolved tension" per session.
3. Provocations are verifiable against direct quotes (Truth Anchor).

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| PII Leakage | LLM instructions to strip names/confidential data before storing fodder. |
| Noise | Rigorous rubric for "provocative" to avoid trivial challenges. |
| Friction | SMS notification makes it easy to remember but session is opt-in. |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. **Devil's Advocate Swap:** Flip cognitive load from defense to offense.
2. **Laziest SMS Nucleus:** Use frictionless pattern interrupt.
3. **Cross-Pollination Friction:** Force synthetic connections between disparate domains.
4. **Registry of Uncertainty:** Value unsolved tensions as highly as solved thoughts.

### Incorporated:
- **Cross-Pollination:** Added to extraction logic.
- **SMS Nucleus Mode:** Added as alternative delivery path.
- **Truth Anchor:** Required quotes to prevent "Meanness Hallucination".
- **Registry of Uncertainty:** Added `unresolved-contradictions.jsonl`.

### Rejected (with rationale):
- **Devil's Advocate Swap (as mandatory):** Kept as an optional register within Mode B to ensure variety, rather than the only way to engage.
- **Filter Bubble breaking (External feeds):** Rejected for Phase 1 to maintain Simple > Easy principle; focus on inbox first.


