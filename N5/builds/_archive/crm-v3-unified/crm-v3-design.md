# CRM Unified Architecture V3 (FINAL)
## Webhook-Triggered, Queue-Based, AI-Queryable Intelligence System

**Designed:** 2025-11-17  
**Version:** 3.0 FINAL  
**For:** V @ Careerspan  
**Status:** ✅ Architecture Complete - Ready for Implementation

---

## Architecture Overview

### Core Paradigm
**Reactive cleanup → Proactive multi-source enrichment with real-time triggers**

### Key Design Principles
1. **AI-queryable, not human-greppable** - Data exists, AI retrieves on demand
2. **SQLite queue for reliability** - Small but needs concurrent access + priority reordering
3. **Email replies as intent signals** - V's responses = CRM-worthy contacts
4. **Spam exclusion patterns** - Filter hostile/dismissive responses
5. **3-day advance enrichment** - Friday enrichment for Monday meetings

---

## System Architecture

### Data Flow

```
INBOUND SOURCES → ENTITY DETECTION → DEDUPLICATION → ENRICHMENT QUEUE → ENRICHMENT → PROFILE
```

### Five Inbound Sources

#### 1. Google Calendar Webhook (Primary)
**Trigger:** Event created/updated with attendees
**Flow:**
```
Webhook received → Extract attendee emails → Entity dedup → Create profiles → Queue enrichment (3 days before)
```

**Webhook Config:**
- Real-time push notifications for calendar events
- Webhook renewal every 7 days (auto-managed)
- Fallback polling every 6 hours for reconciliation
- Health monitoring with SMS alerts on failure

#### 2. Email Reply Tracking (Intent Signal)
**Trigger:** V sends reply to thread
**Flow:**
```
Gmail webhook → Detect V's reply → Extract recipient email → Spam filter check → Entity dedup → Queue enrichment (low priority)
```

**Spam Exclusion Patterns:**
- Message contains: "fuck off", "unsubscribe", "stop emailing", "remove me", "not interested"
- Thread marked as spam in Gmail
- Recipient domain in spam blocklist (stored in config)
- Short message (<20 chars) + hostile tone detected via LLM

**Implementation:**
- Gmail push notifications for sent emails
- Pattern matching + LLM tone analysis
- Exclusion list stored in `crm_v2_config.yaml`

#### 3. Meeting Transcripts (B08 Blocks)
**Trigger:** Meeting processed, B08 strategic intelligence extracted
**Flow:**
```
Meeting transcript → B08 extraction → Entity detection → Dedup → Append intelligence to existing profiles
```

**Does NOT create new profiles** - only enriches existing ones

#### 4. Voice Memos (Networking Events)
**Trigger:** V uploads voice memo saying "Met [names] at [event]"
**Flow:**
```
Voice memo → Transcription → Entity extraction → Speaker diarization → Create profiles → Queue enrichment
```

**Example:**
> "Just left Web Summit. Met Sarah Chen from Stripe, Marcus from Y Combinator, and that founder Alex who's building the HR tool."

**Processing:**
- Extract: Sarah Chen (Stripe), Marcus (Y Combinator), Alex (HR tool founder, name ambiguous)
- Create 3 profiles with partial info
- Queue for enrichment
- Flag "Alex" for manual disambiguation

#### 5. Manual Entry (CLI/Chat)
**Trigger:** V says "Add [name] to CRM" or uses CLI
**Flow:**
```
Manual command → Parse name/email/context → Create profile → Queue enrichment (high priority)
```

---

## Core Database Schema

### 1. Profiles Table (Canonical Records)

```sql
CREATE TABLE profiles (
    id TEXT PRIMARY KEY,  -- UUID
    email TEXT UNIQUE,    -- Primary identifier (nullable initially)
    name TEXT NOT NULL,
    company TEXT,
    role TEXT,
    linkedin_url TEXT,
    category TEXT,        -- ADVISOR | INVESTOR | COMMUNITY | NETWORKING | OTHER
    
    -- State tracking
    quality_state TEXT DEFAULT 'DISCOVERED',  -- DISCOVERED | STUB | ENRICHED | STALE
    last_enriched_at TEXT,
    stale_after_days INTEGER DEFAULT 180,
    
    -- Metadata
    created_at TEXT NOT NULL,
    created_from_source TEXT,  -- calendar | email_reply | transcript | voice_memo | manual
    last_updated_at TEXT,
    profile_file_path TEXT,    -- /home/workspace/Knowledge/crm/individuals/{slug}.md
    
    -- Relationships
    last_meeting_date TEXT,
    next_meeting_date TEXT,
    total_meetings INTEGER DEFAULT 0,
    total_email_threads INTEGER DEFAULT 0
);

CREATE INDEX idx_email ON profiles(email);
CREATE INDEX idx_quality_state ON profiles(quality_state);
CREATE INDEX idx_next_meeting ON profiles(next_meeting_date);
```

