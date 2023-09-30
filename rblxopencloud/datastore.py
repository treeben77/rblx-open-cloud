from .exceptions import rblx_opencloudException, InvalidKey, NotFound, RateLimited, ServiceUnavailable, PreconditionFailed
import json, datetime
import base64, hashlib, urllib.parse
from typing import Union, Optional, Iterable, TYPE_CHECKING
from . import user_agent, request_session

if TYPE_CHECKING:
    from .experience import Experience

if TYPE_CHECKING:
    from .experience import Experience

__all__ = (
    "EntryInfo",
    "EntryVersion",
    "ListedEntry",
    "DataStore",
    "SortedEntry",
    "OrderedDataStore"
)

class EntryInfo():
    """
    Represents a Data Store entry, and contains metadata about the entry.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`DataStore.get()`][rblxopencloud.DataStore.get], [`DataStore.increment()`][rblxopencloud.DataStore.increment], and [`DataStore.get_version()`][rblxopencloud.DataStore.get_version].

    Attributes:
        version (str): The version ID of this entry.
        created (datetime.datetime): The timestamp the entry was created.
        updated (datetime.datetime): The timestamp the entry was last modified.
        users (list[int]): A list of user IDs associated with the entry.
        metadata (dict): The dictionary of custom metadata.
    """
    def __init__(self, version, created, updated, users, metadata) -> None:
        self.version: str = version
        self.created: datetime.date = datetime.datetime.fromisoformat((created.split("Z")[0]+"0"*6)[0:26])
        self.updated: datetime.date = datetime.datetime.fromisoformat((updated.split("Z")[0]+"0"*6)[0:26])
        self.users: list[int] = users
        self.metadata: dict = metadata
    
    def __repr__(self) -> str:
        return f"rblxopencloud.EntryInfo(\"{self.version}\", users={self.users}, metadata={self.metadata})"

class EntryVersion():
    """
    Represents a Data Store entry version, and contains data about the version.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`DataStore.set()`][rblxopencloud.DataStore.set], and [`DataStore.list_versions()`][rblxopencloud.DataStore.list_versions].

    Attributes:
        version (str): The version ID of this entry.
        deleted (bool): Wether this version has been marked as deleted.
        content_length (int): The number of characters the value is.
        created (datetime.datetime): The timestamp the version was created.
        key_created (datetime.datetime): The timestamp the entry was first created.
    """
    def __init__(self, version, deleted, content_length, created, key_created, datastore, key, scope) -> None:
        self.version: str = version
        self.deleted: bool = deleted
        self.content_length: int = content_length
        self.created: datetime.datetime = datetime.datetime.fromisoformat((created.split("Z")[0]+"0"*6)[0:26])
        self.key_created: datetime.datetime = datetime.datetime.fromisoformat((key_created.split("Z")[0]+"0"*6)[0:26])
        self.__datastore = datastore
        self.__key = key
        self.__scope = scope
    
    def __eq__(self, object) -> bool:
        if not isinstance(object, EntryVersion):
            return NotImplemented
        return self.__key == object.__key and self.__scope == object.__scope and self.version == object.version
    
    def get_value(self) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        """
        Gets the value of the current version. This is a shortcut for [`DataStore.get_version()`][rblxopencloud.DataStore.get_version]

        Returns:
            A tuple with the key's value in the first index, and the key's metadata as an EntryInfo in the second index.
        """
        if self.__datastore.scope:
            return self.__datastore.get_version(self.__key, self.version)
        else:
            return self.__datastore.get_version(f"{self.__scope}/{self.__key}", self.version)

    def __repr__(self) -> str:
        return f"rblxopencloud.EntryVersion(\"{self.version}\", content_length={self.content_length})"

