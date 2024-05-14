import json
import logging
import os
import re
import shutil
import tempfile
from typing import List
import zipfile

import requests

from config import Config
from decompression import Decompressor
from models.downloadable import Downloadable

logger = logging.getLogger('Olympus')

class FileMove:
    file_name_pattern: re.Pattern
    new_path: str

    def __init__(self, file_name_pattern=".*", new_path=""):
        self.file_name_pattern = re.compile(file_name_pattern)
        self.new_path = new_path

class Asset(Downloadable):
    download_url: str
    file_name: str
    moves: List[FileMove]
    name: str

    def __init__(self, name="", download_url="", file_name="", moves=[]):
        self.name =name
        self.download_url = download_url
        self.file_name = file_name
        self.moves = [FileMove(**m) for m in moves]

    def _find_urls(self):
        assets = [a for a in assets if a and isinstance(a, dict) and self.pattern.match(a.get('name', None))]

        return [(asset.get('name', None), asset.get('browser_download_url', None)) for asset in assets if asset]
    
    def _process_file(self, filename, file):
        if Decompressor.is_compressed(file):
            Decompressor.decompress(file, Config.output)
            # zipfile.ZipFile(file).extractall(Config.output)
        else:
            if not os.path.exists(Config.output):
                os.makedirs(Config.output)
            with open(os.path.abspath(os.path.join(Config.output, filename)), 'wb') as w:
                shutil.copyfileobj(file, w)

    def _download_to_file(self, stream: requests.Response, file):
        for chunk in stream.iter_content(chunk_size=Config.chunk_size):
            file.write(chunk)

        return file
    
    
    def _process_moves(self):
        old_path = ""
        new_path = ""
        moved = False
        for move in self.moves:
            for path, _, files in os.walk(Config.output):
                for file in files:
                    if move.file_name_pattern.match(file):
                        old_path = os.path.abspath(os.path.join(path, file))
                        new_path = os.path.abspath(os.path.join(Config.output, move.new_path, file))
                        moved = True
                        break
                if moved:
                    break
            if old_path and new_path:
                new_dir = os.path.join(os.path.split(new_path)[0])
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir, exist_ok=True)
                shutil.move(old_path, new_path)
                break

    def download(self):

            if self.download_url and self.file_name:

                with requests.get(self.download_url, stream=True) as res:
                        
                        res.raise_for_status()

                        with tempfile.SpooledTemporaryFile(mode='rb+') as file:

                            logger.info(f"Downloading asset {self.name or self.file_name}")

                            self._download_to_file(res, file)
                            
                            file.seek(0)

                            self._process_file(self.file_name, file)

                            self._process_moves()

    @classmethod
    def from_release(self, release_assets, asset_json ):
            pattern_string = asset_json.get('pattern', None)
            if pattern_string:
                pattern = re.compile(pattern_string)
                for asset_def in release_assets:
                     name = asset_def.get('name', '')
                     if pattern.match(name):
                          download_url = asset_def.get('browser_download_url','None')
                          moves = asset_json.get('moves', [])
                          return Asset(
                                file_name=name,
                                download_url=download_url,
                                moves=moves
                                )
                     
    @classmethod
    def from_definition(self, definition):
        name = definition.get('name', '')
        file_name = definition.get('file_name', '')
        download_url = definition.get('download_url', '')
        moves = definition.get('moves', [])
        if download_url and file_name:
            return Asset(
                name = name,
                file_name=file_name,
                download_url=download_url,
                moves=moves
            )
        else:
            logger.error(f'Unable to add asset based off of definition\n{json.dumps(definition)}')
                    
