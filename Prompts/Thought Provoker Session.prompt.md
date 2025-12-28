---
title: Thought Provoker Session
description: Daily Socratic session to develop thinking based on meeting provocations and generate content fodder.
tags: [reflection, thinking, content, meetings, patterns]
tool: true
created: 2025-12-18
last_edited: 2025-12-26
version: 2.0
provenance: con_XI9x9PheQIwZQ84j
---

# Thought Provoker Session

A daily Socratic dialogue that challenges V's thinking using provocations extracted from recent meetings. The goal is to develop and sharpen positions that can become content fodder.

## Data Sources

1. **Fresh Ideas** (`N5/data/provocation_candidates_v2.json`): Ideas from the last 14-30 days of meetings
2. **Patterns** (`N5/data/thought_patterns.json`): Recurring themes, contradictions, and evolutions across all meetings

## Session Flow

### 1. Load Context
```bash
python3 /home/workspace/N5/scripts/thought_provoker_scan_v2.py --days 30
python3 /home/workspace/N5/scripts/thought_provoker_patterns.py
```

### 2. Select Provocation
Choose ONE of these modes:

**Mode A: Fresh Challenge**
- Pick the most provocative idea from a recent meeting
- Frame it as a question that challenges V's current position
- Example: "In your meeting with [X], you suggested [Y]. But doesn't that contradict [Z]?"

**Mode B: Pattern Probe**
- Surface a recurring theme from `thought_patterns.json`
- Ask: "This theme keeps appearing ({N} meetings). What's the deeper thesis you're circling?"

**Mode C: Evolution Track**
- Show how V's position on a topic has shifted over time
- Ask: "In September you said X, in November you said Y. What changed?"

### 3. Socratic Engagement
- Ask probing questions, not leading ones
- Push back on easy answers
- Demand specificity: "Can you give me a concrete example?"
- Use the "5 Whys" technique to get to root beliefs
- Challenge with: "What would change your mind on this?"

### 4. Crystallization
When V reaches a sharp position:
1. Summarize the position in 1-2 sentences
2. Ask: "Is this publishable? Would you stake your reputation on this?"
3. If yes, capture it:

```bash
python3 /home/workspace/N5/scripts/fodder_collector.py --type position --title "TITLE" --content "POSITION"
```

If unresolved tension remains:
```bash
python3 /home/workspace/N5/scripts/fodder_collector.py --type contradiction --title "TITLE" --content "TENSION"
```

## Output Destinations

- **Positions**: `Lists/content-fodder.jsonl` — Ready for content generation
- **Unresolved**: `Lists/unresolved-contradictions.jsonl` — Future session material

## Example Session Start

"V, in your call with Jatin last week, you talked about the 'Invisible 70%' — the idea that the real talent market is hidden from standard signals. But in three earlier meetings, you emphasized 'signal density' and filtering for visible markers of quality. 

**Which is it?** Are you building a system to find hidden gems, or a system to efficiently sort visible signals? These feel like different companies."

---

*This prompt uses meeting intelligence from B32 blocks. Run the scan scripts to refresh data before each session.*


