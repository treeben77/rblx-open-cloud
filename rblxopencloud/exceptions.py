from typing import Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .datastore import EntryInfo

__all__ = (
    "BaseException",
    "HttpException",
    "NotFound",
    "Forbidden",
    "PreconditionFailed",
    "InsufficientScope",
    "InvalidAsset",
    "InvalidCode",
    "ModeratedText",
    "UnknownEventType",
    "UnhandledEventType"
)

class BaseException(Exception): pass
class HttpException(BaseException):
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

class NotFound(HttpException): pass
class Forbidden(HttpException):
    def __init__(self, *args: object) -> None:
        super().__init__(
            "Authorization lacks permission to this resource", *args
        )

class PreconditionFailed(HttpException):
    def __init__(self, value, info, *args: object) -> None:
        self.value: Optional[Union[str, dict, list, int, float]] = value
        self.info: Optional[EntryInfo] = info
        super().__init__(*args)

class InsufficientScope(HttpException):
    def __init__(self, scope, *args: object) -> None:
        self.required_scope: str = scope
        super().__init__(*args)

class InvalidCode(HttpException): pass
class InvalidAsset(HttpException): pass
class ModeratedText(HttpException): pass

class UnknownEventType(BaseException): pass
class UnhandledEventType(BaseException): pass
