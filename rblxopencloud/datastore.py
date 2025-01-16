# MIT License

# Copyright (c) 2022-2024 treeben77

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import datetime
import json
import urllib.parse
from typing import TYPE_CHECKING, Iterable, Optional, Union

from dateutil import parser

from .exceptions import HttpException, NotFound, PreconditionFailed
from .http import iterate_request, send_request

if TYPE_CHECKING:
    from .experience import Experience

__all__ = (
    "EntryInfo",
    "EntryVersion",
    "ListedEntry",
    "DataStore",
    "SortedEntry",
    "OrderedDataStore",
)


class EntryInfo:
    """
    Contains data about an entry such as version ID, timestamps, users and \
    metadata.

    Attributes:
        version: The string ID of the entry's version
        created: When this key was created
        updated: When this key was last modified, or when this version was \
        created.
        users: a list of user ids attached to this entry.
        metadata: the key-value pairs of metadata attached to this entry.
    """

    def __init__(self, version, created, updated, users, metadata) -> None:
        self.version: str = version
        self.created: datetime.datetime = parser.parse(created)
        self.updated: datetime.datetime = parser.parse(updated)
        self.users: list[int] = users
        self.metadata: dict = metadata

    def __repr__(self) -> str:
        return f'<rblxopencloud.EntryInfo version="{self.version}" \
users={self.users} metadata={self.metadata}>'


class EntryVersion:
    """
    Contains data about a version such as it's ID, timestamps, content length \
    and wether this version is deleted.

    Attributes:
        version: The string ID of this version.
        deleted: Wether this version has been deleted.
        content_length: The length of the value.
        created: When this version was created.
        key_created: When the key was first created.
    
    **Supported Operations:**

    | Operator | Description |
    | -------- | ----------- |
    | `==`     | Whether two [`EntryVersion`][rblxopencloud.EntryVersion] \
        have the same `version` and are of the same key and scope. |
    """

    def __init__(
        self,
        version,
        deleted,
        content_length,
        created,
        key_created,
        datastore,
        key,
        scope,
    ) -> None:
        self.version: str = version
        self.deleted: bool = deleted
        self.content_length: int = content_length
        self.created: datetime.datetime = (
            parser.parse(created) if created else None
        )
        self.key_created: datetime.datetime = (
            parser.parse(key_created) if key_created else None
        )
        self.__datastore: DataStore = datastore
        self.__key = key
        self.__scope = scope

    def __eq__(self, object) -> bool:
        if not isinstance(object, EntryVersion):
            return NotImplemented
        return (
            self.__key == object.__key
            and self.__scope == object.__scope
            and self.version == object.version
        )

    def get_value(
        self,
    ) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        """
        Gets the value of this version. Shortcut for `DataStore.get_version`
        """

        if self.__datastore.scope:
            return self.__datastore.get_version(self.__key, self.version)
        else:
            return self.__datastore.get_version(
                f"{self.__scope}/{self.__key}", self.version
            )

    def __repr__(self) -> str:
        return f'<rblxopencloud.EntryVersion version"{self.version}" \
content_length={self.content_length}>'


class ListedEntry:
    """
    Object which contains an entry's key and scope.

    Attributes:
        key: The entry's key.
        scope: The entry's scope, usually is `global`.

    **Supported Operations:**

    | Operator | Description |
    | -------- | ----------- |
    | `==`     | Whether two [`ListedEntry`][rblxopencloud.ListedEntry] \
        have the same `key` and `scope`. |
    """

    def __init__(self, key, scope) -> None:
        self.key: str = key
        self.scope: str = scope

    def __eq__(self, object) -> bool:
        if not isinstance(object, ListedEntry):
            return NotImplemented
        return self.key == object.key and self.scope == object.scope

    def __repr__(self) -> str:
        return f'<rblxopencloud.ListedEntry key="{self.key}" \
scope="{self.scope}">'


