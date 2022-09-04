import requests, json, datetime
from typing import *
import base64, hashlib, io

class rblx_opencloudException(Exception): pass
class NotFound(rblx_opencloudException): pass
class InvalidKey(rblx_opencloudException): pass
class RateLimited(rblx_opencloudException): pass
class ServiceUnavailable(rblx_opencloudException): pass

BASE_URL = "https://apis.roblox.com/datastores/v1/universes"

class EntryInfo():
    def __init__(self, version, created, updated, users, metadata) -> None:
        self.version = version
        self.created = datetime.datetime.fromisoformat(created[0:26])
        self.updated = datetime.datetime.fromisoformat(updated[0:26])
        self.users = users
        self.metadata = metadata
    
    def __repr__(self) -> str:
        return f"rblxopencloud.EntryInfo(\"{self.version}\", users={self.users}, metadata={self.metadata})"

class EntryVersion():
    def __init__(self, version, deleted, content_length, created, key_created) -> None:
        self.version = version
        self.deleted = deleted
        self.content_length = content_length
        self.created = datetime.datetime.fromisoformat(created[0:26])
        self.key_created = datetime.datetime.fromisoformat(key_created[0:26])
    
    def __repr__(self) -> str:
        return f"rblxopencloud.EntryVersion(\"{self.version}\", deleted={self.deleted}, content_length={self.content_length})"

class DataStore():
    def __init__(self, name, universe, api_key, created, scope):
        self.name = name
        self.__api_key = api_key
        self.scope = scope
        self.universe = universe
        if created: self.created = datetime.datetime.fromisoformat(created[0:26])
        else: self.created = None
    
    def __repr__(self) -> str:
        return f"rblxopencloud.DataStore(\"{self.name}\", scope=\"{self.scope}\", universe={repr(self.universe)})"
    
    def __str__(self) -> str:
        return self.name

    def list_keys(self, prefix: str="") -> list[str]:
        keys = []
        nextcursor = ""
        while True:
            response = requests.get(f"{BASE_URL}/{self.universe.id}/standard-datastores/datastore/entries?datastoreName={self.name}&scope={self.scope}&limit=100&prefix={prefix}{'&cursor='+nextcursor if nextcursor else ''}",
                headers={"x-api-key": self.__api_key})
            if response.status_code == 401 or response.status_code == 403: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
            elif response.status_code == 404: raise NotFound("The datastore you're trying to access does not exist.")
            elif response.status_code == 429: raise RateLimited("You're being rate limited.")
            elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
            
            data = response.json()
            keys += data["keys"]
            nextcursor = data.get("nextPageCursor")
            if not nextcursor: break

        response = []
        for key in keys:
            response.append(key["key"])
        return response
    
    def get(self, key: str) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        response = requests.get(f"{BASE_URL}/{self.universe.id}/standard-datastores/datastore/entries/entry?datastoreName={self.name}&scope={self.scope}&entryKey={key}",
            headers={"x-api-key": self.__api_key})

        if response.status_code == 200:
            try: metadata = json.loads(response.headers["roblox-entry-attributes"])
            except(KeyError): metadata = {}
            try: userids = json.loads(response.headers["roblox-entry-userids"])
            except(KeyError): userids = []
            
            # TODO: add a metadata class to replace this dictionary
            return json.loads(response.text), EntryInfo(response.headers["roblox-entry-version"], response.headers["roblox-entry-created-time"],
    response.headers["roblox-entry-version-created-time"], userids, metadata)
        elif response.status_code == 204: return None
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The key {key} does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

    def set(self, key: str, value: Union[str, dict, list, int, float], users:list=None, metadata:dict={}) -> EntryVersion:
        if users == None: users = []
        data = json.dumps(value)
        response = requests.post(f"{BASE_URL}/{self.universe.id}/standard-datastores/datastore/entries/entry?datastoreName={self.name}&scope={self.scope}&entryKey={key}",
            headers={"x-api-key": self.__api_key, "roblox-entry-userids": json.dumps(users), "roblox-entry-attributes": json.dumps(metadata), "content-type": "application/json",
            "content-md5": base64.b64encode(hashlib.md5(data.encode()).digest())}, data=data)
        if response.status_code == 200:
            data = json.loads(response.text)
            return EntryVersion(data["version"], data["deleted"], data["contentLength"], data["createdTime"], data["objectCreatedTime"])
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

    def increment(self, key: str, increment: Union[int, float], users:list=None, metadata:dict={}) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        if users == None: users = []

        response = requests.post(f"{BASE_URL}/{self.universe.id}/standard-datastores/datastore/entries/entry/increment?datastoreName={self.name}&scope={self.scope}&entryKey={key}&incrementBy={increment}",
            headers={"x-api-key": self.__api_key, "roblox-entry-userids": json.dumps(users), "roblox-entry-attributes": json.dumps(metadata)})
        if response.status_code == 200:
            try: metadata = json.loads(response.headers["roblox-entry-attributes"])
            except(KeyError): metadata = {}
            try: userids = json.loads(response.headers["roblox-entry-userids"])
            except(KeyError): userids = {}
            
            return json.loads(response.text), EntryInfo(response.headers["roblox-entry-version"], response.headers["roblox-entry-created-time"],
    response.headers["roblox-entry-version-created-time"], userids, metadata)
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
    
    def remove(self, key: str) -> None:
        response = requests.delete(f"{BASE_URL}/{self.universe.id}/standard-datastores/datastore/entries/entry?datastoreName={self.name}&scope={self.scope}&entryKey={key}",
            headers={"x-api-key": self.__api_key})

        if response.status_code == 204: return None
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The key {key} does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
    
    def list_versions(self, key: str, after: datetime.datetime=None, before: datetime.datetime=None, descending: bool=True) -> list[EntryVersion]:
        versions = []

        timeparm = (f"&startTime={after.isoformat()}" if after else "") + (f"&endTime={before.isoformat()}" if before else "")
        nextcursor = ""
        while True:
            response = requests.get(f"{BASE_URL}/{self.universe.id}/standard-datastores/datastore/entries/entry/versions?datastoreName={self.name}&scope={self.scope}&entryKey={key}&limit=100&sortOrder={'Descending' if descending else 'Ascending'}{'&cursor='+nextcursor if nextcursor else ''}"+timeparm,
                headers={"x-api-key": self.__api_key})
            if response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
            elif response.status_code == 404: raise NotFound("The datastore you're trying to access does not exist.")
            elif response.status_code == 429: raise RateLimited("You're being rate limited.")
            elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

            data = response.json()
            versions += data["versions"]
            nextcursor = data.get("nextPageCursor")
            if not nextcursor: break
        response = []
        for version in versions:
            response.append(EntryVersion(version["version"], version["deleted"], version["contentLength"], version["createdTime"], version["objectCreatedTime"]))
        return response   

    def get_version(self, key: str, version: str) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        response = requests.get(f"{BASE_URL}/{self.universe.id}/standard-datastores/datastore/entries/entry/versions/version?datastoreName={self.name}&scope={self.scope}&entryKey={key}&versionId={version}",
            headers={"x-api-key": self.__api_key})

        if response.status_code == 200:
            try: metadata = json.loads(response.headers["roblox-entry-attributes"])
            except(KeyError): metadata = {}
            try: userids = json.loads(response.headers["roblox-entry-userids"])
            except(KeyError): userids = []
            
            return json.loads(response.text), EntryInfo(response.headers["roblox-entry-version"], response.headers["roblox-entry-created-time"],
                response.headers["roblox-entry-version-created-time"], userids, metadata)
        elif response.status_code == 204: return None
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The key {key} does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")    

