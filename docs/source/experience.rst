Experience
=============================

.. currentmodule:: rblx-open-cloud

.. class:: Experience(id, api_key)

   Class for interacting with the API for a specific experience.

   :param int id: A Experience ID. Read How to find yours here: `Publishing Places with API Keys <https://create.roblox.com/docs/open-cloud/publishing-places-with-api-keys>`__
   :param str api_key: An API key created from `Creator Dashboard <https://create.roblox.com/credentials>`__. *this should be kept safe, as anyone with the key can use it!*

   .. attribute:: id 

      The Experience's ID

      :type: int
   
   .. method:: get_data_store(name, scope="global")

         Creates a :class:`rblx-open-cloud.DataStore` without :attr:`DataStore.created` with the provided name and scope.

         If ``scope`` is ``None`` then keys require to be formatted like ``scope/key`` and :meth:`DataStore.list_keys` will return keys from all scopes.

         Lua equivalent: `DataStoreService:GetDataStore() <https://create.roblox.com/docs/reference/engine/classes/DataStoreService#GetDataStore>`__

         :param str name: The name of the data store
         :param Union[str, None] scope: A string specifying the scope, can also be None.
         :returns: :class:`rblx-open-cloud.DataStore`

         .. note::
            Ordered DataStores are still in alpha, to use them you must `sign up for the beta <https://devforum.roblox.com/t/opencloud-ordered-datastores/2062532>`__ and then `install the beta library <https://github.com/TreeBen77/rblx-open-cloud/tree/orderedapi>__`
   
   .. method:: list_data_stores(prefix="", scope="global")

         Returns an Iterable of all :class:`rblx-open-cloud.DataStore` in the Experience which includes :attr:`rblx-open-cloud.DataStore.created`, optionally matching a prefix.

         Lua equivalent: `DataStoreService:ListDataStoresAsync() <https://create.roblox.com/docs/reference/engine/classes/DataStoreService#ListDataStoresAsync>`__

         The example below would iterate through every datastore
                
         .. code:: py

            for datastore in experience.list_data_stores():
                print(datastore.name)
        
         You can simply convert it to a list by putting it in the list function:

         .. code:: py

            list(experience.list_data_stores())
         
         :param str prefix: Only Iterates datastores with that start with this string
         :param Union[None, int] limit: Will not return more datastores than this number. Set to ``None`` for no limit.
         :param Union[str, None] scope: The scope the :class:`rblx-open-cloud.DataStore` will have.

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
         :param bool publish: Wether to publish the place or just save it.
         :returns: :class:`int`
         :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to upload places.
         :raises rblx-open-cloud.NotFound: The place ID is invalid
         :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
         :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
         :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.