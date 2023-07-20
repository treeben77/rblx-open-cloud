Experience
=============================

.. currentmodule:: rblx-open-cloud

.. class:: Experience(id, api_key)

    Represents an experience/game object on Roblox. This class allows interaction with an experience's data stores, messaging service, and uploading place files.

    :param int id: The experience ID. See `this Roblox documentation <https://create.roblox.com/docs/cloud/open-cloud/data-store-api-handling#universe-id>`__ to get yours.
    :param str api_key: Your API key created from `Creator Dashboard <https://create.roblox.com/credentials>`__ with access to this experience.

.. attribute:: id 

    The experience's ID

    :type: int

.. method:: get_data_store(name, scope="global")

    Creates a :class:`rblx-open-cloud.DataStore` which allows interaction with a data store from the experience. :attr:`DataStore.created` will be ``None``.

    Lua equivalent: `DataStoreService:GetDataStore() <https://create.roblox.com/docs/reference/engine/classes/DataStoreService#GetDataStore>`__

    :param str name: The data store name
    :param Optional[str] scope: The data store scope. Defaults to ``global``, and can be ``None`` for key syntax like ``scope/key``.
    :returns: :class:`rblx-open-cloud.DataStore`

.. method:: get_ordered_data_store(name, scope="global")

    Creates a :class:`rblx-open-cloud.OrderedDataStore` with the provided name and scope.

    If ``scope`` is ``None`` then keys require to be formatted like ``scope/key`` and :meth:`OrderedDataStore.sort_keys` will not work.

    Lua equivalent: `DataStoreService:GetOrderedDataStore() <https://create.roblox.com/docs/reference/engine/classes/DataStoreService#GetOrderedDataStore>`__

    :param str name: The ordered data store name
    :param Optional[str] scope: The data store scope. Defaults to ``global``, and can be ``None`` for key syntax like ``scope/key``.
    :returns: :class:`rblx-open-cloud.OrderedDataStore`

.. method:: list_data_stores(prefix="", limit=None, scope="global")

    Interates :class:`rblx-open-cloud.DataStore` for all of the Data Stores in the experience.

    Lua equivalent: `DataStoreService:ListDataStoresAsync() <https://create.roblox.com/docs/reference/engine/classes/DataStoreService#ListDataStoresAsync>`__

    The example below would iterate through every datastore
      
    .. code:: python

      for datastore in experience.list_data_stores():
            print(datastore)

    You can get the data stores in a list like this:

    .. code:: python

        list(experience.list_data_stores())

    :param str prefix: Only return Data Stores with names starting with this value.
    :param Optional[int] limit: The maximum number of Data Stores to iterate.
    :param Optional[str] scope: The scope for all data stores. Defaults to global, and can be `None` for key syntax like `scope/key`.

    :returns: Iterable[:class:`rblx-open-cloud.DataStore`]
    :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to list data stores.
    :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
    :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
    :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

.. method:: publish_message(topic, data)

    Publishes a message to live game servers that can be recieved with `MessagingService <https://create.roblox.com/docs/reference/engine/classes/MessagingService>`__.

    The ``universe-messaging-service:publish`` scope is required if authorized via `OAuth2 </oauth2>`__.

    Lua equivalent: `MessagingService:PublishAsync() <https://create.roblox.com/docs/reference/engine/classes/MessagingService#PublishAsync>`__

    :param str topic: The topic to send the message in
    :param str data: The message to send. **Open Cloud does not support sending dictionaries/tables with publishing messages. You'll have to json encode it before sending it, and decode it in Roblox.**
    :returns: None
    :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to publish messages.
    :raises rblx-open-cloud.NotFound: *This shouldn't be raised for this method.*
    :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
    :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
    :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

    .. note::
        Messages sent by Open Cloud with only be recieved by live servers. Studio won't recieve thesse messages.

.. method:: upload_place(place_id, file, publish=False)

    Uploads the place file to Roblox and returns the new version number.

    .. code:: python

    with open("example.rbxl", "rb") as file:
        experience.upload_place(1234, file, publish=False)

    :param int place_id: The place ID to upload the file to.
    :param io.BytesIO file: The file to upload. The file should be opened in bytes.
    :param Optional[bool] publish: Wether to publish the place as well. Defaults to `False`.
    :returns: :class:`int`
    :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to upload places.
    :raises rblx-open-cloud.NotFound: The place ID is invalid
    :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
    :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
    :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.