### 2. Enrichment Queue (Dynamic Priority Queue)

```sql
CREATE TABLE enrichment_queue (
    id TEXT PRIMARY KEY,              -- UUID
    profile_id TEXT NOT NULL,         -- FK to profiles.id
    
    -- Scheduling
    priority INTEGER NOT NULL,        -- 0-100 (higher = sooner)
    scheduled_for TEXT NOT NULL,      -- ISO timestamp
    checkpoint_type TEXT,             -- 'initial' | 'pre_meeting' | 'morning_of' | 'manual'
    
    -- State machine
    status TEXT DEFAULT 'QUEUED',     -- QUEUED | IN_PROGRESS | COMPLETED | FAILED | CANCELLED
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    last_attempt_at TEXT,
    error_message TEXT,
    
    -- Context
    trigger_source TEXT,              -- 'calendar' | 'email_reply' | 'manual' | 'staleness'
    meeting_id TEXT,                  -- If triggered by upcoming meeting
    notes TEXT,                       -- Additional context for enrichment
    
    -- Metadata
    created_at TEXT NOT NULL,
    updated_at TEXT,
    
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_queue_priority ON enrichment_queue(status, priority DESC, scheduled_for);
CREATE INDEX idx_queue_profile ON enrichment_queue(profile_id);
CREATE INDEX idx_queue_meeting ON enrichment_queue(meeting_id);
```

**Priority Levels:**
- **100:** Today's meeting (morning-of checkpoint)
- **90:** Tomorrow's meeting
- **80:** 2-3 days out (pre-meeting checkpoint)
- **50:** New profile from calendar (initial enrichment, 3 days before meeting)
- **30:** Email reply tracking (low priority background)
- **10:** Staleness refresh (last enriched >180 days ago)

**Queue Dynamics:**
- Priorities can change dynamically (meeting moved up → priority increases)
- AI can reorder queue by updating priority field
- Background worker processes highest priority first
- Concurrent enrichments limited to 3 to avoid rate limits

### 3. Email Threads Table

```sql
CREATE TABLE email_threads (
    id TEXT PRIMARY KEY,              -- Gmail thread ID
    profile_id TEXT NOT NULL,         -- FK to profiles.id
    subject TEXT,
    snippet TEXT,
    last_message_date TEXT,
    participant_emails TEXT,          -- JSON array
    message_count INTEGER,
    is_v_participant BOOLEAN,
    thread_url TEXT,
    
    created_at TEXT NOT NULL,
    
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_thread_profile ON email_threads(profile_id);
CREATE INDEX idx_thread_date ON email_threads(last_message_date);
```

### 4. Calendar Events Table

```sql
CREATE TABLE calendar_events (
    id TEXT PRIMARY KEY,              -- Google Calendar event ID
    summary TEXT,
    start_time TEXT NOT NULL,
    end_time TEXT,
    attendee_emails TEXT,             -- JSON array
    location TEXT,
    description TEXT,
    
    -- Webhook tracking
    webhook_received_at TEXT,
    last_updated_at TEXT,
    
    created_at TEXT NOT NULL
);

CREATE INDEX idx_event_start ON calendar_events(start_time);
```

### 5. Webhook Health Table

```sql
CREATE TABLE webhook_health (
    id INTEGER PRIMARY KEY,
    service TEXT UNIQUE NOT NULL,     -- 'google_calendar' | 'gmail_sent'
    channel_id TEXT,
    resource_id TEXT,
    expiration_time TEXT,
    last_renewal_at TEXT,
    last_received_at TEXT,
    status TEXT DEFAULT 'ACTIVE',     -- ACTIVE | EXPIRED | FAILED
    
    updated_at TEXT
);
```

---

## Profile File Format (Hybrid YAML + MD)

**Location:** `/home/workspace/Knowledge/crm/individuals/{name-slug}.md`

### Structure: AI-Queryable, Not Human-Greppable

