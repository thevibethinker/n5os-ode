# Job Sourcing Google Sheets API Troubleshooting Analysis

**Date:** 2025-10-13  
**Status:** CRITICAL ISSUES IDENTIFIED

---

## Executive Summary

The current `n5_job_source_extract.py` script **does not actually connect to Google Sheets API**. It's a stub/skeleton that requires Zo to manually handle all Google Drive operations. This explains the connection failures.

---

## Critical Problem: No Google API Integration

### Current Script Analysis

**Location:** `file 'N5/scripts/n5_job_source_extract.py'`

**Issues Identified:**

1. **No Google API Libraries**
   - Missing: `google-api-python-client`, `google-auth`, `gspread`
   - No imports for Google Sheets/Drive APIs
   - No authentication setup

2. **Stub Functions Only**
   - `update_google_sheet()` returns `{"status": "pending_zo_update"}` 
   - Expects Zo to manually handle ALL Google Drive operations
   - No actual API calls

3. **Hard-Coded File ID**
   ```python
   GDRIVE_FILE_ID = "1LMShFZQ7IwZpsOxs1RWB67LHV1cFmClc"
   ```
   - File ID is present but never used in actual API calls

4. **Workflow Status Only**
   - Script outputs JSON with "next steps" for Zo
   - No automation - just a checklist

---

## Common Google Sheets API Connection Problems (Research Findings)

Based on web research, here are the top issues when working with Google Sheets API:

### 1. **Authentication & Authorization (Most Common)**

**Problem:** Token expiration, refresh token issues, insufficient scopes

**Symptoms:**
- `401 Unauthorized` errors
- `403 Insufficient authentication scopes`
- `Token has been revoked` errors
- `RefreshError` in PyDrive/gspread

**Solutions:**[^1][^2]
- Enable Google Sheets API in Google Cloud Console
- Use OAuth2 with proper scopes:
  ```python
  SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
  ```
- Set `access_type='offline'` to get refresh tokens
- Set `prompt='consent'` to force refresh token generation
- Service Account credentials expire less frequently than user OAuth

### 2. **Missing API Enablement**

**Problem:** API not enabled in Google Cloud Project

**Symptoms:**
- `403 The caller does not have permission`
- `Error 403: The Google Sheets or Google Drive API is not enabled`

**Solutions:**[^3]
- Go to Google Cloud Console → APIs & Services → Library
- Search for "Google Sheets API" and enable it
- Also enable "Google Drive API" if working with file operations

### 3. **Credentials File Issues**

**Problem:** Missing or improperly configured credentials

**Symptoms:**
- `File not found error for credentials.json`
- `client_secret.json` not found

**Solutions:**[^4]
- Download credentials from Google Cloud Console
- Place in project directory
- Ensure file path is correct in code
- For service accounts, share the sheet with service account email

### 4. **Insufficient Permissions**

**Problem:** Sheet not shared with service account or OAuth user lacks permissions

**Symptoms:**
- `403 The user does not have sufficient permissions`
- Can read but not write

**Solutions:**[^5]
- Share Google Sheet with service account email (found in JSON credentials)
- Grant "Editor" permissions, not just "Viewer"
- Check if sheet is in a Shared Drive that requires special permissions

### 5. **API Rate Limits & Quotas**

**Problem:** Exceeding Google API quotas

**Symptoms:**
- `429 Too Many Requests`
- `500 Internal error encountered`

**Solutions:**[^6]
- Default: 60 requests per minute per user
- Use batch operations (`batchUpdate`) instead of multiple single calls
- Implement exponential backoff retry logic
- Check quota usage in Google Cloud Console

### 6. **Incorrect API Method Usage**

**Problem:** Using wrong method or parameters

**Common Mistakes:**
- Using `update()` when should use `append()`
- Wrong `valueInputOption` (should be `"RAW"` or `"USER_ENTERED"`)
- Incorrect range format (should be `"Sheet1!A1:D10"`)
- Not specifying `insertDataOption` for append

**Correct Append Syntax:**[^7]
```python
body = {
    'values': [['Date', 'Title', 'Location', 'Description', 'URL']]
}
result = service.spreadsheets().values().append(
    spreadsheetId=SPREADSHEET_ID,
    range='Sheet1!A1',  # Starting point
    valueInputOption='USER_ENTERED',
    insertDataOption='INSERT_ROWS',
    body=body
).execute()
```

