from .creator import Creator

__all__ = (
    "Group",
)

class Group(Creator):
    """
    Represents a group on Roblox. For now this is only used for uploading assets, but in the future you'll be able to manage other aspects of a group.
    ### Paramaters
    id: int - The group's ID.
    api_key: str - Your API key created from [Creator Dashboard](https://create.roblox.com/credentials) with access to this user.
    """
    def __init__(self, id: int, api_key: str) -> None:
        self.id: int = id
        self.__api_key = api_key
        super().__init__(id, api_key, "Group")
        
    def __repr__(self) -> str:
        return f"rblxopencloud.Group({self.id})"