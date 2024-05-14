# Usage

Example download.json file located in `/examples`

Please check json schema at `/examples/schema.json`

```
usage: main.py [-h] [--cache CACHE] [--download-json DOWNLOAD_JSON] [--force] [--output OUTPUT] [--overwrite]

options:
  -h, --help            show this help message and exit
  --cache CACHE, -c CACHE
                        Location where to store cached release info
  --download-json DOWNLOAD_JSON, -d DOWNLOAD_JSON
                        A json file defining which repos to download from
  --force, -f           Force downloading new release info (may fail due to API rate limits)
  --output OUTPUT, -o OUTPUT
                        Output directory to write downloaded files to
  --overwrite, -w       Remove existing output directory before downloading new files
```

# Planned updates
