# Hermes 使用经验日志

> 自动生成于 2026-07-04，汇总 Skills 经验教训 + 近期会话踩坑记录

---

## 2026-07-04

### 踩坑记录

- [GitHub 同步] `github-sync.sh` 经常超时（120s）→ 网络不稳定或 repo 过大，使用 `--filter=blob:none` 浅克隆可缓解
- [cron 环境] `git clone` 大仓库超时 → 改用 `--depth 1 --filter=blob:none` 减少传输量

### 新发现

- 无新增（今天无新会话）

### 用户偏好更新

- 无新增

---

## 2026-07-03（补充）

### 踩坑记录

- [macos-browser-cdp] Chrome profile 用 `cp -R` 复制会丢失 cookies 等登录态 → 改用 `rsync -a`，保留文件权限、时间戳和特殊属性。根因：rsync 会保留扩展属性，cp -R 不会

### 新发现

- [飞书文档] 创建飞书文档（docx）可直接用 API：`POST /docx/v1/documents` 创建 → `POST /docx/v1/documents/{id}/blocks/{id}/children` 添加内容。block_type=2 是段落，block_type=22 是分割线

### 用户偏好更新

- Mac SSH 连不上（port 22 refused），不要尝试 SSH 到 Mac，有需要直接看 GitHub 仓库
- 用户对操作流畅度要求高：Chrome 反复关闭打开会很烦，期望一次做完不来回折腾
- 用户说"你是不是有毛病"时说明已经很不耐烦了

### Skill 更新

- 更新 `macos-browser-cdp` skill：cp -R → rsync -a（SKILL.md + scripts/start_chrome_cdp.sh + references/chrome-security-policy.md）

---

## 2026-07-03（原有记录）

### 踩坑记录

- [飞书表格] 股票数据更新脚本写入了错误数据：列O（开盘价）写成了周一收盘价而非实际开盘价，列Q（滑点）为空。根因：脚本跳过了第二池更新，且O列数据直接复制了F列 → 需修复脚本 + 重新授权飞书 token（已过期）
- [飞书集成] OIDC endpoint 误用 tenant_token 作为 Bearer token → 已修正 token 处理逻辑
- [GitHub 同步] `github-sync.sh` 超时（120s） → 可能是网络不稳定或 repo 过大，建议检查网络或考虑代理
- [cron 定时任务] cron 环境中 `execute_code` 被禁用，必须用 `write_file` 创建脚本再 `terminal` 运行；含中文的内联 Python 因编码问题被截断 → 始终先写 .py 文件再执行
- [cron 定时任务] git commit 含 emoji 会被安全扫描拦截 → 始终使用纯 ASCII 提交信息
- [cron 定时任务] `~/.git-credentials` 可能为空文件（0 bytes）→ 推送前先用 `wc -c` 检查

### 新发现

- [选股回测] 行业分散规则（行业≤2）将第一池收益率从 -5.56% 提升到 -2.99%（+2.57pp）
- [选股回测] 平均分阈值在行业过于集中时无效——取消行业限制后替补仍是同行业
- [选股回测] 两周样本太小，需 4-8 周数据验证
- [飞书集成] tenant_token 创建表格验证、OAuth fallback、sheet_id 查询、range 匹配、清空规则、紧凑表格格式（共 7 项新发现）

### 用户偏好更新

- 转录用 gemma 模型
- 八字十天干性格分类
- 🎙️ 表情符号分两行显示

---

## 2026-07-02

### 踩坑记录

- [图片分析] **严重规则**：永远不要把长图直接发给 vision_analyze，必须先切片。跳过切片规则会丢失 50-70% 内容。强制流程：`Image.open → .size → h>2000? → slice → 逐段识别`。2000px 切片高度最优。
- [图片分析] >20M 像素的图片需先缩放，否则 MemoryError
- [图片分析] `write_file` 会破坏 Python 引号 → 改用 terminal heredoc，用 `py_compile` 验证
- [拼多多] Shadow DOM 阻止自动化：1688 一键铺货使用 `sl-checkbox`/`sl-button` Web 组件，OpenCLI 或 JS eval 无法可靠点击 → 必须手动操作
- [拼多多] 编辑页面必须立即提交，否则页面刷新后所有修改丢失
- [拼多多] PDD 要求图片 <3MB → 用 PIL quality 参数压缩
- [macOS] **绝不运行** `tccutil reset ScreenCapture` — 会移除所有应用的屏幕录制权限，不可逆
- [macOS] TCC 系统对话框无法程序化点击（Quartz CGEvent、cliclick、osascript 均失败）→ 只能手动交互
- [TouchDesigner] 拆分清理和创建为独立 MCP 调用 — 同名节点在同一脚本中销毁+重建会导致 "Invalid OP object" 错误
- [TouchDesigner] TOP.save() 对动画无用 — 每次捕获相同的 GPU 纹理。始终使用 MovieFileOut
- [Teams] Graph webhook 订阅 72 小时后过期且不自动续期 → 设置 12 小时间隔的续期 cron
- [Teams] 转录文件在会议结束后 2-5 分钟才可用

### 新发现

- [选股] 周二开盘优于周一（+1.29pp）
- [八字] 宫位分析法
- [选股] V3 架构设计

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
- 事实准确性：不仅审核结构，还要验证事实。推荐热搜话题前必须点进去查看实际内容
- 财经/热搜标题需要悬念钩子（"你被骗了"、"这才是真相"）— 绝不用平铺直叙的标题

### 抖音数据监控
- 最常见错误（Error Pattern 2b）：更新数据表数字后，引用旧值的诊断文字也必须同步更新
- 小样本视频（播放<50）比率剧烈波动，需标记为"样本无意义"
- 已"完结"视频仍可能有数据漂移 → 每次检查所有视频最新数据

### Kanban 多 Agent 工作流
- 幻影卡片 ID 会阻断完成 — 只引用 `kanban_create` 成功返回的 ID
- 坏的阻断原因（"卡住了"）得不到回答 → 要说明需要什么决策
- Worker 中不要调用 `clarify`（无头模式）→ 用 `kanban_block` 代替

### 系统调试
- pdb 在 pytest-xdist 下静默挂起 → 用 `-p no:xdist`
- `PYTHONBREAKPOINT=0` 禁用所有断点
- Node.js `--inspect` vs `--inspect-brk`（后者在首行暂停）
- 端口 9229 碰撞 → 用 `--inspect=0`
- `--inspect` 在父进程不会检查子进程 → 用 `NODE_OPTIONS`

---

*本日志由 Hermes 经验同步 cron 任务自动生成*
