from .exceptions import *
import requests, json, io
from typing import *
import urllib3, magic

class Asset():
    def __init__(self,  id, version) -> None:
        self.id = id
        self.version = version
    
    def __repr__(self) -> str:
        return f"rblxopencloud.Asset({self.id}, version={self.version})"

class PendingAsset():
    def __init__(self, operation, api_key) -> None:
        self.__operation = operation
        self.__api_key = api_key
    
    def __repr__(self) -> str:
        return f"rblxopencloud.PendingAsset()"
    
    def fetch_status(self) -> Union[None, Asset]:
        response = requests.get(f"https://apis.roblox.com/assets/v1/create/status/{self.__operation}",
            headers={"x-api-key": self.__api_key})
        
        if response.ok:
            info = response.json()
            if info["status"] == "Pending": return None
            return Asset(info["result"]["assetInfo"]["assetId"], info["result"]["assetInfo"]["assetVersionNumber"])

class Creator():
    def __init__(self, userid: int, api_key: str) -> None:
        self.id = userid
        self.__api_key = api_key
        self.__creator_type = "User"
    
    def __repr__(self) -> str:
        return f"rblxopencloud.Creator({self.id})"
    
    def create_decal(self, file: io.BytesIO, name: str, description: str) -> Union[Asset, PendingAsset]:
        read = file.read()
        body, contentType = urllib3.encode_multipart_formdata({
            "request": json.dumps({
                "targetType": "Decal",
                "creationContext": {
                    "assetName": name,
                    "assetDescription": description,
                    "creator": {
                        "creatorType": self.__creator_type,
                        "creatorId": self.id
                    }
                }
            }),
            "fileContent": (magic.from_buffer(read, mime=True), read)
        })
        response = requests.post(f"https://apis.roblox.com/assets/v1/create",
            headers={"x-api-key": self.__api_key, "content-type": contentType}, data=body)
        
        if response.status_code == 400: raise InvalidAsset(f"The file is not a decal or is corrupted")
        elif response.status_code == 401 or response.status_code == 403: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

        response_status = requests.get(f"https://apis.roblox.com/assets/v1/create/status/{response.json()['statusUrl'].split('/')[-1]}",
            headers={"x-api-key": self.__api_key})
    
        if not response_status.ok:
            return PendingAsset(response.json()['statusUrl'].split('/')[-1], self.__api_key)
        else:
            info = response_status.json()
            if info["status"] == "Pending":
                return PendingAsset(response.json()['statusUrl'].split('/')[-1], self.__api_key)
            else:
                return Asset(info["result"]["assetInfo"]["assetId"], info["result"]["assetInfo"]["assetVersionNumber"])

    def create_audio(self, file: io.BytesIO, name: str, description: str) -> Union[Asset, PendingAsset]:
        read = file.read()
        body, contentType = urllib3.encode_multipart_formdata({
            "request": json.dumps({
                "targetType": "Audio",
                "creationContext": {
                    "assetName": name,
                    "assetDescription": description,
                    "creator": {
                        "creatorType": self.__creator_type,
                        "creatorId": self.id
                    }
                }
            }),
            "fileContent": (magic.from_buffer(read, mime=True), read)
        })
        response = requests.post(f"https://apis.roblox.com/assets/v1/create",
            headers={"x-api-key": self.__api_key, "content-type": contentType}, data=body)
        
        if response.status_code == 400: raise InvalidAsset(f"The file is not an audio or is corrupted")
        elif response.status_code == 401 or response.status_code == 403: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

        response_status = requests.get(f"https://apis.roblox.com/assets/v1/create/status/{response.json()['statusUrl'].split('/')[-1]}",
            headers={"x-api-key": self.__api_key})
    
        if not response_status.ok:
            return PendingAsset(response.json()['statusUrl'].split('/')[-1], self.__api_key)
        else:
            info = response_status.json()
            if info["status"] == "Pending":
                return PendingAsset(response.json()['statusUrl'].split('/')[-1], self.__api_key)
            else:
                return Asset(info["result"]["assetInfo"]["assetId"], info["result"]["assetInfo"]["assetVersionNumber"])

    def create_fbx(self, file: io.BytesIO, name: str, description: str) -> Union[Asset, PendingAsset]:
        read = file.read()
        body, contentType = urllib3.encode_multipart_formdata({
            "request": json.dumps({
                "targetType": "ModelFromFbx",
                "creationContext": {
                    "assetName": name,
                    "assetDescription": description,
                    "creator": {
                        "creatorType": self.__creator_type,
                        "creatorId": self.id
                    },
                    "assetId": "11326252443"
                }
            }),
            "fileContent": (magic.from_buffer(read, mime=True), read)
        })
        response = requests.post(f"https://apis.roblox.com/assets/v1/create",
            headers={"x-api-key": self.__api_key, "content-type": contentType}, data=body)
        
        if response.status_code == 400: raise InvalidAsset(f"The file is not an audio or is corrupted")
        elif response.status_code == 401 or response.status_code == 403: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

        response_status = requests.get(f"https://apis.roblox.com/assets/v1/create/status/{response.json()['statusUrl'].split('/')[-1]}",
            headers={"x-api-key": self.__api_key})
    
        if not response_status.ok:
            return PendingAsset(response.json()['statusUrl'].split('/')[-1], self.__api_key)
        else:
            info = response_status.json()
            if info["status"] == "Pending":
                return PendingAsset(response.json()['statusUrl'].split('/')[-1], self.__api_key)
            else:
                return Asset(info["result"]["assetInfo"]["assetId"], info["result"]["assetInfo"]["assetVersionNumber"])

    def update_fbx(self, id: int, file: io.BytesIO) -> Union[Asset, PendingAsset]:
        read = file.read()
        body, contentType = urllib3.encode_multipart_formdata({
            "request": json.dumps({
                "targetType": "ModelFromFbx",
                "creationContext": {
                    "assetName": "null",
                    "assetDescription": "null",
                    "creator": {
                        "creatorType": self.__creator_type,
                        "creatorId": self.id
                    },
                    "assetId": id
                }
            }),
            "fileContent": (magic.from_buffer(read, mime=True), read)
        })
        response = requests.post(f"https://apis.roblox.com/assets/v1/create",
            headers={"x-api-key": self.__api_key, "content-type": contentType}, data=body)
        
        if response.status_code == 400: raise InvalidAsset(f"The file is not an audio or is corrupted")
        elif response.status_code == 401 or response.status_code == 403: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

        response_status = requests.get(f"https://apis.roblox.com/assets/v1/create/status/{response.json()['statusUrl'].split('/')[-1]}",
            headers={"x-api-key": self.__api_key})
    
        if not response_status.ok:
            return PendingAsset(response.json()['statusUrl'].split('/')[-1], self.__api_key)
        else:
            info = response_status.json()
            if info["status"] == "Pending":
                return PendingAsset(response.json()['statusUrl'].split('/')[-1], self.__api_key)
            else:
                return Asset(info["result"]["assetInfo"]["assetId"], info["result"]["assetInfo"]["assetVersionNumber"])
        
class GroupCreator(Creator):
    def __init__(self, groupid: int, api_key: str) -> None:
        super().__init__(groupid, api_key)
        self._Creator__creator_type = "Group"
    
    def __repr__(self) -> str:
        return f"rblxopencloud.GroupCreator({self.id})"