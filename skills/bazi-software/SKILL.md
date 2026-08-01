---
name: bazi-software
description: "八字软件开发全流程：架构设计、HTML/CSS/JS前端实现、JS分析模块开发、变量管理、调试排错、验收流程。合并了原 bazi-software-dev 和 bazi-software-debug 的所有知识。触发词：八字软件、排盘软件、开发、前端、调试、debug、bazi软件"
tags: ["bazi", "software", "development", "debugging", "javascript", "frontend"]
---

# 八字软件开发指南

> 合并自 bazi-software-dev（开发流程）和 bazi-software-debug（调试经验），提供八字软件从架构到验收的完整知识。

---

## 一、架构原则

### 1.1 JS模块化架构
每个bazi-system skill对应一个JS分析模块（analyzers/目录）。
排盘脚本（core/）输出JSON → 分析模块读取JSON → 输出分析结果JSON → 前端渲染。

### 1.2 三个标签页
- **标签一：八字命盘** — 排盘结果展示（四柱、神煞、纳音、空亡、大运、地支关系、天干五合）
- **标签二：命盘解析** — 格局判定 + 三得法分析 + 8维度取用神 + 喜用神结论
- **标签三：分析结果** — 空亡详细分析 + 性格 + 10个十神分析 + 婚姻 + 大运流年

⚠️ **格局判定在标签二，不在标签三**。标签二是命盘解析（格局+身强+喜用），标签三是断语输出。

### 1.3 分析模块清单
- base-analyzer.js（基类）
- trigger-analyzer.js（条件触发）
- geju-analyzer.js（格局判定）
- xiyong-analyzer.js（身强喜用：三得法 + 8维度取用）
- kongwang-analyzer.js（空亡）
- shishen-analyzer.js + 11个子模块（十神）
- xingge-analyzer.js（性格）
- peiou-analyzer.js（配偶）
- hunyin-analyzer.js（婚姻）
- dayun-analyzer.js（大运流年）
- orchestrator.js（协调器）

---

## 二、变量管理（关键！）

### 2.1 全局变量定义
所有关键变量必须在HTML顶部全局定义，不是函数内部：

```javascript
let sandeLevel = '';        // 三得法结果（'身强'/'身弱'/'中和'）
let tongguanMedicine = '';  // 通关用神五行
let bingyaoMedicine = '';   // 病药用神五行
let currentResult = null;   // 排盘结果对象
```

### 2.2 变量数据字典
必须维护 variable-dictionary.md，记录：
- 每个变量的数据来源
- 赋值位置（哪一行）
- 使用位置（哪些函数）

### 2.3 显示原则
**已计算的变量直接显示，不要重新计算。**
- 病药维度计算了用神=木 → 显示时直接用`bingyaoMedicine`
- 不要在显示时重新算`yxj.yong`，会覆盖正确结果

---

## 三、工作流程坑

### 3.0 ⚠️ 讨论架构时必须先听再做
**用户原话**："你没看这个系统的规划书吗"、"不对，不是这些，你的脑子有毛病"、"你在干嘛，我在和你讨论这个系统架构，你干嘛每次我说完你就去读人家文件呢"

**核心教训：用户在讨论架构时，先听完、讨论清楚，不要立刻去读文件或写代码。**

当用户让我看一个项目的架构时：
1. **先听用户说完意图**，确认理解后再行动
2. **读完所有架构文件**，总结已有模块和缺失模块
3. **讨论方案**，用户确认后再动手

**关键认知：八字性格分析系统的AI执行层**
- 用户的比喻："Claude软件=躯体，AI的key=大脑"
- 系统需要的不是自定义skill调度器，而是**内嵌Claude Code的核心能力**
- Claude Code本身就是为skill执行设计的系统（读SKILL.md、执行skill、调用API）
- 需要把Claude Code的skill执行能力 + 缓存命中能力内嵌到八字系统中

---

## 四、技术实现与调试

### 4.1 变量作用域
函数内定义的变量，其他函数访问不到 → 必须用全局变量

### 4.2 重复定义
同一个变量在多处定义 → 只在全局定义一次，函数内不要重复`let`

### 4.3 pi.hidden格式
排盘脚本的`pi.hidden`是对象数组`[{stem:"戊", god:"正财", type:"Main"}]`，不是字符串数组。访问时用`h.stem`不是`h`。

```javascript
// 错误：pi.hidden = ['戊', '辛', '丁']
// 正确：pi.hidden = [{stem:"戊", god:"正财", type:"Main"}, ...]

// 错误写法：pi.hidden.forEach(h => { ganWx(h); }); // h是对象，不是字符串
// 正确写法：pi.hidden.forEach(h => {
//   const hStem = typeof h === 'string' ? h : (h.stem || '');
//   ganWx(hStem);
// });
```

