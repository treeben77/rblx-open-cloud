from .exceptions import rblx_opencloudException, InvalidKey, NotFound, RateLimited, ServiceUnavailable
import io
from typing import Optional, Iterable, Union, AsyncIterator
from .datastore import DataStore, OrderedDataStore
from . import user_agent, request_session, preform_request

__all__ = (
    "Experience",
)

class Experience():
    """
    Represents an experience/game object on Roblox. This class allows interaction with an experience's data stores, messaging service, and uploading place files.

    ### Example
    ```py
    experience = rblxopencloud.Experience(123456789, "your-api-key")
    ```
    ### Paramaters
    id: int - The experience's (aka universe's) ID. See [this Roblox documentation](https://create.roblox.com/docs/cloud/open-cloud/data-store-api-handling#universe-id) to find yours.
    api_key: str - :param str api_key: Your API key created from [Creator Dashboard](https://create.roblox.com/credentials) with access to this experience.
    """

    def __init__(self, id: int, api_key: str):
        self.id: int = id
        self.owner = None
        self.__api_key: str = api_key
    
    def __repr__(self) -> str:
        return f"rblxopencloud.Experience({self.id})"
    
    def get_data_store(self, name: str, scope: Optional[str]="global") -> DataStore:
        """
        Creates a `rblx-open-cloud.DataStore` which allows interaction with a data store from the experience. `DataStore.created` will be `None`.

        Lua equivalent: [DataStoreService:GetDataStore()](https://create.roblox.com/docs/reference/engine/classes/DataStoreService#GetDataStore)
        ### Example
        ```py
        data_store = Experience.get_data_store(name="playerExperience", scope="global")
        ```
        ### Parameters
        name: str - The data store name.
        scope: Optional[str] - The data store scope. Defaults to global, and can be `None` for key syntax like `scope/key`.
        """
        return DataStore(name, self, self.__api_key, None, scope)
    
    def get_ordered_data_store(self, name: str, scope: Optional[str]="global") -> OrderedDataStore:
        """
        Creates a `rblx-open-cloud.OrderedDataStore` which allows interaction with an ordered data store from the experience.

        Lua equivalent: [DataStoreService:GetOrderedDataStore()](https://create.roblox.com/docs/reference/engine/classes/DataStoreService#GetOrderedDataStore)
        ### Example
        ```py
        data_store = Experience.get_ordered_data_store(name="playerWins", scope="global")
        ```
        ### Parameters
        name: str - The data store name.
        scope: Optional[str] - The data store scope. Defaults to global, and can be `None` for key syntax like `scope/key`.
        """
        return OrderedDataStore(name, self, self.__api_key, scope)

    async def list_data_stores(self, prefix: Optional[str]="", limit: Optional[int]=None, scope: Optional[Union[str, None]]="global") -> AsyncIterator[DataStore]:
        """
        Interates `rblx-open-cloud.DataStore` for all of the Data Stores in the experience.

        Lua equivalent: [DataStoreService:ListDataStoresAsync()](https://create.roblox.com/docs/reference/engine/classes/DataStoreService#ListDataStoresAsync)
        ### Example
        ```py
        for datastore in experience.list_data_stores():
            print(datastore)
        ```
        You can get the data stores in a list like this:
        ```py
        list(experience.list_data_stores())
        ```
        ### Parameters
        prefix: Optional[str] - Only return Data Stores with names starting with this value.
        limit: Optional[int] - The maximum number of Data Stores to iterate.
        scope: Optional[str] - The scope for all data stores. Defaults to global, and can be `None` for key syntax like `scope/key`.
        """
        nextcursor = ""
        yields = 0
        while limit == None or yields < limit:
            status, data, headers = await preform_request("GET", f"datastores/v1/universes/{self.id}/standard-datastores", authorization=self.__api_key, params={
                "prefix": prefix,
                "cursor": nextcursor if nextcursor else None
            })

            if status == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
            elif status == 404: raise NotFound("The datastore you're trying to access does not exist.")
            elif status == 429: raise RateLimited("You're being rate limited.")
            elif status >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
            elif not 200 <= status < 300: raise rblx_opencloudException(f"Unexpected HTTP {status}")
            
            data = data
            for datastore in data["datastores"]:
                yields += 1
                yield DataStore(datastore["name"], self, self.__api_key, datastore["createdTime"], scope)
                if limit == None or yields >= limit: break
            nextcursor = data.get("nextPageCursor")
            if not nextcursor: break
    
    async def publish_message(self, topic: str, data: str) -> None:
        """
        Publishes a message to live game servers that can be recieved with [MessagingService](https://create.roblox.com/docs/reference/engine/classes/MessagingService).

        The `universe-messaging-service:publish` scope is required for OAuth2 authorization.

        Messages sent by Open Cloud with only be recieved by live servers. Studio won't recieve thesse messages.

        ### Example
        ```py
        experience.publish_message("exampleTopic", "Hello World!")
        ```
        ### Parameters
        topic: str - The topic to send the message in
        data: str - The message to send. Open Cloud does not support sending dictionaries/tables with publishing messages. You'll have to json encode it before sending it, and decode it in Roblox.
        """
        
        status, data, headers = await preform_request("POST", f"messaging-service/v1/universes/{self.id}/topics/{topic}", authorization=self.__api_key, json={"message": data})

        if status == 200: return
        elif status == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif status == 404: raise NotFound(f"The place does not exist.")
        elif status == 429: raise RateLimited("You're being rate limited.")
        elif status >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {status}")  
    
    async def upload_place(self, place_id:int, file: io.BytesIO, publish: Optional[bool] = False) -> int:
        """
        Uploads the place file to Roblox and returns the new version number.

        ### Example
        ```py
        with open("example.rbxl", "rb") as file:
            experience.upload_place(1234, file, publish=False)
        ```
        ### Parameters
        place_id: int - The place ID to upload the file to.
        file: io.BytesIO - The file to upload. The file should be opened in bytes.
        publish: Optional[bool] - Wether to publish the place as well. Defaults to `False`.
        """

        status, data, headers = await preform_request("POST", f"universes/v1/{self.id}/places/{place_id}/versions", authorization=self.__api_key,
            headers={'content-type': 'application/octet-stream'}, data=file.read(), params={"versionType": "Published" if publish else "Saved"})

        if status == 200:
            return data["versionNumber"]
        elif status == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif status == 404: raise NotFound(f"The place does not exist.")
        elif status == 429: raise RateLimited("You're being rate limited.")
        elif status >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {status}")   