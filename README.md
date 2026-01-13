# 📖 Bible Versions JSON Dataset

A free, open-source collection of **35 English Bible versions** and **38 total languages** in **JSON format**, structured by book, chapter, and verse. Some versions include the **Full Bible**, while others are **New Testament only**.
This is the **most comprehensive JSON dataset of English Bible translations** available, including popular versions like **NLT, NIV, NKJV, NASB, ESV, KJV, and more**.
Each translation is stored as its own `.json` file for easy parsing, analysis, app development, or AI projects.

## 🗂️ Structure

Each file represents a single Bible version (e.g., `niv.json`, `kjv.json`, `esv.json`).  
Verses are stored in a consistent JSON structure:

```json
{
  "Genesis": {
    "1": {
      "1": "In the beginning God created the heavens and the earth.",
      "2": "Now the earth was formless and empty..."
    },
    "2": { ... }
  },
  "Exodus": { ... }
}
```

This structure makes it easy to:

- Iterate through chapters or verses
- Build Bible search tools
- Compare translations
- Feed data into apps, websites, or AI/NLP models


- ✅ Top-level keys = Book names
- ✅ Second-level keys = Chapter numbers
- ✅ Third-level keys = Verse numbers

## 🧠 Use Cases

- Bible apps and APIs
- AI and NLP text analysis
- Theological research
- Cross-version comparison tools
- Verse similarity or embedding models
- Scripture memorization apps

## 📜 About Non-Canonical / Deuterocanonical Books

This dataset includes access to books often referred to as the "Apocrypha" or "Deuterocanonical" books. While not included in the standard Protestant canon of 66 books, they hold significant historical, theological, and literary value.

### Why are they important?
These texts bridge the historical gap (often called the "Intertestamental Period") between the Old and New Testaments. They provide crucial context for understanding the cultural and political landscape of Judea leading up to the time of Jesus, particularly the struggles against Hellenism and the origins of Jewish festivals like Hanukkah.

### Who follows them?
* **Catholic & Orthodox Traditions:** Recognize most of these books as **Deuterocanonical** ("second canon"), meaning they are considered inspired scripture and are used to establish doctrine.
* **Anglican & Lutheran Traditions:** Often view these books as useful for instruction and "examples of life and instruction of manners," though generally not used to establish doctrine.
* **Coptic Tradition:** Includes books like the Prayer of Manasseh in their canonical lists.

### How were they found?
Most of these books were preserved through the **Septuagint (LXX)**, the Greek translation of the Old Testament widely used by early Christians and the writers of the New Testament. In modern times, the discovery of the **Dead Sea Scrolls** at Qumran provided significant archaeological evidence, containing Hebrew and Aramaic fragments of books like Tobit and Sirach, confirming their ancient usage and circulation alongside canonical texts.

### Included Books
The following books are available in relevant versions within this dataset:

* **Tobit**
* **Judith**
* **Wisdom of Solomon**
* **Sirach (Ecclesiasticus)**
* **Baruch (including the Epistle of Jeremiah)**
* **First Maccabees**
* **Second Maccabees**
* **Prayer of Manasseh** (Found in Coptic canons; sometimes appended to Chronicles)

## 🛠️ Contributing

Pull requests are welcome! If you’d like to:

- Add new versions
- Fix formatting or verse issues
- Improve data consistency

…please open a PR or issue.

If you're feeling generous and want to see this get completed, consider supporting me below ↓

<a href="https://www.buymeacoffee.com/arrontaylor" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

## ❤️ Acknowledgments

Data was collected and structured to make Scripture easier to study, compare, and use in digital projects.
Special thanks to open Bible resources and the developer community for keeping these texts accessible.
