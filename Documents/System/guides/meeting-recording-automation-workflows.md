# Meeting Recording → Processing Automation Workflows

**Created**: 2025-10-16  
**Purpose**: Streamline Google Recorder / Plaud recordings into N5 meeting processing system

---

## 🏆 RECOMMENDED: Plaud AutoFlow + Email to Zo

**Friction Level**: ⭐ Minimal (one-time setup, then hands-free)  
**Reliability**: High  
**Cost**: $0 (using existing Plaud subscription)

### How It Works

1. **Record meeting** on Plaud Note/NotePin (as usual)
2. **AutoFlow automatically**:
   - Uploads audio to Plaud cloud
   - Generates transcript + summary
   - **Emails transcript to `va@zo.computer`**
3. **Scheduled Zo task** (daily at 9 PM ET):
   - Checks for new emails from Plaud
   - Extracts transcript
   - Runs `meeting-process` command
   - Generates all intelligence blocks
   - Emails you completion summary

### Setup Steps

#### Step 1: Configure Plaud AutoFlow
1. Open Plaud app → Settings → AutoFlow
2. Create new AutoFlow rule:
   - **Trigger**: "When recording completes"
   - **Actions**:
     - ✅ Generate transcript
     - ✅ Generate summary
     - ✅ **Email to: `va@zo.computer`**
   - **Email subject format**: `Meeting - [Date] - [Title]` (or keep default)
   - **Email body**: Include transcript (NOT just summary)

#### Step 2: Create Zo Scheduled Task
```bash
# V will run this command to create scheduled task:
# Daily at 9 PM ET: check emails, process Plaud transcripts

/schedule "Check emails from Plaud and process any meeting transcripts using meeting-process command. For each transcript: (1) Determine if internal vs external meeting based on context, (2) Save to appropriate N5/inbox/transcripts/ location with date-prefixed filename, (3) Run meeting-process with correct meeting type, (4) Email me a summary of which meetings were processed." --rrule "FREQ=DAILY;BYHOUR=21;BYMINUTE=0" --delivery email
```

### Advantages
- ✅ **Zero manual steps** after recording
- ✅ Works for both in-person (Plaud device) and phone meetings
- ✅ Transcript quality = Plaud AI (very good)
- ✅ Can batch-process multiple meetings per day
- ✅ Email confirmation when processed

### Limitations
- Requires Plaud Pro subscription (300-600 min/month transcription quota)
- ~5-10 min delay for AutoFlow processing
- Scheduled task runs once daily (not instant)

---

## 🥈 ALTERNATIVE: Google Drive + Scheduled Check

**Friction Level**: ⭐⭐ Low (one extra tap per meeting)  
**Reliability**: Medium-High  
**Cost**: $0

### How It Works

1. **Record on Google Recorder**
2. **After meeting**: Tap "Share" → "Export transcript" → Save to Google Drive folder: `Recordings/Transcripts-to-Process/`
3. **Scheduled Zo task** (daily at 9 PM ET):
   - Scans Drive folder for new `.txt` files
   - Downloads each transcript
   - Processes via `meeting-process`
   - Moves processed files to `Recordings/Transcripts-Processed/`
   - Emails you summary

### Setup Steps

#### Step 1: Create Google Drive Folders
1. Open Google Drive
2. Create folder structure:
   ```
   Recordings/
   ├── Transcripts-to-Process/
   └── Transcripts-Processed/
   ```

#### Step 2: Workflow After Each Meeting
1. Open recording in Google Recorder
2. Tap ⋮ (three dots) → "Share transcript"
3. Save to Google Drive → `Recordings/Transcripts-to-Process/`
4. Rename file to include meeting type: `2025-10-16_internal-logan.txt` or `2025-10-16_external-clientname.txt`

#### Step 3: Create Zo Scheduled Task
```bash
# V will run this command:
/schedule "Check Google Drive folder 'Recordings/Transcripts-to-Process/' for new transcripts. Download each, process via meeting-process command (auto-detect meeting type from filename prefix), move to 'Recordings/Transcripts-Processed/' folder, and email me summary." --rrule "FREQ=DAILY;BYHOUR=21;BYMINUTE=0" --delivery email
```