class Universe():
    def __init__(self, id: int, api_key: str):
        self.id = id
        self.__api_key = api_key
    
    def __repr__(self) -> str:
        return f"rblxopencloud.Universe({self.id})"
    
    def get_data_store(self, name: str, scope: str="global") -> DataStore:
        return DataStore(name, self, self.__api_key, None, scope)

    def list_data_stores(self, prefix: str="") -> list[DataStore]:
        datastores = []

        nextcursor = ""
        while True:
            response = requests.get(f"{BASE_URL}/{self.id}/standard-datastores?limit=100&prefix={prefix}{'&cursor='+nextcursor if nextcursor else ''}",
                headers={"x-api-key": self.__api_key})
            if response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
            elif response.status_code == 404: raise NotFound("The datastore you're trying to access does not exist.")
            elif response.status_code == 429: raise RateLimited("You're being rate limited.")
            elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
            
            data = response.json()
            datastores += data["datastores"]
            nextcursor = data.get("nextPageCursor")
            if not nextcursor: break

        response = []
        for datastore in datastores:
            response.append(DataStore(datastore["name"], self, self.__api_key, datastore["createdTime"], "global"))
        return response  
    
    def publish_message(self, topic:str, data:str):
        response = requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{self.id}/topics/{topic}",
            headers={"x-api-key": self.__api_key}, json={"message": data})
        if response.status_code == 200: return
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The place does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")  
    
    def upload_place(self, place_id:int, file: io.BytesIO, publish:bool = False) -> int:
        response = requests.post(f"https://apis.roblox.com/universes/v1/{self.id}/places/{place_id}/versions?versionType={'Saved' if not publish else 'Published'}",
            headers={"x-api-key": self.__api_key, 'Content-Type': 'application/octet-stream'}, data=file.read())
        if response.status_code == 200:
            return response.json()["versionNumber"]
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The place does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")   