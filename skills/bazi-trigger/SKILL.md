---
name: bazi-trigger
description: "八字条件触发检测Agent。排盘后自动检测所有条件触发规则，输出trigger.json供分析Agent和审核Agent使用。触发词：条件检测、触发检测、skill检测。"
tags: ["bazi", "触发", "trigger", "检测"]
triggers:
  - "条件检测"
  - "触发检测"
  - "skill检测"
---

# 八字条件触发检测Agent

## 职责

排盘完成后（bazi.json生成后），自动检测所有条件触发规则，输出`trigger.json`。

**这个Agent是排盘后的第一步，分析Agent和审核Agent都依赖它的输出。**

## 输入

- `bazi.json`（排盘数据）

## 输出

- `trigger.json`（条件触发清单）

## 输出格式

```json
{
  "conditions": {
    "同五行日柱": {
      "detected": true,
      "day_pillar": "壬子",
      "reason": "壬水坐子水，天干地支同属水",
      "skill": "bazi-hunyin-tongwuxing",
      "skill_dir": "bazi-system"
    },
    "女命": {
      "detected": true,
      "gender": "F",
      "skill": "bazi-fukeshengyu",
      "skill_dir": "bazi-sales"
    },
    "日坐阳刃": {
      "detected": true,
      "day_branch": "子",
      "yangren_of": "壬水",
      "skill": "bazi-fukeshengyu",
      "skill_dir": "bazi-sales"
    },
    "杂气月": {
      "detected": true,
      "month_branch": "辰",
      "canggan": ["戊土", "乙木", "癸水"],
      "rule": "动态格局（大运/流年透干成格）",
      "skill": null
    },
    "墓库": {
      "detected": true,
      "branches": ["辰"],
      "skill": "bazi-muku",
      "skill_dir": "bazi-system"
    },
    "夫妻宫六害": {
      "detected": false,
      "skill": null
    }
  },
  "mandatory_skills": [
    {"name": "bazi-hunyin-tongwuxing", "dir": "bazi-system", "reason": "日柱壬子=同五行"},
    {"name": "bazi-fukeshengyu", "dir": "bazi-sales", "reason": "女命+日坐阳刃"},
    {"name": "bazi-muku", "dir": "bazi-system", "reason": "地支有辰"}
  ]
}
```

## 检测规则（共6项）

### 规则1：日柱同五行

**检测方法：** 日柱天干地支五行是否相同

**12种同五行日柱：**
| 五行 | 日柱 |
|------|------|
| 木 | 甲寅、乙卯 |
| 火 | 丙午、丁巳 |
| 土 | 戊辰、戊戌、己丑、己未 |
| 金 | 庚申、辛酉 |
| 水 | 壬子、癸亥 |

**命中 → 必须加载 bazi-hunyin-tongwuxing**

### 规则2：女命

**检测方法：** gender == "F"

**命中 → 必须加载 bazi-fukeshengyu**（⚠️在bazi-sales目录）

### 规则3：日坐阳刃

**检测方法：** 日支为阳刃
| 日干 | 阳刃 |
|------|------|
| 壬 | 子 |
| 癸 | 亥 |
| 丙 | 午 |
| 戊 | 午 |
| 丁 | 巳 |
| 己 | 巳 |

**命中 → 女命必须加载 bazi-fukeshengyu**

### 规则4：杂气月

**检测方法：** 月支为辰/戌/丑/未

**命中 → 格局判定必须用杂气月取格规则（大运/流年透干成格）**

不需要加载额外skill，但分析Agent必须知道这个规则。

### 规则5：墓库

**检测方法：** 地支中有辰/戌/丑/未

**命中 → 必须加载 bazi-muku**

### 规则6：夫妻宫六害

**检测方法：** 日支与其他地支形成六害
| 六害组合 |
|----------|
| 子未害 |
| 丑午害 |
| 寅巳害 |
| 卯辰害 |
| 申亥害 |
| 酉戌害 |

**命中 → 必须加载 bazi-gongchuan**

## 执行流程

```bash
cd ~/.hermes/profiles/main/skills/bazi-system/bazi-trigger
node scripts/check_conditions.js <bazi.json路径>
```

或由协调器调用：
```
1. 读取bazi.json
2. 逐条检测6项规则
3. 输出trigger.json
4. 将trigger.json路径传给分析Agent和审核Agent
```

## 与其他Agent的关系

```
bazi-paipan → bazi.json
                ↓
            bazi-trigger → trigger.json
                ↓                    ↓
        分析Agent（读trigger.json加载skill）
                ↓
        审核Agent（读trigger.json检查skill是否加载）
```

## Pitfalls

- ⚠️ 这个Agent在排盘后、分析前执行，不可跳过
- ⚠️ 输出的trigger.json必须包含mandatory_skills列表
- ⚠️ 分析Agent必须加载mandatory_skills中的所有skill
- ⚠️ 审核Agent必须检查skills_used是否包含mandatory_skills
- ⚠️ 杂气月不加载额外skill，但分析Agent必须用动态格局规则
