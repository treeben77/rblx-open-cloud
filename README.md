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
you can use `access.user` if you used the `openid` scope, if you only retrieved the profile scope or `access.user` is somehow None, you can use an API call:
```py
access.fetch_userinfo()
```
This will return a `User` object with the following attributes:
- username - str, requires `openid` and `profile`
- id - int, requires `openid`
- display_name - str, requires `openid` and `profile`
- profile_uri - int, requires `openid`
- created_at - datetime, requires `openid` and `profile`

### Fetching resources
If you use a scope that gives experience, group, or user access, you'll have to fetch the resources using `access.fetch_resources`. This will return a Resources object which has two attributes:
- experiences - list of ([Experience](https://rblx-open-cloud.readthedocs.io/en/latest/experience/#rblx-open-cloud.Experience))
- creators - list of ([User](https://rblx-open-cloud.readthedocs.io/en/latest/user/#rblx-open-cloud.User)) and ([Group](https://rblx-open-cloud.readthedocs.io/en/latest/group/#rblx-open-cloud.Group))
*all above types are already documented, because they're in the main library and can also be accessed with api keys!*

Here's an example to publish a message to the first experience in the list:
```py
resources = access.fetch_resources()
resources.experiences[0].publish_message("topic", "string-message")
```

Here's an example to upload an image to the first creator in the list:
```py
resources = access.fetch_resources()
with open("path-to/file-object.png", "rb") as file:
    resources.creators[0].upload_asset(file, rblxopencloud.AssetType.Decal, "name", "description")
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

### Changing the openID certs cache time

By default, certs are cached for 1 hour but this can be modified when creating the `OAuth2App` object. This example will only allow the certs to be stored for 2 minutes (120 seconds)
```py
oauth2 = rblxopencloud.OAuth2App(123456789, "app-secert", "http://localhost:9066/roblox", openid_certs_cache_seconds=120)
```

### Fetching introspect/Token Info
```py
access.fetch_token_info()
```
This will return an `AccessTokenInfo` with the following attributes:
- active - str, wether the token has expired
- id - str, a unique ID for this token
- client_id - str, your app's ID
- user_id - str, the authorized account's user ID
- scope - list[str], list of authorized scopes
- expires_at - datetime.datetime, time the token will expire
- issued_at - datetime.datetime, time the token was generated at
- raw - dict, the raw date **may be removed**

### Finishing notes
Don't forget to run the Flask server at the end:
```py
app.run("localhost", 9066)
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

2. Create an API key from the [Creator Dashboard](https://create.roblox.com/credentials). You can read [Managing API Keys](https://create.roblox.com/docs/open-cloud/managing-api-keys) for help.

You've got the basics down, below are examples for some of the APIs.

### Accessing Data Stores
**NOTE: Roblox doesn't support access to ordered data stores via open cloud yet.**
```py
import rblxopencloud

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
```

### Publishing To Message Service
**NOTE: Messages published with Open Cloud only arrive in live game servers and not in Studio.**
```py
import rblxopencloud

# create an Experience object with your experience ID and your api key
# TODO: replace '13058' with your experience ID
experience = rblxopencloud.Experience(13058, api_key="api-key-from-step-2")

# publish a message with the topic 'topic-name'
experience.publish_message("topic-name", "Hello World!")
```

### Uploading Assets
**NOTE: Only `Decal`, `Audio`, and `Model` (fbx) are supported right now.**
```py
import rblxopencloud

# create an User object with your user ID and your api key
# TODO: replace '13058' with your user ID
user = rblxopencloud.User(13058, api_key="api-key-from-step-2")
# or, create a Group object:
group = rblxopencloud.Group(13058, api_key="api-key-from-step-2")

# this example is for uploading a decal:
with open("path-to/file-object.png", "rb") as file:
    user.upload_asset(file, rblxopencloud.AssetType.Decal, "name", "description")

# this will wait until Roblox has processed the upload
if isinstance(asset, rblxopencloud.Asset):
    # if it's already been processed, then print the asset.
    print(asset)
else:
    # otherwise, we'll go into a loop that continuosly checks if it's done.
    while True:
        # this will try to check if the asset has been processed yet
        operation = asset.fetch_operation()
        if operation:
            # if it has been print it then stop the loop.
            print(operation)
            break
```
Examples for more APIs are avalible in the [examples](https://github.com/TreeBen77/rblx-open-cloud/tree/main/examples) directory.