### 4.4 CHANG_SHENG表
十二长生表按天干查（甲乙丙丁...），不是按五行查（金木水火土）。
用`CHANG_SHENG[dayGan][zhi]`查状态。

### 4.5 WX_WANGXIANG表
旺相休囚死表按**月支五行**查，不是按**月支**查。
用`WX_WANGXIANG[monthWx][wx]`查状态。

### 4.6 格局取格（必须看透干，不能只看本气）⚠️ 重要
index.html中的`renderGeju`和`renderYongShen`函数必须检查**哪个藏干透干**，不能只取月令本气。

**取格优先级**：本气透干 > 中气透干 > 余气透干 > 本气虚格（仅限子午卯酉午）

**子午卯酉午特殊规则**：
- 本气不透但同五行天干透 → 也可按本气取格
- 卯：乙不透甲透 → 按乙木取格
- 酉：辛不透庚透 → 按辛金取格
- 子：癸不透壬透 → 按癸水取格
- 午：丁不透丙透 → 按丁火取格
- 午额外：丁己都不透 → 丁火虚格

**关键规则**：
- 子午卯酉午：不透干可取本气虚格（或同五行透干取格）
- 多藏干月令（申、寅、巳、亥、辰、戌、丑、未）：不透干→**不成格**

**正确做法**（公共函数，计算一次）：
```javascript
function determineGeju(dayGan, monthZhi, tiangan) {
  const monthHidden = ZHI_HIDDEN[monthZhi] || [];
  const roles = ['本气', '中气', '余气'];
  for (let i = 0; i < monthHidden.length; i++) {
    if (tiangan.includes(monthHidden[i])) {
      return { geju: getTenGod(dayGan, monthHidden[i]) + '格', source: roles[i] + '透干' };
    }
  }
  const singleZhi = ['卯', '酉', '子', '午'];
  if (singleZhi.includes(monthZhi)) {
    return { geju: getTenGod(dayGan, monthHidden[0]) + '格', source: '本气虚格' };
  }
  return { geju: '不成格', source: '月令藏干均不透干' };
}
```

### 4.7 代码重复原则（计算只用一次）⚠️ 重要
**核心原则：任何计算只做一次，结果存变量，其他地方直接用变量。**

```javascript
// ❌ 错误：到处重复计算
function renderGeju(r) { const geju = calculateGeju(...); }
function renderYongShen(r) { const geju = calculateGeju(...); }

// ✅ 正确：公共函数，调用一次
function determineGeju(dayGan, monthZhi, tiangan) { ... }
function renderGeju(r) { const result = determineGeju(...); }
function renderYongShen(r) { const result = determineGeju(...); }
```

### 4.8 空亡逻辑（容易搞错）
**日柱空亡** = 检查**日支**是否出现在年柱/月柱/时柱的空亡里（基于各自旬首）。
**年月时空亡** = 检查年支/月支/时支是否出现在**日柱的空亡里**（基于日柱的旬首）。

注意：空亡skill只做判断，不做断语。断语由各专题skill（婚姻、十神等）自行下。

### 4.9 十神分析输出规范 ⚠️ 重要
**核心原则：十神分析必须输出10个子skill的完整内容，不是摘要表格！**

**输出流程：**
1. 检测命局中显著的十神（数量≥2 / 用神 / 忌神 / 格局核心）
2. 加载对应的子skill
3. 串写输出该十神的完整内容

**串写框架**：
- 开篇定调：一句话概括命主核心特征
- 性格分析：用因果关系串联（因为...所以...这意味着...）
- 感情/事业分析：结合具体组合
- 建议/提醒：可操作的建议

### 4.10 文件读取规则（必须遵守）
**文本文档（.md/.txt/.json/.js/.html）→ 用 read_file**
**Excel文件（.xlsx）→ 用 openpyxl 或 XLSX 库**
**图片文件（.png/.jpg）→ 才用 vision_analyze**

绝对不要把文本文档或Excel当图片用vision_analyze识图。

---

## 五、五行与命理调试知识

### 5.1 五行相生相克映射（高频错误）
```javascript
const shengMap = { '水':'木', '木':'火', '火':'土', '土':'金', '金':'水' };
const keMap = { '木':'土', '土':'水', '水':'火', '火':'金', '金':'木' };
```

**验证方法：** 用甲木验证：shengMap['水'] = '木' ✓，keMap['金'] = '木' ✓

