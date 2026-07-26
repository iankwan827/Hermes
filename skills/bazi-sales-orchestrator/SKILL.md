---
name: bazi-sales-orchestrator
description: 八字销售多Agent协调器。管理诊断→话术生成→质检→成交的完整工作流，自动路由数据，管理Agent间通信，降低单个Agent的上下文压力。
---

# 八字销售多Agent协调系统

## 系统架构

```
用户输入 (年月日时 + 客户反馈)
    ↓
[Agent0-协调器] ← 管理流程、路由数据、状态维护
    ↓
    ├─→ [Agent1-诊断顾问] ← 解析八字、生成诊断报告（八层体系，含性格画像）
    ├─→ [Agent6-寿命判断] ← 执行七步法、生成寿元分析
    ├─→ [Agent2-话术生成] ← 根据诊断+寿元生成销售话术
    ├─→ [Agent4-质检员] ← 验证话术数据准确性
    ├─→ [Agent3-成交专家] ← 实时指导销售成交
    └─→ 输出给用户
```

## 各Agent的职责与上下文

### Agent0 - 协调器（本文件）
**职责**：
- 接收用户输入和反馈
- 判断当前流程阶段
- 路由请求到对应Agent
- 管理Agent间数据流转
- 维护客户会话状态

**⚠️ 关键规则：输出控制**
- Agent1-解析、Agent2-图书管理员、Agent5-话术生成的中间输出**不要发送给用户**
- 协调器在内部静默完成所有Agent调用
- Agent4质检通过后，**只输出最终合并的完整销售方案**（诊断报告+话术集+质检结果）
- 用户只需要看到最终结果，不需要看到中间过程

**⚠️ 关键规则：排盘数据源**
- 第一步必须运行JS排盘脚本：`node scripts/generate_bazi_analysis.js <年> <月> <日> <时> <性别>`
- 读取生成的 `references/<年月日时性别>.md` 作为排盘数据源
- **绝对禁止**用Python手算或AI推算排盘

**⚠️ 关键规则：排盘数据源**
- **不要用自写脚本计算四柱**，必须用可靠库（cnlunar）或用户提供排盘工具输出
- cnlunar用法: `cnlunar.Lunar(date=datetime(年,月,日,时,0), godType='12TianGang')`
- cnlunar在 `uv python` 环境中可用（`$(uv python find 3.11)`），不在系统python中
- cnlunar不提供大运数据 → 大运需要用户确认或按规则计算（并让用户校验）
- 排盘结果必须经过Agent4验证后才能进入话术生成环节

**加载的上下文**：
- ✓ 完整的流程定义
- ✓ 各Agent的接口规范
- ✓ 状态机定义

### Agent1 - 诊断顾问
**职责**：解析八字、生成诊断报告
**加载的上下文**：
- ✓ bazi_result.json
- ✓ 诊断规则
- ✓ **bazi-kongwang**（排盘后检查日柱旬首，有空亡则加载）
- ✓ **bazi-muku**（地支出现辰戌丑未时加载）

### Agent6 - 寿命判断专家
**职责**：执行七步法判断寿命、生成寿元分析报告
**加载的上下文**：
- ✓ 排盘数据（日主、十神、五行分布）
- ✓ 特征卡（Agent1输出）
- ✓ bazi-sales/references/14_寿命七步法.md

**触发条件**：当客户询问健康、寿命、寿元、疾病相关话题时自动调用

### Agent2 - 话术生成
**职责**：根据诊断+寿元分析生成销售话术
**加载的上下文**：
- ✓ 诊断报告
- ✓ 寿元分析报告（Agent6输出）
- ✓ 话术模板
- ✓ 知识库

### Agent4 - 质检员
**职责**：验证话术数据准确性
**加载的上下文**：
- ✓ bazi_result.json
- ✓ 生成的话术
- ✓ 验证规则

### Agent3 - 成交专家
**职责**：实时指导销售成交
**加载的上下文**：
- ✓ 对话历史
- ✓ 当前话术集
- ✓ 成交策略

## 流程状态机（八层体系）

```
状态1: 等待输入 → 收到年月日时
状态2: 排盘中 → JS脚本生成bazi_result.json
状态3: 八层分析 → Agent1按八层体系完成诊断
    ├ 第一层：排盘基础
    ├ 第二层：格局核心（用神忌神）
    ├ 第三层：性格画像（7维度：日主/脾气/两头挂/内外/心性/组合/综合）
    ├ 第四层：天赋方向
    ├ 第五层：六亲关系
    ├ 第六层：专项运势
    ├ 第七层：大运流年推演
    └ 第八层：调理建议
状态4: 寿命判断 → Agent6工作中（健康/寿命话题时触发）
状态5: 生成话术 → Agent2根据八层诊断+寿元生成话术
状态6: 质检中 → Agent4验证话术与八层数据匹配
状态7: 输出方案 → 给用户
状态8: 等待反馈 → 收到客户反馈
状态9: 成交指导 → Agent3工作中
状态10: 循环 → 回到状态8
```

## 与bazi-master的关系

bazi-master是通用八字分析的多Agent架构，bazi-sales-orchestrator是销售场景的专用架构。两者共享相同的排盘Agent和审核逻辑，但：
- bazi-master：通用分析，输出analysis.json → 回复Agent
- bazi-sales-orchestrator：销售转化，输出话术 → 成交Agent

新项目如需通用分析功能，优先用bazi-master。

## 数据流转规范

### Agent1 → Agent6
```json
{
  "feature_card": {
    "day_master": "甲木",
    "body_strength": "身强",
    "core_ten_gods": [...],
    "features": [...]
  },
  "bazi_data": {
    "year_pillar": "...",
    "month_pillar": "...",
    "day_pillar": "...",
    "hour_pillar": "...",
    "five_elements": {...}
  }
}
```

### Agent6 → Agent2
```json
{
  "lifespan_analysis": {
    "day_master_vitality": "日主旺相，根基稳固",
    "shouyuan_star": "食神为寿元，旺而有生",
    "protection": "印星有力，禄神健旺",
    "five_elements_balance": "五行基本均衡",
    "shensha_warning": "无重大凶煞",
    "suiyun_timing": "大运不冲寿元星",
    "verdict": "长寿型（80岁以上）",
    "confidence": "95%",
    "key_factors": ["食伤旺相", "印禄护日主", "五行均衡"],
    "risk_factors": [],
    "adjustment_advice": "保持现有生活方式，注意岁运防护"
  }
}
```

### Agent2 → Agent4
```json
{
  "diagnosis_report": {...},
  "speech_set": {
    "opening": "...",
    "calibration": [...],
    "deep": "...",
    "closing": "..."
  }
}
```

### Agent4 → Agent0
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": []
}
```

### Agent0 → Agent3
```json
{
  "customer_feedback": "客户说的话",
  "dialog_history": [...],
  "current_speech_set": {...}
}
```