---
name: bazi-system
description: 八字多Agent系统主入口。协调器指挥分析Agent按八层体系分步执行，每层审核后输出json，回复Agent读json生成回复。触发词：分析八字、八字分析、排盘分析、看看八字。
tags: [bazi, 系统, system, 主入口]
triggers:
  - "分析八字"
  - "八字分析"
  - "排盘分析"
  - "看看八字"
---

# 八字多Agent系统

## 架构

```
用户输入（年月日时性别 / 问题）
    ↓
┌─────────────────────────────────────────┐
│  bazi-master（协调器/指挥）               │
│  - 接收用户输入                           │
│  - 识别问题类型                           │
│  - 按八层体系指挥分析Agent                 │
│  - 确保所有skill在1-5层中都被加载过        │
└──────────────┬──────────────────────────┘
               ↓
    ┌──────────────────────┐
    │  bazi-paipan         │
    │  排盘 → bazi.json    │
    └──────────┬───────────┘
               ↓
    ┌──────────────────────┐
    │  bazi-trigger        │  ← 新增！
    │  条件检测 → trigger.json │
    └──────────┬───────────┘
               ↓
    ┌──────────────────────┐
    │  bazi-finder         │
    │  定位 → 分析方向      │
    └──────────┬───────────┘
               ↓
    ┌──────────────────────────────────┐
    │  bazi-analyst                    │
    │  读trigger.json加载skill          │
    │  第2层：bazi-geju(格局)→          │
    │        bazi-xiyong(用神/喜神)→    │
    │        bazi-shishen(十神)         │
    │  分层执行 → layerX.json           │
    │  ⚠️ 输出必须包含skills_used字段   │
    └──────────┬───────────────────────┘
               ↓
    ┌──────────────────────────────────┐
    │  bazi-reviewer                   │
    │  读trigger.json检查skill          │
    │  审核 → 通过/修正                 │
    │  ⚠️ 检查skills_used是否完整       │
    └──────────┬───────────────────────┘
               ↓
    ┌──────────────────────┐
    │  bazi-responder      │
    │  读json → 命理师视角输出│
    │  ⚠️ 不关心skill加载步骤 │
    └──────────────────────┘
```

## 架构原则

- **分析侧**：协调器确保所有skill在1-5层中都被加载过，结果存JSON
- **输出侧（Responder）**：不关心skill加载步骤，只读JSON，用命理师视角输出——性格怎么样、性冷淡还是啥、健康有什么问题
- **过三关 = Responder侧写模式**：不是分析层，是Responder的输出方式。读取所有JSON，像犯罪心理侧写师一样综合描绘人物画像（性格外貌、身体特征、欲望、婚姻、健康、秘密等）。侧写维度动态生成——根据实际读到的JSON决定侧写哪些方面，不写死固定维度。
- **Responder根据用户问题从相关JSON中取内容润色输出**

## 文件结构

