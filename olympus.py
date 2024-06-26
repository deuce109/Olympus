import argparse
import json
import shutil
import os
import logging
import sys
from typing import List

from config import Config
from models.asset import Asset
from models.downloadable import Downloadable
from regex_patterns import github_ui_repo_re
from models.repo import Repo
from validators import parse_int, check_url

class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    END = '\033[0m'


FORMAT = f'{colors.BLUE}%(asctime)s{colors.END} : {colors.HEADER}%(levelname)s{colors.END} : %(message)s'

logging.basicConfig(format=FORMAT, level=logging.INFO)

logger = logging.getLogger('Olympus')

parser = argparse.ArgumentParser()

parser.add_argument("--cache", "-c", default='release_cache', help="Location where to store cached release info")
parser.add_argument('--download-json', '-d', default='downloads.json', help="A json file defining which repos to download from")
parser.add_argument("--force", "-f", action='store_true', help="Force downloading new release info (may fail due to API rate limits)")
parser.add_argument("--output", "-o", default="sd", help="Output directory to write downloaded files to")
parser.add_argument("--chunk_size", "-s", default=8192, type=parse_int, help="Set chunk size for file downloads defaults to 8192 if value parse to int fails sets to 8192")

parser.add_argument("--format-url", "-u", type=check_url, help="A Github repo releases url to format into an Github api url")

parser.add_argument("--overwrite", "-w", default=False, action='store_true', help="Remove existing output directory before downloading new files")
parser.add_argument("--compress", "-z", default=None, choices=['zip', 'tar'], help="Compress output into zip file")



args =  parser.parse_args()

if args.format_url:
    print(f"https://api.github.com/repos/{args.format_url.group(1)}/releases")

else:

    Config.downloads_json = os.path.abspath(args.download_json)
    
    if not os.path.exists(Config.downloads_json):
        parser.print_help()
        sys.exit(1)
    
    Config.output = os.path.abspath(args.output)

    Config.release_cache = args.cache

    Config.chunk_size = args.chunk_size

    Config.force_release_download = args.force


    if args.overwrite and os.path.exists(Config.output):
        shutil.rmtree(Config.output)
        



    with open(Config.downloads_json) as r:
        json_data: List[dict] = json.load(r)

    downloads: List[Downloadable] = []
    for download in json_data:
        release_url = download.get('releases_url', None)
        if release_url:
            r = Repo(**download)
            r.generate_assets(download.get('assets', []))
            downloads.append(r)
        else:
            downloads.append(Asset.from_definition(download))

    [download.download() for download in downloads]

    if args.compress:
        
        shutil.make_archive(Config.output, args.compress, Config.output)
        shutil.rmtree(Config.output)
        
        
sys.exit(0)