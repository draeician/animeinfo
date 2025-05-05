# AnimeInfo

A utility tool for fetching and processing anime information from various sources.

## Features

- Query the Jikan API for anime data
- Extract information from URLs
- Generate JSON output files with anime metadata
- Support for fuzzy matching of titles

## Usage

```bash
python animeinfo.py <url> [<url> ...] [--title "Optional title override"]
```

### Example

```bash
python animeinfo.py https://hianime.example.com/anime/fairy-tail-100-years-quest-19253
```

## Requirements

- Python 3
- requests library