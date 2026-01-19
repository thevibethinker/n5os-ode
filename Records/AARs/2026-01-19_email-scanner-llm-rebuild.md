---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_0Xb0KBQbQVoVAIgF
type: aar
build_slug: email-llm-scanner
---

# After-Action Report: Email Scanner LLM Rebuild

**Date:** 2026-01-19  
**Duration:** ~45 minutes  
**Outcome:** ✅ Success  

## Mission

Fix the email backfill agent that was failing to find deal signals. The original agent reported "0 signals found" even though V had definitely communicated with tracked contacts (e.g., Vir from Instalily) in the 60-day window.

## What Happened

### The Problem

The original email deal scanner used Python scripts to generate exact-match Gmail queries:
- `"Jennifer Ives" after:2025/12/20`
- `"Vir" after:2025/12/20`

This approach failed catastrophically because:
1. **Missing emails in DB** — Many contacts had no email stored, so couldn't search `from:email@domain.com`
2. **Exact name matching** — Gmail search for `"Vir"` doesn't find emails from `vir@instalily.ai`
3. **No semantic understanding** — Regex can't recognize that "Vir" and "vir@instalily.ai" are the same person

### The Fix

Built an LLM-powered email scanner using the build orchestrator pattern:

| Worker | Deliverable |
|--------|-------------|
| **W1.1** | `get_broad_email_queries()` — date-filtered queries excluding promo/social |
| **W1.1** | `should_analyze_email()` — pre-filter with exclusion patterns |
| **W1.1** | `build_llm_context()` — retrieves 50 contacts + 30 deals for matching |
| **W1.2** | `EMAIL_ANALYSIS_PROMPT` — semantic email analysis with `match_reasoning` field |
| **W2.1** | `update_contact_email()` — enriches contacts with discovered emails |
| **W2.1** | `format_email_for_llm()` + `process_email_with_llm_analysis()` — integration |

### Key Insight

**Zo IS the LLM.** The semantic analysis doesn't require external API calls — the agent instruction tells Zo to analyze each email using the prompt logic. This is the bridge between "LLM does the thinking" and "scripts do the mechanics."

## Decisions Made

1. **Broad queries + LLM analysis** (vs. targeted regex queries)
   - Rationale: Cast wide net, let LLM filter semantically
   
2. **Contact email enrichment during scan** (vs. separate enrichment process)
   - Rationale: If we match "Vir" to `vir@instalily.ai`, store the email immediately
   
3. **Self-destructing agent** (vs. permanent agent)
   - Rationale: Backfill is finite (60 days), agent should clean up after itself

## Artifacts

- `file 'N5/scripts/email_deal_scanner.py'` — Updated with new functions
- `file 'N5/scripts/deal_llm_prompts.py'` — Added EMAIL_ANALYSIS_PROMPT
- `file 'N5/builds/email-llm-scanner/'` — Build folder with worker briefs and completions
- Agent `c4c7c14d-a561-43dc-afd3-e635fc90c35b` — New backfill agent (runs daily 2 AM)

## Lessons Learned

1. **Regex is the wrong tool for semantic matching.** When the task is "does this email relate to a known contact," that's fundamentally a semantic question. LLMs are built for this.

2. **Build orchestrator works.** Three workers in two waves, clean completions, atomic commit at end. The pattern scales.

3. **"Zo is the LLM" is a design principle.** Instead of calling external APIs, write instructions that leverage Zo's native capabilities. The agent instruction is essentially a prompt for the agent execution.

## Open Items

- Monitor first backfill run (2026-01-20 02:00 AM) to verify it finds signals correctly
- May need to tune pre-filter patterns based on actual inbox noise levels
- Consider extending to daily ongoing scan (not just backfill) after validation

## Tags

#n5 #email #deal-intelligence #build #llm #semantic-analysis
