Universe
=============================

.. currentmodule:: rblx-open-cloud

.. class:: Universe(id, api_key)

   Class for interacting with the API for a specific universe.

   :param int id: A Universe ID. Read How to find yours here: `Publishing Places with API Keys <https://create.roblox.com/docs/open-cloud/publishing-places-with-api-keys>`__
   :param str api_key: An API key created from `Creator Dashboard <https://create.roblox.com/credentials>`__. *this should be kept safe, as anyone with the key can use it!*

   .. attribute:: id 

      The universe's ID

      :type: int
   
   .. method:: get_data_store(name, scope="global")

         Creates a :class:`rblx-open-cloud.DataStore` without :attr:`DataStore.created` with the provided name and scope.

         Lua equivalent: `DataStoreService:GetDataStore() <https://create.roblox.com/docs/reference/engine/classes/DataStoreService#GetDataStore>`__

         :param str name: The name of the data store
         :param str scope: A string specifying the scope.
         :returns: :class:`rblx-open-cloud.DataStore`

         .. note::
            Roblox does not support accessing OrderedDataStores with Open Cloud.
   
   .. method:: list_data_stores(prefix="")

         Lua equivalent: `DataStoreService:ListDataStoresAsync() <https://create.roblox.com/docs/reference/engine/classes/DataStoreService#ListDataStoresAsync>`__

         Returns an Iterable of all class:`rblx-open-cloud.DataStore` in the Universe which includes :attr:`rblx-open-cloud.DataStore.created`, optionally matching a prefix.

        The example below would list all versions, along with their value.
                
        .. code:: py

            for datastore in universe.list_data_stores():
                print(datastore.key)
        
        You can simply convert it to a list by putting it in the list function:

        .. code:: py

            list(universe.list_data_stores())

         :returns: Iterable[:class:`rblx-open-cloud.DataStore`]
         :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to list data stores.
         :raises rblx-open-cloud.NotFound: *This shouldn't be raised for this method.*
         :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
         :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
         :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

   .. method:: publish_message(topic, data)

         Publishes a message to live game servers that can be recieved with `MessagingService <https://create.roblox.com/docs/reference/engine/classes/MessagingService>`__.

         Lua equivalent: `MessagingService:PublishAsync() <https://create.roblox.com/docs/reference/engine/classes/MessagingService#PublishAsync>`__

         :param str topic: The topic that servers can subscribe to.
         :param str data: The data to send. Must be a string.
         :returns: None
         :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to publish messages.
         :raises rblx-open-cloud.NotFound: *This shouldn't be raised for this method.*
         :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
         :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
         :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

         .. note::
            Messages sent by Open Cloud with only be recieved by live servers. Studio won't recieve thesse messages.

   .. method:: upload_place(place_id, file, publish=False)

         Updates a place with the ``.rbxl`` file, optionaly publishing it and returns the place version number.
      
         :param int place_id: The place ID to update
         :param io.BytesIO file: The file to send. should be opened as bytes.
         :param publish bool: Wether to publish the place or just save it.
         :returns: :class:`int`
         :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to upload places.
         :raises rblx-open-cloud.NotFound: The place ID is invalid
         :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
         :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
         :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.