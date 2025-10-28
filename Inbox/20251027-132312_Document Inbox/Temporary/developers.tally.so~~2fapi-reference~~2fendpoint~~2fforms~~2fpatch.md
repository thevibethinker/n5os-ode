[Skip to main content](https://developers.tally.so/api-reference/endpoint/forms/patch#content-area)

PATCH

/

forms

/

{formId}

Update a form

```
curl --request PATCH \
  --url https://api.tally.so/forms/{formId} \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
  "name": "<string>",
  "status": "BLANK",
  "blocks": [
    {
      "uuid": "3c90c3cc-0d44-4b50-8888-8dd25736052a",
      "type": "FORM_TITLE",
      "groupUuid": "3c90c3cc-0d44-4b50-8888-8dd25736052a",
      "groupType": "FORM_TITLE",
      "payload": "<any>"
    }
  ],
  "settings": {
    "language": "<string>",
    "isClosed": false,
    "closeMessageTitle": "<string>",
    "closeMessageDescription": "<string>",
    "closeTimezone": "<string>",
    "closeDate": "<string>",
    "closeTime": "<string>",
    "submissionsLimit": 1,
    "uniqueSubmissionKey": "<string>",
    "redirectOnCompletion": "<string>",
    "hasSelfEmailNotifications": false,
    "selfEmailTo": "<string>",
    "selfEmailReplyTo": "<string>",
    "selfEmailSubject": "<string>",
    "selfEmailFromName": "<string>",
    "selfEmailBody": "<string>",
    "hasRespondentEmailNotifications": false,
    "respondentEmailTo": "<string>",
    "respondentEmailReplyTo": "<string>",
    "respondentEmailSubject": "<string>",
    "respondentEmailFromName": "<string>",
    "respondentEmailBody": "<string>",
    "hasProgressBar": false,
    "hasPartialSubmissions": false,
    "pageAutoJump": false,
    "saveForLater": true,
    "styles": "<string>",
    "password": "<string>",
    "submissionsDataRetentionDuration": 1,
    "submissionsDataRetentionUnit": "<string>"
  }
}'
```

```
{
  "id": "<string>",
  "name": "<string>",
  "workspaceId": "<string>",
  "status": "BLANK",
  "numberOfSubmissions": 123,
  "isClosed": true,
  "payments": [
    {
      "amount": 123,
      "currency": "<string>"
    }
  ],
  "createdAt": "2023-11-07T05:31:56Z",
  "updatedAt": "2023-11-07T05:31:56Z"
}
```

#### Path Parameters

formId

string

required

The ID of the form to update

#### Body

application/json

name

string

New name for the form

status

enum<string>

New status for the form

Available options:

`BLANK`,

`DRAFT`,

`PUBLISHED`,

`DELETED`

blocks

object[]

Updated blocks for the form

settings

object

Updated settings for the form

[Fetching forms](https://developers.tally.so/api-reference/endpoint/forms/get) [Deleting forms](https://developers.tally.so/api-reference/endpoint/forms/delete)

⌘I