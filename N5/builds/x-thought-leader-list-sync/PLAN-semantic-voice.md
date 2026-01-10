---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.1
type: build_plan
status: complete
provenance: con_vjh0ymLPzQ0xgJzO
---

# Plan: X Thought Leader — Semantic Gate + Real Voice Model

**Objective:** Remove keyword-based Stage 1 filtering; send ALL tweets to semantic LLM gate. Replace generic voice prompt with two-stage transformation approach using V's actual tweets.

**Status: ✅ COMPLETE**

## Completion Summary

**Phase 1 - Semantic Gate:** ✅ Complete
- Removed ~100 keyword filter (STAGE1_KEYWORDS)
- All tweets now go to LLM with "Would V engage?" prompt
- Basic hygiene only: retweets, <30 chars, >72h old
- Added `--reset` command for reprocessing

**Phase 2 - Voice Model Extraction:** ✅ Complete
- Extracted patterns from 516 tweets in DuckDB
- Documented: em-dash pivots, asterisk actions, profanity-as-punctuation
- Created transformation pairs (neutral → V voice)

**Phase 3 - Two-Stage Transformation:** ✅ Complete
- Stage 1: Generate NEUTRAL insight (what to say)
- Stage 2: Transform to V's voice (how to say it)
- Allows iteration on neutral before transformation
- Uses Zo's /zo/ask API (not OpenRouter)
- Added `--iterate` command to re-transform existing neutrals

**Phase 4 - Integration Test:** ✅ Complete
- Full pipeline working: gate → neutral → transform
- Sample output quality verified (authentic V voice)

---

## Checklist

### Phase 1: Semantic Gate Rewrite
- [x] Remove `STAGE1_KEYWORDS` dict
- [x] Remove `stage1_heuristic()` function
- [x] Keep only basic hygiene (retweets, min length, max age)
- [x] Route ALL hygiene-passing tweets to LLM
- [x] Update gate prompt: "Would V have something interesting to say?"
- [x] Test: process 10 tweets, verify no keyword rejection

### Phase 2: Voice Model Extraction
- [x] Query DuckDB: top-performing original tweets
- [x] Query DuckDB: high-engagement replies
- [x] Create `voice_model.py` with extracted patterns
- [x] Document rhetorical patterns

### Phase 3: Reply Generator Update
- [x] Import voice model into `reply_generator.py`
- [x] Replace `V_VOICE_PROMPT` with real exemplars
- [x] Update prompt template to use extracted patterns
- [x] Test: generate 3 replies, verify authentic voice

### Phase 4: Integration Test
- [x] Reset 10 tweets for reprocessing
- [x] Run semantic gate
- [x] Generate reply drafts for passed tweets
- [x] Verify full pipeline works

---

## Phase 1: Semantic Gate Rewrite

### Affected Files
- `Projects/x-thought-leader/src/relevance_gate.py` — REWRITE core logic

### Design

**Current (broken):**
```
Stage 1: Keyword filter (STAGE1_KEYWORDS dict) → 80% rejected
Stage 2: LLM correlation → only sees 20% of tweets
```

**New (semantic-first):**
```
ALL tweets → LLM semantic gate → "Would V engage?"
No keyword filtering. Cost is acceptable per V's direction.
```

**Semantic Gate Prompt:**
```
You are evaluating whether V (@thevibethinker) would have something interesting to say about this tweet.

V's engagement profile:
- Founder of Careerspan (AI-powered hiring)
- Deep interest in: hiring/talent markets, AI/automation philosophy, epistemology, founder journey, future of work
- Engages when: he can add a non-obvious angle, reframe the conversation, or share genuine insight
- DOESN'T engage with: pure news, memes without substance, promotional spam, hot takes without depth

Tweet: "{tweet_text}" by @{author}

Question: Would V have something genuinely interesting to contribute to this conversation?

Score 0.0-1.0:
- 0.0-0.3: No clear angle for V
- 0.4-0.6: Tangentially relevant, might engage if slow day
- 0.7-1.0: V would definitely have something to say

Respond with JSON: {"score": X.X, "reasoning": "brief explanation"}
```

### Changes to relevance_gate.py

1. **Remove:** `STAGE1_KEYWORDS` dict (lines 36-100+)
2. **Remove:** `stage1_heuristic()` function
3. **Keep:** Basic filters only: is_retweet, min_length (>30 chars), not spam
4. **Rewrite:** `process_tweet()` to call LLM for ALL tweets that pass basic filters
5. **Update:** `gate_stage` always = 2 (semantic)

### Unit Tests
- No tweets rejected for keyword mismatch
- Tweets about "hiring AI" score >0.7
- Tweets about "my breakfast" score <0.3
- Retweets still filtered (basic hygiene, not semantic)

---

## Phase 2: Voice Model Extraction

### Affected Files
- `Projects/x-thought-leader/src/voice_extractor.py` — CREATE
- `Projects/x-thought-leader/config/v_voice_model.yaml` — CREATE

### Design

