#!/usr/bin/env python3
"""Build a map of locales to available versions and short codes.

This script scans a `versions_gz` directory that has the following structure:

    versions_gz/
        en/
            AMERICAN STANDARD VERSION.json.gz
            NEW INTERNATIONAL VERSION.json.gz
            ...
        es/
            REINA VALERA 1909.json.gz
            ...
        und/
            ALEPPO CODEX.json.gz
            ...

For each locale directory, it discovers all `*.json.gz` files and
constructs a mapping of:

    {
        "en": {
            "AMERICAN STANDARD VERSION": "ASV",   # example
            "NEW INTERNATIONAL VERSION": "NIV",   # example
            ...
        },
        "es": {
            "REINA VALERA 1909": "RV1909",
            ...
        },
        ...
    }

By default, this script uses a simple heuristic to derive a short code
from the version name (based on word initials, etc.), since the
canonical codes are not embedded in the filenames. If you already have
an authoritative mapping for some versions (e.g. English ones), you can
edit `KNOWN_CODES` below to override the heuristic for those names.

Usage:

    python build_locale_version_map.py \
        --versions-dir versions_gz \
        --output-file locale_version_map.py

The default `--versions-dir` is `versions_gz`, and the default
`--output-file` is `locale_version_map.py` (a Python file containing a
`LOCALE_VERSION_MAP` dict).
"""

import argparse
import json
import re
from pathlib import Path
from pprint import pformat