### 5.2 十二长生表（必须用传统版）
阴干逆行：乙木长生在午（不是亥），辛金长生在子（不是巳）。

### 5.3 得地判断（必须查所有四柱）
只要有一个地支在长生~帝旺范围就算得地，不是只查日支。

### 5.4 三得法执行顺序
1. 先算三得法 → 存到全局变量 `sandeLevel`
2. 再算用神（`computeYongXiJi`）→ 使用 `sandeLevel` 判断身强身弱
3. 最后渲染UI

### 5.5 三会局 vs 交战
三会局是"成局"（该五行力量大增），六冲才是"交战"（双方力量减弱）。

### 5.6 正印格用食神泄秀
正印格可以用食神：正印=进货（学习积累），食神=出货（才华输出），学以致用，经典高格局。

### 5.7 病药逻辑
- "没有病就是没有病"，不是每个盘都有病
- 用三得法判断每个五行的强弱，三得二以上=强=病
- 药 = 强元素所生的五行，且该五行不是强

### 5.8 喜用神计算规则
用神优先级：通关 > 病药 > 默认（格局/旺衰）

| 用神 | 喜神 | 忌神 | 仇神 |
|------|------|------|------|
| 木 | 火（克金） | 金（克木） | 水（病的一部分） |
| 水 | 木（泄金） | 土（克水） | 金（生水） |
| 金 | 土（生金） | 火（克金） | 木（被金克） |
| 火 | 木（生火） | 水（克火） | 土（被火生） |
| 土 | 火（生土） | 木（克土） | 金（被土生） |

### 5.9 五行力量表角色映射
用反向查找确定每个五行对日主的角色（找"谁生日主"是印星，不是shengMap[dayWx]）。

### 5.10 得令规则
得令 = 旺 OR 相（不是只有旺）。辰戌丑未月统一按土旺算。

### 5.11 排盘脚本集成
```javascript
const dateObj = new Date(year, month-1, day, hour, 0);
const result = window.calculateBazi(dateObj, gender);
// result.pillars — 四柱
// result.bodyStrength — 身强身弱（可能不准，建议用自己的三得法）
// result.yongXiJi — 用神忌神（可能不准，建议自己算）
```

已知问题：bodyStrength.level 可能与三得法结果不一致；浏览器环境下 global 可能未定义。

---

## 六、多Agent开发流程

**标准流程：** 架构师 → 开发 → 验收

**验收任务（关键）：**
- 必须对照需求文档逐项检查
- 必须运行测试案例验证结果
- **不能只测"能不能跑"，要测"功能是否完整"**

### 测试案例
必须用两个案例验证：
- 丁卯己酉甲子丁卯（甲木）→ 身强、正官格、用神=官杀
- 甲戌壬申乙酉壬午（乙木）→ 身弱、金水旺、用神=木

### 改代码前先改需求文档
1. 先改需求文档（写清楚要什么）
2. 用户确认需求文档正确
3. 再改代码
4. 对照需求文档验收

---

## 七、AI执行层设计

### 核心认知
Claude Code = 躯体，API Key = 大脑。系统需要内嵌Claude Code的核心能力（读SKILL.md、执行skill、调用API）。

### 自定义AI执行层
```
用户问题 → SkillRegistry(扫描目录) → SkillDispatcher(匹配skill)
→ SkillLoader(读取文件) → PromptAssembler(组装prompt) → AI API
```

### Prompt缓存优化（Claude）
静态部分（~2K tokens）加 `cache_control: {"type": "ephemeral"}` → 省90%

详细设计见：`D:\tmp\八字性格分析系统_v1.0.0\docs\AI_EXECUTION_LAYER.md`

---

## 八、用户偏好（必须遵守）

1. **先问再改**：修改八字分析逻辑或软件代码之前，先向用户确认修改方案
2. **按需求来**：必须严格按照需求文档实现，不能自己猜测逻辑
3. **变量要对**：JS变量作用域问题需要特别注意，全局变量要在使用前声明
4. **先听再做**：讨论架构时先听完用户意图，不要立刻去读文件或写代码

---

## 九、参考资料位置

- `D:\hermes-agent\imge_v2\` — 案例课、十神组合判定手册、格局.docx
- `D:\hermes-agent\imge_v3\` — 课程录音转写、图片提取、新增内容清单
- `D:\tmp\八字性格分析系统_v1.0.0\` — 架构文档
- 架构文件：`ARCHITECTURE.md` / `APP_ARCHITECTURE.md` / `AI_INTEGRATION_GUIDE.md`

## 参考文件

| 文件 | 内容 |
|------|------|
| `references/variable-dictionary-template.md` | 变量数据字典模板 |
