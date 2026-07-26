# Excel File Reading Error Case

## Date: 2026-07-26

## What Happened

Agent needed to read `E:\下载\十二长生(1).xlsx` (a Chinese astrology reference table).

### Attempted Sequence (WRONG)

1. **Python openpyxl** → Failed (dependency/module issue)
2. **Python3 openpyxl** → Failed (same issue)
3. **vision_analyze on .xlsx file** → WRONG APPROACH
4. **Node.js XLSX library** → Eventually worked

### The Mistake

After steps 1-2 failed, agent used `vision_analyze` on an Excel file:
```python
vision_analyze(
    image_url="E:\\下载\\十二长生(1).xlsx",
    question="这是什么内容？请完整读取表格中的所有数据。"
)
```

User response: "你有毛病啊，这里面都是文本文档，你干嘛要识图呢"

### Correct Approach

1. Check file exists: `ls -la "E:/下载/十二长生(1).xlsx"`
2. Try Python: `python -c "import openpyxl; ..."`
3. If fails, try Node: `node -e "const XLSX = require('xlsx'); ..."`
4. If both fail, report error — DO NOT use vision_analyze

### Root Cause

Agent treated "all tools failed" as justification to try vision_analyze, which is only for images. Excel files contain structured data that vision models cannot interpret.

## Prevention

- File extension `.xlsx` / `.xls` = Excel = use openpyxl or XLSX library
- File extension `.png` / `.jpg` / `.gif` = Image = use vision_analyze
- File extension `.txt` / `.md` / `.json` = Text = use read_file
- NEVER use vision_analyze as fallback for non-image files