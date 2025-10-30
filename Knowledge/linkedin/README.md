# LinkedIn Intelligence System

**Version:** 1.0.0  
**Created:** 2025-10-30  
**Status:** ✅ Active

## Overview

Automated LinkedIn conversation intelligence system integrated with Kondo. Tracks conversations, extracts commitments, monitors pending responses, and links to CRM profiles.

---

## Architecture

```
Kondo (LinkedIn) → Webhook → SQLite → CLI Tools → You (via chat)
                      ↓
                   CRM Link
```

### Components

1. **Webhook Service** (`kondo-linkedin-webhook`)
   - Receives LinkedIn conversation data from Kondo
   - Stores conversations and messages in SQLite
   - Public endpoint: `https://kondo-linkedin-webhook-va.zocomputer.io`

2. **Database** (`Knowledge/linkedin/linkedin.db`)
   - Conversations, messages, commitments
   - Linked to CRM profiles
   - Full schema: file `N5/schemas/linkedin_intel.sql`

3. **CLI Tools** (`N5/scripts/linkedin_*.py`)
   - Query conversations, commitments, pending responses
   - Extract commitments using LLM
   - Sync with CRM

---

## Setup Instructions

### 1. Configure Kondo Webhook

In Kondo's integrations page, create a new webhook with:

- **Name:** `Zo LinkedIn Intelligence`
- **Trigger type:** `Streaming` (real-time updates)
- **URL:** `https://kondo-linkedin-webhook-va.zocomputer.io/webhook/kondo`
- **Method:** `POST`
- **API Key Header:** `x-api-key`
- **API Key Value:** `9d905d8223f0288d8761381ba48f0d90a60fe5b69e5f96841dc4fed090cfb654`

Click "Test then save" to verify the connection.

### 2. Verify Setup

```bash
# Check service health
curl https://kondo-linkedin-webhook-va.zocomputer.io/health

# View stats
python3 /home/workspace/N5/scripts/linkedin_query.py stats
```

---

## Usage

### Query Pending Responses

```bash
# Show conversations awaiting your response (>48 hours)
python3 /home/workspace/N5/scripts/linkedin_query.py pending

# Custom threshold (24 hours)
python3 /home/workspace/N5/scripts/linkedin_query.py pending --threshold-hours=24
```

### Query Commitments

```bash
# Show all commitments
python3 /home/workspace/N5/scripts/linkedin_query.py commitments

# Show only what you owe others
python3 /home/workspace/N5/scripts/linkedin_query.py commitments --mine

# Show only what others owe you
python3 /home/workspace/N5/scripts/linkedin_query.py commitments --theirs

# Filter by status
python3 /home/workspace/N5/scripts/linkedin_query.py commitments --status=FULFILLED
```

### View Conversation

```bash
# Show full conversation with messages and commitments
python3 /home/workspace/N5/scripts/linkedin_query.py conversation <conversation_id>
```

### Search Conversations

```bash
# Search by participant name or email
python3 /home/workspace/N5/scripts/linkedin_query.py search "John Smith"
```

### Extract Commitments

**Note:** Requires ANTHROPIC_API_KEY environment variable

```bash
# Process 10 messages and extract commitments using LLM
export ANTHROPIC_API_KEY=$(cat ~/.anthropic_api_key)
python3 /home/workspace/N5/scripts/linkedin_commitment_extractor.py --batch-size=10

# Dry run (no database changes)
python3 /home/workspace/N5/scripts/linkedin_commitment_extractor.py --dry-run
```

### Sync with CRM

```bash
# Link LinkedIn conversations to CRM profiles automatically
python3 /home/workspace/N5/scripts/linkedin_crm_sync.py --auto

# Dry run (preview matches)
python3 /home/workspace/N5/scripts/linkedin_crm_sync.py --auto --dry-run
```

---

## Chat Interface

You can use natural language with Zo to query your LinkedIn intelligence:

