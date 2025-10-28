Introduction - Tally Developer Docs

[Skip to main content](https://developers.tally.so/api-reference/introduction#content-area)

[Tally Developer Docs home page![light logo](https://mintcdn.com/tally/dNtl8XLd2Tzd_ywC/images/logo/light.svg?fit=max&auto=format&n=dNtl8XLd2Tzd_ywC&q=85&s=78020cb004ffebf54fc270527455d177)![dark logo](https://mintcdn.com/tally/dNtl8XLd2Tzd_ywC/images/logo/dark.svg?fit=max&auto=format&n=dNtl8XLd2Tzd_ywC&q=85&s=50ebb8d72771822a903297d110d5eefd)](https://developers.tally.so/)

Search...

⌘K

* [Support](https://tally.so/support)
* [Help Center](https://tally.so/help)
* [Create API key](https://tally.so/settings/api-keys)
* [Create API key](https://tally.so/settings/api-keys)

Search...

Navigation

Getting started

Introduction

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

On this page

* [Base URL](https://developers.tally.so/api-reference/introduction#base-url)
* [Authentication](https://developers.tally.so/api-reference/introduction#authentication)
* [Response codes](https://developers.tally.so/api-reference/introduction#response-codes)
* [Rate Limits](https://developers.tally.so/api-reference/introduction#rate-limits)
* [Caveats](https://developers.tally.so/api-reference/introduction#caveats)

Getting started

Introduction
============

Fundamental concepts of Tally’s API.

Tally’s API is currently in public beta and subject to change.

[​](https://developers.tally.so/api-reference/introduction#base-url) Base URL
-----------------------------------------------------------------------------

The Tally API follows REST principles and is accessible only via HTTPS. For security reasons, unencrypted HTTP requests are not allowed. The Base URL for all API endpoints is:

Terminal

Copy

Ask AI

```
https://api.tally.so
```

[​](https://developers.tally.so/api-reference/introduction#authentication) Authentication
-----------------------------------------------------------------------------------------

Authentication to the Tally API requires an Authorization header with a Bearer token. Include the Authorization header in your requests as shown below:

Terminal

Copy

Ask AI

```
Authorization: Bearer <token>
```

Learn more about [how to get your API key](https://developers.tally.so/api-reference/api-keys).

[​](https://developers.tally.so/api-reference/introduction#response-codes) Response codes
-----------------------------------------------------------------------------------------

The API returns standard HTTP response codes to indicate the success or failure of an API request. Here are a few examples:

| Code | Description |
| --- | --- |
| `200` | Success - The request completed successfully |
| `400` | Bad Request - The request was malformed or contained invalid parameters |
| `401` | Unauthorized - Authentication credentials are missing or invalid |
| `403` | Forbidden - You don’t have permission to access this resource |
| `404` | Not Found - The requested resource doesn’t exist |
| `429` | Rate Limited - You’ve exceeded the allowed number of requests |
| `500` | Server Error - Something went wrong on our end |

[​](https://developers.tally.so/api-reference/introduction#rate-limits) Rate Limits
-----------------------------------------------------------------------------------

To ensure fair usage and maintain service quality, the Tally API limits requests to 100 per minute.

**Avoid rate limits with webhooks!** Instead of polling for new form submissions, use
[webhooks](https://tally.so/help/webhooks) to receive data instantly when forms are submitted.
This is more efficient and won’t count against your rate limit.

[​](https://developers.tally.so/api-reference/introduction#caveats) Caveats
---------------------------------------------------------------------------

* Tally’s API is currently in public beta and is subject to change. However, we will do our best to keep breaking changes to a minimum.

[API keys](https://developers.tally.so/api-reference/api-keys)

⌘I

[github](https://github.com/tallyforms)[x](https://twitter.com/tallyforms)[reddit](https://www.reddit.com/r/tallyforms)[linkedin](https://linkedin.com/company/tallyforms)[youtube](https://youtube.com/@tallyforms)[bluesky](https://bsky.app/profile/tally.so)[threads](https://threads.net/tallyforms)[facebook](https://facebook.com/tallyforms)

[Powered by Mintlify](https://mintlify.com?utm_campaign=poweredBy&utm_medium=referral&utm_source=tally)