from .experience import *
from .datastore import *
from .exceptions import *

from typing import Literal

VERSION: str = "1.1.0"
VERSION_INFO: Literal['alpha', 'beta', 'final'] = "beta"

del Literal