class DataStore:
    """
    Represents a regular data store in an experience.

    Attributes:
        name: The datastore's name.
        scope: The datastore's scope. `scope/key` syntax is required for keys \
        when scope is `None`.
        experience: The experience this DataStore is a part of.
    """

    def __init__(self, name, experience, api_key, created, scope):
        self.name: str = name
        self.__api_key: str = api_key
        self.scope: Optional[str] = scope
        self.experience: Experience = experience
        if created:
            self.created = parser.parse(created)
        else:
            self.created = None

    def __repr__(self) -> str:
        return f'<rblxopencloud.DataStore name="{self.name}" \
scope="{self.scope}" experience={repr(self.experience)}>'

    def list_keys(
        self, prefix: str = "", limit: int = None
    ) -> Iterable[ListedEntry]:
        """
        Iterates all keys in the database and scope, optionally matching a \
        prefix.

        Args:
            prefix: Only return keys that start with this prefix.
            limit: Will not return more keys than this number. Set to `None` \
            for no limit.
        """

        for entry in iterate_request(
            "GET",
            f"datastores/v1/universes/\
{self.experience.id}/standard-datastores/datastore/entries",
            params={
                "datastoreName": self.name,
                "scope": self.scope,
                "AllScopes": not self.scope,
                "prefix": prefix,
            },
            expected_status=[200],
            authorization=self.__api_key,
            cursor_key="cursor",
            data_key="keys",
        ):
            yield ListedEntry(entry["key"], entry["scope"])

    def get_entry(
        self, key: str
    ) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        """
        Gets the value of a key in the scope and datastore.
        
        Args:
            key: The key to fetch. If `DataStore.scope` is `None`, this must \
            include the scope in the `scope/key` syntax.
        """
        try:
            scope = self.scope
            if not scope:
                scope, key = key.split("/", maxsplit=1)
        except ValueError:
            raise ValueError("'scope/key' syntax expected for key.")

        _, data, headers = send_request(
            "GET",
            f"datastores/v1/universes/{self.experience.id}/standard-datastores\
/datastore/entries/entry",
            authorization=self.__api_key,
            expected_status=[200],
            params={
                "datastoreName": self.name,
                "scope": scope,
                "entryKey": key,
            },
        )

        if headers.get("roblox-entry-attributes"):
            metadata = json.loads(headers["roblox-entry-attributes"])
        else:
            metadata = {}

        if headers.get("roblox-entry-userids"):
            userids = json.loads(headers["roblox-entry-userids"])
        else:
            userids = []

        return data, EntryInfo(
            headers["roblox-entry-version"],
            headers["roblox-entry-created-time"],
            headers["roblox-entry-version-created-time"],
            userids,
            metadata,
        )

    def set_entry(
        self,
        key: str,
        value: Union[str, dict, list, int, float],
        users: Optional[list[int]] = None,
        metadata: dict = {},
        exclusive_create: bool = False,
        previous_version: Optional[str] = None,
    ) -> EntryVersion:
        """
        Sets the value of a key in the datastore and scope.
        
        Args:
            key: The key to update. If `DataStore.scope` is `None`, this must \
            include the scope in the `scope/key` syntax.
            value: The new value to set.
            users: A list of Roblox user IDs to attach to the entry.
            metadata: A key-value pair of metadata to attach to the entry.
            exclusive_create: Whether to update the entry if it already has a \
            value. If `True` and it already has a value, \
            [`PreconditionFailed`][rblxopencloud.PreconditionFailed] is raised.
            previous_version: The expected previous version ID. If provided, \
            and the previous version doesn't match, \
            [`PreconditionFailed`][rblxopencloud.PreconditionFailed] is raised.
        """
        if previous_version and exclusive_create:
            raise ValueError(
                "previous_version and exclusive_create are mutally exclusive."
            )

        if users is None:
            users = []

        try:
            scope = self.scope
            if not scope:
                scope, key = key.split("/", maxsplit=1)
        except ValueError:
            raise ValueError("'scope/key' syntax expected for key.")

        status_code, data, headers = send_request(
            "POST",
            f"datastores/v1/universes/{self.experience.id}/standard-datastores\
/datastore/entries/entry",
            authorization=self.__api_key,
            headers={
                "roblox-entry-userids": json.dumps(users),
                "roblox-entry-attributes": json.dumps(metadata),
            },
            json=value,
            params={
                "datastoreName": self.name,
                "scope": scope,
                "entryKey": key,
                "exclusiveCreate": exclusive_create,
                "matchVersion": previous_version,
            },
            expected_status=[200, 412],
        )

        if status_code == 412:
            if headers.get("roblox-entry-attributes"):
                metadata = json.loads(headers["roblox-entry-attributes"])
            else:
                metadata = {}

            if headers.get("roblox-entry-userids"):
                userids = json.loads(headers["roblox-entry-userids"])
            else:
                userids = []

            if exclusive_create:
                error = "A value already exists for this key."
            elif previous_version:
                error = f"The current version is not '{previous_version}'"
            else:
                error = "Precondition failed."

            raise PreconditionFailed(
                data,
                EntryInfo(
                    headers["roblox-entry-version"],
                    headers["roblox-entry-created-time"],
                    headers["roblox-entry-version-created-time"],
                    userids,
                    metadata,
                ),
                status_code,
                error,
            )

        return EntryVersion(
            data.get("version"),
            data.get("deleted"),
            data.get("contentLength"),
            data.get("createdTime"),
            data.get("objectCreatedTime"),
            self,
            key,
            self.scope if self.scope else scope,
        )

    def increment_entry(
        self,
        key: str,
        delta: Union[int, float],
        users: Optional[list[int]] = None,
        metadata: dict = {},
    ) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        """
        Increments the value of a key in the datastore and scope.
        
        Args:
            key: The key to increment. If `DataStore.scope` is `None`, this \
            must include the scope in the `scope/key` syntax.
            delta: The number to increment the value by. Use negative numbers \
            to decrement the value.
            users: a list of Roblox user IDs to attach to the entry.
            metadata: a dict of metadata to attach to the entry.
        """

        if users is None:
            users = []

        try:
            scope = self.scope
            if not scope:
                scope, key = key.split("/", maxsplit=1)
        except ValueError:
            raise ValueError("'scope/key' syntax expected for key.")

        _, data, headers = send_request(
            "POST",
            f"datastores/v1/universes/{self.experience.id}/standard-datastores\
/datastore/entries/entry/increment",
            authorization=self.__api_key,
            headers={
                "roblox-entry-userids": json.dumps(users),
                "roblox-entry-attributes": json.dumps(metadata),
            },
            params={
                "datastoreName": self.name,
                "scope": scope,
                "entryKey": key,
                "incrementBy": delta,
            },
            expected_status=[200],
        )

        if headers.get("roblox-entry-attributes"):
            metadata = json.loads(headers["roblox-entry-attributes"])
        else:
            metadata = {}

        if headers.get("roblox-entry-userids"):
            userids = json.loads(headers["roblox-entry-userids"])
        else:
            userids = []

        return data, EntryInfo(
            headers["roblox-entry-version"],
            headers["roblox-entry-created-time"],
            headers["roblox-entry-version-created-time"],
            userids,
            metadata,
        )

    def remove_entry(self, key: str) -> None:
        """
        Removes the value of a key from the datastore and scope.
        
        Args:
            key: The key to remove. If `DataStore.scope` is `None`, this must \
            include the scope in the `scope/key` syntax.
        """

        try:
            scope = self.scope
            if not scope:
                scope, key = key.split("/", maxsplit=1)
        except ValueError:
            raise ValueError("'scope/key' syntax expected for key.")

        send_request(
            "DELETE",
            f"datastores/v1/universes/{self.experience.id}/standard-datastores\
/datastore/entries/entry",
            authorization=self.__api_key,
            params={
                "datastoreName": self.name,
                "scope": scope,
                "entryKey": key,
            },
            expected_status=[204],
        )

        return None

    def list_versions(
        self,
        key: str,
        after: datetime.datetime = None,
        before: datetime.datetime = None,
        limit: int = None,
        descending: bool = True,
    ) -> Iterable[EntryVersion]:
        """
        Iterates all available versions of a key.

        Args:
            key: The key to find versions. If `DataStore.scope` is `None`, \
            this must include the scope in the `scope/key` syntax.
            after: Filters versions to only those created after this time.
            before: Filters versions to only those created before this time.
            limit: Maximum number of versions to iterate.
            descending: When `True` versions are iterated oldest first.
        """

        try:
            scope = self.scope
            if not scope:
                scope, key = key.split("/", maxsplit=1)
        except ValueError:
            raise ValueError("'scope/key' syntax expected for key.")

        for entry in iterate_request(
            "GET",
            f"datastores/v1/universes/\
{self.experience.id}/standard-datastores/datastore/entries/versions",
            params={
                "datastoreName": self.name,
                "scope": self.scope,
                "entryKey": key,
                "sortOrder": "Descending" if descending else "Ascending",
                "startTime": after.isoformat() if after else None,
                "endTime": before.isoformat() if before else None,
            },
            expected_status=[200],
            authorization=self.__api_key,
            cursor_key="cursor",
            data_key="keys",
        ):
            yield EntryVersion(
                entry.get("version"),
                entry.get("deleted"),
                entry.get("contentLength"),
                entry.get("createdTime"),
                entry.get("objectCreatedTime"),
                self,
                key,
                self.scope if self.scope else scope,
            )

    def get_version(
        self, key: str, version: Union[str, datetime.datetime]
    ) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        """
        Gets the value of a key at a specific version ID.
        
        Args:
            key: The key to get. If `DataStore.scope` is `None`, this must \
            include the scope in the `scope/key` syntax.
            version: The version ID string to fetch or datetime object to get \
            latest version at specific time.
        """

        try:
            scope = self.scope
            if not scope:
                scope, key = key.split("/", maxsplit=1)
        except ValueError:
            raise ValueError("'scope/key' syntax expected for key.")

        if type(version) == datetime.datetime:
            time = version.astimezone(tz=datetime.timezone.utc)
            version = f"latest:{time.isoformat('T').split('.')[0] + 'Z'}"

        status_code, data, _ = send_request(
            "GET",
            f"/universes/{self.experience.id}/\
data-stores/{self.name}/entries/{key}@{version}",
            authorization=self.__api_key,
            expected_status=[200, 400],
        )

        if status_code == 400:
            if data["message"] == "Invalid version id.":
                raise NotFound(status_code, data)
            else:
                raise HttpException(status_code, data)

        return data["value"], EntryInfo(
            data["revisionId"],
            data["createTime"],
            data["revisionCreateTime"],
            users=[
                int(user_id.split("/")[1]) for user_id in data.get("users", [])
            ],
            metadata=data["attributes"],
        )


