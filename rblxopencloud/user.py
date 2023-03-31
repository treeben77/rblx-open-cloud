from .creator import Creator
import datetime
from typing import Optional

__all__ = (
    "User",
)

class User(Creator):
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
