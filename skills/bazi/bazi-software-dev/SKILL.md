---
name: bazi-software-dev
description: "八字软件开发流程。HTML/CSS/JS前端 + JS分析模块架构。变量管理、验收流程、常见坑。触发词：八字软件、排盘软件、开发、前端"
version: "1.0"
created: "2026-07-26"
source: "用户八字软件开发session"
---

# 八字软件开发指南

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

```
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

## 三、常见坑

### 3.1 变量作用域
函数内定义的变量，其他函数访问不到 → 必须用全局变量

### 3.2 重复定义
同一个变量在多处定义 → 只在全局定义一次，函数内不要重复`let`

### 3.3 pi.hidden格式
排盘脚本的`pi.hidden`是对象数组`[{stem:"戊", god:"正财", type:"Main"}]`，不是字符串数组。访问时用`h.stem`不是`h`。

### 3.4 CHANG_SHENG表
十二长生表按天干查（甲乙丙丁...），不是按五行查（金木水火土）。
用`CHANG_SHENG[dayGan][zhi]`查状态。

### 3.5 WX_WANGXIANG表
旺相休囚死表按**月支五行**查，不是按**月支**查。
用`WX_WANGXIANG[monthWx][wx]`查状态。

### 3.6 格局取格（必须看透干，不能只看本气）⚠️ 重要
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

**错误做法**（只看本气）：
```javascript
const benqiGan = monthHidden[0]; // 只取第一个（本气）
const benqiGod = getTenGod(dayGan, benqiGan);
// → 申月本气=庚金→正官格 ❌（壬水透干应该是正印格）
```

**正确做法**（公共函数，计算一次）：
```javascript
function determineGeju(dayGan, monthZhi, tiangan) {
  const monthHidden = ZHI_HIDDEN[monthZhi] || [];
  const roles = ['本气', '中气', '余气'];
  // 1. 先看哪个藏干透干
  for (let i = 0; i < monthHidden.length; i++) {
    if (tiangan.includes(monthHidden[i])) {
      return { geju: getTenGod(dayGan, monthHidden[i]) + '格', source: roles[i] + '透干' };
    }
  }
  // 2. 都不透：子午卯酉午可以取本气虚格
  const singleZhi = ['卯', '酉', '子', '午'];
  if (singleZhi.includes(monthZhi)) {
    return { geju: getTenGod(dayGan, monthHidden[0]) + '格', source: '本气虚格' };
  }
  // 3. 多藏干月令不透干 → 不成格
  return { geju: '不成格', source: '月令藏干均不透干' };
}
```

**案例验证**：
- 甲戌壬申乙酉壬午：月令申金，藏干=庚(本气)、壬(中气)
- 壬水透干（月干和时干都是壬水）
- 壬水对乙木=正印 → 应该是**正印格**，不是正官格

### 3.7 代码重复原则（计算只用一次）⚠️ 重要
**核心原则：任何计算只做一次，结果存变量，其他地方直接用变量。**

**错误做法**（到处重复计算）：
```javascript
// renderGeju里算一遍格局
function renderGeju(r) {
  const geju = calculateGeju(...); // 算一遍
}
// renderYongShen里又算一遍
function renderYongShen(r) {
  const geju = calculateGeju(...); // 又算一遍 ❌
}
```

**正确做法**（公共函数，调用一次）：
```javascript
// 定义公共函数
function determineGeju(dayGan, monthZhi, tiangan) { ... }

