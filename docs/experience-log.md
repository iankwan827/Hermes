# Hermes 使用经验日志

> 自动生成于 2026-07-05，汇总 Skills 经验教训 + 近期会话踩坑记录

---

## 2026-07-05

### 踩坑记录

- [钉钉直播] 录音目录搞错：先创建了「第五课」目录，实际最新是第十课，今天应为第十一课 → 创建目录前必须先 `ls ~/Pictures/录音/八字课/ | sort -V | tail -1` 确认最新课次
- [八字课程] 用户发来课程内容后又说"你又忘记语录了" → 这是第三次忘记追加到语录文件。收到课程内容时必须自动追加到语录文件，不能只回复整理要点

### 新发现

- 无新增技术发现

### 用户偏好更新

- 用户发来八字课程内容（Day81-99等）时，不要回复整理要点摘要，直接按之前的操作习惯处理（追加到语录文件）。用户觉得"你又忘记语录了"=我重复犯了三次同样的错误
- 录音目录必须先查现有目录确认最新课次，不能自作主张猜

### Skill 更新

- 无新增 skill 更新

---

## 2026-07-04

### 踩坑记录

- [GitHub 同步] `git clone` 大仓库超时 → 使用 `--filter=blob:none` 或 `--depth 1` 浅克隆
- [cron 环境] cron 环境 clone 大仓库超时（120s 限制）→ 浅克隆 + 增量拉取

### 新发现

- 无新增

### 用户偏好更新

- Mac SSH 连不上不要尝试（port 22 refused）
- Chrome 反复开关很烦
- "你是不是有毛病"=用户不耐烦信号

### Skill 更新

- `macos-browser-cdp`: 复制 profile 命令从 `cp -R` 改成 `rsync -a`（cp -R 会丢失 cookies 等登录态）— 3 个文件同步更新（SKILL.md、scripts/start_chrome_cdp.sh、references/chrome-security-policy.md）

---

## 2026-07-03

### 踩坑记录

- [飞书表格] 股票数据更新脚本写入了错误数据：列O（开盘价）写成了周一收盘价而非实际开盘价，列Q（滑点）为空 → 脚本跳过了第二池更新，且O列数据直接复制了F列
- [飞书集成] OIDC endpoint 误用 tenant_token 作为 Bearer token → 已修正 token 处理逻辑
- [GitHub 同步] `github-sync.sh` 超时（120s）→ 网络不稳定或 repo 过大
- [cron 定时任务] cron 环境中 `execute_code` 被禁用，必须用 `write_file` 创建脚本再 `terminal` 运行
- [cron 定时任务] 含中文的内联 Python 因编码问题被截断 → 始终先写 .py 文件再执行
- [cron 定时任务] git commit 含 emoji 会被安全扫描拦截 → 始终使用纯 ASCII 提交信息
- [cron 定时任务] `~/.git-credentials` 可能为空文件（0 bytes）→ 推送前先用 `wc -c` 检查
- [macos-browser-cdp] `cp -R` 复制 Chrome profile 会丢失登录态 → 改用 `rsync -a`

### 新发现

- [飞书文档 API] 创建飞书文档用 block_type=2（段落）、block_type=22（分割线）
- [选股回测] 行业分散规则（行业≤2）将第一池收益率从 -5.56% 提升到 -2.99%（+2.57pp）
- [选股回测] 两周样本太小，需 4-8 周数据验证

### 用户偏好更新

- Mac SSH 连不上不要尝试
- Chrome 反复开关很烦
- "你是不是有毛病"=用户不耐烦

### Skill 更新

- `macos-browser-cdp`: cp -R → rsync -a（3 个文件同步更新）
- `macos-browser-cdp`: 新增抖音视频下载实战案例（用 CDP 直接操作，不依赖 opencli）

---

## 2026-07-02

### 踩坑记录

