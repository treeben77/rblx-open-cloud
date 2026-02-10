# MIT License

# Copyright (c) 2022-2026 treeben77

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

from datetime import datetime
from typing import Optional, Union, Self

from .creator import Asset, AssetType, CreatorStoreProduct
from .datastore import DataStore
from .experience import Experience
from .group import Group
from .http import send_request
from .user import User

from typing import Union

__all__ = ("ApiKey", "ApiKeyScope")


class ApiKeyScope:
    """
    Represents an API key scope used for the introspect endpoint. `name` \
    and `operations` are always available, while the other attributes depend \
    on the scope context.

    Attributes:
        name: The name of the scope; for instance, `universe-datastores.objects`.
        operations: The allowed operations for the scope such as `read` and write`.
        experiences: A list of experiences the scope applies to, if any. \
        Will be `None` if not applicable. `True` indicates all experiences.
        users: A list of users the scope applies to, if any. Will be `None` \
        if not applicable. Primarily for the assets API. `True` indicates all \
        users.
        groups: A list of groups the scope applies to, if any. Will be `None` \
        if not applicable. Primarily for the assets API. `True` indicates all \
        groups.
        datastores: A list of datastores the scope applies to, if any. Will \
        be `None` if not applicable. Note that this is only populated if the \
        scope restricts to specific datastores; if all datastores are \
        allowed, `experiences` will be populated instead. If all datastores \
        in all experiences are allowed, both `experiences` will be `True`. In \
        these last two cases, `datastores` will be an empty list.
    """

    def __repr__(self):
        suffix = ""

        if self.experiences is not None:
            suffix += f" experiences={self.experiences!r}"
        if self.users is not None:
            suffix += f" users={self.users!r}"
        if self.groups is not None:
            suffix += f" groups={self.groups!r}"
        if self.datastores is not None:
            suffix += f" datastores={self.datastores!r}"

        return f"<rblxopencloud.Scope name={self.name!r} \
operations={self.operations!r}{suffix}>"

    def __init__(self, scope, api_key) -> None:
        print(scope)
        self.name: str = scope.get("name")
        self.operations: list[str] = scope.get("operations", [])

        experience_id_cache = {}

        if "universeIds" not in scope:
            self.experiences: Union[list[Experience], True, None] = None
        elif scope["universeIds"][0] == "*":
            self.experiences: Union[list[Experience], True, None] = True
        else:
            self.experiences: Union[list[Experience], True, None] = []
            for experience_id in scope.get("universeIds", []):
                experience = Experience(int(experience_id), api_key)
                self.experiences.append(experience)
                if "universeDatastores" in scope:
                    experience_id_cache[experience_id] = experience

        if "userIds" not in scope:
            self.users: Optional[list[User]] = None
        elif scope["userIds"][0] == "*":
            self.users: Union[list[User], True, None] = True
        else:
            self.users: Union[list[User], True, None] = []
            for user_id in scope.get("userIds", []):
                self.users.append(User(int(user_id), api_key))

        if "groupIds" not in scope:
            self.groups: Union[list[Group], True, None] = None
        elif scope["groupIds"][0] == "*":
            self.groups: Union[list[Group], True, None] = True
        else:
            self.groups: Union[list[Group], True, None] = []
            for group_id in scope.get("groupIds", []):
                self.groups.append(Group(int(group_id), api_key))

        if "universeDatastores" not in scope:
            self.datastores: Union[list[Union[DataStore]], None] = None
        elif scope["universeDatastores"][0].get("universeId") == "*":
            self.datastores: Union[list[Union[DataStore]], None] = None
            self.experiences = True
        else:
            self.datastores: Union[list[Union[DataStore]], None] = []
            if self.experiences is None:
                self.experiences = []

            for datastore in scope.get("universeDatastores", []):
                experience = experience_id_cache.get(
                    datastore.get("universeId")
                )
                if not experience:
                    experience = Experience(
                        int(datastore.get("universeId")), api_key
                    )
                    experience_id_cache[datastore.get("universeId")] = (
                        experience
                    )

                if datastore.get("datastoreName") is None:
                    if experience not in self.experiences:
                        self.experiences.append(experience)
                    continue

                self.datastores.append(
                    experience.get_datastore(datastore.get("datastoreName"))
                )


