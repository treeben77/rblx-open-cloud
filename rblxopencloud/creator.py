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
from typing import Iterable, Optional, TYPE_CHECKING, Union
import urllib3

from dateutil import parser

from . import Operation, send_request
from .exceptions import InvalidAsset, ModeratedText, rblx_opencloudException

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
        id (int): The asset's ID.
        name (str): The filtered name of the asset.
        description (str): The filtered description of the asset.
        type (AssetType): The asset's type.
        creator (Union[Creator, User, Group]): The user, group, or creator\
        which uploaded the asset.
        moderation_status (ModerationStatus): The asset's current moderation\
        status.
        revision_id (Optional[int]): The ID of the current revision of the\
        asset. *Will be `None` if the asset type does not support updating.*
        revision_time (Optional[datetime]): The time the current\
        revision of the asset was created. *Will be `None` if the asset type\
        does not support updating.*
    """
    
    def __init__(self,  data: dict, creator) -> None:
        self.id: int = data.get("assetId")
        self.name: str = data.get("displayName")
        self.description: str = data.get("description")
        self.creator: Union[Creator, User, Group] = creator
        
        self.type: AssetType = ASSET_TYPE_ENUMS.get(
            data.get("assetType"), AssetType.Unknown)
        
        self.moderation_status: ModerationStatus = MODERATION_STATUS_ENUMS.get(
            data.get("moderationResult", {}).get("moderationState"),
            ModerationStatus.Unknown)
        
        self.revision_id: Optional[int] = data.get("revisionId")
        self.revision_time: Optional[datetime] = (
            parser.parse(data["revisionCreateTime"])
            if data.get("revisionCreateTime") else None
        )

    def __repr__(self) -> str:
        return f"<rblxopencloud.Asset id={self.id}, type={self.type}>"

class AssetVersion():
    """
    Represents a version of an asset uploaded on to Roblox.

    Attributes:
        id (int): This asset version's revision ID.
        asset_id (int): The asset's ID.
        creator (Union[Creator, User, Group]): The user, group, or creator\
        which uploaded the asset.
        moderation_status (ModerationStatus): The moderation status of this\
        version.
    """

    def __init__(self, data, creator) -> None:
        self.id: int = data["path"].split("/")[3]

        self.asset_id: int = data["path"].split("/")[1]
        self.creator: Union[Creator, User, Group] = creator

        self.moderation_status: ModerationStatus = MODERATION_STATUS_ENUMS.get(
            data.get("moderationResult", {}).get("moderationState"),
            ModerationStatus.Unknown)
    
    def __repr__(self) -> str:
        return f"<rblxopencloud.AssetVersion\
 asset_id={self.asset_id}, id={self.id}>"

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
    
    def fetch_asset(self, asset_id: int) -> Asset:
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

        _, data, _ = send_request("GET", f"assets/v1/assets/{asset_id}",
            authorization=self.__api_key, expected_status=[200]
        )
        
        return Asset(data, self)
    
    def upload_asset(
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

        **The `asset:read` and `asset:write` scopes are required for OAuth2 \
        authorization.**

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
        
        Raises:
            InvalidAsset: The file is either an unsupported type, uploaded as \
            the wrong type, or has been corrupted.
            ModeratedText: The name or description was filtered.
            InvalidKey: The API key isn't valid, doesn't have access to \
            upload assets, or is from an invalid IP address.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are \
            unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        
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
            "assetType": (asset_type.name if type(asset_type) == AssetType
                            else asset_type),
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
            "fileContent": (file.name, file.read(), ASSET_MIME_TYPES.get(
                file.name.split(".")[-1]))
        })
        
        status, data, _ = send_request("POST", f"assets/v1/assets",
            authorization=self.__api_key, data=body,
            headers={"content-type": contentType}, expected_status=[200, 400]
        )
        
        if status == 400:
            if data["message"] == "\"InvalidImage\"":
                raise InvalidAsset(f"The file is corrupted or not supported.")
            
            if data["message"] == "AssetName is moderated.":
                raise ModeratedText(f"The asset's name was moderated.")
            
            if data["message"] == "AssetDescription is moderated.":
                raise ModeratedText(f"The asset's description was moderated.")
            
            raise rblx_opencloudException(
                body["message"] if type(body) == dict else body
            )

        return Operation(f"assets/v1/{data['path']}", self.__api_key,
            Asset, creator=self)
            
    def update_asset(
            self, asset_id: int, file: io.BytesIO
        ) -> Operation[Asset]:
        """
        Updates an asset on Roblox with the provided file. The following \
        asset types are currently supported:

        | Asset Type | File Formats |
        | --- | --- |
        | Model | `.fbx` |

        Args:
            file: The file opened in bytes to upload.
            asset_id: The ID of the asset to update.

        Returns:
            Returns a [`Operation`][rblxopencloud.Operation] for the asset \
            update operation where `T` is an [`Asset`][rblxopencloud.Asset].
        
        Raises:
            InvalidAsset: The file is either an unsupported type, uploaded as \
            the wrong type, or has been corrupted.
            ModeratedText: The name or description was filtered.
            InvalidKey: The API key isn't valid, doesn't have access to \
            upload assets, or is from an invalid IP address.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are \
            unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        
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
            "assetId": asset_id
        }

        body, contentType = urllib3.encode_multipart_formdata({
            "request": json.dumps(payload),
            "fileContent": (file.name, file.read(), ASSET_MIME_TYPES.get(
                file.name.split(".")[-1]))
        })

        status, data, _ = send_request("PATCH", f"assets/v1/assets/{asset_id}",
            authorization=self.__api_key, data=body,
            headers={"content-type": contentType}, expected_status=[200, 400]
        )
        
        if status == 400:
            if data["message"] == "\"InvalidImage\"":
                raise InvalidAsset(f"The file is corrupted or not supported.")
            
            if data["message"] == "AssetName is moderated.":
                raise ModeratedText(f"The asset's name was moderated.")
            
            if data["message"] == "AssetDescription is moderated.":
                raise ModeratedText(f"The asset's description was moderated.")
        
        return Operation(f"assets/v1/{data['path']}", self.__api_key,
            Asset, creator=self)
    
    def list_asset_versions(
            self, asset_id: int, limit: Optional[int]=None
        ) -> Iterable[Asset]:
        """
        """
        
        nextcursor = ""
        yields = 0
        while limit == None or yields < limit:
            _, data, _ = send_request("GET",
                f"assets/v1/assets/{asset_id}/versions", params={
                    "maxPageSize":
                        limit-yields if limit and limit-yields <= 50 else 50,
                    "pageToken": nextcursor if nextcursor else None
                }, authorization=self.__api_key, expected_status=[200]
            )

            for version in data["assetVersions"]:
                yields += 1
                yield AssetVersion(version, self)
                if limit and yields >= limit: break
            
            nextcursor = data.get("nextPageToken")
            if not nextcursor: break