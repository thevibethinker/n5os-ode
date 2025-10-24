---
name: Meeting Actions → Akiflow
version: 1.0
status: ready-to-build
created: 2025-10-23
---
# Workflow: Meeting Actions → Akiflow

## Purpose
Extract action items from processed meeting Smart Blocks → V approves/edits → Auto-push to Akiflow

## Current State

### Meeting Processing System (V3)
- **Auto-detects:** Transcripts from Google Drive every 30 min
- **Auto-processes:** One transcript every 10 min via scheduled task
- **Generates:** Smart Blocks (B01-B30) in meeting directories
- **Location:** `Records/Company/Meetings/YYYY-MM-DD/`

### Relevant Blocks
- **B01 (Detailed Recap):** Contains decisions and key takeaways
- **B25 (Deliverable Content Map):** Promised deliverables and follow-ups
- **B21 (Salient Questions):** May contain implicit action items

---

## Proposed Workflow

### Phase 1: Extract Actions from Blocks (New)

**Trigger:** Meeting processing completes  
**Script:** `N5/scripts/extract_meeting_actions.py`

**What it does:**
1. Read completed Smart Blocks
2. Extract action items from:
   - B01: Explicit commitments ("will", "need to", "going to")
   - B25: Deliverables with deadlines
   - Implicit: Questions requiring follow-up
3. Create action items JSON:
```json
{
  "meeting_id": "2025-10-22_Leadership-Sync",
  "meeting_title": "Leadership Team Sync",
  "meeting_date": "2025-10-22",
  "actions": [
    {
      "id": "act_001",
      "text": "Draft recap for Leadership Team Sync",
      "context": "Mentioned in B01 - need to distribute by EOD",
      "suggested_when": "Tomorrow 9:30am",
      "suggested_duration": "20m",
      "suggested_priority": "High",
      "suggested_project": "Operations",
      "suggested_tags": ["recap", "meeting"],
      "source_block": "B01",
      "confidence": "high"
    }
  ],
  "extracted_at": "2025-10-22T15:30:00Z",
  "status": "pending_review"
}
```
4. Save to: `N5/inbox/meeting_actions/YYYY-MM-DD_Meeting-Name.json`
5. Notify V: "3 action items extracted from Leadership Sync - ready for review"

---

### Phase 2: Review & Approve (Email-Based)

**Trigger:** Actions extracted  
**Action:** Email V for approval

**Email format:**
```
From: Zo (V's AI) <va@zo.computer>
To: attawar.v@gmail.com
Subject: [N5] 3 action items from Leadership Team Sync

Hi V,

I extracted 3 action items from your Leadership Team Sync meeting (2025-10-22).
Please review and reply with your approval:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**1. Draft recap for Leadership Team Sync**
   📅 Tomorrow 9:30am | ⏱ 20m | 🔴 High
   📁 Operations | 🏷 recap, meeting
   📝 Mentioned in meeting - need to distribute by EOD

**2. Send intro: Sarah Chen → Marcus Rodriguez**  
   📅 Tomorrow 10:00am | ⏱ 15m | 🔴 High
   📁 Networking | 🏷 warm_intro
   📝 Connect Sarah (Product) with Marcus (Recruiting) - both expanding Q1 2026

**3. Review Q4 hiring pipeline**
   📅 Friday 2:00pm | ⏱ 45m | 🟡 Normal
   📁 Personnel | 🏷 hiring, review
   📝 Screen top 5 candidates, prepare interview schedule

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Reply with:**
• "approve all" → Push all 3 to Akiflow
• "approve 1,3" → Push only #1 and #3
• "skip 2" → Don't create #2
• "edit 1: change to 8am, 30m" → Modify then push

Or just reply "approved" and I'll push everything!

—Zo
```

**V's reply options:**
- `approve all` or `approved` or `yes` → Push all to Akiflow
- `approve 1,3` → Selective approval
- `skip 2` or `remove 2` → Exclude specific items
- `edit 1: tomorrow 8am, 30m` → Modify before pushing
- Any custom edits → Parse and apply

**Zo processes reply:**
1. Detect Gmail thread reply
2. Parse approval/edits from V's email
3. Apply changes to actions JSON
4. Batch push to Akiflow
5. Reply confirming: "✓ 3 tasks created in Akiflow"

---

### Phase 3: Push to Akiflow

**Command:** `aki: approve meeting actions from [meeting]`  
**Execution:**
1. Load pending actions JSON
2. Apply any edits from V
3. Batch email to Aki with `---` separators
4. Mark actions as "sent" in JSON
5. Confirm to V: "✓ 3 tasks created in Akiflow from Leadership Sync"

---

## Implementation Steps

### 1. Build Action Extractor (60 min)
**Script:** `N5/scripts/extract_meeting_actions.py`
- Parse Smart Blocks (B01, B25 especially)
- Detect action patterns:
  - "need to", "will", "should", "must"
  - "by [date]", "before [time]"
  - Deliverables from B25
- Score confidence (high/medium/low)
- Generate structured JSON
- Save to inbox
- **Email V with formatted approval request**

### 2. Build Email Reply Monitor (45 min)
**Script:** `N5/scripts/monitor_action_approvals.py`
- Check Gmail every 2 min for replies to action approval emails
- Parse V's response:
  - "approve all" / "approved" / "yes" → all actions
  - "approve 1,3" → selective
  - "skip 2" → exclude
  - "edit 1: [changes]" → modify
- Update actions JSON with approval status
- Trigger Akiflow push

### 3. Hook into Meeting Processor (15 min)
**Update:** Scheduled task or add to existing orchestrator
- After Smart Blocks complete
- Run action extractor automatically
- Email sent automatically

### 4. Wire to Akiflow (10 min)
**Use existing:** file 'N5/commands/aki.md'
- Format approved actions as batch email
- Send via Gmail to Aki
- Update JSON: status="pushed"
- Reply to V: "✓ N tasks created in Akiflow"

### 5. Register Email Monitor Service (5 min)
**Service:** Run monitor_action_approvals.py continuously
- Poll Gmail every 2 min
- Process any approval replies
- Auto-push to Akiflow

---

## File Structure
```
N5/
├── inbox/
│   └── meeting_actions/          # Extracted, pending review
│       ├── 2025-10-22_Leadership-Sync.json
│       └── 2025-10-23_Client-Call.json
├── scripts/
│   └── extract_meeting_actions.py
└── workflows/
    └── meeting-to-akiflow.md     # This file
```

---

## Success Metrics
- ✅ Actions extracted within 2 min of meeting processing
- ✅ <3 steps from meeting → Akiflow (extract, review, approve)
- ✅ Batch approval: all actions in one command
- ✅ Zero manual typing of task details

---

## Example End-to-End

**10:00am:** Meeting with client  
**10:30am:** Transcript uploaded to Google Drive  
**11:00am:** Meeting processor generates Smart Blocks  
**11:02am:** Action extractor runs, finds 4 items  
**11:03am:** Zo notifies: "4 actions from Client Meeting - review?"  
**11:05am:** V: "show them"  
**11:05am:** Zo: [formatted list]  
**11:06am:** V: "approve all"  
**11:06am:** Zo → Aki email sent  
**11:07am:** 4 tasks appear in Akiflow  
**11:07am:** Zo: "✓ 4 tasks created"

**Total time:** 7 minutes from meeting end to Akiflow

---

## Change Log
- 2025-10-23: Initial design
