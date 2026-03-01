---
created: 2026-02-18
last_edited: 2026-02-18
version: 1.0
provenance: con_WqixWLkGYg48Os4p
---

# VAPI Assistant-Request Debugging Protocol

**Purpose:** This document is the canonical troubleshooting guide for the #1 recurring failure mode in the Zo Hotline: VAPI silently rejecting the assistant configuration returned by our webhook, causing calls to connect but have no assistant (dead air → hang up).

**This has happened in:** v2, v4, v5, v6 builds. Every major version change.

---

## The Failure Pattern

1. You deploy a webhook change
2. Calls start failing — callers hear nothing, or get "Couldn't Get Assistant"
3. `end-of-call-report` shows `endedReason: "assistant-request-returned-invalid-assistant"`
4. The error details are ONLY visible in `status-update` webhook events
5. If you haven't subscribed to `status-update`, you see NOTHING — just dead calls

**This is silent and destructive. VAPI does not return an error to the webhook. The call simply fails.**

---

## The 3 Known Killers (in order of frequency)

### 1. Deepgram Keywords with Spaces (3 occurrences)

**Error:** `"assistant.transcriber.each keyword must be in the format 'word' or 'word:number'"`

**Root cause:** VAPI validates that each keyword is a single word (no spaces). Multi-word phrases like `"Zo Computer:25"` or `"cover letter:8"` are rejected.

**Fix:** Remove spaces → `"ZoComputer:25"`, `"coverletter:8"`

**Prevention:** The webhook now has a `sanitizeKeywords()` function that strips spaces at runtime. Even if someone edits the keywords array with spaces, the sanitizer catches it. **DO NOT REMOVE THIS FUNCTION.**

```typescript
function sanitizeKeywords(keywords: string[]): string[] {
  return keywords.map(kw => {
    const cleaned = kw.replace(/\s+/g, '');
    if (cleaned !== kw) {
      console.warn(`[KEYWORD SANITIZER] Fixed invalid keyword: "${kw}" → "${cleaned}"`);
    }
    return cleaned;
  });
}
```

**Instances:**
- v4/D0: "cover letter:8" → "coverletter:8", "job search:8" → "jobsearch:8"
- v6/D1.1: "Zo Computer:25" → "ZoComputer:25"

### 2. Deepgram Feature Model Mismatch (1 occurrence)

**Error:** Invalid transcriber configuration (various)

**Root cause:** Deepgram features like `keyterm` require specific models (`nova-3` or `flux`). Adding them to `nova-2` config makes the entire transcriber invalid.

**Fix:** Check Deepgram docs before adding transcriber features. Current model is `nova-2`.

**Instance:**
- v5: Attempted to add `keyterm` boosting on `nova-2`

### 3. analysisPlan Schema Format (2 occurrences)

**Error:** Various analysis-related validation errors, or silently broken post-call analysis (no summary/structured data)

**Root cause:** VAPI has two formats for analysisPlan — a flat format (working) and a nested format (may not work depending on VAPI version). The flat format uses `summaryPrompt`, `structuredDataPrompt`, `structuredDataSchema`, `successEvaluationPrompt`, `successEvaluationRubric`. The nested format uses `summaryPlan.messages`, `structuredDataPlan.messages`, etc.

**Fix:** Use the FLAT format:
```typescript
analysisPlan: {
  summaryPrompt: "...",
  structuredDataPrompt: "...",
  structuredDataSchema: { type: "object", properties: {...} },
  successEvaluationPrompt: "...",
  successEvaluationRubric: "NumericScale"
}
```

**NOT the nested format:**
```typescript
// DO NOT USE THIS FORMAT
analysisPlan: {
  summaryPlan: { enabled: true, messages: [...] },
  structuredDataPlan: { enabled: true, messages: [...], schema: {...} },
  successEvaluationPlan: { enabled: true, rubric: "...", messages: [...] }
}
```

**Instances:**
- v5: Converted to nested format, broke post-call analysis (no summary data for all calls)
- v6/D1.1: Reverted to flat format

---

## Mandatory Post-Deploy Verification

After ANY change to `hotline-webhook.ts`, run this checklist:

### Step 1: Restart + Check Logs
```bash
# Kill and restart
fuser -k 4243/tcp; sleep 2
cd /home/workspace/Skills/zo-hotline/scripts && bun run hotline-webhook.ts > /dev/shm/zo-hotline-webhook.log 2> /dev/shm/zo-hotline-webhook_err.log &
sleep 3
cat /dev/shm/zo-hotline-webhook_err.log
```

### Step 2: Test assistant-request Response
```bash
curl -s -X POST http://localhost:4243 \
  -H "Content-Type: application/json" \
  -d '{"message":{"type":"assistant-request","call":{"customer":{"number":"+15551234567"}}}}' \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
a = data.get('assistant', {})

# Check keywords
kw = a.get('transcriber', {}).get('keywords', [])
bad = [k for k in kw if ' ' in k.split(':')[0]]
print(f'Keywords: {len(kw)} total, {len(bad)} with spaces')
if bad: print(f'  BAD: {bad}')

# Check analysisPlan format
ap = a.get('analysisPlan', {})
if 'summaryPlan' in ap: print('WARNING: analysisPlan uses nested format (may break)')
if 'summaryPrompt' in ap: print('OK: analysisPlan uses flat format')

# Check tools
tools = a.get('model', {}).get('tools', [])
tool_names = [t.get('function', {}).get('name', '') for t in tools]
print(f'Tools: {tool_names}')

print('ASSISTANT-REQUEST: VALID')
"
```

### Step 3: Make a Test Call
Call the hotline and say "activate testing mode" or "this is a test call". Verify:
- First message plays without clipping
- Zoseph responds to your input
- No dead air

### Step 4: Check for status-update Errors
```bash
# After test call, check for VAPI validation errors
grep "assistant-request-returned-invalid" /dev/shm/zo-hotline-webhook.log
grep "assistantRequestError" /dev/shm/zo-hotline-webhook.log
```

If Step 4 shows errors, the assistant config is invalid. The error message tells you exactly which field is wrong.

---

## For Pulse Drops Working on This File

**If you are a Pulse Drop editing `hotline-webhook.ts`:**

1. **DO NOT add spaces to Deepgram keywords.** The sanitizer will catch it, but don't rely on it.
2. **DO NOT change analysisPlan to nested format.** Use flat `summaryPrompt` / `structuredDataPrompt` / `structuredDataSchema`.
3. **DO NOT add Deepgram features without checking model compatibility.** Current model: `nova-2`.
4. **DO NOT remove `sanitizeKeywords()`.** It exists to catch mistakes.
5. **After making changes, test the assistant-request response** using the curl command in Step 2 above.
6. **Include in your deposit broadcast:** "Tested assistant-request: [PASS/FAIL]"

---

## Historical Timeline

| Date | Build | Issue | Root Cause | Fix |
|------|-------|-------|-----------|-----|
| 2026-02-17 | v4/D0 | Silent assistant failure | Keywords "cover letter:8", "job search:8" had spaces | Remove spaces |
| 2026-02-18 | v5 | Broken post-call analysis | analysisPlan nested format | Reverted to flat format |
| 2026-02-18 | v5 | keyterm on nova-2 | Model-gated feature | Removed keyterm |
| 2026-02-19 | v6/D1.1 | Silent assistant failure | Keyword "Zo Computer:25" had space | Remove space + added sanitizeKeywords() |
