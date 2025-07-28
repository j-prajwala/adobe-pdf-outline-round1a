# Adobe India Hackathon – Round 1A

## 🚀 Challenge: Connecting the Dots - Document Outline Extraction

This project extracts structured outlines from raw PDF files. It identifies the title and heading hierarchy (H1, H2, H3) using font size and formatting information.

---

## 📁 Folder Structure
## 📁 Folder Structure

```
ADOBE_PROJECT/
├── input/              # Folder for input PDF files
├── output/             # Folder where output JSONs are saved
├── src/
│   └── extract_headings.py  # Main script
├── Dockerfile
├── requirements.txt
└── README.md
```
---

## 🧠 Approach

- We use **PyMuPDF** (`fitz`) to extract text blocks and font metadata.
- All font sizes from the document are collected and sorted.
- Thresholds are computed for H1, H2, and H3 based on the top 3 distinct font sizes.
- If text matches a top font size and length conditions, it is assigned a heading level.
- A JSON file is generated with:
  - `"title"` (from first page)
  - `"outline"` list of headings with level and page number

Example Output:
```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
---

## 🛠 How to Build and Run

### 🧱 Step 1: Build the Docker Image

Make sure you are inside the project folder (where your Dockerfile is), then run:

```bash
docker build -t adobe-outline-extractor .
---

## ⚙️ Environment

- Python 3.10 (in Docker container)
- PyMuPDF (for PDF parsing)
- Runs fully offline
- Compatible with CPU-only (amd64)
---

## 📌 Constraints Met

- [x] Execution Time ≤ 10 seconds for a 50-page PDF
- [x] Model Size ≤ 200MB (no model used)
- [x] Runs on CPU (amd64)
- [x] Fully offline – no internet access needed
---

## ✨ Notes

- Uses font-size-based heuristic to assign heading levels.
- Designed to generalize across various document layouts.
- Script automatically processes all PDFs in the input folder.

 

