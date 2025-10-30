# Kondo-LinkedIn Intelligence System - Design Plan

**Status:** Planning Phase  
**Date:** 2025-10-30  
**Conversation:** con_4F5Rd2hAFRKgA6Tj

---

## THINK Phase

### What We're Building

A LinkedIn conversation intelligence system that:
1. Receives LinkedIn conversation data from Kondo webhooks
2. Stores conversations with thread distinction
3. Extracts commitments/promises automatically
4. Monitors response status and timing
5. Enriches existing CRM profiles with LinkedIn context
6. Enables chat-based querying of all above

### Integration Points (Existing Architecture)

**CRM System:**
- Database: `/home/workspace/Knowledge/crm/crm.db` (SQLite)
- Profiles: `/home/workspace/Knowledge/crm/individuals/*.md` (Markdown)
- Schema: Individuals table with categories, status, priority, tags
- Query tool: `N5/scripts/crm_query_helper.py`
- Pattern: Hybrid (SQLite index + Markdown source of truth)

**Meeting Processing Pattern:**
- Meeting data flows to `/home/workspace/Personal/Meetings/`
- Enrichment happens via `meeting_prep_digest_v2.py`
- Contact extraction → CRM profiles
- LinkedIn intelligence already partially integrated (via `n5_linkedin_intel.py`)

**Email Processing Pattern:**
- TODO: Research this (no clear grep results yet)

### Architectural Decisions (Nemawashi)

**Decision 1: Storage Architecture**

*Option A: Parallel SQLite Database*
- New DB: `/home/workspace/Knowledge/linkedin/linkedin.db`
- Tables: conversations, messages, commitments, participants
- Link to CRM via email/linkedin_url
- PRO: Clean separation, optimized schema for LinkedIn data
- PRO: Can query independently or join with CRM
- CON: Another database to maintain
- TRAP DOOR: Medium (SQLite is portable, can consolidate later)

*Option B: Extend CRM Database*
- Add tables to existing `crm.db`: linkedin_conversations, linkedin_messages, etc.
- PRO: Single database, unified queries
- CON: Couples LinkedIn to CRM (what if we want Slack next?)
- CON: CRM focused on *individuals*, LinkedIn focused on *conversations*
- TRAP DOOR: High (hard to decouple later)

*Option C: Hybrid - Separate DB, Shared Profiles*
- New `linkedin.db` for conversations/messages/commitments
- Update CRM profiles (markdown) with LinkedIn context
- Link via linkedin_url field
- PRO: Simple (disentangled concerns)
- PRO: Each system optimized for its purpose
- PRO: Follows existing pattern (SQLite index + Markdown source)
- CON: Need sync mechanism between systems
- TRAP DOOR: Low (easy to change DB structure, markdown is universal)

**RECOMMENDATION: Option C** - Separate LinkedIn DB, shared CRM profiles
- Aligns with "Simple Over Easy" (disentangled)
- Allows independent evolution
- Markdown profiles become the integration layer
- Future channels (email, Slack) follow same pattern

**Decision 2: Commitment Extraction**

*Option A: Real-time LLM extraction on webhook receipt*
- PRO: Immediate extraction
- CON: Slow webhook response (timeouts?)
- CON: Expensive (every message)

*Option B: Batch processing on schedule*
- PRO: Can optimize for cost (batch API)
- PRO: Reliable webhook response
- CON: Delay in extraction (acceptable for MVP)

*Option C: Hybrid - Flag for extraction, process async*
- Webhook marks new messages
- Scheduled task processes flagged items
- PRO: Fast webhook, reliable extraction
- PRO: Can retry failures
- TRAP DOOR: Low

**RECOMMENDATION: Option C** - Flag + async processing

**Decision 3: Thread Distinction**

Kondo provides:
- `conversation_id` - unique per LinkedIn conversation thread
- `messages` - array of messages in conversation

**APPROACH:**
- Use Kondo's `conversation_id` directly
- No need to infer threads (Kondo already does this)
- Store as separate table: `conversations` (metadata) + `messages` (individual messages)

**Decision 4: Security**