class ListedEntry():
    """
    Represents a Data Store entry iterated by [`DataStore.list_keys()`][rblxopencloud.DataStore.list_keys].

    !!! warning
        This class isn't designed to be created by users. It is returned by [`DataStore.list_keys()`][rblxopencloud.DataStore.list_keys].

    Attributes:
        key (str): The entry's key.
        scope (str): The entry's scope.
    """
    def __init__(self, key, scope) -> None:
        self.key: str = key
        self.scope: str = scope
    
    def __eq__(self, object) -> bool:
        if not isinstance(object, ListedEntry):
            return NotImplemented
        return self.key == object.key and self.scope == object.scope
    
    def __repr__(self) -> str:
        return f"rblxopencloud.ListedEntry(\"{self.key}\", scope=\"{self.scope}\")"

class DataStore():
    """
    Represents a regular data store in an experience.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`Experience.get_data_store()`][rblxopencloud.Experience.get_data_store] and [`Experience.list_data_stores()`][rblxopencloud.Experience.list_data_stores].

    Attributes:
        name (str): The data store's name.
        scope (Optional[str]): The data store's scope. If it is `None`, then it uses the `scope/key` syntax.
        experience (Experience): The experience the data store belongs to.
        created (Optional[datetime.datetime]): The time the datetime was created. Only present if returned by `Experience.list_data_stores()`.
    """

    def __init__(self, name, experience, api_key, created, scope):
        self.name: str = name
        self.__api_key: str = api_key
        self.scope: str = scope
        self.experience: Experience = experience
        if created: self.created = datetime.datetime.fromisoformat((created.split("Z")[0]+"0"*6)[0:26])
        else: self.created = None
    
    def __repr__(self) -> str:
        return f"rblxopencloud.DataStore(\"{self.name}\", scope=\"{self.scope}\", universe={repr(self.experience)})"
    
    def __str__(self) -> str:
        return self.name

    def list_keys(self, prefix: str="", limit: Optional[int]=None) -> Iterable[ListedEntry]:
        """
        Returns an Iterable of keys in the database and scope, optionally matching a prefix. Will return keys from all scopes if the `scope` attribute is `None`.

        Example:
            This will print every key in the data store. 
            ```py
            for key in datastore.list_keys():
                print(key.key, key.scope)
            ```
            If you'd like the keys in a list, you can use the list method:
            ```py
            list(datastore.list_keys())
            ```

        Args:
            prefix: Only return keys that start with this prefix.
            limit: Will not return more keys than this number. Set to `None` for no limit.
        
        Returns:
            An Iterable of all keys in the data store.
        
        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to list data store keys, or is from an invalid IP address.
            NotFound: The experience or data store does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        """
        nextcursor = ""
        yields = 0
        while limit == None or yields < limit:
            response = request_session.get(f"https://apis.roblox.com/datastores/v1/universes/{self.experience.id}/standard-datastores/datastore/entries",
                headers={"x-api-key": self.__api_key, "user-agent": user_agent}, params={
                "datastoreName": self.name,
                "scope": self.scope,
                "AllScopes": not self.scope,
                "prefix": prefix,
                "cursor": nextcursor if nextcursor else None
            })
            if response.status_code == 400: raise rblx_opencloudException(response.json()["message"])
            elif response.status_code == 401: raise InvalidKey(response.text)
            elif response.status_code == 403: raise InvalidKey(response.json()["message"])
            elif response.status_code == 404: raise NotFound(response.json()["message"])
            elif response.status_code == 429: raise RateLimited(response.json()["message"])
            elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")
            
            data = response.json()
            for key in data["keys"]:
                yields += 1
                yield ListedEntry(key["key"], key["scope"])
                if limit != None and yields >= limit: break
            nextcursor = data.get("nextPageCursor")
            if not nextcursor: break
    
    def get(self, key: str) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        """
        Fetches the value of a key.

        Args:
            key: The key to find. If `scope` is `None`, then the key should use the `scope/key` syntax.
        
        Returns:
            A tuple with the key's value in the first index, and the key's metadata as an [`rblxopencloud.EntryInfo()`][rblxopencloud.EntryInfo] in the second index.
        
        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to get data store keys, or is from an invalid IP address.
            NotFound: The experience, data store, or entry does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        """
        try:
            scope = self.scope
            if not scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("a scope and key seperated by a forward slash is required for DataStore without a scope.")
        response = request_session.get(f"https://apis.roblox.com/datastores/v1/universes/{self.experience.id}/standard-datastores/datastore/entries/entry",
            headers={"x-api-key": self.__api_key, "user-agent": user_agent}, params={
                "datastoreName": self.name,
                "scope": scope,
                "entryKey": key
            })

        if response.status_code == 200:
            try: metadata = json.loads(response.headers["roblox-entry-attributes"])
            except(KeyError): metadata = {}
            try: userids = json.loads(response.headers["roblox-entry-userids"])
            except(KeyError): userids = []
            
            return json.loads(response.text), EntryInfo(response.headers["roblox-entry-version"], response.headers["roblox-entry-created-time"],
    response.headers["roblox-entry-version-created-time"], userids, metadata)
        elif response.status_code == 400: raise rblx_opencloudException(response.json()["message"])
        elif response.status_code == 401: raise InvalidKey(response.text)
        elif response.status_code == 403: raise InvalidKey(response.json()["message"])
        elif response.status_code == 404: raise NotFound(response.json()["message"])
        elif response.status_code == 429: raise RateLimited(response.json()["message"])
        elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")

    def set(self, key: str, value: Union[str, dict, list, int, float], users:Optional[list[int]]=None, metadata:dict={}, exclusive_create:bool=False, previous_version:Optional[str]=None) -> EntryVersion:
        """
        Sets the value of a key with the new data.

        Args:
            key: The key to set. If `scope` is `None`, then the key should use the `scope/key` syntax.
            value: The key's new value.
            users: a list of Roblox user IDs to attach to the entry to assist with GDPR tracking/removal.
            metadata: A dictionary of custom metadata for the entry.
            exclusive_create: whether to update the entry if it already has a value. Raises `rblx-open-cloud.PreconditionFailed` if it has a value.
            previous_version: don't update if the current version is not this value. Raises `rblx-open-cloud.PreconditionFailed` if it has a value.
        
        Returns:
            An [`rblxopencloud.EntryInfo()`][rblxopencloud.EntryInfo] object with information about the datastore entry.
        
        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to create/update data store keys, or is from an invalid IP address.
            NotFound: The experience, data store, or entry does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
            ValueError: `previous_version` and `exclusive_create` are both set, or the `scope/key` syntax wasn't used and `scope` is `None`.
            PreconditionFailed: A precondition such as `previous_version` or `exclusive_create` failed.
        
        !!! warning
            If `users` and `metadata` parameters are not included, they will be removed from the entry.
        """
        if previous_version and exclusive_create: raise ValueError("previous_version and exclusive_create can not both be set")
        try:
            scope = self.scope
            if not scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("a scope and key seperated by a forward slash is required for DataStore without a scope.")
        if users == None: users = []
        data = json.dumps(value)

        response = request_session.post(f"https://apis.roblox.com/datastores/v1/universes/{self.experience.id}/standard-datastores/datastore/entries/entry",
            headers={"x-api-key": self.__api_key, "user-agent": user_agent, "roblox-entry-userids": json.dumps(users), "roblox-entry-attributes": json.dumps(metadata),
            "content-md5": base64.b64encode(hashlib.md5(data.encode()).digest())}, data=data, params={
                "datastoreName": self.name,
                "scope": scope,
                "entryKey": key,
                "exclusiveCreate": exclusive_create,
                "matchVersion": previous_version
            })
        
        if response.status_code == 200:
            data = json.loads(response.text)
            return EntryVersion(data["version"], data["deleted"], data["contentLength"], data["createdTime"], data["objectCreatedTime"], self, key, self.scope if self.scope else scope)
        elif response.status_code == 400: raise rblx_opencloudException(response.json()["message"])
        elif response.status_code == 401: raise InvalidKey(response.text)
        elif response.status_code == 403: raise InvalidKey(response.json()["message"])
        elif response.status_code == 404: raise NotFound(response.json()["message"])
        elif response.status_code == 429: raise RateLimited(response.json()["message"])
        elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
        elif response.status_code == 412:
            try: metadata = json.loads(response.headers["roblox-entry-attributes"])
            except(KeyError): metadata = {}
            try: userids = json.loads(response.headers["roblox-entry-userids"])
            except(KeyError): userids = []

            if exclusive_create:
                error = "An entry already exists with the provided key and scope"
            elif previous_version:
                error = f"The current version is not '{previous_version}'"
            else:
                error = "A Precondition Failed"

            raise PreconditionFailed(json.loads(response.text), EntryInfo(response.headers["roblox-entry-version"], response.headers["roblox-entry-created-time"],
    response.headers["roblox-entry-version-created-time"], userids, metadata), error)
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")

    def increment(self, key: str, increment: Union[int, float], users:Optional[list[int]]=None, metadata:dict={}) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        """
        Increments the value of a key with the provided number. Numbers may be negative to decrement the value.

        Args:
            key: The key to increment. If `scope` is `None`, then the key should use the `scope/key` syntax.
            increment: The amount to increment the value. This number can be negative to decrement the value.
            users: a list of Roblox user IDs to attach to the entry to assist with GDPR tracking/removal.
            metadata: A dictionary of custom metadata for the entry.
        
        Returns:
            A tuple with the key's value in the first index, and the key's metadata as an [`rblxopencloud.EntryInfo()`][rblxopencloud.EntryInfo] in the second index. The same as [`DataStore.get()`][rblxopencloud.DataStore.get].
        
        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to increment data store keys, or is from an invalid IP address.
            NotFound: The experience, data store, or entry does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
            ValueError: The `scope/key` syntax wasn't used and `scope` is `None`.
        
        !!! warning
            If `users` and `metadata` parameters are not included, they will be removed from the entry.
        """

        try:
            scope = self.scope
            if not scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("a scope and key seperated by a forward slash is required for DataStore without a scope.")
        if users == None: users = []

        response = request_session.post(f"https://apis.roblox.com/datastores/v1/universes/{self.experience.id}/standard-datastores/datastore/entries/entry/increment",
            headers={"x-api-key": self.__api_key, "user-agent": user_agent, "roblox-entry-userids": json.dumps(users), "roblox-entry-attributes": json.dumps(metadata)}, params={
                "datastoreName": self.name,
                "scope": scope,
                "entryKey": key,
                "incrementBy": increment
            })

        if response.status_code == 200:
            try: metadata = json.loads(response.headers["roblox-entry-attributes"])
            except(KeyError): metadata = {}
            try: userids = json.loads(response.headers["roblox-entry-userids"])
            except(KeyError): userids = []
            
            return json.loads(response.text), EntryInfo(response.headers["roblox-entry-version"], response.headers["roblox-entry-created-time"],
    response.headers["roblox-entry-version-created-time"], userids, metadata)
        elif response.status_code == 400: raise rblx_opencloudException(response.json()["message"])
        elif response.status_code == 401: raise InvalidKey(response.text)
        elif response.status_code == 403: raise InvalidKey(response.json()["message"])
        elif response.status_code == 404: raise NotFound(response.json()["message"])
        elif response.status_code == 429: raise RateLimited(response.json()["message"])
        elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")
    
    def remove(self, key: str) -> None:
        """
        Removes the key. The key isn't permanently deleted for 30 days after it is removed.

        Args:
            key: The key to remove. If `scope` is `None`, then the key should use the `scope/key` syntax.
        
        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to remove data store keys, or is from an invalid IP address.
            NotFound: The experience, data store, or entry does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
            ValueError: The `scope/key` syntax wasn't used and `scope` is `None`.
        """
        try:
            scope = self.scope
            if not scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("a scope and key seperated by a forward slash is required for DataStore without a scope.")
        response = request_session.delete(f"https://apis.roblox.com/datastores/v1/universes/{self.experience.id}/standard-datastores/datastore/entries/entry",
            headers={"x-api-key": self.__api_key, "user-agent": user_agent}, params={
                "datastoreName": self.name,
                "scope": scope,
                "entryKey": key
            })

        if response.status_code == 204: return None
        elif response.status_code == 400: raise rblx_opencloudException(response.json()["message"])
        elif response.status_code == 401: raise InvalidKey(response.text)
        elif response.status_code == 403: raise InvalidKey(response.json()["message"])
        elif response.status_code == 404: raise NotFound(response.json()["message"])
        elif response.status_code == 429: raise RateLimited(response.json()["message"])
        elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")
    
    def list_versions(self, key: str, after: Optional[datetime.datetime]=None, before: Optional[datetime.datetime]=None, limit: Optional[int]=None, descending: bool=True) -> Iterable[EntryVersion]:
        """
        Returns an Iterable of versions avaliable for the key. Optionally within a ceartin time period.

        Example:
            This will print every version avaliable for the key, and fetch their values. 
            ```py
            for version in datastore.list_versions("key-name"):
                print(version, version.get_value())
            ```
            If you'd like the versions in a list, you can use the list method:
            ```py
            list(datastore.list_versions("key-name"))
            ```

        Args:
            key: The key to find versions for. If `scope` is `None`, then the key should use the `scope/key` syntax.
            after: Only find versions after this datetime
            before: Only find versions before this datetime
            limit: Will not return more versions than this number. Set to `None` for no limit.
            descending: Wether the versions should be sorted by date ascending or descending.
        
        Returns:
            An Iterable of all versions of the key.
        
        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to list data store keys, or is from an invalid IP address.
            NotFound: The experience, data store, or key does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
            ValueError: The `scope/key` syntax wasn't used and `scope` is `None`.
        """
        try:
            scope = self.scope
            if not scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("a scope and key seperated by a forward slash is required for DataStore without a scope.")
        nextcursor = ""
        yields = 0
        while limit == None or yields < limit:
            response = request_session.get(f"https://apis.roblox.com/datastores/v1/universes/{self.experience.id}/standard-datastores/datastore/entries/entry/versions",
                headers={"x-api-key": self.__api_key, "user-agent": user_agent}, params={
                    "datastoreName": self.name,
                    "scope": scope,
                    "entryKey": key,
                    "sortOrder": "Descending" if descending else "Ascending",
                    "cursor": nextcursor if nextcursor else None,
                    "startTime": after.isoformat() if after else None,
                    "endTime": before.isoformat() if before else None
                })
            
            if response.status_code == 400: raise rblx_opencloudException(response.json()["message"])
            elif response.status_code == 401: raise InvalidKey(response.text)
            elif response.status_code == 403: raise InvalidKey(response.json()["message"])
            elif response.status_code == 404: raise NotFound(response.json()["message"])
            elif response.status_code == 429: raise RateLimited(response.json()["message"])
            elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")

            data = response.json()
            for version in data["versions"]:
                yields += 1
                yield EntryVersion(version["version"], version["deleted"], version["contentLength"], version["createdTime"], version["objectCreatedTime"], self, key, self.scope if self.scope else scope)
                if limit == None or yields >= limit: break
            nextcursor = data.get("nextPageCursor")
            if not nextcursor: break

    def get_version(self, key: str, version: str) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        """
        Gets the value of a key at a specific version.

        Args:
            key: The key to find. If `scope` is `None`, then the key should use the `scope/key` syntax.
            version: The ID of the version to find.
        
        Returns:
            A tuple with the key's value in the first index, and the key's metadata as an [`rblxopencloud.EntryInfo`][rblxopencloud.EntryInfo] in the second index. The same as [`DataStore.get()`][rblxopencloud.DataStore.get].
        
        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to get data store keys, or is from an invalid IP address.
            NotFound: The experience, data store, entry, or version does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.

        !!! Tip
            Since [`DataStore.list_versions()`][rblxopencloud.DataStore.list_versions], and [`DataStore.set()`][rblxopencloud.DataStore.set] return [`rblxopencloud.EntryVersion()`][rblxopencloud.EntryVersion], you can use the [`EntryVersion.get_value()`][rblxopencloud.EntryVersion.get_value] method as a shortcut when using those methods.
        """
        try:
            scope = self.scope
            if not scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("a scope and key seperated by a forward slash is required for DataStore without a scope.") 
        response = request_session.get(f"https://apis.roblox.com/datastores/v1/universes/{self.experience.id}/standard-datastores/datastore/entries/entry/versions/version",
            headers={"x-api-key": self.__api_key, "user-agent": user_agent}, params={
                "datastoreName": self.name,
                "scope": scope,
                "entryKey": key,
                "versionId": version
            })

        if response.status_code == 200:
            try: metadata = json.loads(response.headers["roblox-entry-attributes"])
            except(KeyError): metadata = {}
            try: userids = json.loads(response.headers["roblox-entry-userids"])
            except(KeyError): userids = []
            
            return json.loads(response.text), EntryInfo(response.headers["roblox-entry-version"], response.headers["roblox-entry-created-time"],
                response.headers["roblox-entry-version-created-time"], userids, metadata)
        elif response.status_code == 400:
            if response.json()["message"] == "Invalid version id.":
                raise NotFound(response.json()["message"])
            else:
                raise rblx_opencloudException(response.json()["message"])
        elif response.status_code == 401: raise InvalidKey(response.text)
        elif response.status_code == 403: raise InvalidKey(response.json()["message"])
        elif response.status_code == 404: raise NotFound(response.json()["message"])
        elif response.status_code == 429: raise RateLimited(response.json()["message"])
        elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")

