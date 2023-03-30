from .creator import Creator

class User(Creator):
    def __init__(self, id: int, api_key: str) -> None:
        self.id = id
        self.__api_key = api_key
        super().__init__(id, api_key, "User")
    
    def __repr__(self) -> str:
        return f"rblxopencloud.User({self.id})"