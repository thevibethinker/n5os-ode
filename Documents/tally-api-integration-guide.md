# Tally.so API Integration Guide

**Document Type:** Technical Integration Guide  
**Created:** 2025-10-24  
**Purpose:** Complete reference for integrating with Tally.so using API keys

---

## Overview

Tally.so provides a REST API (currently in public beta) for programmatic access to forms, submissions, webhooks, and workspaces. The API enables custom integrations for automation, data retrieval, and form management.

---

## Authentication

### API Key Setup

1. **Generate API Key:**
   - Navigate to **Settings** > [**API Keys**](https://tally.so/settings/api-keys)
   - Click "Create API key"
   - Copy and securely store the key (it won't be shown again)

2. **Key Characteristics:**
   - Tied to a specific user account
   - Inherits all user permissions
   - Revoked if user is removed from organization
   - Currently no fine-grained permission controls

3. **Usage:**
   ```bash
   Authorization: Bearer tly-xxxx
   ```

### Base URL
```
https://api.tally.so
```

All requests must use HTTPS (unencrypted HTTP is not allowed).

---

## Rate Limits

- **Limit:** 100 requests per minute
- **Best Practice:** Use webhooks instead of polling for real-time data
- **Response Code:** `429` when rate limited

---

## Core API Endpoints

### Forms

#### List Forms
```bash
GET https://api.tally.so/forms
Authorization: Bearer <token>
```

#### Get Specific Form
```bash
GET https://api.tally.so/forms/{formId}
Authorization: Bearer <token>
```

#### Create Form
```bash
POST https://api.tally.so/forms
Authorization: Bearer <token>
Content-Type: application/json

{
  "workspaceId": "<string>",
  "templateId": "<string>",
  "title": "<string>"
}
```

#### Update Form
```bash
PATCH https://api.tally.so/forms/{formId}
Authorization: Bearer <token>
Content-Type: application/json
```

#### Delete Form
```bash
DELETE https://api.tally.so/forms/{formId}
Authorization: Bearer <token>
```

---

### Submissions

#### List Submissions
```bash
GET https://api.tally.so/forms/{formId}/submissions?page=1&filter=all
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (number): Page number for pagination (default: 1)
- `filter` (enum): `all`, `completed`, `partial`
- `startDate` (ISO 8601): Filter submissions on/after date
- `endDate` (ISO 8601): Filter submissions on/before date
- `afterId` (string): Get submissions after specific submission ID

**Response Structure:**
```json
{
  "page": 1,
  "limit": 50,
  "hasMore": true,
  "totalNumberOfSubmissionsPerFilter": {
    "all": 123,
    "completed": 100,
    "partial": 23
  },
  "questions": [
    {
      "id": "<string>",
      "type": "INPUT_TEXT",
      "title": "Question text",
      "fields": [...]
    }
  ],
  "submissions": [
    {
      "id": "<string>",
      "formId": "<string>",
      "isCompleted": true,
      "submittedAt": "2023-11-07T05:31:56Z",
      "responses": [
        {
          "questionId": "<string>",
          "value": "<string>"
        }
      ]
    }
  ]
}
```

#### Get Single Submission
```bash
GET https://api.tally.so/forms/{formId}/submissions/{submissionId}
Authorization: Bearer <token>
```

#### Delete Submission
```bash
DELETE https://api.tally.so/forms/{formId}/submissions/{submissionId}
Authorization: Bearer <token>
```

---

### Webhooks (Recommended for Real-Time Data)

Webhooks provide instant notifications when forms are submitted, avoiding rate limits and polling overhead.

#### Create Webhook
```bash
POST https://api.tally.so/webhooks
Authorization: Bearer <token>
Content-Type: application/json

{
  "formId": "<string>",
  "url": "https://your-endpoint.com/webhook",
  "signingSecret": "optional-secret-key",
  "httpHeaders": [
    {
      "name": "X-Custom-Header",
      "value": "custom-value"
    }
  ],
  "eventTypes": ["FORM_RESPONSE"],
  "externalSubscriber": "optional-identifier"
}
```

**Response:**
```json
{
  "id": "<webhook-id>",
  "url": "https://your-endpoint.com/webhook",
  "eventTypes": ["FORM_RESPONSE"],
  "isEnabled": true,
  "createdAt": "2023-11-07T05:31:56Z"
}
```

#### List Webhooks
```bash
GET https://api.tally.so/webhooks?formId={formId}
Authorization: Bearer <token>
```

#### Update Webhook
```bash
PATCH https://api.tally.so/webhooks/{webhookId}
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://new-endpoint.com",
  "isEnabled": false
}
```

#### Delete Webhook
```bash
DELETE https://api.tally.so/webhooks/{webhookId}
Authorization: Bearer <token>
```

#### List Webhook Events
```bash
GET https://api.tally.so/webhooks/{webhookId}/events
Authorization: Bearer <token>
```

#### Retry Webhook Event
```bash
POST https://api.tally.so/webhooks/{webhookId}/events/{eventId}/retry
Authorization: Bearer <token>
```

---

### Webhook Payload Structure

When a form is submitted, Tally sends a POST request to your webhook URL:

```json
{
  "eventId": "a4cb511e-d513-4fa5-baee-b815d718dfd1",
  "eventType": "FORM_RESPONSE",
  "createdAt": "2023-06-28T15:00:21.889Z",
  "data": {
    "responseId": "2wgx4n",
    "submissionId": "2wgx4n",
    "respondentId": "dwQKYm",
    "formId": "VwbNEw",
    "formName": "Contact Form",
    "createdAt": "2023-06-28T15:00:21.000Z",
    "fields": [
      {
        "key": "question_3EKz4n",
        "label": "Name",
        "type": "INPUT_TEXT",
        "value": "John Doe"
      },
      {
        "key": "question_w4Q4Xn",
        "label": "Email",
        "type": "INPUT_EMAIL",
        "value": "[email protected]"
      }
    ]
  }
}
```

**Field Types Supported:**
- `INPUT_TEXT`, `INPUT_NUMBER`, `INPUT_EMAIL`, `INPUT_PHONE_NUMBER`
- `INPUT_LINK`, `INPUT_DATE`, `INPUT_TIME`
- `TEXTAREA`, `MULTIPLE_CHOICE`, `CHECKBOXES`, `DROPDOWN`, `MULTI_SELECT`
- `FILE_UPLOAD`, `PAYMENT`, `RATING`, `RANKING`, `LINEAR_SCALE`
- `SIGNATURE`, `MATRIX`, `HIDDEN_FIELDS`, `CALCULATED_FIELDS`

---

### Webhook Security

#### Signing Secret Verification

Enable signing secret when creating webhook to verify authenticity:

**Node.js/Express Example:**
```javascript
const crypto = require('crypto');
const express = require('express');
const app = express();

app.use(express.json());

app.post('/webhook', (req, res) => {
  const webhookPayload = req.body;
  const receivedSignature = req.headers['tally-signature'];
  const signingSecret = 'YOUR_SIGNING_SECRET';
  
  // Calculate expected signature
  const calculatedSignature = crypto
    .createHmac('sha256', signingSecret)
    .update(JSON.stringify(webhookPayload))
    .digest('base64');
  
  if (receivedSignature === calculatedSignature) {
    // Valid webhook - process data
    console.log('Valid submission:', webhookPayload.data);
    res.status(200).send('Success');
  } else {
    // Invalid signature
    res.status(401).send('Invalid signature');
  }
});

app.listen(3000);
```

**Python/Flask Example:**
```python
import hmac
import hashlib
import json
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_json()
    received_signature = request.headers.get('Tally-Signature')
    signing_secret = 'YOUR_SIGNING_SECRET'
    
    # Calculate expected signature
    calculated_signature = hmac.new(
        signing_secret.encode(),
        json.dumps(payload).encode(),
        hashlib.sha256
    ).digest().encode('base64').decode().strip()
    
    if received_signature == calculated_signature:
        # Valid webhook - process data
        print('Valid submission:', payload['data'])
        return 'Success', 200
    else:
        return 'Invalid signature', 401

if __name__ == '__main__':
    app.run(port=3000)
```

---

### Webhook Requirements

Your webhook endpoint must:
- Accept POST requests with JSON payload
- Return 2XX status code within 10 seconds
- Use HTTPS (HTTP also supported but not recommended)

**Retry Logic:**
If endpoint fails (non-2XX or timeout), Tally retries:
1. After 5 minutes
2. After 30 minutes
3. After 1 hour
4. After 6 hours
5. After 1 day

---

### Workspaces

#### List Workspaces
```bash
GET https://api.tally.so/workspaces
Authorization: Bearer <token>
```

#### Get Workspace
```bash
GET https://api.tally.so/workspaces/{workspaceId}
Authorization: Bearer <token>
```

#### Create Workspace (Pro subscription required)
```bash
POST https://api.tally.so/workspaces
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New Workspace"
}
```

#### Update Workspace
```bash
PATCH https://api.tally.so/workspaces/{workspaceId}
Authorization: Bearer <token>
```

#### Delete Workspace
```bash
DELETE https://api.tally.so/workspaces/{workspaceId}
Authorization: Bearer <token>
```

---

### User Information

#### Get Current User
```bash
GET https://api.tally.so/users/me
Authorization: Bearer <token>
```

---

### Organizations

#### List Organization Users
```bash
GET https://api.tally.so/organizations/users
Authorization: Bearer <token>
```

#### Remove User
```bash
DELETE https://api.tally.so/organizations/users/{userId}
Authorization: Bearer <token>
```

#### List Invites
```bash
GET https://api.tally.so/organizations/invites
Authorization: Bearer <token>
```

#### Create Invite
```bash
POST https://api.tally.so/organizations/invites
Authorization: Bearer <token>
```

#### Cancel Invite
```bash
DELETE https://api.tally.so/organizations/invites/{inviteId}
Authorization: Bearer <token>
```

---

## Response Codes

| Code | Description |
|------|-------------|
| `200` | Success - request completed successfully |
| `201` | Created - resource created successfully |
| `400` | Bad Request - malformed or invalid parameters |
| `401` | Unauthorized - missing or invalid credentials |
| `403` | Forbidden - no permission to access resource |
| `404` | Not Found - resource doesn't exist |
| `429` | Rate Limited - exceeded 100 requests/minute |
| `500` | Server Error - something went wrong on Tally's end |

---

## Integration Patterns

### Pattern 1: Real-Time Processing (Webhook)
**Best for:** Instant notifications, automated workflows

1. Create webhook pointing to your endpoint
2. Implement webhook handler with signature verification
3. Process submissions in real-time
4. Return 2XX within 10 seconds

**Pros:** 
- No polling overhead
- Instant data delivery
- Doesn't count against rate limit

**Cons:**
- Requires publicly accessible endpoint
- Must handle retries and failures

---

### Pattern 2: Polling for Submissions (API)
**Best for:** Batch processing, historical data retrieval

1. Periodically call `/forms/{formId}/submissions`
2. Use `afterId` or `startDate`/`endDate` for incremental fetches
3. Handle pagination with `page` parameter
4. Process submissions in batches

**Pros:**
- No webhook infrastructure needed
- Full control over timing
- Can fetch historical data

**Cons:**
- Uses rate limit quota
- Potential delays in data retrieval
- More complex pagination logic

---

### Pattern 3: Hybrid Approach
**Best for:** High-reliability applications

1. Use webhooks for real-time processing
2. Run periodic API polls as backup
3. Deduplicate using `submissionId`
4. Maintain event log for audit

---

## Sample Integration Scripts

### Python: Fetch All Submissions
```python
#!/usr/bin/env python3
import requests
import time
from datetime import datetime

