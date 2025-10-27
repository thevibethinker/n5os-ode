API keys - Tally Developer Docs

[Skip to main content](https://developers.tally.so/api-reference/api-keys#content-area)

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

API keys

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

* [Creating an API key](https://developers.tally.so/api-reference/api-keys#creating-an-api-key)

Getting started

API keys
========

Learn how API keys work on Tally

API keys on Tally allow you to access your account programmatically. This is useful for integrating Tally into your application or with other tools and services.

For now, each API key is tied to a specific user - meaning that it will inherit the permissions of
the user, also when they change. With the key you will be able to access all of the user’s
resources.

[​](https://developers.tally.so/api-reference/api-keys#creating-an-api-key) Creating an API key
-----------------------------------------------------------------------------------------------

You can create an API key by following these steps:

1

Go to settings

Go to **Settings** > [**API keys**](https://tally.so/settings/api-keys).

![API keys overview](https://mintcdn.com/tally/dNtl8XLd2Tzd_ywC/images/api-keys/overview.jpg?fit=max&auto=format&n=dNtl8XLd2Tzd_ywC&q=85&s=c4e0692aa7dff4a5d0a2cd2788ce57a4)

2

Create an API key

Click on the “Create API key” button.Currently, you can only create an API key in the context of your own user. While we might add fine-grained permissions in the future, it’s not option right now.

![Creating an API key](https://mintcdn.com/tally/dNtl8XLd2Tzd_ywC/images/api-keys/creating.jpg?fit=max&auto=format&n=dNtl8XLd2Tzd_ywC&q=85&s=8dba33156529a3ee8b3805e3d866473e)

3

Store your API key

Once your API key is created, make sure to copy and store it in a safe place. You won’t be able to see it again for security reasons. If it gets lost, you can create a new one.

![API key created](https://mintcdn.com/tally/dNtl8XLd2Tzd_ywC/images/api-keys/created.jpg?fit=max&auto=format&n=dNtl8XLd2Tzd_ywC&q=85&s=d701df80b35544c1c3f69099cd0917c1)

4

Use your API key

Now that you have your API key, you can use it to access your account’s resources programmatically via any API request as a bearer token.

Copy

Ask AI

```
Authorization: Bearer tly-xxxx
```

When you remove a user from your organization (or they leave your organization), all API keys
associated with that user will stop working as well. Keep this in mind when managing users.

[Introduction](https://developers.tally.so/api-reference/introduction)[Versioning](https://developers.tally.so/api-reference/versioning)

⌘I

[github](https://github.com/tallyforms)[x](https://twitter.com/tallyforms)[reddit](https://www.reddit.com/r/tallyforms)[linkedin](https://linkedin.com/company/tallyforms)[youtube](https://youtube.com/@tallyforms)[bluesky](https://bsky.app/profile/tally.so)[threads](https://threads.net/tallyforms)[facebook](https://facebook.com/tallyforms)

[Powered by Mintlify](https://mintlify.com?utm_campaign=poweredBy&utm_medium=referral&utm_source=tally)