import hashlib, json, requests
import dateutil.parser as dp

base_url = "https://apis.roblox.com/datastores/v1/universes"
api_key = None

class rblx_opencloudException(Exception): pass
class NotFound(rblx_opencloudException): pass
class InvalidKey(rblx_opencloudException): pass
class RateLimited(rblx_opencloudException): pass
class ServiceUnavailable(rblx_opencloudException): pass

class DataStore():
    def __init__(self, name, universe, created):
        self.name = name
        self.universe = universe
        if created: self.created = dp.parse(created).timestamp()
        else: self.created = None
    
    def __repr__(self) -> str:
        return f"DataStore({self.name})"

    def listKeys(self, prefix="") -> list:
        keys = []
        nextcursor = ""
        while True:
            cursorparm = ""
            if nextcursor != "": cursorparm = "&cursor=" + nextcursor
            response = requests.get(f"{base_url}/{self.universe}/standard-datastores/datastore/entries?datastoreName={self.name}&limit=100&prefix={prefix}"+cursorparm,
                headers={"x-api-key": api_key})
            if response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
            elif response.status_code == 404: raise NotFound("The datastore you're trying to access does not exist.")
            elif response.status_code == 429: raise RateLimited("You're being rate limited.")
            elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
            data = response.json()
            keys += data["keys"]
            try: nextcursor = data["nextPageCursor"]
            except(KeyError): break
        response = []
        for key in keys:
            response.append(key["key"])
        return response
    
    def get(self, key) -> tuple[str, dict]:
        response = requests.get(f"{base_url}/{self.universe}/standard-datastores/datastore/entries/entry?datastoreName={self.name}&entryKey={key}",
            headers={"x-api-key": api_key})

        if response.status_code == 200:
            try: metadata = json.loads(response.headers["roblox-entry-attributes"])
            except(KeyError): metadata = {}
            return response.text, {
                "version": response.headers["roblox-entry-version"],
                "created": dp.parse(response.headers["roblox-entry-created-time"]).timestamp(),
                "updated": dp.parse(response.headers["roblox-entry-version-created-time"]).timestamp(),
                "userids": json.loads(response.headers["roblox-entry-userids"]),
                "metadata": metadata
            }
        elif response.status_code == 204: return None
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The key {key} does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")

class DataStoreService():
    def __init__(self, universe):
        self.universe = universe
    
    def listDataStores(self, prefix="", limit=None) -> list[DataStore]:
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
            data = response.json()
            datastores += data["datastores"]
            if data["nextPageCursor"]:
                nextcursor = data["nextPageCursor"]
            else: break
        response = []
        for datastore in datastores:
            response.append(DataStore(datastore["name"], self.universe, datastore["createdTime"]))
        return response
    
    def getDataStore(self, name) -> DataStore:
        return DataStore(name, self.universe, None)