```
bazi-system/
├── SKILL.md                    # 主入口（本文件）
├── bazi-master/                # 协调器/指挥
├── bazi-paipan/                # 排盘（含JS脚本）
│   └── scripts/                # 排盘JS脚本
├── bazi-trigger/               # 条件触发检测（排盘后自动执行，输出trigger.json）
├── bazi-finder/                # 定位Agent
├── bazi-analyst/               # 分析Agent
├── bazi-reviewer/              # 审核Agent
│   └── references/             # 审核参考文档
│       ├── 必须调用skill清单.md  # skill调用验证规则
│       ├── 十神速查表.md
│       └── 常见错误.md
├── bazi-responder/             # 回复Agent
├── bazi-exporter/              # 输出Agent
│
├── # === 基础知识类 ===
├── bazi-shishen/               # 十神分类、详解、组合
├── bazi-dizhi/                 # 地支关系：三会/三合/六冲/刑害
├── bazi-sizhu/                 # 四柱代表、宫位分析
├── bazi-geju/                  # 格局判定、用神忌神
│   └── references/
│       └── 十二长生与旺衰判断.md  # 两个版本的十二长生+旺衰判断方法
├── bazi-xiyong/                # 取喜用神（6维度交叉验证）
│   └── references/
│       └── 十天干贵格速查.md     # 10个天干的贵格体系（第6-14课）
│
├── # === 专项分析类 ===
├── bazi-xingge/                # 性格分析
├── bazi-peiou/                 # 配偶画像分析
├── bazi-hunyin-tongwuxing/     # 上下同五行=二婚之象（条件触发）
├── bazi-gongchuan/             # 夫妻宫穿夫妻星
├── bazi-hunyin-cishu/          # 婚姻次数判断
├── bazi-duanpeifu/             # 配偶类型/异性偏好
├── bazi-zhi/                   # 痣相三板斧
├── bazi-xinglengdan/           # 性冷淡八字密码
├── bazi-xiongbu/               # 胸部痣分析
├── bazi-haose/                 # 好色分析
├── bazi-shencai/               # 身材体型
├── bazi-daogui/                # 被女倒追特征
├── bazi-lanyin/                # 印星过旺与懒
├── bazi-dinghuo/               # 丁火专题（熬夜/背部痣）
│
├── # === 健康类 ===
├── bazi-weibing/               # 脾胃病八字分析
├── bazi-feibu/                 # 肺部健康八字分析
├── bazi-shenbing/              # 肾病八字分析
├── bazi-ganbing/               # 肝部健康八字分析
├── bazi-xinzangbing/           # 心脏健康八字分析
│
├── # === 辅助工具类 ===
├── bazi-baceng/                # 八层体系框架
├── bazi-duanshi/               # 断事方法论
├── bazi-chuanzhuo/             # 穿着搭配
├── bazi-analysis-writing/      # 分析写作指导（串联技巧、两种输出模式）
│
└── references/
    ├── Skill总索引.md           # 所有skill的索引
    ├── 十天干进度.md            # 十天干详解进度追踪
    └── 死木与活木.md            # 甲乙木日元先判死活（第十九课知识点）
```

## Skills_used验证机制

**核心规则**：分析Agent输出的每层json必须包含`skills_used`字段，审核Agent会检查是否遗漏必要skill。

### 流程
1. 协调器指令中明确列出"必须加载skill"
2. 分析Agent输出json包含`skills_used: ["skill1", "skill2", ...]`
3. 审核Agent加载 `references/必须调用skill清单.md`
4. 对比：协调器指定的必须skill vs 分析agent的skills_used
5. 遗漏 → 审核不通过 → 打回重做

### 各层必须加载skill

| 阶段 | 必须加载skill | 条件触发skill（由bazi-trigger检测，mandatory_skills中指定） |
|------|--------------|-------------------------------------------------------|
| 排盘后 | bazi-trigger | 自动检测6项条件，输出trigger.json |
| 1 | bazi-paipan, bazi-sizhu | — |
| 2 | bazi-geju, bazi-xiyong, bazi-shishen | bazi-dizhi（如有三会/三合局） |
|| 3 | bazi-xingge, bazi-shishen-tiangan, bazi-shishen, **bazi-analysis-writing** | bazi-shishen-*（日坐十神或突出十神）、bazi-zhi, bazi-xiongbu, bazi-xinglengdan, bazi-haose, bazi-shencai, bazi-daogui, bazi-lanyin, bazi-dinghuo |
| 4 | bazi-sizhu, bazi-shishen, bazi-peiou, bazi-duanpeifu, bazi-hunyin-cishu | bazi-gongchuan（夫妻宫六害时） |
| 5 | - | 按问题类型加载专项skill |
| 6 | bazi-dayun（待创建） | bazi-dizhi（流年地支关系） |
| 7 | - | - |
| 8 | bazi-tiaoli（待创建） | - |

### 第5层专项skill对照

| 问题类型 | 必须加载Skill | 状态 |
|----------|--------------|------|
| 被女倒追 | bazi-daogui | 已有（可选） |
| 印星懒 | bazi-lanyin | 已有（可选） |
| 婚姻/配偶 | bazi-peiou, bazi-duanpeifu, bazi-gongchuan, bazi-hunyin-cishu | 已有 |
| 同五行二婚（条件触发） | bazi-hunyin-tongwuxing | 已有（仅日柱同五行时加载） |
| 事业/财运 | bazi-shiye | 待创建 |
| 健康/寿元 | bazi-weibing, bazi-feibu, bazi-shenbing, bazi-ganbing, bazi-xinzangbing | 已有 |
| 性格/天赋 | bazi-xingge, bazi-shishen-tiangan, bazi-shishen-* | 已有 |
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

### ⚠️ 女命特殊规则（铁律，不可遗漏）

**当gender=F时，必须额外加载 bazi-fukeshengyu**（⚠️ 在bazi-sales目录，不在bazi-system）。

