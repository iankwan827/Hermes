---
name: documents
description: "PDF & document operations: extract text from PDFs/scans (pymupdf, marker-pdf) and edit PDF text via natural language (nano-pdf)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, documents, OCR, extraction, editing, pymupdf, marker-pdf, nano-pdf]
---

# Documents — PDF Extraction & Editing

Two complementary skills for PDF and document operations: extraction (pymupdf, marker-pdf) and editing (nano-pdf).

## When to use

- User wants to extract text from a PDF or scanned document
- User wants to edit text/typos/titles in a PDF
- User needs OCR on a scanned document
- User wants to split, merge, or search within PDFs
- User has a DOCX with embedded images that need OCR

## Skill Selection

| Need | Skill | Tool |
|------|-------|------|
| Extract text from PDF/scans, split/merge/search PDFs | **ocr-and-documents** | pymupdf, marker-pdf, web_extract |
| Edit PDF text via natural language instructions | **nano-pdf** | nano-pdf CLI |

## ocr-and-documents — PDF Extraction & Manipulation

### Decision: pymupdf vs marker-pdf

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| Text-based PDF | ✅ | ✅ |
| Scanned PDF (OCR) | ❌ | ✅ (90+ languages) |
| Tables | ✅ (basic) | ✅ (high accuracy) |
| Equations/LaTeX | ❌ | ✅ |
| Code blocks | ❌ | ✅ |
| Speed | Instant | ~1-14s/page (CPU) |
| Install size | ~25MB | ~3-5GB |

**Default:** Use pymupdf unless you need OCR, equations, forms, or complex layout.

### Quick Start
```bash
# pymupdf (lightweight)
pip install pymupdf pymupdf4llm
python scripts/extract_pymupdf.py document.pdf --markdown

# marker-pdf (high-quality OCR)
pip install marker-pdf
python scripts/extract_marker.py document.pdf --use_llm

# Remote URL (always try first)
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
```

### Split, Merge, Search
```python
import pymupdf
# Split
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")

# Merge
result = pymupdf.open()
for path in ["a.pdf", "b.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")

# Search
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
```

### DOCX Embedded Images
When a DOCX contains screenshots/images (not text), extract and OCR them:
```python
import zipfile
with zipfile.ZipFile(docx_path, 'r') as z:
    for name in z.namelist():
        if name.startswith('word/media/') and name.lower().endswith(('.png', '.jpg')):
            img_data = z.read(name)
```
**Pitfall:** Large images (98MP+ from scrolling captures) → downscale before processing.

## nano-pdf — Edit PDFs via Natural Language

### Quick Start
```bash
uv pip install nano-pdf
nano-pdf edit report.pdf 1 "Change the title to 'Q3 Results'"
nano-pdf edit deck.pdf 3 "Update the date from January to February 2026"
```

### Notes
- Page numbers may be 0-based or 1-based — retry with ±1 if wrong page
- Uses LLM under the hood — requires API key
- Works well for text changes; complex layout may need different approach
