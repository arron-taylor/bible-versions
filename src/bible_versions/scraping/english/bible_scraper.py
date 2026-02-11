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
    "Genesis": {50: [31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 55, 32, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26]},
    "Exodus": {40: [22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 36, 31, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38]},
    "Leviticus": {27: [17, 16, 17, 35, 19, 30, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 46, 34]},
    "Numbers": {36: [54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 50, 13, 32, 22, 29, 35, 41, 30, 25, 18, 65, 23, 31, 40, 16, 54, 42, 56, 29, 34, 13]},
    "Deuteronomy": {34: [46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 32, 18, 29, 23, 22, 20, 22, 21, 20, 23, 30, 25, 22, 19, 19, 26, 68, 29, 20, 30, 52, 29, 12]},
    "Joshua": {24: [18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33]},
    "Judges": {21: [36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25]},
    "Ruth": {4: [22, 23, 18, 22]},
    "1_Samuel": {31: [28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 15, 23, 29, 22, 44, 25, 12, 25, 11, 31, 13]},
    "2_Samuel": {24: [27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 33, 43, 26, 22, 51, 39, 25]},
    "1_Kings": {22: [53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 53]},
    "2_Kings": {25: [18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30]},
    "1_Chronicles": {29: [54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30]},
    "2_Chronicles": {36: [17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 22, 15, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23]},
    "Ezra": {10: [11, 70, 13, 24, 17, 22, 28, 36, 15, 44]},
    "Nehemiah": {13: [11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31]},
    "Esther": {10: [22, 23, 15, 17, 14, 14, 10, 17, 32, 3]},
    "Job": {42: [22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 24, 34, 17]},
    "Psalms": {150: [6, 12, 8, 8, 12, 10, 17, 9, 20, 18, 7, 8, 6, 7, 5, 11, 15, 50, 14, 9, 13, 31, 6, 10, 22, 12, 14, 9, 11, 12, 24, 11, 22, 22, 28, 12, 40, 22, 13, 17, 13, 11, 5, 26, 17, 11, 9, 14, 20, 23, 19, 9, 6, 7, 23, 13, 11, 11, 17, 12, 8, 12, 11, 10, 13, 20, 7, 35, 36, 5, 24, 20, 28, 23, 10, 12, 20, 72, 13, 19, 16, 8, 18, 12, 13, 17, 7, 18, 52, 17, 16, 15, 5, 23, 11, 13, 12, 9, 9, 5, 8, 28, 22, 35, 45, 48, 43, 13, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 13, 10, 7, 12, 15, 21, 10, 20, 14, 9, 6]},
    "Proverbs": {31: [33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31]},
    "Ecclesiastes": {12: [18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14]},
    "Song_of_Solomon": {8: [17, 17, 11, 16, 16, 13, 13, 14]},
    "Isaiah": {66: [31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 12, 25, 24]},
    "Jeremiah": {52: [19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34]},
    "Lamentations": {5: [22, 22, 66, 22, 22]},
    "Ezekiel": {48: [28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 49, 32, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35]},
    "Daniel": {12: [21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13]},
    "Hosea": {14: [11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 14, 16, 9]},
    "Joel": {3: [20, 32, 21]},
    "Amos": {9: [15, 16, 15, 13, 27, 14, 17, 14, 15]},
    "Obadiah": {1: [21]},
    "Jonah": {4: [17, 10, 10, 11]},
    "Micah": {7: [16, 13, 12, 13, 15, 16, 20]},
    "Nahum": {3: [15, 13, 19]},
    "Habakkuk": {3: [17, 20, 19]},
    "Zephaniah": {3: [18, 15, 20]},
    "Haggai": {2: [15, 23]},
    "Zechariah": {14: [21, 13, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21]},
    "Malachi": {4: [14, 17, 18, 6]},
    "Matthew": {28: [25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20]},
    "Mark": {16: [45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20]},
    "Luke": {24: [80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 53]},
    "John": {21: [51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25]},
    "Acts": {28: [26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 41, 38, 40, 30, 35, 27, 27, 32, 44, 31]},
    "Romans": {16: [32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27]},
    "1_Corinthians": {16: [31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24]},
    "2_Corinthians": {13: [24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14]},
    "Galatians": {6: [24, 21, 29, 31, 26, 18]},
    "Ephesians": {6: [23, 22, 21, 32, 33, 24]},
    "Philippians": {4: [30, 30, 21, 23]},
    "Colossians": {4: [29, 23, 25, 18]},
    "1_Thessalonians": {5: [10, 20, 13, 18, 28]},
    "2_Thessalonians": {3: [12, 17, 18]},
    "1_Timothy": {6: [20, 15, 16, 16, 25, 21]},
    "2_Timothy": {4: [18, 26, 17, 22]},
    "Titus": {3: [16, 15, 15]},
    "Philemon": {1: [25]},
    "Hebrews": {13: [14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25]},
    "James": {5: [27, 26, 18, 17, 20]},
    "1_Peter": {5: [25, 25, 22, 19, 14]},
    "2_Peter": {3: [21, 22, 18]},
    "1_John": {5: [10, 29, 24, 21, 21]},
    "2_John": {1: [13]},
    "3_John": {1: [14]},
    "Jude": {1: [25]},
    "Revelation": {22: [20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 17, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21]}
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
    
    def build_url(self, book: str, chapter: int, verse: int) -> str:
        """Build BibleHub URL for a specific verse, handling special cases like Song of Solomon."""
        # Map internal book name to BibleHub URL
        book_url_map = {
            "Song_of_Solomon": "songs"
        }
        book_url = book_url_map.get(book, book.lower())
        return f"https://biblehub.com/{book_url}/{chapter}-{verse}.htm"
    
    def fetch_page(self, url: str, book: str = None, chapter: int = None, verse: int = None) -> Optional[str]:
        """Fetch HTML content from URL with retry logic. Cache HTML locally for each verse."""
        cache_dir = Path("html_cache") / (book if book else "unknown")
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{chapter}-{verse}.htm" if (chapter and verse) else None
        # Try to load from cache first
        if cache_file and cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    logger.info(f"Loaded HTML from cache: {cache_file}")
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not read cache file {cache_file}: {e}")
        # Otherwise, fetch from the web
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
        if not translations:
            logger.warning(f"No translations found in verse page")
        return translations
    def scrape_verse(self, book: str, chapter: int, verse: int) -> bool:
        """Scrape a single verse page and extract all translations."""
        # Check if already completed
        if self.is_verse_completed(book, chapter, verse):
            logger.debug(f"Skipping already completed: {book} {chapter}:{verse}")
            return True
        
        # Build URL and fetch
        url = self.build_url(book, chapter, verse)
        logger.info(f"Scraping: {book} {chapter}:{verse}")
        # Use fetch_page with caching
        html_content = self.fetch_page(url, book, chapter, verse)
        if not html_content:
            logger.error(f"Failed to fetch: {url}")
            return False
        
        # Parse all translations from this verse page
        translations = self.parse_verse_page(html_content)
        
        if not translations:
            logger.warning(f"No translations extracted from {url}")
            return False
        
        # Store in data structure organized by translation -> book -> chapter -> verse
        for translation_name, verse_text in translations.items():
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
        
        logger.info(f"Successfully scraped {len(translations)} translations for {book} {chapter}:{verse}")
        
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
