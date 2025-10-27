# Google Drive Integration Preferences

**Module:** Integration  
**Version:** 2.0.0  
**Date:** 2025-10-09

---

## Preference

**Always first try to access Google Drive related content through the integration**, versus through a web browser or consumer access.

**Rationale:** 
- Integration provides programmatic access
- More reliable than web scraping
- Better for automation
- Respects authentication properly

---

## Access Workflow

### Step 1: Verify Integration

```
list_app_tools(app_slug="google_drive")
```

**Check:** Confirm Google Drive app integration is connected

---

### Step 2: Retrieve File Metadata

```
use_app_google_drive(
    tool_name="google_drive-get-file-by-id",
    configured_props={
        "fileId": "[file_id]"
    }
)
```

**Returns:** File metadata including name, type, permissions

---

### Step 3: Download File Content

```
use_app_google_drive(
    tool_name="google_drive-download-file",
    configured_props={
        "fileId": "[file_id]",
        "filePath": "/tmp/filename.txt",
        "mimeType": "text/plain"  # For Google Docs export
    }
)
```

**MIME types for Google formats:**
- Google Docs → `text/plain` or `application/pdf`
- Google Sheets → `text/csv` or `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Google Slides → `application/pdf`

---

### Step 4: Retrieve to Workspace

If tool returns a download URL:

```bash
curl -o /home/workspace/filename.txt "[download_url]"
```

**Target:** Always save to `/home/workspace/` unless user specifies otherwise

---

### Step 5: Read Downloaded File

```
read_file(target_file="/home/workspace/filename.txt")
```

---

## Common Patterns

### Fetching a Shared Document

**User provides:** Google Drive link or file ID

**Workflow:**
1. Extract file ID from URL if needed
2. Get metadata to determine type
3. Choose appropriate MIME type for export
4. Download to workspace
5. Read and process content

---

### Listing Files in Folder

```
use_app_google_drive(
    tool_name="google_drive-list-files",
    configured_props={
        "folderId": "[folder_id]",
        "pageSize": 100
    }
)
```

---

### Searching Drive

```
use_app_google_drive(
    tool_name="google_drive-search-files",
    configured_props={
        "query": "name contains 'keyword'",
        "pageSize": 20
    }
)
```

**Query syntax:** Google Drive search query format

---

## Fallback: Web Browser Access

**Only use if integration fails or is not available.**

### When to Fall Back
- Integration not connected
- File permissions prevent API access
- Specific Drive feature not supported by API

### Browser Access
```
view_webpage(url="https://drive.google.com/file/d/[file_id]/view")
```

**Note:** This is slower and less reliable. Always try integration first.

---

## File ID Extraction

### From Share Link

**Pattern:** `https://drive.google.com/file/d/[FILE_ID]/view`

**Extract:** Capture string between `/d/` and `/view`

**Example:**
```
URL: https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j/view
ID:  1a2b3c4d5e6f7g8h9i0j
```

---

### From Open Link

**Pattern:** `https://docs.google.com/document/d/[FILE_ID]/edit`

**Extract:** Capture string between `/d/` and `/edit`

---

## Error Handling

### Permission Denied

**Cause:** User's Google account doesn't have access

**Solution:**
1. Ask user to grant access via Drive UI
2. Or ask user to provide file another way

---

### File Not Found

**Cause:** Invalid file ID or file deleted

**Solution:**
1. Verify file ID is correct
2. Ask user to confirm file still exists
3. Try web browser access as fallback

---

### Integration Not Connected

**Cause:** Google Drive app not authorized

**Solution:**
1. Inform user integration is not connected
2. Direct to settings: https://va.zo.computer/settings
3. Fall back to web browser access if urgent

---

## Related Files

- **App Tools (General):** Zo system app integration
- **Coding Agent:** `file 'N5/prefs/integration/coding-agent.md'`

---

## Change Log

### v2.0.0 — 2025-10-09
- Extracted from monolithic prefs.md
- Added detailed step-by-step workflow
- Added MIME type reference for Google formats
- Added file ID extraction patterns
- Added error handling section
- Added fallback procedures
