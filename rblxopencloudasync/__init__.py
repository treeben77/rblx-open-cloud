from typing import Literal, Optional, Union
import aiohttp

VERSION: str = "1.7.0"
VERSION_INFO: Literal['alpha', 'beta', 'final'] = "alpha"

user_agent: str = f"rblx-open-cloud/{VERSION} (https://github.com/treeben77/rblx-open-cloud)"

request_session: Optional[aiohttp.ClientSession] =  None

async def preform_request(method: str, path: str, authorization: Optional[str]=None, params: Optional[dict]=None, **kwargs):
    global request_session
    import aiohttp

    if not request_session:
        request_session = aiohttp.ClientSession()

    if params:
        def convert_type(v):
            if type(v) == bool: return 'true' if v else 'false'
            return v
        
        kwargs['params'] = {k: convert_type(v) for k, v in params.items() if v is not None}
    
    headers = {
        "user-agent": user_agent,
        **kwargs.get('headers', {})
    }

    if authorization: headers["x-api-key" if not authorization.startswith("Bearer ") else "authorization"] = authorization
    if kwargs.get('headers'): del kwargs['headers']

    response = await request_session.request(method, f"https://apis.roblox.com/{path}", headers=headers, **kwargs)

    try:
        body = await response.json()
    except(aiohttp.client_exceptions.ContentTypeError):
        body = await response.text()
    if not body: body = await response.text()

    return response.status, body, response.headers

del Literal, Optional, aiohttp, Union

from .experience import *
from .datastore import *
from .exceptions import *
from .user import *
from .oauth2 import *
from .group import *
from .creator import *
from .webhook import *
