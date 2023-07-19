Data Store
=============================

.. currentmodule:: rblx-open-cloud

.. class:: DataStore

    Class for interacting with the DataStore API for a specific DataStore.

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`Experience.get_data_store` and :meth:`Experience.list_data_stores`.

    .. attribute:: name 

        :type: str

    .. attribute:: scope 

        :type: Union[str, None]
    
    .. attribute:: experience 

        :type: rblx-open-cloud.Experience
    
    .. attribute:: created 

        The data store's creation timestamp, could be ``None`` if not retrieved by :meth:`Experience.list_data_stores`.

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
        :param Union[None, int] limit: Will not return more keys than this number. Set to ``None`` for no limit.
        
        :returns: Iterable[:class:`ListedEntry`]
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to list data store keys.
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
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to get data store keys.
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
        :param bool exclusive_create: whether to update the entry if it already has a value. Raises :class:`rblx-open-cloud.PreconditionFailed` if it has a value.
        :param Union[str, None] previous_version: don't update if the current version is not this value. Raises :class:`rblx-open-cloud.PreconditionFailed` if it has a value.

        :returns: :class:`EntryVersion`
        :raises ValueError: The :class:`DataStore` doesn't have a scope and the key must be formatted as ``scope/key`` or both ``exlcusive_create`` and ``previous_version`` were provided.
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to set data store keys.
        :raises rblx-open-cloud.NotFound: The datastore does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.
        :raises rblx-open-cloud.PreconditionFailed: ``exclusive_create`` is ``True`` and the key already has a value or the current version doesnt match ``previous_version``.

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
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to increment data store keys.
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
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to remove data store keys.
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
        :param Union[None, int] limit: Will not return more versions than this number. Set to ``None`` for no limit.
        :param bool descending: Wether the versions should be sorted by date ascending or descending.

        :returns: Iterable[:class:`EntryVersion`]
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to remove data store keys.
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
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to get data store keys.
        :raises rblx-open-cloud.NotFound: The datastore or key does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

.. class:: OrderedDataStore

    Class for interacting with the Ordered DataStore API for a specific Ordered DataStore.

    .. versionadded:: 1.2

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`Experince.get_ordered_data_store`.

    .. attribute:: name 

        :type: str

    .. attribute:: scope 

        :type: Optional[str]
    
    .. attribute:: experince 

        :type: :meth:`rblx-open-cloud.Experince`
    
    .. method:: sort_keys(descending=True, limit=None, min=None, max=None)

        Returns a list of keys and their values.

        The example below would list all keys, along with their value.
                
        .. code:: py

            for key in datastore.sort_keys():
                print(key.name, key.value)
        
        You can simply convert it to a list by putting it in the list function:

        .. code:: py

            list(datastore.sort_keys())

        Lua equivalent: `OrderedDataStore:GetSortedAsync() <https://create.roblox.com/docs/reference/engine/classes/OrderedDataStore#GetSortedAsync>`__

        :param bool descending: Wether the largest number should be first, or the smallest.
        :param bool limit: Max number of entries to loop through.
        :param int min: Minimum entry value to retrieve
        :param int max: Maximum entry value to retrieve.
        
        :returns: Iterable[:class:`SortedEntry`]
        :raises ValueError: The :class:`OrderedDataStore` doesn't have a scope.
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to list data store keys.
        :raises rblx-open-cloud.NotFound: The datastore or key does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

    .. note::

        Unlike :meth:`DataStore.list_keys`, this function is unable to work without a scope, this is an Open Cloud limitation. You can still use other functions with the normal ``scope/key`` syntax when scope is ``None``.

    .. method:: get(key)

        Gets the value of a key.

        Lua equivalent: `OrderedDataStore:GetAsync() <https://create.roblox.com/docs/reference/engine/classes/OrderedDataStore#GetAsync>`__

        :param str key: The key to find.
        
        :returns: int
        :raises ValueError: The :class:`OrderedDataStore` doesn't have a scope and the key must be formatted as ``scope/key``
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to read data store keys.
        :raises rblx-open-cloud.NotFound: The datastore or key does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.
    
    .. method:: set(key, value, exclusive_create=False, exclusive_update=False)

        Sets the value of a key.

        Lua equivalent: `OrderedDataStore:SetAsync() <https://create.roblox.com/docs/reference/engine/classes/OrderedDataStore#SetAsync>`__

        :param str key: The key to create/update.
        :param int value: The new integer value. Must be positive.
        :param bool exclusive_create: Wether to fail if the key already has a value.
        :param bool exclusive_update: Wether to fail if the key does not have a value.
        
        :returns: int
        :raises ValueError: The :class:`OrderedDataStore` doesn't have a scope and the key must be formatted as ``scope/key`` or both ``exclusive_create`` and ``exclusive_update`` are ``True``.
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to write data store keys.
        :raises rblx-open-cloud.NotFound: The datastore or key does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.
        :raises rblx-open-cloud.PreconditionFailed: ``exclusive_create`` is ``True`` and the key already has a value, or ``exclusive_update`` is ``True`` and there is no pre-existing value.
    
    .. method:: increment(key, increment)

        Increments the value of a key.

        Lua equivalent: `OrderedDataStore:IncrementAsync() <https://create.roblox.com/docs/reference/engine/classes/OrderedDataStore#IncrementAsync>`__

        :param str key: The key to increment.
        :param int increment: The amount to increment the key by. You can use negative numbers to decrease the value.
        
        :returns: int
        :raises ValueError: The :class:`OrderedDataStore` doesn't have a scope and the key must be formatted as ``scope/key``
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to write data store keys.
        :raises rblx-open-cloud.NotFound: The datastore or key does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

    .. method:: remove(key)

        Removes a key.

        Lua equivalent: `OrderedDataStore:RemoveAsync() <https://create.roblox.com/docs/reference/engine/classes/OrderedDataStore#RemoveAsync>`__

        :param str key: The key to remove.

        :raises ValueError: The :class:`OrderedDataStore` doesn't have a scope and the key must be formatted as ``scope/key``
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to write data store keys.
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

        Gets the value of this version. Shortcut for :meth:`DataStore.get_version`
        
        :returns: tuple[Union[:class:`str`, :class:`dict`, :class:`list`, :class:`int`, :class:`float`], :class:`rblx-open-cloud.EntryInfo`]
        :raises rblx-open-cloud.InvalidKey: The token is invalid or doesn't have sufficent permissions to get data store keys.
        :raises rblx-open-cloud.NotFound: The datastore or key does not exist
        :raises rblx-open-cloud.RateLimited: You're being rate limited by Roblox. Try again in a minute.
        :raises rblx-open-cloud.ServiceUnavailable: Roblox's services as currently experiencing downtime.
        :raises rblx-open-cloud.rblx_opencloudException: Roblox's response was unexpected.

.. class:: ListedEntry

    Object which contains an entry's key and scope.

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`DataStore.list_keys`.

    .. attribute:: key 

        The Entry's key

        :type: str
    
    .. attribute:: scope

        The Entry's scope

        :type: str

.. class:: SortedEntry

    Object which contains a sorted entry's key, scope, and value.

    .. versionadded:: 1.2

    .. warning::

        This class is not designed to be created by users. It is returned by :meth:`OrderedDataStore.sort_keys`.

    .. attribute:: key 

        The Entry's key

        :type: str
    
    .. attribute:: scope

        The Entry's scope

        :type: str

    .. attribute:: value

        The Entry's value

        :type: int