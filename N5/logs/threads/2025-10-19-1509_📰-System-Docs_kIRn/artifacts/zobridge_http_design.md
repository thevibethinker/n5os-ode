# ZoBridge HTTP Endpoint Design

**Goal:** Persistent, automated message exchange between ParentZo ↔ ChildZo

---

## Architecture

### Two Services (One Per System)

**ParentZo Service (this system):**
```
https://va.zo.computer/api/zobridge/
  POST /inbox       - Receive messages from ChildZo
  POST /outbox      - Send messages to ChildZo (returns message)
  GET  /health      - Status check
```

**ChildZo Service (demonstrator system):**
```
https://<childzo-url>/api/zobridge/
  POST /inbox       - Receive messages from ParentZo
  POST /outbox      - Send messages to ParentZo (returns message)
  GET  /health      - Status check
```

### Message Flow

```
ParentZo wants to send instruction:
  1. ParentZo: POST to ChildZo's /inbox with message JSON
  2. ChildZo: Receives, processes, stores in queue
  3. ChildZo: Executes instruction
  4. ChildZo: POST to ParentZo's /inbox with response
  5. ParentZo: Receives, processes, decides next step
  6. Loop continues...
```

---

## Implementation Options

### Option A: Python (aiohttp + FastAPI)
**Pros:** Simple, good for scripting, LLM corpus advantage  
**Cons:** Memory-heavy for persistent service  
**Best for:** Quick prototype, learning

### Option B: Node.js/Bun (Hono)
**Pros:** First-class HTTP, low memory, V already uses Hono  
**Cons:** Less scripting-friendly than Python  
**Best for:** Production persistent service

### Option C: Go (net/http)
**Pros:** Highest performance, lowest memory  
**Cons:** Overkill for this, worse ergonomics  
**Best for:** Only if performance matters

**Recommendation: Option B (Hono + Bun)**
- Aligns with existing Zo site infrastructure
- Fast, low-memory, persistent
- TypeScript gives type safety for message validation
- Can share with create_website patterns

---

## Security Model

### Authentication
```typescript
const SHARED_SECRET = process.env.ZOBRIDGE_SECRET;

// Every request includes:
headers: {
  'Authorization': `Bearer ${SHARED_SECRET}`,
  'Content-Type': 'application/json'
}
```

