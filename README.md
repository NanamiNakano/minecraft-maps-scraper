# Minecraft Maps Scraper

Scripts in this project can scrape Minecraft maps and metadata from various websites. I do not offer these files
directly, please use them as your own risk.

## Usage

### Install dependencies

```shell
uv venv --seed --python 3.13
uv sync
```

### Run the scraper

```shell
cd /path/to/scraper
# Scraper metadata first
python metadata.py
# Download map files
python downloader.py
```