- [图片分析] **严重规则**：永远不要把长图直接发给 vision_analyze，必须先切片。跳过切片规则会丢失 50-70% 内容。强制流程：`Image.open → .size → h>2000? → slice → 逐段识别`。2000px 切片高度最优。
- [图片分析] >20M 像素的图片需先缩放，否则 MemoryError
- [图片分析] `write_file` 会破坏 Python 引号 → 改用 terminal heredoc，用 `py_compile` 验证
- [拼多多] Shadow DOM 阻止自动化：1688 一键铺货使用 `sl-checkbox`/`sl-button` Web 组件 → 必须手动操作
- [拼多多] 编辑页面必须立即提交，否则页面刷新后所有修改丢失
- [拼多多] PDD 要求图片 <3MB → 用 PIL quality 参数压缩
- [macOS] **绝不运行** `tccutil reset ScreenCapture` — 会移除所有应用的屏幕录制权限，不可逆
- [macOS] TCC 系统对话框无法程序化点击 → 只能手动交互
- [TouchDesigner] 拆分清理和创建为独立 MCP 调用 — 同名节点在同一脚本中销毁+重建会导致 "Invalid OP object" 错误
- [TouchDesigner] TOP.save() 对动画无用 — 每次捕获相同的 GPU 纹理。始终使用 MovieFileOut
- [Teams] Graph webhook 订阅 72 小时后过期且不自动续期 → 设置 12 小时间隔的续期 cron
- [Teams] 转录文件在会议结束后 2-5 分钟才可用

### 新发现

- [选股] 周二开盘优于周一（+1.29pp）
- [八字] 宫位分析法
- [选股] V3 架构设计
- [飞书集成] tenant_token 创建表格验证、OAuth fallback、sheet_id 查询、range 匹配、清空规则、紧凑表格格式（共 7 项新发现）

### Skill 更新

- 新建 `llm-provider-fix` skill（LLM provider 401/402 错误诊断）
- 更新 `hermes-agent` skill
- 更新 `douyin-download` skill

---

## 2026-07-01

### 踩坑记录

- [LLM] credential_pool 重置 bug 导致 401/402 错误
- [选股] 追高风险：南大光电极端滑点 +15.21%
- [钉钉] 坐标配置纠正

### 新发现

- [风控] 7月1日和2日 Top20 持仓均无重大风险
- [选股] 选股系统 V3 架构

---

## 跨日期通用经验汇总（来自 Skills）

### 视频内容审核
- 审核是强制流程，不是可选项 — 用户发现跳过审核直接给文案会批评
- 事实准确性：不仅审核结构，还要验证事实
- 财经/热搜标题需要悬念钩子 — 绝不用平铺直叙的标题

### 抖音数据监控
- 最常见错误：更新数据表数字后，引用旧值的诊断文字也必须同步更新
- 小样本视频（播放<50）比率剧烈波动，需标记为"样本无意义"

### Kanban 多 Agent 工作流
- 幻影卡片 ID 会阻断完成 — 只引用 `kanban_create` 成功返回的 ID
- Worker 中不要调用 `clarify`（无头模式）→ 用 `kanban_block` 代替

### 系统调试
- pdb 在 pytest-xdist 下静默挂起 → 用 `-p no:xdist`
- `PYTHONBREAKPOINT=0` 禁用所有断点
- Node.js `--inspect` vs `--inspect-brk`（后者在首行暂停）
- 端口 9229 碰撞 → 用 `--inspect=0`

---

## 用户核心偏好（持续有效）

1. **录音不要反复测试**，确认录到就开始
2. 对「失忆」极度敏感 → 每次操作前必须先查现有 skill
3. **配置变更必须用 `hermes config set`**
4. 进度汇报只在 50%、80%、100% 时报告
5. 用户改完文案就是终版，不要自作主张加回删掉的内容
6. 转录必须用 gemma，不能用 whisper
7. 八字性格分类用十天干，不是五行
8. 笔记上传飞书：🎙️标记和内容必须分两行
9. 飞书创建表格不是文档（spreadsheet ≠ document）
10. 用户偏好紧凑表格格式（五行做列、维度做行）
11. 收到八字课程内容时自动追加到语录文件，不要只回复整理要点
12. 录音目录必须先查现有目录确认最新课次

---

*本日志由 Hermes 经验同步 cron 任务自动生成*
