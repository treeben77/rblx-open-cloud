import hashlib, json, requests, base64
from typing import Union
import dateutil.parser as dp
import datetime
base_url = "https://apis.roblox.com/datastores/v1/universes"
api_key = None

class rblx_opencloudException(Exception): pass
class NotFound(rblx_opencloudException): pass
class InvalidKey(rblx_opencloudException): pass
class RateLimited(rblx_opencloudException): pass
class ServiceUnavailable(rblx_opencloudException): pass

class DataStore():
    def __init__(self, name, universe, created, scope="global"):
        self.name = name
        self.scope = scope
        self.universe = universe
        if created: self.created = dp.parse(created).timestamp()
        else: self.created = None
    
    def __repr__(self) -> str:
        return f"DataStore({self.name})"

    def listKeys(self, prefix:str="") -> list:
        keys = []
        nextcursor = ""
        while True:
            cursorparm = ""
            if nextcursor != "": cursorparm = "&cursor=" + nextcursor
            response = requests.get(f"{base_url}/{self.universe}/standard-datastores/datastore/entries?datastoreName={self.name}&scope={self.scope}&limit=100&prefix={prefix}"+cursorparm,
                headers={"x-api-key": api_key})
            if response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
            elif response.status_code == 404: raise NotFound("The datastore you're trying to access does not exist.")
            elif response.status_code == 429: raise RateLimited("You're being rate limited.")
            elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
            data = response.json()
            keys += data["keys"]
            try: nextcursor = data["nextPageCursor"]
            except(KeyError): break
        response = []
        for key in keys:
            response.append(key["key"])
        return response
    
    def get(self, key:str) -> tuple[Union[str, dict, list, int, float], dict]:
        response = requests.get(f"{base_url}/{self.universe}/standard-datastores/datastore/entries/entry?datastoreName={self.name}&scope={self.scope}&entryKey={key}",
            headers={"x-api-key": api_key})

        if response.status_code == 200:
            try: metadata = json.loads(response.headers["roblox-entry-attributes"])
            except(KeyError): metadata = {}
            try: userids = json.loads(response.headers["roblox-entry-userids"])
            except(KeyError): userids = {}
            
            return json.loads(response.text), {
                "version": response.headers["roblox-entry-version"],
                "created": dp.parse(response.headers["roblox-entry-created-time"]).timestamp(),
                "updated": dp.parse(response.headers["roblox-entry-version-created-time"]).timestamp(),
                "userids": userids,
                "metadata": metadata
            }
        elif response.status_code == 204: return None
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The key {key} does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

    def set(self, key:str, value:Union[str, dict, list, int, float], users:list=None, metadata:dict={}) -> str:
        if users == None: users = []
        data = json.dumps(value)
        response = requests.post(f"{base_url}/{self.universe}/standard-datastores/datastore/entries/entry?datastoreName={self.name}&scope={self.scope}&entryKey={key}",
            headers={"x-api-key": api_key, "roblox-entry-userids": json.dumps(users), "roblox-entry-attributes": json.dumps(metadata), "content-type": "application/json",
            "content-md5": base64.b64encode(hashlib.md5(data.encode()).digest())}, data=data)
        if response.status_code == 200:
            return response.json()["version"]
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")

    def increment(self, key:str, increment:Union[int, float], users:list=None, metadata:dict={}) -> str:
        if users == None: users = []

        response = requests.post(f"{base_url}/{self.universe}/standard-datastores/datastore/entries/entry/increment?datastoreName={self.name}&scope={self.scope}&entryKey={key}&incrementBy={increment}",
            headers={"x-api-key": api_key, "roblox-entry-userids": json.dumps(users), "roblox-entry-attributes": json.dumps(metadata)})
        if response.status_code == 200:
            try: metadata = json.loads(response.headers["roblox-entry-attributes"])
            except(KeyError): metadata = {}
            try: userids = json.loads(response.headers["roblox-entry-userids"])
            except(KeyError): userids = {}
            
            return json.loads(response.text), {
                "version": response.headers["roblox-entry-version"],
                "created": dp.parse(response.headers["roblox-entry-created-time"]).timestamp(),
                "updated": dp.parse(response.headers["roblox-entry-version-created-time"]).timestamp(),
                "userids": userids,
                "metadata": metadata
            }
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
    
    def remove(self, key:str) -> None:
        response = requests.delete(f"{base_url}/{self.universe}/standard-datastores/datastore/entries/entry?datastoreName={self.name}&scope={self.scope}&entryKey={key}",
            headers={"x-api-key": api_key})

        if response.status_code == 204: return None
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The key {key} does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
    
    def listVersions(self, key:str, after:int=0, before:int=0, descending:bool=True) -> list[dict]:
        versions = []

        timeparm = "" + (f"&startTime={datetime.datetime.utcfromtimestamp(after).isoformat()}" if after > 0 else "") + (f"&endTime={datetime.datetime.utcfromtimestamp(before).isoformat()}" if before > 0 else "")
        nextcursor = ""
        while True:
            cursorparm = ""
            if nextcursor != "": cursorparm = "&cursor=" + nextcursor
            response = requests.get(f"{base_url}/{self.universe}/standard-datastores/datastore/entries/entry/versions?datastoreName={self.name}&scope={self.scope}&entryKey={key}&limit=100&sortOrder={'Descending' if descending else 'Ascending'}&"+cursorparm+timeparm,
                headers={"x-api-key": api_key})
            if response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
            elif response.status_code == 404: raise NotFound("The datastore you're trying to access does not exist.")
            elif response.status_code == 429: raise RateLimited("You're being rate limited.")
            elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
            data = response.json()
            versions += data["versions"]
            if data["nextPageCursor"]:
                nextcursor = data["nextPageCursor"]
            else: break
        response = []
        for version in versions:
            response.append({
                "version": version["version"],
                "timestamp": version["createdTime"],
                "content_length": version["contentLength"]
            })
        return response   

    def getVersion(self, key:str, version:str) -> tuple[Union[str, dict, list, int, float], dict]:
        response = requests.get(f"{base_url}/{self.universe}/standard-datastores/datastore/entries/entry/versions/version?datastoreName={self.name}&scope={self.scope}&entryKey={key}&versionId={version}",
            headers={"x-api-key": api_key})

        if response.status_code == 200:
            try: metadata = json.loads(response.headers["roblox-entry-attributes"])
            except(KeyError): metadata = {}
            try: userids = json.loads(response.headers["roblox-entry-userids"])
            except(KeyError): userids = []
            
            return json.loads(response.text), {
                "version": response.headers["roblox-entry-version"],
                "created": dp.parse(response.headers["roblox-entry-created-time"]).timestamp(),
                "updated": dp.parse(response.headers["roblox-entry-version-created-time"]).timestamp(),
                "userids": userids,
                "metadata": metadata
            }
        elif response.status_code == 204: return None
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The key {key} does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")    

