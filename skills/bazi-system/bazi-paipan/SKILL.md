---
name: bazi-paipan
description: 八字排盘skill。运行JS脚本排盘，输出bazi.json和各层json。被排盘Agent使用。
tags: [bazi, 排盘, paipan]
triggers:
  - "排盘"
  - "生成八字"
---

# 八字排盘Skill

## 职责

运行JS脚本排盘，输出标准化json文件。

## 脚本位置

```
scripts/
├── generate_bazi_analysis.js    # 主排盘脚本
├── paipan_node_core.js          # 核心排盘逻辑
├── bazi_classes.js              # 天干地支类
├── bazi_interpreter.js          # 特征检测
├── shishen_geshi.js             # 十神格式
├── shishen_wangshuai.js         # 十神旺衰
└── verify_bazi.js               # 验证脚本
```

## 执行命令

```bash
cd ~/.hermes/profiles/main/skills/bazi-paipan && node scripts/generate_bazi_analysis.js <年> <月> <日> <时> <性别>
```

- 年/月/日/时：数字
- 性别：M（男）或 F（女）
- 时=小时（0-23），不传分钟

## 输出文件

脚本输出到 `references/<年月日时性别>.md`

## ⚠️ 已知问题

1. **性别bug**：脚本可能忽略gender参数，输出"女命"。必须检查输出性别是否与输入一致
2. **子时处理**：23:00-23:59算第二天子时（日期+1，hour=0）
3. **十神标注**：脚本输出的十神可能有误，需审核Agent校验

## 🚨 致命陷阱：绝对不能手算十神

**AI手算十神错误率极高，已被用户多次纠正。** 典型错误：
- 甲木见丁火：AI常算成食神，实际是**伤官**（阳生阴=伤官）
- 甲木见酉金：AI常算成七杀，实际是**正官**（酉阴金克甲阳木=异性克=正官）
- 甲木见卯木：AI常算成比肩，实际是**劫财**（卯阴木帮甲阳木=异性帮=劫财）

**正确流程：用户给八字 → 立即跑JS排盘脚本 → 读取脚本输出的十神 → 绝不手算。**

即使用户只给了天干地支（如"丁卯年己酉月甲子日丁卯时"），也要推算公历年份后跑脚本。丁卯年=1987年，己酉月=农历八月≈公历9月，用近似日期跑即可。

## 输出格式

读取生成的md文件，提取以下信息输出为bazi.json：

```json
{
  "input": { "year": 1987, "month": 9, "day": 12, "hour": 6, "gender": "M" },
  "pillars": {
    "year":  { "gan": "丁", "zhi": "卯", "shishen": "伤官" },
    "month": { "gan": "己", "zhi": "酉", "shishen": "正财" },
    "day":   { "gan": "甲", "zhi": "子", "shishen": "日主" },
    "hour":  { "gan": "丁", "zhi": "卯", "shishen": "伤官" }
  },
  "canggan": {
    "year": ["乙"],
    "month": ["辛"],
    "day": ["癸"],
    "hour": ["丁"]
  },
  "shishen_distribution": { "比肩": 0, "劫财": 0, "食神": 0, "伤官": 2, ... },
  "five_elements": { "金": 2, "木": 1, "水": 1, "火": 2, "土": 2 },
  "kongwang": "戌亥"
}
```

## 关键规则

1. **必须用JS脚本排盘**，不能手算或AI推算
2. **输出性别必须检查**，与输入不一致则手动修正
3. **十神需审核Agent校验**，脚本可能有误
