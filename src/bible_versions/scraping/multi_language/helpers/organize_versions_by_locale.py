#!/usr/bin/env python3
"""Organize gzipped per-version JSON files into locale subfolders.

This script scans a *source* versions directory for compressed files
(`*.json.gz`), infers an approximate language/locale code from the version
filename (e.g. "SPANISH", "GERMAN", "FRENCH"), and moves each `.json.gz` file
into a corresponding subdirectory under a *target* directory, such as:

    versions_gz/en/NEW INTERNATIONAL VERSION.json.gz
    versions_gz/es/REINA VALERA 1909.json.gz
    versions_gz/pt/BÍBLIA KING JAMES ATUALIZADA PORTUGUÊS.json.gz

Unknown languages are placed into an "und" (undetermined) folder.

Plain `.json` files are left untouched in the source directory.

Usage:
    python organize_versions_by_locale.py \
        --source-dir versions \
        --target-dir versions_gz
"""

import argparse
import logging
import shutil
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def detect_locale_from_name(version_name: str) -> str:
    """Heuristically infer a BCP-47-ish language code from a version name.

    This is best-effort and based on substrings in the filename.
    """
    name = version_name.lower()

    # Explicit language markers first
    if 'spanish' in name or 'reina valera' in name or ('biblia' in name and 'portugu' not in name) or 'sagradas escrituras' in name:
        return 'es'
    if 'portuge' in name or 'portugu' in name:
        return 'pt'
    if 'german' in name or 'luther' in name or 'deutsch' in name:
        return 'de'
    if 'french' in name or 'louis segond' in name or 'martin (1744)' in name:
        return 'fr'
    if 'italian' in name or 'giovanni diodati' in name or 'riveduta' in name:
        return 'it'
    if 'dutch' in name or 'staten vertaling' in name:
        return 'nl'
    if 'swedish' in name:
        return 'sv'
    if 'norwegian' in name:
        return 'no'
    if 'danish' in name:
        return 'da'
    if 'afrikaans' in name:
        return 'af'
    if 'albanian' in name:
        return 'sq'
    if 'basque' in name:
        return 'eu'
    if 'bavarian' in name:
        return 'bar'
    if 'armenian' in name:
        return 'hy'
    if 'turkish' in name:
        return 'tr'
    if 'finnish' in name:
        return 'fi'
    if 'latvian' in name:
        return 'lv'
    if 'lithuanian' in name:
        return 'lt'
    if 'hungarian' in name or 'karoli' in name:
        return 'hu'
    if 'romanian' in name:
        return 'ro'
    if 'croatian' in name:
        return 'hr'
    if 'czech' in name or 'bkr' in name:
        return 'cs'
    if 'bulgarian' in name:
        return 'bg'
    if 'maori' in name:
        return 'mi'
    if 'swahili' in name:
        return 'sw'
    if 'esperanto' in name:
        return 'eo'
    if 'indonesian' in name:
        return 'id'
    if 'vietnamese' in name:
        return 'vi'
    if 'thai' in name:
        return 'th'
    if 'korean' in name:
        return 'ko'
    if 'chinese' in name or '中文' in name or 'æœ¬' in name:
        return 'zh'
    if 'arabic' in name or 'arab' in name:
        return 'ar'
    if 'russian' in name or 'koi8r' in name:
        return 'ru'
    if 'ukrainian' in name:
        return 'uk'
    if 'greek' in name or 'septuagint' in name or 'textus receptus' in name or 'byzantine' in name or 'tischendorf' in name or 'westcott' in name:
        return 'el'
    if 'hebrew' in name or 'westminster leningrad codex' in name or 'wlc' in name or 'aleppo' in name:
        return 'he'
    if 'latin' in name or 'vulgata' in name:
        return 'la'

    # Some English-ish hints
    if (
        'english' in name
        or 'kjv' in name
        or 'king james' in name
        or 'niv' in name
        or 'nasb' in name
        or 'american standard' in name
        or 'bible' in name
        or 'testament' in name
        or "webster" in name
        or "weymouth" in name
        or "young's" in name
        or 'jubilee' in name
        or 'international version' in name
        or 'international standard version' in name
        or 'living translation' in name
        or "god's word" in name
    ):
        return 'en'

    # Default: undetermined
    return 'und'


def organize_versions(source_dir: str, target_dir: str) -> None:
    src = Path(source_dir)
    dst = Path(target_dir)
    if not src.exists() or not src.is_dir():
        logger.error("Source versions directory does not exist or is not a directory: %s", src)
        return

    # Ensure target root exists
    dst.mkdir(parents=True, exist_ok=True)

    # Collect .json and .json.gz files
    files = [
        p for p in src.iterdir() 
        if p.is_file() and (p.name.endswith('.json') or p.name.endswith('.json.gz'))
    ]
    logger.info("Found %d version files to organize from %s into %s", len(files), src, dst)

    moved_count = 0
    for path in sorted(files):
        # Determine the version name stem
        if path.name.endswith('.json.gz'):
            version_name = path.name[:-8]  # strip .json.gz
        elif path.name.endswith('.json'):
            version_name = path.name[:-5]  # strip .json
        else:
            version_name = path.stem

        locale = detect_locale_from_name(version_name)
        locale_dir = dst / locale
        locale_dir.mkdir(parents=True, exist_ok=True)

        target_path = locale_dir / path.name
        if target_path.exists():
            logger.warning("Target file already exists, skipping move: %s", target_path)
            continue

        try:
            shutil.move(str(path), str(target_path))
            moved_count += 1
            logger.info("Moved %s -> %s", path.name, target_path)
        except Exception as e:
            logger.error("Failed to move %s: %s", path, e)

    logger.info("Finished organizing. Moved %d files.", moved_count)


def main() -> None:
    parser = argparse.ArgumentParser(description='Organize gzipped version JSON files into locale subfolders.')
    parser.add_argument('--source-dir', '-s', default='versions', help='Source directory containing per-version JSON.gz files (default: versions)')
    parser.add_argument('--target-dir', '-t', default='versions_gz', help='Target directory for locale subfolders (default: versions_gz)')

    args = parser.parse_args()

    organize_versions(args.source_dir, args.target_dir)


if __name__ == '__main__':
    main()
