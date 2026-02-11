# Quick Start Guide

## Setup (5 minutes)

1. **Install Python** (if not already installed):
   - Download from [python.org](https://www.python.org/downloads/)
   - Requires Python 3.7 or higher

2. **Install the project**:
  In the root folder of the repository install the project with the following command:
   ```bash
   pip install -e .
   ```

3. **Run the scraper**:
   ```bash
   bible-scraper --output bible_data.json
   ```

That's it! The script will start scraping and save to `bible_data.json`.

## Full Scrape

Once you've verified it works, run the full scrape:

```bash
bible-scraper --output bible_data.json
```

**Time estimate**: 8-10 hours for all 22 versions
**Output size**: 50-200 MB JSON file

## Monitor Progress

Watch the scraper work:

```bash
# In another terminal, watch the log file
tail -f bible_scraper.log
```

## HTML Cache

As it scrapes, the script saves a local copy of each verse page HTML under `html_cache/` (organized by book). On resume/re-runs it will read from this cache first, which reduces repeat downloads and helps you recover faster from network issues.

## If Interrupted

Just run with the `--resume` flag:

```bash
bible-scraper --resume --output bible_data.json
```

It will continue where it left off!

## Optional: Split into individual JSON files per translation

After `bible_data.json` is complete, you can split it into one file per translation:

```bash
separate-versions --input bible_data.json --output-dir versions
```

This creates `versions/` with files like `NIV.json`, `KJV.json`, etc.

## Use Your Data

### Python Example

```python
import json

# Load the Bible data
with open('bible_data.json', 'r', encoding='utf-8') as f:
    bible = json.load(f)

# Get a specific verse
verse = bible["NIV"]["John"]["3"]["16"]
print(verse)

# Get all of John 3
for verse_num, verse_text in bible["NIV"]["John"]["3"].items():
    print(f"John 3:{verse_num} - {verse_text}")

# Compare versions
versions = ["NIV", "KJV", "ESV"]
for ver in versions:
    print(f"{ver}: {bible[ver]['Genesis']['1']['1']}")
```

### Script is slow
- Default delay is 1 second between requests (to be polite)
- You can reduce `REQUEST_DELAY` in the script, but be respectful!
- Consider running overnight

### Out of memory
- The script saves after every chapter, so you won't lose progress
- Final JSON file is large but should fit in memory on most systems
- If needed, you can scrape versions one at a time

### Network issues
- The script has built-in retry logic
- Use `--resume` if disconnected
- Check your internet connection

## Tips for Success

1. ✅ **Start small**: Test with 1-2 versions first
2. ✅ **Run overnight**: Full scrape takes many hours
3. ✅ **Stable connection**: Use wired internet if possible
4. ✅ **Watch the logs**: Monitor `bible_scraper.log` for issues
5. ✅ **Backup often**: Copy `bible_data.json` periodically
6. ✅ **Verify data**: Run verification script when done

## What You Get

A JSON file structured like this:

```json
{
  "NIV": {
    "Genesis": {
      "1": {
        "1": "In the beginning God created...",
        "2": "Now the earth was formless...",
        ...
      }
    }
  },
  "KJV": { ... },
  ...
}
```

Easy lookup: `bible[version][book][chapter][verse]`

## Need Help?

- Check `bible_scraper.log` for detailed error messages
- See README.md for full documentation
- Verify BibleHub is accessible in your region
- Check that version abbreviations match BibleHub's codes

## Legal Note

This is for personal/educational use. Bible translations have different copyright restrictions. For public or commercial use, verify licensing terms.

