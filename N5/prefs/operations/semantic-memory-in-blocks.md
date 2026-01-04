# Semantic Memory Integration Guide for Block Generation

**Version:** 1.0
**Created:** 2026-01-03
**Purpose:** Best practices for using semantic memory in meeting block generation

---

## Overview

Block generators MUST use semantic memory to provide historical context. This enables:
- Relationship trajectory tracking (not every meeting is "first contact")
- Credibility weighting (trust insights based on source track record)
- Pattern detection (recurring themes, concerns, resonance)
- Deduplication (don't re-introduce people already in network)

---

## Memory Client API

```python
from N5.cognition.n5_memory_client import N5MemoryClient
client = N5MemoryClient()
```

### Named Profiles

| Profile | Path Prefixes | Use Case |
|---------|---------------|----------|
| `crm` | N5/crm_v3/profiles/, Knowledge/crm/ | Stakeholder profiles, relationship history |
| `meetings` | Personal/Meetings/, N5/digests/ | Prior meeting content, B-blocks |
| `wellness` | Personal/Health/ | Fitbit data, health protocols |
| `voice-guides` | N5/prefs/communication/ | Communication style patterns |
| `capabilities` | N5/capabilities/, Prompts/ | V's skills, prompt library |
| `content-library` | Knowledge/content-library/ | Links, resources, assets |
| `system-architecture` | Documents/System/, N5/docs/ | System design docs |

### Core Methods

```python
# Scoped search (recommended)
results = client.search_profile(
    profile="crm",
    query="Jane Smith Acme Corp",
    limit=5
)

# Full search with filters
results = client.search(
    query="partnership discussion",
    metadata_filters={"path": ("contains", "B08")},
    limit=10
)
```

---

## Block-Specific Memory Patterns

### B08: Stakeholder Intelligence

**Load:**
1. CRM profile for stakeholder (prior relationship)
2. Prior meetings with stakeholder
3. Prior B08 blocks (domain authority evolution)

**Use for:**
- Relationship trajectory (Warming/Stable/Cooling/New)
- Domain authority baseline
- Recurring resonance topics

```python
crm = client.search_profile("crm", f"{name} {org}", limit=3)
meetings = client.search_profile("meetings", f"{name}", limit=5)
prior_b08s = client.search(
    query=f"{name} B08",
    metadata_filters={"path": ("contains", "B08")},
    limit=3
)
```

### B31: Stakeholder Research

**Load:**
1. Prior B08 domain authority (credibility weighting)
2. Prior B31 insights from this stakeholder (avoid duplicates)

**Use for:**
- Credibility scoring per domain
- Deduplication of insights
- Track record validation

```python
b08 = client.search_profile("meetings", f"{name} B08 domain authority", limit=3)
prior_insights = client.search(
    query=f"{name} insight",
    metadata_filters={"path": ("contains", "B31")},
    limit=10
)
```

### B07: Warm Introductions

**Load:**
1. CRM profile for intro TARGET (deduplication)
2. Meeting history with target (prior contact check)

**Use for:**
- Flag if target already in network
- Note existing relationship depth
- Avoid duplicate introductions

```python
for target in intro_targets:
    existing = client.search_profile("crm", f"{target}", limit=3)
    prior = client.search_profile("meetings", f"{target}", limit=5)
    if existing or prior:
        # Flag: "Already in network"
```

### B27: Wellness Indicators

**Load:**
1. Prior B27 blocks (baseline metrics)
2. Wellness profile (biometric data)
3. Recent stress/energy patterns

**Use for:**
- Trend comparison (↑/↓/→)
- Cumulative stress detection
- Baseline deviation alerts

```python
prior_b27 = client.search_profile("meetings", "B27 wellness", limit=10)
health = client.search_profile("wellness", "heart rate sleep energy", limit=5)
recent = client.search(
    query="stress pressure deadline energy",
    metadata_filters={"path": ("contains", "B27")},
    limit=5
)
```

### B10: Relationship Trajectory

**Load:**
1. All prior meetings with stakeholder
2. CRM profile history

**Use for:**
- Meeting count and frequency
- Relationship stage progression
- Trust signal evolution

```python
all_meetings = client.search_profile("meetings", f"{name}", limit=20)
crm = client.search_profile("crm", f"{name} {org}", limit=1)
```

---

## Orchestration: Meeting Process Prompt

The Meeting Process prompt (v5.3.0+) includes Step 2b: Semantic Memory Enrichment.

**Flow:**
1. Step 2a: Classify complexity (BRIEF/STANDARD/DEEP)
2. Step 2b: Load semantic memory context
3. Step 3: Select blocks to generate
4. Step 4: Generate blocks WITH enrichment context

**Enrichment Context Object:**
```json
{
  "prior_relationship": {
    "exists": true,
    "meetings_count": 3,
    "last_meeting": "2025-10-14",
    "relationship_depth": "warm",
    "crm_profile_path": "Knowledge/crm/individuals/jane-smith.md"
  },
  "historical_signals": {
    "prior_resonance_topics": ["AI-first coaching", "enterprise"],
    "prior_concerns": ["integration complexity"],
    "relationship_trajectory": "warming"
  },
  "context_for_blocks": {
    "B08": "Load prior B08 to compare stakeholder evolution",
    "B10": "Use meeting_history for trajectory assessment",
    "B07": "Check CRM for intro target existence",
    "B27": "Compare wellness metrics to baseline"
  }
}
```

---

## Skip Conditions

Skip semantic memory enrichment when:
- **Internal meeting** (no external stakeholder)
- **First-ever contact** (no prior history exists - note in B10)
- **Memory client unavailable** (fallback to transcript-only)
- **BRIEF meeting** with no stakeholder intelligence blocks

---

## Anti-Patterns

❌ **Generating blocks without memory lookup**
- Every B08, B07, B27, B31 should check for prior context

❌ **Treating every meeting as first contact**
- Always note meeting count and relationship trajectory

❌ **Hardcoding credibility scores without track record**
- B31 insights should reference B08 domain authority

❌ **Missing deduplication checks**
- B07 intros should verify target not already in CRM

❌ **Analyzing in isolation**
- B27 wellness should compare to baseline, not just current state

---

## Implementation Checklist for New Block Generators

When creating a new block generator prompt:

- [ ] Add `semantic-memory` tag to frontmatter
- [ ] Include "Semantic Memory Context (Load First)" section
- [ ] Show specific `search_profile()` queries
- [ ] Document what context is used for
- [ ] Add `semantic_enrichment: true` to output frontmatter
- [ ] Include "⭐ MEMORY-ENRICHED" markers on enriched sections
- [ ] Add anti-patterns section warning against isolated analysis
- [ ] Update version number

---

## Related Documentation

- `/home/workspace/N5/cognition/n5_memory_client.py` - Memory client implementation
- `/home/workspace/Prompts/Meeting Process.prompt.md` - Orchestration (Step 2b)
- `/home/workspace/N5/prefs/operations/crm-usage.md` - CRM policy
- `/home/workspace/N5/prefs/system/persona_routing_contract.md` - Memory mandate

---

**Maintained by:** Vibe Architect
**Last Updated:** 2026-01-03
