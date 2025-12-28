---
created: 2025-12-26
last_edited: 2025-12-26
version: 1.0
type: build_plan
status: draft
provenance: con_XI9x9PheQIwZQ84j
---

# Plan: Thought Provoker V2 — Meeting-Based Pattern Detection

**Objective:** Replace the email-based scanning with meeting `B32_THOUGHT_PROVOKING_IDEAS.md` blocks as the primary source. Add cross-meeting pattern detection to surface recurring themes, contradictions, and evolving positions over time.

---

## Open Questions

1. **Time Window:** Should the daily scan look at the last 7 days, 14 days, or all-time for pattern detection?
   - *Recommendation:* Last 14 days for "fresh" ideas, but query semantic memory for all-time contradiction detection.
2. **Pattern Categories:** What types of patterns to detect?
   - Recurring themes (same topic across 3+ meetings)
   - Contradictions (opposing positions taken)
   - Evolving positions (stance shifted over time)
   - Cross-pollination opportunities (idea from domain A applies to domain B)

---

## Checklist

### Phase 1: B32 Scanner
- [ ] Create `thought_provoker_scan_v2.py` to scan `B32` blocks
- [ ] Parse B32 markdown structure (idea title, provocation, category)
- [ ] Filter to last N days (configurable, default 14)
- [ ] Output structured JSON to `N5/data/provocation_candidates_v2.json`
- [ ] Unit test: Verify valid JSON output with at least 1 candidate

### Phase 2: Pattern Detector
- [ ] Create `thought_provoker_patterns.py` for cross-meeting analysis
- [ ] Implement recurring theme detection (semantic similarity >0.8)
- [ ] Implement contradiction detection (opposing positions)
- [ ] Implement evolution tracking (same topic, different stance)
- [ ] Output pattern report to `N5/data/provocation_patterns.json`
- [ ] Unit test: Run on 140 existing B32 files, verify pattern output

### Phase 3: Session Integration
- [ ] Update `Prompts/Thought Provoker Session.prompt.md` to use new data sources
- [ ] Add "Pattern Challenge" mode (confront V with contradictions)
- [ ] Add "Theme Deep Dive" mode (explore recurring theme)
- [ ] Update scheduled task to run v2 scanner
- [ ] Unit test: Verify prompt loads candidates correctly

---

## Phase 1: B32 Scanner

### Affected Files
- `N5/scripts/thought_provoker_scan_v2.py` (NEW)
- `N5/data/provocation_candidates_v2.json` (NEW)

### Changes

**1.1 Create B32 Scanner Script**
- Walk `Personal/Meetings/Week-of-*/**/B32_*.md`
- Parse each B32 file for structured ideas (title, provocation, category if present)
- Filter by file modification date (last N days)
- Output JSON array of candidates with:
  - `meeting_folder`: Path to source meeting
  - `meeting_date`: Extracted from folder name
  - `ideas`: Array of {title, provocation, category}

**1.2 Data Structure**
```json
{
  "scan_date": "2025-12-26T12:00:00Z",
  "window_days": 14,
  "meetings_scanned": 12,
  "candidates": [
    {
      "meeting_folder": "Week-of-2025-12-08/2025-12-09_Mckinsey-Alumni-Founders-Monthly",
      "meeting_date": "2025-12-09",
      "ideas": [
        {
          "title": "Philanthropy as a Reputation Multiplier",
          "provocation": "Can a community-wide philanthropy standard actually lower the cost of capital?",
          "category": "Strategy"
        }
      ]
    }
  ]
}
```

### Unit Tests
- `test_b32_scan`: Run scanner, verify JSON is valid and contains expected fields.

---

## Phase 2: Pattern Detector

### Affected Files
- `N5/scripts/thought_provoker_patterns.py` (NEW)
- `N5/data/provocation_patterns.json` (NEW)
- `N5/prompts/extraction/detect_patterns.md` (NEW)

### Changes

**2.1 Pattern Detection Script**
- Load all B32 candidates (not just last 14 days for pattern detection)
- Use semantic similarity (via `N5/cognition/n5_memory_client.py` embeddings) to cluster ideas
- Detect:
  - **Recurring Themes:** Ideas with >0.8 similarity across 3+ meetings
  - **Contradictions:** Ideas with high topic similarity but opposing sentiment/stance
  - **Evolutions:** Same topic, chronologically shifting position

