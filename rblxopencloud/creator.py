from .exceptions import InvalidAsset, InvalidKey, ModeratedText, rblx_opencloudException, RateLimited, ServiceUnavailable
import requests, json, io
from typing import Union, Optional, TYPE_CHECKING
import urllib3
from enum import Enum
from datetime import datetime
from . import user_agent

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
        
        if assetObject.get("assetType") in ["Decal", "ASSET_TYPE_DECAL"]: self.type: AssetType = AssetType.Decal
        elif assetObject.get("assetType") in ["Audio", "ASSET_TYPE_AUDIO"]: self.type: AssetType = AssetType.Audio
        elif assetObject.get("assetType") in ["Model", "ASSET_TYPE_MODEL"]: self.type: AssetType = AssetType.Model
        else: self.type: AssetType = AssetType.Unknown
    
    def __repr__(self) -> str:
        return f"rblxopencloud.Asset({self.id}, name=\"{self.name}\", type={self.type})"

class PendingAsset():
    """
    Represents an asset uploaded to Roblox, but hasn't been processed yet.
    """

    def __init__(self, path, api_key, creator=None) -> None:
        self.__path = path
        self.__api_key = api_key
        self.__creator = creator
    
    def __repr__(self) -> str:
        return f"rblxopencloud.PendingAsset()"
    
    def fetch_operation(self) -> Optional[Asset]:
        """
        Checks if the asset has finished proccessing, if so returns the :class:`rblx-open-cloud.Asset` object.
        """

        response = requests.get(f"https://apis.roblox.com/assets/v1/{self.__path}",
            headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "user-agent": user_agent})
        
        if response.ok:
            info = response.json()
            if not info.get("done"): return None
            return Asset(info["response"], self.__creator)
        else:
            if response.status_code == 401 or response.status_code == 403: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
            elif response.status_code == 429: raise RateLimited("You're being rate limited.")
            elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

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
    
    def upload_asset(self, file: io.BytesIO, asset_type: Union[AssetType, str], name: str, description: str, expected_robux_price: int = 0) -> Union[Asset, PendingAsset]:
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
        response = requests.post(f"https://apis.roblox.com/assets/v1/assets",
            headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "content-type": contentType, "user-agent": user_agent}, data=body)
        
        if response.status_code == 400 and response.json()["message"] == "\"InvalidImage\"": raise InvalidAsset(f"The file is not a supported type, or is corrupted")
        elif response.status_code == 400 and response.json()["message"] == "AssetName is moderated.": raise ModeratedText(f"The asset's name was moderated.")
        elif response.status_code == 400 and response.json()["message"] == "AssetDescription is moderated.": raise ModeratedText(f"The asset's description was moderated.")
        elif response.status_code == 401 or response.status_code == 403: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

        response_op = requests.get(f"https://apis.roblox.com/assets/v1/{response.json()['path']}",
            headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "user-agent": user_agent})
        
        if not response_op.ok:
            return PendingAsset(response_op.json()['path'], self.__api_key, self)
        else:
            info = response_op.json()
            if not info.get("done"):
                return PendingAsset(response_op.json()['path'], self.__api_key, self)
            else:
                return Asset(info["response"], self)
    
    def update_asset(self, asset_id: int, file: io.BytesIO) -> Union[Asset, PendingAsset]:
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
        response = requests.patch(f"https://apis.roblox.com/assets/v1/assets/{asset_id}",
            headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "content-type": contentType, "user-agent": user_agent}, data=body)

        if response.status_code == 400 and response.json()["message"] == "\"InvalidImage\"": raise InvalidAsset(f"The file is not a supported type, or is corrupted")
        elif response.status_code == 400 and response.json()["message"] == "AssetName is moderated.": raise ModeratedText(f"The asset's name was moderated.")
        elif response.status_code == 400 and response.json()["message"] == "AssetDescription is moderated.": raise ModeratedText(f"The asset's description was moderated.")
        elif response.status_code == 401 or response.status_code == 403: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

        response_op = requests.get(f"https://apis.roblox.com/assets/v1/{response.json()['path']}",
            headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "user-agent": user_agent})
        
        if not response_op.ok:
            return PendingAsset(response_op.json()['path'], self.__api_key, self)
        else:
            info = response_op.json()
            if not info.get("done"):
                return PendingAsset(response_op.json()['path'], self.__api_key, self)
            else:
                return Asset(info["response"], self)
        