---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
type: build_plan
status: ready_for_build
---

# Plan: Careerspan Sales Prospecting Engine

**Objective:** Build a system that surfaces recruiters discussing problems Careerspan solves, enabling V to engage constructively and warm them into sales conversations.

**Trigger:** V wants to leverage X for Careerspan pipeline generation — not cold DMs, but strategic engagement with recruiters who are actively discussing relevant pain points.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

<!-- Surface unknowns HERE at the TOP. Resolve before proceeding. -->
- [x] **X API tier**: Basic tier ($100/mo, 10K tweets/mo search)
- [x] **Careerspan value props**: Confirmed — candidate quality, sourcing efficiency, visibility, talent network
- [x] **Volume target**: 5 qualified prospects/day
- [x] **ICP**: NYC and SF based/focused recruiters (agency or in-house)
- [x] **Separate system or TLE extension?**: Separate project, shared x_api.py

---

## Architecture Decision: Nemawashi

### Option A: Extend X Thought Leadership Engine
- **Pros**: Reuse existing infra, single codebase
- **Cons**: Conflates personal brand (contrarian) with sales (constructive); different target audiences; muddies the TLE's purpose

### Option B: Separate System, Shared Utilities (RECOMMENDED)
- **Pros**: Clean separation of concerns; can evolve independently; different engagement philosophy
- **Cons**: Some code duplication
- **Approach**: New project `Projects/careerspan-prospector/`, imports `x_api.py` from TLE

### Option C: External Tool (PhantomBuster, Tweet Hunter)
- **Pros**: More powerful search/scraping
- **Cons**: Additional cost ($50-200/mo), vendor lock-in, less control
- **Verdict**: Consider as Phase 2 enhancement if X API search proves insufficient

**Recommendation: Option B** — Clean separation, shared API wrapper, purpose-built for sales.

---

## Trap Doors (Irreversible Decisions)

| Decision | Reversibility | Notes |
|----------|---------------|-------|
| Database schema | 🟡 Medium | Can migrate but painful; design carefully |
| X API tier upgrade | 🟢 Easy | Can upgrade/downgrade monthly |
| External tool integration | 🟢 Easy | Can add later if needed |

---

## Checklist

### Phase 1: Foundation & Topic Monitoring
- ☐ Create project structure at `Projects/careerspan-prospector/`
- ☐ Create SQLite database with prospects, tweets, engagements tables
- ☐ Create `topic_monitor.py` — searches X for recruiting pain point keywords
- ☐ Create `careerspan_value_props.yaml` — defines what problems CS solves
- ☐ Test: Run topic search, verify tweets captured

### Phase 2: Prospect Qualification & Pipeline
- ☐ Create `prospect_qualifier.py` — scores tweets for recruiter-ness and fit
- ☐ Create `prospect_pipeline.py` — manages prospect states (discovered → engaged → responded)
- ☐ Create CLI interface for V to review prospects
- ☐ Test: End-to-end flow from search → qualified prospect in pipeline

### Phase 3: Engagement Suggestions
- ☐ Create `engagement_suggester.py` — generates constructive reply angles
- ☐ Create `Prompts/Careerspan Prospect Review.prompt.md` — V's interface
- ☐ Wire up to Zo's interface for daily review
- ☐ Test: Generate suggestions for 5 prospects, V reviews quality

---

## Phase 1: Foundation & Topic Monitoring

### Affected Files
- `Projects/careerspan-prospector/` - CREATE - new project directory
- `Projects/careerspan-prospector/db/prospector.db` - CREATE - SQLite database
- `Projects/careerspan-prospector/src/topic_monitor.py` - CREATE - X search wrapper
- `Projects/careerspan-prospector/src/x_api.py` - SYMLINK - from TLE
- `Projects/careerspan-prospector/config/value_props.yaml` - CREATE - Careerspan pain points
- `Projects/careerspan-prospector/config/search_queries.yaml` - CREATE - keyword sets to monitor

### Changes

