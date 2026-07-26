# 各层必须调用Skill清单

> 审核agent用此文档验证分析agent的skills_used字段

## 验证规则

1. 读取trigger.json（bazi-trigger的输出）→ 提取mandatory_skills
2. 检查分析agent的skills_used是否包含mandatory_skills中的所有skill
3. 遗漏任何mandatory_skill → 审核不通过
4. 可选skill不强制，但加载了要如实填写

**⚠️ 没有trigger.json → 审核不通过（bazi-trigger未执行）**

---

## ⚠️ 条件触发Skill（第1层审核时自动检测，不可遗漏）

**以下skill在排盘后立即检测条件，命中则必须加载：**

| 条件 | 检测方法 | 必须加载skill | 遗漏后果 |
|------|----------|--------------|----------|
| 日柱同五行 | 日柱天干地支五行相同（12种：甲寅/乙卯/丙午/丁巳/戊辰/戊戌/己丑/己未/庚申/辛酉/壬子/癸亥） | bazi-hunyin-tongwuxing | 审核不通过 |
| 女命 | gender=F | bazi-fukeshengyu（⚠️在bazi-sales目录） | 审核不通过 |
| 日坐阳刃 | 日支为子（壬日）/午（丙戊日）/巳（丁己日）/亥（癸日） | bazi-fukeshengyu（女命） | 审核不通过 |
| 杂气月 | 月支为辰/戌/丑/未 | 用杂气月取格规则（大运/流年透干成格） | 审核不通过 |
| 墓库 | 地支有辰/戌/丑/未 | bazi-muku | 审核不通过 |
| 夫妻宫六害 | 日支与其他地支六害（子未/丑午/寅巳/卯辰/申亥/酉戌） | bazi-gongchuan | 审核不通过 |

**检测流程（第1层审核时执行）：**
```
1. 读取bazi.json中的日柱天干地支
2. 检查日柱是否为12种同五行日柱 → 是则必须有bazi-hunyin-tongwuxing
3. 检查gender → F则必须有bazi-fukeshengyu
4. 检查日支是否为阳刃 → 是则女命必须有bazi-fukeshengyu
5. 检查月支是否为辰戌丑未 → 是则检查是否用了杂气月取格规则
6. 检查地支是否有辰戌丑未 → 是则必须有bazi-muku
7. 检查日支是否与其他地支六害 → 是则必须有bazi-gongchuan
```

---

## 各层必须调用Skill

| 层 | 层名称 | 必须调用Skill | 条件触发skill（命中则必须） |
|----|--------|--------------|--------------------------|
| 1 | 基础排盘层 | bazi-paipan, bazi-sizhu | 同五行→bazi-hunyin-tongwuxing；女命→bazi-fukeshengyu；杂气月→动态格局；墓库→bazi-muku；日坐阳刃→bazi-fukeshengyu；夫妻宫六害→bazi-gongchuan |
| 2 | 格局核心层 | bazi-geju, bazi-shishen | bazi-dizhi（如有三会/三合局） |
| 3 | 先天禀赋层 | bazi-xingge, bazi-shishen | bazi-zhi, bazi-xiongbu, bazi-xinglengdan, bazi-haose, bazi-shencai, bazi-daogui, bazi-lanyin, bazi-dinghuo |
| 4 | 六亲关系层 | bazi-sizhu, bazi-shishen, bazi-peiou, bazi-duanpeifu, bazi-hunyin-cishu | bazi-gongchuan（夫妻宫六害时） |
| 5 | 专项运势层 | - | 按问题类型加载（见下方专项表） |
| 6 | 运势推演层 | bazi-dayun（待创建） | bazi-dizhi（流年地支关系） |
| 7 | 进阶深度层 | - | - |
| 8 | 调理建议层 | bazi-tiaoli（待创建） | - |

---

## 第5层专项Skill对照表

| 问题类型 | 必须加载Skill | 状态 |
|----------|--------------|------|
| 被女倒追 | bazi-daogui | 已有（可选） |
| 印星懒 | bazi-lanyin | 已有（可选） |
| 婚姻/配偶 | bazi-peiou, bazi-duanpeifu, bazi-gongchuan, bazi-hunyin-cishu | 已有 |
| 同五行二婚（条件触发） | bazi-hunyin-tongwuxing | 已有（仅日柱同五行时加载） |
| 事业/财运 | bazi-shiye | 待创建 |
| 健康/寿元 | bazi-weibing, bazi-feibu, bazi-shenbing, bazi-ganbing, bazi-xinzangbing | 已有 |
| 性格/天赋 | bazi-xingge | 已有 |
| 痣相 | bazi-zhi | 已有 |
| 性冷淡 | bazi-xinglengdan | 已有 |
| 胸部大小 | bazi-xiongbu | 已有 |
| 好色 | bazi-haose | 已有 |
| 脾胃病 | bazi-weibing | 已有 |
| 肺部健康 | bazi-feibu | 已有 |
| 肾病 | bazi-shenbing | 已有 |
| 肝病 | bazi-ganbing | 已有 |
| 心脏健康 | bazi-xinzangbing | 已有 |
| 丁火专题 | bazi-dinghuo | 已有 |
| 夫妻宫穿夫妻星 | bazi-gongchuan | 已有 |
| 婚姻次数判断 | bazi-hunyin-cishu | 已有 |
| 配偶类型/异性偏好 | bazi-duanpeifu | 已有 |
| 身材 | bazi-shencai | 已有 |

---

## ⚠️ 女命特殊规则（gender=F，铁律）

**触发条件**：命盘性别为女时，以下规则自动生效

### 必须加载Skill
- **bazi-fukeshengyu**：女命流产与剖腹产判断（在bazi-sales目录）

### 触发时机
- 第1层审核时自动检测gender=F → 必须加载
- 不需要用户特别指定
- 日坐阳刃（壬子/丙午/丁巳/戊午/己巳/癸亥）→ 更要加载（应验率90%+）

### 遗漏后果
- 审核不通过（严重错误）
- 女命分析缺少生育健康维度

---

## 地支关系触发规则

当分析涉及以下内容时，必须加载bazi-dizhi：
- 判断三会局/三合局对五行力量的影响
- 分析六冲对格局的破坏
- 检查六害穿夫妻宫
- 流年地支与原局地支的关系
- 断盘步骤中需要用地支关系判断

---

## 墓库触发规则（待创建bazi-muku）

当八字地支出现辰、戌、丑、未时，必须加载bazi-muku。

---

## 空亡触发规则（待创建bazi-kongwang）

每层分析都应检查空亡，如协调器指定加载bazi-kongwang，必须加载。

---

## 审核检查流程

1. 读取协调器指令 → 提取"必须加载skill"列表
2. 读取分析agent的layerX.json → 提取skills_used字段
3. 逐项对比：协调器指定的必须skill是否都在skills_used中
4. 如有遗漏 → 输出fail，列出遗漏的skill名称
5. 如全部包含 → 继续其他审核项
