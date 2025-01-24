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

import io
import json
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional, Union

import urllib3
from dateutil import parser

from .exceptions import HttpException, InvalidFile, ModeratedText
from .http import Operation, iterate_request, send_request

if TYPE_CHECKING:
    from .group import Group
    from .user import User

__all__ = (
    "AssetType",
    "ModerationStatus",
    "Asset",
    "AssetVersion",
    "Creator",
    "CreatorStoreProduct",
    "Money",
    "ProductRestriction",
)


class AssetType(Enum):
    """
    Enum denoting an [`Asset`][rblxopencloud.Asset]'s asset type.

    Attributes:
        Unknown (0): The asset type is unknown/unsupported.
        Decal (1):
        Audio (2):
        Model (3):
        Plugin (4): Only for fetching assets; does not support uploading.
        FontFamily (5): Only for fetching assets; does not support uploading.
        MeshPart (6): Only for fetching assets; does not support uploading.
        Video (7): Only for fetching assets; does not support uploading.
        Animation (8): Only for fetching assets; does not support uploading.
        Image (9): Only for fetching assets; does not support uploading.
    """

    Unknown = 0
    Decal = 1
    Audio = 2
    Model = 3
    Plugin = 4
    FontFamily = 5
    MeshPart = 6
    Video = 7
    Animation = 8
    Image = 9


ASSET_TYPE_ENUMS = {
    "Decal": AssetType.Decal,
    "Audio": AssetType.Audio,
    "Model": AssetType.Model,
    "Plugin": AssetType.Plugin,
    "FontFamily": AssetType.FontFamily,
    "MeshPart": AssetType.MeshPart,
    "Video": AssetType.Video,
    "Animation": AssetType.Animation,
    "Image": AssetType.Image,
    "ASSET_TYPE_DECAL": AssetType.Decal,
    "ASSET_TYPE_AUDIO": AssetType.Audio,
    "ASSET_TYPE_MODEL": AssetType.Model,
}


class ModerationStatus(Enum):
    """
    Enum denoting the current moderation status of an asset.

    Attributes:
        Unknown (0): The current moderation status is unknown.
        Reviewing (1): The asset has not completed moderation yet.
        Rejected (2): The asset failed moderation.
        Approved (3): The asset passed moderation.
    """

    Unknown = 0
    Reviewing = 1
    Rejected = 2
    Approved = 3


MODERATION_STATUS_ENUMS = {
    "Reviewing": ModerationStatus.Reviewing,
    "Rejected": ModerationStatus.Rejected,
    "Approved": ModerationStatus.Approved,
    "MODERATION_STATE_REVIEWING": ModerationStatus.Reviewing,
    "MODERATION_STATE_REJECTED": ModerationStatus.Rejected,
    "MODERATION_STATE_APPROVED": ModerationStatus.Approved,
}


class Asset:
    """
    Represents an asset uploaded by a [`Creator`][rblxopencloud.Creator].

    Attributes:
        id: The asset's ID.
        name: The filtered name of the asset.
        description: The filtered description of the asset.
        type: The asset's type.
        creator: The user, group, or creator which uploaded the asset.
        moderation_status: The asset's current moderation status.
        revision_id: The ID of the current revision of the asset. *Will be \
        `None` if the asset type does not support updating.*
        revision_time: The time the current revision of the asset was \
        created. *Will be `None` if the asset type does not support updating.*
    """

    def __init__(self, data: dict, creator, api_key) -> None:
        self.id: int = data.get("assetId")
        self.name: str = data.get("displayName")
        self.description: str = data.get("description")
        self.__api_key = api_key

        from .group import Group
        from .user import User

        if (
            creatorid := data.get("creationContext", {})
            .get("creator", {})
            .get("userId")
        ):
            data_creator = User(creatorid, self.__api_key)
        else:
            data_creator = Group(
                data.get("creationContext", {}).get("creator", {})["groupId"],
                self.__api_key,
            )

        if (
            type(creator) in (Creator, User, Group)
            and data_creator.id == creator.id
        ):
            self.creator: Union[Creator, User, Group] = creator
        else:
            self.creator: Union[User, Group] = data_creator

        self.type: AssetType = ASSET_TYPE_ENUMS.get(
            data.get("assetType"), AssetType.Unknown
        )

        self.moderation_status: ModerationStatus = MODERATION_STATUS_ENUMS.get(
            data.get("moderationResult", {}).get("moderationState"),
            ModerationStatus.Unknown,
        )

        self.revision_id: Optional[int] = data.get("revisionId")
        self.revision_time: Optional[datetime] = (
            parser.parse(data["revisionCreateTime"])
            if data.get("revisionCreateTime")
            else None
        )

    def __repr__(self) -> str:
        return f"<rblxopencloud.Asset id={self.id} type={self.type}>"

    async def fetch_creator_store_prodcut(self) -> "CreatorStoreProduct":
        """
        Fetches the creator store prodcut information for this asset, if it \
            is on the creator store.

        Returns:
            An [`CreatorStoreProduct`][rblxopencloud.CreatorStoreProduct] \
                representing the asset as a prodct.
        """

        return await self.creator.fetch_creator_store_product(
            self.type, self.id
        )


