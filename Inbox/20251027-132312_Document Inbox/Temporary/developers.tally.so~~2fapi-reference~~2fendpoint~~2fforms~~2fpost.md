[Skip to main content](https://developers.tally.so/api-reference/endpoint/forms/post#content-area)

POST

/

forms

Create a new form

```
curl --request POST \

  --url https://api.tally.so/forms \

  --header 'Authorization: Bearer <token>' \

  --header 'Content-Type: application/json' \

  --data '{

  "workspaceId": "<string>",

  "templateId": "<string>",

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

#### Body

application/json

status

enum<string>

required

Initial status of the form

Available options:

`BLANK`,

`DRAFT`,

`PUBLISHED`,

`DELETED`

blocks

object[]

required

workspaceId

string

ID of the workspace to create the form in. If not provided, uses the user's default workspace

templateId

string

ID of the template to base the form on

settings

object

[Listing forms](https://developers.tally.so/api-reference/endpoint/forms/list) [Fetching forms](https://developers.tally.so/api-reference/endpoint/forms/get)

⌘I