- "Show me pending LinkedIn responses"
- "What commitments do I owe people on LinkedIn?"
- "Search for conversations with John"
- "What's the status of my LinkedIn commitments?"

---

## Automation

### Scheduled Commitment Extraction

Create a daily agent to extract commitments:

```bash
# Example: Run daily at 8 AM
python3 /home/workspace/N5/scripts/session_manager.py create-agent \
  --name "LinkedIn Commitment Extraction" \
  --schedule "0 8 * * *" \
  --command "ANTHROPIC_API_KEY=\$(cat ~/.anthropic_api_key) python3 /home/workspace/N5/scripts/linkedin_commitment_extractor.py --batch-size=20"
```

### Pending Response Alerts

Create a daily digest of pending responses:

```bash
# Example: Check every weekday morning at 9 AM
python3 /home/workspace/N5/scripts/session_manager.py create-agent \
  --name "LinkedIn Pending Response Digest" \
  --schedule "0 9 * * 1-5" \
  --command "python3 /home/workspace/N5/scripts/linkedin_query.py pending --threshold-hours=48"
```

---

## Database Schema

See file `N5/schemas/linkedin_intel.sql` for full schema.

**Key Tables:**

- `conversations` - LinkedIn conversation threads
- `messages` - Individual messages
- `commitments` - Extracted commitments and promises
- `processing_log` - Webhook processing history

**Views:**

- `my_commitments` - What you owe others
- `their_commitments` - What others owe you
- `pending_responses` - Conversations awaiting your response

---

## Files

- **Service:** `N5/services/kondo-webhook/`
- **Scripts:** `N5/scripts/linkedin_*.py`
- **Database:** `Knowledge/linkedin/linkedin.db`
- **Schema:** `N5/schemas/linkedin_intel.sql`
- **API Key:** `N5/config/secrets/kondo_webhook_key.txt`

---

## Integration with CRM

When a LinkedIn conversation is synced with a CRM profile:

- The conversation is linked via `crm_profile_slug`
- You can see LinkedIn activity in CRM context
- Commitments are tied to known individuals
- Better relationship intelligence

Sync runs automatically when possible, or use:

```bash
python3 /home/workspace/N5/scripts/linkedin_crm_sync.py --auto
```

---

## Troubleshooting

### Webhook not receiving data

```bash
# Check service health
curl https://kondo-linkedin-webhook-va.zocomputer.io/health

# View service logs
tail -f /dev/shm/kondo-linkedin-webhook.log

# Check for errors
tail -f /dev/shm/kondo-linkedin-webhook_err.log
```

### Commitment extraction failing

```bash
# Ensure API key is set
echo $ANTHROPIC_API_KEY

# Check for errors in database
sqlite3 /home/workspace/Knowledge/linkedin/linkedin.db \
  "SELECT * FROM messages WHERE extraction_error IS NOT NULL"
```

### Database queries slow

```bash
# Check database size
ls -lh /home/workspace/Knowledge/linkedin/linkedin.db

# Vacuum database
sqlite3 /home/workspace/Knowledge/linkedin/linkedin.db "VACUUM"
```

---

## Future Enhancements

Planned for later iterations:

1. **Auto-draft responses** - Generate suggested replies based on commitments
2. **Commitment fulfillment tracking** - Automatically mark commitments as fulfilled when actions complete
3. **Smart notifications** - Alert when high-priority commitments are approaching deadline
4. **Thread intelligence** - Better conversation context and history
5. **Response templates** - Common response patterns for frequent scenarios

---

## Support

- View service status: `https://va.zo.computer/system`
- Check logs: `/dev/shm/kondo-linkedin-webhook*.log`
- Database: `Knowledge/linkedin/linkedin.db`
- Ask Zo: "Help me with LinkedIn intelligence system"

**Version:** 1.0.0 | **Last Updated:** 2025-10-30
