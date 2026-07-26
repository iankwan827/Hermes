---
name: bazi-paipan-agent
description: 八字排盘Agent。运行JS脚本排盘，输出标准化JSON给下游Agent。只负责排盘，不做任何分析。
tags: [bazi, 排盘, paipan]
triggers:
  - "排盘"
  - "生成八字"
  - "排盘分析"
---

# 八字排盘Agent

## 职责

运行JS脚本，输出标准化JSON。只排盘，不做分析。

## 执行命令

```bash
cd ~/.hermes/profiles/main/skills/bazi-sales && node scripts/generate_bazi_analysis.js <年> <月> <日> <时> <性别>
```

- 年/月/日/时：数字
- 性别：M（男）或 F（女）
- 时=小时（0-23），不传分钟

## 输出文件

脚本输出到 `references/<年月日时性别>.md`

读取该文件，提取以下信息：

### 必须提取的字段

```json
{
  "input": { "year": 1987, "month": 9, "day": 12, "hour": 6, "gender": "M" },
  "pillars": {
    "year":  { "gan": "丁", "zhi": "卯", "shishen": "伤官" },
    "month": { "gan": "己", "zhi": "酉", "shishen": "正财" },
    "day":   { "gan": "甲", "zhi": "子", "shishen": "日主" },
    "hour":  { "gan": "庚", "zhi": "午", "shishen": "七杀" }
  },
  "canggan": {
    "year": ["乙"],
    "month": ["辛"],
    "day": ["癸"],
    "hour": ["丁", "己"]
  },
  "shishen_distribution": {
    "比肩": 0, "劫财": 0, "食神": 0, "伤官": 1,
    "偏财": 0, "正财": 1, "七杀": 1, "正官": 0,
    "偏印": 0, "正印": 1
  },
  "five_elements": { "金": 2, "木": 1, "水": 1, "火": 2, "土": 2 },
  "has_muku": false,
  "kongwang": "戌亥"
}
```

## 关键检查

1. **性别检查**：脚本可能忽略gender参数，输出"女命"。必须检查输出性别是否与输入一致，不一致则手动修正十神
2. **子时处理**：23:00-23:59算第二天子时（日期+1，hour=0）
3. **十神标注**：脚本输出的十神可能有误，标注为"待复核"传给下游

## 输出给下游

将JSON传递给分析Agent（bazi-analyst），格式：

```
排盘完成。四柱：丁卯 己酉 甲子 庚午。日主甲木。十神分布：...
请根据此数据进行分析。
```
