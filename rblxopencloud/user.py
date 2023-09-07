from .creator import Creator
from .exceptions import rblx_opencloudException, InvalidKey, NotFound, RateLimited, ServiceUnavailable
import datetime
from typing import Optional, Iterable, TYPE_CHECKING
from . import user_agent, request_session

if TYPE_CHECKING:
    from .group import GroupMember

__all__ = (
    "User",
)

class User(Creator):
    """
    Represents a user on Roblox. It is used to provide information about a user in OAuth2, and to upload assets to a user.
    ### Paramaters
    id: int - The user's ID.
    api_key: str - Your API key created from [Creator Dashboard](https://create.roblox.com/credentials) with access to this user.
    """
    def __init__(self, id: int, api_key: str) -> None:
        self.username: Optional[str] = None
        self.id: int = id
        self.display_name: Optional[str] = None
        self.profile_uri: str = f"https://roblox.com/users/{self.id}/profile"
        self.created_at: Optional[datetime.datetime] = None

        self.__api_key = api_key

        super().__init__(id, api_key, "User")

    def list_groups(self, limit: Optional[int]=None) -> Iterable["GroupMember"]:
        from .group import GroupMember

        filter = None

        nextcursor = ""
        yields = 0
        while limit == None or yields < limit:
            response = request_session.get(f"https://apis.roblox.com/cloud/v2/groups/-/memberships",
                headers={"x-api-key" if not self.__api_key.startswith("Bearer ") else "authorization": self.__api_key, "user-agent": user_agent}, params={
                "maxPageSize": limit if limit and limit <= 99 else 99,
                "filter": f"user == 'users/{self.id}'",
                "pageToken": nextcursor if nextcursor else None
            })

            if response.status_code == 400: raise rblx_opencloudException(response.json()["message"])
            elif response.status_code == 401: raise InvalidKey(response.text)
            elif response.status_code == 404: raise NotFound(response.json()["message"])
            elif response.status_code == 429: raise RateLimited("You're being rate limited!")
            elif response.status_code >= 500: raise ServiceUnavailable(f"Internal Server Error: '{response.text}'")
            elif not response.ok: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}: '{response.text}'")
            
            data = response.json()
            for member in data["groupMemberships"]:
                yields += 1
                
                yield GroupMember(member, self.__api_key)
            nextcursor = data.get("nextPageToken")
            if not nextcursor: break

        pass
    
    def __repr__(self) -> str:
        return f"rblxopencloud.User({self.id})"