class AssetVersion:
    """
    Represents a version of an asset uploaded on to Roblox.

    Attributes:
        version_number: This asset version's revision ID.
        asset_id: The asset's ID.
        creator: The user, group, or creator which uploaded the asset.
        moderation_status: The moderation status of this version.
    """

    def __init__(self, data, creator) -> None:
        self.version_number: int = data["path"].split("/")[3]
        self.asset_id: int = data["path"].split("/")[1]

        self.creator: Union[Creator, User, Group] = creator

        self.moderation_status: ModerationStatus = MODERATION_STATUS_ENUMS.get(
            data.get("moderationResult", {}).get("moderationState"),
            ModerationStatus.Unknown,
        )

    def __repr__(self) -> str:
        return f"<rblxopencloud.AssetVersion \
asset_id={self.asset_id} version_number={self.version_number}>"


class ProductRestriction(Enum):
    Unknown = 0
    Unspecified = 1
    ItemRestricted = 2
    SellerTemporarilyRestricted = 3
    SellerPermanentlyRestricted = 4
    SellerNoLongerActive = 5


RESTRICTION_ENUMS = {
    "RESTRICTION_UNSPECIFIED": ProductRestriction.Unspecified,
    "SOLD_ITEM_RESTRICTED": ProductRestriction.ItemRestricted,
    "SELLER_TEMPORARILY_RESTRICTED": (
        ProductRestriction.SellerTemporarilyRestricted
    ),
    "SELLER_PERMANENTLY_RESTRICTED": (
        ProductRestriction.SellerPermanentlyRestricted
    ),
    "SELLER_NO_LONGER_ACTIVE": ProductRestriction.SellerNoLongerActive,
}


