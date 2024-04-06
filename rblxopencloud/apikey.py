from .experience import Experience
from .group import Group
from .user import User

class ApiKey():
    """
    Represents an API key and allows creation of API classes (such as
    [`User`][rblxopencloud.User]) without needing to use the API key string \
    all the time.

    Args:
        api_key: Your API key created from \
        [Creator Dashboard](https://create.roblox.com/credentials).
    """

    def __init__(self, api_key) -> None:
        self.__api_key = api_key

    def get_experience(self, id: int, fetch_info: bool = False) -> Experience:
        obj = Experience(id, self.__api_key)

        if fetch_info:
            obj.fetch_info()
        
        return obj
    
    def get_group(self, id: int, fetch_info: bool = False) -> Group:
        obj = Group(id, self.__api_key)

        if fetch_info:
            obj.fetch_info()
        
        return obj
    
    def get_user(self, id: int, fetch_info: bool = False) -> User:
        obj = User(id, self.__api_key)

        if fetch_info:
            obj.fetch_info()
        
        return obj
