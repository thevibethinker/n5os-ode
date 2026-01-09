---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
type: build_plan
status: in_progress
provenance: con_nRtJ8573Bwl836An
---

# Plan: Second-Order Adjacency Finder

## Objective
Find small (1K-5K followers) but high-engagement accounts that orbit V's power mutuals.
These are accounts that would be impressed by V's mutual connections and likely to follow back.

## The Logic
```
Power mutuals (66K-414K) post tweets
         ↓
Small aspiring accounts (1K-5K) reply/engage
         ↓
We identify and monitor THOSE accounts
         ↓
V engages with their content
         ↓
They check V's profile → see impressive mutuals → follow
```

## Checklist

### Phase 1: Engager Discovery
- ☐ Create `src/adjacency_finder.py`
- ☐ Fetch recent tweets from power mutuals
- ☐ Find who replies to those tweets (via search `to:username`)
- ☐ Extract unique repliers with user IDs
- ☐ Test: Get 50+ unique engagers from power mutual tweets

### Phase 2: Clout Score Calculation  
- ☐ Look up public_metrics for each engager
- ☐ Calculate clout_score = avg_engagement_per_tweet / followers
- ☐ Filter: 1K-5K followers AND clout_score > threshold
- ☐ Store in `adjacency_candidates` table with scores
- ☐ Test: Identify 20+ high-clout small accounts

### Phase 3: Integration
- ☐ Add CLI to review and approve candidates
- ☐ Promote approved candidates to `monitored_accounts`
- ☐ Add to scheduled agent for daily refresh
- ☐ Test: End-to-end pipeline surfaces new targets

## Affected Files
- `Projects/x-thought-leader/src/adjacency_finder.py` — CREATE
- `Projects/x-thought-leader/db/tweets.db` — ADD `adjacency_candidates` table

## Success Criteria
- Daily discovery of 10-20 new high-clout small accounts
- V can review/approve in batches
- Approved accounts feed into reply generator pipeline

