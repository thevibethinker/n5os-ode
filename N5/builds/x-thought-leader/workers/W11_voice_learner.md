---
created: 2026-01-09
worker_id: W11
component: Voice Learner
status: pending
depends_on: [W9, W10]
---

# W11: Voice Learner

## Objective
Analyze V's posted tweets and historical archive to refine voice model over time.

## Output Files
- `Projects/x-thought-leader/src/voice_learner.py`
- `Projects/x-thought-leader/config/learned_voice.yaml`

## Learning Sources

1. **Historical tweets** (from archive) — baseline voice
2. **Posted tweets** (approved by V) — what V actually wants
3. **Skipped drafts** — what V rejected
4. **Refined drafts** — V's corrections show preferences

## Voice Features to Extract

```python
@dataclass
class VoiceFeatures:
    # Structural
    avg_length: int
    sentence_patterns: list[str]  # e.g., "question opener", "em-dash aside"
    punctuation_style: dict  # frequency of ..., —, !
    
    # Lexical
    favorite_words: list[str]  # frequently used
    avoided_words: list[str]   # never used
    jargon_level: str  # "none", "light", "heavy"
    
    # Tonal
    assertiveness: float  # 0-1
    humor_frequency: float
    emoji_usage: str  # "never", "rare", "moderate"
    
    # Engagement patterns
    preferred_hooks: list[str]
    closing_patterns: list[str]
```

## Core Functions

```python
def analyze_tweet_batch(tweets: list[str]) -> VoiceFeatures:
    """
    Extract voice features from a batch of tweets.
    Uses LLM for nuanced analysis.
    """

def compare_approved_vs_skipped(
    approved: list[dict],
    skipped: list[dict]
) -> dict:
    """
    What patterns distinguish approved from skipped?
    Returns preference signals.
    """

def update_voice_model(
    current_model: dict,
    new_signals: dict
) -> dict:
    """
    Incrementally update voice model with new learnings.
    Weight recent feedback higher.
    """

def generate_voice_report() -> str:
    """
    Human-readable report of learned voice patterns.
    For V to review and correct if needed.
    """
```

## Learning Loop

```
Weekly agent:
1. Gather all tweets posted this week
2. Gather all skipped/refined drafts
3. Extract patterns
4. Update learned_voice.yaml
5. Generate report for V (optional review)
```

## Integration with Draft Generator

W5 (Draft Generator) should load learned_voice.yaml and use it to:
- Adjust prompts for each variant
- Include learned favorite phrases
- Avoid patterns V consistently rejects

## Acceptance Criteria
- [ ] Extracts meaningful voice features from tweets
- [ ] Learns from approval/rejection patterns
- [ ] Updates voice model incrementally
- [ ] Generates human-readable reports
- [ ] Integrates with draft generation
