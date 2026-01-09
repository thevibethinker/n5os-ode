---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
type: build_plan
status: complete
provenance: con_nRtJ8573Bwl836An
---

# Plan: X Thought Leader — List-as-SSOT Monitoring + SMS Alerts

**Objective:** Replace YAML-based account curation with a single X List as SSOT; add two-stage relevance filtering and SMS alerting for high-correlation tweets.

**Trigger:** V wants to scale monitored accounts from 10 → 60–200 while maintaining 5–6 high-quality engagement opportunities per day. Current 10-account setup yields <1 relevant tweet/day. Manual YAML curation is friction; X List is a native, on-the-fly curation surface.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

<!-- All resolved via deterministic probes -->
- [x] Can bearer token read public list members? **YES** — probe confirmed `GET /2/lists/:id/members` works
- [x] Can bearer token read list tweets? **YES** — probe confirmed `GET /2/lists/:id/tweets` works
- [x] What is the list ID? **1703516711629054447** ("Curated opinions")
- [x] Where should alerts go? **SMS via `send_sms_to_user`** — V confirmed "being texted ASAP"

---

## Alternatives Considered (Nemawashi)

### Alternative A: Keep YAML as SSOT, add CLI helper
- **Pros:** No new API integration; simple
- **Cons:** Still requires manual file editing; friction remains; no on-the-fly curation from X mobile app
- **Verdict:** ❌ Rejected — doesn't solve the core UX problem

### Alternative B: X List as SSOT (SELECTED)
- **Pros:** Native X UX; add/remove from mobile; automatic sync; no file editing
- **Cons:** Depends on X API availability; public list required for app-only auth
- **Verdict:** ✅ Selected — best UX, V already made list public

### Alternative C: Bookmarks as trigger
- **Pros:** Even more lightweight
- **Cons:** Bookmarks API requires OAuth2 user context (more complex auth); bookmarks are for content, not people
- **Verdict:** ❌ Rejected — wrong abstraction (content vs accounts)

---

## Trap Doors 🚨

| Decision | Reversibility | Mitigation |
|----------|---------------|------------|
| Deprecating YAML as SSOT | Medium | Keep YAML as fallback; add `--source yaml` flag to polling_agent |
| SMS alerting for every high-correlation tweet | Low (spam risk) | Two-stage gate + daily cap (max 8 SMS/day) + quiet hours |
| Public list requirement | High | Can revert to private + add X_API_SECRET for OAuth1 later |

---

## Checklist

### Phase 1: List Sync Module
- ☑ Create `src/list_sync.py` with `sync_from_list(list_id)` function
- ☑ Add `get_list_members()` and `get_list_info()` to `x_api.py`
- ☑ Update `monitored_accounts` table schema (add `source` column)
- ☑ Test: Sync list → DB, verify 3 current members appear

