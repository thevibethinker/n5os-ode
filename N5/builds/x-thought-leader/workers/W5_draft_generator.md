---
created: 2026-01-09
worker_id: W5
component: Draft Generator
status: pending
depends_on: [W3, W4]
---

# W5: Draft Generator

## Objective
Generate 4 draft tweet responses (one per variant) for high-correlation tweets.

## Output Files
- `Projects/x-thought-leader/src/draft_generator.py`

## Core Function

```python
@dataclass
class DraftSet:
    source_tweet_id: str
    source_tweet_text: str
    drafts: list[TweetDraft]  # 4 variants
    expires_at: str  # EOD

def generate_drafts(tweet_id: str, tweet_text: str, position_match: PositionMatch) -> DraftSet
```

## Generation Flow
1. Load voice variants from YAML
2. For each variant: build prompt, call Zo Ask API
3. Validate: length <=280, not generic
4. Store in DB

## Quality Checks
- Length: 50-280 chars
- Not generic ("Great point!", "So true!")
- References position naturally

## Acceptance Criteria
- [ ] Generates exactly 4 distinct drafts
- [ ] All under 280 chars
- [ ] Stored in database correctly
