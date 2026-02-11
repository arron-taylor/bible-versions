# 📖 Bible Versions JSON Scraper
 
<a href="https://www.buymeacoffee.com/arrontaylor" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

Due to copyright restrictions, this repository does **not** include any Bible translation text.
Instead, it provides scripts that let you scrape Bible translations across **37 languages** from **BibleHub.com** and store them as **JSON** for your own usage.
 
Each translation can be stored as its own `.json` file for easy parsing, analysis, app development, or AI projects.

## � Quick start
 
Step-by-step installation instructions live [here](src/bible_versions/scraping/QUICKSTART.md)
 
This repo includes scrapers for:
 
- **English**
  - [`bible-scraper --help`](src/bible_versions/scraping/english/bible_scraper.py)
- **Multi-language**
  - [`bible-scraper-multi-lang --help`](src/bible_versions/scraping/multi_language/bible_scraper_multi.py)
- **Apocrypha**
  - [`bible-scraper-apoc --help`](src/bible_versions/scraping/apocrypha/bible_scraper.py)
 
And a utility to split a combined scrape into one file per version:
 
- [`separate-versions --help`](src/bible_versions/scraping/separate_versions.py)

Other misc scripts:

- [`apply-book-name-map  --help`](src/bible_versions/scraping/multi_language/helpers/apply_book_name_mapping.py)
- [`build-book-name-map --help`](src/bible_versions/scraping/multi_language/helpers/build_book_name_mapping.py)
- [`build-locale-map --help`](src/bible_versions/scraping/multi_language/helpers/build_locale_version_map.py)
- [`organize-versions-by-locale --help`](src/bible_versions/scraping/multi_language/helpers/organize_versions_by_locale.py)
 
## 📁 What files you get
 
- **Combined output**
  A single `bible_data.json` containing all scraped versions.
- **Per-version files (optional)**
  Use the `seperate-versions` tool to create a `versions/` folder with one JSON per translation/version.
- **HTML cache**
  The scrapers store cached verse HTML under `html_cache/` inside each scraper folder.
- **Progress file**
  The scrapers maintain `scraper_progress.json` so you can resume an interrupted scrape.

## 🗂️ Structure

The combined `bible_data.json` is stored as:
 
`VERSION -> Book -> Chapter -> Verse`

```json
{
  "NIV": {
    "Genesis": {
      "1": {
        "1": "In the beginning God created the heavens and the earth.",
        "2": "Now the earth was formless and empty..."
      }
    }
  }
}
```

- ✅ Top-level keys = Version codes/names
- ✅ Second-level keys = Book names
- ✅ Third-level keys = Chapter numbers
- ✅ Fourth-level keys = Verse numbers

## 🧠 Use Cases

- Bible apps and APIs
- AI and NLP text analysis
- Theological research
- Cross-version comparison tools
- Verse similarity or embedding models
- Scripture memorization apps

## Disclaimer

The Bible text formatted by the script(s) in this repository is for educational, personal, non-commercial, and reference purposes only.

Many of the Bible translations you may scrape are protected by copyright and may not be legally redistributed or used in other projects without explicit permission from their respective copyright holders.

Bible text is retrieved from BibleHub.com. Use of this content may be subject to BibleHub's Terms of Service and the individual licenses for each Bible translation. Some translations (such as KJV, ASV, YLT, and WEB) are in the public domain and may be freely used. Others (e.g., ESV, NIV, NLT, NASB, etc.) are licensed, and require permission for redistribution or certain uses.

You are solely responsible for ensuring you have the proper rights or licenses before using, distributing, or publishing any of these translations.

If you fork this repository, you must maintain compliance with all applicable copyright laws and licensing requirements. Forking does not grant you any additional rights to distribute or use copyrighted Bible translations beyond what is explicitly permitted by their respective copyright holders.

This project does not claim ownership of any Bible text and is not affiliated with BibleHub or any copyright holder.

## 🛠️ Contributing

Pull requests are welcome! If you’d like to:

- Add new versions
- Fix formatting or verse issues
- Improve data consistency

…please open a PR or issue.


## ❤️ Acknowledgments

Data was collected and structured to make Scripture easier to study, compare, and use in digital projects.
Special thanks to open Bible resources and the developer community for keeping these texts accessible.