```yaml
---
# Core Facts Section (LLM-editable for corrections)
core_facts:
  name: Alex Caveny
  email: alex.caveny@gmail.com
  company: Wisdom Partners
  role: Founder Advisor/Coach
  linkedin_url: https://linkedin.com/in/alexcaveny
  location: San Francisco, CA
  category: ADVISOR
  status: Active Advisor
  
# Metadata (System-managed)
metadata:
  created_at: 2024-11-14T10:00:00Z
  last_enriched_at: 2024-11-17T08:00:00Z
  quality_state: ENRICHED
  total_meetings: 4
  total_email_threads: 12
  
# Intelligence Log (Append-only, immutable)
intelligence_log:
  - timestamp: 2024-11-10T19:30:00Z
    source: meeting_transcript
    meeting_id: mtg_abc123
    confidence: high
    content: |
      Uses "task bankruptcy" framework - legitimizes dropping commitments as 
      "strategic debt relief" not failure. Shows sophisticated reframing ability.
      
  - timestamp: 2024-11-15T10:00:00Z
    source: aviato_enrichment
    confidence: high
    content: |
      LinkedIn: 2,400+ connections. Previously PM at Google (2018-2020). 
      Founded Wisdom Partners in 2021. Active in Ukrainian tech community.
      
  - timestamp: 2024-11-17T08:00:00Z
    source: gmail_search
    confidence: medium
    content: |
      Email thread from 2024-10-15: Offered intro to Sarah Guo (Conviction VC). 
      Quote: "Happy to connect you, just send me context on why you'd like to meet her."
      Shows generosity with intros but expects specificity.
      
  - timestamp: 2024-11-17T08:05:00Z
    source: linkedin_activity
    confidence: low
    content: |
      Recent post about founder mental health (2024-11-10). Aligns with burnout 
      prevention focus. 150+ likes, engagement from SF tech community.

# Meeting Brief (Generated morning-of)
meeting_brief:
  generated_at: 2024-11-18T07:00:00Z
  next_meeting: 2024-11-18T14:00:00Z
  
  key_points:
    - Last met 19 days ago (2024-10-30)
    - Discussed burnout prevention frameworks
    - Pending: Intro request to Sarah Guo (sent context 2024-11-12, no response yet)
    - Recent email (2024-11-16): Asked about Q1 2025 advisory schedule
    
  suggested_topics:
    - Follow up on Sarah Guo intro
    - Discuss Q1 advisory cadence
    - Ask about recent founder mental health post
    
  recent_emails: |
    Thread 1: "Q1 2025 Advisory Schedule" (2024-11-16, 3 messages)
    Thread 2: "Intro Request - Sarah Guo" (2024-11-12, 2 messages, awaiting reply)
    Thread 3: "Task Bankruptcy Framework Follow-up" (2024-11-05, 5 messages)
---

# Alex Caveny

*AI-queryable profile. Ask about Alex anytime - system will retrieve and synthesize.*
```

**Key Design Choices:**

1. **No Human Greppability Required**
   - As long as data exists, AI can query on demand
   - LLM reads YAML, extracts relevant intelligence, synthesizes answer
   - No need for markdown prose or structured sections

2. **Append-Only Intelligence Log**
   - New insights appended with timestamp, source, confidence
   - Never edited - avoids LLM document editing issues
   - Grows chronologically, creating intelligence timeline

3. **Meeting Brief Generated Daily**
   - Morning-of enrichment checkpoint generates brief
   - Synthesizes recent activity, pending items, suggested topics
   - Emailed to V at 7 AM

---

## Enrichment Pipeline

### Worker Process (Background Daemon)

```python
async def enrichment_worker():
    """
    Continuously processes enrichment queue.
    Runs as background service, checks queue every 60 seconds.
    """
    while True:
        job = await fetch_next_job()  # Highest priority, scheduled_for <= now
        
        if not job:
            await asyncio.sleep(60)
            continue
        
        try:
            await process_enrichment(job)
        except Exception as e:
            await handle_failure(job, e)
        
        await asyncio.sleep(5)  # Brief pause between jobs

async def process_enrichment(job):
    """
    Multi-source enrichment:
    1. Aviato API (professional info)
    2. Gmail search (email threads, last 90 days)
    3. LinkedIn activity (if manual scraping approved)
    4. Synthesize intelligence via LLM
    5. Append to profile intelligence log
    6. Update quality_state
    """
    profile = await get_profile(job.profile_id)
    
    # 1. Aviato enrichment
    aviato_data = await aviato_enrich(profile.email)
    
    # 2. Gmail search (3-4 recent threads)
    threads = await gmail_search(profile.email, limit=4, days=90)
    
    # 3. LLM synthesis
    intelligence = await llm_synthesize(aviato_data, threads, profile.name)
    
    # 4. Append to intelligence log
    await append_intelligence(profile.id, intelligence, source="aviato_gmail_enrichment")
    
    # 5. Update state
    await update_profile_state(profile.id, quality_state="ENRICHED", last_enriched_at=now())
    
    # 6. Mark job complete
    await complete_job(job.id)
```

