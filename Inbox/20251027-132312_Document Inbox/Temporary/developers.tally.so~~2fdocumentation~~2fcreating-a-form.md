Creating a form - Tally Developer Docs

[Skip to main content](https://developers.tally.so/documentation/creating-a-form#content-area)

[Tally Developer Docs home page![light logo](https://mintcdn.com/tally/dNtl8XLd2Tzd_ywC/images/logo/light.svg?fit=max&auto=format&n=dNtl8XLd2Tzd_ywC&q=85&s=78020cb004ffebf54fc270527455d177)![dark logo](https://mintcdn.com/tally/dNtl8XLd2Tzd_ywC/images/logo/dark.svg?fit=max&auto=format&n=dNtl8XLd2Tzd_ywC&q=85&s=50ebb8d72771822a903297d110d5eefd)](https://developers.tally.so/)

Search...

⌘K

* [Support](https://tally.so/support)
* [Help Center](https://tally.so/help)
* [Create API key](https://tally.so/settings/api-keys)
* [Create API key](https://tally.so/settings/api-keys)

Search...

Navigation

Basics

Creating a form

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

* [Prerequisites](https://developers.tally.so/documentation/creating-a-form#prerequisites)
* [Request](https://developers.tally.so/documentation/creating-a-form#request)
* [Response](https://developers.tally.so/documentation/creating-a-form#response)

Basics

Creating a form
===============

Creating an empty form using the Tally API

[​](https://developers.tally.so/documentation/creating-a-form#prerequisites) Prerequisites
------------------------------------------------------------------------------------------

* A Tally account
* An API key

[​](https://developers.tally.so/documentation/creating-a-form#request) Request
------------------------------------------------------------------------------

To create a form, send a POST request to the `/forms` endpoint with the following payload:

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
        "title": "Test",
        "html": "Test"
      }
    }
  ]
}'
```

Each block requires a unique UUID. You can generate UUIDs using any standard UUID library.

[​](https://developers.tally.so/documentation/creating-a-form#response) Response
--------------------------------------------------------------------------------

The API will respond with a 201 status code and with some form meta data:

Copy

Ask AI

```
{
  "id": "m2fK5R",
  "name": "Test",
  "workspaceId": "kb3o5R",
  "organizationId": "atL65s",
  "status": "PUBLISHED",
  "hasDraftBlocks": false,
  "isClosed": false,
  "updatedAt": "2024-12-20T10:34:19.262Z",
  "createdAt": "2024-12-20T10:34:19.262Z"
}
```

Your form should now show up in the Tally dashboard. And when you open it, you should see the empty form with just a title “Test”.

![Create a simple form](https://mintcdn.com/tally/dNtl8XLd2Tzd_ywC/images/documentation/creating-a-form.jpg?fit=max&auto=format&n=dNtl8XLd2Tzd_ywC&q=85&s=380d41d94b96bd5ef2a96e32594a2fe6)

[Adding blocks to a form](https://developers.tally.so/documentation/adding-blocks-to-a-form)

⌘I

[github](https://github.com/tallyforms)[x](https://twitter.com/tallyforms)[reddit](https://www.reddit.com/r/tallyforms)[linkedin](https://linkedin.com/company/tallyforms)[youtube](https://youtube.com/@tallyforms)[bluesky](https://bsky.app/profile/tally.so)[threads](https://threads.net/tallyforms)[facebook](https://facebook.com/tallyforms)

[Powered by Mintlify](https://mintlify.com?utm_campaign=poweredBy&utm_medium=referral&utm_source=tally)