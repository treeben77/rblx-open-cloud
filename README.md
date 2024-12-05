# rblx-open-cloud

[![Discord Server](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fdiscord.com%2Fapi%2Fv10%2Finvites%2F4CSc9E5uQy%3Fwith_counts%3Dtrue&query=%24.approximate_member_count&suffix=%20members&style=for-the-badge&logo=discord&logoColor=white&label=Discord%20Server&labelColor=%235865F2&color=%23353535)](https://discord.gg/4CSc9E5uQy)
[![DevForum Post](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fdevforum.roproxy.com%2Ft%2F1991959.json&query=%24.like_count&suffix=%20Likes&style=for-the-badge&logo=robloxstudio&logoColor=white&label=DevForum%20Post&labelColor=%23009fff&color=%23353535)](https://devforum.roblox.com/t/1991959)
[![Downloads](https://img.shields.io/pypi/dm/rblx-open-cloud?style=for-the-badge&logo=pypi&logoColor=white&label=PyPi%20Downloads&labelColor=%23006dad&color=%23353535)](https://pypi.org/project/rblx-open-cloud)

rblx-open-cloud is a Python API wrapper for [Roblox Open Cloud](https://create.roblox.com/docs/cloud/open-cloud).

### Key Features
- Support for most endpoints, including the OAuth2 flow and authentication.
- Allows both syncronous and asyncronous usage.
- Logic for operation polling and internal error retrying.

**Documentation: https://rblx-open-cloud.readthedocs.io/en/latest/**

## Quickstart

### Getting Started

1. Install the library with pip in your terminal.

```sh
# Stable (PyPi, recommended)
pip install rblx-open-cloud~=2.0

# Development (GitHub)
pip install "rblx-open-cloud @ git+https://github.com/treeben77/rblx-open-cloud@main"
```

2. Create an API key from the [Creator Dashboard](https://create.roblox.com/credentials). You can read [Managing API Keys](https://create.roblox.com/docs/open-cloud/managing-api-keys) for help.

You've got the basics down, below are examples for some of the APIs.

### Accessing Data Stores

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
with open("path/to/file.png", "rb", encoding="utf-8") as file:
    asset = user.upload_asset(file, rblxopencloud.AssetType.Decal, "name", "description").wait()

print(asset.id)
```

Examples for more APIs are avalible in the [examples](/examples/) directory.
