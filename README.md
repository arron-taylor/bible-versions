# 📖 Bible Versions JSON Dataset

A free, open-source collection of **35 complete English Bible versions** in **JSON format**, structured by book, chapter, and verse.  
This is the **most comprehensive JSON dataset of complete English Bible translations** available, including popular versions like **NLT, NIV, NKJV, NASB, ESV, KJV, and more**.  
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
	•	Iterate through chapters or verses
	•	Build Bible search tools
	•	Compare translations
	•	Feed data into apps, websites, or AI/NLP models


	•	✅ Top-level keys = Book names
	•	✅ Second-level keys = Chapter numbers
	•	✅ Third-level keys = Verse numbers

🧠 Use Cases
	•	Bible apps and APIs
	•	AI and NLP text analysis
	•	Theological research
	•	Cross-version comparison tools
	•	Verse similarity or embedding models
	•	Scripture memorization apps

🛠️ Contributing

Pull requests are welcome!
If you’d like to:
	•	Add new versions
	•	Fix formatting or verse issues
	•	Improve data consistency

…please open a PR or issue.

❤️ Acknowledgments

Data was collected and structured to make Scripture easier to study, compare, and use in digital projects.
Special thanks to open Bible resources and the developer community for keeping these texts accessible.
