Data Store
=============================

.. currentmodule:: rblx-open-cloud

.. class:: DataStore

    Class for interacting with the DataStore API for a specific DataStore.

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`Universe.get_data_store` and :meth:`Universe.list_data_stores`.

    .. attribute:: name 

        :type: str

    .. attribute:: scope 

        :type: Union[str, None]
    
    .. attribute:: universe 

        :type: rblx-open-cloud.Universe
    
    .. attribute:: created 

        The data store's creation timestamp, could be ``None`` if not retrieved by :meth:`Universe.list_data_stores`.

        :type: Union[datetime.datetime, None]
   
    .. method:: list_keys(prefix="")

        Returns an Iterable of keys in the database and scope, optionally matching a prefix. Will return keys from all scopes if :attr:`scope` is ``None``.

        The example below would list all keys, along with their scope.
                
        .. code:: py

            for entry in datastore.list_keys():
                print(entry.key, entry.scope)
        
        You can simply convert it to a list by putting it in the list function:

        .. code:: py

            list(datastore.list_keys())

        Lua equivalent: `DataStore:ListKeysAsync() <https://create.roblox.com/docs/reference/engine/classes/DataStore#ListKeysAsync>`__

        :param str prefix: Only return keys that start with this prefix.
        
        :returns: Iterable[:class:`ListedEntry`]
        :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to list data store keys.
        :raises rblx-open-cloud.NotFound: The datastore does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

        
    .. method:: get(key)

        Gets the value of a key.

        Lua equivalent: `DataStore:GetAsync() <https://create.roblox.com/docs/reference/engine/classes/DataStore#GetAsync>`__

        :param str key: The key to find.
        
        :returns: tuple[Union[:class:`str`, :class:`dict`, :class:`list`, :class:`int`, :class:`float`], :class:`rblx-open-cloud.EntryInfo`]
        :raises ValueError: The :class:`DataStore` doesn't have a scope and the key must be formatted as ``scope/key``
        :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to get data store keys.
        :raises rblx-open-cloud.NotFound: The datastore or key does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.
    
    .. method:: set(key, value, users=None, metadata={})

        Sets the value of a key.

        Lua equivalent: `DataStore:SetAsync() <https://create.roblox.com/docs/reference/engine/classes/DataStore#SetAsync>`__

        :param str key: The key to change.
        :param Union[str, dict, list, int, float] value: The new value
        :param list[int] users: a list of Roblox user IDs to attach to the entry to assist with GDPR tracking/removal.
        :param dict metadata: a dictionary, just like the lua equivalent `DataStoreSetOptions:SetMetadata() <https://create.roblox.com/docs/reference/engine/classes/DataStoreSetOptions#SetMetadata>`__

        :returns: :class:`EntryVersion`
        :raises ValueError: The :class:`DataStore` doesn't have a scope and the key must be formatted as ``scope/key``
        :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to set data store keys.
        :raises rblx-open-cloud.NotFound: The datastore does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

        .. warning::

            If ``users`` and ``metadata`` are not included, they will be removed.
    
    .. method:: increment(key, increment, users=None, metadata={})

        Increments the value of a key.

        Lua equivalent: `DataStore:IncrementAsync() <https://create.roblox.com/docs/reference/engine/classes/DataStore#IncrementAsync>`__

        :param str key: The key to increment.
        :param Union[int, float] value: The number to increase the value by, use negative numbers to decrease it.
        :param list[int] users: a list of Roblox user IDs to attach to the entry to assist with GDPR tracking/removal.
        :param dict metadata: a dictionary of user-defind metadata, just like the lua equivalent `DataStoreSetOptions:SetMetadata() <https://create.roblox.com/docs/reference/engine/classes/DataStoreSetOptions#SetMetadata>`__

        :returns: tuple[Union[:class:`str`, :class:`dict`, :class:`list`, :class:`int`, :class:`float`], :class:`rblx-open-cloud.EntryInfo`]
        :raises ValueError: The :class:`DataStore` doesn't have a scope and the key must be formatted as ``scope/key``
        :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to increment data store keys.
        :raises rblx-open-cloud.NotFound: The datastore or key does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

        .. warning::

            If ``users`` and ``metadata`` are not included, they will be removed!
    
    .. method:: remove(key)

        Removes a key.

        Lua equivalent: `DataStore:RemoveAsync() <https://create.roblox.com/docs/reference/engine/classes/DataStore#RemoveAsync>`__

        :param str key: The key to remove.

        :returns: None
        :raises ValueError: The :class:`DataStore` doesn't have a scope and the key must be formatted as ``scope/key``
        :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to remove data store keys.
        :raises rblx-open-cloud.NotFound: The datastore or key does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.
    
    .. method:: list_versions(key, after, before, descending)

        Returns an Iterable of previous versions of a key.

        The example below would list all versions, along with their value.
                
        .. code:: py

            for version in datastore.list_versions("key-name"):
                print(version, version.get_value())
        
        You can simply convert it to a list by putting it in the list function:

        .. code:: py

            list(datastore.list_versions("key-name"))

        Lua equivalent: `DataStore:ListVersionsAsync() <https://create.roblox.com/docs/reference/engine/classes/DataStore#ListVersionsAsync>`__

        :param str key: The key to find versions for.
        :param datetime.datetime after: Only find versions after this datetime
        :param datetime.datetime before: Only find versions before this datetime
        :param bool descending: Wether the versions should be sorted by date ascending or descending.

        :returns: Iterable[:class:`EntryVersion`]
        :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to remove data store keys.
        :raises rblx-open-cloud.NotFound: The datastore or key does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.
    
    .. method:: get_version(key, version)

        Gets the value of a key version.

        Lua equivalent: `DataStore:GetVersionAsync() <https://create.roblox.com/docs/reference/engine/classes/DataStore#GetVersionAsync>`__

        :param str key: The key to find.
        :param str version: The version ID to get.
        
        :returns: tuple[Union[:class:`str`, :class:`dict`, :class:`list`, :class:`int`, :class:`float`], :class:`rblx-open-cloud.EntryInfo`]
        :raises ValueError: The :class:`DataStore` doesn't have a scope and the key must be formatted as ``scope/key``
        :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to get data store keys.
        :raises rblx-open-cloud.NotFound: The datastore or key does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