### Enrichment Sources

#### 1. Aviato API
**Endpoint:** (To be researched)  
**Input:** Email address  
**Output:** Professional info (name, company, role, LinkedIn, etc.)  
**Rate Limits:** (To be researched)  
**Error Handling:** Exponential backoff, cache results

#### 2. Gmail Search
**API:** Google Gmail API (already connected)  
**Query:** 
```python
query = f"from:{email} OR to:{email}"
max_results = 4
timeframe = "after:{90_days_ago}"
```

**Output:** 3-4 most recent threads  
**Processing:** LLM extracts key intelligence from thread snippets

#### 3. LinkedIn Activity (Optional)
**Status:** Legal gray area - manual scraping  
**If enabled:** Scrape recent posts, connections, activity  
**If disabled:** Skip this source  

---

## Two-Checkpoint Enrichment Strategy

### Checkpoint 1: Pre-Meeting (3 Days Before)
**Trigger:** Calendar event detected → enrichment queued for 3 days before  
**Purpose:** Full enrichment before meeting  
**Actions:**
1. Run Aviato enrichment
2. Search Gmail for recent threads
3. Synthesize intelligence via LLM
4. Append to profile intelligence log
5. Update quality_state to ENRICHED

**Example:**
- Monday meeting at 2 PM
- Friday at 2 PM: Full enrichment completes
- V has weekend to review if needed

### Checkpoint 2: Morning-Of (7 AM)
**Trigger:** Meeting day arrives → priority 100 job queued  
**Purpose:** Delta update + generate meeting brief  
**Actions:**
1. Check for new emails since last enrichment (delta)
2. Synthesize meeting brief (key points, suggested topics, recent activity)
3. Email meeting brief to V at 7 AM
4. Append brief to profile

**Example Meeting Brief Email:**

```
Subject: Meeting Brief: Alex Caveny @ 2 PM today

Hi V,

You're meeting Alex Caveny (Wisdom Partners) today at 2 PM.

KEY POINTS:
- Last met 19 days ago (2024-10-30)
- Discussed burnout prevention frameworks
- Pending: Intro request to Sarah Guo (awaiting response)

RECENT ACTIVITY:
- Emailed 2024-11-16 asking about Q1 2025 advisory schedule
- LinkedIn post about founder mental health (2024-11-10, 150+ likes)

SUGGESTED TOPICS:
- Follow up on Sarah Guo intro status
- Confirm Q1 advisory cadence
- Reference his recent mental health post

RECENT EMAILS (last 30 days):
1. "Q1 2025 Advisory Schedule" - 3 messages, most recent 2024-11-16
2. "Intro Request - Sarah Guo" - 2 messages, awaiting reply
3. "Task Bankruptcy Framework Follow-up" - 5 messages, 2024-11-05

Full profile: /home/workspace/Knowledge/crm/individuals/alex-caveny.md

-- Zo CRM
```

---

## Entity Deduplication System

### Problem
Multiple sources create duplicates:
- Calendar: "Alex Caveny" <alex.caveny@gmail.com>
- Transcript: "Alex C."
- Voice memo: "That founder Alex"
- Email: "alexander.caveny@gmail.com"

### Solution: Three-Tier Matching

#### Tier 1: Email Exact Match (Canonical)
```python
if email:
    existing = db.query("SELECT * FROM profiles WHERE email = ?", email)
    if existing:
        return existing.id  # Use existing profile
```

#### Tier 2: Name Fuzzy Match
```python
if not email:
    candidates = db.query("SELECT * FROM profiles WHERE similarity(name, ?) > 0.85", name)
    if len(candidates) == 1:
        return candidates[0].id
    elif len(candidates) > 1:
        # Ambiguous - send to manual review queue
        add_to_review_queue(name, candidates)
```