// 所有地方调用它
function renderGeju(r) {
  const result = determineGeju(dayGan, monthZhi, tiangan); // 调用
}
function renderYongShen(r) {
  const result = determineGeju(dayGan, monthZhi, tiangan); // 同一个函数
}
```

**好处**：改一处全生效，不会出现A处改了B处没改的bug。

### 3.8 空亡逻辑（容易搞错）
**日柱空亡** = 检查**日支**是否出现在年柱/月柱/时柱的空亡里（基于各自旬首）。
**年月时空亡** = 检查年支/月支/时支是否出现在**日柱的空亡里**（基于日柱的旬首）。

示例（甲戌壬申乙酉壬午）：
- 日支酉出现在年柱甲戌旬空亡（申、酉）里 → 日柱空亡！
- 时支午出现在日柱乙酉旬空亡（午、未）里 → 时柱空亡！


注意：空亡skill只做判断，不做断语。断语由各专题skill（婚姻、十神等）自行下。

### 3.8 参考资料位置
课程笔记和参考资料在两个目录：
- `D:\hermes-agent\imge_v2\` — 案例课、十神组合判定手册、格局.docx
- `D:\hermes-agent\imge_v3\` — 课程录音转写、图片提取、新增内容清单

**十神组合判定与断语**：
- `D:\hermes-agent\imge_v2\十神组合判定手册.md` — 组合判定条件
- `D:\hermes-agent\imge_v2\十神组合判定与断语手册.md` — 组合判定+断语+案例原话

读取时用read_file，不要用vision_analyze。

### 3.9 十神分析输出规范 ⚠️ 重要

**核心原则：十神分析必须输出10个子skill的完整内容，不是摘要表格！**

**数据来源：**
- bazi-shishen-shishen（食神，105条语录）
- bazi-shishen-shangguan（伤官，93条语录）
- bazi-shishen-zhengguan（正官，86条语录）
- bazi-shishen-qisha（七杀，94条语录）
- bazi-shishen-zhengyin（正印，57条语录）
- bazi-shishen-pianyin（偏印，88条语录）
- bazi-shishen-bijian（比肩，24条语录）
- bazi-shishen-jiecai（劫财，69条语录）
- bazi-shishen-zhengcai（正财，11条语录）
- bazi-shishen-piancai（偏财，50条语录）

**输出流程：**
1. 检测命局中显著的十神（满足以下任一条件）：
   - 该十神数量≥2（天干透出+地支藏干累计）
   - 该十神为用神
   - 该十神为忌神
   - 该十神为格局核心（如正官格的正官、七杀格的七杀、正印格的正印等）
2. 加载对应的子skill
3. 输出该十神的完整内容（不是表格）：
   - 核心定义（阴阳、本质、五行）
   - 性格特征（正面表现、负面表现）
   - 常见组合（组合名、含义、吉凶）
   - 实战断语（用神时如何、忌神时如何）
   - 大运流年影响
   - 语录参考（从references/shishen-yulu.md读取，已按十神过滤）

**语录过滤规则**：每个skill的语录文件必须只包含与该十神相关的内容。过滤方法：
- 保留包含该十神关键词的语录（如食神skill保留含"食神"、"食伤"、"枭神夺食"的）
- 删除不相关的通用断语（如"木五行受伤导致精神障碍"这种五行通用断语）
- 用户原话："正印的skill，应该不会出现其他十神的断语"

**串写框架（来自bazi-analysis-writing）：**
- 开篇定调：一句话概括命主核心特征
- 性格分析：用因果关系串联（因为...所以...这意味着...）
- 感情/事业分析：结合具体组合
- 建议/提醒：可操作的建议

**错误做法**（摘要表格）：
```javascript
// ❌ 不要这样
html += '<table><tr><th>十神</th><th>力量</th><th>人际关系</th>...';
shishenNames.forEach(ss => {
  html += '<tr><td>' + ss + '</td><td>' + count + '</td>...';
});
```

**正确做法**（串写输出skill完整内容）：
```javascript
// ✓ 检测显著十神，用串写框架输出
const significantShishen = detectSignificantShishen(r);
significantShishen.forEach(ss => {
  const skillData = SHISHEN_SKILL_DATA[ss];
  // 开篇定调
  html += '<p>' + dayGan + '日主，' + 核心特征 + '。</p>';
  // 逐个十神串写
  html += '<h4>' + ss + '（' + 用神/忌神/格局核心 + '）</h4>';
  // 性格：用"因为...所以..."串联
  // 组合：结合具体组合
  // 断语：用神时如何、忌神时如何
  // 语录：选1-2条最相关的引用
});
```

**串写框架（来自bazi-analysis-writing）**：
- 开篇定调：一句话概括命主核心特征
- 性格分析：用因果关系串联（因为...所以...这意味着...）
- 感情/事业分析：结合具体组合
- 建议/提醒：可操作的建议
- **不要罗列特质，要讲故事**

**语录过滤规则**：
- 每个skill的语录必须只包含与该十神**主要相关**的内容
- 不是包含关键词就算相关——语录的**主语**必须是该十神
- 例如："七杀本质是刚强...但如果有正印..." → 这是讲七杀的，不应该出现在正印skill里
- 过滤方法：语录的前50字符不能以其他十神开头（跳过数字前缀如"4."）
- 用户原话："正印的skill，应该不会出现其他十神的断语"
- "理华老师说"前缀不需要，语录直接融入分析
- 过滤后要重新生成shishen-skill-data.js

**语录拆分规则**（重要）：
- 对比语录（如"正印...而偏印..."）应拆开分别放进对应skill
- 拆分点：而、但是、不过、但
- 拆分后每部分独立成条，各自归类

**语录上下文感知过滤**（重要）：
- 语录应该根据命局条件来显示，不是盲目显示
- 例如："日支是比肩..." → 只有当日支确实是比肩时才显示
- 例如："身旺时..." → 只有命局身旺时才显示
- 实现方法：检测语录中的条件关键词，与命局实际条件匹配

**用神/忌神检测必须检查实际出现**（重要bug）：
- 不能只根据五行关系就加入用神/忌神集合
- 必须检查该十神在命局中是否真的存在（count > 0）
- 错误：用神=木 → 直接把比肩加入用神集合（即使比肩count=0）
- 正确：用神=木 → 只有当比肩count > 0时才加入

### 3.10 文件读取规则（必须遵守）
**文本文档（.md/.txt/.json/.js/.html）→ 用 read_file**
**Excel文件（.xlsx）→ 用 openpyxl 或 XLSX 库**
**图片文件（.png/.jpg）→ 才用 vision_analyze**

绝对不要把文本文档或Excel当图片用vision_analyze识图。用户明确批评过这个问题。

示例：
```bash
# 正确：读取SKILL.md
read_file("D:/test/bazi-system/bazi-kongwang/SKILL.md")