# Optional: seed this with any known, authoritative codes you care about.
# Keys are exact version names as they appear in filenames (without
# the `.json.gz` suffix), values are the short codes you want.
KNOWN_CODES = {
    # Core English/BibleHub-friendly versions
    "NEW INTERNATIONAL VERSION": "NIV",
    "NEW LIVING TRANSLATION": "NLT",
    "ENGLISH STANDARD VERSION": "ESV",
    "BEREAN STUDY BIBLE": "BSB",
    "KING JAMES BIBLE": "KJV",
    "NEW KING JAMES VERSION": "NKJV",
    "AMPLIFIED BIBLE": "AMP",
    "CHRISTIAN STANDARD BIBLE": "CSB",
    "HOLMAN CHRISTIAN STANDARD BIBLE": "HCSB",
    "CONTEMPORARY ENGLISH VERSION": "CEV",
    "GOOD NEWS TRANSLATION": "GNT",
    "AMERICAN STANDARD VERSION": "ASV",
    "DARBY BIBLE TRANSLATION": "DBY",
    "DOUAY-RHEIMS BIBLE": "DRB",
    "EASY-TO-READ VERSION": "ERV",  # if present under a slightly different name, heuristic will still apply
    "GOD'S WORD® TRANSLATION": "GWT",
    "INTERNATIONAL STANDARD VERSION": "ISV",
    "NEW HEART ENGLISH BIBLE": "NHEB",
    "ORTHODOX JEWISH BIBLE": "OJB",
    "NEW AMERICAN STANDARD BIBLE": "NASB",
    "NASB 1977": "NASB77",
    "NASB 1995": "NASB95",
    "NEW AMERICAN BIBLE": "NAB",
    "THE MESSAGE": "MSG",
    "YOUNG'S LITERAL TRANSLATION": "YLT",
    "WORLD ENGLISH BIBLE": "WEB",
    "NEW REVISED STANDARD VERSION": "NRSV",
    "REVISED STANDARD VERSION": "RSV",
    "NEW CENTURY VERSION": "NCV",
    "NEW INTERNATIONAL READER'S VERSION": "NIRV",
    "GENEVA BIBLE": "GNV",
    "LEXHAM ENGLISH BIBLE": "LEB",
    "JUBILEE BIBLE 2000": "JUB",

    # Additional English/public-domain or well-known variants from your files
    "BEREAN LITERAL BIBLE": "BLB",
    "BRENTON SEPTUAGINT TRANSLATION": "BST",
    "CATHOLIC PUBLIC DOMAIN VERSION": "CPDV",
    "ENGLISH REVISED VERSION": "ERV",  # shares abbreviation; context will disambiguate
    "GODBEY NEW TESTAMENT": "GNT",      # distinct from GNT2 but user-facing code may still be GNT
    "GOOD NEWS TRANSLATION": "GNT2",
    "HAWEIS NEW TESTAMENT": "HNT",
    "JPS TANAKH 1917": "JPS",
    "KING JAMES 2000 BIBLE": "KJ2000",
    "LAMSA BIBLE": "LAMSA",
    "LEGACY STANDARD BIBLE": "LSB",
    "LITERAL STANDARD VERSION": "LSV",
    "MACE NEW TESTAMENT": "MNT",
    "MAJORITY STANDARD BIBLE": "MSB",
    "NET BIBLE": "NET",
    "PESHITTA HOLY BIBLE TRANSLATED": "PESHITTA",
    "SMITH'S LITERAL TRANSLATION": "SLT",
    "WEBSTER'S BIBLE TRANSLATION": "WBT",
    "WEYMOUTH NEW TESTAMENT": "WNT",
    "WORRELL NEW TESTAMENT": "WORRELL",
    "WORSLEY NEW TESTAMENT": "WORSLEY",

    # Additional English versions in en/
    "ANDERSON NEW TESTAMENT": "ANT",
    "ARAMAIC BIBLE IN PLAIN ENGLISH": "ABPE",
    "SHUAR NEW TESTAMENT": "SHUARNT",
    "UMA NEW TESTAMENT": "UMANT",

    # Afrikaans
    "AFRIKAANS PWL": "AFRPWL",

    # Arabic
    "ARABIC: SMITH & VAN DYKE": "ARASVD",

    # Bavarian
    "BAVARIAN": "BAV",

    # Bulgarian
    "BULGARIAN": "BUL",

    # Czech
    "CZECH BKR": "BKR",

    # Danish
    "DANISH": "DAN",

    # German
    "GERMAN: LUTHER (1912)": "LUTH1912",
    "GERMAN: MODERNIZED": "GERMOD",
    "GERMAN: TEXTBIBEL (1899)": "TEXTBIBEL1899",

    # Greek
    "GREEK NT: TISCHENDORF 8TH ED. - TRANSLITERATED": "TNT8TR",
    "GREEK ORTHODOX CHURCH 1904": "GOC1904",
    "NESTLE GREEK NEW TESTAMENT 1904 - TRANSLITERATED": "NGNT1904TR",
    "NESTLE GREEK NEW TESTAMENT 1904": "NGNT1904",
    "SWETE'S SEPTUAGINT": "SWETELXX",

    # Esperanto
    "ESPERANTO": "ESP",

    # Spanish (note: filenames may contain Mojibake, keys match exact filenames)
    "LA BIBLIA DE LAS AMÃ©RICAS": "LBLA",
    "LA NUEVA BIBLIA DE LOS HISPANOS": "LNBH",
    "REINA VALERA 1909": "RV1909",
    "REINA VALERA GÃ³MEZ": "RVG",
    "SAGRADAS ESCRITURAS 1569": "SE1569",
    "TAGALOG: ANG DATING BIBLIA (1905)": "ADB1905",

    # Finnish
    "FINNISH: BIBLE (1776)": "FIN1776",

    # French
    "FRENCH: DARBY": "FRDBY",
    "FRENCH: LOUIS SEGOND (1910)": "LS1910",
    "FRENCH: MARTIN (1744)": "MR1744",

    # Hebrew
    "WESTMINSTER LENINGRAD CODEX": "WLC",
    "WLC (CONSONANTS ONLY)": "WLC-CONSONANTS",

    # Croatian
    "CROATIAN BIBLE": "CRO",

    # Hungarian
    "HUNGARIAN: KAROLI": "KAROLI",

    # Armenian
    "ARMENIAN (WESTERN): NT": "ARMWNT",

    # Indonesian
    "INDONESIAN - TERJEMAHAN LAMA (TL)": "IDTL",

    # Italian
    "ITALIAN: GIOVANNI DIODATI BIBLE (1649)": "IGD1649",
    "ITALIAN: RIVEDUTA BIBLE (1927)": "IRIV1927",

    # Korean
    "KOREAN": "KOR",

    # Latin
    "LATIN: VULGATA CLEMENTINA": "VULGCL",

    # Lithuanian
    "LITHUANIAN": "LIT",

    # Latvian
    "LATVIAN NEW TESTAMENT": "LAVNT",

    # Maori
    "MAORI": "MAO",

    # Dutch
    "DUTCH STATEN VERTALING": "DSV",

    # Norwegian
    "NORWEGIAN: DET NORSK BIBELSELSKAP (1930)": "DNB1930",

    # Portuguese (filenames include accented characters as-is)
    "BÃBLIA KING JAMES ATUALIZADA PORTUGUÃªS": "BKJA",
    "PORTUGESE BIBLE": "POR",

    # Romanian
    "ROMANIAN: CORNILESCU": "ROCORN",

    # Russian
    "RUSSIAN KOI8R": "RUKOI8R",
    "RUSSIAN: SYNODAL TRANSLATION (1876)": "RUSYNO1876",

    # Albanian
    "ALBANIAN": "ALB",

    # Swedish
    "SWEDISH (1917)": "SWE1917",

    # Swahili
    "SWAHILI NT": "SWHNT",

    # Thai
    "THAI: FROM KJV": "THKJV",

    # Turkish
    "TURKISH": "TUR",

    # Ukrainian
    "UKRAINIAN: NT": "UKRNT",

    # Undetermined-language scholarly texts and others under und/
    "ALEPPO CODEX": "ALEPPO",
    "AMERICAN KING JAMES VERSION": "AKJV",
    "BASQUE (NAVARRO-LABOURDIN): NT": "BSQNT",
    "KABYLE: NT": "KABNT",
    "RP BYZANTINE MAJORITY TEXT 2005": "RP2005",
    "SCRIVENER'S TEXTUS RECEPTUS (1894) - TRANSLITERATED": "TR1894TR",
    "SCRIVENER'S TEXTUS RECEPTUS 1894": "TR1894",
    "STEPHANUS TEXTUS RECEPTUS 1550": "TR1550",
    "STEPHENS TEXTUS RECEPTUS (1550) - TRANSLITERATED": "TR1550TR",
    "TAWALLAMAT TAMAJAQ NT": "TTNT",
    "TISCHENDORF 8TH EDITION": "TISCH8",
    "WESTCOTT AND HORT 1881 - TRANSLITERATED": "WH1881TR",
    "WESTCOTT AND HORT 1881": "WH1881",

    # Vietnamese
    "VIETNAMESE (1934)": "VIE1934",

    # Chinese
    "CHINESE BIBLE: UNION (SIMPLIFIED)": "CUNPSS",
    "CHINESE BIBLE: UNION (TRADITIONAL)": "CUNPTR",
}


