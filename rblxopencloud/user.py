from .creator import Creator
import datetime
from typing import Optional

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
    
    def __repr__(self) -> str:
        return f"rblxopencloud.User({self.id})"
