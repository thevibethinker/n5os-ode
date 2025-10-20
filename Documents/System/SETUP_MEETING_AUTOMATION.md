# Meeting Recording Automation - Setup Guide

**Date**: 2025-10-16  
**For**: V  
**Objective**: Eliminate manual copy-paste for meeting transcript processing

---

## 🎯 Quick Decision

**Best Solution**: **Plaud AutoFlow → Email → Zo Scheduled Task**

**Why**:
- ✅ Zero manual steps after recording
- ✅ You already have Plaud device
- ✅ Works for in-person + phone meetings
- ✅ Automatic overnight processing
- ✅ Email confirmation when done

---

## 📋 Setup Instructions (15 minutes)

### Step 1: Configure Plaud AutoFlow (5 min)

1. **Open Plaud app** on your phone
2. Navigate to: **Settings → AutoFlow**
3. **Create new AutoFlow rule**:
   - **Name**: "Send to Zo for Processing"
   - **Trigger**: "When recording completes"
   - **Actions** (enable all):
     - ✅ Generate transcript
     - ✅ Generate summary
     - ✅ **Email transcript to: `va@zo.computer`**
   - **Email format**: Make sure "Include full transcript" is checked (not just summary)
4. **Save rule** and mark as active

### Step 2: Test Plaud AutoFlow (2 min)

1. **Record a 30-second test** (say: "This is a test recording for automation setup")
2. **Wait 2-3 minutes** for Plaud to process
3. **Check email** at `va@zo.computer`:
   - Should receive email from Plaud
   - Subject: Contains recording date/time
   - Body: Contains full transcript text

### Step 3: Tell Zo to Create Scheduled Task (2 min)

**Send this message to Zo**:

```
Create a scheduled task that runs daily at 9 PM ET:

Check Gmail for unread emails from Plaud (from:plaud.ai OR from:support@plaud.ai). 
For each email found:
1. Extract the transcript from email body
2. Detect meeting type (internal if mentions team/Logan/Danny/Ilsa/Rockwell, otherwise external)
3. Save transcript to N5/inbox/transcripts/ with filename: YYYY-MM-DD_[type]-plaud-[time].txt
4. Process via meeting-process command with auto-detected type
5. Mark email as read

After processing all emails, send me a summary email with:
- How many meetings were processed
- Meeting IDs and types
- Any errors encountered
- Links to processed meeting folders

Use --rrule "FREQ=DAILY;BYHOUR=21;BYMINUTE=0" and --delivery email
```

### Step 4: Verify End-to-End (next day)

1. **Record real meeting** using Plaud (as usual)
2. **Do nothing else** — AutoFlow handles it
3. **Next evening (9+ PM)**: Check email for Zo's processing summary
4. **Verify**: Check `file 'N5/records/meetings/'` for new meeting folder with all blocks

---

## 🔄 Your New Workflow

### Before (manual, 5-10 min per meeting):
1. Record on Google Recorder or Plaud
2. Open recording
3. Copy transcript manually
4. Paste into Google Doc
5. Share Doc link with Zo
6. Ask Zo to process
7. Wait for processing

### After (automated, 0 min per meeting):
1. **Record on Plaud** ← Only step!
2. *[AutoFlow emails transcript to Zo]*
3. *[Scheduled task processes overnight]*
4. *[You get email summary]*
5. **Done** ← Check results in morning

**Time saved**: ~5-10 min per meeting = **2-4 hours/month**

---

## 📊 Alternative: Google Recorder + Drive

If you prefer using Google Recorder (Pixel phone):

### One-time setup:
1. Create Google Drive folder: `Recordings/Transcripts-to-Process/`
2. Tell Zo to create scheduled task (scans Drive folder instead of email)

### Per-meeting workflow:
1. Record on Google Recorder
2. After meeting: Share → Save transcript to Drive folder
3. Rename file: `2025-10-16_internal-logan.txt` (include type in filename)
4. Scheduled task processes it overnight

**Pros**: Free, unlimited transcription  
**Cons**: One extra manual step (export to Drive)

---

## 🚨 Troubleshooting

### "Plaud AutoFlow not sending emails"
1. Check AutoFlow rule is **enabled** (toggle on)
2. Verify email address: `va@zo.computer` (no typos)
3. Check transcript generated (open recording in Plaud app)
4. Check spam folder (look for `@plaud.ai` sender)

### "Zo didn't process my meeting"
1. Check if scheduled task ran: Ask Zo to show scheduled task logs
2. Verify email arrived at va@zo.computer (ask Zo to check inbox)
3. Check N5/inbox/transcripts/ — transcript should be saved there
4. Manually trigger: "Zo, process the transcript in N5/inbox/transcripts/[filename].txt"

### "Meeting type was wrong (internal vs external)"
- Edit the processed meeting folder name if needed
- Or: Update scheduled task to improve detection logic
- Or: Send Zo a note with clearer keywords for detection

---

## 📝 Files Created

- file 'Documents/System/meeting-recording-automation-workflows.md' - Full comparison of all options
- file 'N5/scripts/plaud_meeting_processor.py' - Python script for scheduled task (skeleton)
- file 'Documents/System/SETUP_MEETING_AUTOMATION.md' - This setup guide

---

## ✅ Next Steps

1. **[ ] Complete Step 1-3 above** (Plaud AutoFlow + scheduled task)
2. **[ ] Test with dummy recording** (30-sec test)
3. **[ ] Verify next day** (check email + processed meeting folder)
4. **[ ] Archive this doc** once confirmed working

---

**Questions?** Ask Zo to troubleshoot or adjust the workflow.

---

*Created 2025-10-16 21:25 ET*