class SortedEntry():
    """
    Represents an Ordered Data Store entry when listed with `OrderedDataStore.sort_keys()`.

    !!! warning
        This class isn't designed to be created by users. It is returned by `OrderedDataStore.sort_keys()`.

    Attributes:
        key (str): The entry's key.
        scope (str): The entry's scope.
        value (int): The value of the entry.
    """
    def __init__(self, key: str, value: int, scope: str="global") -> None:
        self.key: str = key
        self.scope: str = scope
        self.value: int = value
    
    def __eq__(self, object) -> bool:
        if not isinstance(object, SortedEntry):
            return NotImplemented
        return self.key == object.key and self.scope == object.scope and self.value == object.value
    
    def __repr__(self) -> str:
        return f"rblxopencloud.SortedEntry(\"{self.key}\", value={self.value})"

class OrderedDataStore():
    """
    Represents an ordered data store in an experience.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`Experience.get_ordered_data_store()`][rblxopencloud.Experience.get_ordered_data_store].

    Attributes:
        name (str): The data store's name.
        scope (Optional[str]): The data store's scope. If it is `None`, then it uses the `scope/key` syntax.
        experience (Experience): The experience the data store belongs to.
    """

    def __init__(self, name, experince, api_key, scope):
        self.name = name
        self.__api_key = api_key
        self.scope = scope
        self.experince = experince
    
    def __repr__(self) -> str:
        return f"rblxopencloud.OrderedDataStore(\"{self.name}\", scope=\"{self.scope}\", experince={repr(self.experince)})"
    
    def __str__(self) -> str:
        return self.name
    
    def sort_keys(self, descending: bool=True, limit: Optional[int]=None, min: int=None, max: int=None) -> Iterable[SortedEntry]:
        """
        Returns an Iterable of keys in order based on their value.

        Example:
            This will print every key in the datastore. 
            ```py
            for key in datastore.sort_keys():
                print(key.name, key.value)
            ```
            If you'd like the keys in a list, you can use the list method:
            ```py
            list(datastore.sort_keys())
            ```

        Args:
            descending: Wether the largest number should be first, or the smallest.
            limit: Will not return more keys than this number. Set to `None` for no limit.
            min: Minimum entry value to retrieve
            max: Maximum entry value to retrieve.
        
        Returns:
            An Iterable of all keys in the data store.
        
        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to list ordered data store keys, or is from an invalid IP address.
            NotFound: The experience, data store, or key does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
            ValueError: The `scope/key` syntax wasn't used and `scope` is `None`.
        """
        if not self.scope: raise ValueError("A scope is required to list keys on OrderedDataStore.")

        filter = None
        if min and max:
            if min > max: raise ValueError("min must not be greater than max.")
            filter = f"entry >= {min} && entry <= {max}"

        if min: filter = f"entry >= {min}"
        if max: filter = f"entry <= {max}"

        nextcursor = ""
        yields = 0
        while limit == None or yields < limit:
            response = request_session.get(f"https://apis.roblox.com/ordered-data-stores/v1/universes/{self.experince.id}/orderedDataStores/{urllib.parse.quote(self.name)}/scopes/{urllib.parse.quote(self.scope)}/entries",
                headers={"x-api-key": self.__api_key, "user-agent": user_agent}, params={
                "max_page_size": limit if limit and limit < 100 else 100,
                "order_by": "desc" if descending else None,
                "page_token": nextcursor if nextcursor else None,
                "filter": filter
            })

            if response.status_code == 400: raise rblx_opencloudException(response.json()["message"])
            elif response.status_code == 401: raise InvalidKey(response.text)
            elif response.status_code == 403: raise InvalidKey(response.json()["message"])
            elif response.status_code == 404: raise NotFound(response.json()["message"])
            elif response.status_code == 429: raise RateLimited(response.json()["message"])
            elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")
            
            data = response.json()
            for key in data["entries"]:
                yields += 1
                yield SortedEntry(key["id"], key["value"], self.scope)
                if limit != None and yields >= limit: break
            nextcursor = data.get("nextPageToken")
            if not nextcursor: break
    
    def get(self, key: str) -> int:
        """
        Gets the value of the key.

        Args:
            key: The key to get. If `scope` is `None`, then the key should use the `scope/key` syntax.
        
        Returns:
            The integer value of the key.

        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to get ordered data store keys, or is from an invalid IP address.
            NotFound: The experience, data store, or entry does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
            ValueError: The `scope/key` syntax wasn't used and `scope` is `None`.
        """
        try:
            if not self.scope: scope, key = key.split("/", maxsplit=1)
            else: scope = self.scope
        except(ValueError): raise ValueError("a scope and key seperated by a forward slash is required for OrderedDataStore without a scope.")

        response = request_session.get(f"https://apis.roblox.com/ordered-data-stores/v1/universes/{self.experince.id}/orderedDataStores/{urllib.parse.quote(self.name)}/scopes/{urllib.parse.quote(scope)}/entries/{urllib.parse.quote(key)}",
            headers={"x-api-key": self.__api_key, "user-agent": user_agent})
        
        if response.status_code == 200: return int(response.json()["value"])
        elif response.status_code == 400: raise rblx_opencloudException(response.json()["message"])
        elif response.status_code == 401: raise InvalidKey(response.text)
        elif response.status_code == 403: raise InvalidKey(response.json()["message"])
        elif response.status_code == 404: raise NotFound(response.json()["message"])
        elif response.status_code == 429: raise RateLimited(response.json()["message"])
        elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")
        
    def set(self, key: str, value: int, exclusive_create: bool=False, exclusive_update: bool=False) -> int:
        """
        Sets the value of the key, and then returns the new value.

        Args:
            key: The key to get. If `scope` is `None`, then the key should use the `scope/key` syntax.
            value: The new integer value. Must be positive.
            exclusive_create: Wether to fail if the key already has a value.
            exclusive_update: Wether to fail if the key does not have a value.
        
        Returns:
            The integer value of the key.

        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to create/update ordered data store keys, or is from an invalid IP address.
            NotFound: The experience, data store, or entry does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
            PreconditionFailed: A precondition such as `exclusive_create` or `exclusive_update` failed.
            ValueError: The `scope/key` syntax wasn't used and `scope` is `None`, or both `exclusive_create` and `exclusive_update` are `True`.
        """
        try:
            if not self.scope: scope, key = key.split("/", maxsplit=1)
            else: scope = self.scope
        except(ValueError): raise ValueError("a scope and key seperated by a forward slash is required for OrderedDataStore without a scope.")
        if exclusive_create and exclusive_update: raise ValueError("exclusive_create and exclusive_updated can not both be True")

        if not exclusive_create:
            response = request_session.patch(f"https://apis.roblox.com/ordered-data-stores/v1/universes/{self.experince.id}/orderedDatastores/{urllib.parse.quote(self.name)}/scopes/{urllib.parse.quote(scope)}/entries/{urllib.parse.quote(key)}",
                headers={"x-api-key": self.__api_key, "user-agent": user_agent}, params={"allow_missing": not exclusive_update}, json={
                    "value": value
                })
        else:
            response = request_session.post(f"https://apis.roblox.com/ordered-data-stores/v1/universes/{self.experince.id}/orderedDatastores/{urllib.parse.quote(self.name)}/scopes/{urllib.parse.quote(scope)}/entries",
                headers={"x-api-key": self.__api_key, "user-agent": user_agent}, params={"id": key}, json={
                    "value": value
                })
        
        if response.status_code == 200: return int(response.json()["value"])
        elif response.status_code == 400:
            if response.json()["message"] == "Entry already exists.":
                raise PreconditionFailed(None, None, response.json()["message"])
            else:
                raise rblx_opencloudException(response.json()["message"])
        elif response.status_code == 401: raise InvalidKey(response.text)
        elif response.status_code == 403: raise InvalidKey(response.json()["message"])
        elif response.status_code == 404 and exclusive_update and response.json()["code"] == "NOT_FOUND": raise PreconditionFailed(response.json()["message"])
        elif response.status_code == 429: raise RateLimited(response.json()["message"])
        elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")

    def increment(self, key: str, increment: int) -> int:
        """
        Increments the value of the key, and then returns the new value.

        Args:
            key: The key to get. If `scope` is `None`, then the key should use the `scope/key` syntax.
            increment: The amount to increment the value. You can use negative numbers to decrease the value.

        Returns:
            The integer value of the key.

        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to increment ordered data store keys, or is from an invalid IP address.
            NotFound: The experience, data store, or entry does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
            ValueError: The `scope/key` syntax wasn't used and `scope` is `None`, or both `exclusive_create` and `exclusive_update` are `True`.
        """
        try:
            if not self.scope: scope, key = key.split("/", maxsplit=1)
            else: scope = self.scope
        except(ValueError): raise ValueError("a scope and key seperated by a forward slash is required for OrderedDataStore without a scope.")

        response = request_session.post(f"https://apis.roblox.com/ordered-data-stores/v1/universes/{self.experince.id}/orderedDatastores/{urllib.parse.quote(self.name)}/scopes/{urllib.parse.quote(scope)}/entries/{urllib.parse.quote(key)}:increment",
            headers={"x-api-key": self.__api_key, "user-agent": user_agent}, json={
                "amount": increment
            })
        
        if response.status_code == 200: return int(response.json()["value"])
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The key {key} does not exist.")
        elif response.status_code == 409 and response.json()["message"] == "Entry value outside of bounds.": raise ValueError("New value can't be less than 0.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

    def remove(self, key: str) -> None:
        """
        Removes a key.

        Args:
            key: The key to remove. If `scope` is `None`, then the key should use the `scope/key` syntax.

        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to remove ordered data store keys, or is from an invalid IP address.
            NotFound: The experience, data store, or entry does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
            ValueError: The `scope/key` syntax wasn't used and `scope` is `None`, or both `exclusive_create` and `exclusive_update` are `True`.
        """

        try:
            if not self.scope: scope, key = key.split("/", maxsplit=1)
            else: scope = self.scope
        except(ValueError): raise ValueError("a scope and key seperated by a forward slash is required for OrderedDataStore without a scope.")

        response = request_session.delete(f"https://apis.roblox.com/ordered-data-stores/v1/universes/{self.experince.id}/orderedDatastores/{urllib.parse.quote(self.name)}/scopes/{urllib.parse.quote(scope)}/entries/{urllib.parse.quote(key)}",
            headers={"x-api-key": self.__api_key, "user-agent": user_agent})
        
        if response.status_code in [200, 204]: return None
        elif response.status_code == 400: raise rblx_opencloudException(response.json()["message"])
        elif response.status_code == 401: raise InvalidKey(response.text)
        elif response.status_code == 403: raise InvalidKey(response.json()["message"])
        elif response.status_code == 404: raise NotFound(response.json()["message"])
        elif response.status_code == 429: raise RateLimited(response.json()["message"])
        elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")