.. class:: EntryInfo

    Contains data about an entry such as version ID, timestamps, users and metadata.

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`DataStore.get`, :meth:`DataStore.increment`, and :meth:`DataStore.get_version`.

    .. attribute:: version 

        The version ID of the key.

        :type: str

    .. attribute:: created 

        The time this key was first set.

        :type: datetime.datetime
    
    .. attribute:: updated 

        The time this version was created.

        :type: datetime.datetime
    
    .. attribute:: metadata

        A dictionary of user-defind metadata, just like the lua equivalent `DataStoreSetOptions:GetMetadata() <https://create.roblox.com/docs/reference/engine/classes/DataStoreSetOptions#GetMetadata>`__

        :type: dict

.. class:: EntryVersion

    Contains data about a version such as it's ID, timestamps, content length and wether this version is deleted.

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`DataStore.set` and :meth:`DataStore.list_versions`.

    .. attribute:: version 

        The ID of this version.

        :type: str
    
    .. attribute:: deleted

        Wether this version was deleted by :meth:`DataStore.remove`.

        :type: bool
    
    .. attribute:: content_length

        The length of the value.

        :type: int

    .. attribute:: created 

        The time when this version was created.

        :type: datetime.datetime
    
    .. attribute:: key_created 

        The time when the key was created

        :type: datetime.datetime
    
    .. method:: get_value()

        Gets the value of this versions. Shortcut for :meth:`DataStore.get_version`
        
        :returns: tuple[Union[:class:`str`, :class:`dict`, :class:`list`, :class:`int`, :class:`float`], :class:`rblx-open-cloud.EntryInfo`]
        :raises rblx-open-cloud.InvalidToken: The token is invalid or doesn't have sufficent permissions to get data store keys.
        :raises rblx-open-cloud.NotFound: The datastore or key does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

.. class:: ListedEntry

    Object which contains a entry's key and scope.

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`DataStore.list_keys`.

    .. attribute:: key 

        The Entry's key

        :type: str
    
    .. attribute:: scope

        The Entry's scope

        :type: str