**2.2 LLM-Assisted Pattern Synthesis**
- For detected clusters, use LLM to synthesize:
  - Theme name
  - Summary of positions
  - Key tension or contradiction
  - Suggested provocation question for V

**2.3 Output Structure**
```json
{
  "analysis_date": "2025-12-26T12:00:00Z",
  "patterns": [
    {
      "type": "recurring_theme",
      "theme": "Talent Incentive Models",
      "meetings": ["2025-12-09_Mckinsey...", "2025-11-15_Founder..."],
      "summary": "V keeps returning to the question of what motivates early-stage talent.",
      "provocation": "You've discussed cash vs. credentials vs. equity across 4 meetings. What's your synthesized thesis?"
    },
    {
      "type": "contradiction",
      "theme": "AI Automation vs. Human Touch",
      "meetings": ["2025-12-01_...", "2025-12-08_..."],
      "tension": "In meeting A, you argued for full automation. In meeting B, you emphasized human judgment.",
      "provocation": "Where exactly is the line between 'automate everything' and 'humans in the loop'?"
    }
  ]
}
```

### Unit Tests
- `test_pattern_detection`: Run on existing 140 B32 files, verify at least 1 pattern detected.

---

## Phase 3: Session Integration

### Affected Files
- `Prompts/Thought Provoker Session.prompt.md` (UPDATE)
- `N5/scripts/thought_provoker_agent.py` (UPDATE)
- Scheduled task (UPDATE instruction)

### Changes

**3.1 Update Prompt**
- Add two session modes:
  - **Fresh Ideas Mode:** Pick from last 14 days of B32 candidates
  - **Pattern Challenge Mode:** Confront V with a detected pattern/contradiction
- Include pattern data in prompt context

**3.2 Update Agent Script**
- Run `thought_provoker_scan_v2.py` first
- Run `thought_provoker_patterns.py` second
- Combine outputs for notification decision

**3.3 Update Scheduled Task**
- Change instruction to run v2 scripts
- Notify if either fresh provocations OR interesting patterns detected

### Unit Tests
- `test_session_load`: Verify prompt can load both candidate files.

---

## Alternatives Considered (Nemawashi)

### Alternative A: Pure Semantic Memory Query
- **Approach:** Query the N5 Brain directly for "contradictions in V's recent thinking"
- **Pros:** Leverages existing infrastructure, no new scanning needed
- **Cons:** Less structured, harder to trace back to specific meetings
- **Decision:** REJECTED for Phase 1. May incorporate in Phase 2 for deeper pattern detection.

### Alternative B: Raw Transcript Scanning
- **Approach:** Scan raw `transcript.jsonl` files instead of B32 blocks
- **Pros:** More comprehensive, catches ideas not in B32
- **Cons:** Noisy, slower, requires heavy LLM processing
- **Decision:** REJECTED. B32 blocks are already distilled. Use them.

### Alternative C: Hybrid (B32 + B01 Recap)
- **Approach:** Also scan B01_DETAILED_RECAP for additional context
- **Pros:** Richer context for pattern detection
- **Cons:** More complexity, B32 should already capture key provocations
- **Decision:** DEFERRED. Start with B32-only, add B01 if needed.

---

## Trap Doors (Irreversible Decisions)

1. **Data Format:** The JSON structure for `provocation_candidates_v2.json` will be consumed by the prompt. Changing it later requires prompt updates.
   - *Mitigation:* Keep structure simple and extensible (array of objects).

2. **Deprecating V1:** The email-based scanner will be superseded but not deleted.
   - *Mitigation:* Keep v1 files in place. Update scheduled task to use v2.

---

## Success Criteria

1. Scanner produces valid JSON from 140+ existing B32 files
2. Pattern detector identifies at least 3 recurring themes and 1 contradiction
3. Updated prompt successfully loads and uses new data sources
4. Scheduled task triggers with meeting-based provocations

---

## Level Upper Review

*(To be completed after initial plan review)*

### Incorporated:
- 

### Rejected (with rationale):
- 