Webhook will be public endpoint. Options:
- No auth (rely on obscure URL)
- API key validation (Kondo supports `x-api-key` header)

**RECOMMENDATION:** API key validation
- Generate secure random key
- Store in `/home/workspace/N5/config/secrets/kondo_webhook_key.txt`
- Validate on every webhook request

---

## Information Flow Design

### Inbound Flow (Kondo → Zo)

```
Kondo Webhook POST
  ↓
Webhook Receiver (Hono endpoint)
  ↓ (validate API key)
  ↓ (parse payload)
  ↓
SQLite Write (linkedin.db)
  - conversations table (metadata)
  - messages table (individual messages)
  - participants table (who's in conversation)
  ↓
Flag for Processing
  - commitment_extraction_needed = true
  - crm_enrichment_needed = true
```

### Processing Flow (Async)

```
Scheduled Task (every 15min)
  ↓
Query: messages WHERE commitment_extraction_needed = true
  ↓
LLM Extraction (batch)
  - Identify commitments/promises
  - Extract: what, who owes, deadline, status
  ↓
Write: commitments table
  - conversation_id (link to conversation)
  - message_id (specific message)
  - commitment_text
  - commitment_type (I_OWE_THEM, THEY_OWE_ME)
  - deadline (if mentioned)
  - status (PENDING, FULFILLED, OVERDUE)
  ↓
CRM Enrichment
  - Find/create profile in crm.db
  - Update markdown with LinkedIn context
  - Link conversation in profile
```

### Query Flow (V → Zo)

```
V asks: "What LinkedIn responses are pending?"
  ↓
Query: conversations WHERE last_message_from != 'me' AND response_time > threshold
  ↓
Return: List with names, last message, elapsed time
```

---

## Schema Design

### linkedin.db Tables

**conversations**
```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,              -- Kondo conversation_id
    linkedin_profile_url TEXT,        -- Participant's profile
    participant_name TEXT,
    participant_email TEXT,           -- If available
    first_message_at INTEGER,         -- Unix timestamp
    last_message_at INTEGER,
    last_message_from TEXT,           -- 'me' or 'them'
    message_count INTEGER,
    status TEXT,                      -- ACTIVE, PENDING_RESPONSE, ARCHIVED
    crm_profile_slug TEXT,            -- Link to CRM: individuals/{slug}.md
    created_at INTEGER,
    updated_at INTEGER
);

CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_crm ON conversations(crm_profile_slug);
```

**messages**
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    message_id TEXT,                  -- Kondo's message ID (if provided)
    sender TEXT NOT NULL,             -- 'me' or participant name
    content TEXT NOT NULL,
    sent_at INTEGER NOT NULL,         -- Unix timestamp
    commitment_extraction_needed BOOLEAN DEFAULT 1,
    commitment_extracted_at INTEGER,
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_extraction_needed ON messages(commitment_extraction_needed);
```

**commitments**
```sql
CREATE TABLE commitments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    message_id INTEGER NOT NULL,
    commitment_type TEXT NOT NULL,    -- I_OWE_THEM, THEY_OWE_ME, MUTUAL
    what TEXT NOT NULL,               -- What's owed
    deadline TEXT,                    -- Extracted deadline (ISO format if mentioned)
    status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, FULFILLED, OVERDUE, CANCELLED
    confidence REAL,                  -- LLM confidence score
    notes TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id),
    FOREIGN KEY (message_id) REFERENCES messages(id)
);

CREATE INDEX idx_commitments_status ON commitments(status);
CREATE INDEX idx_commitments_type ON commitments(commitment_type);
```

---

## Component Design

### 1. Webhook Receiver Service

**Location:** `/home/workspace/N5/services/kondo-webhook/`

**Tech Stack:**
- Bun + Hono (matches existing services pattern)
- Simple POST endpoint
- API key validation
- SQLite writes

**Endpoints:**
- `POST /webhook/kondo` - Receive LinkedIn data
- `GET /health` - Health check

**Registered as user service:**
- Label: `kondo-linkedin-webhook`
- Protocol: HTTP
- Port: TBD (find available port)

### 2. Commitment Extractor Script

**Location:** `/home/workspace/N5/scripts/linkedin_commitment_extractor.py`

**Functionality:**
- Query unprocessed messages
- Batch process with LLM
- Extract commitments
- Update database
- Log results

**Prompt Engineering:**
```
Analyze this LinkedIn message and extract any commitments or promises.

