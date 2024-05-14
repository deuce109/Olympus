from packaging.version import Version
import json
import os
from typing import List
import requests
import logging


from models.downloadable import Downloadable
from regex_patterns import github_api_re
from config import Config
from models.asset import Asset

logger = logging.getLogger('Olympus')

class Repo(Downloadable):
    name: str
    releases_url: str
    assets = List[Asset]
    release_cache_path: str

    _cached: bool = False

    def __init__(self, name='', releases_url='', **_):
        match = github_api_re.match(releases_url)
        if match:
            self.name = name or match.group(1).replace('\\', '-').replace('/', '-')
            self.releases_url = releases_url
            self.assets =  []
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

    
    def generate_assets(self, assets):
        release = self._current_release(Config.force_release_download)
        release_assets = release.get('assets', [])
        for asset in assets:
            new_asset = Asset.from_release(release_assets, asset)
            if new_asset:
                self.assets.append(new_asset)



    
    def download(self) -> str:

        for asset in self.assets:
            asset.download()