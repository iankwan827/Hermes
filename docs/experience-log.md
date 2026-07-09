# Hermes 使用经验日志

> 自动生成于 2026-07-09，基于 Skills 踩坑库、Memory 记录和最近会话分析

---

## 2026-07-09（本周总结）

### 踩坑记录

#### 课件笔记系统（高频重灾区）

| # | 问题 | 解决方案 | 来源 |
|---|------|----------|------|
| 1 | **没读 skill 就动手** — 误用 `course-notes-docx` 而非 `course-notes-fusion` | 删除 `course-notes-docx`，合并到 `course-notes-fusion`，现在只有一个 skill | 会话 07/08 |
| 2 | **凭印象走旧流程** — 看到 docx 就以为要生成 docx | 每次执行前必须读 skill 文档 | 会话 07/08 |
| 3 | **记忆短暂/失忆** — 反复忘记之前的纠正 | 关键纠正立即存入 memory，不依赖会话记忆 | 会话 07/08 |
| 4 | **课次搞混** — 第十三课录音存到第五课文件夹 | 开始前先确认当前课次，录音文件名包含课次编号 | 会话 07/07 |
| 5 | **语录追加第四次忘记** — 收到课程内容必须立即追加到语录文件 | 收到课程笔记后第一步就是追加语录，用 `bazi-yulu` skill | 会话 07/05 |

#### OCR / 图片识别

| # | 问题 | 解决方案 | 来源 |
|---|------|----------|------|
| 6 | **tesseract 中文识别率极低** — "肺痨"→"肺许"，"逢三冲"→"估三冲" | tesseract 只用于定位章节边界，逐字识别用 `vision_analyze` | 会话 07/07 |
| 7 | **OCR 切片高度 2000px 太粗** — 8426px 高图漏掉中间内容 | 改用 600-800px 切片 | 会话 07/07 |
| 8 | **课件图片文件夹混入非课件图片** — 录音界面截图混在其中 | 用 `vision_analyze` 逐张识别过滤 | 会话 07/08 |
| 9 | **不能边写边传** — 只写 3 个点实际有 8 个点 | 先完整 OCR → 列目录确认 → 再动笔 → 每章核对 → 全部完成再传 | 会话 07/07 |

#### 八字系统

| # | 问题 | 解决方案 | 来源 |
|---|------|----------|------|
| 10 | **Step 2 条件触发检测被跳过** — 上下同五行、女命剖腹产 skill 没触发 | 审核 agent 新增"条件触发验证"检查项（6 项自动检测） | 会话 07/07 |
| 11 | **身强身弱判断错误** — 印星无地支根≠"虚浮不弱" | 必须综合四项（得令/得地/得生/得助）判断，`bazi-geju` skill 已更新 | 会话 07/07 |
| 12 | **排盘错误** — 日元庚金应为丙火 | 必须以转录稿为准，不能自己推断排盘 | 会话 07/05 |
| 13 | **申亥穿分析修正** — 案例一是星宫同宫被亥水穿，不是宫星相穿 | 重新核对穿的定义：宫与星的关系 | 会话 07/05 |
| 14 | **6 个八字 skill 的 SKILL.md 缺失** — 目录存在但文件不存在 | 需要补充创建 SKILL.md | 会话 07/06 |

#### 飞书集成

| # | 问题 | 解决方案 | 来源 |
|---|------|----------|------|
| 15 | **Token 过期导致上传失败** | 定期刷新 token，上传前先检测有效性 | 会话 07/05-07/07 |
| 16 | **课件笔记格式 🎙️ 块内嵌套 ### 标题** — 飞书 orange 块只显示几行 | `upload_notes.py` 已修复嵌套问题 | 会话 07/05 |
| 17 | **案例解释错误，237 个 block 全部重传** | 上传前必须逐条审核案例解释 | 会话 07/05 |

### 新发现

| # | 发现 | 来源 |
|---|------|------|
| 1 | **选股系统：周二开盘比周一便宜 75%** — 40 只股票对比，30 只周二更便宜（平均 -3.68%） | 会话 07/08 |
| 2 | **风险监控 26 条仅 2 条需关注** — 大部分是噪音，需要优化过滤规则 | 会话 07/08 |
| 3 | **飞书 token 管理经验库：29 条飞书相关教训** | 会话 07/07 |
| 4 | **3 个八字 skill 避坑指南**（宫穿、直断、审核）已沉淀 | 会话 07/07 |
| 5 | **完整八字 skill 架构梳理** — 7 个 Agent + 25 个分析 skill + 2 个框架 skill + 5 个其他 = 39 个 skill | 会话 07/06 |
| 6 | **周一执行价采集** — 40 只股票平均滑点 +0.10%，16 涨 24 跌 | 会话 07/06 |

