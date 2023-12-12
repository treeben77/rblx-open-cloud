from typing import Literal, Optional, Union
import requests

VERSION: str = "1.6.0"
VERSION_INFO: Literal['alpha', 'beta', 'final'] = "final"

user_agent: str = f"rblx-open-cloud/{VERSION} (https://github.com/treeben77/rblx-open-cloud)"

request_session: requests.Session = requests.Session()

from .exceptions import *

def send_request(method: str, path: str, authorization: Optional[str]=None,
        expected_status: Optional[list[int]]=None, **kwargs) -> tuple[int, Union[str, int, float, dict, list, None], dict]:
    headers = {
        "user-agent": user_agent,
        **kwargs.get('headers', {})
    }

    if authorization: headers["x-api-key" if not authorization.startswith("Bearer ") else "authorization"] = authorization
    if kwargs.get('headers'): del kwargs['headers']

    response = request_session.request(method, f"https://apis.roblox.com/{path}", headers=headers, **kwargs)

    print(f"[DEBUG] {method} /{path} - {response.status_code}")

    if 'application/json' in response.headers.get('Content-Type', ''):
        body = response.json()
    else:
        body = response.text

    if expected_status:
        if response.status_code == 401 and 401 not in expected_status:
            raise InvalidKey("The authorization key is not valid.")
        elif response.status_code == 403 and 403 not in expected_status:
            raise PermissionDenied("The authorization does not have scope to access this resource.")
        elif response.status_code == 404 and 404 not in expected_status:
            raise NotFound(body["message"] if type(body) == dict else body)
        elif response.status_code == 429 and 429 not in expected_status:
            raise RateLimited("The resource is being rate limited.")
        elif response.status_code >= 500  and 500 not in expected_status:
            raise ServiceUnavailable("The service is unavailable or has encountered an error.")
        elif response.status_code == 400 and 400 not in expected_status:
            raise rblx_opencloudException(body["message"] if type(body) == dict else body)
        elif response.status_code not in expected_status: raise rblx_opencloudException(f"Unexpected HTTP {response.status_code}")
    
    return response.status_code, body, response.headers

from .experience import *
from .datastore import *
from .user import *
from .oauth2 import *
from .group import *
from .creator import *
from .webhook import *

del Literal, Optional, requests
