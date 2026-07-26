---
name: bazi-analysis
description: "八字分析SOP：排盘→按Phase分析→Agent审核→修正→输出终版。输入年月日时性别，输出完整八字分析报告。"
tags: ["bazi", "analysis", "sop", "review"]
triggers:
  - "分析八字"
  - "八字分析"
  - "排盘分析"
  - "看看八字"
---

# 八字分析 Skill

用户提供年月日时性别，要求分析八字时使用此skill。

## 核心流程（5步，严格按顺序）

```
Step 1: JS排盘 → 获取四柱+十神
Step 2: 过三关 + 加载专题Skill + 按Phase写分析
Step 3: delegate_task 审核Agent（对照排盘校验十神）
Step 4: 审核通过 → 输出终版给用户
  ╔════════════════════════════════════════════════╗
  ║ 🚫 硬性规则：Step 2写完分析后，禁止直接输出！   ║
  ║    必须先执行Step 3审核，通过后才能输出终版。    ║
  ╚════════════════════════════════════════════════╝
```

## Step 1: JS排盘

```bash
# Mac
cd ~/.hermes/profiles/main/skills/bazi-sales && node scripts/generate_bazi_analysis.js <年> <月> <日> <时> <性别>

# Windows
cd "E:/Users/Administrator/AppData/Local/hermes/skills/bazi-sales" && node scripts/generate_bazi_analysis.js <年> <月> <日> <时> <性别>
```

- 时=小时（0-23），不传分钟
- ⚠️ **脚本性别bug（严重）**：gender参数无效，始终输出"女命"。四柱天干地支正确，但**十神全部错误**（十神取决于性别）。必须手动重算十神，详见 `references/常见错误.md` P9
- 用户直接给四柱时：需反查日期（遍历日期匹配四柱），再跑脚本确认
- 读取 `references/关键路径.md` 获取脚本位置和关键文件

## Step 2: 分析（过三关 + 专题 + 完整报告）

### 2a. 直断验证
加载 `bazi-zhiduan` skill，扫描全部速查表（28秘诀、十天干性格、痣位置、身材体型、婚姻断语、健康断语等）。命中的全部列出。

### 2b. 格局判定+用神忌神
按Phase 2-3执行（详见 `references/分析步骤.md`）。
⚠️ 用户定义的"过三关"= 格局判定+用神忌神+日主强弱，不是28秘诀直断。

### 2b.5 加载取象skill（性格/外貌/事业分析前必须）
加载 `bazi-zhiduan` skill的 `references/天干地支取象速查.md`，提取每个天干地支的：
- **本义+核心特质**→性格描述素材（不要只用十天干性格表的基础内容）
- **身体取象**→健康/外貌断语（如甲木=头发、丁火+水=近视）
- **行业取象**→事业建议
- **讲师独有解读**→深度断语（如甲木水旺=头发浓黑、丁火点烟=熬夜、卯木要凑堆）

⚠️ 性格分析不能只用十天干性格表的4行文字，必须结合取象skill的本义+特质+讲师解读来丰富描述。

### 2c. 专题Skill加载（排盘后必须检查）
| 条件 | Skill |
|------|-------|
| 始终 | `bazi-kongwang`（空亡） |
| 地支有辰戌丑未 | `bazi-muku`（墓库） |
| Phase 8 大运流年 | `bazi-dayun-liunian` |
| gender=F | `bazi-fukeshengyu`（女命生育） |

### 2d. 按Phase写完整分析
按 `references/分析步骤.md` 中的Phase 2-9步骤执行。

## Step 3: Agent审核

用 `delegate_task` 启动审核Agent，传入排盘数据+分析文本，对照校验十神用词。Prompt模板见 `references/分析步骤.md`。

- 审核发现错误 → patch修正 → 重新提交审核 → 直到通过
- **审核未通过前，不得输出给用户**

## Step 4: 输出终版

审核通过后，输出完整分析报告。

## 课程语录管理（用户发笔记时自动执行）

当用户发送带"Day"标签的课程笔记/语录时（如"Day81-99 1. xxx 2. xxx"），自动追加到语录文件，无需确认：

