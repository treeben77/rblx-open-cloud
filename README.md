## **IMPORTANT**

**The Assets API is an alpha API subject to breaking changes and it is not avaliable to everyone. DO NOT try to use it unless you have access. You might be looking for [main](https://github.com/TreeBen77/rblx-open-cloud/tree/main).**

## If you understand the above:

Installing:
```console
pip install git+https://github.com/TreeBen77/rblx-open-cloud/tree/assetsapi
```
there's no documantation yet. but here's a cheat sheet
```py
import rblxopencloud

# to upload to your own account, use Creator - insert your user ID and api key
creator = rblxopencloud.Creator(287113233, "api-key-here")
# to upload to your group, use GroupCreator - insert your group ID and api key
creator = rblxopencloud.GroupCreator(9697297, "api-key-here")

# let's start with decals. open the file as read bytes.
with open("experiment.png", "rb") as file:
    # call the create_decal object, name is the item name and description is the item description
    asset = creator.create_decal(file, "name", "description")
    # asset will be either Asset or PendingAsset. Asset contains it's ID and version number
    # PendingAsset means roblox hasn't finnished processing it. This will have a fetch_status method
    # and that's it. the fetch status method will check if it's ready yet, it will return None or Asset.

    # here's a method that will wait until the decal is ready
    if isinstance(asset, rblxopencloud.Asset):
        # if it's already been processed, then print the asset.
        print(asset)
    else:
        # otherwise, we'll go into a loop that continuosly loops through that.
        while True:
            # this will try to check if the asset has been processed yet
            status = asset.fetch_status()
            if status:
                # if it has been print it then stop the loop.
                print(status)
                break

# now for audio. it's the same as above but with audio
# there's a bug with audio and groups preventing it from uploading right now.
with open("experiment.mp3", "rb") as file:
    # call the create_decal object, name is the item name and description is the item description
    asset = creator.create_audio(file, "name", "description")
    # for simplicity, i won't include the asset fetch_status part above here but it also works.

    # please note that you can only upload 10 audios a month and if you're ID verified that's 100.

# and finally for .fbx files. it's the same as above but with a model
with open("experiment.fbx", "rb") as file:
    # call the create_decal object, name is the item name and description is the item description
    asset = creator.create_fbx(file, "name", "description")
    # for simplicity, i won't include the asset fetch_status part above here but it also works.
    # you're post likely going to recieve a PendingAsset with models because roblox has to render them which takes time

# you can also update uploaded fbx files:
with open("experiment.2.fbx", "rb") as file:
    # the first number is the fbx asset you want to update
    asset = creator.create_fbx(11326252443, file)
    # for simplicity, i won't include the asset fetch_status part above here but it also works.
    # you're post likely going to recieve a PendingAsset with models because roblox has to render them which takes time

```
**IMPORTANT:** This code is also subject to breaking changes. Don't use it in production code!

# rblx-open-cloud
 
Python API wrapper for [Roblox Open Cloud](https://create.roblox.com/docs/open-cloud/index).

**Documentation: https://rblx-open-cloud.readthedocs.io**

## Quickstart

### Getting Started

1. Install the library with pip in your terminal.
    ```console
    pip install rblx-open-cloud
    ```

2. Create an API key from the [Creator Dashboard](https://create.roblox.com/credentials). You can read [Managing API Keys](https://create.roblox.com/docs/open-cloud/managing-api-keys) if you get stuck.

3. Add the following code to your project and replace `api-key-from-step-2` with the key you generated.
    ```py
    # create a Universe object with your universe/experience ID and your api key
    # TODO: replace '13058' with your universe ID
    universe = rblxopencloud.Universe(13058, api_key="api-key-from-step-2")
    ```
    If you don't know how to get the universe or place ID read [Publishing Places with API Keys](https://create.roblox.com/docs/open-cloud/publishing-places-with-api-keys#:~:text=Find%20the%20experience,is%206985028626.)

4. If you want to start by accessing your game's data stores go to [Data Stores](#accessing-data-stores) otherwise, you can go to [Messaging Service](#publishing-to-message-service) if you want to publish messages to live game servers, or [Place Publishing](#publish-or-save-a-rbxl-file) if you'd like to upload `.rbxl` files to Roblox.**

### Accessing Data Stores
**NOTE: Roblox doesn't support access to ordered data stores via open cloud at the moment.**
```py
# get the data store, using the data store name and scope (defaults to global)
datastore = universe.get_data_store("data-store-name", scope="global")

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
universe.publish_message("topic-name", "Hello World!")
```

### Publish or Save a `.rbxl` File
**NOTE: [Place Publishing](#publish-or-save-a-rbxl-file) isn't included in this example due to it requiring an `.rbxl` file.**
```py
#open the .rbxl file as read bytes
with open("path-to/place-file.rbxl", "rb") as file:
    # the first number is the place ID to update, and publish denotes wether to publish or save the place.
    # TODO: replace '1818' with your place ID
    universe.upload_place(1818, file, publish=False)
```
## Final Result (a.k.a copy and paste section)
```py
# create a Universe object with your universe/experience ID and your api key
# TODO: replace '13058' with your universe ID
universe = rblxopencloud.Universe(13058, api_key="api-key-from-step-2")

# get the data store, using the data store name and scope (defaults to global)
datastore = universe.get_data_store("data-store-name", scope="global")

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
universe.publish_message("topic-name", "Hello World!")
```