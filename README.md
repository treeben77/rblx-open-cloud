## OAuth2 Beta API Info

**__IMPORTANT: This is an UNRELEASED API and is subject to change. It may break at any time, the code may recieve breaking changes, and is overall an unstable API. You should not auto update this beta branch. You must be enrolled in the beta to join, you can do so here: https://devforum.roblox.com/t/open-cloud-oauth20-alpha-program/1791194/84?u=treeben77__**

The beta is undocumented but here's some instructions: Once you've created an App you can process requests using the examples below (using Flask):

### Installing the beta library
Run this command in your terminal.
```console
pip install git+https://github.com/TreeBen77/rblx-open-cloud.git@oauth2
```
### Creating an `OAuth2App` and `Flask` object

```py
from flask import Flask, request, redirect
import rblxopencloud

app = Flask(__name__)
oauth2 = rblxopencloud.OAuth2App(123456789, "app-secert", "http://localhost:9066/roblox")
```
`123456789` should be your client ID, `"app-secert"` should be your client secret (should be stored in enviroment) and `"http://localhost:9066/roblox"` is the redirect uri.

### Generating the redirect URI
You can build the URI yourself and paste that, but a cleaner solution is using the built in uri builder.
```py
@app.route("/")
def index():
    return redirect(oauth2.generate_uri(scope=["openid", "profile"], state="hello world"))
```
scope should be either a string (with scopes seperated with a space) or a list of strings. State is optional, but recommended.

### Exchanging the code

```py
@app.route("/roblox")
def roblox():
    access = oauth2.exchange_code(code=request.args["code"])
```
This will return an `AccessToken` object. This allows you to retrieve all the information about the authorization.

### Fetching user info
**NOTE: OpenID is not yet supported. I'm still trying to figure that out.**
```py
access.fetch_userinfo()
```
This will return a `User` object with the following attributes:
- username - str, requires `openid` and `profile`
- id - int, requires `openid`
- display_name - str, requires `openid` and `profile`
- profile_uri - int, requires `openid`
- created_at - datetime, requires `openid` and `profile`
### Fetching experiences
If you use a scope that gives experience access, you'll have to fetch the experiences. This will return a list of `Experience` ([this is actually documented!](https://rblx-open-cloud.readthedocs.io/en/latest/experience/#rblx-open-cloud.Experience))
```py
experiences = access.fetch_experiences()
```
Here's an example to publish a message to the first experience in the list:
```py
experiences = access.fetch_experiences()
experiences[0].publish_message("topic", "string-message")
```

### Refreshing a token
After the old token expires, you must renew it using `refresh_token`. Here's how to do that:
```py
new_access = oauth2.refresh_token(access.refresh_token)
```

### Using a database to store tokens
You can use the `refresh_token` value from `AccessToken` and store that. Next time you want to access the user's account refresh the token above. You can also reload an `access_token`, but it's unadvised because it's insecure and the tokens expire shortly.
```py
oauth2.from_access_token_string(access.token)
```
**NOTE: This returns a `PartialAccessToken`, which is almost identical to an `AccessToken` except for it doesn't have `revoke_refresh_token`, `scope`, `refresh_token`, or `expires_at`.**
### Revoking tokens
Once you're finished with an `AccessToken`, you can use the `revoke_token` function to revoke it. Here's how to use it:
```py
oauth2.revoke_token(access.token)
```
You can also revoke tokens from the `AccessToken` object itself:
```py
access.revoke()
access.revoke_refresh_token()
```
If you have any feedback for the beta, or want to report bugs, please join the Discord server: https://discord.gg/gEBdHNAR46, message [TreeBen77](https://devforum.roblox.com/u/TreeBen77) on the DevForum, or message [TreeBen77](https://www.roblox.com/users/287113233) on Roblox (must follow me first).
___

# rblx-open-cloud
 