**Fuzzy matching:** Levenshtein distance, handles typos and variations

#### Tier 3: Manual Review Queue
```python
if ambiguous:
    # Store in review queue
    db.insert("manual_review_queue", {
        "input_name": "Alex",
        "input_context": "HR tool founder at Web Summit",
        "candidates": ["Alex Caveny", "Alex Zhang", "Alex Rodriguez"],
        "status": "PENDING"
    })
    
    # SMS V for clarification
    send_sms(f"Who is 'Alex' (HR tool founder)? Reply: 1=Caveny, 2=Zhang, 3=Rodriguez, 4=New person")
```

**Manual review triggers:**
- Multiple fuzzy matches (>2 candidates)
- No email + low confidence name match
- Transcript extraction with ambiguous names

---

## Email Reply Tracking & Spam Filtering

### Inbound: Gmail Sent Webhook

```python
async def handle_gmail_sent_webhook(message_data):
    """
    Triggered when V sends an email.
    Check if reply indicates CRM-worthy contact.
    """
    message = await gmail.get_message(message_data.id)
    
    # 1. Is this a reply? (has In-Reply-To header)
    if not message.is_reply:
        return
    
    # 2. Extract recipient
    recipient_email = message.to[0]  # Primary recipient
    
    # 3. Spam filter check
    if is_spam_response(message.body, message.subject):
        log_spam_exclusion(recipient_email, reason="hostile_response")
        return
    
    # 4. Entity deduplication
    profile_id = await find_or_create_profile(
        email=recipient_email,
        name=extract_name_from_email(message),
        source="email_reply"
    )
    
    # 5. Queue low-priority enrichment
    await queue_enrichment(
        profile_id=profile_id,
        priority=30,
        trigger_source="email_reply",
        scheduled_for=now() + timedelta(days=1)  # Next day, low priority
    )
```

### Spam Filter Logic

```python
def is_spam_response(body: str, subject: str) -> bool:
    """
    Returns True if message is hostile/dismissive spam response.
    """
    body_lower = body.lower()
    subject_lower = subject.lower()
    
    # Pattern matching
    hostile_patterns = [
        "fuck off", "fuck you", "piss off", "go away",
        "stop emailing", "unsubscribe", "remove me",
        "not interested", "don't contact", "leave me alone"
    ]
    
    for pattern in hostile_patterns:
        if pattern in body_lower or pattern in subject_lower:
            return True
    
    # Short + hostile tone (LLM check)
    if len(body) < 50:
        tone = await llm_analyze_tone(body)
        if tone in ["hostile", "dismissive", "angry"]:
            return True
    
    # Domain blocklist
    domain = extract_domain(recipient_email)
    if domain in load_spam_domains():
        return True
    
    return False
```

**Spam domain blocklist** (stored in `crm_v2_config.yaml`):
```yaml
spam_domains:
  - "spammer.com"
  - "marketing-blaster.io"
  # Add as discovered
```

---

## System Configuration

### File: `N5/config/crm_v2_config.yaml`

```yaml
# CRM V2 Configuration
version: 2.0
created: 2025-11-17

# Database paths
database:
  primary: /home/workspace/Knowledge/crm/crm_v2.db
  backup_dir: /home/workspace/N5/backups/databases/

# Profile storage
profiles:
  directory: /home/workspace/Knowledge/crm/individuals/
  naming_pattern: "{name-slug}.md"
  
# Enrichment settings
enrichment:
  checkpoint_1_days_before: 3
  checkpoint_2_time: "07:00"  # Morning-of at 7 AM
  staleness_threshold_days: 180
  max_concurrent: 3
  
  queue:
    max_attempts: 3
    retry_delay_minutes: 30
    timeout_minutes: 10
  
  sources:
    aviato:
      enabled: true
      api_key_env: AVIATO_API_KEY
      rate_limit_per_hour: 100  # TBD from docs
      
    gmail:
      enabled: true
      max_threads_per_search: 4
      search_timeframe_days: 90
      search_scope: all  # all | inbox | sent
      
    linkedin:
      enabled: false  # Legal gray area
      
# Email reply tracking
email_tracking:
  enabled: true
  spam_filter:
    enabled: true
    hostile_patterns:
      - "fuck off"
      - "fuck you"
      - "unsubscribe"
      - "stop emailing"
      - "remove me"
      - "not interested"
      - "don't contact"
    
    spam_domains:
      - "spammer.com"
      - "marketing-blaster.io"
    
    llm_tone_check:
      enabled: true
      threshold: 50  # chars - messages shorter than this get LLM tone analysis

# Webhooks
webhooks:
  google_calendar:
    enabled: true
    renewal_days: 7
    health_check_interval_hours: 6
    
  gmail_sent:
    enabled: true
    renewal_days: 7

# Entity deduplication
deduplication:
  email_match: exact  # Always trust email as canonical
  name_similarity_threshold: 0.85  # Levenshtein
  manual_review_sms: true

# Notifications
notifications:
  morning_brief:
    enabled: true
    time: "07:00"
    delivery: email  # email | sms | both
    
  enrichment_failures:
    enabled: true
    threshold: 3  # Alert after 3 failures
    delivery: sms
    
  webhook_health:
    enabled: true
    delivery: sms

# Categories
categories:
  - ADVISOR
  - INVESTOR
  - COMMUNITY
  - NETWORKING
  - CLIENT
  - PARTNER
  - OTHER
```