def derive_code(version_name: str) -> str:
    """Derive a short-ish code for a version name.

    Preference order:
    1. If the name is in KNOWN_CODES, use that.
    2. Otherwise, build an acronym from the words.
    """

    if version_name in KNOWN_CODES:
        return KNOWN_CODES[version_name]

    # Strip any parenthetical year/notes to keep codes small, e.g.
    # "GERMAN: LUTHER (1912)" -> "GERMAN: LUTHER" for acronym purposes.
    base = re.sub(r"\s*\([^)]*\)", "", version_name)

    words = re.findall(r"[A-Za-z0-9]+", base.upper())
    if not words:
        cleaned = re.sub(r"[^A-Za-z0-9]+", "", version_name.upper())
        return cleaned or "UNKNOWN"

    # Take initials of the words. If that ends up too short, fall back.
    initials = "".join(w[0] for w in words)
    if len(initials) >= 2:
        return initials

    # Fallback: collapse the whole title to alnum and truncate
    cleaned = re.sub(r"[^A-Za-z0-9]+", "", "".join(words))
    return cleaned or "UNKNOWN"


def build_locale_version_map(versions_dir: str) -> dict:
    root = Path(versions_dir)
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Versions directory does not exist or is not a directory: {root}")

    locale_map: dict[str, dict[str, str]] = {}

    for locale_dir in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")):
        locale = locale_dir.name
        versions: dict[str, str] = {}

        for path in sorted(locale_dir.iterdir()):
            if not path.is_file():
                continue
            if not path.name.endswith(".json"):
                continue
            if path.name == "available":
                continue

            version_name = path.name[:-5]  # strip .json.gz
            code = derive_code(version_name)
            versions[version_name] = code

        if versions:
            locale_map[locale] = versions

    return locale_map


def write_python_map(output_file: str, locale_map: dict) -> None:
    out_path = Path(output_file)
    content = "# Auto-generated by build_locale_version_map.py\n" "LOCALE_VERSION_MAP = " + pformat(locale_map, sort_dicts=True) + "\n"
    out_path.write_text(content, encoding="utf-8")


def write_json_map(output_file: str, locale_map: dict) -> None:
    out_path = Path(output_file)
    out_path.write_text(json.dumps(locale_map, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a locale->version-name->code map from versions_gz.")
    parser.add_argument(
        "--versions-dir",
        "-v",
        default="versions_gz",
        help="Directory containing locale subfolders with *.json.gz files (default: versions_gz)",
    )
    parser.add_argument(
        "--output-file",
        "-o",
        default="locale_version_map.json",
        help="Output file path. If it ends with .json, a JSON file is written; otherwise a Python file with LOCALE_VERSION_MAP is written (default: locale_version_map.py)",
    )

    args = parser.parse_args()

    locale_map = build_locale_version_map(args.versions_dir)

    if args.output_file.lower().endswith(".json"):
        write_json_map(args.output_file, locale_map)
    else:
        write_python_map(args.output_file, locale_map)


if __name__ == "__main__":
    main()
