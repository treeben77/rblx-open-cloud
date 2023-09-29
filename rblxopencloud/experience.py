from .exceptions import rblx_opencloudException, InvalidKey, NotFound, RateLimited, ServiceUnavailable
import io
from typing import Optional, Iterable, Literal, Union
from .datastore import DataStore, OrderedDataStore
from . import user_agent, request_session

__all__ = (
    "Experience",
)

class Experience():
    """
    Represents an experience/game on Roblox. Allows interaction with data stores, messaging service, etc.

    Args:
        id: The experience/universe ID
        api_key: The API key created on the [Creator Dashboard](https://create.roblox.com/credentials) with access to the experience.
    
    Attributes:
        id (int): The experience/universe ID
        owner (Optional[Union[User, Group]]): The object of the experience owner. Only present from OAuth2.
    """

    def __init__(self, id: int, api_key: str):
        self.id: int = id
        self.owner = None
        self.__api_key: str = api_key
    
    def __repr__(self) -> str:
        return f"rblxopencloud.Experience({self.id})"
    
    def get_data_store(self, name: str, scope: Optional[str]="global") -> DataStore:
        """
        Creates a `rblxopencloud.DataStore` with the provided name and scope. This function doesn't make an API call so there is no validation.

        Args:
            name: The data store name.
            scope: The data store scope. Set it to none for `scope/key` syntax.
        
        Returns:
            The Data Store with the provided name and scope.
        """
        return DataStore(name, self, self.__api_key, None, scope)
    
    def get_ordered_data_store(self, name: str, scope: Optional[str]="global") -> OrderedDataStore:
        """
        Creates a `rblxopencloud.OrderedDataStore` with the provided name and scope. This function doesn't make an API call so there is no validation.

        Args:
            name: The data store name.
            scope: The data store scope. Set it to none for `scope/key` syntax.

        Returns:
            The Ordered Data Store with the provided name and scope.
        """
        return OrderedDataStore(name, self, self.__api_key, scope)

    def list_data_stores(self, prefix: Optional[str]="", limit: Optional[int]=None, scope: Optional[Union[str, None]]="global") -> Iterable[DataStore]:
        """
        Interates `rblxopencloud.DataStore` for all of the Data Stores in the experience.

        Example:
            This will print every data store in the experience. 
            ```py
            for datastore in experience.list_data_stores():
                print(datastore)
            ```
            If you'd like the datastores in a list, you can use the list method:
            ```py
            list(experience.list_data_stores())
            ```

        Args:
            prefix: Only return Data Stores with names starting with this value.
            limit: The maximum number of Data Stores to iterate.
            scope: The scope for all data stores. Defaults to global, and can be `None` for key syntax like `scope/key`.
        
        Returns:
            An Iterable of `rblxopencloud.DataStore` in the experience.

        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to list data stores, or is from an invalid IP address.
            NotFound: The experience does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        """
        nextcursor = ""
        yields = 0
        while limit == None or yields < limit:
            response = request_session.get(f"https://apis.roblox.com/datastores/v1/universes/{self.id}/standard-datastores",
                headers={"x-api-key": self.__api_key}, params={
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
                yields += 1
                yield DataStore(datastore["name"], self, self.__api_key, datastore["createdTime"], scope)
                if limit == None or yields >= limit: break
            nextcursor = data.get("nextPageCursor")
            if not nextcursor: break
    
    def publish_message(self, topic: str, data: str) -> None:
        """
        Publishes a message to live game servers that can be recieved with [MessagingService](https://create.roblox.com/docs/reference/engine/classes/MessagingService).

        **The `universe-messaging-service:publish` scope is required for OAuth2 authorization.**

        Args:
            topic: The topic to send the message in
            data: The message to send. Open Cloud does not support sending dictionaries/tables with publishing messages. You'll have to json encode it before sending it, and decode it in Roblox.
        
        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to publish messages, or is from an invalid IP address.
            NotFound: The experience does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        
        !!! note
            Messages sent by Open Cloud with only be recieved by live servers. Studio won't recieve thesse messages.
        """
        response = request_session.post(f"https://apis.roblox.com/messaging-service/v1/universes/{self.id}/topics/{topic}",
        json={"message": data}, headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "user-agent": user_agent})
        if response.status_code == 200: return
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The place does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")  
    
    def upload_place(self, place_id:int, file: io.BytesIO, publish: Optional[bool] = False) -> int:
        """
        Uploads the place file to Roblox, optionally choosing to publish it.

        Example:
            Replace `0000000` with the target place's ID, and `example.rbxl` should be the path to the roblox place file.
            ```py
            with open("example.rbxl", "rb") as file:
                experience.upload_place(0000000, file, publish=False)
            ```

        Args:
            place_id: The place ID to upload the file to.
            file: The place file to upload, opened in bytes.
            publish: Wether to publish the new place file.

        Returns:
            The place's new version ID.
        
        Raises:
            InvalidKey: The API key isn't valid, doesn't have access to publish places, or is from an invalid IP address.
            NotFound: The experience does not exist.
            RateLimited: You've exceeded the rate limits.
            ServiceUnavailable: The Roblox servers ran into an error, or are unavailable right now.
            rblx_opencloudException: Roblox returned an unexpected error.
        """
        response = request_session.post(f"https://apis.roblox.com/universes/v1/{self.id}/places/{place_id}/versions",
            headers={"x-api-key": self.__api_key, 'content-type': 'application/octet-stream', "user-agent": user_agent}, data=file.read(), params={
                "versionType": "Published" if publish else "Saved"
            })
        if response.status_code == 200:
            return response.json()["versionNumber"]
        elif response.status_code == 401: raise InvalidKey("Your key may have expired, or may not have permission to access this resource.")
        elif response.status_code == 404: raise NotFound(f"The place does not exist.")
        elif response.status_code == 429: raise RateLimited("You're being rate limited.")
        elif response.status_code >= 500: raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        else: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")   