---
title: OAuth2 
---

# OAuth2

OAuth2 allows app developers to access user's Roblox accounts on their behalf for many different use cases. You could use OAuth2 to allow users to securely identify themselves to allow signing in with Roblox, or so app developers can create intergrations with the user's account, experiences, or groups.

## Getting Started

### Creating Your Application

!!! note
    You must be [ID verified](https://create.roblox.com/docs/production/publishing/account-verification) on Roblox to create OAuth2 applications.

To create an OAuth2 application, you must go to the [Creator Dashboard](https://create.roblox.com/dashboard/credentials) click the 'OAUTH2.0 APPS' tab, and then press 'CREATE APP'. In the modal, give your app a name, and accept the Third-Party App Terms. After pressing 'CREATE' you will get a prompt asking you to copy the Client ID and secret, you should copy both of these values and keep them somewhere safe.

Once you've saved the Client ID and secret, press 'CONTINUE TO EDIT', in the edit screen you can fill out the description, links, and upload a thumbnail. In the 'Redirect URLs' section at the bottom of the edit page, put in the URLs for where you want the users to go after they authorize, this should be a special route within your website to handle the OAuth2 requests.

After you've finished developing your app, and it is accessible on the internet, you will need to go back to the Creator Dashboard and submit your app for review. Roblox moderators will go through your app and ensure it isn't malicous. If you do not do this, then your app will be limited to 100 users authorizing it.

### Choosing Scopes

Scopes define what resources you're trying to access. For example, most apps will need to use the `openid` and `profile` scopes to identify the user. Other scopes have different purposes, such as `user.inventory-item:read` allows the app to view all items in the user's inventory, even if it is private.

You should consider what scopes your app will need to complete the tasks it needs to. In the edit page of your app, you will see a 'Permissions' section, this is where you select the scopes your app will need to use. Once you've selected the scopes you will need to use, make sure to press 'SAVE CHANGES'.

### Adding the OAuth2 Object

Now that you've created your OAuth2 app, it's time to use it in your code. In your script, add these lines below your imports but near the top:

```py
from rblxopencloud import OAuth2App

rblxapp = OAuth2App(0000000000000000000, "your-client-secret", "https://example.com/redirect")
```

Change `0000000000000000000` to your app's client ID, `your-client-secret` to your app's client secret, and `https://example.com/redirect` to the redirect URI you'll use for testing that you configured in the dashboard. You've created a [`rblxopencloud.OAuth2App`][rblxopencloud.OAuth2App] which can be used for generating redirect URIs, and processing OAuth2 requests.

## Basic OAuth2 Flow

### Redirecting Users to Consent Page

The first part of the OAuth2 flow is redirecting users to Roblox's consent page. You can create the redirection URI yourself, however the library has one built in which makes everything cleaner and easier. To generate a redirect URI you can use [`OAuth2App.generate_uri`][rblxopencloud.OAuth2App.generate_uri]:

```py
rblxapp.generate_uri(['openid', 'profile'])
```

This will return a redirect URI to direct your user to. The list of strings is the scopes you want permission for, and you can use the `state` parameter to include some basic data with your authorization request which will be returned to you after the user is done with the OAuth2 consent page. If you're using flask, a basic set up could look like this:

```py
from flask import Flask, request, redirect
from rblxopencloud import OAuth2App

rblxapp = OAuth2App(0000000000000000000, "your-client-secret", "https://example.com/redirect")
app = Flask(__name__)

@app.route('/login')
def login():
    return redirect(rblxapp.generate_uri(['openid', 'profile']))
```

### Exchanging the Code

After the user has authorized your app on the consent page, Roblox will redirect them to the redirect URI you configured, with a special code, and if provided, a state in the parameters, like this:
```
https://example.com/redirect?code=examplecode&state=yourstatehere
``` 
You will need to extract that code from the URI and pass it through [`OAuth2App.exchange_code`][rblxopencloud.OAuth2App.exchange_code], as shown below:
```py
access = rblxapp.exchange_code("examplecode")
```
This will return an [`rblxopencloud.AccessToken`][rblxopencloud.AccessToken], which will be explained below. If you're using flask, a basic set up could look like this:

```py
@app.route('/redirect')
def redirect():
    access = rblxapp.exchange_code(request.args.get('code'))
```

### Accessing Authorized Data

All authorized data can be accessed from the [`rblxopencloud.AccessToken`][rblxopencloud.AccessToken]. If you used the `openid` scope, you can access the user's ID using `access.user.id`. If you also used the `profile` scope, you can access other user info such as `access.user.username` and `access.user.headshot_uri`. However if you've requested access to the user's resources, it gets a little bit more complex.

If you've request access to the user's inventory (`user.inventory-item:read`) or groups (`group:read`), you can use the methods inside of [`AccessToken.user`][rblxopencloud.AccessToken], for example like this:
```py
for item in access.user.list_inventory():
    print(item)

for membership in access.user.list_groups():
    print(membership)
```

However, things get a little bit more complex if you asked for permissions for the user's experiences, or scopes that could apply to both users, and groups such as `asset:write`. These are covered in the [Accessing Resources](#accessing-resources) section below.

## Advanced Usecases

### Accessing Resources

When requesting scopes for experiences, or accounts (users and groups), the user chooses what experiences/accounts get that scope. For example, the use may want to provide you access to upload asset's to their group but not personal account. After exchanging the code, you have to use [`AccessToken.fetch_resources`][rblxopencloud.AccessToken.fetch_resources] to see what accounts and experiences were authorized. Here's an example:
```py
resources = access.fetch_resources()

print(resources.experiences)

print(resources.accounts)
```

[`Resources.experiences`][rblxopencloud.Resources] is a list of [`rblxopencloud.Experience`][rblxopencloud.Experience] objects, and [`Resources.accounts`][rblxopencloud.Resources] is a list of [`rblxopencloud.User`][rblxopencloud.User] and [`rblxopencloud.Group`][rblxopencloud.Group] objects. The example below will fetch resources, and send a messaging service message to every experience that was authorized.
```py
resources = access.fetch_resources()

for experience in resources.experiences:
    experience.publish_message("exampletopic", "exampledata")
```

### Refreshing Tokens

Roblox Access Tokens only last for 15 minutes before expiring, once an Access Token has expired, it can no longer be used. However, instead of request authorization from the user every 15 minutes, you can refresh a token. When your app is first authorized, you must store the [`AccessToken.refresh_token`][rblxopencloud.AccessToken] somewhere where you'll be able to access it later. Anytime within 6 months of previously refreshing the token, you may use [`OAuth2App.refresh_token`][rblxopencloud.OAuth2App.refresh_token] to convert it to a new Access Token, like this example below:

```py
access = rblxapp.refresh_token("your stored refresh token")
```

Note that the new access token will not have a [`AccessToken.user`][rblxopencloud.AccessToken], and instead you'll have to use [`AccessToken.fetch_userinfo()`][rblxopencloud.AccessToken.fetch_userinfo]. After refreshing the token, you will recieve a new refresh token which you must store in the old token's place. The old token is completly useless after it has been used.

!!! warning
    After refreshing a token, the old token will no longer work. You must store the new token.

### Revoking Tokens

When you're finished with an authorization and you won't need to use it anymore, you can revoke the token, and it's refresh token pair by using [`AccessToken.revoke()`][rblxopencloud.AccessToken.revoke], here's an example:

```py
access.revoke()
```
Users can still authorize your app again and you will be able to get a new access token after they authorize it. Revoking the Token will immedietly invalidate it, and it's refresh token.

### Authorization with PKCE

If your application can't keep a secret (the application's client secret can not be kept a secret from other parties), then you should use PKCE for extra security. Before you redirect a user, you should generate a code verifier using [`OAuth2App.generate_code_verifier()`][rblxopencloud.OAuth2App.generate_code_verifier], and then pass it to the [`OAuth2App.generate_uri()`][rblxopencloud.OAuth2App.generate_uri] in the `code_verifier` field, like this:
```py
code_verifier = rblxapp.generate_code_verifier()
rblxapp.generate_uri(['openid', 'profile'], code_verifier=code_verifier)
```
You will need to store the code verifier for when the user returns back from the authorization page. When the user does return from the authorization page, you must feed the code verifier with the code in [`OAuth2App.exchange_code()`][rblxopencloud.OAuth2App.exchange_code], like this:
```py
access = rblxapp.exchange_code("examplecode", code_verifier=code_verifier)
```
If your application has a chance of multiple users authorizing at once, you'll need to set up a cache and give each authorization a state to ensure code verifiers don't get mixed up.