此skill判断：流产史、剖腹产几率、子宫卵巢健康。

**触发条件（Step 2条件检测时自动执行）：**
- gender=F → 必须加载
- 日坐阳刃（壬子/丙午/丁巳/戊午/己巳/癸亥）→ 更要加载（应验率90%+）

**遗漏后果：** 女命分析缺少生育健康维度，审核不通过。

## 完整流程

### Step 1: 排盘

```bash
cd ~/.hermes/profiles/main/skills/bazi-system/bazi-paipan && node scripts/generate_bazi_analysis.js <年> <月> <日> <时> <性别>
```

输出：bazi.json

### Step 2: 条件触发检测（排盘后立刻执行，不可跳过）

排盘完成后，协调器**必须立即调用 bazi-trigger**，自动检测所有条件触发规则。

```bash
cd ~/.hermes/profiles/main/skills/bazi-system/bazi-trigger
node scripts/check_conditions.js <bazi.json路径>
```

**输出：trigger.json**（条件触发清单）

**trigger.json 包含：**
- `conditions`：6项检测结果（同五行日柱、女命、日坐阳刃、杂气月、墓库、夫妻宫六害）
- `mandatory_skills`：必须加载的skill列表（含原因）

**分析Agent和审核Agent都读取trigger.json：**
- 分析Agent：根据mandatory_skills加载对应skill
- 审核Agent：根据mandatory_skills检查skills_used是否完整

**⚠️ 这个步骤不可跳过！遗漏条件触发skill → 审核不通过。**

### Step 3: 定位

加载bazi-sizhu skill，根据问题类型确定分析方向。

### Step 3: 分析（按八层体系）

协调器按八层体系指挥bazi-analyst分步执行，每层指令中明确必须加载的skill。确保所有skill在1-5层中都被加载过。

### Step 4: 审核

每层做完，bazi-reviewer审核：
1. 校验十神、用神忌神
2. 检查skills_used是否完整
3. 通过才输出json

### Step 5: 回复

bazi-responder读取已审核的json，用命理师视角生成用户可读回复。不关心skill加载步骤，只关心内容。

## 根据问题类型决定分析深度

| 用户问题 | 分析到哪层 |
|---------|-----------|
| 看性格/什么人 | 第1-3层 |
| 看六亲/婚姻/配偶 | 第1-4层 |
| 看事业/财运 | 第1-5层 |
| 看今年运势 | 第1-6层 |
| 全面分析 | 第1-8层 |

## 关键规则

0. **⚠️ 排盘后必须先查地支冲合**：排盘完成后，第一步不是做三得法，而是检查四柱地支有没有六冲/六合/三合/三刑。有冲合→标记相战五行→准备通关用神。通关用神优先级最高。如卯酉冲→用水通关（金生水→水生木）。
1. **排盘必须用JS脚本**，不能手算或AI推算
2. **每层json必须审核通过**才能输出
3. **只有回复Agent对外输出**，其他都是内部流转
4. **协调器按八层体系指挥**，分析Agent只执行当前步骤
5. **分析Agent必须输出skills_used**，审核Agent会检查
6. **女命（gender=F）必须加载bazi-fukeshengyu**
7. **协调器确保所有skill在1-5层中都被加载过**，不能遗漏
8. **Responder不关心skill加载步骤**：只读JSON，用命理师视角输出
9. **bazi-analysis-writing必须在第3层加载**：分析写作指导，提供串联技巧和两种输出模式（算命工具/分析报告），确保分析报告不是语录拼盘而是有逻辑的推理过程

## 软件架构

如果要把本系统的skill体系做成独立软件（Windows/手机/Web），参考 `references/软件架构模式.md`：
- 核心原则：每个skill → 一个JS分析器类，不建规则引擎
- orchestrator.js调度所有分析器，函数调用链串联
- AI是可选叠加层（JS输出JSON → AI翻译成流畅文本）
- 断语模板存JSON（templates/），方便编辑

## 与其他skill的关系

- 本系统替代原有的bazi-analysis skill
- bazi-sales系统（销售话术）独立使用，部分skill（bazi-zhiduan/bazi-fukeshengyu）被本系统引用
- **⚠️ 本系统≠整理课程笔记**：用户发来八字案例时，可能是要整理笔记（course-notes-fusion），不是要跑分析系统。先判断任务类型再加载skill
- 参考文档：`references/Skill总索引.md`

## 开发软件时的Pitfalls

