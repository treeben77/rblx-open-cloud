class rblx_opencloudException(Exception): pass
class NotFound(rblx_opencloudException): pass
class InvalidKey(rblx_opencloudException): pass
class RateLimited(rblx_opencloudException): pass
class ServiceUnavailable(rblx_opencloudException): pass
class PreconditionFailed(rblx_opencloudException):
    def __init__(self, value, info, *args: object) -> None:
        self.value = value
        self.info = info
        super().__init__(*args)