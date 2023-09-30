from typing import Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .datastore import EntryInfo

__all__ = (
    "rblx_opencloudException",
    "NotFound",
    "InvalidKey",
    "PermissionDenied",
    "RateLimited",
    "ServiceUnavailable",
    "PreconditionFailed",
    "InsufficientScope",
    "InvalidAsset",
    "InvalidCode",
    "ModeratedText",
    "UnknownEventType",
    "UnhandledEventType"
)

class rblx_opencloudException(Exception):
    """
    The base exception of the library. Most Exceptions inherit from this exception.
    """
class NotFound(rblx_opencloudException):
    """
    Raised when a ceartin resource, such as an experience, user, group, or data store could not be found.
    """
class InvalidKey(rblx_opencloudException):
    """
    The API key, or OAuth2 access token is invalid because it either isn't valid, used on an unauthorized IP address, doesn't have access to the requested API, or has been invalidated.

    Not to be confused with [`rblxopencloud.PermissionDenied`][rblxopencloud.PermissionDenied]
    """
class PermissionDenied(InvalidKey):
    """
    The API key, or OAuth2 access token has access to the API, but not the resource, such as trying to access a private inventory.
    """
class RateLimited(rblx_opencloudException):
    """
    You have exceeded an API's rate limit.
    """
class ServiceUnavailable(rblx_opencloudException):
    """
    Roblox's servers have either encountered an internal error, or are experiencing downtime.
    """
class PreconditionFailed(rblx_opencloudException):
    """
    A DataStore precondition failed such as the entry already existing when `exclusive_create` is `True`. 

    Attributes:
        value (Optional[Union[str, dict, list, int, float]]): The current value of the entry, only present for data store methods, not ordered data store methods.
        info (Optional[EntryInfo]): The metadata of the current value, only present for data store methods, not ordered data store methods.
    """

    def __init__(self, value, info, *args: object) -> None:
        self.value: Optional[Union[str, dict, list, int, float]] = value
        self.info: Optional[EntryInfo] = info
        super().__init__(*args)
class InsufficientScope(InvalidKey):
    """
    When authorized for OAuth2, it indicates a required scope for this action is missing.

    Attributes:
        required_scope (str): The required scope to complete this action.
    """
    def __init__(self, scope, *args: object) -> None:
        self.required_scope: str = scope
        super().__init__(*args)
class InvalidCode(InvalidKey):
    """
    The code used in [`OAuth2App.exchange_code`][rblxopencloud.OAuth2App.exchange_code] is either invalid, or has already been used.
    """
class InvalidAsset(rblx_opencloudException):
    """
    Roblox could not accept the Asset you attempted to upload, most likely because it's either an unsupported type, uploaded as the wrong [`rblxopencloud.AssetType`][rblxopencloud.AssetType], or has been corrupted.
    """
class ModeratedText(rblx_opencloudException):
    """
    The text you provided was moderated by the text filter.
    """
class UnknownEventType(rblx_opencloudException):
    """
    The event type recieved from the webhook is unknown. This is most likely due to an outdated library.
    """
class UnhandledEventType(rblx_opencloudException):
    """
    The event type recieved from the webhook does not have a handler.
    """