class ApiKey:
    """
    Represents an API key and allows creation of API classes (such as
    [`User`][rblxopencloud.User]) without needing to use the API key string \
    all the time.

    Args:
        api_key: Your API key created from \
        [Creator Dashboard](https://create.roblox.com/credentials).
    
    The following attributes are only available after calling \
    [`fetch_info`][rblxopencloud.ApiKey.fetch_info].
    
    Attributes:
        name: The name of the API key as set in Creator Dashboard.
        enabled: Whether the API key is enabled.
        expired: Whether the API key is expired.
        expires_at: The expiration date and time of the API key.
        authorized_user: The user who generated the API key. For group API \
        keys, this will be the user who last generated the key.
    """

    def __init__(self, api_key: str) -> None:
        self.__api_key = api_key

        self.name: Optional[str] = None
        self.enabled: Optional[bool] = None
        self.expired: Optional[bool] = None
        self.expires_at: Optional[datetime] = None
        self.authorized_user: Optional[User] = None
        self.scopes: Optional[list[ApiKeyScope]] = None

    async def fetch_info(self) -> Self:
        """
        Fetches information about the API key.

        Returns:
            The same [`ApiKey`][rblxopencloud.ApiKey] instance with fetched \
            information.
        """

        _, data, _ = await send_request(
            "POST",
            f"api-keys/v1/introspect",
            json={"apiKey": self.__api_key},
            expected_status=[200],
        )

        self.name = data.get("name")
        self.enabled = data.get("enabled")
        self.expired = data.get("expired")
        self.expires_at = (
            datetime.fromisoformat(data["expirationUtcTime"])
            if data.get("expirationUtcTime") is not None
            else None
        )
        self.authorized_user = User(data["authorizedUserId"], self.__api_key)

        self.scopes = [
            ApiKeyScope(scope, self.__api_key)
            for scope in data.get("scopes", [])
        ]

        return self

    def get_experience(self, id: int, fetch_info: bool = False) -> Experience:
        obj = Experience(id, self.__api_key)

        if fetch_info:
            obj.fetch_info()

        return obj

    def get_group(self, id: int, fetch_info: bool = False) -> Group:
        obj = Group(id, self.__api_key)

        if fetch_info:
            obj.fetch_info()

        return obj

    def get_user(self, id: int, fetch_info: bool = False) -> User:
        obj = User(id, self.__api_key)

        if fetch_info:
            obj.fetch_info()

        return obj

    async def fetch_asset(self, asset_id: int) -> Asset:
        """
        Fetches an asset uploaded to Roblox.

        Args:
            asset_id: The ID of the asset to fetch.

        Returns:
            An [`Asset`][rblxopencloud.Asset] representing the asset.
        """

        read_mask = [
            "path",
            "revisionId",
            "revisionCreateTime",
            "assetId",
            "displayName",
            "assetType",
            "creationContext",
            "moderationResult",
            "state",
            "description",
            "icon",
            "socialLink",
        ]

        _, data, _ = await send_request(
            "GET",
            f"assets/v1/assets/{asset_id}",
            params={"readMask": ",".join(read_mask)},
            authorization=self.__api_key,
            expected_status=[200],
        )

        return Asset(data, self, self.__api_key)

    async def fetch_creator_store_product(
        self, asset_type: Union[AssetType, str], product_id: int
    ) -> CreatorStoreProduct:
        """
        Fetches information about an asset on the creator store.

        Args:
            asset_type: The type of asset the product is.
            product_id: The ID of the asset to fetch.

        Returns:
            A [`CreatorStoreProduct`][rblxopencloud.CreatorStoreProduct] \
            representing the asset.

        Tip:
            If the asset type is unknown or other information such as the \
            description is required, use the \
            [`fetch_asset`][rblxopencloud.ApiKey.fetch_asset].
        """

        asset_type = (
            asset_type.name if type(asset_type) == AssetType else asset_type
        )

        _, data, _ = send_request(
            "GET",
            "/creator-store-products/CreatorMarketplaceAsset"
            f"-{asset_type}-{product_id}",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return CreatorStoreProduct(data, self.__api_key)
