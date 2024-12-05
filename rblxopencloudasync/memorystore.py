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
from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional, Union

from dateutil import parser

from .exceptions import HttpException, NotFound, PreconditionFailed
from .http import iterate_request, send_request

if TYPE_CHECKING:
    from .experience import Experience

__all__ = ("SortedMap", "SortedMapEntry", "MemoryStoreQueue")


class SortedMapEntry:
    """
    Represents an entry in a sorted map.

    Attributes:
        key: The entry's key.
        sort_key: The numeric or string key used to sort the entry.
        scope: The entry's scope.
        value: The value of the entry.
        etag: A server generated value for preconditional updating.
        expires_at: The timestamp the entry will expire at.
    """

    def __init__(self, data) -> None:
        self.key: str = data["id"]
        self.sort_key: Optional[Union[int, float, str]] = data.get(
            "numericSortKey"
        ) or data.get("stringSortKey")
        self.value: int = data["value"]
        self.etag: str = data["etag"]
        self.expires_at: datetime.datetime = parser.parse(data["expireTime"])

    def __repr__(self) -> str:
        return f'<rblxopencloud.SortedMapEntry \
key="{self.key}" value={json.dumps(self.value)}>'


class SortedMap:
    """
    Represents a sorted map memory store in an experience.

    Attributes:
        name (str): The sorted map's name.
        experience (Experience): The experience the sorted map is a part of.
    """

    def __init__(self, name, experience, api_key):
        self.name: str = name
        self.__api_key: str = api_key
        self.experience: Experience = experience

    def __repr__(self) -> str:
        return f'<rblxopencloud.SortedMap \
"{self.name}" experience={repr(self.experience)}>'

    async def list_keys(
        self,
        descending: bool = False,
        limit: int = None,
        lower_bound_key: Union[str, int] = None,
        upper_bound_key: Union[str, int] = None,
        lower_bound_sort_key: Union[str, int] = None,
        upper_bound_sort_key: Union[str, int] = None,
    ) -> AsyncGenerator[Any, SortedMapEntry]:
        """
        Returns an Iterable of keys in the sorted map.

        Args:
            descending: Wether to return keys in descending order.
            limit: Will not return more keys than this number. Set to `None` \
            for no limit.
            lower_bound_key: Only return values with key names greater than \
            this value.
            upper_bound_key: Only return values with key names less than this \
            value.
            lower_bound_sort_key: Only return values with sort keys greater \
            than this value.
            upper_bound_sort_key: Only return values with sort keys less than \
            this value.
            
        Yields:
            A sorted map entry representing for each entry in the sorted map.
        """
        filter = []

        if lower_bound_key:
            if type(lower_bound_key) == str:
                lower_bound_key = f'"{lower_bound_key}"'

            filter.append(f"id > {lower_bound_key}")

        if upper_bound_key:
            if type(upper_bound_key) == str:
                upper_bound_key = f'"{upper_bound_key}"'

            filter.append(f"id < {upper_bound_key}")

        if lower_bound_sort_key:
            if type(lower_bound_sort_key) == str:
                lower_bound_sort_key = f'"{lower_bound_sort_key}"'

            filter.append(f"sortKey > {lower_bound_sort_key}")

        if upper_bound_sort_key:
            if type(upper_bound_sort_key) == str:
                upper_bound_sort_key = f'"{upper_bound_sort_key}"'
            filter.append(f"sortKey < {upper_bound_sort_key}")

        async for entry in iterate_request(
            "GET",
            f"/universes/{self.experience.id}/memory-store/\
sorted-maps/{urllib.parse.quote_plus(self.name)}/items",
            authorization=self.__api_key,
            expected_status=[200],
            params={
                "orderBy": "desc" if descending else None,
                "maxPageSize": limit if limit and limit < 100 else 100,
                "filter": " && ".join(filter),
            },
            cursor_key="pageToken",
            data_key="items",
            max_yields=limit,
        ):
            yield SortedMapEntry(entry)

    async def get_key(self, key: str) -> SortedMapEntry:
        """
        Fetches the value of a key.

        Args:
            key: The key to find.

        Returns:
            The entry information.
        """

        _, data, _ = await send_request(
            "GET",
            f"/universes/{self.experience.id}/memory-store/\
sorted-maps/{urllib.parse.quote_plus(self.name)}/items/\
{urllib.parse.quote_plus(key)}",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return SortedMapEntry(data)

    async def set_key(
        self,
        key: str,
        value: Union[str, dict, list, int, float],
        expiration_seconds: int,
        sort_key: Union[int, float, str] = None,
        exclusive_create: bool = False,
        exclusive_update: bool = False,
    ) -> SortedMapEntry:
        """
        Creates or updates the provided key.

        Args:
            key: The key to be created or updated.
            value: The new value of the key.
            expiration_seconds: The number of seconds for the entry to live. \
            Can not be greater than 3,888,000 seconds.
            sort_key: The sort key used for sorting.
            exclusive_create: Wether to fail if the key already has a value.
            exclusive_update: Wether to fail if the key doesn't have a value.
        
        Returns:
            The new entry information. 
        """

        if exclusive_create and exclusive_update:
            raise ValueError(
                "exclusive_create and exclusive_updated can not both be True"
            )

        if not exclusive_create:
            status, data, _ = await send_request(
                "PATCH",
                f"/universes/{self.experience.id}/memory-store/\
sorted-maps/{urllib.parse.quote_plus(self.name)}/items/\
{urllib.parse.quote_plus(key)}",
                authorization=self.__api_key,
                expected_status=[200, 404, 409],
                params={"allowMissing": str(not exclusive_update).lower()},
                json={
                    "id": key,
                    "Value": value,
                    "Ttl": f"{expiration_seconds}s",
                    (
                        "stringSortKey"
                        if type(sort_key) == str
                        else "numericSortKey"
                    ): sort_key,
                },
            )
        else:
            status, data, _ = await send_request(
                "POST",
                f"/universes/{self.experience.id}/memory-store\
/sorted-maps/{urllib.parse.quote_plus(self.name)}/items",
                authorization=self.__api_key,
                expected_status=[200, 409],
                params={"id": urllib.parse.quote_plus(key)},
                json={
                    "id": key,
                    "value": value,
                    "ttl": f"{expiration_seconds}s",
                    (
                        "stringSortKey"
                        if type(sort_key) == str
                        else "numericSortKey"
                    ): sort_key,
                },
            )

        if status == 404:
            if exclusive_update:
                raise PreconditionFailed(None, None, status, data)

            raise NotFound(status, data)

        if status == 409:
            if data["error"] == "ALREADY_EXISTS":
                raise PreconditionFailed(None, None, status, data)

            raise HttpException(status, data)

        if not data.get("id"):
            data["id"] = key

        return SortedMapEntry(data)

    async def remove_key(self, key: str, etag: str = None) -> None:
        """
        Deletes a key from the sorted map.

        Args:
            key: The key to remove.
            etag: Only delete if the current etag is the same as the provided \
            value. Etag can be retrieved from \
            [`SortedMapEntry.etag`][rblxopencloud.SortedMapEntry].
        """

        await send_request(
            "DELETE",
            f"/universes/{self.experience.id}/memory-store/\
sorted-maps/{urllib.parse.quote_plus(self.name)}/items/\
{urllib.parse.quote_plus(key)}",
            authorization=self.__api_key,
            params={"etag": etag},
        )


class MemoryStoreQueue:
    """
    Represents a memory store queue in an experience.

    Attributes:
        name: The queue's name.
        experience: The experience the queue belongs to.
    """

    def __init__(self, name, experience, api_key):
        self.name: str = name
        self.__api_key: str = api_key
        self.experience: Experience = experience

    def __repr__(self) -> str:
        return f'<rblxopencloud.MemoryStoreQueue \
"{self.name}", experience={repr(self.experience)}>'

    async def add_item(
        self,
        value: Union[str, dict, list, int, float],
        expiration_seconds: int = 30,
        priority: float = 0,
    ) -> None:
        """
        Adds a value to the queue.

        Args:
            value: The value to be added to the queue.
            expiration_seconds: The number of seconds for the value to stay \
            in the queue.
            priority: The value's priority. Keys with higher priorities leave \
            the queue first.
        """

        await send_request(
            "POST",
            f"/universes/{self.experience.id}/memory-store/\
queues/{urllib.parse.quote_plus(self.name)}/items:add",
            authorization=self.__api_key,
            expected_status=[200],
            json={
                "Data": value,
                "Ttl": f"{expiration_seconds}s",
                "Priority": priority,
            },
        )

    async def read_items(
        self,
        count: int = 1,
        all_or_nothing: bool = False,
        invisibility_seconds: int = 30,
    ) -> tuple[list[Union[str, dict, list, int, float]], Optional[str]]:
        """
        Reads values from the queue.

        Args:
            count: The number of values to return
            all_or_nothing: Wether to return nothing if there isn't enough \
            items in the queue to fullfill the requested `count`.
            invisibility_seconds: The number of seconds the items in the \
            queue should be invisible from further read requests.
        
        Returns:
            A list of values as the first parameter and a readid string as \
            the second parameter. The read ID string can be passed to \
            [`MemoryStoreQueue.remove_items`\
            ][rblxopencloud.MemoryStoreQueue.remove_items].
        """

        status, data, _ = await send_request(
            "GET",
            f"/universes/{self.experience.id}/memory-store/\
queues/{urllib.parse.quote_plus(self.name)}/items:read",
            authorization=self.__api_key,
            expected_status=[200, 204],
            params={
                "count": count,
                "allOrNothing": all_or_nothing,
                "invisibilityTimeoutSeconds": invisibility_seconds,
            },
            json={},
        )

        if status == 204:
            return [], None

        return data["data"], data["id"]

    async def remove_items(self, read_id: str) -> None:
        """
        Permanently removes previously read values from the queue. 

        Args:
            read_id: The read ID returned by [`MemoryStoreQueue.read_items`\
            ][rblxopencloud.MemoryStoreQueue.read_items].
        """

        await send_request(
            "POST",
            f"/universes/{self.experience.id}/memory-store/\
queues/{urllib.parse.quote_plus(self.name)}/items:discard",
            authorization=self.__api_key,
            expected_status=[200],
            params={"readId": read_id},
            json={},
        )