---

## Migration Strategy

### Phase 1: Database Setup (Week 1)
1. Create `crm_v2.db` with new schema
2. Write migration script to consolidate 3 existing systems:
   - `Knowledge/crm/crm.db` (57 profiles)
   - `N5/data/profiles.db` (44 profiles)
   - `N5/stakeholders/*.md` (12 profiles)
3. Deduplicate during migration (email exact → name fuzzy → manual review)
4. Generate YAML profile files in new format
5. Backup old systems to `N5/backups/pre_v2_migration/`

**Estimated:** ~70 unique profiles after deduplication

### Phase 2: Webhook Integration (Week 2)
1. Set up Google Calendar webhook
2. Set up Gmail sent webhook
3. Implement webhook health monitoring
4. Test event detection → profile creation → enrichment queuing

### Phase 3: Enrichment Pipeline (Week 2-3)
1. Research Aviato API (docs, rate limits, cost)
2. Implement enrichment worker (async background daemon)
3. Integrate Aviato API
4. Integrate Gmail search
5. Implement two-checkpoint system
6. Test full enrichment flow

### Phase 4: Multi-Source Ingestion (Week 3-4)
1. Meeting transcript integration (B08 → intelligence append)
2. Voice memo processing (transcription → entity extraction)
3. Email reply tracking
4. Manual entry CLI
5. Entity deduplication across all sources

### Phase 5: Intelligence Automation (Week 4+)
1. Morning meeting brief generation
2. Strategic intelligence extraction from transcripts
3. Email thread summarization
4. Profile staleness detection + refresh queuing
5. Monitoring & alerting

---

## Success Metrics

### System Health
- **Enrichment queue backlog:** <10 jobs at any time
- **Webhook uptime:** >99% (monitored, auto-renewed)
- **Enrichment success rate:** >95% (handle failures gracefully)
- **Entity dedup accuracy:** >98% (minimize false matches)

### User Experience
- **Pre-meeting brief delivery:** 100% on time (7 AM day-of)
- **Profile freshness:** <1% stale profiles (>180 days since enrichment)
- **Manual review queue:** <5 pending items at any time
- **SMS interruptions:** <2 per week (only critical clarifications)

### Data Quality
- **Profile completeness:** >90% have company, role, LinkedIn
- **Intelligence log growth:** ~2-3 entries per profile per quarter
- **Email thread coverage:** 80% of profiles have ≥1 thread indexed
- **Meeting coverage:** 100% of calendar meetings generate pre-meeting briefs

---

## Risk Mitigation

### Risk 1: Webhook Instability
**Mitigation:**
- Fallback polling every 6 hours
- Auto-renewal 2 days before expiration
- Health monitoring with SMS alerts
- Manual renewal CLI command

