from .creator import Creator
import datetime
from typing import Optional, Literal

__all__ = (
    "User",
)

class User(Creator):
    def __init__(self, id: int, api_key: str) -> None:
        self.username: Optional[str] = None
        self.id: int = id
        self.display_name: Optional[str] = None
        self.profile_uri: str = f"https://roblox.com/users/{self.id}/profile"
        self.created_at: Optional[datetime.datetime]

        self.__api_key = api_key
        self.__key_type: Literal["API_KEY", "BEARER"] = "API_KEY"

        super().__init__(id, api_key, self.__key_type, "User")
    
    def __repr__(self) -> str:
        return f"rblxopencloud.User({self.id})"