# 正确：读取Excel
python -c "import openpyxl; wb = openpyxl.load_workbook('file.xlsx'); ..."

# 错误：用vision_analyze读文本
vision_analyze("D:/test/bazi-system/bazi-kongwang/SKILL.md")  # ❌ 绝对不要这样做
```

### 3.11 变量字典（必须维护）
每次修改后必须更新variable-dictionary.md，记录：
- 全局变量定义位置（HTML顶部）
- 每个变量的数据来源
- 赋值位置（哪一行）
- 使用位置（哪些函数）
不维护变量字典 = 下次修改必出bug。

---

## 四、验收流程

### 4.0 改代码前先改需求文档 ⚠️ 重要
**用户明确要求：改代码之前必须先改需求文档。**

流程：
1. 先改需求文档（写清楚要什么）
2. 用户确认需求文档正确
3. 再改代码
4. 对照需求文档验收

**错误做法**：直接改代码，然后说"我理解错了"
**正确做法**：先改需求文档 → 用户确认 → 再改代码

### 4.1 测试案例
必须用两个案例验证：
- 丁卯己酉甲子丁卯（甲木）→ 身强、正官格、用神=官杀
- 甲戌壬申乙酉壬午（乙木）→ 身弱、金水旺、用神=木

### 4.2 验收标准
对照需求文档逐项检查：
1. 每个模块有`analyze()`方法
2. 分析逻辑符合对应skill规则
3. 输出格式符合需求
4. 两个测试案例通过
5. 三个标签页都能正常显示

### 4.3 验收报告
输出到`D:\test\bazi-app\review-report.md`，包含：
- 每个模块的验收结果
- 发现的问题清单
- 修改建议

---

## 五、喜用神计算规则（软件实现）

**用神优先级：** 通关 > 病药 > 默认（格局/旺衰）

**喜用神对应关系（根据用神五行确定）：**

| 用神 | 喜神 | 忌神 | 仇神 |
|------|------|------|------|
| 木 | 火（克金） | 金（克木） | 水（病的一部分） |
| 水 | 木（泄金） | 土（克水） | 金（生水） |
| 金 | 土（生金） | 火（克金） | 木（被金克） |
| 火 | 木（生火） | 水（克火） | 土（被火生） |
| 土 | 火（生土） | 木（克土） | 金（被土生） |

**身弱时的默认用神：**
- 用神 = 水（印星，生我）
- 喜神 = 木（比劫，同我）
- 忌神 = 金（官杀，克我）
- 仇神 = 土（财星，克印）
