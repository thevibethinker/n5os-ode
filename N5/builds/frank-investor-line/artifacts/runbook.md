---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: pulse:frank-investor-line:D3.1
---

# Frank Investor Line — Operations Runbook

## 1. Overview

Frank is the voice AI answering `+1 (878) 879-2087`. This build added investor intelligence: mode detection, question tracking, sentiment analysis, and a rewritten briefing in V-voice.

**Stack:** Vapi (voice) → webhook.ts (Bun/Hono) → DuckDB (storage) → Zo API (analysis) → Gmail (recaps)

## 2. Voice Protocol

### Caller Mode Detection
Frank's first message asks: "Are you calling as an investor or as a Zo user?"

- **Investor mode**: Third-person about V ("V built X"), loads zo-101-briefing.md FAQ, references prefab answers
- **User mode**: Second-person practical ("You can do X with Zo"), standard help
- **Unknown**: Default if caller doesn't specify — behaves as user mode

Mode is stored in `calls.caller_mode` via the `recordCallerMode` tool.

### Voice Primitives
Briefing uses V-voice patterns from `Skills/vapi/assets/voice-primitives-reference.md`:
- "isn't X... it's Y" framing
- Concrete proof points over abstract claims
- Redirect-to-V pattern for sensitive questions (funding, user count, revenue)

### Updating the Briefing
Edit `Skills/vapi/assets/zo-101-briefing.md`. Changes take effect on the next call (loaded fresh at call start). No restart needed. Keep under 3,000 words.

## 3. Question Tracking

### How It Works
1. Call ends → `extractQuestions()` fires (non-blocking)
2. Sends transcript to `/zo/ask` with structured output format
3. Returns: question_text, normalized_question, answer_text, answer_quality, category
4. Stored in `call_questions` table

### Schema: call_questions
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR | UUID |
| call_id | VARCHAR | FK to calls |
| question_text | VARCHAR | Verbatim from transcript |
| normalized_question | VARCHAR | Deduplicated phrasing |
| answer_text | VARCHAR | What Frank said |
| answer_quality | VARCHAR | answered / redirected / unanswered |
| category | VARCHAR | differentiation, business_model, fundraising, roadmap, etc. |
| extracted_at | TIMESTAMP | When extraction ran |

### Querying Questions
```bash
duckdb /home/workspace/Datasets/vapi-calls/data.duckdb -c "
  SELECT normalized_question, category, COUNT(*) as freq
  FROM call_questions
  GROUP BY normalized_question, category
  ORDER BY freq DESC
  LIMIT 20
"
```

## 4. Prefab Answers

### Auto-Generation Trigger
When a normalized question reaches 3+ occurrences, the system auto-generates a prefab answer via `/zo/ask`.

### Schema: prefab_answers
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR | UUID |
| normalized_question | VARCHAR | The question pattern |
| answer_text | VARCHAR | Frank's answer |
| occurrence_count | INTEGER | How many times asked |
| auto_generated | BOOLEAN | LLM-generated |
| manually_approved | BOOLEAN | V reviewed and approved |
| created_at | TIMESTAMP | Created |
| updated_at | TIMESTAMP | Last update |

### Reviewing Prefabs
```bash
# List all prefab answers
duckdb /home/workspace/Datasets/vapi-calls/data.duckdb -c "
  SELECT normalized_question, answer_text, occurrence_count, manually_approved
  FROM prefab_answers ORDER BY occurrence_count DESC
"
```

To approve or edit: update directly in DuckDB or build a review UI.

### FAQ Injection
`getPrefabAnswers()` queries approved + auto-generated prefabs and formats them as:
```
Investor FAQ (from past calls):
Q: what makes zo different from chatgpt
A: Zo isn't a chatbot — it's a full computer...
```
This block is appended to the system prompt at call start.

## 5. Recap Emails

Each call triggers `sendRecapEmail()` which sends V:

- **Sentiment** with emoji (😊 positive, 😐 neutral, 😟 negative, 😠 frustrated)
- **Call Grade** (A through F with rationale)
- **Key Interests** (bullet list)
- **Concerns** (bullet list)
- **Suggested Follow-Ups** (numbered list)
- **Notable Quotes** (blockquotes)
- **Question Summary** (total questions, categories, unanswered count)
- **Caller Mode** badge (💼 Investor / 👤 User)

Analysis is LLM-powered via `/zo/ask` with structured output. Falls back to basic email if analysis fails.

## 6. Instrumentation

### Logs
```bash
# Webhook debug log
tail -f /tmp/vapi-debug.log

# Service logs
tail -f /dev/shm/vapi-webhook.log
tail -f /dev/shm/vapi-webhook_err.log
```

### Database
```bash
# Quick health check
duckdb /home/workspace/Datasets/vapi-calls/data.duckdb -c "
  SELECT COUNT(*) as total_calls,
         COUNT(CASE WHEN caller_mode='INVESTOR' THEN 1 END) as investor_calls,
         COUNT(CASE WHEN analysis IS NOT NULL THEN 1 END) as analyzed
  FROM calls
"
```

### Migrations
```bash
# Run v3 migration (caller_mode column)
bun Skills/vapi/scripts/migrate-v3.ts

# Verify schema
duckdb /home/workspace/Datasets/vapi-calls/data.duckdb -c "DESCRIBE calls"
```

## 7. Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| No sentiment in email | `/zo/ask` failed or ZO_CLIENT_IDENTITY_TOKEN expired | Check logs, verify token |
| Questions not extracting | Extraction is fire-and-forget; check `/tmp/vapi-debug.log` | Look for "Question extraction error" |
| Prefab not generating | Need 3+ occurrences of same normalized question | Wait for more calls or manually insert |
| Prompt too long | Too many prefab answers loaded | Cap at 20 (already limited in getPrefabAnswers) |
| Mode not recording | `recordCallerMode` tool not called by Frank | Check system prompt includes mode detection instruction |
| Briefing stale | Old version on disk | Edit `Skills/vapi/assets/zo-101-briefing.md`, next call picks it up |

## 8. Future Work
- Investor call analytics dashboard (caller mode distribution, question frequency heatmap)
- Weekly investor question digest (top new questions, answer quality trends)
- Prefab answer review queue integrated with N5/review/
- Hook question data into CRM pipeline for investor follow-up tracking
- A/B test different briefing versions by caller cohort
