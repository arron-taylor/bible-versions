#!/usr/bin/env python3
"""
Build Book Name Mapping - infer localized book names per translation from html_cache.

This script scans cached multilingual verse pages (e.g. html_cache/<Book>/1-1.htm),
looks at the translation labels, and attempts to infer localized book names for
translations that encode them in labels like:

    "2 Mosebog 20:8 Danish"
    "Exodus 20:8 Tagalog: Ang Dating Biblia (1905)"
    "Исход 20:8 Russian koi8r"

The goal is to build a mapping structure like:

    {
      "DANISH": {
        "Exodus": "2 Mosebog"
      },
      "TAGALOG: ANG DATING BIBLIA (1905)": {
        "Exodus": "Exodo"  # if we can infer it
      },
      ...
    }

Usage:
    python build_book_name_mapping.py \
        --cache-dir html_cache \
        --output book_name_mapping.json
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

from bs4 import BeautifulSoup


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build_book_name_mapping.log'),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def normalize_translation_label(raw_label: str) -> str:
    """Normalize a translation label into the same form used by bible_scraper_from_cache.

    We reuse the logic from parse_verse_page in bible_scraper_from_cache.py so that
    mapping keys line up with the version names in bible_data_from_cache.json.
    """
    if not raw_label:
        return ""

    import re as _re_norm

    remainder = raw_label.strip()
    m = _re_norm.search(r"\d+\s*:\s*\d+", remainder)
    if m:
        remainder = remainder[m.end():].lstrip()

    lower_rem = remainder.lower()
    if lower_rem.startswith("spanish:"):
        translation_name = remainder.split(":", 1)[1].strip()
    else:
        translation_name = remainder.strip()

    return translation_name


def extract_local_book_from_label(raw_label: str) -> Optional[str]:
    """Try to extract a localized book name from a raw translation label.

    We look for patterns like:
        "2 Mosebog 20:8 Danish"        -> "2 Mosebog"
        "Exodo 20:8 Spanish: ..."      -> "Exodo"
        "Исход 20:8 Russian koi8r"     -> "Исход"

    That is, we take the text before the first "chapter:verse" occurrence.
    """
    if not raw_label:
        return None

    import re as _re_book

    m = _re_book.search(r"(.+?)\s+\d+\s*:\s*\d+", raw_label)
    if not m:
        return None

    candidate = m.group(1).strip()
    # Heuristic: ignore very short tokens which are unlikely to be valid book names
    if len(candidate) < 2:
        return None

    return candidate


def build_book_name_mapping(cache_dir: str, output_file: str) -> None:
    cache_path = Path(cache_dir)
    if not cache_path.exists() or not cache_path.is_dir():
        logger.error("Cache directory does not exist or is not a directory: %s", cache_path)
        return

    mapping: Dict[str, Dict[str, str]] = {}

    logger.info("Scanning html_cache for 1-1.htm files to infer book names")

    for book_dir in sorted(cache_path.iterdir()):
        if not book_dir.is_dir():
            continue

        # Derive English book name used in data (underscore -> space)
        english_book = book_dir.name.replace('_', ' ')

        sample_file = book_dir / '1-1.htm'
        if not sample_file.exists():
            # Not all books may have 1:1 cached; skip for now.
            continue

        try:
            with sample_file.open('r', encoding='utf-8') as f:
                html_content = f.read()
        except Exception as e:
            logger.warning("Could not read %s: %s", sample_file, e)
            continue

        soup = BeautifulSoup(html_content, 'html.parser')
        version_spans = soup.find_all('span', class_='versiontext')

        for version_span in version_spans:
            link = version_span.find('a')
            if not link:
                continue

            raw_label = link.get_text(strip=True)
            if not raw_label:
                continue

            translation_name = normalize_translation_label(raw_label)
            if not translation_name:
                continue

            # Now try to extract the local book name from the raw label.
            local_book = extract_local_book_from_label(raw_label)
            if not local_book:
                continue

            # Store under the normalized translation key (uppercased like main scraper).
            trans_key = translation_name.upper()
            mapping.setdefault(trans_key, {})

            # Only set if we don't already have a mapping (first hit wins).
            if english_book not in mapping[trans_key]:
                mapping[trans_key][english_book] = local_book

    logger.info("Inferred localized book names for %d translations", len(mapping))

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        logger.info("Saved book name mapping to %s", output_file)
    except Exception as e:
        logger.error("Could not save mapping to %s: %s", output_file, e)


def main() -> None:
    parser = argparse.ArgumentParser(description='Infer localized book names per translation from html_cache 1-1.htm files.')
    parser.add_argument('--cache-dir', '-c', default='html_cache', help='Directory containing cached HTML files (default: html_cache)')
    parser.add_argument('--output', '-o', default='book_name_mapping.json', help='Output JSON mapping file (default: book_name_mapping.json)')

    args = parser.parse_args()

    build_book_name_mapping(args.cache_dir, args.output)


if __name__ == '__main__':
    main()
