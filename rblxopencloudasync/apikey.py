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

from .creator import Asset, AssetType, CreatorStoreProduct
from .experience import Experience
from .group import Group
from .http import send_request
from .user import User

from typing import Union

__all__ = ("ApiKey",)


class ApiKey:
    """
    Represents an API key and allows creation of API classes (such as
    [`User`][rblxopencloud.User]) without needing to use the API key string \
    all the time.

    Args:
        api_key: Your API key created from \
        [Creator Dashboard](https://create.roblox.com/credentials).
    """

    def __init__(self, api_key: str) -> None:
        self.__api_key = api_key

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

        _, data, _ = await send_request(
            "GET",
            f"assets/v1/assets/{asset_id}",
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