```
文件路径：~/Pictures/八字课/语录/理华老师语录.md
标题格式：## DayX-99（如 ## Day81-99）
操作：读取文件末尾 → 在最后追加新标题和笔记内容
```

⚠️ 用户发笔记时直接追加，不要问"要我帮你加到语录吗"。

## ⚠️ 新架构已创建（bazi-master多Agent系统）

新的多Agent架构已创建完成，位于 `~/Pictures/八字课/bazi-multi-agent-arch.md`：
- **bazi-master**（协调器）：接收输入 → 识别问题 → 路由agent
- **bazi-paipan-agent**（排盘Agent）：只运行JS脚本，输出bazi.json
- **bazi-analyst**（分析Agent）：读取JSON + 动态加载skill（指针数组模式）
- **bazi-reviewer**（审核Agent）：校验十神/用神/断语
- **bazi-exporter**（输出Agent）：审核通过后标准化为analysis.json
- **bazi-responder**（回复Agent）：读取JSON生成用户回复

**bazi-analysis与bazi-master的关系**：bazi-master是bazi-analysis的多Agent重构版，功能重叠。新项目优先用bazi-master，旧skill保留作为参考。

## 参考文件（按需加载）

| 文件 | 内容 |
|------|------|
| `references/分析步骤.md` | Phase 2-9详细步骤 + 审核Prompt模板 |
| `references/常见错误.md` | 17条Pitfalls（流程/十神/格局/脚本/文件） |
| `references/JS脚本Bug修复记录.md` | generate_bazi_analysis.js 的6个Bug修复记录（2026-07-06） |
| `references/排盘系统.md` | Web排盘系统API和前端说明 |
| `references/关键路径.md` | 脚本位置、案例文件、课堂资料路径 |
| `bazi-zhiduan` skill | 28秘诀+十天干性格+痣位置+身材体型+四柱代表等速查表 |
| `bazi-kongwang` skill | 空亡分析 |
| `bazi-muku` skill | 墓库分析 |
| `bazi-dayun-liunian` skill | 大运流年分析 |
| `bazi-fukeshengyu` skill | 女命生育分析 |

## ⚠️ 工作流偏好（必须遵守）

1. **先写架构再写skill**：用户明确要求"先把多agent系统创建了，再写这个skill"。不要边读边写，按用户指定的顺序执行。
2. **只有回复Agent对外输出**：排盘、分析、审核、输出Agent的结果都在协调器内部流转，用户看不到。只有bazi-responder可以发送消息给用户。
3. **回复要有血有肉**：不要输出干巴巴的断语（"日主甲木。伤官两头挂。"❌），要扩写成有血有肉的分析（"日主甲木，参天大树的命格。甲木的人正直公正、领导力强..."✅），像命理师在讲解。
4. **不要过度阅读**：用户说"你先别看，听我指挥"时，立即停下，等用户指令。不要自作主张翻阅大量文件。
5. **文件搜索要全面**：找不到文件时，先`ls`看目录结构，不要只用grep搜内容。

## ⚠️ JS脚本已知Bug（generate_bazi_analysis.js）

脚本有6个已修复的bug，详见 `references/JS脚本Bug修复记录.md`。核心问题：
- calculateBazi需要Date对象，不是数字参数
- Shishen构造函数需要Gan对象，不是字符串
- zhis需要Zhi对象数组，不是字符串数组
- BaziInterpreter的ctx需要dayZhi/yearZhi/monthZhi/hourZhi属性
- getFeatures()应为detectAll()

**修复后仍需注意**：gender参数可能无效，十神标注为"待复核"。

## 快速参考（最常见错误，完整版见 references/常见错误.md）

1. **十神搞混**：甲木见丁火=伤官（阳见阴），不是食神
2. **用神忌神必须格局法推导**，不能抄脚本输出
3. **偏印格是凶格**，喜财来破印
4. **流年年份必须准确**：2024=甲辰...2030=庚戌
5. **流年必须结合大运**分析
6. **子时(23-23:59)算第二天**子时（日期+1，hour=0）
