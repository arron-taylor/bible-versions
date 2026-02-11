#!/usr/bin/env python3
"""
Apply Book Name Mapping - replace English book names in per-version JSON files
with localized book names using book_name_mapping.json.

This script expects:

- A directory of version JSON files, e.g. versions/NEW INTERNATIONAL VERSION.json
- A mapping file book_name_mapping.json of the form:

    {
      "AFRIKAANS PWL": {
        "Exodus": "Eksodus",
        "1 Chronicles": "1 Kronieke",
        ...
      },
      ...
    }

For each version file, it derives the version key from the filename (without
.extension), uppercases it, and if that key exists in the mapping, it will
rename book keys in the JSON according to the mapping for that version.

Usage:
    python apply_book_name_mapping.py \
        --versions-dir versions \
        --mapping-file book_name_mapping.json
"""

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def load_mapping(mapping_file: str) -> Dict[str, Dict[str, str]]:
    path = Path(mapping_file)
    if not path.exists():
        raise FileNotFoundError(f"Mapping file not found: {mapping_file}")
    with path.open('r', encoding='utf-8') as f:
        mapping = json.load(f)
    if not isinstance(mapping, dict):
        raise ValueError("Mapping file must contain a JSON object at the top level")
    return mapping


def apply_mapping_to_version_file(filepath: Path, mapping: Dict[str, Dict[str, str]]) -> None:
    version_name = filepath.stem  # filename without .json
    version_key = version_name.upper()

    if version_key not in mapping:
        logger.debug("No book-name mapping for version '%s' (file %s)", version_key, filepath.name)
        return

    book_map = mapping[version_key]
    if not isinstance(book_map, dict):
        logger.warning("Invalid book map for version '%s' in mapping file", version_key)
        return

    # Load the version data
    try:
        with filepath.open('r', encoding='utf-8') as f:
            data: Dict[str, Any] = json.load(f)
    except Exception as e:
        logger.error("Could not load %s: %s", filepath, e)
        return

    if not isinstance(data, dict):
        logger.warning("Skipping %s: expected top-level object (got %s)", filepath, type(data))
        return

    new_data: Dict[str, Any] = {}
    changed = False

    for english_book, chapters in data.items():
        # Determine localized name if available
        local_book = book_map.get(english_book)
        if local_book:
            changed = True
            target_name = local_book
        else:
            target_name = english_book

        # If there is a collision (two English books mapping to same local name), merge
        if target_name in new_data and isinstance(new_data[target_name], dict) and isinstance(chapters, dict):
            # Merge chapters, later entries override
            new_data[target_name].update(chapters)
        else:
            new_data[target_name] = chapters

    if not changed:
        logger.info("No book-name changes for %s", filepath.name)
        return

    # Save back to file
    try:
        with filepath.open('w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        logger.info("Applied book-name mapping to %s", filepath.name)
    except Exception as e:
        logger.error("Error writing %s: %s", filepath, e)


def main() -> None:
    parser = argparse.ArgumentParser(description='Apply localized book name mapping to per-version JSON files.')
    parser.add_argument('--versions-dir', '-v', default='versions', help='Directory containing per-version JSON files (default: versions)')
    parser.add_argument('--mapping-file', '-m', default='book_name_mapping.json', help='JSON file with book name mappings (default: book_name_mapping.json)')

    args = parser.parse_args()

    try:
        mapping = load_mapping(args.mapping_file)
    except Exception as e:
        logger.error("Failed to load mapping file: %s", e)
        return

    versions_path = Path(args.versions_dir)
    if not versions_path.exists() or not versions_path.is_dir():
        logger.error("Versions directory does not exist or is not a directory: %s", versions_path)
        return

    files = [p for p in versions_path.iterdir() if p.suffix == '.json']
    logger.info("Applying book-name mapping to %d version files in %s", len(files), versions_path)

    for filepath in sorted(files):
        apply_mapping_to_version_file(filepath, mapping)

    logger.info("Book-name mapping application completed.")


if __name__ == '__main__':
    main()