class Money:
    """
    Represents a price on the Roblox platform, such as on the creator store.

    Arguments:
        currency: The [ISO 4217](https://en.wikipedia.org/wiki/ISO_4217) \
            currency code for this price.
        quantity: The quantity of the currency. For instance, `4.99` would be \
            four dollars and ninety-nine cents in USD.

    Attributes:
        currency: The [ISO 4217](https://en.wikipedia.org/wiki/ISO_4217) \
            currency code for this price. Crypto and virtual \
            currencies will begin with `X-`. 
        quantity: The quantity of the currency. For instance, `4.99` would be \
            four dollars and ninety-nine cents in USD.

    **Supported Operations:**

    | Operator | Description |
    | -------- | ----------- |
    | `==`     | Whether two [`Money`][rblxopencloud.Money] have the same \
        currency and quantity or `quantity` equals the [`float`][float]. |
    | `<`      | Whether the `quantity` is less than the `quantity` of \
        another [`Money`][rblxopencloud.Money] with the same currency or a \
        [`float`][float]. Also supports `<=`. |
    | `>`      | Whether the `quantity` is greater than the `quantity` of \
        another [`Money`][rblxopencloud.Money] with the same currency or a \
        [`float`][float]. Also supports `>=`. |
    """

    def __init__(self, currency: str, quantity: float) -> None:
        self.currency: str = currency
        self.quantity: float = quantity

    def __repr__(self) -> str:
        return f'<rblxopencloud.Money currency="{self.currency}" \
quantity={self.quantity}>'

    def __eq__(self, value: object) -> bool:
        if type(value) not in (int, float, Money):
            raise NotImplemented

        if type(value) == Money:
            if self.currency != value.currency:
                raise ValueError("Cannot compare Money of different currency.")
            return self.quantity == value.quantity

        return self.quantity == value

    def __lt__(self, value: object) -> bool:
        if type(value) not in (int, float, Money):
            raise NotImplemented

        if type(value) == Money:
            if self.currency != value.currency:
                raise ValueError("Cannot compare Money of different currency.")
            return self.quantity < value.quantity

        return self.quantity < value

    def __gt__(self, value: object) -> bool:
        if type(value) not in (int, float, Money):
            raise NotImplemented

        if type(value) == Money:
            if self.currency != value.currency:
                raise ValueError("Cannot compare Money of different currency.")
            return self.quantity > value.quantity

        return self.quantity > value

    def __le__(self, value: object) -> bool:
        if type(value) not in (int, float, Money):
            raise NotImplemented

        if type(value) == Money:
            if self.currency != value.currency:
                raise ValueError("Cannot compare Money of different currency.")
            return self.quantity <= value.quantity

        return self.quantity <= value

    def __gt__(self, value: object) -> bool:
        if type(value) not in (int, float, Money):
            raise NotImplemented

        if type(value) == Money:
            if self.currency != value.currency:
                raise ValueError("Cannot compare Money of different currency.")
            return self.quantity >= value.quantity

        return self.quantity >= value

    def to_scientific_notation(self) -> dict:
        """
        Converts the quantity to a dict containing a significand and exponent \
        used internally for Roblox's API.

        Returns:
            A dictionary with `significand` and `exponent` values \
                representing the quantity.
        """

        num_str = f"{self.quantity:.15g}"
        decimal_places = len(num_str.split(".")[1]) if "." in num_str else 0

        return {
            "significand": int(self.quantity * (10**decimal_places)),
            "exponent": -decimal_places,
        }


class CreatorStoreProduct:
    """
    Represents an asset as a product on the creator store.

    Attributes:
        asset_id (int): The ID of the product's asset.
        asset_type (AssetType): The product's asset type.
        creator (Union[User, Group]): The user or group who created the asset.
        purchasable (bool): Whether the product can be purchased.
        published (bool): Whether the product is considered published from \
            the creator's perspective.
        restrictions (list[ProductRestriction]): A list of restrictions \
            applied to the product.
        base_price (Money): The base price set by the creator.
        purchase_price (Money): The price of the asset to the user, factoring \
        locale-specific considerations.
    """

    def __init__(self, data: dict, api_key) -> None:

        for asset_id_key, type in {
            "modelAssetId": AssetType.Model,
            "pluginAssetId": AssetType.Plugin,
            "audioAssetId": AssetType.Audio,
            "decalAssetId": AssetType.Decal,
            "meshPartAssetId": AssetType.MeshPart,
            "videoAssetId": AssetType.Video,
            "fontFamilyAssetId": AssetType.FontFamily,
        }.items():
            if asset_id := data.get(asset_id_key):
                self.asset_id: int = asset_id
                self.asset_type: AssetType = type
                break

        from .group import Group
        from .user import User

        if creatorid := data.get("userSeller"):
            self.creator: Union[User, Group] = User(creatorid, api_key)
        else:
            self.creator: Union[User, Group] = User(
                data["groupSeller"], api_key
            )

        self.purchasable: bool = data.get("purchasable")
        self.published: bool = data.get("published")

        restrictions = []

        for restriction in data.get("restrictions", []):
            restrictions.append(
                RESTRICTION_ENUMS.get(restriction, ProductRestriction.Unknown)
            )

        self.restrictions: list[ProductRestriction] = restrictions

        self.base_price: Money = Money(
            data["purchasePrice"]["currencyCode"],
            data["basePrice"]["quantity"]["significand"]
            * 10 ** data["basePrice"]["quantity"]["exponent"],
        )
        self.purchase_price: Money = Money(
            data["purchasePrice"]["currencyCode"],
            data["purchasePrice"]["quantity"]["significand"]
            * 10 ** data["purchasePrice"]["quantity"]["exponent"],
        )

    def __repr__(self) -> str:
        return f"<rblxopencloud.CreatorStoreProduct \
asset_id={self.asset_id} asset_type={self.asset_type}>"

    async def fetch_asset(self) -> Asset:
        """
        Fetches the asset information for this prodcut.

        Returns:
            An [`Asset`][rblxopencloud.Asset] representing the product's asset.
        """

        return await self.creator.fetch_asset(self.asset_id)


