Listing submissions - Tally Developer Docs

[Skip to main content](https://developers.tally.so/api-reference/endpoint/forms/submissions/list#content-area)

[Tally Developer Docs home page![light logo](https://mintcdn.com/tally/dNtl8XLd2Tzd_ywC/images/logo/light.svg?fit=max&auto=format&n=dNtl8XLd2Tzd_ywC&q=85&s=78020cb004ffebf54fc270527455d177)![dark logo](https://mintcdn.com/tally/dNtl8XLd2Tzd_ywC/images/logo/dark.svg?fit=max&auto=format&n=dNtl8XLd2Tzd_ywC&q=85&s=50ebb8d72771822a903297d110d5eefd)](https://developers.tally.so/)

Search...

⌘K

* [Support](https://tally.so/support)
* [Help Center](https://tally.so/help)
* [Create API key](https://tally.so/settings/api-keys)
* [Create API key](https://tally.so/settings/api-keys)

Search...

Navigation

Forms

Listing submissions

[API Reference](https://developers.tally.so/api-reference/introduction)[Documentation](https://developers.tally.so/documentation/creating-a-form)

##### Getting started

* [Introduction](https://developers.tally.so/api-reference/introduction)
* [API keys](https://developers.tally.so/api-reference/api-keys)
* [Versioning](https://developers.tally.so/api-reference/versioning)
* [Changelog](https://developers.tally.so/api-reference/changelog)
* [MCP Integration](https://developers.tally.so/api-reference/mcp)

##### Users

* [GET

  Fetching user info](https://developers.tally.so/api-reference/endpoint/users/me/get)

##### Organizations

* [GET

  Listing users](https://developers.tally.so/api-reference/endpoint/organizations/users/get)
* [DEL

  Removing users](https://developers.tally.so/api-reference/endpoint/organizations/users/delete)
* [GET

  Listing invites](https://developers.tally.so/api-reference/endpoint/organizations/invites/get)
* [POST

  Creating invites](https://developers.tally.so/api-reference/endpoint/organizations/invites/post)
* [DEL

  Cancelling invites](https://developers.tally.so/api-reference/endpoint/organizations/invites/delete)

##### Forms

* [GET

  Listing forms](https://developers.tally.so/api-reference/endpoint/forms/list)
* [POST

  Creating forms](https://developers.tally.so/api-reference/endpoint/forms/post)
* [GET

  Fetching forms](https://developers.tally.so/api-reference/endpoint/forms/get)
* [PATCH

  Updating forms](https://developers.tally.so/api-reference/endpoint/forms/patch)
* [DEL

  Deleting forms](https://developers.tally.so/api-reference/endpoint/forms/delete)
* [GET

  Listing questions](https://developers.tally.so/api-reference/endpoint/forms/questions/list)
* [GET

  Listing submissions](https://developers.tally.so/api-reference/endpoint/forms/submissions/list)
* [GET

  Fetching submissions](https://developers.tally.so/api-reference/endpoint/forms/submissions/get)
* [DEL

  Deleting submissions](https://developers.tally.so/api-reference/endpoint/forms/submissions/delete)

##### Workspaces

* [GET

  Listing workspaces](https://developers.tally.so/api-reference/endpoint/workspaces/list)
* [POST

  Creating workspaces](https://developers.tally.so/api-reference/endpoint/workspaces/post)
* [GET

  Fetching workspaces](https://developers.tally.so/api-reference/endpoint/workspaces/get)
* [PATCH

  Updating workspaces](https://developers.tally.so/api-reference/endpoint/workspaces/patch)
* [DEL

  Deleting workspaces](https://developers.tally.so/api-reference/endpoint/workspaces/delete)

##### Webhooks

* [GET

  Listing webhooks](https://developers.tally.so/api-reference/endpoint/webhooks/get)
* [POST

  Creating webhooks](https://developers.tally.so/api-reference/endpoint/webhooks/post)
* [PATCH

  Updating webhooks](https://developers.tally.so/api-reference/endpoint/webhooks/patch)
* [DEL

  Deleting webhooks](https://developers.tally.so/api-reference/endpoint/webhooks/delete)
* [GET

  Listing webhook events](https://developers.tally.so/api-reference/endpoint/webhooks/events/get)
* [POST

  Retrying webhook events](https://developers.tally.so/api-reference/endpoint/webhooks/events/retry)

List form submissions

cURL

Copy

Ask AI

```
curl --request GET \
  --url https://api.tally.so/forms/{formId}/submissions \
  --header 'Authorization: Bearer <token>'
```

200

401

403

404

Copy

Ask AI

```
{
  "page": 123,
  "limit": 123,
  "hasMore": true,
  "totalNumberOfSubmissionsPerFilter": {
    "all": 123,
    "completed": 123,
    "partial": 123
  },
  "questions": [
    {
      "id": "<string>",
      "type": "FORM_TITLE",
      "title": "<string>",
      "isTitleModifiedByUser": true,
      "formId": "<string>",
      "isDeleted": true,
      "numberOfResponses": 123,
      "createdAt": "2023-11-07T05:31:56Z",
      "updatedAt": "2023-11-07T05:31:56Z",
      "fields": [
        {
          "uuid": "3c90c3cc-0d44-4b50-8888-8dd25736052a",
          "type": "FORM_TITLE",
          "blockGroupUuid": "3c90c3cc-0d44-4b50-8888-8dd25736052a",
          "title": "<string>"
        }
      ]
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

Forms

Listing submissions
===================

Returns a paginated list of form submissions with their responses.

GET

/

forms

/

{formId}

/

submissions

Try it

List form submissions

cURL

Copy

Ask AI

```
curl --request GET \
  --url https://api.tally.so/forms/{formId}/submissions \
  --header 'Authorization: Bearer <token>'
```

200

401

403

404

Copy

Ask AI

```
{
  "page": 123,
  "limit": 123,
  "hasMore": true,
  "totalNumberOfSubmissionsPerFilter": {
    "all": 123,
    "completed": 123,
    "partial": 123
  },
  "questions": [
    {
      "id": "<string>",
      "type": "FORM_TITLE",
      "title": "<string>",
      "isTitleModifiedByUser": true,
      "formId": "<string>",
      "isDeleted": true,
      "numberOfResponses": 123,
      "createdAt": "2023-11-07T05:31:56Z",
      "updatedAt": "2023-11-07T05:31:56Z",
      "fields": [
        {
          "uuid": "3c90c3cc-0d44-4b50-8888-8dd25736052a",
          "type": "FORM_TITLE",
          "blockGroupUuid": "3c90c3cc-0d44-4b50-8888-8dd25736052a",
          "title": "<string>"
        }
      ]
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

**Looking for real-time submissions?** The most efficient way to instantly retrieve new
submissions is by using a [webhook](https://tally.so/help/webhooks). This allows you to receive
data as soon as a form is submitted, without needing to poll the API.

#### Authorizations

[​](https://developers.tally.so/api-reference/endpoint/forms/submissions/list#authorization-authorization)

Authorization

string

header

required

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.

#### Path Parameters

[​](https://developers.tally.so/api-reference/endpoint/forms/submissions/list#parameter-form-id)

formId

string

required

The ID of the form

#### Query Parameters

[​](https://developers.tally.so/api-reference/endpoint/forms/submissions/list#parameter-page)

page

number

Page number for pagination (default: 1)

[​](https://developers.tally.so/api-reference/endpoint/forms/submissions/list#parameter-filter)

filter

enum<string>

Filter submissions by status

Available options:

`all`,

`completed`,

`partial`

[​](https://developers.tally.so/api-reference/endpoint/forms/submissions/list#parameter-start-date)

startDate

string<date-time>

Filter submissions submitted on or after this date (ISO 8601 format)

[​](https://developers.tally.so/api-reference/endpoint/forms/submissions/list#parameter-end-date)

endDate

string<date-time>

Filter submissions submitted on or before this date (ISO 8601 format)

[​](https://developers.tally.so/api-reference/endpoint/forms/submissions/list#parameter-after-id)

afterId

string

Get submissions that came after a specific submission ID

#### Response

200

application/json

List of form submissions

[​](https://developers.tally.so/api-reference/endpoint/forms/submissions/list#response-page)

page

number

Current page number

[​](https://developers.tally.so/api-reference/endpoint/forms/submissions/list#response-limit)

limit

number

Number of submissions per page

[​](https://developers.tally.so/api-reference/endpoint/forms/submissions/list#response-has-more)

hasMore

boolean

Whether there are more pages available

[​](https://developers.tally.so/api-reference/endpoint/forms/submissions/list#response-total-number-of-submissions-per-filter)

totalNumberOfSubmissionsPerFilter

object

Show child attributes

[​](https://developers.tally.so/api-reference/endpoint/forms/submissions/list#response-questions)

questions

object[]

List of form questions

Show child attributes

[​](https://developers.tally.so/api-reference/endpoint/forms/submissions/list#response-submissions)

submissions

object[]

List of form submissions

Show child attributes

[Listing questions](https://developers.tally.so/api-reference/endpoint/forms/questions/list)[Fetching submissions](https://developers.tally.so/api-reference/endpoint/forms/submissions/get)

⌘I

[github](https://github.com/tallyforms)[x](https://twitter.com/tallyforms)[reddit](https://www.reddit.com/r/tallyforms)[linkedin](https://linkedin.com/company/tallyforms)[youtube](https://youtube.com/@tallyforms)[bluesky](https://bsky.app/profile/tally.so)[threads](https://threads.net/tallyforms)[facebook](https://facebook.com/tallyforms)

[Powered by Mintlify](https://mintlify.com?utm_campaign=poweredBy&utm_medium=referral&utm_source=tally)