### 7. **Python Library Issues**

**Problem:** Version conflicts, missing dependencies

**Solutions:**
- Install required packages:
  ```bash
  pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
  # OR for simpler API:
  pip install gspread oauth2client
  ```

---

## Zo's Google Drive Integration

Zo provides built-in Google Drive integration via **app tools**:

### Available Tools:
- `use_app_google_drive` - Direct Drive operations
- Tools include: `upload-file`, `update-file`, `download-file`, `find-spreadsheets`

### Current Implementation Gap:

The script expects Zo to:
1. Extract webpage content manually
2. Parse job data manually  
3. Update Google Sheet manually via `use_app_google_drive`

**This is inefficient and error-prone.**

---

## Recommended Solutions (Priority Order)

### Option 1: **Use Zo's Native Google Drive Tools** (Recommended)
**Pros:** No authentication setup, works immediately  
**Cons:** Requires Zo to be in the loop for each execution

**Implementation:**
- Refactor script to output structured JSON
- Have Zo call `use_app_google_drive` with the `update-file` tool
- For Google Sheets, may need to use `google_drive-download-file`, modify CSV, then `google_drive-upload-file`

### Option 2: **Implement Proper Google Sheets API** (Best for Automation)
**Pros:** Fully automated, no manual intervention  
**Cons:** Requires setup, authentication config

**Implementation Steps:**
1. Enable Google Sheets API in Cloud Console
2. Create Service Account
3. Download credentials JSON
4. Share sheet with service account email
5. Rewrite script with proper API calls

**Example Code:**
```python
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = '/home/workspace/N5/config/google_credentials.json'

creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# Append row
values = [[date, title, location, description, url]]
body = {'values': values}
result = service.spreadsheets().values().append(
    spreadsheetId=SPREADSHEET_ID,
    range='Sheet1!A:E',
    valueInputOption='USER_ENTERED',
    insertDataOption='INSERT_ROWS',
    body=body
).execute()
```

### Option 3: **Use `gspread` Library** (Simpler API)
**Pros:** Much simpler API than official Google Sheets API  
**Cons:** Still requires authentication setup

**Example:**
```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'credentials.json', scope)
client = gspread.authorize(creds)

# Open sheet and append
sheet = client.open_by_key(SPREADSHEET_ID).sheet1
sheet.append_row([date, title, location, description, url])
```

---

## Immediate Action Items

### 1. **Clarify Integration Approach**
**Questions for V:**
- Do you have Google Cloud credentials set up?
- Should this be fully automated (needs service account) or Zo-assisted?
- Is the file ID `1LMShFZQ7IwZpsOxs1RWB67LHV1cFmClc` a CSV or Google Sheet?

### 2. **Check Current File Type**
- Need to verify if target file is CSV or native Google Sheet
- Different update methods depending on type

### 3. **Test Zo's Google Drive Connection**
- Verify Zo can access the file
- Test with simple read operation first

---

## Testing Checklist

- [ ] Verify Google Drive app is connected in Zo settings
- [ ] Confirm file ID exists and is accessible
- [ ] Test read access to the file
- [ ] Determine file type (CSV vs Google Sheet)
- [ ] Test write/append permissions
- [ ] Implement error handling for API failures
- [ ] Add retry logic with exponential backoff
- [ ] Verify data format matches sheet columns

---

## References

[^1]: https://stackoverflow.com/questions/79580274/how-to-fix-an-apparently-expired-refresh-token
[^2]: https://developers.google.com/workspace/drive/api/troubleshoot-authentication-authorization
[^3]: https://automategeniushub.com/ultimate-guide-to-n8n-google-sheets-integration/
[^4]: https://developers.google.com/workspace/drive/labels/troubleshoot-authentication-authorization
[^5]: https://developers.google.com/workspace/sheets/api/quickstart/python
[^6]: https://moldstud.com/articles/p-how-to-check-api-quotas-limits-and-debug-google-drive-issues
[^7]: https://developers.google.com/workspace/sheets/api/guides/values

---

**Next Steps:** Await V's direction on preferred implementation approach.

*Analysis completed: 2025-10-13 17:08 ET*
