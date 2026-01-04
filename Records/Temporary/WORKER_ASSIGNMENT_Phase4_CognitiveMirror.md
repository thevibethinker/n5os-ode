---
created: 2026-01-04
last_edited: 2026-01-04
version: 1
provenance: con_uXZfAchvpXYIevBj
---
# Worker Assignment: Phase 4 — Cognitive Mirror

## Context

Build: `N5/builds/context-graph/`
Plan: `file 'N5/builds/context-graph/PLAN.md'` (lines 474-580)
Status: `file 'N5/builds/context-graph/STATUS.md'`

**Starting conditions:**
- 95 active edges in `edges.db`
- Phases 1-3 complete
- edge_query.py works for data retrieval

## Scope

Create 5 LLM-powered cognitive mirror scripts that:
1. Query edges.db for relevant data
2. Pass to LLM via `/zo/ask` API for semantic reasoning
3. Output dated Markdown reports to `N5/insights/cognitive_mirror/`

## Deliverables

| Script | Purpose | Output |
|--------|---------|--------|
| `_base.py` | Shared infrastructure | Helper functions |
| `decision_retrospective.py` | "Did what I hoped/feared happen?" | Prediction review |
| `reversal_detector.py` | "Where am I inconsistent?" | Flip-flop analysis |
| `influence_map.py` | "Who shapes my thinking?" | Influence breakdown |
| `originated_vs_adopted.py` | "Do my ideas stick better?" | Origination analysis |
| `decay_detector.py` | "What have I abandoned?" | Stale edge review |

## Implementation Pattern

```python
# Each script follows this pattern:

import sys
sys.path.insert(0, "/home/workspace/N5/scripts")
from cognitive_mirror._base import query_edges, ask_zo, write_report

def main():
    # 1. Query relevant edges
    edges = query_edges("""
        SELECT * FROM edges 
        WHERE relation IN ('hoped_for', 'concerned_about')
        AND status = 'active'
        AND extracted_at < datetime('now', '-90 days')
    """)
    
    if not edges:
        print("No edges match criteria")
        return
    
    # 2. Build context for LLM
    context = format_edges_for_llm(edges)
    
    # 3. Ask LLM for semantic analysis
    prompt = """
    Analyze these predictions V made 90+ days ago...
    [detailed prompt with output format]
    """
    
    analysis = ask_zo(prompt, context)
    
    # 4. Write dated report
    report_path = write_report("decision_retrospective", analysis)
    print(f"Report written: {report_path}")

if __name__ == "__main__":
    main()
```

## _base.py Functions

```python
def query_edges(sql: str) -> list[dict]:
    """Execute SQL against edges.db, return list of dicts."""

def ask_zo(prompt: str, context: str) -> str:
    """Call /zo/ask API, return response text."""

def write_report(script_name: str, content: str) -> Path:
    """Write to N5/insights/cognitive_mirror/YYYY-MM-DD_{script_name}.md"""
    
def format_edges_table(edges: list[dict]) -> str:
    """Format edges as readable table for LLM context."""
```

## Prompts (Embedded in Scripts)

### decision_retrospective.py prompt:
```
You are analyzing V's past predictions to identify patterns in his forecasting accuracy.

Given these edges representing V's hopes and concerns from meetings over 90 days ago:

{edges_table}

For each prediction:
1. Identify if an outcome was linked (validated/invalidated)
2. For those without outcomes, assess if they're still open or implicitly resolved

Then synthesize:
- Which predictions need V to explicitly close the loop?
- What patterns exist in prediction accuracy?
- Are there domains where V is consistently over/under-optimistic?

Output as Markdown with sections: ## Predictions Needing Closure, ## Patterns Observed, ## Recommendations
```

### reversal_detector.py prompt:
```
You are analyzing V's intellectual consistency to help him understand his thinking evolution.

These edges were marked 'superseded' or 'reversed':

{edges_table}

Cluster these by semantic topic. For each cluster:
1. Is this healthy evolution (new information, growth) or concerning pattern (indecision)?
2. What triggered the reversal if evident?

Output as Markdown with sections: ## Healthy Pivots, ## Concerning Patterns, ## Domain Stability Analysis
```

### influence_map.py prompt:
```
You are mapping who shapes V's thinking across different domains.

These edges show idea origination and influence:

{edges_table}

Analyze:
1. Who are V's top intellectual influences (by ideas adopted)?
2. Who effectively challenges V (challenged_by edges)?
3. Are there echo chambers (same people, no challengers)?
4. Which perspectives might be underrepresented?

Output as Markdown with sections: ## Top Influencers, ## Effective Challengers, ## Echo Chamber Risk, ## Underutilized Perspectives
```

### originated_vs_adopted.py prompt:
```
You are comparing V's originated ideas vs ideas he adopted from others.

These edges show idea origins:

{edges_table}

Analyze:
1. What % of V's active ideas originated from him vs others?
2. Which category has better "survival rate" (still active vs superseded/reversed)?
3. Are there domain differences (e.g., V's product ideas stick, but GTM ideas from others stick better)?

Output as Markdown with sections: ## Origination Breakdown, ## Survival Analysis, ## Domain Comparison, ## Strategic Implications
```

### decay_detector.py prompt:
```
You are identifying abandoned ideas/decisions that were never explicitly closed.

These edges haven't been touched in 90+ days:

{edges_table}

For each:
1. Is this still relevant (should be revived)?
2. Is this implicitly dead (should be formally closed)?
3. What type of ideas does V tend to abandon?

Output as Markdown with sections: ## Candidates for Revival, ## Candidates for Closure, ## Abandonment Patterns, ## Recommendations
```

## Success Criteria

1. All 5 scripts run without error on current edge data
2. Each produces a dated Markdown report
3. Reports contain substantive semantic analysis (not just data regurgitation)
4. Empty result sets handled gracefully

## Handoff

After completion:
1. Update STATUS.md Phase 4 checkmarks
2. Run each script once to produce initial reports
3. Return to Operator with summary

---

**Assigned to:** Builder
**Estimated time:** 1.5-2 hours

