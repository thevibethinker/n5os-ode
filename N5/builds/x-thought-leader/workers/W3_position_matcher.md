---
created: 2026-01-09
worker_id: W3
component: Position Correlation Engine
status: pending
---

# W3: Position Correlation Engine

## Objective
Match tweets against V's 105 positions using semantic similarity.

## Output Files
- `Projects/x-thought-leader/src/position_matcher.py`

## Source Database
`/home/workspace/N5/data/positions.db` - 105 positions

## Core Functions

```python
@dataclass
class PositionMatch:
    position_id: str
    title: str
    insight: str
    similarity_score: float

def match_tweet_to_positions(tweet_text: str, top_n: int = 5) -> list[PositionMatch]
```

## Matching Strategy
1. Check for pre-computed embeddings
2. If none, use LLM-based matching via Zo Ask API
3. Return top N matches above threshold (0.5)

## Acceptance Criteria
- [ ] Loads positions from DB
- [ ] Returns relevant matches for HR/hiring tweets
- [ ] Handles off-topic tweets gracefully