### 用户偏好更新

| 偏好 | 说明 |
|------|------|
| **一步到位交付** | 不要分步确认，直接交付终版 |
| **读 skill 再动手** | 每次执行前读 SKILL.md，不靠名字/印象 |
| **语录即时追加** | 收到课程内容第一步就是追加语录文件 |
| **课次核对** | 开始录音/整理前先确认当前课次编号 |
| **案例以转录稿为准** | 八字排盘和案例分析必须以转录稿原文为准 |

---

## 2026-07-05 至 2026-07-09 高频踩坑排行

| 排名 | 问题 | 出现次数 | 严重程度 |
|------|------|----------|----------|
| 1 | 没读 skill 就动手执行 | 3+ 天 | 🔴 严重 |
| 2 | 记忆短暂/反复忘记纠正 | 3+ 天 | 🔴 严重 |
| 3 | 忘记追加语录文件 | 4 次 | 🔴 严重 |
| 4 | OCR 中文识别率低 | 3+ 天 | 🟡 中等 |
| 5 | 飞书 Token 过期 | 3 天 | 🟡 中等 |
| 6 | 课次搞混 | 2 天 | 🟡 中等 |

---

## Skill 踩坑库精选（22 个 Skill 的关键 Pitfalls）

### 开发工具类

#### OpenCode (`autonomous-ai-agents/opencode`)
- TUI 模式必须 `pty=true`，`opencode run` 不需要
- `/exit` 不是有效命令（会打开 agent 选择器），用 Ctrl+C
- PATH 不匹配可能选错二进制文件
- 不要让多个 OpenCode session 共享同一个工作目录
- Enter 可能需要按两次（一次定稿，一次发送）

#### Claude Code (`autonomous-ai-agents/claude-code`)
- 交互模式必须用 tmux
- `--dangerously-skip-permissions` 对话框默认选"No, exit"，需要先按 Down 再 Enter
- `--max-budget-usd` 最低约 $0.05
- `--max-turns` 只在 print 模式生效
- 后台 tmux session 会持久存在，必须 `tmux kill-session` 清理

#### Airtable (`productivity/airtable`)
- `filterByFormula` 必须 URL 编码
- PATCH 合并，PUT 替换——默认用 PATCH
- 空字段从响应中省略，缺失 key 不代表字段不存在
- 限流按 base 而非 token：不同 base 各 5 req/sec

#### Teams Meeting (`productivity/teams-meeting-pipeline`)
- **Graph 订阅 72 小时过期** — 不会自动续期，3 天后通知静默停止
- Transcript 生成需要等 2-5 分钟
- Delivery mode 不匹配会导致摘要生成但 Teams 收不到

### 创意编码类

#### P5.js WebGL
- `createCanvas(w, h, WEBGL)` 原点在中心，不是左上角
- Y 轴方向反转
- `texture()` 必须在 `rect()`/`plane()` 之前调用
- 每次 transform 必须 `push()`/`pop()` 包裹

#### ComfyUI (`creative/comfyui`)
- API 需要 API 格式的工作流 JSON，不是编辑器格式
- 模型名称区分大小写且包含扩展名
- "class type not found" = 缺少自定义节点
- 免费版 API 限制：`/api/prompt` 等端点返回 403

### 软件开发类

#### Node Inspector
- `--inspect` 不会暂停执行，需要 `--inspect-brk`
- 端口冲突：默认 9229，用 `--inspect=0` 随机端口
- 子进程不会被父进程的 `--inspect` 覆盖
- 通过 agent 终端运行 `node inspect` 需要 PTY 模式

#### Python debugpy
- pdb 在 pytest-xdist 下静默失效，用 `-p no:xdist`
- `breakpoint()` 在 CI/非 TTY 环境会挂起进程
- `PYTHONBREAKPOINT=0` 会禁用所有 `breakpoint()`
- pdb 只调试当前线程，多线程用 debugpy

