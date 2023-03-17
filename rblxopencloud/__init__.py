from .experience import *
from .datastore import *
from .exceptions import *
from .user import *
from .oauth2 import *

from typing import Literal

VERSION: str = "1.1.0"
VERSION_INFO: Literal['alpha', 'beta', 'final'] = "alpha"

del Literal