# n8n Workflow Test Results
**Date:** 2025-10-22 22:15 ET  
**Test:** Warm intro via webhook

---

## Test Input
```json
{
  "text": "Need to connect Sarah Chen (Product) with Marcus Rodriguez (Recruiting). Both expanding teams in Q1 2026. Draft the intro by tomorrow 10am.",
  "context": {
    "type": "warm_intro",
    "person_a": "Sarah Chen (Product)",
    "person_b": "Marcus Rodriguez (Recruiting)",
    "reason": "Both expanding teams in Q1 2026",
    "deadline": "tomorrow 10am"
  }
}
```

## Webhook Response
✅ `{"message":"Workflow was started"}`

## System Status
- **n8n workflow:** Active ✓
- **Zo API:** Healthy ✓ (http://localhost:8770/health)
- **Webhook trigger:** Received ✓

## Expected Behavior
1. n8n receives webhook POST
2. n8n → Zo API (http://localhost:8770) to extract tasks
3. Zo API returns structured tasks:
   - Draft intro (tomorrow 10am, 15m, High, Networking)
   - Send intro (tomorrow 11am, 5m, High, Networking)  
   - Follow-up (7 days later, 10m, Normal, Networking)
4. n8n → Gmail sends batch email to aki+qztlypb6-d@aki.akiflow.com
5. Tasks appear in Akiflow within 60 seconds

## Verification Steps
1. Check Akiflow for 3 new tasks in "Scheduled on calendar" section
2. Verify timing, projects, notes match expected format
3. If tasks don't appear:
   - Check n8n execution log (view workflow → Executions tab)
   - Check Zo API logs: `tail -50 /dev/shm/zo-n8n-api.log`
   - Check Gmail sent folder for email to Aki

## Status
⏳ **Awaiting V's confirmation from Akiflow**

---

## Notes
- First live test of full n8n → Zo API → Akiflow pipeline
- Webhook accepted successfully (HTTP 200)
- Need to verify end-to-end execution