### Phase 2: Integrate List Sync into Polling Agent
- ☑ Modify `polling_agent.py` to call list sync before YAML sync
- ☑ Add `--list-id` CLI flag (default: V's list)
- ☑ Add config constant `DEFAULT_LIST_ID`
- ☑ Test: Run polling agent, confirm it syncs from list first

### Phase 3: Two-Stage Relevance Gate
- ☑ Create `src/relevance_gate.py` with cheap heuristic filter (stage 1)
- ☑ Add LLM correlation call (stage 2) for tweets passing stage 1
- ☑ Store relevance scores in `tweets` table (`gate_stage`, `gate_passed`, `gate_reason`)
- ☑ Test: Process 50 sample tweets, ~70% Stage 1 rejection rate confirmed

### Phase 4: SMS Alert Integration
- ☑ Create `src/alert_dispatcher.py` with SMS routing logic
- ☑ Add daily cap tracking (max 8/day) and quiet hours (10pm–8am ET)
- ☑ Integrate with `send_sms_to_user` via `/zo/ask` API
- ☑ Test: Trigger test alert, SMS delivery confirmed

---

## Phase 1: List Sync Module

### Affected Files
- `Projects/x-thought-leader/src/list_sync.py` — CREATE — X List → DB sync module
- `Projects/x-thought-leader/src/x_api.py` — UPDATE — add list endpoints
- `Projects/x-thought-leader/db/tweets.db` — UPDATE — add `source` column to `monitored_accounts`

### Changes

**1.1 Add list endpoints to x_api.py:**
```python
def get_list_info(list_id: str) -> dict | None:
    """Get list metadata (name, description, member_count)."""
    # GET /2/lists/:id
    # Returns: {id, name, description, member_count, ...}

def get_list_members(list_id: str, max_results: int = 100) -> list[dict]:
    """Get all members of a list with pagination."""
    # GET /2/lists/:id/members
    # user.fields: id,username,name,description,public_metrics
    # Handle pagination via next_token
```

**1.2 Create list_sync.py:**
```python
def sync_from_list(list_id: str, dry_run: bool = False) -> dict:
    """
    Sync X list members to monitored_accounts table.
    
    - Fetches all members from list
    - Adds new members to DB (source='list')
    - Marks members removed from list as inactive (soft delete)
    - Returns stats: {added: [], removed: [], unchanged: []}
    """
```

**1.3 Schema migration — add source column:**
```sql
ALTER TABLE monitored_accounts ADD COLUMN source TEXT DEFAULT 'yaml';
-- Values: 'yaml', 'list', 'manual'
```

### Unit Tests
- `sync_from_list('1703516711629054447')` returns stats with 3 members (LuisvonAhn, asanwal, ordinarytings)
- Running sync twice is idempotent (second run: added=[], unchanged=[3])
- Members in DB but not in list are marked inactive, not deleted

---

## Phase 2: Integrate List Sync into Polling Agent

### Affected Files
- `Projects/x-thought-leader/src/polling_agent.py` — UPDATE — add list sync call
- `Projects/x-thought-leader/config/settings.py` — CREATE — centralized config constants

### Changes

**2.1 Create config/settings.py:**
```python
# X Thought Leader Configuration
DEFAULT_LIST_ID = '1703516711629054447'  # V's "Curated opinions" list
POLLING_INTERVAL_MINUTES = 15
APPROVAL_HOURS = (8, 22)  # 8am-10pm ET
MAX_SMS_PER_DAY = 8
QUIET_HOURS = (22, 8)  # 10pm-8am ET (no SMS)
```

**2.2 Update polling_agent.py:**
- Import `sync_from_list` from `list_sync`
- Before `sync_accounts()` (YAML sync), call `sync_from_list(DEFAULT_LIST_ID)`
- Add `--list-id` flag to override default
- Add `--skip-yaml` flag to skip YAML sync entirely (list-only mode)

### Unit Tests
- `python polling_agent.py --list-accounts` shows members from list
- `python polling_agent.py --dry-run` logs "Syncing from list..." before "Syncing from YAML..."
- Accounts from list have `source='list'` in DB

---

## Phase 3: Two-Stage Relevance Gate

### Affected Files
- `Projects/x-thought-leader/src/relevance_gate.py` — CREATE — two-stage filter
- `Projects/x-thought-leader/db/tweets.db` — UPDATE — add relevance columns to tweets table
- `Projects/x-thought-leader/src/polling_agent.py` — UPDATE — call gate after storing tweets

### Changes

**3.1 Schema migration — add relevance columns:**
```sql
ALTER TABLE tweets ADD COLUMN relevance_score REAL;  -- 0.0-1.0
ALTER TABLE tweets ADD COLUMN gate_stage INTEGER;    -- 1=heuristic, 2=llm
ALTER TABLE tweets ADD COLUMN gate_passed INTEGER DEFAULT 0;  -- 0/1
ALTER TABLE tweets ADD COLUMN gate_reason TEXT;      -- why passed/failed
```

**3.2 Create relevance_gate.py:**
```python
# Stage 1: Cheap heuristic filter (runs on ALL tweets)
def stage1_heuristic(tweet: dict) -> tuple[bool, str]:
    """
    Fast filter based on:
    - Keyword presence (hiring, talent, AI, career, recruiting, founder)
    - Not a retweet (unless quote tweet with commentary)
    - Not a reply (unless to monitored account)
    - Minimum length (>50 chars)
    - Recency (<24h)
    
    Returns: (passed: bool, reason: str)
    """

# Stage 2: LLM correlation (runs on Stage 1 passes only)
def stage2_llm_correlation(tweet: dict, positions: list[dict]) -> tuple[float, str]:
    """
    Uses existing correlator.py logic or calls /zo/ask.
    Checks correlation with V's positions from positions.db.
    
    Returns: (score: 0.0-1.0, explanation: str)
    Threshold for alert: score >= 0.7
    """

def process_tweet(tweet_id: str) -> dict:
    """
    Run tweet through both stages, update DB, return result.
    """
```

**3.3 Integration point:**
- After `store_tweet()` in polling_agent, call `process_tweet(tweet_id)`
- Only tweets with `gate_passed=1` AND `relevance_score >= 0.7` trigger alerts

### Unit Tests
- Stage 1 rejects retweets (RT @...) with reason "retweet"
- Stage 1 rejects tweets <50 chars with reason "too_short"
- Stage 2 returns score >0.7 for tweet about "hiring in AI" (matches V's positions)
- Stage 2 returns score <0.3 for tweet about unrelated topic

---

## Phase 4: SMS Alert Integration

### Affected Files
- `Projects/x-thought-leader/src/alert_dispatcher.py` — CREATE — SMS routing + rate limiting
- `Projects/x-thought-leader/db/tweets.db` — UPDATE — add alerts table
- `Projects/x-thought-leader/src/polling_agent.py` — UPDATE — call dispatcher after gate

### Changes

**4.1 Schema — create alerts table:**
```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_id TEXT NOT NULL,
    alert_type TEXT DEFAULT 'sms',  -- 'sms', 'approval_queue', 'email'
    sent_at TEXT,
    status TEXT DEFAULT 'pending',  -- 'pending', 'sent', 'rate_limited', 'quiet_hours'
    FOREIGN KEY (tweet_id) REFERENCES tweets(id)
);

CREATE INDEX idx_alerts_sent_at ON alerts(sent_at);
```

**4.2 Create alert_dispatcher.py:**
```python
from datetime import datetime
import pytz

ET = pytz.timezone('America/New_York')
MAX_SMS_PER_DAY = 8
QUIET_HOURS = (22, 8)  # 10pm-8am ET

def get_sms_count_today() -> int:
    """Count SMS alerts sent today (ET)."""

def is_quiet_hours() -> bool:
    """Check if current time is in quiet hours (10pm-8am ET)."""

def can_send_sms() -> tuple[bool, str]:
    """
    Check if SMS can be sent now.
    Returns: (can_send: bool, reason: str)
    """

def dispatch_alert(tweet_id: str, tweet_text: str, author: str, relevance_score: float) -> dict:
    """
    Dispatch alert for high-relevance tweet.
    
    1. Check rate limits and quiet hours
    2. If can send: format SMS and send via send_sms_to_user
    3. Always add to approval_queue for web review
    4. Log to alerts table
    
    SMS format:
    "🎯 High-relevance tweet from @{author} (score: {score:.0%})
    
    {tweet_text[:200]}
    
    Reply or queue: [link]"
    """

def send_sms(message: str) -> bool:
    """
    Send SMS using Zo's send_sms_to_user.
    Implementation: subprocess call or /zo/ask API.
    """
```

**4.3 Integration:**
- In polling_agent, after `process_tweet()`:
  - If `gate_passed=1` AND `relevance_score >= 0.7`:
    - Call `dispatch_alert(tweet_id, ...)`

### Unit Tests
- `can_send_sms()` returns `(False, 'quiet_hours')` at 11pm ET
- `can_send_sms()` returns `(False, 'rate_limited')` after 8 SMS in a day
- `dispatch_alert()` creates record in alerts table even when rate limited
- SMS message is <160 chars or properly chunked

---

## Success Criteria

1. **List sync works:** Running `python list_sync.py --list-id 1703516711629054447` syncs all list members to DB
2. **Polling uses list:** `python polling_agent.py --list-accounts` shows accounts from X list (not just YAML)
3. **Relevance gate filters:** Of 100 tweets polled, <20% pass Stage 1, <5% pass Stage 2
4. **SMS alerts fire:** High-relevance tweet (score ≥0.7) triggers SMS within 2 minutes of polling
5. **Rate limits work:** 9th high-relevance tweet in a day goes to queue only, no SMS
6. **Quiet hours work:** High-relevance tweet at 11pm ET goes to queue only, no SMS

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| X API rate limits (Basic tier: 10K tweets/month read) | Batch polling, 15-min intervals, prioritize high-value accounts |
| SMS spam if relevance gate too permissive | Conservative Stage 1 keywords + 0.7 threshold + daily cap |
| List becomes private accidentally | Graceful fallback to YAML; log warning |
| LLM correlation is slow/expensive | Cache position embeddings; batch Stage 2 calls |
| V adds 200 accounts, overwhelms system | Start with 60 account target; monitor before scaling |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
*(To be filled after Level Upper review)*

1. _
2. _

### Incorporated:
- _

### Rejected (with rationale):
- _

---

## Handoff

**When ready for execution:**
1. V confirms plan is acceptable
2. V adds `X_API_SECRET` to secrets (for future OAuth1 if needed, not blocking)
3. Switch to Builder: `set_active_persona("567cc602-060b-4251-91e7-40be591b9bc3")`
4. Builder executes Phase 1, then Phase 2, etc.

**Estimated effort:** 2–3 hours of Builder time across 4 phases.




