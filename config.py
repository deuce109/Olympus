

import os
from typing import Union


class Config:
    output: Union[str, bytes, os.PathLike]
    release_cache: Union[str, bytes, os.PathLike]