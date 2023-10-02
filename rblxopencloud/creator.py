from .exceptions import InvalidAsset, InvalidKey, ModeratedText, rblx_opencloudException, RateLimited, ServiceUnavailable
import json, io
from typing import Union, Optional, TYPE_CHECKING
import urllib3
from enum import Enum
from datetime import datetime
from . import user_agent, request_session

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
    Enum denoting what type a [`rblxopencloud.Asset`][rblxopencloud.Asset] is.

    Attributes:
        Unknown (0): The asset type is unknown.
        Decal (1):
        Audio (2):
        Model (3):
    """
    
    Unknown = 0
    Decal = 1
    Audio = 2
    Model = 3

class Asset():
    """
    Represents an uploaded and processed asset on Roblox.

    !!! warning
        This class isn't designed to be created by users. It is returned by [`Creator.upload_asset()`][rblxopencloud.Creator.upload_asset], and [`Creator.update_asset()`][rblxopencloud.Creator.update_asset].
    
    Attributes:
        id (int): The ID of the asset.
        type (AssetType): The type of the asset.
        name (str): The asset's name.
        description (str): The asset's description.
        creator (Union[User, Group]): The [`rblxopencloud.User`][rblxopencloud.User] and [`rblxopencloud.Group`][rblxopencloud.Group] the asset was uploaded to.
        revision_id (Optional[int]): The ID of the current revision (only for updatable assets).
        revision_time (Optional[datetime.datetime]): The timestamp the current revision was made (only for updatable assets).
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

    !!! warning
        This class isn't designed to be created by users. It is returned by [`Creator.upload_asset()`][rblxopencloud.Creator.upload_asset], and [`Creator.update_asset()`][rblxopencloud.Creator.update_asset].
    """

    def __init__(self, path, api_key, creator=None) -> None:
        self.__path = path
        self.__api_key = api_key
        self.__creator = creator
    
    def __repr__(self) -> str:
        return f"rblxopencloud.PendingAsset()"
    
    def fetch_operation(self) -> Optional[Asset]:
        """
        Checks if the asset has finished proccessing, if so returns the asset's [`rblxopencloud.Asset`][rblxopencloud.Asset] object.

        Returns:
            If it has finished processing it'll return the asset's [`rblxopencloud.Asset`][rblxopencloud.Asset] object, otherwise it'll return `None`.

        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to upload assets, or is from an invalid IP address.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        """

        response = request_session.get(f"https://apis.roblox.com/assets/v1/{self.__path}",
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
    Represents a base object that assets can be uploaded to, such as users or groups.

    !!! warning
        This class isn't designed to be created by users. It bases [`rblxopencloud.User()`][rblxopencloud.User], and [`rblxopencloud.Group()`][rblxopencloud.Group].

    Attributes:
        id (int): The user/group ID.
    """

    def __init__(self, userid, api_key, type) -> None:
        self.id: int = userid
        self.__api_key = api_key
        self.__creator_type = type
    
    def __repr__(self) -> str:
        return f"rblxopencloud.Creator({self.id})"
    
    def upload_asset(self, file: io.BytesIO, asset_type: Union[AssetType, str], name: str, description: str, expected_robux_price: int = 0) -> Union[Asset, PendingAsset]:
        """
        Uploads the file requested file onto roblox as an asset with the provided name and description. The following asset types and file formats are accepted:

        | Asset Type | File Formats |
        | --- | --- |
        | [`rblxopencloud.AssetType.Decal`][rblxopencloud.AssetType] | `.png`, `.jpeg`, `.bmp`, `.tga` |
        | [`rblxopencloud.AssetType.Audio`][rblxopencloud.AssetType] | `.mp3`, `.ogg` |
        | [`rblxopencloud.AssetType.Model`][rblxopencloud.AssetType] | `.fbx` |

        **The `asset:read` and `asset:write` scopes are required for OAuth2 authorization.**

        Example:
            You can upload a file stored on your computer like this:
            ```py
            with open('path-to/file.png', 'rb') as file:
                creator.upload_asset(file, AssetType.Decal, "Asset Name", "This is the description")
            
            if not isinstance(asset, Asset):
                while True:
                    status = asset.fetch_status()
                    if status: 
                        asset = status
                        break
            
            print(asset)
            ```
            If the asset is from hosted from a URL on the internet, you could use this:
            ```py
            import requests, io

            response = requests.get('https://example.com/file.png')
            response.raise_for_status()

            file = io.BytesIO(response.content)
            file.name = "file.png"

            creator.upload_asset(file, AssetType.Decal, "Asset Name", "This is the description")
            ```

        Args:
            file: The file opened in bytes to be uploaded.
            asset_type: The type of asset you're uploading.
            name: The name of your asset.
            description: The description of your asset.
            expected_robux_price: The amount of robux expected to upload. Fails if lower than actual price.

        Returns:
            Returns [`rblxopencloud.Asset`][rblxopencloud.Asset] if the asset is processed instantly, otherwise it will return [`rblxopencloud.PendingAsset`][rblxopencloud.PendingAsset]`.
        
        Raises:
            InvalidAsset: The file is either an unsupported type, uploaded as the wrong [`rblxopencloud.AssetType`][rblxopencloud.AssetType], or has been corrupted.
            ModeratedText: The name or description was moderated by Roblox's text filter.
            InvalidKey: The API key isn't valid, doesn't have access to upload assets, or is from an invalid IP address.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        
        !!! danger
            Avoid uploading assets to Roblox that you don't have full control over, such as AI generated assets or content created by unknown people. Assets uploaded that break Roblox's Terms of Services can get your account moderated.

            For OAuth2 developers, it has been confirmed by Roblox staff [in this DevForum post](ttps://devforum.roblox.com/t/2401354/36), that your app will not be punished if a malicious user uses it to upload Terms of Service violating content, and instead the authorizing user's account will be punished.
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
        response = request_session.post(f"https://apis.roblox.com/assets/v1/assets",
            headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "content-type": contentType, "user-agent": user_agent}, data=body)
        
        if response.status_code == 400 and response.json()["message"] == "\"InvalidImage\"": raise InvalidAsset(f"The file is not a supported type, or is corrupted")
        elif response.status_code == 400 and response.json()["message"] == "AssetName is moderated.": raise ModeratedText(f"The asset's name was moderated.")
        elif response.status_code == 400 and response.json()["message"] == "AssetDescription is moderated.": raise ModeratedText(f"The asset's description was moderated.")
        elif response.status_code == 401 or response.status_code == 403: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

        response_op = request_session.get(f"https://apis.roblox.com/assets/v1/{response.json()['path']}",
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
        Uploads the file requested file onto roblox, replacing the existing asset. The following asset types and file formats can be updated:

        | Asset Type | File Formats |
        | --- | --- |
        | [`rblxopencloud.AssetType.Model`][rblxopencloud.AssetType] | `.fbx` |

        **The `asset:read` and `asset:write` scopes are required for OAuth2 authorization.**

        Args:
            asset_id: The ID of the asset to update.
            file: The file opened in bytes to be replace the old one.

        Returns:
            Returns [`rblxopencloud.Asset`][rblxopencloud.Asset] if the asset is processed instantly, otherwise it will return [`rblxopencloud.PendingAsset`][rblxopencloud.PendingAsset]`.
        
        Raises:
            InvalidAsset: The file is either an unsupported type, uploaded as the wrong [`rblxopencloud.AssetType`][rblxopencloud.AssetType], or has been corrupted.
            ModeratedText: The name or description was moderated by Roblox's text filter.
            InvalidKey: The API key isn't valid, doesn't have access to upload assets, or is from an invalid IP address.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        
        !!! danger
            Avoid uploading assets to Roblox that you don't have full control over, such as AI generated assets or content created by unknown people. Assets uploaded that break Roblox's Terms of Services can get your account moderated.

            For OAuth2 developers, it has been confirmed by Roblox staff [in this DevForum post](ttps://devforum.roblox.com/t/2401354/36), that your app will not be punished if a malicious user uses it to upload Terms of Service violating content, and instead the authorizing user's account will be punished.
        """

        body, contentType = urllib3.encode_multipart_formdata({
            "request": json.dumps({
                "assetId": asset_id
            }),
            "fileContent": (file.name, file.read(), mimetypes.get(file.name.split(".")[-1]))
        })
        response = request_session.patch(f"https://apis.roblox.com/assets/v1/assets/{asset_id}",
            headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "content-type": contentType, "user-agent": user_agent}, data=body)

        if response.status_code == 400 and response.json()["message"] == "\"InvalidImage\"": raise InvalidAsset(f"The file is not a supported type, or is corrupted")
        elif response.status_code == 400 and response.json()["message"] == "AssetName is moderated.": raise ModeratedText(f"The asset's name was moderated.")
        elif response.status_code == 400 and response.json()["message"] == "AssetDescription is moderated.": raise ModeratedText(f"The asset's description was moderated.")
        elif response.status_code == 401 or response.status_code == 403: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

        response_op = request_session.get(f"https://apis.roblox.com/assets/v1/{response.json()['path']}",
            headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "user-agent": user_agent})
        
        if not response_op.ok:
            return PendingAsset(response_op.json()['path'], self.__api_key, self)
        else:
            info = response_op.json()
            if not info.get("done"):
                return PendingAsset(response_op.json()['path'], self.__api_key, self)
            else:
                return Asset(info["response"], self)
        