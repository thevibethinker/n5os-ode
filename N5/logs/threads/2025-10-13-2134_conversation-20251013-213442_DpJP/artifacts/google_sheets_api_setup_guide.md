# Google Sheets API Setup Guide for Job Sourcing

**For:** Vrijen Attawar  
**Date:** 2025-10-13  
**Goal:** Enable automated job sourcing to Google Sheets without manual intervention

---

## What We're Setting Up

**Service Account** = A robot user that your script can use to access Google Sheets automatically, without you needing to log in each time.

**What You'll Get:** A JSON file with credentials that the script will use to authenticate.

---

## Step-by-Step Setup Process

### Part 1: Google Cloud Console Setup (10 minutes)

#### Step 1: Access Google Cloud Console

1. Go to: **https://console.cloud.google.com/**
2. Sign in with your Careerspan Google account
3. Select your company's project (or create a new one if needed)

**If you need to create a project:**
- Click "Select a project" dropdown at the top
- Click "New Project"
- Name it something like "Careerspan Automation" or "Job Sourcing"
- Click "Create"

---

#### Step 2: Enable Google Sheets API

1. In the left sidebar, go to: **APIs & Services → Library**
2. Search for: **"Google Sheets API"**
3. Click on it
4. Click the blue **"Enable"** button
5. Wait for it to enable (takes ~10 seconds)

**Repeat for Google Drive API:**
1. Go back to Library
2. Search for: **"Google Drive API"**
3. Click on it
4. Click **"Enable"**

---

#### Step 3: Create Service Account

1. In the left sidebar, go to: **APIs & Services → Credentials**
2. Click **"+ Create Credentials"** at the top
3. Select **"Service Account"**
4. Fill in the form:
   - **Service account name:** `job-sourcing-bot` (or any name you like)
   - **Service account ID:** (auto-generated, leave it)
   - **Description:** "Automated job sourcing to Google Sheets"
5. Click **"Create and Continue"**
6. **Grant this service account access to project:**
   - Role: Select **"Editor"** (or "Basic → Editor")
   - Click **"Continue"**
7. **Grant users access:** (Skip this)
   - Click **"Done"**

---

#### Step 4: Create & Download Credentials JSON

1. You should now see your service account in the list
2. Click on the **service account email** (looks like: `job-sourcing-bot@project-name.iam.gserviceaccount.com`)
3. Go to the **"Keys"** tab at the top
4. Click **"Add Key" → "Create new key"**
5. Select **"JSON"** format
6. Click **"Create"**

**A JSON file will download automatically** - this is your credentials file!

**IMPORTANT:** 
- Keep this file secure - it's like a password
- Don't share it publicly or commit to git
- We'll upload it to your Zo workspace securely

---

### Part 2: Share Google Sheet with Service Account

#### Step 5: Get Service Account Email

From the downloaded JSON file, find the email that looks like:
```
job-sourcing-bot@careerspan-automation.iam.gserviceaccount.com
```

Or just look in Google Cloud Console → Service Accounts → Email column

---

#### Step 6: Share Your Google Sheet

1. Open your "Sourced Jobs" Google Sheet
   - URL: https://drive.google.com/file/d/1LMShFZQ7IwZpsOxs1RWB67LHV1cFmClc/view
   - **Note:** If this is a CSV, you'll need to convert it to a Google Sheet first:
     - Open the CSV
     - File → Save as Google Sheets
     - Use the new Google Sheet's ID going forward

2. Click the **"Share"** button (top right)
3. Paste the service account email
4. Set permission to **"Editor"**
5. Uncheck "Notify people" (it's a robot, no need to email it)
6. Click **"Share"**

**The sheet is now accessible by your script!**

---

### Part 3: Upload Credentials to Zo (Secure)

#### Step 7: Upload the JSON File

**Option A: Via Zo's file upload**
1. In your Zo workspace, drag and drop the JSON file
2. Place it in: `/home/workspace/N5/config/`
3. Rename it to: `google_service_account.json`

**Option B: I can help you upload it**
- You can paste the contents of the JSON file to me
- I'll create it securely in the right location
- We'll set proper permissions (read-only for the script)

---

### Part 4: Update the Script

#### Step 8: Install Required Python Libraries

I'll run these commands to install the Google Sheets API libraries:

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

#### Step 9: Update Script Configuration

I'll need to update `N5/scripts/n5_job_source_extract.py` with:

1. **Credentials path:**
   ```python
   SERVICE_ACCOUNT_FILE = '/home/workspace/N5/config/google_service_account.json'
   ```

2. **Spreadsheet ID:**
   - If your file is a Google Sheet (not CSV), get the ID from the URL:
   - URL format: `https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit`
   - Example: `1LMShFZQ7IwZpsOxs1RWB67LHV1cFmClc`

3. **Sheet name:** (the tab name, usually "Sheet1")

---

## Verification Checklist

Before we proceed with implementation:

- [ ] Google Sheets API enabled
- [ ] Google Drive API enabled
- [ ] Service account created
- [ ] Service account JSON downloaded
- [ ] Service account email copied
- [ ] Google Sheet shared with service account (as Editor)
- [ ] JSON file uploaded to Zo workspace
- [ ] Spreadsheet ID identified

---

## Security Best Practices

✅ **Do:**
- Store credentials in `/home/workspace/N5/config/`
- Add `*.json` to `.gitignore` if using version control
- Set file permissions to 600 (read/write for owner only)

❌ **Don't:**
- Share the JSON file publicly
- Commit it to public repositories
- Email it unencrypted

---

## Troubleshooting Common Issues

### Issue: "Permission denied" when sharing sheet
**Solution:** Make sure you're sharing with the service account email (ends with `@*.iam.gserviceaccount.com`), not a regular Gmail address.

### Issue: "API not enabled" error
**Solution:** Go back to APIs & Services → Library and verify both Google Sheets API and Google Drive API show as "Enabled"

### Issue: JSON file won't download
**Solution:** Check your browser's download folder, or try creating the key again.

### Issue: Can't find spreadsheet ID
**Solution:** 
- If the file is a CSV, convert it to Google Sheet first (File → Save as Google Sheets)
- The ID is in the URL: `docs.google.com/spreadsheets/d/[THIS_PART]/edit`

---

## What Happens After Setup

Once configured, the workflow will be:

1. **You:** Run `n5 job-source-extract <job-url>` (or just send me a URL)
2. **Script:** Extracts job posting automatically
3. **Script:** Appends to Google Sheet via API (no manual steps)
4. **You:** See the new row in your Google Sheet immediately

**No more manual intervention needed!**

---

## Next Steps

1. **Complete Part 1-2** (Google Cloud setup, share sheet)
2. **Let me know when done** - I'll help with Part 3-4
3. **Test with a sample job URL** to verify everything works

---

**Questions? Let me know where you get stuck and I'll guide you through it.**

*Guide created: 2025-10-13 17:14 ET*