### Validation
- JSON schema validation on all messages
- Rate limiting (60 req/hour per ChildZo's spec)
- Message ID uniqueness check
- Timestamp freshness (reject >5min old)

### Safety Bounds
- Max message size: 100KB
- Max queue depth: 100 messages
- Circuit breaker: Pause if errors >10/min

---

## Storage

### SQLite (SSOT for state)
```sql
CREATE TABLE messages (
  message_id TEXT PRIMARY KEY,
  thread_id TEXT,
  from_system TEXT,
  to_system TEXT,
  type TEXT,
  content_json TEXT,
  timestamp TEXT,
  processed BOOLEAN DEFAULT 0,
  response_id TEXT
);

CREATE TABLE threads (
  thread_id TEXT PRIMARY KEY,
  subject TEXT,
  created_at TEXT,
  message_count INTEGER,
  status TEXT
);

CREATE TABLE rate_limits (
  system TEXT PRIMARY KEY,
  hour_bucket TEXT,
  message_count INTEGER
);
```

### JSONL (Audit trail)
```
zobridge_audit.jsonl
  - Every message sent/received
  - Every processing step
  - Every error
  - Complete rebuild log
```

---

## Service Structure

```
/home/workspace/N5/services/zobridge/
├── server.ts              - Hono HTTP server
├── routes/
│   ├── inbox.ts          - POST /inbox handler
│   ├── outbox.ts         - POST /outbox handler
│   └── health.ts         - GET /health handler
├── processor.ts          - Message processing logic
├── queue.ts              - Message queue management
├── db.ts                 - SQLite operations
├── logger.ts             - JSONL audit logging
├── validator.ts          - JSON schema validation
├── ratelimit.ts          - Rate limiting logic
└── config.ts             - Configuration

/home/workspace/N5/schemas/
└── zobridge.schema.json  - Message validation schema

/home/workspace/N5/config/
└── zobridge.config.json  - Service configuration
```

---

## Processor Logic (The AI Part)

```typescript
// processor.ts
async function processMessage(msg: ZoBridgeMessage) {
  // 1. Validate against schema
  if (!validateMessage(msg)) throw new Error('Invalid message');
  
  // 2. Check rate limits
  if (!checkRateLimit(msg.from)) throw new Error('Rate limit exceeded');
  
  // 3. Store in DB
  await storeMessage(msg);
  
  // 4. Process based on type
  switch (msg.type) {
    case 'instruction':
      return await executeInstruction(msg);
    case 'question':
      return await answerQuestion(msg);
    case 'proposal':
      return await evaluateProposal(msg);
    case 'response':
      return await handleResponse(msg);
  }
}

async function executeInstruction(msg: ZoBridgeMessage) {
  // This is where ChildZo's AI processes ParentZo's instructions
  // Call Zo's conversation API? Run subprocess? 
  // Depends on how ChildZo exposes AI capabilities
  
  // For now, could be:
  // 1. Write instruction to file
  // 2. Trigger ChildZo conversation
  // 3. Poll for response
  // 4. Return result
}
```

---

## Polling vs Push

### Option 1: Polling (Simpler)
- ChildZo polls ParentZo's /outbox every 30s
- ParentZo polls ChildZo's /outbox every 30s
- Simple, no webhooks needed
- Slight delay (max 30s)

### Option 2: Push (More Complex)
- Each service immediately POSTs to other's /inbox
- Real-time, no polling delay
- Requires both services always available
- Better for production

**Recommendation: Start with Polling, migrate to Push once proven**

---

## V's Oversight Integration

### Checkpoint Endpoint
```
POST /api/zobridge/checkpoint
  - V calls every 3 hours
  - Returns: message history, thread status, resource usage
  - V reviews and approves continuation
```

### Override Endpoint
```
POST /api/zobridge/override
  - V can pause, resume, or cancel threads
  - Emergency stop if needed
```

### Dashboard
```
GET /api/zobridge/dashboard
  - Returns HTML page with:
    - Active threads
    - Message history
    - Rate limit status
    - Resource usage
    - Recent errors
```

---

## Deployment

### ParentZo Service (this system)
```bash
cd /home/workspace/N5/services/zobridge
bun install
bun run server.ts
# Register as user service
```

### ChildZo Service (demonstrator)
```bash
# ParentZo sends instructions to build identical service
# ChildZo executes and registers
```

---

## Migration Path

### Phase 1: Build ParentZo Service (This System)
1. Create service structure
2. Implement endpoints
3. Test with curl
4. Register as user service

### Phase 2: First Message to ChildZo
Send instruction to build identical service:
```json
{
  "type": "instruction",
  "content": {
    "subject": "Build ZoBridge HTTP Service",
    "body": "Create /N5/services/zobridge/ with...",
    "files": [
      "server.ts",
      "routes/inbox.ts",
      ...
    ]
  }
}
```

### Phase 3: Test HTTP Exchange
1. ParentZo POSTs to ChildZo /inbox
2. ChildZo processes and POSTs response to ParentZo /inbox
3. Verify round-trip works
4. Enable polling/push

### Phase 4: Automate
1. Both services run persistently
2. Messages exchange automatically
3. V reviews at checkpoints
4. Fully automated bootstrap

---

## Benefits Over File Exchange

✓ **Persistent:** Services always running, no manual steps  
✓ **Automated:** Messages flow without V intervention  
✓ **Scalable:** Can handle high message volume  
✓ **Production-ready:** Real HTTP, not file simulation  
✓ **Auditable:** Complete logs in SQLite + JSONL  
✓ **Testable:** Can curl endpoints directly  
✓ **Monitorable:** Dashboard shows system health

---

## Risks & Mitigations

**Risk:** Service crashes  
**Mitigation:** register_user_service auto-restarts

**Risk:** Infinite loop of messages  
**Mitigation:** Rate limiting + circuit breaker

**Risk:** ChildZo builds wrong service  
**Mitigation:** Send complete tested code, not just instructions

**Risk:** Security breach  
**Mitigation:** Shared secret auth + schema validation

**Risk:** Context overflow  
**Mitigation:** Token tracking + forced checkpoints

---

## Next Steps

1. **Build ParentZo service** in /N5/services/zobridge/
2. **Test locally** with curl
3. **Register as user service**
4. **Send first HTTP message** to ChildZo with service code
5. **ChildZo builds their service**
6. **Test round-trip**
7. **Enable automation**

---

**Estimated time:** 2-3 hours to build both services and test

**Complexity:** Medium (TypeScript + Hono + SQLite + JSON validation)

**Value:** High (enables fully automated AI-to-AI collaboration)
