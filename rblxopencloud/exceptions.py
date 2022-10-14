class rblx_opencloudException(Exception): pass
class NotFound(rblx_opencloudException): pass
class InvalidKey(rblx_opencloudException): pass
class RateLimited(rblx_opencloudException): pass
class ServiceUnavailable(rblx_opencloudException): pass