#!/usr/bin/env python3
"""
Bible Scraper - Scrapes Bible verses from BibleHub for multiple translations
and stores them in a structured JSON format.

This version scrapes individual verse pages (e.g. genesis/1-1.htm) which contain
all translations on a single page, making it more efficient and reliable.

Usage:
    python bible_scraper.py [--resume] [--output bible_data.json]
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import html
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bible_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Bible structure: Book name -> Number of chapters -> Number of verses per chapter
# This is a comprehensive map of the entire Bible
BIBLE_STRUCTURE = {
    "1 Esdras": {9: [36, 37, 41, 42, 56, 38, 40, 40, 55]},
    "2 Esdras": {16: [40, 36, 40, 44, 48, 58, 50, 40, 41, 44, 44, 57, 48, 53, 48, 41]},
    "Tobit": {14: [21, 22, 17, 21, 22, 23, 22, 21, 23, 22, 22, 24, 22, 25]},
    "Judith": {16: [16, 16, 19, 17, 20, 21, 19, 23, 17, 21, 19, 18, 23, 17, 20, 24]},
    "Esther (Greek)": {10: [22, 23, 15, 17, 14, 14, 24, 19, 17, 29]},
    "Wisdom of Solomon": {19: [16, 24, 19, 20, 23, 19, 20, 21, 22, 23, 19, 18, 20, 22, 21, 21, 20, 19, 21]},
    "Ecclesiasticus (Sira)": {51: [28, 32, 22, 21, 28, 23, 25, 30, 19, 29, 19, 21, 27, 20, 28, 21, 23, 30, 32, 19, 23, 27, 20, 28, 23, 25, 22, 24, 26, 26, 22, 27, 24, 28, 29, 24, 23, 31, 30, 26, 24, 28, 29, 31, 23, 26, 22, 22, 25, 30, 23]},
    "Baruch": {6: [22, 35, 38, 37, 9, 36]},
    "Epistle of Jeremiah": {1: [73]},
    "Prayer of Azariah": {1: [68]},
    "Susanna": {1: [64]},
    "Bel and the Dragon": {1: [42]},
    "Prayer of Manasseh": {1: [15]},
    "1 Maccabees": {16: [64, 70, 60, 61, 68, 63, 50, 53, 59, 70, 55, 57, 61, 61, 41, 36]},
    "2 Maccabees": {15: [36, 32, 39, 31, 39, 36, 29, 30, 38, 34, 28, 39, 40, 38, 32]}
}

# Request configuration
REQUEST_DELAY = 0  # Seconds between requests (be polite!)
# REQUEST_DELAY = 0.125  # Seconds between requests (be polite!)
# REQUEST_DELAY = 0.125  # Seconds between requests (be polite!)
REQUEST_TIMEOUT = 30  # Seconds
MAX_RETRIES = 3
RETRY_DELAY = 5  # Seconds

# User agent to identify ourselves
USER_AGENT = "Mozilla/5.0 (compatible; BibleScraperBot/2.0; Educational purposes)"

# Map internal book name to BibleHub URL slugs
BIBLE_HUB_BOOK_MAP = {
    "Song_of_Solomon": "songs",
    "1 Esdras": "1_esdras",
    "2 Esdras": "2_esdras",
    "Esther (Greek)": "esther_greek",
    "Wisdom of Solomon": "wisdom_of_solomon",
    "Ecclesiasticus (Sira)": "ecclesiasticus",
    "Epistle of Jeremiah": "epistle_of_jeremiah",
    "Prayer of Azariah": "prayer_of_azariah",
    "Bel and the Dragon": "bel_and_the_dragon",
    "Prayer of Manasseh": "prayer_of_manasseh",
    "1 Maccabees": "1_maccabees",
    "2 Maccabees": "2_maccabees"
}


class BibleScraper:
    """Main scraper class for downloading Bible verses from BibleHub."""
    
    def __init__(self, output_file: str = "bible_data.json", progress_file: str = "scraper_progress.json"):
        self.output_file = output_file
        self.progress_file = progress_file
        self.data: Dict = {}
        self.progress: Dict = {}
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        
    def load_progress(self) -> None:
        """Load progress from file to resume interrupted scraping."""
        if Path(self.progress_file).exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    self.progress = json.load(f)
                logger.info(f"Loaded progress from {self.progress_file}")
            except Exception as e:
                logger.warning(f"Could not load progress file: {e}")
                self.progress = {}
        
        # Load existing data if available
        if Path(self.output_file).exists():
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info(f"Loaded existing data from {self.output_file}")
            except Exception as e:
                logger.warning(f"Could not load output file: {e}")
                self.data = {}
    
    def save_progress(self) -> None:
        """Save current progress to file."""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save progress: {e}")
    
    def save_data(self) -> None:
        """Save scraped data to JSON file."""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved data to {self.output_file}")
        except Exception as e:
            logger.error(f"Could not save data: {e}")
    
    def is_verse_completed(self, book: str, chapter: int, verse: int) -> bool:
        """Check if a verse has already been scraped."""
        progress_key = f"{book}_{chapter}_{verse}"
        return self.progress.get(progress_key, False)
    
    def mark_verse_completed(self, book: str, chapter: int, verse: int) -> None:
        """Mark a verse as completed."""
        progress_key = f"{book}_{chapter}_{verse}"
        self.progress[progress_key] = True
        # Save progress every 10 verses
        if len(self.progress) % 10 == 0:
            self.save_progress()
    
    def build_urls(self, book: str, chapter: int, verse: int) -> List[str]:
        """Build BibleHub URLs for a specific verse, trying both catholic and apocrypha paths."""
        # Map internal book name to BibleHub URL slugs
        # These slugs are based on typical BibleHub URL structure
        book_slug = BIBLE_HUB_BOOK_MAP.get(book, book.lower().replace(' ', '_'))
        
        # Handle special cases for chapter numbering (e.g. Epistle of Jeremiah is often Chapter 6)
        chapters = [chapter]
        if book == "Epistle of Jeremiah" and chapter == 1:
            chapters.append(6)
            
        # Return list of potential paths to check
        urls = []
        for ch in chapters:
            for base in ["catholic", "apocrypha"]:
                urls.append(f"https://biblehub.com/{base}/{book_slug}/{ch}-{verse}.htm")
        return urls
    
    def fetch_page(self, url: str, book: str = None, chapter: int = None, verse: int = None, skip_fetch: bool = False) -> Optional[str]:
        """Fetch HTML content from URL with retry logic. Cache HTML locally for each verse."""
        # Determine source (catholic/apocrypha) for distinct caching
        source = "unknown"
        if "/catholic/" in url:
            source = "catholic"
        elif "/apocrypha/" in url:
            source = "apocrypha"

        # Use absolute path relative to script to avoid CWD issues
        script_dir = Path(__file__).resolve().parent
        cache_dir = script_dir / "html_cache" / (book.replace(' ', '_') if book else "unknown") / source
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{chapter}-{verse}.htm" if (chapter and verse) else None
        
        # Try to load from cache first
        if cache_file and cache_file.exists():
            try:
                # Check if file is small (might be an empty or error file)
                if cache_file.stat().st_size < 100:
                     logger.warning(f"Cache file {cache_file} is very small ({cache_file.stat().st_size} bytes), ignoring.")
                else:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            logger.info(f"Loaded HTML from cache: {cache_file}")
                            return content
            except Exception as e:
                logger.warning(f"Could not read cache file {cache_file}: {e}")
        
        if skip_fetch:
            return None

        # Otherwise, fetch from the web
        # Be polite - delay between requests only when hitting the web
        time.sleep(REQUEST_DELAY)
        for attempt in range(MAX_RETRIES):
            try:
                logger.debug(f"Fetching {url} (attempt {attempt + 1}/{MAX_RETRIES})")
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                if response.status_code == 200:
                    html_content = response.text
                    # Save to cache
                    if cache_file:
                        try:
                            with open(cache_file, 'w', encoding='utf-8') as f:
                                f.write(html_content)
                            logger.info(f"Saved HTML to cache: {cache_file}")
                        except Exception as e:
                            logger.warning(f"Could not write cache file {cache_file}: {e}")
                    return html_content
                elif response.status_code == 404:
                    logger.warning(f"Page not found: {url}")
                    return None
                else:
                    logger.warning(f"HTTP {response.status_code} for {url}")
            except requests.RequestException as e:
                logger.warning(f"Request failed for {url}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
        logger.error(f"Failed to fetch {url} after {MAX_RETRIES} attempts")
        return None
    
    def clean_verse_text(self, text: str) -> str:
        """Clean and normalize verse text. Remove all HTML tags, decode entities, and normalize whitespace."""
        if not text:
            return ""
        # Remove all HTML tags
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        # Decode HTML entities
        import html
        text = html.unescape(text)
        # Remove extra whitespace
        import re
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text
    
    def parse_verse_page(self, html_content: str) -> Dict[str, str]:
        """
        Parse HTML and extract all translation verses from a verse page.
        Returns a dictionary mapping translation names to verse text.
        Systematically extract every translation (including NIV) from <span class='versiontext'> blocks,
        collecting all text and inline tags until the next <span class='versiontext'> or a block-level tag.
        """
        # Use the more fault-tolerant html5lib parser so that malformed quote
        # entities (like stray &#8220 sequences) do not break the DOM structure
        # and hide subsequent <span class="versiontext"> blocks.
        soup = BeautifulSoup(html_content, 'html5lib')
        translations = {}

        version_spans = soup.find_all('span', class_='versiontext')
        for version_span in version_spans:
            link = version_span.find('a')
            if not link:
                continue
            translation_name = link.get_text(strip=True)
            if not translation_name:
                continue

            # Collect all text between this <span class='versiontext'> and the next <span class='versiontext'> or block-level tag
            verse_parts = []
            current = version_span.next_sibling
            def collect_text(node):
                # Recursively collect all text from node and its children
                from bs4 import NavigableString, Tag
                if isinstance(node, NavigableString):
                    text = str(node).strip()
                    if text:
                        verse_parts.append(text)
                elif isinstance(node, Tag):
                    # Stop at next translation or block-level tag
                    if node.name == 'span' and 'versiontext' in (node.get('class') or []):
                        return False
                    if node.name in ['div', 'table', 'tr', 'td', 'th', 'ul', 'ol', 'li', 'hr']:
                        return False
                    # Otherwise, collect text from children
                    for child in node.children:
                        if collect_text(child) is False:
                            return False
                return True

            # Skip whitespace and <br/>
            while current and (str(current).strip() == '' or (hasattr(current, 'name') and current.name == 'br')):
                current = current.next_sibling

            while current:
                # Stop at the next translation or a block-level tag
                stop = False
                if hasattr(current, 'name'):
                    if current.name == 'span' and 'versiontext' in (current.get('class') or []):
                        break
                    if current.name in ['div', 'table', 'tr', 'td', 'th', 'ul', 'ol', 'li', 'hr']:
                        break
                if collect_text(current) is False:
                    break
                current = current.next_sibling

            verse_text = ' '.join(verse_parts)
            verse_text = self.clean_verse_text(verse_text)
            if verse_text:
                translations[translation_name] = verse_text

        # If no translations found with versiontext spans, try the "Parallel Verses" structure
        if not translations:
            par_div = soup.find('div', id='par')
            if par_div:
                from bs4 import NavigableString
                # This structure uses images or text links followed by the verse text
                # e.g., <a href="..."><img src="/kjv.gif"></a><br>Verse text...<p>
                for a_tag in par_div.find_all('a'):
                    # Try to extract translation name from image src or link text
                    img = a_tag.find('img')
                    if img and img.get('src'):
                        trans_name = Path(img['src']).stem.upper()
                    else:
                        trans_name = a_tag.get_text(strip=True).upper()
                    
                    if not trans_name or trans_name in ["", "PARALLEL"]:
                        continue
                    
                    # Collect all text until the next <a> or <p> or <hr>
                    verse_parts = []
                    current = a_tag.next_sibling
                    while current:
                        if hasattr(current, 'name') and current.name in ['a', 'p', 'hr']:
                            break
                        if isinstance(current, NavigableString):
                            text = str(current).strip()
                            if text:
                                verse_parts.append(text)
                        elif hasattr(current, 'get_text'):
                            # For inline tags like <i>, <b>, etc.
                            text = current.get_text(strip=True)
                            if text:
                                verse_parts.append(text)
                        current = current.next_sibling
                    
                    verse_text = ' '.join(verse_parts)
                    verse_text = self.clean_verse_text(verse_text)
                    if verse_text:
                        translations[trans_name] = verse_text

        if not translations:
            logger.warning(f"No translations found in verse page")
        return translations
    def scrape_verse(self, book: str, chapter: int, verse: int) -> bool:
        """Scrape a single verse page and extract all translations."""
        # Check if already completed
        if self.is_verse_completed(book, chapter, verse):
            logger.debug(f"Skipping already completed: {book} {chapter}:{verse}")
            return True
        
        # Build URLs and try each one
        urls = self.build_urls(book, chapter, verse)
        all_translations = {}
        found_any = False
        
        # Phase 1: Check ALL candidate URLs in cache FIRST
        for url in urls:
            html_content = self.fetch_page(url, book, chapter, verse, skip_fetch=True)
            if html_content:
                translations = self.parse_verse_page(html_content)
                if translations:
                    all_translations.update(translations)
                    found_any = True
        
        # Phase 2: If nothing found in cache, try fetching from the web
        if not found_any:
            for url in urls:
                logger.info(f"Scraping: {book} {chapter}:{verse} from {url} (web fetch)")
                html_content = self.fetch_page(url, book, chapter, verse, skip_fetch=False)
                if not html_content:
                    continue
                
                translations = self.parse_verse_page(html_content)
                if translations:
                    all_translations.update(translations)
                    found_any = True
                
                # If we found it on one source, the user's "either OR" suggests we might be done
                if found_any:
                    break
        
        if not found_any:
            logger.warning(f"No translations extracted from any URLs for {book} {chapter}:{verse}")
            return False
        
        # Store in data structure organized by translation -> book -> chapter -> verse
        for translation_name, verse_text in all_translations.items():
            # Normalize translation name to uppercase code
            trans_upper = translation_name.upper()
            # Remove underscores for saving book title
            book_save = book.replace('_', ' ')
            # Initialize structure
            if trans_upper not in self.data:
                self.data[trans_upper] = {}
            if book_save not in self.data[trans_upper]:
                self.data[trans_upper][book_save] = {}
            if str(chapter) not in self.data[trans_upper][book_save]:
                self.data[trans_upper][book_save][str(chapter)] = {}
            # Store verse
            self.data[trans_upper][book_save][str(chapter)][str(verse)] = verse_text
        
        # Mark as completed
        self.mark_verse_completed(book, chapter, verse)
        
        # Save data periodically (every 10 verses)
        if len(self.progress) % 10 == 0:
            self.save_data()
        
        logger.info(f"Successfully scraped {len(all_translations)} translations for {book} {chapter}:{verse}")
        
        # Be polite - delay between requests
        time.sleep(REQUEST_DELAY)
        
        return True
    
    def scrape_all(self) -> None:
        """Scrape all books, chapters, and verses."""
        # Calculate total verses
        total_verses = 0
        for book, chapters_data in BIBLE_STRUCTURE.items():
            num_chapters = list(chapters_data.keys())[0]
            verses_per_chapter = list(chapters_data.values())[0]
            total_verses += sum(verses_per_chapter)
        
        completed = 0
        
        logger.info(f"Starting scrape of {len(BIBLE_STRUCTURE)} books, ~{total_verses} verses")
        
        for book, chapters_data in BIBLE_STRUCTURE.items():
            num_chapters = list(chapters_data.keys())[0]
            verses_per_chapter = list(chapters_data.values())[0]
            
            logger.info(f"=== Starting book: {book} ({num_chapters} chapters) ===")
            
            for chapter in range(1, num_chapters + 1):
                num_verses = verses_per_chapter[chapter - 1]
                logger.info(f"  -> Chapter {chapter} ({num_verses} verses)")
                
                for verse in range(1, num_verses + 1):
                    success = self.scrape_verse(book, chapter, verse)
                    completed += 1
                    
                    if completed % 100 == 0:
                        progress_pct = (completed / total_verses) * 100
                        logger.info(f"Progress: {completed}/{total_verses} ({progress_pct:.1f}%)")
        
        logger.info("=== Scraping completed! ===")
        self.save_data()
        self.save_progress()
        
        # Report statistics
        logger.info(f"Total verses scraped: {completed}")
        logger.info(f"Total translations found: {len(self.data)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Scrape Bible verses from BibleHub for all translations'
    )
    parser.add_argument(
        '--output', '-o',
        default='bible_data.json',
        help='Output JSON file (default: bible_data.json)'
    )
    parser.add_argument(
        '--resume', '-r',
        action='store_true',
        help='Resume from previous progress'
    )
    
    args = parser.parse_args()
    
    # Create scraper
    scraper = BibleScraper(output_file=args.output)
    
    # Load progress if resuming
    if args.resume:
        logger.info("Resume mode enabled")
        scraper.load_progress()
    
    # Start scraping
    try:
        scraper.scrape_all()
        logger.info(f"All data saved to {args.output}")
        
    except KeyboardInterrupt:
        logger.info("\nScraping interrupted by user")
        logger.info(f"Progress saved. Run with --resume to continue")
        scraper.save_data()
        scraper.save_progress()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        scraper.save_data()
        scraper.save_progress()
        sys.exit(1)


if __name__ == "__main__":
    main()
