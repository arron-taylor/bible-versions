#!/usr/bin/env python3
"""
Separate Bible Versions - Splits bible_data.json into individual files per translation.

This script reads the main bible_data.json file and creates separate JSON files
for each translation/version found in the data.

Usage:
    python separate_versions.py [--input bible_data.json] [--output-dir versions/]
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict

def separate_versions(input_file: str, output_dir: str) -> None:
    """
    Separate all Bible versions from the main JSON file into individual files.
    
    Args:
        input_file: Path to the main bible_data.json file
        output_dir: Directory to save individual version files
    """
    # Check if input file exists
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load the main bible data
    print(f"Loading data from {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            bible_data = json.load(f)
    except Exception as e:
        print(f"Error loading {input_file}: {e}")
        sys.exit(1)
    
    # Check the structure
    if not isinstance(bible_data, dict):
        print("Error: Expected bible_data to be a dictionary")
        sys.exit(1)
    
    print(f"Found {len(bible_data)} translations/versions")
    
    # Separate each version into its own file
    for version_code, version_data in bible_data.items():
        # Create a clean filename from the version code
        filename = f"{version_code}.json"
        output_file = output_path / filename
        
        # Count total verses for this version
        verse_count = 0
        if isinstance(version_data, dict):
            for book, chapters in version_data.items():
                if isinstance(chapters, dict):
                    for chapter, verses in chapters.items():
                        if isinstance(verses, dict):
                            verse_count += len(verses)
        
        print(f"  - Writing {version_code}: {verse_count} verses -> {output_file}")
        
        # Save this version to its own file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"    Error writing {output_file}: {e}")
            continue
    
    print(f"\n✓ Successfully separated {len(bible_data)} versions into {output_dir}")
    print(f"\nFiles created:")
    for file in sorted(output_path.glob("*.json")):
        size_kb = file.stat().st_size / 1024
        print(f"  - {file.name} ({size_kb:.1f} KB)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Separate Bible translations from main JSON into individual files'
    )
    parser.add_argument(
        '--input', '-i',
        default='bible_data.json',
        help='Input JSON file containing all versions (default: bible_data.json)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='versions',
        help='Output directory for individual version files (default: versions/)'
    )
    
    args = parser.parse_args()
    
    separate_versions(args.input, args.output_dir)


if __name__ == "__main__":
    main()
