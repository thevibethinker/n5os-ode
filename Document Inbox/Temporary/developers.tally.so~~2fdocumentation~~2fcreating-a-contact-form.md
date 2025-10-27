Creating a contact form - Tally Developer Docs

[Skip to main content](https://developers.tally.so/documentation/creating-a-contact-form#content-area)

[Tally Developer Docs home page![light logo](https://mintcdn.com/tally/dNtl8XLd2Tzd_ywC/images/logo/light.svg?fit=max&auto=format&n=dNtl8XLd2Tzd_ywC&q=85&s=78020cb004ffebf54fc270527455d177)![dark logo](https://mintcdn.com/tally/dNtl8XLd2Tzd_ywC/images/logo/dark.svg?fit=max&auto=format&n=dNtl8XLd2Tzd_ywC&q=85&s=50ebb8d72771822a903297d110d5eefd)](https://developers.tally.so/)

Search...

⌘K

* [Support](https://tally.so/support)
* [Help Center](https://tally.so/help)
* [Create API key](https://tally.so/settings/api-keys)
* [Create API key](https://tally.so/settings/api-keys)

Search...

Navigation

Examples

Creating a contact form

[API Reference](https://developers.tally.so/api-reference/introduction)[Documentation](https://developers.tally.so/documentation/creating-a-form)

##### Basics

* [Creating a form](https://developers.tally.so/documentation/creating-a-form)
* [Adding blocks to a form](https://developers.tally.so/documentation/adding-blocks-to-a-form)
* [Styling title blocks](https://developers.tally.so/documentation/styling-title-blocks)
* [Fetching form submissions](https://developers.tally.so/documentation/fetching-form-submissions)

##### Examples

* [Creating a contact form](https://developers.tally.so/documentation/creating-a-contact-form)
* [Creating a dropdown](https://developers.tally.so/documentation/creating-a-dropdown)

##### Advanced

* [Creating a mention](https://developers.tally.so/documentation/creating-a-mention)
* [Creating a form with settings](https://developers.tally.so/documentation/creating-a-form-with-settings)

##### Crawler

* [TallyBot](https://developers.tally.so/documentation/tally-bot)

On this page

* [Prerequisites](https://developers.tally.so/documentation/creating-a-contact-form#prerequisites)
* [Request](https://developers.tally.so/documentation/creating-a-contact-form#request)
* [Response](https://developers.tally.so/documentation/creating-a-contact-form#response)

Examples

Creating a contact form
=======================

Learn how to create a contact form using the Tally API

[​](https://developers.tally.so/documentation/creating-a-contact-form#prerequisites) Prerequisites
--------------------------------------------------------------------------------------------------

* A Tally account
* An API key

[​](https://developers.tally.so/documentation/creating-a-contact-form#request) Request
--------------------------------------------------------------------------------------

To create the form, send a POST request to the `/forms` endpoint with the following payload:

Copy

Ask AI

```
curl -X POST 'https://api.tally.so/forms' \
-H 'Authorization: Bearer <token>' \
-H 'Content-Type: application/json' \
-d '{
  "status": "PUBLISHED",
  "blocks": [
    {
      "uuid": "6ef8675d-33cb-419b-a81e-93982e726f2e",
      "type": "FORM_TITLE",
      "groupUuid": "073c835f-7ad4-459c-866d-4108b6b7e2e1",
      "groupType": "TEXT",
      "payload": {
        "html": "Contact form"
      }
    },
    {
      "uuid": "48b4cdf3-2c9d-47d3-b8fb-b0ccabc5cd84",
      "type": "TITLE",
      "groupUuid": "93034250-5f05-4710-b8e0-5c9145c5b9ea",
      "groupType": "QUESTION",
      "payload": {
        "html": "Name"
      }
    },
    {
      "uuid": "884ff838-97f9-4ac9-8db1-31aa052df988",
      "type": "INPUT_TEXT",
      "groupUuid": "93034250-5f05-4710-b8e0-5c9145c5b9ea",
      "groupType": "QUESTION",
      "payload": {
        "isRequired": true,
        "placeholder": "Enter your name"
      }
    },
    {
      "uuid": "7d9c2e31-b5aa-4c8b-9c2d-123456789abc",
      "type": "TITLE",
      "groupUuid": "3287d15c-c2b2-4f84-a915-bc57380a4b51",
      "groupType": "QUESTION",
      "payload": {
        "html": "Email"
      }
    },
    {
      "uuid": "9b3f5d2a-1c8e-4f7d-b6a9-def012345678",
      "type": "INPUT_EMAIL",
      "groupUuid": "3287d15c-c2b2-4f84-a915-bc57380a4b51",
      "groupType": "QUESTION",
      "payload": {
        "isRequired": true,
        "placeholder": "Enter your email"
      }
    },
    {
      "uuid": "abc12345-6789-def0-1234-56789abcdef0",
      "type": "TITLE",
      "groupUuid": "456789ab-cdef-4321-b8e0-987654321def",
      "groupType": "QUESTION",
      "payload": {
        "html": "Message"
      }
    },
    {
      "uuid": "456789ab-cdef-0123-4567-89abcdef0123",
      "type": "TEXTAREA",
      "groupUuid": "456789ab-cdef-4321-b8e0-987654321def",
      "groupType": "QUESTION",
      "payload": {
        "isRequired": true,
        "placeholder": "Enter your message"
      }
    }
  ]
}'
```

This example adds in total 7 blocks to the form:

1. The form title
2. A title block for the name field
3. A required text input block for the name field
4. A title block for the email field
5. A required email input block for the email field
6. A title block for the message field
7. A required large text input block for the message field

[​](https://developers.tally.so/documentation/creating-a-contact-form#response) Response
----------------------------------------------------------------------------------------

The API will respond with a 201 status code and with some form meta data:

Copy

Ask AI

```
{
  "id": "m2fK5R",
  "name": "Contact form",
  "workspaceId": "kb3o5R",
  "organizationId": "atL65s",
  "status": "PUBLISHED",
  "hasDraftBlocks": false,
  "isClosed": false,
  "updatedAt": "2024-12-20T10:34:19.262Z",
  "createdAt": "2024-12-20T10:34:19.262Z"
}
```

The form that was created should now show up in the Tally dashboard & look like this.

![Create a contact form](https://mintcdn.com/tally/dNtl8XLd2Tzd_ywC/images/documentation/creating-a-contact-form.jpg?fit=max&auto=format&n=dNtl8XLd2Tzd_ywC&q=85&s=40d045d8958113aad9d4692b7a54b7d7)

[Fetching form submissions](https://developers.tally.so/documentation/fetching-form-submissions)[Creating a dropdown](https://developers.tally.so/documentation/creating-a-dropdown)

⌘I

[github](https://github.com/tallyforms)[x](https://twitter.com/tallyforms)[reddit](https://www.reddit.com/r/tallyforms)[linkedin](https://linkedin.com/company/tallyforms)[youtube](https://youtube.com/@tallyforms)[bluesky](https://bsky.app/profile/tally.so)[threads](https://threads.net/tallyforms)[facebook](https://facebook.com/tallyforms)

[Powered by Mintlify](https://mintlify.com?utm_campaign=poweredBy&utm_medium=referral&utm_source=tally)