**1.1 Project Structure:**
```
Projects/careerspan-prospector/
├── src/
│   ├── topic_monitor.py      # Searches X for relevant conversations
│   ├── x_api.py              # Symlinked from TLE
│   └── __init__.py
├── db/
│   └── prospector.db         # SQLite: prospects, tweets, engagements
├── config/
│   ├── value_props.yaml      # Careerspan's pain point vocabulary
│   └── search_queries.yaml   # Search keyword combinations
└── README.md
```

**1.2 Database Schema:**
```sql
-- Tweets we've captured from topic searches
CREATE TABLE tweets (
    id TEXT PRIMARY KEY,              -- X tweet ID
    content TEXT NOT NULL,
    author_id TEXT NOT NULL,
    author_username TEXT NOT NULL,
    author_name TEXT,
    author_bio TEXT,
    created_at TEXT,
    search_query TEXT,                -- Which query found this
    relevance_score REAL,             -- LLM-scored relevance to CS
    recruiter_signal REAL,            -- Likelihood author is recruiter
    captured_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Prospects (authors we're tracking)
CREATE TABLE prospects (
    id TEXT PRIMARY KEY,              -- X user ID
    username TEXT NOT NULL UNIQUE,
    name TEXT,
    bio TEXT,
    follower_count INTEGER,
    tweet_count INTEGER,
    status TEXT DEFAULT 'discovered', -- discovered, qualified, engaged, responded, converted
    fit_score REAL,                   -- Overall fit for Careerspan
    notes TEXT,                       -- V's notes
    discovered_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_interaction TEXT
);

-- Engagement tracking
CREATE TABLE engagements (
    id TEXT PRIMARY KEY,
    prospect_id TEXT REFERENCES prospects(id),
    tweet_id TEXT REFERENCES tweets(id),
    engagement_type TEXT,             -- reply, like, retweet, dm
    content TEXT,                     -- What V said
    status TEXT DEFAULT 'pending',    -- pending, sent, replied
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**1.3 Topic Monitor:**
- Imports `x_api.py` from TLE (symlink)
- Loads search queries from `config/search_queries.yaml`
- Runs searches, dedupes, stores in `tweets` table
- Initial query set (V to refine):
  - "recruiter sourcing candidates"
  - "talent acquisition challenge"
  - "hiring pipeline"
  - "candidate quality"
  - "recruiting struggle"

**1.4 Value Props Config:**
```yaml
# config/value_props.yaml
careerspan_solves:
  - name: "candidate_quality"
    description: "Finding high-quality, motivated candidates"
    keywords: ["candidate quality", "bad applicants", "unqualified", "ghosting"]
    
  - name: "sourcing_efficiency"
    description: "Time spent sourcing vs. evaluating"
    keywords: ["sourcing time", "finding candidates", "where to find"]
    
  - name: "visibility"
    description: "Getting job posts seen by right candidates"
    keywords: ["job visibility", "applicant volume", "no applications"]
    
  - name: "talent_network"
    description: "Building pipeline vs. posting and praying"
    keywords: ["talent pool", "pipeline", "proactive recruiting"]

icp_filters:
  geo_focus:
    - "NYC"
    - "New York"
    - "SF"
    - "San Francisco"
    - "Bay Area"
  bio_signals:
    - "recruiter"
    - "talent acquisition"
    - "TA"
    - "hiring"
    - "HR"
    - "headhunter"
    - "sourcer"