### ⛔ 先问再改，不要瞎猜（2026-07-26 教训）

**用户原话：「你咋回事，能不能先问了再改」**

开发八字分析软件时，多次自行修改代码没有先问用户确认：
1. 把通关用神改成了别的，用户说"这是通关，取水"
2. 自己猜病药规则，用户说"没有病就是没有病"
3. 自己改五行映射，结果搞反了

**正确做法：**
- 涉及八字理论的修改，先问用户确认再改
- 不确定的规则，先问"这个对吗"再动手
- 用户说"没有病"就是没有病，不要硬凑

### ⛔ 验收必须对照需求文档（2026-07-26 教训）

**用户原话：「你完全没当回事啊，验收agent是干啥的」**

上次开发软件时，验收agent只测了"能不能跑"，没有对照需求文档检查功能是否完整。结果排盘能跑但分析模块没实现。

**正确做法：**
- 验收agent必须对照需求文档逐项检查
- 不是"代码能运行"就算通过
- 是"需求文档里的每个功能都实现了"才算通过
- 验收报告要列出每个模块的通过/不通过状态

### ⛔ 五行映射不能搞反（2026-07-26 教训）

**用户原话：「你这取用神都不是按skill写的，你也没审核出来」**

代码中五行相生相克映射搞反了：
- `shengMap['木']='水'` → 错！应该是`shengMap['水']='木'`（水生木）
- `keMap['木']='金'` → 这个是对的（金克木）

**正确验证方法：**
用具体例子验证：甲木日主，水生木→水是印星，金克木→金是官杀。如果映射后结果不对，就是搞反了。

### ⛔ 十二长生必须区分阴阳干（2026-07-26 教训）

**用户原话：「你看你看看，你自己前面和后面是一样吗」**

十二长生表有两个版本：阳干顺行、阴干逆行。必须用传统版（阴干逆行）：
- 甲木长生在亥，乙木长生在午
- 丙火长生在寅，丁火长生在酉
- 如果甲乙木共用一张表，乙木的身强弱会判断错误

---

## 分析系统的Pitfalls

### ⛔ 必须先查地支冲合再做三得法（2026-07-26 教训）

**用户原话：「你看你很明显错了，地支卯酉冲，金木交战，你说没有」**

排盘完成后，第一步不是做三得法，而是检查四柱地支有没有六冲/六合/三合/三刑。

丁卯己酉甲子丁卯这个盘，两个卯酉冲（年支卯↔月支酉，时支卯↔月支酉），金木交战。必须用水通关（金生水→水生木），而不是直接按三得法判断身强身弱。

**正确流程：**
1. 排盘后先查地支冲合
2. 有冲合→标记相战五行→准备通关用神
3. 通关用神优先级最高
4. 然后再做三得法判断身强身弱

### ⛔ Step 2条件触发检测不可跳过（2026-07-07 严重教训）

**用户原话：「这个应该是上下同五行，skill没触发，然后是女命的那个刨腹产啥的也没触发」**

排盘完成后，必须立即执行Step 2条件触发检测，检查：
1. 日柱是否为12种同五行日柱 → 是则必须加载bazi-hunyin-tongwuxing
2. gender是否为F → 是则必须加载bazi-fukeshengyu
3. 月支是否为辰戌丑未 → 是则用杂气月取格规则
4. 地支是否有辰戌丑未 → 是则必须加载bazi-muku
5. 日支是否为阳刃 → 是则女命必须加载bazi-fukeshengyu
6. 日支是否与其他地支六害 → 是则必须加载bazi-gongchuan

**这些条件在Step 2检测，不是在第4层才检查！** 第4层的skill表是分析时的补充，条件触发检测在排盘后立刻执行。