Message: "{content}"
Sender: {sender}

Identify:
1. What was promised/committed
2. Who owes what (I_OWE_THEM, THEY_OWE_ME, or MUTUAL)
3. Any deadline mentioned
4. Confidence level (0.0-1.0)

Return JSON with extracted commitments.
```

### 3. Response Monitor Script

**Location:** `/home/workspace/N5/scripts/linkedin_response_monitor.py`

**Functionality:**
- Query conversations with pending responses
- Calculate response times
- Flag overdue conversations
- Generate alerts/reports

### 4. CRM Enrichment Script

**Location:** `/home/workspace/N5/scripts/linkedin_crm_enricher.py`

**Functionality:**
- Link LinkedIn conversations to CRM profiles
- Update markdown profiles with LinkedIn context
- Create profiles for new contacts
- Sync bidirectionally

### 5. Query Interface (Chat)

**Location:** `/home/workspace/N5/scripts/linkedin_query.py`

**Commands:**
- `linkedin_query.py pending` - Show pending responses
- `linkedin_query.py commitments --status=PENDING` - Show pending commitments
- `linkedin_query.py conversation <id>` - Show full conversation
- `linkedin_query.py search <name>` - Find conversations with person

---

## Failure Modes & Monitoring

### What Can Go Wrong?

1. **Webhook failures**
   - Detection: Health check endpoint, log monitoring
   - Recovery: Retry mechanism, dead letter queue

2. **Commitment extraction errors**
   - Detection: Confidence scores, manual review flag
   - Recovery: Queue for manual review

3. **CRM sync drift**
   - Detection: Scheduled validation script
   - Recovery: Re-sync from LinkedIn DB

4. **Response monitoring false positives**
   - Detection: Manual feedback loop
   - Recovery: Adjust thresholds, add exclusion rules

5. **Database corruption**
   - Detection: Regular integrity checks
   - Recovery: Automated backups (daily snapshot)

---

## MVP Scope (Phase 1)

**In Scope:**
1. ✅ Webhook receiver with API key validation
2. ✅ Store conversations + messages in linkedin.db
3. ✅ Basic CRM profile linking
4. ✅ Commitment extraction (async)
5. ✅ Response monitoring (simple time-based)
6. ✅ Query interface (CLI)

**Out of Scope (Future):**
- Auto-draft responses
- Complex NLP on conversations
- LinkedIn profile change monitoring
- Integration with outbound LinkedIn posting
- Web dashboard

**Phase 1 Success Criteria:**
1. Webhook receives and stores LinkedIn data
2. Can query: "Show pending LinkedIn responses"
3. Can query: "What commitments do I owe people?"
4. CRM profiles show linked LinkedIn conversations
5. System runs for 1 week without manual intervention

---

## Implementation Order

1. **Database schema** - Create linkedin.db with tables
2. **Webhook service** - Receive and store data
3. **API key setup** - Generate and configure
4. **Test with Kondo** - Verify webhook integration works
5. **Query interface** - Basic CLI for viewing data
6. **Commitment extractor** - LLM-based extraction
7. **CRM enrichment** - Link to existing profiles
8. **Response monitor** - Alert on pending responses
9. **Scheduled tasks** - Automate processing
10. **Documentation** - Usage guide for V

---

## Trade-offs Accepted

1. **Separate DB vs. unified**: Accept sync complexity for architectural simplicity
2. **Async extraction vs. real-time**: Accept delay for reliability and cost
3. **CLI vs. web dashboard**: Accept less polish for faster MVP
4. **Basic thread distinction**: Trust Kondo's conversation_id over complex inference

---

## Next: Execute Phase

Ready to activate Builder Mode and implement Phase 1.