ASSET_MIME_TYPES = {
    "mp3": "audio/mpeg",
    "ogg": "audio/ogg",
    "png": "image/png",
    "jpeg": "image/jpeg",
    "bmp": "image/bmp",
    "tga": "image/tga",
    "fbx": "model/fbx",
}


class Creator:
    """
    Represents an object that can upload assets, such as a user or a group.

    Attributes:
        id (int): The ID of the creator.
    """

    def __init__(self, id, api_key, type) -> None:
        self.id: int = id
        self.__api_key = api_key
        self.__creator_type = type

    def __repr__(self) -> str:
        return f"<rblxopencloud.Creator id={self.id}>"

    async def fetch_asset(self, asset_id: int) -> Asset:
        """
        Fetches an asset uploaded to Roblox.

        Args:
            asset_id: The ID of the asset to fetch.

        Returns:
            An [`Asset`][rblxopencloud.Asset] representing the asset.
        """

        from .apikey import ApiKey

        return await ApiKey(self.__api_key).fetch_asset(asset_id)

    async def upload_asset(
        self,
        file: io.BytesIO,
        asset_type: Union[AssetType, str],
        name: str,
        description: str,
        expected_robux_price: int = 0,
    ) -> Operation[Asset]:
        """
        Uploads the file to Roblox as an asset and returns an \
        [`Operation`][rblxopencloud.Operation]. The following asset types are \
        currently supported:

        | Asset Type | File Formats |
        | --- | --- |
        | Decal | `.png`, `.jpeg`, `.bmp`, `.tga` |
        | Audio | `.mp3`, `.ogg` |
        | Model | `.fbx` |

        Args:
            file: The file opened in bytes to be uploaded.
            asset_type: The [`AssetType`][rblxopencloud.AssetType] for the \
            asset type you're uploading.
            name: The name of your asset.
            description: The description of your asset.
            expected_robux_price: The amount of robux expected to upload this \
            asset. Will fail if lower than the actual price.

        Returns:
            Returns a [`Operation`][rblxopencloud.Operation] for the asset \
            upload operation where `T` is an [`Asset`][rblxopencloud.Asset].
        
        !!! danger
            Avoid uploading assets to Roblox that you don't have full control \
            over, such as AI generated assets or content created by unknown \
            people. Assets uploaded that break Roblox's Terms of Services can \
            get your account moderated.

            For OAuth2 developers, it has been confirmed by Roblox staff [in \
            this DevForum post](https://devforum.roblox.com/t/2401354/36), \
            that your app will not be punished if a malicious user uses it to \
            upload Terms of Service violating content, and instead the \
            authorizing user's account will be punished.
        """

        payload = {
            "assetType": (
                asset_type.name
                if type(asset_type) == AssetType
                else asset_type
            ),
            "creationContext": {
                "creator": (
                    {
                        "userId": str(self.id),
                    }
                    if self.__creator_type == "User"
                    else {"groupId": str(self.id)}
                ),
                "expectedPrice": expected_robux_price,
            },
            "displayName": name,
            "description": description,
        }

        body, contentType = urllib3.encode_multipart_formdata(
            {
                "request": json.dumps(payload),
                "fileContent": (
                    file.name,
                    file.read(),
                    ASSET_MIME_TYPES.get(file.name.split(".")[-1]),
                ),
            }
        )

        status, data, _ = await send_request(
            "POST",
            "assets/v1/assets",
            authorization=self.__api_key,
            expected_status=[200, 400],
            headers={"content-type": contentType},
            data=body,
        )

        if status == 400:
            if data["message"] == '"InvalidImage"':
                raise InvalidFile(status, body)

            if data["message"] == "AssetName is moderated.":
                raise ModeratedText(status, body)

            if data["message"] == "AssetDescription is moderated.":
                raise ModeratedText(status, body)

            raise HttpException(status, data)

        return Operation(
            f"assets/v1/{data['path']}",
            self.__api_key,
            Asset,
            creator=self,
            api_key=self.__api_key,
        )

    async def update_asset(
        self,
        asset_id: int,
        file: io.BytesIO = None,
        name: str = None,
        description: str = None,
        expected_robux_price: int = 0,
    ) -> Operation[Asset]:
        """
        Updates an asset on Roblox with the provided file. The following \
        asset types are currently supported for file uploading:

        | Asset Type | File Formats |
        | --- | --- |
        | Model | `.fbx` |

        Args:
            asset_id: The ID of the asset to update.
            file: The file opened in bytes to upload. The asset must be one \
            of the supported file formats above.
            name: The new name of the asset.
            description: The new description for the asset.
            expected_robux_price: The amount of robux expected to update this \
            asset. Will fail if lower than the actual price.

        Returns:
            Returns a [`Operation`][rblxopencloud.Operation] for the asset \
            update operation where `T` is an [`Asset`][rblxopencloud.Asset].
        """

        payload, field_mask = {
            "assetId": asset_id,
            "creationContext": {"expectedPrice": expected_robux_price},
            "displayName": name,
            "description": description,
        }, []

        if name:
            field_mask.append("displayName")
        if description:
            field_mask.append("description")

        if file:
            body, contentType = urllib3.encode_multipart_formdata(
                {
                    "request": json.dumps(payload),
                    "fileContent": (
                        file.name,
                        file.read(),
                        ASSET_MIME_TYPES.get(file.name.split(".")[-1]),
                    ),
                }
            )
        else:
            body, contentType = urllib3.encode_multipart_formdata(
                {"request": json.dumps(payload)}
            )

        status, data, _ = await send_request(
            "PATCH",
            f"assets/v1/assets/{asset_id}",
            authorization=self.__api_key,
            expected_status=[200, 400],
            headers={"content-type": contentType},
            data=body,
            params={"updateMask": ",".join(field_mask)},
        )

        if status == 400:
            if data["message"] == '"InvalidImage"':
                raise InvalidFile(status, body)

            if data["message"] == "AssetName is moderated.":
                raise ModeratedText(status, body)

            if data["message"] == "AssetDescription is moderated.":
                raise ModeratedText(status, body)

        return Operation(
            f"assets/v1/{data['path']}",
            self.__api_key,
            Asset,
            creator=self,
            api_key=self.__api_key,
        )

    async def list_asset_versions(
        self, asset_id: int, limit: int = None
    ) -> AsyncGenerator[Any, AssetVersion]:
        """
        Iterates all avaliable versions of the asset, providing the latest \
        version first.

        Args:
            asset_id: The ID of the asset to find versions for.
            limit: The maximum number of versions to return.
        
        Yields:
            An asset version for each version of the asset.
        """

        async for entry in iterate_request(
            "GET",
            f"assets/v1/assets/{asset_id}/versions",
            params={
                "maxPageSize": limit if limit and limit <= 50 else 50,
            },
            authorization=self.__api_key,
            expected_status=[200],
            data_key="assetVersions",
            cursor_key="pageToken",
        ):
            yield AssetVersion(entry, self)

    async def fetch_asset_version(
        self, asset_id: int, version_number: int
    ) -> AssetVersion:
        """
        Fetches the version for a specific version number of the asset.

        Args:
            asset_id: The ID of the asset to find the version for.
            version_number: The version number to find.

        Returns:
            The found asset version.
        """

        _, data, _ = await send_request(
            "GET",
            f"assets/v1/assets/{asset_id}/versions/{version_number}",
            authorization=self.__api_key,
            expected_status=[200],
        )

        return AssetVersion(data)

    async def rollback_asset(
        self, asset_id: int, version_number: int
    ) -> AssetVersion:
        """
        Reverts the asset to a previous version specified.

        Args:
            asset_id: The ID of the asset to rollback.
            version_number: The version number to rollback to.

        Returns:
            The new asset version.
        """

        _, data, _ = await send_request(
            "POST",
            f"assets/v1/assets/{asset_id}/versions:rollback",
            authorization=self.__api_key,
            expected_status=[200],
            json={
                "assetVersion": f"assets/{asset_id}/versions/{version_number}"
            },
        )

        return AssetVersion(data)

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

        from .apikey import ApiKey

        return await ApiKey(self.__api_key).fetch_creator_store_product(
            asset_type, product_id
        )
