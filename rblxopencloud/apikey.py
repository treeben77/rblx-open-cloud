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
import sys
from typing import Iterable, Optional, Sequence, Union

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


from .creator import (
    Asset,
    AssetType,
    CreatorStoreProduct,
    InstanceType,
    Money,
    MusicChartType,
    ToolboxAsset,
    ToolboxAssetSubtype,
    ToolboxSearchSortCategory,
    ToolboxSearchContext,
)
from .datastore import DataStore
from .experience import Experience
from .group import Group
from .http import iterate_request, send_request
from .user import User

__all__ = ("ApiKey", "ApiKeyScope")


class ApiKeyScope:
    """
    Represents an API key scope used for the introspect endpoint. `name` \
    and `operations` are always available, while the other attributes depend \
    on the scope context.

    Attributes:
        name: The name of the scope; for instance, `universe-datastores.objects`.
        operations: The allowed operations for the scope such as `read` and `write`.
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


SAVED_ASSETS_SEARCH_SORT_CATEGORY_MAPPING = {
    "Top": "Ratings",
    "AssetType": "TargetType",
    "SaveTime": "DateSaved",
    "UpdateTime": "LastModified",
}


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

    def fetch_info(self) -> Self:
        """
        Fetches information about the API key.

        Returns:
            The same [`ApiKey`][rblxopencloud.ApiKey] instance with fetched \
            information.
        """

        _, data, _ = send_request(
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

    def fetch_asset(self, asset_id: int) -> Asset:
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
            "previews",
            "facebookSocialLink",
            "twitterSocialLink",
            "youtubeSocialLink",
            "twitchSocialLink",
            "discordSocialLink",
            "githubSocialLink",
            "robloxSocialLink",
            "guildedSocialLink",
            "devForumSocialLink",
            "tryAssetSocialLink",
        ]

        _, data, _ = send_request(
            "GET",
            f"assets/v1/assets/{asset_id}",
            params={"readMask": ",".join(read_mask)},
            authorization=self.__api_key,
            expected_status=[200],
        )

        return Asset(data, self, self.__api_key)

    def fetch_creator_store_product(
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

    def fetch_toolbox_asset(self, asset_id: int) -> ToolboxAsset:
        """
        Fetches information about an asset in the toolbox.

        Requires `creator-store-product:read` on an API key. OAuth2 authorization \
        is not supported. No authorization is supported (i.e. `api_key` is `None`).

        Args:
            asset_id: The ID of the asset to fetch.

        Returns:
            The asset information for the toolbox asset.
        """

        _, data, _ = send_request(
            "GET",
            f"toolbox-service/v2/assets/{asset_id}",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return ToolboxAsset(data, None, self.__api_key)

    def search_toolbox(
        self,
        asset_type: AssetType,
        query: Optional[str] = None,
        model_subtype: Optional[Sequence[ToolboxAssetSubtype]] = None,
        excluded_model_subtype: Optional[Sequence[ToolboxAssetSubtype]] = None,
        creator: Optional[Union[Group, User]] = None,
        verified_creators_only: Optional[bool] = None,
        descending: Optional[bool] = None,
        limit: Optional[int] = None,
        sort_by: Optional[ToolboxSearchSortCategory] = None,
        min_duration_seconds: Optional[int] = None,
        max_duration_seconds: Optional[int] = None,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        include_top_charts: Optional[bool] = False,
        included_instance_types: Optional[Sequence[InstanceType]] = None,
        min_price: Optional[Money] = None,
        max_price: Optional[Money] = None,
        category_path: Optional[str] = None,
        music_chart_type: Optional[MusicChartType] = None,
        facets: Optional[Sequence[str]] = None,
    ) -> Iterable[tuple[ToolboxAsset, ToolboxSearchContext]]:
        """
        Searches for assets in the toolbox (or, the creator store) with various \
        filters and sorting options.

        Requires `creator-store-product:read` on an API key. OAuth2 authorization \
        is not supported. No authorization is supported (i.e. `api_key` is `None`).

        ??? example
            Searchs for audio assets in the toolbox with the query *"Menu Theme"*, \
            uploaded by @DistrokidOffical. The results are filtered to only \
            include assets that are free and are between 45 and 60 seconds long. \
            The first result is printed to the console along with how many more \
            results there are.
            ```python
            user = apikey.get_user(7135127272)

            for asset, context in apikey.search_toolbox(
                asset_type=rblxopencloud.AssetType.Audio,
                query="Menu Theme",
                creator=user,
                max_price=Money("USD", 0),
                max_duration_seconds=60,
                min_duration_seconds=45,
                limit=1
            ):
                print(asset, "and", context.total_results - 1, "more...")
            >>> "<rblxopencloud.ToolboxAsset asset_id=114376757380093> and 4 more..."
            ```

        Args:
            asset_type: The category of the toolbox assets to search. Only \
            `Audio`, `Model`, `Decal`, `Plugin`, `MeshPart`, `Video`, and \
            `FontFamily` are accepted.
            query: The search query.
            model_subtype: Any model subtypes to filter by. Only applicable if \
            `asset_type` is `Model`.
            excluded_model_subtype: Any model subtypes to exclude. Only \
            applicable if `asset_type` is `Model`.
            creator: The creator object (either a group or user) to filter by.
            verified_creators_only: Whether to include only verified creators.
            descending: Whether to sort the results in descending order.
            sort_by: The category to sort by. Defaults to relevance.
            min_duration_seconds: For audio, the minimum duration of the audio in seconds.
            max_duration_seconds: For audio, the maximum duration of the audio in seconds.
            artist: For audio, the artist of the audio.
            album: For audio, the album of the audio.
            facets: Additional keywords to query by. \
            [`ToolboxSearchContext.available_facets`][rblxopencloud.ToolboxSearchContext] \
            contains available facets for the search results.
            include_top_charts: For audio, whether to include top charts results.
            included_instance_types: For plugins, the instance types to include.
            min_price: The minimum price of the asset in USD.
            max_price: The maximum price of the asset in USD.
            category_path: The category path to filter by. For instance, `3d__props-and-decor`.
            music_chart_type: For audio, the type of music chart duration to include.
        
        Yields:
            A tuple containing the asset information for each toolbox asset \
            found and the context for the search results page such as total \
            results, facets, and filtered keywords.
        """

        sort_by = sort_by.name if sort_by else None

        if sort_by == "UpdateTime":
            sort_by = "UpdatedTime"

        min_price_cents = None
        max_price_cents = None

        if min_price is not None:
            if min_price.currency.lower() != "usd":
                raise ValueError("min_price must be in USD")

            min_price_cents = int(min_price.quantity * 100)

        if max_price is not None:
            if max_price.currency.lower() != "usd":
                raise ValueError("max_price must be in USD")

            max_price_cents = int(max_price.quantity * 100)

        payload = {
            "searchCategoryType": asset_type.name,
            "maxPageSize": limit if limit and limit < 100 else 100,
            "query": query,
            "modelSubtypes": (
                ",".join(st.name for st in model_subtype)
                if model_subtype
                else None
            ),
            "excludedModelSubtypes": (
                ",".join(st.name for st in excluded_model_subtype)
                if excluded_model_subtype
                else None
            ),
            "creatorId": creator.id if creator else None,
            "creatorType": (
                "User"
                if isinstance(creator, User)
                else "Group" if isinstance(creator, Group) else None
            ),
            "sortOrder": (
                "Descending"
                if descending
                else "Ascending" if descending is not None else None
            ),
            "sortBy": sort_by,
            "audioMinDurationSeconds": min_duration_seconds,
            "audioMaxDurationSeconds": max_duration_seconds,
            "audioArtist": artist,
            "audioAlbum": album,
            "includeTopCharts": include_top_charts,
            "includedInstanceTypes": (
                ",".join(it.name for it in included_instance_types)
                if included_instance_types
                else None
            ),
            "includeOnlyVerifiedCreators": verified_creators_only,
            "minPriceCents": min_price_cents,
            "maxPriceCents": max_price_cents,
            "categoryPath": category_path,
            "searchView": "Full",
            "musicChartType": (
                music_chart_type.name if music_chart_type else None
            ),
            "facets": ",".join(facets) if facets else None,
        }

        if creator is not None:
            if isinstance(creator, User):
                payload["userId"] = creator.id
            elif isinstance(creator, Group):
                payload["groupId"] = creator.id

        for entry, response in iterate_request(
            "GET",
            f"toolbox-service/v2/assets:search",
            authorization=self.__api_key,
            expected_status=[200],
            params=payload,
            data_key="creatorStoreAssets",
            cursor_key="pageToken",
            max_yields=limit,
            include_raw_response=True,
        ):
            yield ToolboxAsset(
                entry, creator, self.__api_key
            ), ToolboxSearchContext(response)

    def search_saved_assets(
        self,
        asset_type: Optional[AssetType] = None,
        query: Optional[str] = None,
        asset_id: Optional[int] = None,
        descending: Optional[bool] = None,
        limit: Optional[int] = None,
        sort_by: Optional[ToolboxSearchSortCategory] = None,
        exclude_owned_assets: Optional[bool] = None,
    ) -> Iterable[tuple[ToolboxAsset, ToolboxSearchContext]]:
        """
        Iterates through the authenticated user's [saved assets](https://create.roblox.com/store/saved) \
        with various filters and sorting options.

        Requires `creator-store-save:read` on an API key. OAuth2 \
        authorization is not supported.

        ??? example
            Iterates through the authenticated user's saved model assets and \
            prints the first one along with when it was saved and how many more \
            results there are. Ordered with highest rated first.

            ```python
            for asset, context in api_key.search_saved_assets(
                asset_type=AssetType.Model,
                sort_by=ToolboxSearchSortCategory.Top,
                descending=True,
                exclude_owned_assets=True,
            ):
                print(asset, "saved at", asset.saved_at, "and", context.total_results - 1, "more...")
                break
            >>> <rblxopencloud.ToolboxAsset asset_id=77975161416102> saved at 2026-02-11 11:01:33.495+00:00 and 67 more...
            ```

        Args:
            asset_type: The category of the saved assets to search.
            query: Keywords to filter by.
            asset_id: The ID of the asset to filter by. Can only be present if \
            `asset_type` is also present.
            descending: Whether to sort the results in descending order.
            limit: The maximum number of results to return.
            sort_by: The category to sort by. Defaults to saved time.
            exclude_owned_assets: Whether to exclude assets the authenticated user \
            owns from the results.
        
        Yields:
            A tuple containing the asset information for each saved toolbox asset \
            found along with `is_owned` and `saved_at`, and the context for \
            the search results - limited to `total_results` for this endpoint.
        """

        sort_by = sort_by.name if sort_by else None

        sort_by = SAVED_ASSETS_SEARCH_SORT_CATEGORY_MAPPING.get(
            sort_by, sort_by
        )

        for entry, response in iterate_request(
            "GET",
            f"toolbox-service/v1/saves",
            authorization=self.__api_key,
            expected_status=[200],
            params={
                "keyword": query,
                "targetType": asset_type.name if asset_type else None,
                "targetId": asset_id,
                "sortBy": sort_by,
                "sortDirection": (
                    "Descending"
                    if descending
                    else "Ascending" if descending is not None else None
                ),
                "limit": limit if limit and limit < 100 else 100,
                "hideOwnedAssets": exclude_owned_assets,
            },
            data_key="saves",
            cursor_key="page",
            include_raw_response=True,
            next_cursor_hook=lambda prev_cursor: (
                prev_cursor + 1 if prev_cursor else 2
            ),
        ):
            if entry.get("creatorStoreAsset") is None:
                continue

            yield ToolboxAsset(
                entry["creatorStoreAsset"], None, self.__api_key, entry
            ), ToolboxSearchContext(response)

    def save_asset(self, asset_id: int, asset_type: AssetType) -> None:
        """
        Saves an asset from the toolbox to the authenticated user's [saved \
        assets](https://create.roblox.com/store/saved).

        Requires `creator-store-save:write` on an API key. OAuth2 \
        authorization is not supported.

        Args:
            asset_id: The ID of the asset to save.
        """

        send_request(
            "POST",
            f"toolbox-service/v1/saves",
            authorization=self.__api_key,
            expected_status=[200, 201],
            json={
                "targetType": asset_type.name,
                "targetId": asset_id,
            },
        )

    def unsave_assets(
        self, assets: Union[list[tuple[int, AssetType]], tuple[int, AssetType]]
    ) -> int:
        """
        Unsaves one or more assets in the toolbox from the authenticated \
        user's [saved assets](https://create.roblox.com/store/saved).

        Requires `creator-store-save:write` on an API key. OAuth2 \
        authorization is not supported.

        ??? example
            Unsaves a single asset with ID `114376757380093` of type `Audio`.
            ```python
            count = api_key.unsave_assets((114376757380093, AssetType.Audio))
            print("Unsaved", count, "asset!")
            >>> "Unsaved 1 asset!"
            ```

            Unsaves multiple assets with IDs `114376757380093` of type `Audio` and \
            `14903722621` of type `Model`:
            ```python
            count = api_key.unsave_assets([
                (114376757380093, AssetType.Audio),
                (14903722621, AssetType.Model)
            ])
            print("Unsaved", count, "assets!")
            >>> "Unsaved 2 assets!"
            ```

        Args:
            assets: A list of tuples (or a single tuple) comprising of the \
            asset ID as the first value, and the asset type as the second \
            value to be unsaved.
        
        Returns:
            The number of assets successfully unsaved.
        """

        if type(assets) is tuple:
            assets = [assets]

        if len(assets) == 1:
            send_request(
                "DELETE",
                f"toolbox-service/v1/saves",
                authorization=self.__api_key,
                expected_status=[200, 201, 204],
                params={
                    "targetType": assets[0][1].name,
                    "targetId": assets[0][0],
                },
            )

            return 1
        else:
            targets = []

            for asset_id, asset_type in assets:
                targets.append(
                    {
                        "targetType": asset_type.name,
                        "targetId": asset_id,
                    }
                )

            _, data, _ = send_request(
                "POST",
                f"toolbox-service/v1/saves:bulkDelete",
                authorization=self.__api_key,
                expected_status=[200, 201, 204],
                json={"targets": targets},
            )

            return data.get("deletedCount")