class PlacePublishing():
    def __init__(self, universe:int):
        self.universe = universe
    
    def savePlace(self, place:int, file):
        response = requests.post(f"https://apis.roblox.com/universes/v1/{self.universe}/places/{place}/versions?versionType=Saved",
            headers={"x-api-key": api_key, 'Content-Type': 'application/octet-stream'}, data=file.read())
        if response.status_code == 200:
            return response.json()["versionNumber"]
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The place does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")    
        
    def publishPlace(self, place:int, file):
        response = requests.post(f"https://apis.roblox.com/universes/v1/{self.universe}/places/{place}/versions?versionType=Published",
            headers={"x-api-key": api_key, 'Content-Type': 'application/octet-stream'}, data=file.read())
        if response.status_code == 200:
            return response.json()["versionNumber"]
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The place does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")    
        

class DataStoreService():
    def __init__(self, universe:int):
        self.universe = universe
    
    def listDataStores(self, prefix:str="") -> list[DataStore]:
        datastores = []
        nextcursor = ""
        while True:
            cursorparm = ""
            if nextcursor != "": cursorparm = "&cursor=" + nextcursor
            response = requests.get(f"{base_url}/{self.universe}/standard-datastores?limit=100&prefix={prefix}"+cursorparm,
                headers={"x-api-key": api_key})
            if response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
            elif response.status_code == 404: raise NotFound("The datastore you're trying to access does not exist.")
            elif response.status_code == 429: raise RateLimited("You're being rate limited.")
            elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
            data = response.json()
            datastores += data["datastores"]
            if data["nextPageCursor"]:
                nextcursor = data["nextPageCursor"]
            else: break
        response = []
        for datastore in datastores:
            response.append(DataStore(datastore["name"], self.universe, datastore["createdTime"]))
        return response
    
    def getDataStore(self, name:str, scope:str="global") -> DataStore:
        return DataStore(name, self.universe, None, scope)

class MessagingService():
    def __init__(self, universe:int):
        self.universe = universe
    
    def publish(self, topic:str, data:str):
        response = requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{self.universe}/topics/{topic}",
            headers={"x-api-key": api_key}, json={"message": data})
        if response.status_code == 200: return
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The place does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")  