### Risk 2: Enrichment Queue Backup
**Mitigation:**
- Priority-based scheduling (today's meetings first)
- Concurrent enrichment limit (3 max)
- Timeout handling (10 min max per job)
- Manual queue inspection CLI

### Risk 3: Aviato API Failures
**Mitigation:**
- Exponential backoff on failures
- Cache enriched data (avoid re-enriching)
- Fallback to Gmail-only enrichment if Aviato down
- Alert after 3 consecutive failures

### Risk 4: Entity Duplication
**Mitigation:**
- Email exact match as canonical
- Fuzzy name matching (85% threshold)
- Manual review queue for ambiguous cases
- SMS clarifications when needed

### Risk 5: Profile Bloat
**Mitigation:**
- Archival strategy after 2 years no contact
- Intelligence log pruning (keep last 50 entries)
- Stale profiles marked but not deleted
- Manual cleanup CLI for bulk operations

---

## Open Questions (Resolved)

### ✅ Aviato API
**Action:** Look up docs during implementation  
**Status:** V confirmed docs exist, cost not a concern

### ✅ SMS Notifications
**Decision:** No SMS for general notifications  
**Use cases:** Only for critical alerts (webhook failures, manual review clarifications)

### ✅ Email Search Scope
**Decision:** Search all emails (work + personal), but primarily work-related  
**Rationale:** Occasional work emails end up in personal

### ✅ Voice Memo Format
**Assumption:** One memo listing multiple people  
**Example:** "Met Sarah, Marcus, and Alex at Web Summit"

### ✅ LinkedIn Integration
**Decision:** Disabled for now (legal gray area)  
**Revisit:** If manual scraping approved later

### ✅ Profile Archival
**Decision:** Mark stale after 180 days, don't delete  
**Archival:** After 2 years no contact, move to archive directory

---

## Implementation Timeline

### Week 1: Foundation
- [ ] Create `crm_v2.db` with schema
- [ ] Write migration script (3 systems → 1)
- [ ] Run deduplication (email exact → fuzzy → manual)
- [ ] Generate YAML profiles
- [ ] Backup old systems

### Week 2: Real-Time Integration
- [ ] Research Aviato API docs
- [ ] Set up Google Calendar webhook
- [ ] Set up Gmail sent webhook
- [ ] Implement webhook health monitoring
- [ ] Test event → profile → queue flow

### Week 2-3: Enrichment Engine
- [ ] Implement enrichment worker (async daemon)
- [ ] Integrate Aviato API
- [ ] Integrate Gmail search
- [ ] Implement two-checkpoint system
- [ ] Test full enrichment pipeline

### Week 3-4: Multi-Source Ingestion
- [ ] Meeting transcript integration (B08 append)
- [ ] Voice memo processing
- [ ] Email reply tracking + spam filter
- [ ] Manual entry CLI
- [ ] Entity dedup across sources

### Week 4+: Intelligence & Polish
- [ ] Morning meeting brief generation
- [ ] Strategic intelligence extraction (LLM)
- [ ] Email thread summarization
- [ ] Profile staleness detection
- [ ] Monitoring, alerting, cleanup tools

**Estimated Total:** 4-5 weeks for full system

---

## Design Principles Validated

✅ **AI-Queryable Over Human-Greppable** - Data exists, AI retrieves on demand  
✅ **SQLite for Reliability** - Small but needs concurrent access + queries  
✅ **Email Replies as Intent** - V's responses signal CRM-worthy contacts  
✅ **Spam Exclusion** - Filter hostile/dismissive responses  
✅ **3-Day Advance Enrichment** - Friday enrichment for Monday meetings  
✅ **P2: Single Source of Truth** - One profile per person  
✅ **P0.1: LLM-First** - Strategic intelligence via LLM extraction  
✅ **Simple Over Easy** - YAML + append-only is conceptually simple  
✅ **Flow Over Pools** - Calendar-first creates natural enrichment flow  
✅ **Code Is Free** - Invest in automation, save manual work forever  

---

## Architecture Status

**Version:** 3.0 FINAL ✅  
**Level Upper Enhanced:** ✅  
**V's Refinements Incorporated:** ✅  
**Ready for Implementation:** ✅  

**Deliverables:**
1. Complete database schema (5 tables)
2. Hybrid YAML profile format
3. Multi-source ingestion architecture
4. Two-checkpoint enrichment strategy
5. Entity deduplication system
6. Email reply tracking + spam filtering
7. Webhook integration design
8. Migration strategy
9. Success metrics + risk mitigation

**Next Steps:**
1. Begin Phase 1 implementation (database + migration)
2. Research Aviato API during Week 2
3. Progressive rollout over 4-5 weeks

---

**Architecture Complete. Ready to Build.**

---

*Designed by Vibe Architect + Level Upper*  
*Incorporating V's refinements: AI-queryable data, SQLite queue, email reply tracking, spam filtering, 3-day checkpoint*  
*2025-11-17 21:30 ET*  
*Conversation: con_RxzhtBdWYFsbQueb*