#### Code Review
- diff >15k 字符需要按文件拆分
- 空 diff 检查 `git status`
- `delegate_task` 返回非 JSON 时重试一次，然后标记失败

### 生产力类

#### Maps (`productivity/maps`)
- Nominatim 限制 1 req/s
- `nearby` 必须提供 lat/lon 或 `--near "<address>"`
- OSRM 覆盖率在欧洲和北美最佳

#### Skill Authoring (`software-development/hermes-agent-skill-authoring`)
- `skill_manage(action='create')` 写入 `~/.hermes/skills/`，不是项目内
- 前导空格会导致 YAML frontmatter 解析失败
- Description 应以 "Use when ..." 开头
- 新 skill 创建后当前 session 看不到（需要重载）

### 研究类

#### LLM Wiki (`research/llm-wiki`)
- 永远不要修改 `raw/` 目录的文件
- 每次新 session 先读 SCHEMA + index + recent log
- 前 200 行以内保持可扫描性
- 标签必须来自已有分类体系

#### 研究论文模板
- 复制 `.tex` 文件时必须连同 `.sty` 一起复制
- 永远不要修改 `.sty` 文件
- 图表用矢量 PDF (`savefig('fig.pdf')`)，不用 PNG

---

## 飞书集成经验（29 条精选）

> 来源：会话 07/07 完整 token 管理经验库

- Token 过期是上传失败的头号原因
- 上传前必须检测 token 有效性
- Block 数量大时（237 个）需分批上传
- Markdown 格式导入比 docx 更稳定
- Callout 颜色检测逻辑需要简化
- 嵌套标题在飞书块级元素中会导致渲染问题

---

## 八字系统 39 Skill 架构概览

```
八字系统
├── 协调层（1）
│   └── bazi-master（主协调器）
├── Agent 层（6）
│   ├── bazi-paipan-agent（排盘）
│   ├── bazi-analyst（分析）
│   ├── bazi-reviewer（审核）
│   ├── bazi-exporter（导出）
│   ├── bazi-responder（回复）
│   └── bazi-trigger（条件触发）
├── 分析 skill（25）
│   ├── 格局：bazi-geju、bazi-sizhu
│   ├── 十神：bazi-shishen
│   ├── 地支：bazi-dizhi
│   ├── 性格：bazi-xingge
│   ├── 配偶：bazi-peiou、bazi-duanpeifu
│   ├── 婚姻：bazi-hunyin-tongwuxing、bazi-hunyin-cishu
│   ├── 健康：bazi-feibu、bazi-weibing、bazi-shenbing、bazi-ganbing、bazi-xinzangbing
│   ├── 身材：bazi-shencai、bazi-xiongbu
│   ├── 其他：bazi-zhi（痣）、bazi-chuanzhuo（穿搭）、bazi-haose、bazi-daogui...
│   └── ...
├── 框架 skill（2）
│   ├── bazi-baceng（八层体系）
│   └── bazi-duanshi（断事流程）
└── 其他（5）
    ├── bazi-paipan（排盘脚本）
    ├── bazi-trigger（条件触发）
    ├── bazi-reviewer（审核标准）
    └── ...
```

---

## 本周关键修复

| 修复 | 说明 |
|------|------|
| 删除 `course-notes-docx` | 合并到 `course-notes-fusion`，避免混淆 |
| `bazi-reviewer` 新增条件触发验证 | 6 项自动检测，防止漏触发 |
| `bazi-geju` 新增身强身弱判断要点 | 得令/得地/得生/得助四项综合 |
| OCR 切片高度 2000px → 600-800px | 避免漏掉中间内容 |
| `upload_notes.py` 修复嵌套问题 | ### 标题不再嵌套在 callout 块内 |
| 审核 agent 新增侧写审核 | 逐条检查侧写文本与 JSON 数据一致性 |

---

## 行动建议

1. **强制读 skill 流程**：每次执行前，先 `skill_view(name)` 读取当前 skill，不依赖记忆
2. **语录即时追加**：收到课程内容后，第一步执行 `bazi-yulu` 追加语录
3. **OCR 最佳实践**：tesseract 定位 → vision_analyze 识别 → 600-800px 切片
4. **八字身强身弱**：必须综合四项判断，不能只看月令
5. **飞书上传前**：先检测 token 有效性，再逐 block 审核
