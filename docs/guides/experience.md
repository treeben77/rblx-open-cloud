# Experience

The experience object allows access to an experience's resources such as data stores, messaging service, or uploading places.

## Getting Started

### Creating an API Key

To use any APIs, first you will need to create an API key, the key allows the library to preform requests. To create an API key, you must go to the [Creator Dashboard](https://create.roblox.com/dashboard/credentials), switch to the creator (e.g. user/group) who owns the experience if necessary, and then press 'CREATE API KEY'. This will open the new API key menu.

First, you will need to give your API key a name, it should be something that will help you identify it from any other API keys you might have. Next, you will need to define what APIS and permissions you give to your API key. APIs such as DataStore, or Messaging Service API are experience APIs. Once you've selected the API you'd like to use, press 'ADD API SYSTEM', and it will appear below.

For experience APIs, you will need to specifiy what experience(s) to use allow by clicking 'Select an Experience' and 'ADD EXPERIENCE'. The experience's name will appear below, and now you can specify what API operations. The API permissions you provide here will define what functions you can use in the library.

Once you've finished selecting permissions, the last section is security. This allows you to define what IP addresses/CIDR notations can use your API key, and how long until it expires. If you do not know your IP address, you can add `0.0.0.0/0` to the IP address list to allow all IP addresses. The experiation allows you to configure a set time for your API key to be disabled, which is useful if you plan to not use the API key in the future.

After pressing 'SAVE & GENERATE KEY', Roblox will provide you with a string of random letters, numbers and symbols. You will need this key, but do not share the key with anyone else. This key allows people to use your API key!

!!! warning
    When selecting permissions, you should provide only what APIs and scopes your API key will need to use. This helps minize the impact if the API key is comprimised. Using `0.0.0.0/0` significantly increases the risk in your API key being used by bad actors.

### The `Experience` Object

Now that you've created an API key, you may now use it in your code. The following code library imports and creates an [`rblxopencloud.Experience`][rblxopencloud.Experience] object:

```py
from rblxopencloud import Experience

experience = Experience(00000000, "your-api-key")
```

Replace `00000000` with your experience/universe ID (NOT place ID), and `your-api-key` with the API key string you just generated. Now that you've created an [`rblxopencloud.Experience`][rblxopencloud.Experience] object, you can start using the experience APIs!

## DataStore APIs

### Getting Data Stores

You can use Open Cloud to access your experience's [DataStores](https://create.roblox.com/docs/cloud-services/datastores) in Python, including Ordered Data Stores. This could be useful if you're creating a Discord bot, or website to remotly manage user data, or to control certain settings.

To get started, you will need to create a [`rblxopencloud.DataStore`][rblxopencloud.DataStore] object. The following code example creates a [`rblxopencloud.DataStore`][rblxopencloud.DataStore] with the name 'ExampleStore' and the scope 'global' (global is the default scope in Lua):

```py
datastore = experience.get_data_store("ExampleStore", scope="global")
```

Great! Now that you've created a data store, you can now access it's entrys.  

!!! tip
    You can set the `scope` parameter to `None` if you want to access all scopes. You will be required to format keys in the `scope/key` syntax. For example, in `pets/user_287113233`, the scope is `pets`, and `user_287113233` is the key.

### Getting Keys

To get the value of a DataStore key, you can use [`DataStore.get_entry`][rblxopencloud.DataStore.get_entry]. The following code will get the value for `user_287113233` in the data store.

```py
value, info = datastore.get_entry("user_287113233")
```

[`DataStore.get_entry`][rblxopencloud.DataStore.get_entry] returns a tuple of two items, the key's value, and an [`rblxopencloud.EntryInfo`][rblxopencloud.EntryInfo] object. The value can be either `str`, `int`, `float`, `list`, or `dict`, and is the equivalent value in Roblox Lua. The [`rblxopencloud.EntryInfo`][rblxopencloud.EntryInfo] object contains metadata about the DataStore key, such as the current version ID, when it was created and last updated, a list of user IDs for GDPR tracking, and the custom metadata, learn more about this on [Roblox's DataStore Guide](https://create.roblox.com/docs/cloud-services/datastores#metadata).

If the requested key does not exist, then this method will raise [`rblxopencloud.NotFound`][rblxopencloud.NotFound]. So, you should create a try block and deal with errors correctly, for example:

```py
try:
    value, info = datastore.get_entry("user_287113233")
except(rblxopencloud.NotFound):
    print("the key doesn't exist!")
else:
    print(f"the key's value is {value}.")
```

You can list all keys in a Data Store using [`DataStore.list_keys`][rblxopencloud.DataStore.list_keys], it will iterate all keys in the DataStore, and can be used like this:

```py
for key in datastore.list_keys():
    print(key.key, key.scope)
```

If the data store's scope is `None` this will return keys from every scope. You can also provide an optional `prefix`, and `limit`.

### Changing Keys

DataStore values can be changed with [`DataStore.set_entry`][rblxopencloud.DataStore.set_entry] and [`DataStore.increment_entry`][rblxopencloud.DataStore.increment_entry]. Both will need the 'Create Entry' permission to create new keys, and/or 'Update Entry' permission to update existing keys. First, here's an example using [`DataStore.set_entry`][rblxopencloud.DataStore.set_entry]:

```py
version = datastore.set_entry("user_287113233", {"xp": 1337, "level": 7}, users=[287113233])
```

This will set the key `user_287113233` to the dictionary `{"xp": 1337, "level": 7}`, with the user's ID in the list of users. The method returns [`rblxopencloud.EntryVersion`][rblxopencloud.EntryVersion], which contains metadata about the new version, such as it's version ID. The code above is equivalent to the the following lua code:

```lua
local version = DataStore:SetAsync("user_287113233", {["xp"] = 1337, ["level"] = 7}, {287113233})
```

If the current value of the key is an integer, or float you can use [`DataStore.increment_entry`][rblxopencloud.DataStore.increment_entry] to update the value, while guaranteeing you don't overwrite the old value. The following example will increment the key `user_score_287113233` by 70:

```py
value, info = datastore.increment_entry("user_score_287113233", 70, users=[287113233])
```

[`DataStore.increment_entry`][rblxopencloud.DataStore.increment_entry] actually returns the new value just like [`DataStore.get_entry`][rblxopencloud.DataStore.get_entry] instead.

!!! warning
    If an entry has `users` and `metadata`, you must provide them every time you set or increment the value, otherwise they will be removed.

### Removing Keys

You can remove a key from a DataStore with Open Cloud with the following code:

```py
version = datastore.remove_entry("user_287113233")
```

This will mark the key as deleted, and calls to get the key will fail. However, the old version of the key can still be accessed by listing versions (explained below), and listing keys will still return the key. These are limitations with Open Cloud, not one with the library.

### Key Versioning

Data Stores retain previous versions of the key for 30 days. You can list all previous versions with [`DataStore.list_versions`][rblxopencloud.DataStore.list_versions], like this:

```py
for version in datastore.list_versions("user_287113233"):
    print(version, version.get_value())
```

This will iterate [`rblxopencloud.EntryVersion`][rblxopencloud.EntryVersion] for every version in the key. It contains information like the version ID, when the version was created, the content length, and wether it has been deleted. You can fetch a version's value with [`EntryVersion.get_value`][rblxopencloud.EntryVersion.get_value], but if you already have the version ID, and don't need to list versions you can use [`DataStore.get_version`][rblxopencloud.DataStore.get_version].

```py
value, info = datastore.get_version("user_287113233", "VERSION_ID")
```

It returns the same as [`DataStore.get_entry`][rblxopencloud.DataStore.get_entry].

### Ordered Data Stores

You can also access Ordered Data Stores with Open Cloud. There are a few differences between regular Data Stores and Ordered Data Stores:

- Ordered Data Store do not support versioning, therefore you can not use versioning functions.
- Ordered Data Stores also do not support user IDs or metadata, and since they also don't support versioning, there is no second parameter returned on get methods.
- [`OrderedDataStore.set_entry`][rblxopencloud.OrderedDataStore.set_entry] doesn't have the `previous_version` precondition, instead it has an `exclusive_update` precondition.
- Ordered Data Stores don't have a `list_keys` method, but instead [`OrderedDataStore.sort_keys`][rblxopencloud.OrderedDataStore.sort_keys]. They also iterate [`rblxopencloud.SortedEntry`][rblxopencloud.SortedEntry] which includes the key's value.

To create an Ordered Data Store, you can use the [`Experience.get_ordered_datastore`][rblxopencloud.Experience.get_ordered_datastore] method, which also supports `scope` being `None`:

```py
datastore = experience.get_ordered_data_store("ExampleStore", scope="global")
```

## Other Experience APIs

You can also use other experience APIs with open cloud, some of which are shown below.

### Messaging Service

You can publish messages with Open Cloud that live game servers will recieve. Here's an example to send a messsage top the topic `topic-name`:

```py
experience.publish_message("topic-name", "this is an example message content.")
```

!!! note
    Messages sent by Open Cloud with only be recieved by live servers. Studio won't recieve thesse messages.

!!! warning
    The messaging service only supports strings being sent. To send more complex data, such as dictionaries, you will need to JSON encode the string. See [the json built-in python library](https://docs.python.org/3/library/json.html) and [the Roblox game engine method HttpService:JSONDecode()](https://create.roblox.com/docs/reference/engine/classes/HttpService#JSONDecode).

You can not recieve messages with Open Cloud.

### User Restrictions (Banning) API

You can fetch, ban and unban users from the experience with Open Cloud. Here is an example to ban and then unban a user from the entire experience:

```py
experience.ban_user(
    287113233, duration_seconds=86400,
    display_reason="Breaking the rules.",
    private_reason="Top secret!"
)
```

Display reason is shown to the client, whereas private reason is not. `287113233` is the ID of the user that will be banned, and detected alternative accounts will also be banned by default. The duration in section is how long it will last. If you want to ban them permemently, set it to `None`. You can unban a user as such:

```py
experience.ban_user(287113233)
```

Additionally, you can check whether a user is banned and get information about why they are banned with the following code:

```py
restriction = experience.fetch_user_restriction(287113233)

if restriction.active:
    print(f"The user is banned because: {restriction.private_reason}")
else:
    print(f"The user is not banned right now!")
```

The previous methods can also be used on a place-level by using a them from a [`Place`][rblxopencloud.Place] object.