API_KEY = "tly-xxxx"
FORM_ID = "your-form-id"
BASE_URL = "https://api.tally.so"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

def fetch_all_submissions(form_id):
    """Fetch all submissions with pagination."""
    all_submissions = []
    page = 1
    has_more = True
    
    while has_more:
        response = requests.get(
            f"{BASE_URL}/forms/{form_id}/submissions",
            headers=headers,
            params={"page": page, "filter": "all"}
        )
        
        if response.status_code == 200:
            data = response.json()
            all_submissions.extend(data.get("submissions", []))
            has_more = data.get("hasMore", False)
            page += 1
            
            print(f"Fetched page {page-1}, total: {len(all_submissions)}")
            time.sleep(0.6)  # Rate limit: 100/min = 1 per 0.6s
        elif response.status_code == 429:
            print("Rate limited, waiting 60s...")
            time.sleep(60)
        else:
            print(f"Error: {response.status_code}")
            break
    
    return all_submissions

if __name__ == "__main__":
    submissions = fetch_all_submissions(FORM_ID)
    print(f"Total submissions: {len(submissions)}")
```

---

### Node.js: Webhook Receiver
```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

const SIGNING_SECRET = 'your-signing-secret';

app.use(express.json());

app.post('/tally-webhook', (req, res) => {
  const payload = req.body;
  const signature = req.headers['tally-signature'];
  
  // Verify signature
  const expectedSignature = crypto
    .createHmac('sha256', SIGNING_SECRET)
    .update(JSON.stringify(payload))
    .digest('base64');
  
  if (signature !== expectedSignature) {
    return res.status(401).send('Invalid signature');
  }
  
  // Process submission
  const { eventType, data } = payload;
  
  if (eventType === 'FORM_RESPONSE') {
    console.log('New submission:', data.submissionId);
    console.log('Form:', data.formName);
    console.log('Respondent:', data.respondentId);
    
    // Extract field values
    data.fields.forEach(field => {
      console.log(`${field.label}: ${field.value}`);
    });
    
    // TODO: Store in database, trigger workflows, etc.
  }
  
  res.status(200).send('OK');
});

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});
```

---

## Testing Tools

### Test Webhook Endpoint
Use [RequestInspector](https://requestinspector.com/) to test webhook payloads without setting up infrastructure.

### cURL Examples

**List Forms:**
```bash
curl -X GET "https://api.tally.so/forms" \
  -H "Authorization: Bearer tly-xxxx"