Python API wrapper for [Roblox Open Cloud](https://create.roblox.com/docs/open-cloud/index).

**Documentation: https://rblx-open-cloud.readthedocs.io**

**Discord Server: https://discord.gg/gEBdHNAR46**

## Quickstart

### Getting Started

1. Install the library with pip in your terminal.
    ```console
    pip install rblx-open-cloud
    ```

2. Create an API key from the [Creator Dashboard](https://create.roblox.com/credentials). You can read [Managing API Keys](https://create.roblox.com/docs/open-cloud/managing-api-keys) if you get stuck.

3. Add the following code to your project and replace `api-key-from-step-2` with the key you generated.
    ```py
    # create an Experience object with your experience ID and your api key
    # TODO: replace '13058' with your experience ID
    experience = rblxopencloud.Experience(13058, api_key="api-key-from-step-2")
    ```
    If you don't know how to get the experience or place ID read [Publishing Places with API Keys](https://create.roblox.com/docs/open-cloud/publishing-places-with-api-keys#:~:text=Find%20the%20experience,is%206985028626.)

4. If you want to start by accessing your game's data stores go to [Data Stores](#accessing-data-stores) otherwise, you can go to [Messaging Service](#publishing-to-message-service) if you want to publish messages to live game servers, or [Place Publishing](#publish-or-save-a-rbxl-file) if you'd like to upload `.rbxl` files to Roblox.**

### Accessing Data Stores
**NOTE: Roblox doesn't support access to ordered data stores via open cloud at the moment.**
```py
# get the data store, using the data store name and scope (defaults to global)
datastore = experience.get_data_store("data-store-name", scope="global")

# sets the key 'key-name' to 68 and provides users and metadata
# DataStore.set does not return the value or an EntryInfo object, instead it returns a EntryVersion object.
datastore.set("key-name", 68, users=[287113233], metadata={"key": "value"})

# get the value with the key 'number'
# info is a EntryInfo object which contains data like the version code, metadata, userids and timestamps.
value, info = datastore.get("key-name")

print(value, info)

# increments the key 'key-name' by 1 and ensures to keep the old users and metadata
# DataStore.increment retuens a value and info pair, just like DataStore.get and unlike DataStore.set
value, info = datastore.increment("key-name", 1, users=info.users, metadata=info.metadata)

print(value, info)

# deletes the key
datastore.remove("key-name")
```

### Publishing To Message Service
**NOTE: Messages published with Open Cloud only arrive in live game servers and not in Studio, so you'll have to publish the place to test this.**
```py
# publish a message with the topic 'topic-name'
experience.publish_message("topic-name", "Hello World!")
```

### Publish or Save a `.rbxl` File
**NOTE: [Place Publishing](#publish-or-save-a-rbxl-file) isn't included in this example due to it requiring an `.rbxl` file.**
```py
#open the .rbxl file as read bytes
with open("path-to/place-file.rbxl", "rb") as file:
    # the first number is the place ID to update, and publish denotes wether to publish or save the place.
    # TODO: replace '1818' with your place ID
    experience.upload_place(1818, file, publish=False)
```
## Final Result (a.k.a copy and paste section)
```py
# create an Experience object with your experience ID and your api key
# TODO: replace '13058' with your experience ID
experience = rblxopencloud.Experience(13058, api_key="api-key-from-step-2")

# get the data store, using the data store name and scope (defaults to global)
datastore = experience.get_data_store("data-store-name", scope="global")

# sets the key 'key-name' to 68 and provides users and metadata
# DataStore.set does not return the value or an EntryInfo object, instead it returns a EntryVersion object.
datastore.set("key-name", 68, users=[287113233], metadata={"key": "value"})

# get the value with the key 'number'
# info is a EntryInfo object which contains data like the version code, metadata, userids and timestamps.
value, info = datastore.get("key-name")

print(value, info)

# increments the key 'key-name' by 1 and ensures to keep the old users and metadata
# DataStore.increment retuens a value and info pair, just like DataStore.get and unlike DataStore.set
value, info = datastore.increment("key-name", 1, users=info.users, metadata=info.metadata)

print(value, info)

# deletes the key
datastore.remove("key-name")

# publish a message with the topic 'topic-name'
experience.publish_message("topic-name", "Hello World!")
```
