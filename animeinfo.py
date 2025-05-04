#!/usr/bin/env python3
import requests
from difflib import get_close_matches
import re
import argparse
import json
import os

#jq '{status, type, title_english}' fairy-tail-100-years-quest-19253.json
#{
#  "status": "Finished Airing",
#  "type": "TV",
#  "title_english": "Fairy Tail: 100 Years Quest"
#}
#draeician@nomnom /opt/md1/anime/tv/fairy_tail-100_years_quest $ jq -r '.status, .type, .title_english' fairy-tail-100-years-quest-19253.json
#Finished Airing
#TV
#Fairy Tail: 100 Years Quest

# pull the urls from the mp4 files if available
# for i in `ap *e01* | grep desc | sed 's/.*: //'`

def extract_slug_base(hianime_url):
    """Extract the hyphenated slug (excluding numeric ID) from the Hianime URL."""
    parts = hianime_url.rstrip('/').split('/')[-1].split('-')[:-1]
    return '-'.join(parts)


def extract_slug(hianime_url):
    """Get the raw slug for filename output."""
    return hianime_url.rstrip('/').split('/')[-1]


def search_jikan_for_title(title_query):
    """Query the Jikan API for anime matches."""
    url = "https://api.jikan.moe/v4/anime"
    params = {"q": title_query, "limit": 10}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    return data.get("data", [])


def clean_tokens(text):
    """Lowercase text, replace non-alphanumerics with spaces, split into tokens."""
    cleaned = re.sub(r'[^A-Za-z0-9]', ' ', text.lower())
    return set(cleaned.split())


def slug_match_to_result(slug_base, candidates):
    """Find exact or subset token match between slug and anime titles."""
    slug_tokens = clean_tokens(slug_base)
    # exact token match
    for anime in candidates:
        if slug_tokens == clean_tokens(anime['title']):
            return anime
    # subset token match for sequels/spin-offs
    for anime in candidates:
        if slug_tokens <= clean_tokens(anime['title']):
            return anime
    return None


def fuzzy_match_title(candidates, title_query):
    """Fallback to fuzzy matching on title_query string."""
    if not candidates:
        return None
    title_map = {anime['title']: anime for anime in candidates}
    match = get_close_matches(title_query, title_map.keys(), n=1, cutoff=0.4)
    if match:
        return title_map[match[0]]
    return None


def get_jikan_anime_info(url, override_title):
    """Main: use slug_base as query, match candidates, return anime dict."""
    slug_base = extract_slug_base(url)
    query = override_title or slug_base
    candidates = search_jikan_for_title(query)
    # first try slug-match then fuzzy
    anime = slug_match_to_result(slug_base, candidates) or fuzzy_match_title(candidates, query)
    return anime


def main():
    parser = argparse.ArgumentParser(
        description="Fetch full Jikan info for Hianime URLs; dumps entire anime dict to JSON.")
    parser.add_argument('urls', nargs='+', help='Hianime episode or season URL(s)')
    parser.add_argument('--title', default='', help='Optional override search title')
    args = parser.parse_args()

    for url in args.urls:
        print(f"Processing: {url}")
        anime = get_jikan_anime_info(url, args.title)
        if not anime:
            print(f"No match found for {url}")
            continue
        slug = extract_slug(url)
        output_file = f"{slug}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(anime, f, indent=2, ensure_ascii=False)
        print(f"Written: {output_file}")

if __name__ == '__main__':
    main()