### Advantages
- ✅ Works with free Google Recorder (Pixel phones only)
- ✅ Can batch rename files for better organization
- ✅ No transcription quota limits (Recorder is free)

### Limitations
- ❌ One extra manual step (export to Drive)
- ❌ Must remember to do it after each meeting
- ❌ Pixel phones only

---

## 🥉 ADVANCED: Android Automation (MacroDroid)

**Friction Level**: ⭐⭐⭐ Medium (complex setup)  
**Reliability**: Medium (can be flaky)  
**Cost**: $0 (free tier) or $3 one-time (Pro)

### How It Works

MacroDroid automation triggers when Google Recorder finishes recording, auto-exports transcript to email or Drive.

### Setup Steps

1. Install **MacroDroid** from Play Store
2. Create macro:
   - **Trigger**: "App/Activity Launched" → Google Recorder
   - **Condition**: "App in foreground" = False (recording ended)
   - **Action**: Simulate taps to:
     - Open share menu
     - Select "Gmail" or "Drive"
     - Send to `va@zo.computer`
3. Test thoroughly (screen automation is brittle)

### Advantages
- ✅ Fully automated once configured
- ✅ Works immediately after recording

### Limitations
- ❌ Complex to set up (requires screen coordinate mapping)
- ❌ Breaks if Google Recorder UI changes
- ❌ Unreliable across Android versions
- ❌ Not recommended unless you're comfortable debugging

---

## 📊 Comparison Matrix

| Solution | Friction | Reliability | Device | Cost | Recommended? |
|----------|----------|-------------|--------|------|--------------|
| **Plaud + AutoFlow** | ⭐ | ⭐⭐⭐⭐⭐ | Any | Subscription | ✅ **YES** |
| **Drive + Scheduled** | ⭐⭐ | ⭐⭐⭐⭐ | Pixel | Free | ✅ Good fallback |
| **MacroDroid** | ⭐⭐⭐ | ⭐⭐ | Android | Free-$3 | ⚠️ Advanced users |

---

## 🎯 My Recommendation for V

### Primary Workflow: **Plaud AutoFlow**
Since you already have Plaud, this is the obvious winner:
1. Enable AutoFlow email to `va@zo.computer`
2. Create scheduled task (9 PM daily check)
3. Done — every recording auto-processes overnight

### Fallback: **Google Drive** (if quota issues)
If you hit Plaud's monthly transcription limit:
1. Record on Google Recorder (free, unlimited)
2. One-tap export to Drive after meeting
3. Same scheduled task processes it

---

## 📋 Implementation Checklist

- [ ] **Configure Plaud AutoFlow** (Settings → AutoFlow → Email `va@zo.computer`)
- [ ] **Test AutoFlow** (record 30-sec dummy meeting, confirm email arrives)
- [ ] **Create scheduled task** (see command above)
- [ ] **Test end-to-end** (record → wait for AutoFlow → check Zo processing next day)
- [ ] **(Optional)** Set up Google Drive folders as backup method
- [ ] **(Optional)** Add calendar reminder to check processed meetings weekly

---

## 🔧 Troubleshooting

### Plaud AutoFlow not sending emails
- Check AutoFlow is enabled and email is correct
- Verify transcript generation completed (check Plaud app)
- Check spam folder for `no-reply@plaud.ai`

### Scheduled task not processing
- Check Zo task logs: `/schedule list`
- Verify emails are arriving at `va@zo.computer`
- Check inbox for Plaud emails

### Meeting type detection failing
- Ensure email subject or filename includes "internal" or "external"
- Or: Update scheduled task to ask V for meeting type if ambiguous

---

## 📖 Related Documentation

- file 'N5/commands/meeting-process.md' - Meeting processing command
- file 'N5/prefs/block_type_registry.json' - Meeting types and blocks
- file 'N5/prefs/operations/scheduled-task-protocol.md' - Scheduled task standards

---

**Next Steps**: V to decide on Plaud AutoFlow vs. Drive method, then Zo will implement scheduled task.

---

*Created 2025-10-16 21:21 ET*
