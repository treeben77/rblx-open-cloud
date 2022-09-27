import requests, json, datetime
from typing import *
import base64, hashlib, io

class rblx_opencloudException(Exception): pass
class NotFound(rblx_opencloudException): pass
class InvalidKey(rblx_opencloudException): pass
class RateLimited(rblx_opencloudException): pass
class ServiceUnavailable(rblx_opencloudException): pass

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
    def __init__(self, version, deleted, content_length, created, key_created, datastore, key, scope) -> None:
        self.version = version
        self.deleted = deleted
        self.content_length = content_length
        self.created = datetime.datetime.fromisoformat(created[0:26])
        self.key_created = datetime.datetime.fromisoformat(key_created[0:26])
        self.__datastore = datastore
        self.__key = key
    
    def get_value(self) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        if self.__datastore.scope:
            return self.__datastore.get_version(self.__key, self.version)
        else:
            return self.__datastore.get_version(f"{self.__scope}/{self.__key}", self.version)

    def __repr__(self) -> str:
        return f"rblxopencloud.EntryVersion(\"{self.version}\", content_length={self.content_length})"

class ListedEntry():
    def __init__(self, key, scope) -> None:
        self.key = key
        self.scope = scope
    
    def __repr__(self) -> str:
        return f"rblxopencloud.ListedEntry(\"{self.key}\", scope=\"{self.scope}\")"

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

    def list_keys(self, prefix: str="") -> Iterable[ListedEntry]:
        nextcursor = ""
        while True:
            response = requests.get(f"https://apis.roblox.com/datastores/v1/universes/{self.universe.id}/standard-datastores/datastore/entries",
                headers={"x-api-key": self.__api_key}, params={
                "datastoreName": self.name,
                "scope": self.scope,
                "AllScopes": not self.scope,
                "limit": 100,
                "prefix": prefix,
                "cursor": nextcursor if nextcursor else None
            })
            if response.status_code == 401 or response.status_code == 403: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
            elif response.status_code == 404: raise NotFound("The datastore you're trying to access does not exist.")
            elif response.status_code == 429: raise RateLimited("You're being rate limited.")
            elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
            
            data = response.json()
            for key in data["keys"]:
                yield ListedEntry(key["key"], key["scope"])
            nextcursor = data.get("nextPageCursor")
            if not nextcursor: break
    
    def get(self, key: str) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        try:
            if not self.scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("a scope and key seperated by a forward slash is required for DataStore without a scope.")
        response = requests.get(f"https://apis.roblox.com/datastores/v1/universes/{self.universe.id}/standard-datastores/datastore/entries/entry",
            headers={"x-api-key": self.__api_key}, params={
                "datastoreName": self.name,
                "scope": self.scope if self.scope else scope,
                "entryKey": key
            })

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

    def set(self, key: str, value: Union[str, dict, list, int, float], users:list=None, metadata:dict={}) -> EntryVersion:
        try:
            if not self.scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("a scope and key seperated by a forward slash is required for DataStore without a scope.")
        if users == None: users = []
        data = json.dumps(value)

        response = requests.post(f"https://apis.roblox.com/datastores/v1/universes/{self.universe.id}/standard-datastores/datastore/entries/entry",
            headers={"x-api-key": self.__api_key, "roblox-entry-userids": json.dumps(users), "roblox-entry-attributes": json.dumps(metadata),
            "content-md5": base64.b64encode(hashlib.md5(data.encode()).digest())}, data=data, params={
                "datastoreName": self.name,
                "scope": self.scope if self.scope else scope,
                "entryKey": key
            })
        
        if response.status_code == 200:
            data = json.loads(response.text)
            return EntryVersion(data["version"], data["deleted"], data["contentLength"], data["createdTime"], data["objectCreatedTime"], self, key, self.scope if self.scope else scope)
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

    def increment(self, key: str, increment: Union[int, float], users:list=None, metadata:dict={}) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        try:
            if not self.scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("a scope and key seperated by a forward slash is required for DataStore without a scope.")
        if users == None: users = []

        response = requests.post(f"https://apis.roblox.com/datastores/v1/universes/{self.universe.id}/standard-datastores/datastore/entries/entry/increment",
            headers={"x-api-key": self.__api_key, "roblox-entry-userids": json.dumps(users), "roblox-entry-attributes": json.dumps(metadata)}, params={
                "datastoreName": self.name,
                "scope": self.scope if self.scope else scope,
                "entryKey": key,
                "incrementBy": increment
            })

        if response.status_code == 200:
            try: metadata = json.loads(response.headers["roblox-entry-attributes"])
            except(KeyError): metadata = {}
            try: userids = json.loads(response.headers["roblox-entry-userids"])
            except(KeyError): userids = []
            
            return json.loads(response.text), EntryInfo(response.headers["roblox-entry-version"], response.headers["roblox-entry-created-time"],
    response.headers["roblox-entry-version-created-time"], userids, metadata)
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
    
    def remove(self, key: str) -> None:
        try:
            if not self.scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("a scope and key seperated by a forward slash is required for DataStore without a scope.")
        response = requests.delete(f"https://apis.roblox.com/datastores/v1/universes/{self.universe.id}/standard-datastores/datastore/entries/entry",
            headers={"x-api-key": self.__api_key}, params={
                "datastoreName": self.name,
                "scope": self.scope if self.scope else scope,
                "entryKey": key
            })

        if response.status_code == 204: return None
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The key {key} does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
    
    def list_versions(self, key: str, after: datetime.datetime=None, before: datetime.datetime=None, descending: bool=True) -> Iterable[EntryVersion]:
        try:
            if not self.scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("a scope and key seperated by a forward slash is required for DataStore without a scope.")
        nextcursor = ""
        while True:
            response = requests.get(f"https://apis.roblox.com/datastores/v1/universes/{self.universe.id}/standard-datastores/datastore/entries/entry/versions",
                headers={"x-api-key": self.__api_key}, params={
                    "datastoreName": self.name,
                    "scope": self.scope if self.scope else scope,
                    "entryKey": key,
                    "limit": 100,
                    "sortOrder": "Descending" if descending else "Ascending",
                    "cursor": nextcursor if nextcursor else None,
                    "startTime": after.isoformat() if after else None,
                    "endTime": before.isoformat() if before else None
                })
            
            if response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
            elif response.status_code == 404: raise NotFound("The datastore you're trying to access does not exist.")
            elif response.status_code == 429: raise RateLimited("You're being rate limited.")
            elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

            data = response.json()
            for version in data["versions"]:
                yield EntryVersion(version["version"], version["deleted"], version["contentLength"], version["createdTime"], version["objectCreatedTime"], self, key, self.scope if self.scope else scope)
            nextcursor = data.get("nextPageCursor")
            if not nextcursor: break

    def get_version(self, key: str, version: str) -> tuple[Union[str, dict, list, int, float], EntryInfo]:
        try:
            if not self.scope: scope, key = key.split("/", maxsplit=1)
        except(ValueError):
            raise ValueError("a scope and key seperated by a forward slash is required for DataStore without a scope.") 
        response = requests.get(f"https://apis.roblox.com/datastores/v1/universes/{self.universe.id}/standard-datastores/datastore/entries/entry/versions/version",
            headers={"x-api-key": self.__api_key}, params={
                "datastoreName": self.name,
                "scope": self.scope if self.scope else scope,
                "entryKey": key,
                "versionId": version
            })

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
    
    def get_data_store(self, name: str, scope: Union[str, None]="global") -> DataStore:
        return DataStore(name, self, self.__api_key, None, scope)

    def list_data_stores(self, prefix: str="", scope: str="global") -> list[DataStore]:
        nextcursor = ""
        while True:
            response = requests.get(f"https://apis.roblox.com/datastores/v1/universes/{self.id}/standard-datastores",
                headers={"x-api-key": self.__api_key}, params={
                    "limit": 100,
                    "prefix": prefix,
                    "cursor": nextcursor if nextcursor else None
                })
            if response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
            elif response.status_code == 404: raise NotFound("The datastore you're trying to access does not exist.")
            elif response.status_code == 429: raise RateLimited("You're being rate limited.")
            elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
            
            data = response.json()
            for datastore in data["datastores"]:
                yield DataStore(datastore["name"], self, self.__api_key, datastore["createdTime"], scope)
            nextcursor = data.get("nextPageCursor")
            if not nextcursor: break
    
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
        response = requests.post(f"https://apis.roblox.com/universes/v1/{self.id}/places/{place_id}/versions",
            headers={"x-api-key": self.__api_key, 'Content-Type': 'application/octet-stream'}, data=file.read(), params={
                "versionType": "Published" if publish else "Saved"
            })
        if response.status_code == 200:
            return response.json()["versionNumber"]
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The place does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")   