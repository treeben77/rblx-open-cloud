from .exceptions import rblx_opencloudException, NotFound, PreconditionFailed
import json, datetime
import base64, hashlib, urllib.parse
from typing import Union, Optional, Iterable, TYPE_CHECKING
from . import send_request, iterate_request
from dateutil import parser

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
    Contains data about an entry such as version ID, timestamps, users and \
    metadata.
    """
    def __init__(self, version, created, updated, users, metadata) -> None:
        self.version: str = version
        self.created: datetime.datetime = parser.parse(created)
        self.updated: datetime.datetime = parser.parse(updated)
        self.users: list[int] = users
        self.metadata: dict = metadata
    
    def __repr__(self) -> str:
        return f"<rblxopencloud.EntryInfo version=\"{self.version}\" \
users={self.users} metadata={self.metadata}>"

class EntryVersion():
    """
    Contains data about a version such as it's ID, timestamps, content length \
    and wether this version is deleted.
    """

    def __init__(self, version, deleted, content_length, created, key_created,
        datastore, key, scope) -> None:
        self.version: str = version
        self.deleted: bool = deleted
        self.content_length: int = content_length
        self.created: datetime.datetime = parser.parse(created)
        self.key_created: datetime.datetime = parser.parse(key_created)
        self.__datastore: DataStore = datastore
        self.__key = key
        self.__scope = scope
    
    def __eq__(self, object) -> bool:
        if not isinstance(object, EntryVersion):
            return NotImplemented
        return (
            self.__key == object.__key and self.__scope == object.__scope and
            self.version == object.version
        )
    
    def get_value(self
        ) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        """
        Gets the value of this version. Shortcut for `DataStore.get_version`
        """

        if self.__datastore.scope:
            return self.__datastore.get_version(self.__key, self.version)
        else:
            return self.__datastore.get_version(
                f"{self.__scope}/{self.__key}", self.version)

    def __repr__(self) -> str:
        return f"<rblxopencloud.EntryVersion version\"{self.version}\" \
content_length={self.content_length}>"

class ListedEntry():
    """
    Object which contains an entry's key and scope.
    """
    def __init__(self, key, scope) -> None:
        self.key: str = key
        self.scope: str = scope
    
    def __eq__(self, object) -> bool:
        if not isinstance(object, ListedEntry):
            return NotImplemented
        return self.key == object.key and self.scope == object.scope
    
    def __repr__(self) -> str:
        return f"<rblxopencloud.ListedEntry key=\"{self.key}\" \
scope=\"{self.scope}\">"

class DataStore():
    """
    Represents a regular data store in an experience.
    """

    def __init__(self, name, experience, api_key, created, scope):
        self.name: str = name
        self.__api_key: str = api_key
        self.scope: str = scope
        self.experience: Experience = experience
        if created: self.created = parser.parse(created)
        else: self.created = None
    
    def __repr__(self) -> str:
        return f"<rblxopencloud.DataStore(name=\"{self.name}\" \
            scope=\"{self.scope}\" experience={repr(self.experience)}>"
    
    def __str__(self) -> str:
        return self.name

    def list_keys(self, prefix: str="", limit: int=None
        ) -> Iterable[ListedEntry]:
        """
        Iterates all keys in the database and scope, optionally matching a \
        prefix.

        Args:
            prefix (str): Only return keys that start with this prefix.
            limit (int): Will not return more keys than this number. Set to \
            `None` for no limit.
        """
        
        for entry in iterate_request("GET", f"datastores/v1/universes/\
{self.experience.id}/standard-datastores/datastore/entries", params={
            "datastoreName": self.name,
            "scope": self.scope,
            "AllScopes": not self.scope,
            "prefix": prefix
        }, expected_status=[200], authorization=self.__api_key,
        cursor_key="cursor", data_key="keys"):
            yield ListedEntry(entry["key"], entry["scope"])
    
    def get(self, key: str
        ) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        """
        Gets the value of a key in the scope and datastore.
        
        Args:
            key (str): The key to fetch. If `DataStore.scope` is `None`, this \
            must include the scope in the `scope/key` syntax.
        """
        try:
            scope = self.scope
            if not scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("'scope/key' syntax expected for key.")
        
        _, data, headers = send_request("GET", 
            f"datastores/v1/universes/{self.experience.id}/standard-datastores\
/datastore/entries/entry",
            authorization=self.__api_key, expected_status=[200], params={
                "datastoreName": self.name,
                "scope": scope,
                "entryKey": key
            })

        if headers.get("roblox-entry-attributes"):
            metadata = json.loads(headers["roblox-entry-attributes"])
        else: metadata = {}

        if headers.get("roblox-entry-userids"):
            userids = json.loads(headers["roblox-entry-userids"])
        else: userids = []
        
        return data, EntryInfo(
            headers["roblox-entry-version"],
            headers["roblox-entry-created-time"],
            headers["roblox-entry-version-created-time"], userids, metadata)

    def set(self, key: str, value: Union[str, dict, list, int, float],
            users: Optional[list[int]]=None, metadata: dict={},
            exclusive_create: bool=False, previous_version: Optional[str]=None
        ) -> EntryVersion:
        """
        Sets the value of a key in the datastore and scope.
        
        Args:
            key (str): The key to update. If `DataStore.scope` is `None`, \
            this must include the scope in the `scope/key` syntax.
            value (Union[str, dict, list, int, float]): The new value to set.
            users (list[int]): a list of Roblox user IDs to attach to the \
            entry.
            metadata (dict): a dict of metadata to attach to the entry.
            exclusive_create (bool): Whether to update the entry if it \
            already has a value. Raises \
            [`PreconditionFailed`][rblxopencloud.PreconditionFailed] if it \
            has a value.
            previous_version (Optional[str]): If provided, the current \
            version ID must match this string or the entry will not be \
            updated and \
            [`PreconditionFailed`][rblxopencloud.PreconditionFailed] is raised.
        """
        if previous_version and exclusive_create:
            raise ValueError(
                "previous_version and exclusive_create are mutally exclusive."
            )

        if users == None: users = []
        
        try:
            scope = self.scope
            if not scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("'scope/key' syntax expected for key.")

        status_code, data, headers = send_request("POST",
            f"datastores/v1/universes/{self.experience.id}/standard-datastores\
/datastore/entries/entry", authorization=self.__api_key, headers={
                "roblox-entry-userids": json.dumps(users),
                "roblox-entry-attributes": json.dumps(metadata)
            }, json=value, params={
                "datastoreName": self.name,
                "scope": scope,
                "entryKey": key,
                "exclusiveCreate": exclusive_create,
                "matchVersion": previous_version
            }, expected_status=[200, 412])
        
        if status_code == 412:
            if headers.get("roblox-entry-attributes"):
                metadata = json.loads(headers["roblox-entry-attributes"])
            else: metadata = {}

            if headers.get("roblox-entry-userids"):
                userids = json.loads(headers["roblox-entry-userids"])
            else: userids = []
        
            if exclusive_create:
                error = "A value already exists for this key."
            elif previous_version:
                error = f"The current version is not '{previous_version}'"
            else:
                error = "Precondition failed."

            raise PreconditionFailed(data, EntryInfo(
                headers["roblox-entry-version"],
                headers["roblox-entry-created-time"],
                headers["roblox-entry-version-created-time"], userids, metadata
            ), error)
        
        return EntryVersion(
            data["version"], data["deleted"], data["contentLength"],
            data["createdTime"], data["objectCreatedTime"], self, key,
            self.scope if self.scope else scope
        )

    def increment(self, key: str, delta: Union[int, float],
            users: Optional[list[int]]=None, metadata:dict={}
        ) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        """
        Increments the value of a key in the datastore and scope.
        
        Args:
            key (str): The key to increment. If `DataStore.scope` is `None`, \
            this must include the scope in the `scope/key` syntax.
            delta (Union[int, float]): The number to increment the value by. \
            Use negative numbers to decrement the value.
            users (list[int]): a list of Roblox user IDs to attach to the \
            entry.
            metadata (dict): a dict of metadata to attach to the entry.
        """
        
        if users == None: users = []
        
        try:
            scope = self.scope
            if not scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("'scope/key' syntax expected for key.")

        _, data, headers = send_request("POST",
            f"datastores/v1/universes/{self.experience.id}/standard-datastores\
/datastore/entries/entry/increment", authorization=self.__api_key, headers={
                "roblox-entry-userids": json.dumps(users),
                "roblox-entry-attributes": json.dumps(metadata)
            }, params={
                "datastoreName": self.name,
                "scope": scope,
                "entryKey": key,
                "incrementBy": delta
            }, expected_status=[200])

        if headers.get("roblox-entry-attributes"):
            metadata = json.loads(headers["roblox-entry-attributes"])
        else: metadata = {}

        if headers.get("roblox-entry-userids"):
            userids = json.loads(headers["roblox-entry-userids"])
        else: userids = []
        
        return data, EntryInfo(
            headers["roblox-entry-version"],
            headers["roblox-entry-created-time"],
            headers["roblox-entry-version-created-time"], userids, metadata)
    
    def remove(self, key: str) -> None:
        """
        Removes the value of a key from the datastore and scope.
        
        Args:
            key (str): The key to remove. If `DataStore.scope` is `None`, \
            this must include the scope in the `scope/key` syntax.
        """

        try:
            scope = self.scope
            if not scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("'scope/key' syntax expected for key.")
                
        send_request("DELETE",
            f"datastores/v1/universes/{self.experience.id}/standard-datastores\
/datastore/entries/entry",
            authorization=self.__api_key, params={
                "datastoreName": self.name,
                "scope": scope,
                "entryKey": key
            }, expected_status=[204])

        return None
    
    def list_versions(self, key: str, after: datetime.datetime = None,
            before: datetime.datetime = None, limit: Optional[int] = None,
            descending: bool = True) -> Iterable[EntryVersion]:
        """
        Iterates all available versions of a key.

        Args:
            key (str): The key to find versions. If `DataStore.scope` is \
            `None`, this must include the scope in the `scope/key` syntax.
            after (datetime.datetime): Filters versions to only those created \
            after this time.
            before (datetime.datetime): Filters versions to only those \
            created before this time.
            limit (Optional[int]): Maximum number of versions to iterate.
            descending (bool) When `True`, versions are iterated in \
            descending order (oldest to youngest).
        """

        try:
            scope = self.scope
            if not scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("'scope/key' syntax expected for key.")
        
        for entry in iterate_request("GET", f"datastores/v1/universes/\
{self.experience.id}/standard-datastores/datastore/entries/versions", params={
            "datastoreName": self.name,
            "scope": self.scope,
            "entryKey": key,
            "sortOrder": "Descending" if descending else "Ascending",
            "startTime": after.isoformat() if after else None,
            "endTime": before.isoformat() if before else None
        }, expected_status=[200], authorization=self.__api_key,
        cursor_key="cursor", data_key="keys"):
            yield EntryVersion(entry["version"], entry["deleted"],
                entry["contentLength"], entry["createdTime"],
                entry["objectCreatedTime"], self, key,
                self.scope if self.scope else scope)

    def get_version(self, key: str, version: str
        ) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        """
        Gets the value of a key at a specific version ID.
        
        Args:
            key (str): The key to get. If `DataStore.scope` is `None`, this \
            must include the scope in the `scope/key` syntax.
            version (str): The version ID string to fetch.
        """

        try:
            scope = self.scope
            if not scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("'scope/key' syntax expected for key.")
        
        status_code, data, headers = send_request("GET",
            f"datastores/v1/universes/{self.experience.id}/standard-datastores\
/datastore/entries/entry/versions/version", authorization=self.__api_key,
            params={
                "datastoreName": self.name,
                "scope": scope,
                "entryKey": key,
                "versionId": version
            }, expected_status=[200, 400])

        if status_code == 400:
            if data["message"] == "Invalid version id.":
                raise NotFound(data["message"])
            else:
                raise rblx_opencloudException(data["message"])
        
        if headers.get("roblox-entry-attributes"):
            metadata = json.loads(headers["roblox-entry-attributes"])
        else: metadata = {}

        if headers.get("roblox-entry-userids"):
            userids = json.loads(headers["roblox-entry-userids"])
        else: userids = []
        
        return data, EntryInfo(
            headers["roblox-entry-version"],
            headers["roblox-entry-created-time"],
            headers["roblox-entry-version-created-time"], userids, metadata)

class SortedEntry():
    """
    Object which contains a sorted entry's key, scope, and value.
    """
    def __init__(self, key: str, value: int, scope: str="global") -> None:
        self.key: str = key
        self.scope: str = scope
        self.value: int = value
    
    def __eq__(self, object) -> bool:
        if not isinstance(object, SortedEntry): return NotImplemented
        return (
            self.key == object.key and
            self.scope == object.scope and
            self.value == object.value
        )
    
    def __repr__(self) -> str:
        return f"<rblxopencloud.SortedEntry \"{self.key}\" value={self.value}>"

class OrderedDataStore():
    """
    Represents an ordered data store in an experience.
    """

    def __init__(self, name, experience, api_key, scope):
        self.name = name
        self.__api_key = api_key
        self.scope = scope
        self.experience = experience
    
    def __repr__(self) -> str:
        return f"<rblxopencloud.OrderedDataStore \"{self.name}\" \
scope=\"{self.scope}\" experience={repr(self.experience)}>"
    
    def __str__(self) -> str:
        return self.name
    
    def sort_keys(self, descending: bool=True, limit: Optional[int]=None,
        min=None, max=None) -> Iterable[SortedEntry]:
        """
        Returns a list of keys and their values.

        Args:
            descending (bool): Wether the largest number should be first, or \
            the smallest.
            limit (int): Max number of entries to loop through.
            min (int): Minimum entry value to retrieve
            max (int): Maximum entry value to retrieve.
        """
        if not self.scope:raise ValueError(
            "scope is required to list keys with OrderedDataStore."
        )

        filter = None
        if min and max:
            if min > max: raise ValueError("min must not be greater than max.")
            filter = f"entry >= {min} && entry <= {max}"
        elif min: filter = f"entry >= {min}"
        elif max: filter = f"entry <= {max}"

        for entry in iterate_request("GET", f"ordered-data-stores/v1/universes\
/{self.experience.id}/orderedDataStores/{urllib.parse.quote(self.name)}/scopes\
/{urllib.parse.quote(self.scope)}/entries", params={
            "max_page_size": limit if limit and limit < 100 else 100,
            "order_by": "desc" if descending else None,
            "filter": filter
        }, expected_status=[200], authorization=self.__api_key,
        cursor_key="page_token", data_key="entries"):
            yield SortedEntry(entry["id"], entry["value"], self.scope)
    
    def get(self, key: str) -> int:
        """
        Gets the value of a key.
        
        Args:
            key (str): The key to find.
        """
        try:
            if not self.scope: scope, key = key.split("/", maxsplit=1)
            else: scope = self.scope
        except(ValueError):
            raise ValueError("'scope/key' syntax expected for key.")

        _, data, _ = send_request("GET", f"ordered-data-stores/v1/universes/\
{self.experience.id}/orderedDataStores/{urllib.parse.quote(self.name)}/scopes/\
{urllib.parse.quote(scope)}/entries/{urllib.parse.quote(key)}",
                authorization=self.__api_key, expected_status=[200])
        
        return int(data["value"])
        
    def set(self, key: str, value: int, exclusive_create: bool=False,
            exclusive_update: bool=False) -> int:
        """
        Sets the value of a key.

        Args:
            key (str): The key to create/update.
            value (int): The new integer value. Must be positive.
            exclusive_create (bool): Wether to fail if the key already has a \
            value.
            exclusive_update (bool): Wether to fail if the key does not have \
            a value.
        """
        try:
            if not self.scope: scope, key = key.split("/", maxsplit=1)
            else: scope = self.scope
        except(ValueError):
            raise ValueError("'scope/key' syntax expected for key.")
        if exclusive_create and exclusive_update: raise ValueError(
            "exclusive_create and exclusive_updated can not both be True"
        )

        if not exclusive_create:
            status_code, data, _ = send_request("PATCH", f"ordered-data-stores\
/v1/universes/{self.experience.id}/orderedDataStores/\
{urllib.parse.quote(self.name)}/scopes/{urllib.parse.quote(scope)}/entries/\
{urllib.parse.quote(key)}",
                authorization=self.__api_key, expected_status=[200], params={
                    "allow_missing": not exclusive_update
                }, json={
                    "value": value
                })
        else:
            status_code, data, _ = send_request("POST", f"ordered-data-stores\
/v1/universes/{self.experience.id}/orderedDataStores/\
{urllib.parse.quote(self.name)}/scopes/{urllib.parse.quote(scope)}/entries",
                authorization=self.__api_key, expected_status=[200, 400, 404],
                params={
                    "id": key
                }, json={
                    "value": value
                })
        
        if status_code == 400:
            if data["message"] == "Entry already exists.":
                raise PreconditionFailed(None, None, data["message"])
            else:
                raise rblx_opencloudException(data["message"])
        
        if (
            status_code == 404 and exclusive_update and
            data["code"] == "NOT_FOUND"
        ):
            raise PreconditionFailed(data["message"])

        return int(data["value"])

    def increment(self, key: str, delta: int) -> None:
        """
        Increments the value of a key.
        
        Args:
            key (str): The key to increment.
            delta (int): The amount to increment the key by. You can use \
            negative numbers to decrease the value.
        """
        try:
            if not self.scope: scope, key = key.split("/", maxsplit=1)
            else: scope = self.scope
        except(ValueError): raise ValueError(
            "'scope/key' syntax expected for key."
        )

        status_code, data, _ = send_request("POST", f"ordered-data-stores/v1/\
            universes/{self.experience.id}/orderedDataStores/\
            {urllib.parse.quote(self.name)}/scopes/{urllib.parse.quote(scope)}\
            /entries/{urllib.parse.quote(key)}:increment",
            authorization=self.__api_key, expected_status=[200, 409], json={
                "amount": delta
            })
        
        if (status_code == 409 and
            data["message"] == "Entry value outside of bounds."
        ):
            raise ValueError("Entry value outside of bounds.")
        
        if status_code == 409:
            raise rblx_opencloudException(f"Unexpected HTTP {status_code}")
        
        return int(data["value"])

    def remove(self, key: str) -> None:
        """
        Removes a key.
        
        Args:
            key (str): The key to remove.
        """

        try:
            if not self.scope: scope, key = key.split("/", maxsplit=1)
            else: scope = self.scope
        except(ValueError): raise ValueError(
            "'scope/key' syntax expected for key."
        )

        send_request("DELETE", f"ordered-data-stores/v1/universes/\
{self.experience.id}/orderedDataStores/{urllib.parse.quote(self.name)}/scopes/\
{urllib.parse.quote(scope)}/entries/{urllib.parse.quote(key)}",
            authorization=self.__api_key, expected_status=[200, 204])
        
        return None