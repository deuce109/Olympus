from distutils.version import Version
import json
import os
import re
import shutil
import tempfile
from typing import List
import zipfile
import requests
import logging

from regex_patterns import github_api_re
from config import Config

logger = logging.getLogger('Olympus')

class FileMove():
    file_name_pattern: re.Pattern
    new_path: str

    def __init__(self, file_name_pattern=".*", new_path=""):
        self.file_name_pattern = re.compile(file_name_pattern)
        self.new_path = new_path

class Asset():
    pattern: re.Pattern
    moves: List[FileMove]

    def __init__(self, pattern=".*", moves=[]):
        self.pattern = re.compile(pattern)
        self.moves = [FileMove(**m) for m in moves]

    def process_moves(self):
        old_path = ""
        new_path = ""
        for move in self.moves:
            for path, _, files in os.walk(Config.output):
                for file in files: 
                    if move.file_name_pattern.match(file):
                         old_path = os.path.abspath(os.path.join(path, file))
                         new_path = os.path.abspath(os.path.join(Config.output, move.new_path, file))
                         break
            if old_path and new_path:
                new_dir = os.path.join(os.path.split(new_path)[0])
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir, exist_ok=True)
                shutil.move(old_path, new_path)
                break

class Repo():
    name: str
    releases_url: str
    assets = List[Asset]
    release_cache_path: str

    _cached: bool = False

    def __init__(self, name='', releases_url='', assets=[]):
        match = github_api_re.match(releases_url)
        if match:
            self.name = name or match.group(1).replace('\\', '-').replace('/', '-')
            self.releases_url = releases_url
            self.assets =  [Asset(**asset) for asset in assets]
            self.release_cache_path = os.path.abspath(os.path.join(Config.release_cache, f"{self.name}.json"))
    
    def _is_release_cached(self):
        if os.path.exists(self.release_cache_path):
            try:
                with open(self.release_cache_path) as reader:
                    self._cached = True

                    cache = json.load(reader)
                    return cache
            except json.JSONDecodeError as e:
                logger.info(f"Error decoding release cache: {e}")
                return False
            
        return False
    
    def _cache_release(self, releases):
        with open(self.release_cache_path, 'w') as w:
            json.dump(releases, w)

    def _download_release(self):
        
        logger.info(f"Unable to find cached files for {self.name}. Downloading...")

        res = requests.get(self.releases_url)

        if res.status_code >= 300:
            return None
        else:
            releases = res.json()
            if isinstance(releases, dict) and releases.get('message', None):
                logger.info('Github API limit reached please try again later')
                return []
            self._cache_release(releases)
            self._cached = True
            return releases
    
    def _get_releases(self, force) -> List[dict]:
        
        cache = {}

        cache = self._is_release_cached()
        if force or not cache:
            return self._download_release()
        else:
            
            logger.info(f"{self.name} was cached. Using cache...")
            return cache
            
        
    def _current_release(self, force) -> dict:

        releases = self._get_releases(force)

        versions = {r.get("tag_name", '0.0.0'): r  for r in releases if r}

        newest_version = sorted(versions.keys(), key=lambda x: Version(x.split('-')[0]))[-1]
        return versions[newest_version]
    
    def _find_asset_url(self, asset: Asset, force) -> str:
        
        assets = self._current_release(force).get('assets', [])

        assets = [a for a in assets if a and isinstance(a, dict) and asset.pattern.match(a.get('name', None))]

        return [(asset.get('name', None), asset.get('browser_download_url', None)) for asset in assets if asset]
    
    def _process_file(self, filename, file):
        if zipfile.is_zipfile(file):
            zipfile.ZipFile(file).extractall(Config.output)
        else:
            with open(os.path.abspath(os.path.join(Config.output, filename)), 'w') as w:
                shutil.copyfileobj(file, w )

    def _download_to_file(self, stream: requests.Response, file):
        for chunk in stream.iter_content(chunk_size=Config.chunk_size):
            file.write(chunk)

        return file

    
    def _download_asset(self, asset: Asset, force):

        for name, url in self._find_asset_url(asset, force):

            if url and name:

                with requests.get(url, stream=True) as res:
                        
                        res.raise_for_status()

                        with tempfile.SpooledTemporaryFile(mode='wb') as file:

                            logger.info(f"File {name} downloading...")

                            self._download_to_file(res, file)

                            self._process_file(name, file)

                            asset.process_moves()

    def download_assets(self, force):
        [self._download_asset(asset, force) for asset in self.assets]