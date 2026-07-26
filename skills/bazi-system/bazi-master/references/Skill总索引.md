# 八字多Agent系统 — Skill总索引

> 最后更新：2026-07-06

## 系统架构

```
用户输入 → bazi-master(协调器)
              ↓
    ┌─────────────────────┐
    │ Agent1: 排盘Agent    │ → 输出 bazi.json
    │ Agent1.5: 定位Agent  │ → 输出分析方向
    │ Agent2: 分析Agent    │ → 分层输出分析文本
    │ Agent3: 审核Agent    │ → 校验
    │ Agent4: 输出Agent    │ → 输出 analysis.json
    │ Agent5: 回复Agent    │ → 唯一对外输出
    └─────────────────────┘
```

---

## Agent清单（7个）

| Agent | 路径 | 职责 |
|-------|------|------|
| bazi-master | bazi-system/bazi-master/ | 协调器，指挥整个分析流程 |
| bazi-analyst | bazi-system/bazi-analyst/ | 分析Agent，执行各层分析 |
| bazi-reviewer | bazi-system/bazi-reviewer/ | 审核Agent，校验分析结果 |
| bazi-paipan | bazi-system/bazi-paipan/ | 排盘Agent，运行JS脚本出四柱 |
| bazi-finder | bazi-system/bazi-finder/ | 定位Agent，确定分析方向 |
| bazi-exporter | bazi-system/bazi-exporter/ | 输出Agent，汇总JSON |
| bazi-responder | bazi-system/bazi-responder/ | 回复Agent，生成用户可读的回复 |

---

## Skill清单（bazi-system目录，32个）

### 基础知识类

| Skill | 路径 | 内容 | 触发条件 |
|-------|------|------|----------|
| bazi-shishen | bazi-system/bazi-shishen/ | 十神分类、详解、组合、实战应用 | 始终 |
| bazi-dizhi | bazi-system/bazi-dizhi/ | 地支关系：三会/三合/六冲/刑害/优先级 | 地支关系分析 |
| bazi-sizhu | bazi-system/bazi-sizhu/ | 四柱代表、宫位分析 | 始终 |
| bazi-geju | bazi-system/bazi-geju/ | 格局判定、用神忌神推导 | 始终 |

### 专项分析类

| Skill | 路径 | 内容 | 触发条件 |
|-------|------|------|----------|
| bazi-xingge | bazi-system/bazi-xingge/ | 性格分析 | 问性格 |
| bazi-peiou | bazi-system/bazi-peiou/ | 配偶画像分析 | 问配偶 |
| bazi-duanpeifu | bazi-system/bazi-duanpeifu/ | 断配偶偏好与异性类型 | 问配偶类型/异性偏好 |
| bazi-hunyin-tongwuxing | bazi-system/bazi-hunyin-tongwuxing/ | 上下同五行婚姻 | 问婚姻 |
| bazi-zhi | bazi-system/bazi-zhi/ | 痣相三板斧（天干/地支/土五行/丁火阴木） | 问痣相 |
| bazi-xinglengdan | bazi-system/bazi-xinglengdan/ | 性冷淡八字密码 | 问性冷淡 |
| bazi-xiongbu | bazi-system/bazi-xiongbu/ | 胸部痣分析 | 问胸部 |
| bazi-haose | bazi-system/bazi-haose/ | 好色分析 | 问好色 |
| bazi-shencai | bazi-system/bazi-shencai/ | 八字看身材 | 问身材 |
| bazi-daogui | bazi-system/bazi-daogui/ | 被女倒追特征 | 问倒追 |
| bazi-lanyin | bazi-system/bazi-lanyin/ | 印星过旺与懒 | 问懒 |

### 健康类

| Skill | 路径 | 内容 | 触发条件 |
|-------|------|------|----------|
| bazi-weibing | bazi-system/bazi-weibing/ | 脾胃病八字分析 | 问脾胃 |
| bazi-feibu | bazi-system/bazi-feibu/ | 肺部健康八字分析 | 问肺部 |
| bazi-shenbing | bazi-system/bazi-shenbing/ | 肾病八字分析 | 问肾病 |
| bazi-ganbing | bazi-system/bazi-ganbing/ | 肝部健康八字分析 | 问肝病 |
| bazi-xinzangbing | bazi-system/bazi-xinzangbing/ | 心脏健康八字分析 | 问心脏 |

### 特殊专题类

| Skill | 路径 | 内容 | 触发条件 |
|-------|------|------|----------|
| bazi-dinghuo | bazi-system/bazi-dinghuo/ | 丁火专题（性质/熬夜/背部痣/感情） | 丁火日主/问熬夜/问丁火 |
| bazi-gongchuan | bazi-system/bazi-gongchuan/ | 夫妻宫穿夫妻星（穿害/婚姻风险） | 问穿害/问婚姻/问离婚 |
| bazi-hunyin-cishu | bazi-system/bazi-hunyin-cishu/ | 婚姻次数判断（宫坏/星多） | 问婚姻次数/问几段感情 |

