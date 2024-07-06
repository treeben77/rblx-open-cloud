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

from datetime import datetime
from enum import Enum
import io
import json
from typing import Any, AsyncGenerator, Optional, TYPE_CHECKING, Union
import urllib3

from dateutil import parser

from .exceptions import HttpException, InvalidFile, ModeratedText
from .http import iterate_request, Operation, send_request

if TYPE_CHECKING:
    from .group import Group
    from .user import User

__all__ = (
    "AssetType",
    "ModerationStatus",
    "Asset",
    "AssetVersion",
    "Creator"
)

class AssetType(Enum):
    """
    Enum denoting an [`Asset`][rblxopencloud.Asset]'s asset type.

    Attributes:
        Unknown (0): The asset type is unknown/unsupported.
        Decal (1):
        Audio (2):
        Model (3):
    """
    
    Unknown = 0
    Decal = 1
    Audio = 2
    Model = 3

ASSET_TYPE_ENUMS = {
    "Decal": AssetType.Decal,
    "Audio": AssetType.Audio,
    "Model": AssetType.Model,
    "ASSET_TYPE_DECAL": AssetType.Decal,
    "ASSET_TYPE_AUDIO": AssetType.Audio,
    "ASSET_TYPE_MODEL": AssetType.Model
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
    "MODERATION_STATE_APPROVED": ModerationStatus.Approved
}

class Asset():
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
    
    def __init__(self,  data: dict, creator) -> None:
        self.id: int = data.get("assetId")
        self.name: str = data.get("displayName")
        self.description: str = data.get("description")
        self.creator: Union[Creator, User, Group] = creator
        
        self.type: AssetType = ASSET_TYPE_ENUMS.get(
            data.get("assetType"), AssetType.Unknown
        )
        
        self.moderation_status: ModerationStatus = MODERATION_STATUS_ENUMS.get(
            data.get("moderationResult", {}).get("moderationState"),
            ModerationStatus.Unknown
        )
        
        self.revision_id: Optional[int] = data.get("revisionId")
        self.revision_time: Optional[datetime] = (
            parser.parse(data["revisionCreateTime"])
            if data.get("revisionCreateTime") else None
        )

    def __repr__(self) -> str:
        return f"<rblxopencloud.Asset id={self.id} type={self.type}>"

class AssetVersion():
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
            ModerationStatus.Unknown
        )
    
    def __repr__(self) -> str:
        return f"<rblxopencloud.AssetVersion \
asset_id={self.asset_id} version_number={self.version_number}>"

ASSET_MIME_TYPES = {
    "mp3": "audio/mpeg",
    "ogg": "audio/ogg",
    "png": "image/png",
    "jpeg": "image/jpeg",
    "bmp": "image/bmp",
    "tga": "image/tga",
    "fbx": "model/fbx"
}

class Creator():
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
        
        Raises:
            InvalidKey: The API key isn't valid or doesn't have access to \
            the endpoint.
            RateLimited: You've exceeded the endpoint's rate limits.
            ServiceUnavailable: The server ran into an error.
            rblx_opencloudException: The server returned an unexpected error.
        """

        _, data, _ = await send_request("GET", f"assets/v1/assets/{asset_id}",
            authorization=self.__api_key, expected_status=[200]
        )
        
        return Asset(data, self)
    
    async def upload_asset(
            self, file: io.BytesIO, asset_type: Union[AssetType, str],
            name: str, description: str, expected_robux_price: int = 0
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
                asset_type.name if type(asset_type) == AssetType
                else asset_type
            ),
            "creationContext": {
                "creator": {
                    "userId": str(self.id),
                } if self.__creator_type == "User" else {
                    "groupId": str(self.id)
                },
                "expectedPrice": expected_robux_price
            },
            "displayName": name,
            "description": description
        }

        body, contentType = urllib3.encode_multipart_formdata({
            "request": json.dumps(payload),
            "fileContent": (
                file.name, file.read(),
                ASSET_MIME_TYPES.get(file.name.split(".")[-1])
            )
        })
        
        status, data, _ = await send_request(
            "POST", f"assets/v1/assets",
            authorization=self.__api_key, expected_status=[200, 400],
            headers={"content-type": contentType}, data=body
        )
        
        if status == 400:
            if data["message"] == "\"InvalidImage\"":
                raise InvalidFile(status, body)
            
            if data["message"] == "AssetName is moderated.":
                raise ModeratedText(status, body)
            
            if data["message"] == "AssetDescription is moderated.":
                raise ModeratedText(status, body)
            
            raise HttpException(status, data)

        return Operation(
            f"assets/v1/{data['path']}", self.__api_key, Asset, creator=self
        )
            
    async def update_asset(
            self, asset_id: int, file: io.BytesIO = None, name: str = None,
            description: str = None, expected_robux_price: int = 0
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
            "creationContext": {
                "expectedPrice": expected_robux_price
            },
            "displayName": name,
            "description": description
        }, []

        if name: field_mask.append("displayName")
        if description: field_mask.append("description")

        if file:
            body, contentType = urllib3.encode_multipart_formdata({
                "request": json.dumps(payload),
                "fileContent": (
                    file.name, file.read(),
                    ASSET_MIME_TYPES.get(file.name.split(".")[-1])
                )
            })
        else:
            body, contentType = urllib3.encode_multipart_formdata({
                "request": json.dumps(payload)
            })

        status, data, _ = await send_request(
            "PATCH", f"assets/v1/assets/{asset_id}",
            authorization=self.__api_key, expected_status=[200, 400],
            headers={"content-type": contentType}, data=body,
            params={"updateMask": ",".join(field_mask)}
        )
        
        if status == 400:
            if data["message"] == "\"InvalidImage\"":
                raise InvalidFile(status, body)
            
            if data["message"] == "AssetName is moderated.":
                raise ModeratedText(status, body)
            
            if data["message"] == "AssetDescription is moderated.":
                raise ModeratedText(status, body)
        
        return Operation(
            f"assets/v1/{data['path']}", self.__api_key, Asset, creator=self
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
        
        for entry in await iterate_request(
            "GET", f"assets/v1/assets/{asset_id}/versions", params={
                "maxPageSize": limit if limit and limit <= 50 else 50,
            }, authorization=self.__api_key, expected_status=[200],
            data_key="assetVersions", cursor_key="pageToken"
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
            "GET", f"assets/v1/assets/{asset_id}/versions/{version_number}",
            authorization=self.__api_key, expected_status=[200]
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
            "POST", f"assets/v1/assets/{asset_id}/versions:rollback",
            authorization=self.__api_key, expected_status=[200],
            json={
                "assetVersion": f"assets/{asset_id}/versions/{version_number}"
            }
        )

        return AssetVersion(data)
