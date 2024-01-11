from .exceptions import InvalidAsset, InvalidKey, ModeratedText, rblx_opencloudException, RateLimited, ServiceUnavailable
import json, io
from typing import Union, Optional, TYPE_CHECKING
import urllib3
from enum import Enum
from datetime import datetime
from . import send_request, Operation

if TYPE_CHECKING:
    from .user import User
    from .group import Group

__all__ = (
    "AssetType",
    "Asset",
    "PendingAsset",
    "Creator"
)

class AssetType(Enum):
    """
    Enum to denote what type an asset is.
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
    Enum to denote the current moderation status of an asset.
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
    Represents an processed asset uploaded to Roblox.
    """
    
    def __init__(self,  assetObject, creator=None) -> None:
        self.id: int = assetObject.get("assetId")
        self.name: str = assetObject.get("displayName")
        self.description: str = assetObject.get("description")
        
        self.creator: Union[User, Group] = creator if creator else None
        
        self.revision_id: Optional[int] = assetObject.get("revisionId")
        self.revision_time: Optional[datetime] = datetime.fromisoformat(assetObject["revisionCreateTime"][0:26]) if assetObject.get("revisionCreateTime") else None
        self.type: AssetType = ASSET_TYPE_ENUMS.get(assetObject.get("assetType"), AssetType.Unknown)
        self.moderation_status: ModerationStatus = MODERATION_STATUS_ENUMS.get(
            assetObject.get("moderationState"), ModerationStatus.Unknown)
    
    def __repr__(self) -> str:
        return f"rblxopencloud.Asset({self.id}, name=\"{self.name}\", type={self.type})"

mimetypes = {
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
    Represents an object that can upload assets, usually a user or a group.
    """

    def __init__(self, userid, api_key, type) -> None:
        self.id: int = userid
        self.__api_key = api_key
        self.__creator_type = type
    
    def __repr__(self) -> str:
        return f"rblxopencloud.Creator({self.id})"
    
    def upload_asset(self, file: io.BytesIO, asset_type: Union[AssetType, str], name: str, description: str, expected_robux_price: int = 0) -> Operation[Asset]:
        """
        Uploads the file onto roblox as an asset with the provided name and description. It will return `rblx-open-cloud.Asset` if the asset is processed instantly, otherwise it will return `rblx-open-cloud.PendingAsset`. The following asset types and file formats are accepted:

        | Asset Type | File Formats |
        | --- | --- |
        | `rblx-open-cloud.AssetType.Decal` | `.png`, `.jpeg`, `.bmp`, `.tga` |
        | `rblx-open-cloud.AssetType.Audio` | `.mp3`, `.ogg` |
        | `rblx-open-cloud.AssetType.Model` | `.fbx` |

        The ``asset:read`` and ``asset:write`` scopes are required if authorized via `OAuth2 </oauth2>`__.

        ### Parameters
        file: io.BytesIO -The file opened in bytes to be uploaded.
        asset_type: rblx-open-cloud.AssetType - The type of asset you're uploading.
        name: str - The name of your asset.
        description: str - The description of your asset.
        expected_robux_price: int - The amount of robux expected to upload. Fails if lower than actual price.
        """

        body, contentType = urllib3.encode_multipart_formdata({
            "request": json.dumps({
                "assetType": asset_type.name if type(asset_type) == AssetType else asset_type,
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
            }),
            "fileContent": (file.name, file.read(), mimetypes.get(file.name.split(".")[-1]))
        })
        
        status_code, data, _ = send_request("POST", f"assets/v1/assets", authorization=self.__api_key,
            headers={"content-type": contentType}, expected_status=[200, 400], data=body)
        
        if status_code == 400:
            if data["message"] == "\"InvalidImage\"":
                raise InvalidAsset(f"The file is not a supported type, or is corrupted")
            
            if data["message"] == "AssetName is moderated.":
                raise ModeratedText(f"The asset's name was moderated.")
            
            if data["message"] == "AssetDescription is moderated.":
                raise ModeratedText(f"The asset's description was moderated.")
            
            raise rblx_opencloudException(body["message"] if type(body) == dict else body)

        return Operation(f"assets/v1/{data['path']}", self.__api_key, Asset, creator=self)
    
    def update_asset(self, asset_id: int, file: io.BytesIO) -> Operation[Asset]:
        """
        Updates the file for an existing assest on Roblox. It will return :class:`rblx-open-cloud.Asset` if the asset is processed instantly, otherwise it will return :class:`rblx-open-cloud.PendingAsset`. The following asset types and file formats can be updated:

        | Asset Type | File Formats |
        | --- | --- |
        | `rblx-open-cloud.AssetType.Model` | `.fbx` |

        The `asset:read` and `asset:write` scopes are required if authorized via OAuth2.

        ### Parameters
        asset_id: int - The ID of the asset to update.
        file: io.BytesIO - The file opened in bytes to be uploaded.
        """

        body, contentType = urllib3.encode_multipart_formdata({
            "request": json.dumps({
                "assetId": asset_id
            }),
            "fileContent": (file.name, file.read(), mimetypes.get(file.name.split(".")[-1]))
        })

        status_code, data, _ = send_request("PATCH", f"https://apis.roblox.com/assets/v1/assets/{asset_id}",
            authorization=self.__api_key, headers={"content-type": contentType}, expected_status=[200, 400], data=body)
        
        if status_code == 400:
            if data["message"] == "\"InvalidImage\"":
                raise InvalidAsset(f"The file is not a supported type, or is corrupted")
            
            if data["message"] == "AssetName is moderated.":
                raise ModeratedText(f"The asset's name was moderated.")
            
            if data["message"] == "AssetDescription is moderated.":
                raise ModeratedText(f"The asset's description was moderated.")
        
        return Operation(f"assets/v1/{data['path']}", self.__api_key, Asset, creator=self)
        