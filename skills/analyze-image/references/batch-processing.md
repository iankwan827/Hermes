# 批量图片处理完整流程

## Windows脚本路径
- Python: `E:\Users\Administrator\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe`
- .env: `~/AppData/Local/hermes/.env`

## 方案A: 简单批量（短图，ratio<3）
脚本 `scripts/batch_ocr.py`，max_tokens=8000。

## 方案B: 切割批量（推荐）
脚本 `scripts/full_extract.py`：
- ratio>3 或 h>8000 → 切割3000px段
- 否则整张，max_tokens=16000

## Docx提取
脚本 `scripts/extract_from_docx.py`：
- 从docx的 `word/media/` 提取图片
- 自动切割、缩放、失败跳过
- 输出到 `docs/` 目录

## 散装图片提取
脚本 `scripts/extract_loose_images.py`：
- 扫描 `images/`、`图片/` 子目录
- 排除已处理的副本目录

## 重试
- `retry_zero.py` — 批量重试0字节文件
- `retry_one.py` — 单张重试
- `retry_failed_images.py` — 重试docx提取失败的

## 课程识别+分类
提取后按内容关键词分类：案例课/五行课/婚姻课/事业课/财运课/子女课/健康课/风水课/神煞课/格局课

命名规则：`第X课_xxx.png` 或 `{分类}_{hash}.png`

## 四Agent质检（知识库整理用）
- Agent1: 标题审核
- Agent2: 逐条提取断语
- Agent3: 监控完整性
- Agent4: 条件检查

详见 `references/bazi_knowledge_organization.md`
