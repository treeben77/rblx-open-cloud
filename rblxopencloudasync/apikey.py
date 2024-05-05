# MIT License

# Copyright (c) 2022-2024 treeben77

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from .experience import Experience
from .group import Group
from .user import User

__all__ = (
    "ApiKey",
)

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