### 辅助工具类

| Skill | 路径 | 内容 | 触发条件 |
|-------|------|------|----------|
| bazi-baceng | bazi-system/bazi-baceng/ | 八层体系框架 | 始终 |
| bazi-duanshi | bazi-system/bazi-duanshi/ | 断事方法论 | 始终 |
| bazi-chuanzhuo | bazi-system/bazi-chuanzhuo/ | 穿着搭配 | 问穿着 |

---

## bazi-sales目录（5个，独立系统）

| Skill | 路径 | 内容 |
|-------|------|------|
| bazi-zhiduan | bazi-sales/bazi-zhiduan/ | 直断速查、28秘诀、十天干性格 |
| bazi-fukeshengyu | bazi-sales/bazi-fukeshengyu/ | 女命妇科生育直断 |
| bazi-sales-steps | bazi-sales/bazi-sales-steps/ | 销售实战步骤 |
| bazi-sales-agent6-lifespan | bazi-sales/bazi-sales-agent6-lifespan/ | 寿命判断 |
| bazi-sales | bazi-sales/ | 销售系统主入口 |

---

## 各层必须加载Skill（待补充）

> ⚠️ 以下为设计目标，部分skill尚未创建

| 层 | 层名称 | 必须调用Skill | 可选Skill |
|----|--------|--------------|-----------|
| 1 | 基础排盘层 | bazi-paipan, bazi-sizhu | bazi-kongwang（待创建） |
| 2 | 格局核心层 | bazi-geju, bazi-shishen | bazi-dizhi（如有三会/三合局） |
| 3 | 先天禀赋层 | bazi-xingge, bazi-shishen | - |
| 4 | 六亲关系层 | bazi-sizhu, bazi-shishen | bazi-muku（待创建，如有辰戌丑未） |
| 5 | 专项运势层 | - | 按问题类型加载（见专项表） |
| 6 | 运势推演层 | bazi-dayun（待创建） | bazi-dizhi（流年地支关系） |
| 7 | 进阶深度层 | - | - |
| 8 | 调理建议层 | bazi-tiaoli（待创建） | - |

---

## 第5层专项Skill对照表

| 问题类型 | 必须加载Skill | 状态 |
|----------|--------------|------|
| 过三关/快速验证 | bazi-xingge, bazi-zhi, bazi-xiongbu, bazi-xinglengdan, bazi-haose, bazi-shencai, bazi-daogui, bazi-lanyin, bazi-hunyin-tongwuxing, bazi-fukeshengyu, bazi-gongchuan, bazi-hunyin-cishu, bazi-dinghuo, bazi-duanpeifu | 已有 | ✅ |
| 婚姻/配偶 | bazi-hunyin-tongwuxing, bazi-peiou, bazi-duanpeifu | 已有 |
| 事业/财运 | bazi-shiye | 待创建 |
| 健康/寿元 | bazi-weibing, bazi-feibu, bazi-shenbing, bazi-ganbing, bazi-xinzangbing | 已有 |
| 性格/天赋 | bazi-xingge | 已有 |
| 痣相 | bazi-zhi | 已有 |
| 性冷淡 | bazi-xinglengdan | 已有 |
| 胸部大小 | bazi-xiongbu | 已有 |
| 好色 | bazi-haose | 已有 |
| 身材 | bazi-shencai | 已有 |
| 配偶类型/异性偏好 | bazi-duanpeifu | 已有 |

---

## 女命特殊规则（待补充）

> ⚠️ bazi-fukeshengyu在bazi-sales目录，尚未迁移到bazi-system

当命盘性别为女（gender=F）时，需加载 **bazi-fukeshengyu**。

---

## 排盘脚本位置

| 脚本 | 路径 |
|------|------|
| generate_bazi_analysis.js | bazi-system/bazi-paipan/scripts/ |
| generate_bazi_analysis_*.js | bazi-system/bazi-paipan/scripts/（多个版本） |

---

## 参考文档

| 文档 | 路径 | 内容 |
|------|------|------|
| 必须调用skill清单.md | bazi-reviewer/references/ | 审核agent用的skill验证规则 |
| 十神速查表.md | bazi-reviewer/references/ | 十天干×十神对照表 |
| 常见错误.md | bazi-reviewer/references/ | 17条Pitfalls |
| 分析步骤.md | bazi-master/references/ | Phase 2-9详细步骤 |
| 关键路径.md | bazi-master/references/ | 脚本位置、案例文件路径 |
