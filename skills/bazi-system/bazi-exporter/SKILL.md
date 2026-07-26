---
name: bazi-exporter
description: 八字输出Agent。把审核通过的分析结果标准化为JSON文件，供回复Agent读取。触发词：导出八字、保存分析。
tags: [bazi, 导出, exporter]
triggers:
  - "导出八字"
  - "保存分析"
---

# 八字输出Agent

## 职责

把审核通过的分析文本标准化为analysis.json，供回复Agent读取。

## 输入

- 审核通过的分析文本
- bazi.json（排盘数据）
- 问题类型

## 输出

`references/analysis.json`

## JSON结构

```json
{
  "meta": {
    "input": {
      "year": 1987,
      "month": 9,
      "day": 12,
      "hour": 6,
      "gender": "M"
    },
    "question_type": "婚姻",
    "timestamp": "2026-07-06T12:00:00"
  },
  "bazi": {
    "pillars": {
      "year": "丁卯",
      "month": "己酉",
      "day": "甲子",
      "hour": "庚午"
    },
    "day_master": "甲木",
    "body_strength": "身强",
    "geju": "正官格",
    "yongshen": ["正官", "财星"],
    "jishen": ["比劫", "食伤"],
    "five_elements": {
      "金": 2,
      "木": 1,
      "水": 1,
      "火": 2,
      "土": 2
    }
  },
  "analysis": {
    "xingge": {
      "riyuan": "甲木：正直公正、领导力强、宁折不弯...",
      "rizhi_piqi": "子水坐食神：急脾气...",
      "liangtougua": "无（年干丁≠时干庚）",
      "sixiu_xinxing": {
        "nianzhu": "公众人设：...",
        "yuezhu": "社交性格：...",
        "rizhu": "真实本我：...",
        "shizhu": "深层隐秘：..."
      },
      "xiangchu": "对方五行...，应该..."
    },
    "peifu": {
      "wuxing": "子水：聪明灵活、体型圆润、皮肤偏黑、灵动飘逸",
      "shishen": "食神：开朗乐观、懂生活、能一起吃喝玩乐",
      "wuhe": "甲木合己土：喜欢丰腴厚重、有内在美型",
      "zonghe": "综合画像：聪明幽默的暖男..."
    },
    "hunyin": "...",
    "dayun": "...",
    "shishen_analysis": "...",
    "wuxing_analysis": "..."
  },
  "conclusions": [
    "结论1：...",
    "结论2：...",
    "结论3：..."
  ],
  "advice": "建议：..."
}
```

## 提取规则

### 从分析文本中提取

1. **bazi字段**：从排盘数据直接复制
2. **xingge字段**：提取性格分析的5个维度
3. **peifu字段**：提取配偶画像的4个部分
4. **conclusions**：提取分析中的核心结论（列表）
5. **advice**：提取综合建议

### 标准化格式

- 每个字段必须有值，不能为空
- 用"..."表示需要从分析文本中填充的内容
- 时间戳自动生成

## 输出路径

```
~/.hermes/profiles/main/skills/bazi-sales/references/analysis.json
```

## 关键规则

1. **必须审核通过后才能导出**
2. **JSON字段必须完整**，不能遗漏
3. **保留原始分析文本的关键表述**
4. **conclusions要简洁**，每条一句话