- **⚠️ 读笔记必须读融合笔记，不要读OCR文件**：课程目录下有融合笔记（`_笔记.md`）和OCR文件（`_课件OCR.md`），融合笔记包含课件+讲师解读，内容更完整。永远优先读融合笔记。
- **⚠️ 格局分析必须用格局核心法**：用神忌神基于格局×组合判定矩阵，不能用身强身弱推导。详见bazi-geju skill。
- **⚠️ 条件触发skill必须有前置检查**：不是所有skill都无条件加载。bazi-hunyin-tongwuxing仅日柱同五行时加载（12种），bazi-fukeshengyu仅gender=F时加载，bazi-gongchuan仅日支六害时加载。skill的SKILL.md必须写明前置检查条件和适用范围，协调器不能把条件触发skill放在"必须加载"里无脑加载。**教训：之前bazi-hunyin-tongwuxing标为"过三关必查"，甲子日柱（木水不同五行）被错误加载并得出"不是同五行=没默契"的错误结论。**
- **⚠️ 过三关不是独立层，是Responder侧写模式**：之前有"第0层过三关"的概念，现在已删除。过三关是Responder的输出方式——读取所有JSON，综合判断，像侧写师一样描绘人物画像。侧写维度动态生成，不写死固定维度（因为skill会不断增加）。分析侧按8层体系执行，skill分配到对应层加载。
- **⚠️ Responder不关心skill加载**：Responder只读JSON，用命理师视角输出。不要在Responder中引用skill或讨论skill加载逻辑。
- **⚠️ 8层体系不能写死为5层**：目前实现了1-5层，但8层体系是完整的。Responder跳过没有JSON的层，不代表那些层不存在。以后实现第6-8层时自然加入。
- **⚠️ 部分skill目录存在但SKILL.md缺失**：测试发现bazi-dinghuo、bazi-duanpeifu、bazi-gongchuan、bazi-hunyin-cishu、bazi-ganbing、bazi-xinzangbing目录存在但SKILL.md文件缺失，子agent找不到。创建skill时必须确保SKILL.md文件实际写入，不能只建目录。
- **bazi-system和bazi-sales是两个独立系统**：bazi-zhiduan/bazi-fukeshengyu在bazi-sales目录，不要在bazi-system的skill清单中标记为"已有"
- **skill命名必须用正确拼音**：配偶=pèi'ǒu（不是pèifù），已将bazi-peifu改名为bazi-peiou
- **新建skill前先查是否已存在**：避免重复创建
- **创建skill前先写进度文档**：如十天干详解，先标记每课内容再做成skill，避免遗漏
- **skill分类要准确**：专项分析类（性冷淡/痣相/好色/胸部痣/脾胃病/被倒追/懒）vs辅助工具类（八层体系/断事方法/穿着搭配），不要搞混
- **索引文档必须同步更新**：每次新增/改名skill都要更新Skill总索引.md和必须调用skill清单.md
- **OCR前必须加载analyze-image skill**：不要直接调用vision_analyze，先按skill流程检查尺寸再切片
- **⚠️ 参考文件不要写测试案例（2026-07-10 教训）**：用户需要用同一个案例反复测试验证分析流程。参考文件（references/）只写方法论、通用示例和判断标准，不写具体八字案例。测试案例由分析Agent实际执行时判断。用户原话："你把这个八字写到案例，我还怎么测试呢"。通用示例（如"甲木见丑土→得地但不得助"）可以写，具体八字盘不能写。
- **⚠️ 用户发八字≠要跑分析系统（2026-07-16 教训）**：用户发来八字案例时，可能是要整理/修正课程笔记，不是要跑完整的八字分析流程。**先判断任务类型**：
  - 用户说"整理笔记""笔记里有""修正案例" → 任务是笔记整理，加载 `course-notes-fusion`
  - 用户说"帮我分析""看看这个八字""排盘分析" → 任务是八字分析，加载本系统
  - 用户只发了八字没有上下文 → 先搜索session历史找上下文，再判断
  - **绝对不要看到八字就自动加载bazi-system**，用户原话："你看错 skill 了"
- **⚠️ 取象≠用神，不要混淆（2026-07-16 教训）**：整理笔记时，取象（如家具、雕刻、唢呐）是用来说明用神的**例子**，不是核心知识点本身。用户原话："你明白个鬼，雕刻那些是取象"。笔记中取象和用神要分开标注——取象只是参考，用神才是核心结论。
- **⚠️ 不要自创总结性规则（2026-07-16 教训）**：整理讲师内容时，忠实记录讲师的教学过程（先问学生→学生回答→讲师引导→得出结论），不要自己提炼简洁规则。用户原话："你有毒啊，谁让你总结出这么一句话"。讲师的教学方式是引导式思考，不是给你一个公式背。
- **⚠️ 喜忌分类必须准确（2026-07-16 教训）**：身强的八字，金（官杀）通常是喜神而非忌神——"身强得官杀能担当事业重任，化煞为权"。笔记中用神/喜神/忌神/仇神的分类必须与讲师原文一致，不能凭自己理解写。教训：截图显示金是喜神，笔记却写成了忌神。
