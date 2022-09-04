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