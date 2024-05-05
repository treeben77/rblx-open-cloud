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

from typing import Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .datastore import EntryInfo

__all__ = (
    "BaseException",
    "HttpException",
    "NotFound",
    "RateLimited",
    "Forbidden",
    "PreconditionFailed",
    "InvalidFile",
    "InvalidCode",
    "ModeratedText",
    "UnknownEventType",
    "UnhandledEventType"
)

class BaseException(Exception):
    """
    The base exception for all exception raised by the library.
    """

class HttpException(BaseException):
    """
    The base exception for HTTP request failures. In many situations, a \
    different exception inheriting \
    [`HttpException`][rblxopencloud.HttpException] may be raised. Different \
    exceptions that could be raised are as follows:

    | Status | Exception | Description |
    | --- | --- | --- |
    | 400 Bad Request | [`HttpException`][rblxopencloud.HttpException] \
    | The request body is malformed or not valid. Some methods will return \
    a specific error instead of \
    [`HttpException`][rblxopencloud.HttpException]. |
    | 401 Unauthorized | [`HttpException`][rblxopencloud.HttpException] \
    | The API key or OAuth2 bearer token is invalid, has expired, not from \
    an accepted IP, or the API has been been enabled for the key. |
    | 403 Forbidden | [`Forbidden`][rblxopencloud.Forbidden] \
    | The authorization doesn't have access to the requested resource. |
    | 404 Not Found | [`NotFound`][rblxopencloud.NotFound] \
    | The resource or endpoint could not be found. |
    | 429 Rate Limited | [`RateLimited`][rblxopencloud.RateLimited] \
    | The resource is being rate limited. |
    | 5xx Server Error | [`HttpException`][rblxopencloud.HttpException] \
    | The server ran into an internal error and is unable to process the \
    request. |
    | Other Error Statuses | [`HttpException`][rblxopencloud.HttpException] \
    | The server returned an unexpected HTTP status. |

    Functions in the library that raise different exception from those above \
    will be documented in the method itself.
    """
    def __init__(self, *args: object) -> None:
        
        if len(args) and args[0] == 401:
            args = ("Authorization was denied",)
        elif len(args) and args[0] == 404:
            args = ("Resource not found",)
        elif len(args) and args[0] == 429:
            args = ("The resource is being rate limited",)
        elif len(args) and args[0] == 500:
            args = ("Internal server error",)
        elif len(args) and type(args[0]) == int:
            args = (f"Unexpected HTTP {args[0]}",)

        super().__init__(*args)

class NotFound(HttpException):
    """
    The exception raised when a requested resource or endpoint couldn't \
    be found.
    """

class RateLimited(HttpException):
    """
    Roblox blocked the request for exceeding the endpoint's rate limit. The \
    library does not currently support any rate limiting handling but this \
    exception can be used to implement automatic retrying. 
    """

class Forbidden(HttpException):
    """
    This exception is raised if the API key or OAuth2 bearer token does not \
    have access to the requested resource.

    In certain situations, [`HttpException`][rblxopencloud.HttpException] \
    will be raised when [`Forbidden`][rblxopencloud.Forbidden] is expected. \
    Some situations where this happens includes attempting to access a \
    resource without the necessary OAuth2 scope or the API key permission and \
    API enabled. 
    """

    def __init__(self, *args: object) -> None:
        super().__init__(
            "Authorization lacks permission to this resource", *args
        )

class PreconditionFailed(HttpException):
    """
    A precondition specified for the request was not met or failed. If raised \
    by [`DataStore.set_entry`][rblxopencloud.DataStore.set_entry], extra \
    information about the entry's current value and info will be provided.

    Attributes:
        value: The current entry value, if raised by \
        [`DataStore.set_entry`][rblxopencloud.DataStore.set_entry]
        info: The current entry information such as metadata, if raised by \
        [`DataStore.set_entry`][rblxopencloud.DataStore.set_entry]
    """

    def __init__(self, value, info, *args: object) -> None:
        self.value: Optional[Union[str, dict, list, int, float]] = value
        self.info: Optional[EntryInfo] = info
        super().__init__(*args)

class InvalidCode(HttpException): pass
class InvalidFile(HttpException): pass
class ModeratedText(HttpException): pass

class UnknownEventType(BaseException): pass
class UnhandledEventType(BaseException): pass
