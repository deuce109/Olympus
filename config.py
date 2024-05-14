

import os
from typing import Union


class Config:
    output: Union[str, bytes, os.PathLike]
    release_cache: Union[str, bytes, os.PathLike]
    downloads_json: Union[str, bytes, os.PathLike]
    chunk_size: int
    force_release_download: bool
    