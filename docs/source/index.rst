Welcome to ``rblx-open-cloud``!
===============

Quickstart
----------

Getting Started
~~~~~~~~~~~~~~~

1. Install the library with pip in your terminal.

   .. code::

      pip install rblx-open-cloud

2. Create an API key from the `Creator Dashboard <https://create.roblox.com/credentials>`__. You can read
   `Managing API Keys <https://create.roblox.com/docs/open-cloud/managing-api-keys>`__
   if you get stuck.

3. Add the following code to your project and replace
   ``api-key-from-step-2`` with the key you generated.

   If you don't know how to get the experience or place ID read
   `Publishing Places with API
   Keys <https://create.roblox.com/docs/open-cloud/publishing-places-with-api-keys#:~:text=Find%20the%20experience,is%206985028626.>`__

.. code:: py

   import rblxopencloud
   # create an Experience object with your experience ID and your api key
   # TODO: replace '13058' with your experience ID
   experience = rblxopencloud.Experience(13058, api_key="api-key-from-step-2")`

4. If you want to start by accessing your game's data stores go to `Data
   Stores <#accessing-data-stores>`__ otherwise, you can go to
   `Messaging Service <#publishing-to-message-service>`__ if you want to
   publish messages to live game servers, or `Place
   Publishing <#publish-or-save-a-rbxl-file>`__ if you'd like to upload
   ``.rbxl`` files to Roblox.*\*

Accessing Data Stores
~~~~~~~~~~~~~~~~~~~~~

.. code:: py

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

Publishing To Message Service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**NOTE: Messages published with Open Cloud only arrive in live game
servers and not in Studio, so you'll have to publish the place to test
this.**

.. code:: py

   # publish a message with the topic 'topic-name'
   experience.publish_message("topic-name", "Hello World!")

Publish or Save a ``.rbxl`` File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: py

   #open the .rbxl file as read bytes
   with open("path-to/place-file.rbxl", "rb") as file:
       # the first number is the place ID to update, and publish denotes wether to publish or save the place.
       # TODO: replace '1818' with your place ID
       experience.upload_place(1818, file, publish=False)

Final Result (a.k.a copy and paste section)
-------------------------------------------

.. code:: py

   # create a Experience object with your experience ID and your api key
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
   
Table of Contents
----------

.. toctree::

   experience
   user
   group
   oauth2
   datastore
   creator
   exceptions