```

### Unit Tests
- `python3 topic_monitor.py --dry-run`: Shows what queries would run, doesn't hit API
- `python3 topic_monitor.py --run --limit 10`: Captures 10 tweets, verify in DB
- `sqlite3 db/prospector.db "SELECT COUNT(*) FROM tweets"`: Confirms data stored

---

## Phase 2: Prospect Qualification & Pipeline

### Affected Files
- `Projects/careerspan-prospector/src/prospect_qualifier.py` - CREATE - scores prospects
- `Projects/careerspan-prospector/src/prospect_pipeline.py` - CREATE - state management
- `Projects/careerspan-prospector/src/cli.py` - CREATE - V's interface

### Changes

**2.1 Prospect Qualifier:**
- For each new tweet, extracts author info via X API
- Scores "recruiter-ness" based on:
  - Bio keywords (recruiter, talent, hiring, HR, TA)
  - Tweet content patterns
  - Account characteristics (B2B-ish follower count)
- Scores "fit" based on value prop alignment
- Uses LLM for nuanced scoring (via Zo API)

**2.2 Pipeline Manager:**
- State machine: `discovered` → `qualified` → `engaged` → `responded` → `converted`
- V can move prospects through stages
- Tracks interaction history

**2.3 CLI Interface:**
```bash
# View today's discoveries
python3 cli.py queue

# View a specific prospect
python3 cli.py prospect @username

# Mark as engaged
python3 cli.py engage @username --note "Replied to their sourcing tweet"

# Skip a prospect
python3 cli.py skip @username --reason "Enterprise TA, not our ICP"
```

### Unit Tests
- `python3 prospect_qualifier.py --test`: Score 3 sample tweets, verify reasonable scores
- `python3 cli.py queue`: Shows pending prospects with context
- `python3 cli.py prospect @test --status qualified`: State transition works

---

## Phase 3: Engagement Suggestions

### Affected Files
- `Projects/careerspan-prospector/src/engagement_suggester.py` - CREATE - generates angles
- `Prompts/Careerspan Prospect Review.prompt.md` - CREATE - V's daily interface

### Changes

**3.1 Engagement Suggester:**
- Different from TLE's contrarian approach
- Generates constructive angles:
  - "Agree and add value" — affirm their pain, offer insight
  - "Share resource" — relevant content without being salesy
  - "Ask curious question" — genuine engagement, learn more
- Does NOT auto-draft tweets (V writes final copy)
- Outputs: tweet context + 2-3 angle suggestions + Careerspan connection

**3.2 Daily Review Prompt:**
```markdown
# Careerspan Prospect Review

Surfaces today's qualified prospects for V to engage.

## Workflow
1. Run `python3 Projects/careerspan-prospector/src/cli.py queue`
2. For each prospect, show:
   - Their tweet + context
   - Their bio/background
   - Suggested engagement angles
   - Careerspan value prop connection
3. V decides: engage, skip, or save for later
```

### Unit Tests
- Generate engagement suggestions for 5 prospects
- V reviews quality: Are angles constructive? Non-salesy? Authentic?

---

## Success Criteria

1. **Daily surfacing**: System surfaces 5-10 qualified prospects per day
2. **Quality filter**: >70% of surfaced prospects are actual recruiters
3. **Engagement rate**: V engages with >50% of qualified prospects (not skipping most)
4. **Pipeline movement**: At least 2 prospects/week move to "responded" status
5. **Time efficiency**: Daily review takes <15 minutes

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| X API rate limits block volume | Start conservative (50 searches/day), upgrade tier if needed |
| Low recruiter signal in search results | Refine search queries iteratively; consider adding external list |
| Engagement feels salesy | Strict "constructive only" guidelines; V reviews all before sending |
| Too many false positives | Tune qualifier thresholds; add manual skip feedback loop |

---

## Level Upper Review

<!-- To be completed before Builder handoff -->

### Counterintuitive Suggestions to Solicit:
1. What if we inverted the approach — instead of finding recruiters, find candidates complaining about recruiters and work backwards?
2. What if the "engagement" is actually building in public about Careerspan's approach, and letting recruiters come to us?
3. What if we prioritized quality over volume — 1 perfect prospect/day vs. 10 mediocre ones?

### Incorporated:
- TBD after Level Upper review

### Rejected (with rationale):
- TBD after Level Upper review

---

## Next Steps

1. ~~V to answer open questions~~ ✓ DONE
2. Architect quick divergent check (below)
3. **Hand off to Builder** for Phase 1 execution