**Data source:** `/home/workspace/x-history-pre-jan-8/data.duckdb`
- Table: `tweets`
- Column: `full_text`
- Filter: `is_retweet = 0` (original tweets only)
- Count: ~516 tweets

**Extraction dimensions:**

1. **Sentence structure**
   - Average sentence length
   - Use of em-dashes, parentheticals
   - Question frequency
   - Thread vs. single-tweet ratio

2. **Vocabulary patterns**
   - Recurring phrases ("case in point", "toxic trait", etc.)
   - Technical vs. casual register balance
   - Hashtag usage patterns
   - @mention patterns

3. **Rhetorical devices**
   - Analogies and reframes
   - Wit/wordplay frequency
   - Contrarian framing
   - Direct address patterns

4. **Content themes**
   - Topic clustering (Zo, Careerspan, social commentary, etc.)
   - Emotional tone distribution

**Output format (v_voice_model.yaml):**
```yaml
voice_model:
  version: 1.0
  generated_from: x-history-pre-jan-8/data.duckdb
  tweet_count: 516
  
  structure:
    avg_sentence_length: X words
    uses_em_dashes: true
    uses_parentheticals: true
    question_frequency: X%
    
  vocabulary:
    recurring_phrases:
      - "case in point"
      - "toxic trait"
      - "the millennial urge to"
      # ... extracted from corpus
    
    avoids:
      - excessive emojis
      - "great point!"
      - generic praise
      
  rhetorical_devices:
    - analogies (frequent)
    - reframes ("you're not X, you're Y")
    - wit/wordplay
    - contrarian angles
    
  top_examples:  # 50 highest-engagement original tweets
    - text: "..."
      engagement: X
    # ...
```

### Unit Tests
- `voice_extractor.py --analyze` produces valid YAML
- Top examples are sorted by engagement
- Recurring phrases appear 3+ times in corpus

---

## Phase 3: Reply Generator Update

### Affected Files
- `Projects/x-thought-leader/src/reply_generator.py` — UPDATE voice prompt

### Design

**Current V_VOICE_PROMPT (lines 39-58):**
```python
V_VOICE_PROMPT = """You are helping V (@thevibethinker) write Twitter replies.

V's voice characteristics:
- Founder of Careerspan (AI-powered hiring)
- Thoughtful, not hot-take-bro
...
```

**Problem:** Generic bullet points, not learned from actual tweets.

**New approach:**
1. Load `config/v_voice_model.yaml` at startup
2. Include 10-20 highest-engagement V tweets as few-shot examples
3. Dynamically reference extracted patterns in prompt
4. Use actual recurring phrases as style markers

**New V_VOICE_PROMPT structure:**
```python
def build_voice_prompt():
    model = load_voice_model()
    examples = model['top_examples'][:15]
    
    return f"""You are helping V (@thevibethinker) write Twitter replies.

V's ACTUAL voice (learned from {model['tweet_count']} real tweets):

Structure patterns:
- {model['structure']['description']}

Recurring phrases V uses:
{format_phrases(model['vocabulary']['recurring_phrases'][:10])}

V NEVER:
{format_list(model['vocabulary']['avoids'])}

Examples of V's real tweets (study his voice):
{format_examples(examples)}

Now write a reply in V's voice. Match his rhythm, wit, and substance.
"""
```

### Unit Tests
- Voice prompt includes real V tweet examples
- Generated replies don't contain phrases in `avoids` list
- Character count under 280 by default

---

## Phase 4: Integration Test

### Test Protocol

1. **Semantic gate capture rate:**
   ```bash
   # Before: ~5% pass with keywords
   # Target: 30-50% pass with semantic gate
   python3 src/relevance_gate.py --process --limit 50
   sqlite3 db/tweets.db "SELECT COUNT(*) as passed FROM tweets WHERE gate_passed = 1"
   ```

2. **Reply quality (manual review):**
   ```bash
   python3 src/reply_generator.py --generate --limit 5
   python3 src/reply_generator.py --pending
   # V reviews: Do these sound like me?
   ```

3. **Full pipeline:**
   ```bash
   python3 src/polling_agent.py --once
   # Check: tweets collected → semantic gate → drafts generated
   ```

### Success Criteria
- Semantic gate passes 30-50% of tweets (vs. current ~5%)
- 80%+ of generated replies "sound like V" (manual review)
- No crashes or errors in full pipeline run
- Processing time <10s per tweet (LLM call acceptable)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| LLM cost increase (all tweets → LLM) | V explicitly approved: "fuck the cost" |
| Voice extraction misses V's style | Include raw examples as few-shot; iterate |
| Over-fitting to past tweets | Include position context for current views |
| Slow processing (LLM for every tweet) | Batch processing; async where possible |

---

## Execution Order

1. **Phase 1 first** — unblocks pipeline; stops keyword rejection
2. **Phase 2** — extract voice model (can run in parallel with Phase 1 test)
3. **Phase 3** — update generator with voice model
4. **Phase 4** — integration test

**Estimated effort:** 1-2 hours Builder time.

---

## Handoff

Plan created. Builder can now execute Phase 1 → Phase 4 in sequence.



