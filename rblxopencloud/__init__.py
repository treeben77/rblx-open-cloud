from typing import Literal
import requests

VERSION: str = "1.5.1"
VERSION_INFO: Literal['alpha', 'beta', 'final'] = "final"

user_agent: str = f"rblx-open-cloud/{VERSION} (https://github.com/treeben77/rblx-open-cloud)"

request_session: requests.Session = requests.Session()

del Literal, requests

from .experience import *
from .datastore import *
from .exceptions import *
from .user import *
from .oauth2 import *
from .group import *
from .creator import *
from .webhook import *