class SortedEntry:
    """
    Object which contains a sorted entry's key, scope, and value.

    Attributes:
        key: The entry's key.
        scope: The entry's scope.
        value: The entry's value.
    
    **Supported Operations:**

    | Operator | Description |
    | -------- | ----------- |
    | `==`     | Whether two [`SortedEntry`][rblxopencloud.SortedEntry] \
        have the same `key`, `scope` and `value`. |
    """

    def __init__(self, key: str, value: int, scope: str = "global") -> None:
        self.key: str = key
        self.scope: str = scope
        self.value: int = int(value)

    def __eq__(self, object) -> bool:
        if not isinstance(object, SortedEntry):
            return NotImplemented
        return (
            self.key == object.key
            and self.scope == object.scope
            and self.value == object.value
        )

    def __repr__(self) -> str:
        return f'<rblxopencloud.SortedEntry "{self.key}" value={self.value}>'


class OrderedDataStore:
    """
    Represents an ordered data store in an experience.

    Attributes:
        name: The ordered data store's name.
        scope: The ordered data store's scope. If `None`, `scope/key` syntax \
        must be used for keys.
        experience: The experience this ordered data store is a part of.
    """

    def __init__(self, name, experience, api_key, scope):
        self.name: str = name
        self.__api_key = api_key
        self.scope: str = scope
        self.experience: Experience = experience

    def __repr__(self) -> str:
        return f'<rblxopencloud.OrderedDataStore "{self.name}" \
scope="{self.scope}" experience={repr(self.experience)}>'

    def sort_keys(
        self,
        descending: bool = True,
        limit: Optional[int] = None,
        min: int = None,
        max: int = None,
    ) -> Iterable[SortedEntry]:
        """
        Returns an Iterable of keys in order based on their value.

        Args:
            descending: Wether the largest or the smallest number should be \
            first.
            limit: Max number of entries to loop through.
            min: Minimum entry value to retrieve
            max: Maximum entry value to retrieve.
        
        !!! note
            `OrderedDataStore.scope` must not be `None` to sort keys. It is \
            not possible to sort keys from all scopes.
        """

        if not self.scope:
            raise ValueError(
                "scope is required to list keys with OrderedDataStore."
            )

        filter = None
        if min and max:
            if min > max:
                raise ValueError("min must not be greater than max.")
            filter = f"entry >= {min} && entry <= {max}"
        elif min:
            filter = f"entry >= {min}"
        elif max:
            filter = f"entry <= {max}"

        for entry in iterate_request(
            "GET",
            f"ordered-data-stores/v1/universes\
/{self.experience.id}/orderedDataStores/{urllib.parse.quote(self.name)}/scopes\
/{urllib.parse.quote(self.scope)}/entries",
            params={
                "max_page_size": limit if limit and limit < 100 else 100,
                "order_by": "desc" if descending else None,
                "filter": filter,
            },
            expected_status=[200],
            authorization=self.__api_key,
            cursor_key="page_token",
            data_key="entries",
            max_yields=limit,
        ):
            yield SortedEntry(entry["id"], entry["value"], self.scope)

    def get_entry(self, key: str) -> int:
        """
        Gets the value of a key.
        
        Args:
            key: The key to find. If `OrderedDataStore.scope` is `None`, this \
            must include the scope in the `scope/key` syntax.
        """
        try:
            if not self.scope:
                scope, key = key.split("/", maxsplit=1)
            else:
                scope = self.scope
        except ValueError:
            raise ValueError("'scope/key' syntax expected for key.")

        _, data, _ = send_request(
            "GET",
            f"ordered-data-stores/v1/universes/\
{self.experience.id}/orderedDataStores/{urllib.parse.quote(self.name)}/scopes/\
{urllib.parse.quote(scope)}/entries/{urllib.parse.quote(key)}",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return int(data["value"])

    def set_entry(
        self,
        key: str,
        value: int,
        exclusive_create: bool = False,
        exclusive_update: bool = False,
    ) -> int:
        """
        Sets the value of a key.

        Args:
            key: The key to create or update. If `OrderedDataStore.scope` is \
            `None`, this must include the scope in the `scope/key` syntax.
            value: The new integer value. Must be positive.
            exclusive_create: Wether to fail if the key already has a value.
            exclusive_update: Wether to fail if the key does not have a value.
        """
        try:
            if not self.scope:
                scope, key = key.split("/", maxsplit=1)
            else:
                scope = self.scope
        except ValueError:
            raise ValueError("'scope/key' syntax expected for key.")
        if exclusive_create and exclusive_update:
            raise ValueError(
                "exclusive_create and exclusive_updated can not both be True"
            )

        if not exclusive_create:
            status_code, data, _ = send_request(
                "PATCH",
                f"ordered-data-stores\
/v1/universes/{self.experience.id}/orderedDataStores/\
{urllib.parse.quote(self.name)}/scopes/{urllib.parse.quote(scope)}/entries/\
{urllib.parse.quote(key)}",
                authorization=self.__api_key,
                expected_status=[200],
                params={"allow_missing": not exclusive_update},
                json={"value": value},
            )
        else:
            status_code, data, _ = send_request(
                "POST",
                f"ordered-data-stores\
/v1/universes/{self.experience.id}/orderedDataStores/\
{urllib.parse.quote(self.name)}/scopes/{urllib.parse.quote(scope)}/entries",
                authorization=self.__api_key,
                expected_status=[200, 400, 404],
                params={"id": key},
                json={"value": value},
            )

        if status_code == 400:
            if data["message"] == "Entry already exists.":
                raise PreconditionFailed(None, None, status_code, data)
            else:
                raise HttpException(status_code, data)

        if (
            status_code == 404
            and exclusive_update
            and data["code"] == "NOT_FOUND"
        ):
            raise PreconditionFailed(status_code, data)

        return int(data["value"])

    def increment_entry(self, key: str, delta: int) -> None:
        """
        Increments the value of a key.
        
        Args:
            key: The key to increment.
            delta: The amount to increment the key by. Negative numbers will \
            decrease the value.
        """
        try:
            if not self.scope:
                scope, key = key.split("/", maxsplit=1)
            else:
                scope = self.scope
        except ValueError:
            raise ValueError("'scope/key' syntax expected for key.")

        _, data, _ = send_request(
            "POST",
            f"ordered-data-stores/v1/\
universes/{self.experience.id}/orderedDataStores/\
{urllib.parse.quote(self.name)}/scopes/{urllib.parse.quote(scope)}\
/entries/{urllib.parse.quote(key)}:increment",
            authorization=self.__api_key,
            expected_status=[200],
            json={"amount": delta},
        )

        return int(data["value"])

    def remove_entry(self, key: str) -> None:
        """
        Removes a key.

        Args:
            key: The key to remove.
        """

        try:
            if not self.scope:
                scope, key = key.split("/", maxsplit=1)
            else:
                scope = self.scope
        except ValueError:
            raise ValueError("'scope/key' syntax expected for key.")

        send_request(
            "DELETE",
            f"ordered-data-stores/v1/universes/\
{self.experience.id}/orderedDataStores/{urllib.parse.quote(self.name)}/scopes/\
{urllib.parse.quote(scope)}/entries/{urllib.parse.quote(key)}",
            authorization=self.__api_key,
            expected_status=[200, 204],
        )