```

**Get Submissions:**
```bash
curl -X GET "https://api.tally.so/forms/VwbNEw/submissions?page=1" \
  -H "Authorization: Bearer tly-xxxx"
```

**Create Webhook:**
```bash
curl -X POST "https://api.tally.so/webhooks" \
  -H "Authorization: Bearer tly-xxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "formId": "VwbNEw",
    "url": "https://your-domain.com/webhook",
    "eventTypes": ["FORM_RESPONSE"]
  }'
```

---

## Important Notes

1. **API is in Public Beta:** Subject to breaking changes (though Tally minimizes these)
2. **No OAuth:** Only API key authentication currently supported
3. **User-Level Keys:** Keys inherit user permissions; no service accounts yet
4. **HTTPS Only:** Unencrypted HTTP requests are rejected
5. **Webhook Preference:** Use webhooks over polling whenever possible
6. **10s Timeout:** Webhook endpoints must respond within 10 seconds
7. **Fair Use:** Free plan includes webhooks; API subject to fair use policy

---

## Additional Resources

- **Developer Docs:** [developers.tally.so](https://developers.tally.so)
- **Help Center:** [tally.so/help](https://tally.so/help)
- **Webhook Guide:** [tally.so/help/webhooks](https://tally.so/help/webhooks)
- **Support:** [tally.so/support](https://tally.so/support)
- **API Key Management:** [tally.so/settings/api-keys](https://tally.so/settings/api-keys)

---

## References

[^1]: https://developers.tally.so/api-reference/introduction
[^2]: https://developers.tally.so/api-reference/api-keys
[^3]: https://developers.tally.so/api-reference/endpoint/forms/submissions/list
[^4]: https://tally.so/help/webhooks
[^5]: https://developers.tally.so/api-reference/endpoint/webhooks/post
