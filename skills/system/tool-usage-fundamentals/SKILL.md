---
name: tool-usage-fundamentals
description: Fundamental tool usage rules and file type handling patterns. Prevents common mistakes like using vision_analyze on text files or Excel spreadsheets.
triggers:
  - file reading
  - text files
  - Excel files
  - vision_analyze
  - read_file
  - file type detection
---

# Tool Usage Fundamentals

## Core Rule: Match Tool to File Type

**Wrong approach**: Try one tool, fail, try another, fail, use wrong tool as last resort.
**Right approach**: Identify file type FIRST, then use the correct tool.

## File Type → Tool Mapping

| File Type | Correct Tool | Wrong Tool |
|-----------|--------------|------------|
| Text files (.txt, .md, .json, .csv, .js, .py, .html) | `read_file` | ~~vision_analyze~~ |
| Images (.png, .jpg, .gif, .bmp) | `vision_analyze` | ~~read_file~~ |
| Excel (.xlsx, .xls) | Python openpyxl / Node XLSX | ~~vision_analyze~~ |
| PDF | `ocr-and-documents` skill | ~~vision_analyze~~ |
| Word (.docx) | Python-docx / LibreOffice | ~~vision_analyze~~ |

## Pitfall: Never Use vision_analyze on Non-Image Files

**What happened**: Agent tried to read an Excel file with `vision_analyze` after Python/Node failed. User correctly called this out: "这里面都是文本文档，你干嘛要识图呢" (These are all text documents, why use image recognition?)

**Why it's wrong**: `vision_analyze` sends files to a vision model that expects images. Text/Excel files are not images — the model cannot interpret them correctly.

**Correct sequence when file reading fails**:
1. Identify the file type (extension, content)
2. Use the appropriate library/tool for that type
3. If primary tool fails, check: is the file corrupted? wrong path? missing dependency?
4. NEVER fall back to `vision_analyze` as a "last resort" for non-image files

## Excel-Specific Handling

When Python openpyxl fails:
1. Check if file exists: `ls -la <path>`
2. Check if openpyxl is installed: `pip show openpyxl`
3. Try alternative: Node.js `xlsx` library
4. If all fail, report the error — don't try vision_analyze

```bash
# Python approach
python -c "import openpyxl; wb = openpyxl.load_workbook('file.xlsx')..."

# Node approach  
node -e "const XLSX = require('xlsx'); const wb = XLSX.readFile('file.xlsx')..."
```

## Session Learning

This skill was created after user correction: "你有毛病啊，这里面都是文本文档，你干嘛要识图呢"

The agent had:
1. Failed to read Excel with Python (dependency issue)
2. Failed to read with Node (dependency issue)
3. WRONG: Used `vision_analyze` as "last resort"
4. User correctly identified this as a fundamental error

**Lesson**: File type detection is step ZERO. Never skip it.