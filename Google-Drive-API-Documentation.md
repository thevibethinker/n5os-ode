---
created: 2024-01-11
last_edited: 2024-01-11
version: 1.0
---

# Google Drive API & Zo Tool Documentation

Comprehensive guide to using Google Drive with Zo and the Google Drive API.

## Table of Contents

1. [Zo's Google Drive Integration](#zos-google-drive-integration)
2. [Available Google Drive Tools](#available-google-drive-tools)
3. [Google Drive API Documentation](#google-drive-api-documentation)
4. [Authentication Methods](#authentication-methods)
5. [Common Use Cases & Examples](#common-use-cases--examples)
6. [Additional Resources](#additional-resources)

## Zo's Google Drive Integration

Zo provides built-in integration with Google Drive through the `use_app_google_drive` tool. This integration is powered by Pipedream and provides access to your Google Drive accounts.

### Connected Accounts

You have two Google Drive accounts connected:
- **Personal**: attawar.v@gmail.com
- **Business**: vrijen@mycareerspan.com

When using the Google Drive tools, you can specify which account to use by providing the `email` parameter.

### Basic Tool Usage

```python
# List available tools
list_app_tools(app_slug="google_drive")

# Use a specific tool
use_app_google_drive(
    tool_name="google_drive-list-files",
    configured_props={
        "folderId": "root",
        "fields": "files(id,name,mimeType)"
    },
    email="vrijen@mycareerspan.com"  # Optional: specify account
)
```

## Available Google Drive Tools

Zo provides 40+ Google Drive operations through the integration:

### File Operations
- `google_drive-upload-file` - Upload files to Drive
- `google_drive-download-file` - Download files from Drive
- `google_drive-list-files` - List files in a folder
- `google_drive-get-file-by-id` - Get specific file metadata
- `google_drive-find-file` - Search for files by name
- `google_drive-find-spreadsheets` - Find spreadsheet files
- `google_drive-find-forms` - Find Google Form documents
- `google_drive-update-file` - Update file metadata/content
- `google_drive-copy-file` - Create a copy of a file
- `google_drive-move-file` - Move files between folders
- `google_drive-move-file-to-trash` - Move files to trash
- `google_drive-delete-file` - Permanently delete files

### Folder Operations
- `google_drive-create-folder` - Create new folders
- `google_drive-find-folder` - Search for folders by name
- `google_drive-get-folder-id-for-path` - Get folder ID from path

### Shared Drive Operations
- `google_drive-get-shared-drive` - Get shared drive metadata
- `google_drive-search-shared-drives` - Search shared drives
- `google_drive-create-shared-drive` - Create shared drives
- `google_drive-update-shared-drive` - Update shared drive settings
- `google_drive-delete-shared-drive` - Delete shared drives

### Sharing & Permissions
- `google_drive-add-file-sharing-preference` - Add sharing permissions
- `google_drive-list-access-proposals` - List access requests
- `google_drive-resolve-access-proposal` - Accept/deny access requests

### Comments & Collaboration
- `google_drive-add-comment` - Add comments to files
- `google_drive-list-comments` - List comments on files
- `google_drive-get-comment` - Get specific comment
- `google_drive-update-comment` - Update comment content
- `google_drive-delete-comment` - Delete comments
- `google_drive-reply-to-comment` - Reply to comments
- `google_drive-list-replies` - List comment replies
- `google_drive-get-reply` - Get specific reply
- `google_drive-update-reply` - Update reply content
- `google_drive-delete-reply` - Delete replies
- `google_drive-resolve-comment` - Mark comments as resolved

### File Creation
- `google_drive-create-file-from-text` - Create files from plain text
- `google_drive-create-file-from-template` - Create files from templates
- `google_drive-get-current-user` - Get current user metadata

**Reference**: All tools include links to official Google Drive API documentation for detailed parameters and usage.

## Google Drive API Documentation

### Official API Reference

The Google Drive API is a RESTful API that allows programmatic access to Google Drive functionality. Key resources include:

**API Versions:**
- **v3** (current) - Latest version with improved performance
- **v2** (legacy) - Older version still supported

**Core API Resources:**

1. **Files** - Core file operations
   - Reference: https://developers.google.com/drive/api/reference/rest/v3/files
   - Operations: create, get, update, delete, copy, list, export

2. **Permissions** - Sharing and access control
   - Reference: https://developers.google.com/drive/api/reference/rest/v3/permissions
   - Operations: create, get, update, delete, list

3. **Comments** - File commenting system
   - Reference: https://developers.google.com/workspace/drive/api/reference/rest/v3/comments
   - Operations: create, get, update, delete, list

4. **Replies** - Comment replies
   - Reference: https://developers.google.com/workspace/drive/api/reference/rest/v3/replies
   - Operations: create, get, update, delete, list

5. **Drives** - Shared drive management
   - Reference: https://developers.google.com/drive/api/reference/rest/v3/drives
   - Operations: create, get, update, delete, list, hide, unhide

6. **Changes** - Track file changes
   - Reference: https://developers.google.com/drive/api/reference/rest/v3/changes
   - Operations: list, getStartPageToken, watch

### Drive API Key Features

- **File Management**: Upload, download, organize, and delete files
- **Search**: Powerful query-based file searching
- **Sharing**: Granular permission control
- **Collaboration**: Comments, suggestions, and real-time editing
- **Change Tracking**: Monitor file modifications
- **Revision History**: Access file version history
- **Export**: Convert Google Workspace documents to various formats

### API Limits and Quotas

**Usage Limits:**
- Queries per 100 seconds: 1,000 (can be increased to 10,000)
- Queries per 100 seconds per user: 100

**Best Practices:**
- Use batch requests when possible
- Implement exponential backoff for retries
- Use field masks to reduce response size
- Handle rate limit errors gracefully

**Reference**: https://developers.google.com/workspace/drive/api/guides/limits

## Authentication Methods

### 1. OAuth 2.0 (User Authentication)

Used for accessing user-owned files and data with user consent.

**Flow:**
1. User grants permission through consent screen
2. Application receives access token
3. Token used for API requests
4. Token can be refreshed when expired

**Python Example:**
```python
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

service = build('drive', 'v3', credentials=creds)
```

**Reference**: https://developers.google.com/identity/protocols/oauth2

### 2. Service Account (Server-to-Server)

Used for server-side applications without user interaction.

**Best For:**
- Automated backups
- Server-side file processing
- Applications accessing their own data

**Python Example:**
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service-account.json'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('drive', 'v3', credentials=creds)
```

**Note**: Service accounts require explicit sharing or domain-wide delegation.

### 3. API Key (Limited Access)

Used for public data access only (cannot access private user files).

**Limitations:**
- Read-only access to public files
- Cannot access user data
- Limited quota

## Common Use Cases & Examples

### 1. File Upload and Management

```python
# Upload a file
file_metadata = {'name': 'document.pdf'}
media = MediaFileUpload('document.pdf', mimetype='application/pdf')
file = service.files().create(
    body=file_metadata, media_body=media, fields='id'
).execute()

print(f'File ID: {file.get("id")}')
```

### 2. File Search and Listing

```python
# List files with query
results = service.files().list(
    q="name contains 'report' and mimeType='application/pdf'",
    pageSize=10,
    fields="nextPageToken, files(id, name)"
).execute()

files = results.get('files', [])
for file in files:
    print(f"{file['name']} ({file['id']})")
```

### 3. Sharing and Permissions

```python
# Share file with user
permission = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': 'user@example.com'
}

service.permissions().create(
    fileId=file_id,
    body=permission,
    fields='id'
).execute()
```

### 4. Export Google Workspace Documents

```python
# Export Google Doc as PDF
request = service.files().export_media(
    fileId=document_id,
    mimeType='application/pdf'
)

with open('document.pdf', 'wb') as f:
    f.write(request.execute())
```

### 5. Monitor Changes

```python
# Get starting page token
response = service.changes().getStartPageToken().execute()
start_page_token = response.get('startPageToken')

# List changes
changes = service.changes().list(
    pageToken=start_page_token,
    fields='*'
).execute()
```

### 6. Zo Integration Example

```python
# Using Zo's Google Drive tool to download a file
use_app_google_drive(
    tool_name="google_drive-download-file",
    configured_props={
        "fileId": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
        "filePath": "/tmp/report.pdf",
        "mimeType": "application/pdf"
    },
    email="vrijen@mycareerspan.com"
)
```

## Search Query Syntax

Google Drive API uses a powerful query language for searching files.

**Common Query Examples:**

```
# Find PDF files
mimeType = 'application/pdf'

# Files in specific folder (including subfolders)
'1234567890' in parents

# Files modified recently
modifiedTime > '2024-01-01T00:00:00'

# Files with specific name
name contains 'project'

# Combine conditions
mimeType = 'application/pdf' and modifiedTime > '2024-01-01'

# Search in shared drives
sharedWithMe = true

# Find trashed files
trashed = true

# Full text search
fullText contains 'important document'
```

**Reference**: https://developers.google.com/workspace/drive/api/guides/ref-search-terms

## MIME Types

**Common MIME Types:**
- PDF: `application/pdf`
- JPEG: `image/jpeg`
- Plain text: `text/plain`
- CSV: `text/csv`
- Microsoft Word: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Microsoft Excel: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

**Google Workspace Types:**
- Google Docs: `application/vnd.google-apps.document`
- Google Sheets: `application/vnd.google-apps.spreadsheet`
- Google Slides: `application/vnd.google-apps.presentation`
- Google Forms: `application/vnd.google-apps.form`
- Google Drive folder: `application/vnd.google-apps.folder`

**Export Formats**: https://developers.google.com/workspace/drive/api/guides/ref-export-formats

## Additional Resources

### Official Documentation
- **Main API Docs**: https://developers.google.com/workspace/drive/api/guides/about-sdk
- **API Reference**: https://developers.google.com/drive/api/reference/rest/v3
- **Python Quickstart**: https://developers.google.com/workspace/drive/api/quickstart/python
- **OAuth Guide**: https://developers.google.com/identity/protocols/oauth2

### Client Libraries
- **Python**: https://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.html
- **JavaScript**: https://github.com/google/google-api-javascript-client
- **Java**: https://developers.google.com/api-client-library/java
- **Node.js**: https://googleapis.dev/nodejs/googleapis/latest/drive/index.html

### Zo Resources
- **Pipedream Google Drive Integration**: https://pipedream.com/apps/google-drive
- **Tool Documentation**: Each tool includes links to relevant Google API docs

### Community and Support
- **Stack Overflow**: https://stackoverflow.com/questions/tagged/google-drive-api
- **Google Workspace Developer Community**: https://developers.google.com/workspace/community
- **Issue Tracker**: https://issuetracker.google.com/issues?q=componentid:191650

## Best Practices

1. **Authentication**: Use service accounts for server-side applications
2. **Error Handling**: Implement exponential backoff for rate limits
3. **Performance**: Use field masks to request only needed data
4. **Security**: Never expose API keys or credentials
5. **Quotas**: Monitor usage and request quota increases when needed
6. **Testing**: Use test accounts and files during development
7. **Permissions**: Request minimum necessary scopes

---

*Document compiled from Google Drive API documentation and Zo tool specifications.*

**Google Drive API References:** 
- https://developers.google.com/drive/api/v3/reference [^1]
- https://developers.google.com/workspace/drive/api/guides/about-sdk [^2]
- https://developers.google.com/identity/protocols/oauth2 [^3]

**Zo Integration:** Powered by Pipedream Google Drive integration with 40+ available operations.

[^1]: https://developers.google.com/drive/api/v3/reference
[^2]: https://developers.google.com/workspace/drive/api/guides/about-sdk
[^3]: https://developers.google.com/identity/protocols/oauth2

