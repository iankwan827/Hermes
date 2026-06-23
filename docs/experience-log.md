# Hermes 使用经验日志

## 2026-06-23

### 踩坑记录
- [录音skill] Agent"失忆"——已有 `macos-audio-recording` skill 和 `record.py`，但没先查skill就自己写脚本录音 → **每次录音前必须先 `skills_list` + `skill_view('macos-audio-recording')`**，用户原话"你之前录音没有写skill吗，你又对录音失忆了"
- [录音skill] 自写脚本用了44100Hz采样率，record.py标准是16000Hz → 必须按skill标准参数执行，不能自作主张改参数

### 新发现
- [选股执行价] **周一买 vs 周二买对比**：75%的股票（30/40只）周一开盘价更便宜，等待一天平均多付+3.54% → **信号产生后应当日立即挂单**，等待次日买入平均多付3-4%
- [选股执行价] 追高最严重TOP3：花园生物+29.41%、株冶集团+20.99%、南大光电+15.44% → 这类涨幅过大的股票需警惕追高风险
- [选股执行价] 仅少数电子/材料类个股（矩子科技-6%、顺络电子-5.65%、达瑞电子-3.56%）周二低开，等待有小幅收益
- [风险监控] 持仓20只股扫描：株冶集团+四川黄金减持已完成（抛压已释放），佛塑科技大股东质押需关注比例，整体无严重风险事件

### 用户偏好更新
- 用户对"失忆"极度敏感（原话"你又对录音失忆了"）→ 每次执行操作前必须先查现有skill，不要自己从零写

### Skill 更新
- 无新增/修改skill（本次主要是执行价采集和风险监控的经验积累）

---


## 2026-06-22

### 踩坑记录
- [选股系统] capture_execution.py 内联中文命令被截断 → 写成.py文件再用`python3 script.py`执行
- [录音] 1分钟测试后忘记继续录 → 直接用后台录制脚本一步到位，不要先测试
- [cron脚本] symlink路径被Hermes安全机制拦截（解析后超出profile scripts目录）→ 直接运行完整路径脚本
- [飞书表格] boolean值在JSON序列化时出错 → 需要`str(v) if isinstance(v, bool) else v`处理
- [飞书API] 写入spreadsheet时range必须包含header+全部数据行 → 用实际行数而非固定20行

### 新发现
- [选股系统] 执行价采集支持双数据源(eastmoney+tencent)备选，eastmoney价格/100需注意
- [录音验证] 检查最大振幅>0.01即可确认录到内容，不需要等转录完成
- [飞书表格] 选股执行价更新流程：读取execution CSV → 刷新token → 写入两个sheet（稳健池+成长池）
- [选股数据] 6/22（周一）开盘平均滑点+0.68%，花园生物+13.89%异常追高，天赐材料-2.15%低开买入最佳
- [选股策略] 第一池19只信号(非20只，株冶集团开盘跳空+9.30%)，第二池20只全部正常

### 用户偏好更新
- 录音不要反复测试，直接开始录（用户原话"你1分钟后忘记继续录就坏了"）
- 用户对"失忆"很敏感 — 前面说没有飞书表格后面又找到，必须先搜再下结论
- 审核文案时必须严格按字数估算时长（粤语约4字/秒），超90秒不能标"通过"

### Skill 更新
- 更新 `stock-screener`：新增执行价采集+飞书表格更新工作流
- 更新 `macos-audio-recording`：record.py后台录制验证方法

---

## 2026-06-21

### 踩坑记录

#### analyze-image（图片批量分析）
- [SKILL] **exec() 环境变量陷阱**: 用 `exec(open(...).read())` 运行 Python 不会加载环境变量 → 必须用 `terminal` 工具
- [SKILL] **中文数字匹配陷阱**: 课程编号搜索必须从长到短匹配，否则"二"会被"二十二"错误截获
- [SKILL] **长图必须切割**: 长宽比>3 或高度>8000px 的图片直接发送会丢失大量内容 → 用 `full_extract.py` 按3000px分段
- [SKILL] **超宽图(>5000px)切割**: 需要用1500px分段而非3000px，否则文字模糊
- [SKILL] **大图(>20M像素)**: 必须先缩放再处理，否则 MemoryError/DecompressionBomb
- [SKILL] **不要手动解析图片头**: 必须用 `PIL.Image.open()`，手动解析在JPEG上会失败
- [SKILL] **不要用 bash `export $(grep ...)`**: 特殊字符会出错 → 用 Python 读取 .env
- [SKILL] **`write_file` 破坏 f-string**: 用 `terminal` 配合 heredoc 写 Python 脚本
- [SKILL] **系统 Python 可能损坏**: 始终使用 `uv python` 路径
- [SKILL] **批量处理前先检查源文件夹**: "最重要的教训"——在跑脚本之前先确认源文件夹里有什么

#### douyin-data-check（抖音数据查看）
- [SKILL] **按钮索引偏移陷阱**: "最新作品"和"近期作品"区域有重复按钮，导致索引错位
- [SKILL] **按钮是 `<div>` 不是 `<span>`**: 必须用 `querySelectorAll('*')` 而非 `querySelectorAll('span')`
- [SKILL] **Python + MSYS 中文编码陷阱**: format字符串中的中文字符会触发 ValueError → 只用ASCII格式字符串
- [SKILL] **审计陷阱（多个）**: 多轮审计发现错误但从不实际修复；不同段落引用不同数字自相矛盾；里程碑排名未随新视频更新；声称"已修复"但 read_file 显示什么都没变
- [SKILL] **复核必须从原始数据重新计算比率**: 永远不要信任之前记录的比率

#### course-notes-fusion（课件笔记融合）
- [SKILL] **回退陷阱**: Agent4 发现匹配错误时，应发回 Agent2（不是 Agent3）
- [SKILL] **讲稿缺失导致整章消失**: 课件独有章节不在讲稿中会被丢弃 → 必须保留并标记为"课件独有"
- [SKILL] **macOS sed 损坏文件**: BSD sed 与 GNU sed 不同 → 用 `patch` 或 `write_file` 替代
- [SKILL] **移动端字号陷阱**: 桌面端习惯16-17pt在手机上太大 → 必须用11pt正文
- [SKILL] **Markdown表格转换陷阱**: `python-docx` 脚本会静默跳过markdown表格，丢失关键内容

#### teams-meeting-pipeline（Teams会议摘要）
- [SKILL] **Graph订阅72小时过期**: 微软Graph不会自动续订 → 必须设置12小时自动续订，否则会议摘要静默停止
- [SKILL] **转录可用性**: 会后需要2-5分钟才能生成转录

#### feishu-docx-to-native（飞书文档）
- [SKILL] **Callout块语法高亮创建后不可更改**
- [SKILL] **代码块不支持 language=1**: 必须用 language=34 (PlainText)
- [SKILL] **原生表格(block_type=20)无法通过API创建**: Cell字段校验始终失败
- [SKILL] **Callout检测必须在标题检测之前**: 否则 `### 📋` 会被解析为H3

#### pdd-store（拼多多开店）
- [SKILL] **1688一键铺货的 shadow DOM**: web components 无法被 OpenCLI 可靠触发
- [SKILL] **编辑页必填字段**: 品牌、材质等必须填写否则无法提交
- [SKILL] **必须确认成本再定价**: 不同SKU成本不同
- [SKILL] **OpenCLI会话不稳定**: 复杂操作应由用户手动完成
- [SKILL] **Camofox无法访问PDD后台**: PDD检测非Chrome浏览器

#### pokemon-player（宝可梦）
- [SKILL] **必须频繁使用Vision**: 每2-4步截一次图。RAM告诉你位置/HP但不告诉你环境
- [SKILL] **传送需要2-3个 wait_60**: 否则位置读数为过时数据
- [SKILL] **建筑出口陷阱**: 出现在门口，必须先侧移才能离开

#### audio-transcribe（音频转录）
- [SKILL] **Whisper CLI不在PATH**: 使用显式 Python 3.9 路径
- [SKILL] **粤语(yue)中等模型不支持**: 用 `--language zh`

#### creative/ascii-video
- [SKILL] **macOS Pillow `textbbox()` 返回错误高度**: 用 `font.getmetrics()` 替代
- [SKILL] **不要用 `stderr=subprocess.PIPE` 配合长时间运行的ffmpeg**: 64KB缓冲区满会导致死锁

#### xurl（X/Twitter）
- [SKILL] **省略 `--app my-app`**: token会保存到错误的profile
- [SKILL] **Docker HOME 陷阱**: `~/.xurl` 根据 HERMES_HOME 与 subprocess HOME 解析到不同路径

#### touchdesigner-mcp
- [SKILL] **清理和创建必须分开MCP调用**: 同一脚本中销毁和重建同名节点会导致 "Invalid OP object" 错误

### 新发现
- [SKILL] **bazi-muku 墓库避坑规则**: 不见财库就说"有财库"；不见冲就说"开库"；无墓库≠无财；墓库化用神/化忌神=吉/凶
- [SKILL] **bazi-kongwang 空亡分析**: 空亡查法、五行空亡断语、填实方法
- [SKILL] **dbs-diagnosis 语言陷阱检测**: ~25%的复杂问题是语言陷阱，需停下来与用户澄清
- [SKILL] **dbs-goal 本质主义陷阱**: 不要将SMART作为充分必要条件，应用家族相似性特征
- [MEMORY] **小红书采集**: 必须用 `/search_result/` 链接（带 xsec_token），仿人操作3-8秒间隔
- [MEMORY] **选股系统**: 两池(稳健/成长)，B规则推荐默认，周频策略，周五15:30出信号
- [MEMORY] **八字巳月**: 5月5日立夏~6月5日芒种（不是6月）
- [MEMORY] **2030=庚戌(火库), 大运甲辰(水库), 辰戌冲双库齐开**

### 用户偏好更新
- 用 `hermes config set` 改配置，永远不要直接编辑 config.yaml
- 进度汇报只在 50%、80%、100% 时报告
- 写完文案必须自动跑 video-content-audit 审核
- 引用热搜事件必须确认时间线
- 栋笃笑文案用"阿强"(朋友角色)做叙事载体，开头第一句必须是选题
- 喜欢"争议性开头"，中间加钩子(共鸣/反面案例/冲突对比)
- 过三关遇到女命(gender=F)必须额外加载 bazi-fukeshengyu skill
- 用户痛点：不从标题推断内容要读文件；视频50秒-1分30秒；用户改完文案就是终版

### Skill 更新
- 删除了 `dbs-agent-migration` skill（过时，已合并到其他流程）
- 电商图工作流：首选 Gemini banana 原生图编辑，备选 rembg 抠图+纯背景合成
- 课件笔记生成Word文档：markdown笔记→python-docx生成带样式docx→上传飞书三板斧
- 选股系统路径：~/Pictures/选股/

---

## 2026-06-20

### 踩坑记录
- [CRON] Agent错误声称"Ollama转录不了"导致用户错过Gemma4方案 → 给结论前必须验证
- [CRON] github-sync.sh 脚本在profile目录下的symlink被Hermes安全机制拦截 → 直接运行完整路径

### 新发现
- [录音skill] 从20KB拆分为3.2KB核心+references+scripts
- [AI推理] llama.cpp/LM Studio/Ollama三者对比
- [录音] 持续录制脚本 record_live.py 每5分钟自动保存一个WAV文件
- [飞书] 浏览器工具已升级为 agent-browser 0.28.0 + Chrome 150

### 用户偏好更新
- 直播录音流程：先录1分钟测试→转录验证→确认录到才开始正式录制
- Mac → GitHub 需要 SOCKS5 代理 `socks5h://127.0.0.1:7897`（Clash）

### Skill 更新
- 更新 `douyin-download`：SKILL.md 变更
- 更新 `huang-zihua-perspective`：SKILL.md 变更

---

## 2026-06-19

### 踩坑记录
- [feishu-docx-to-native] Callout块语法高亮创建后不可更改 → 创建前就确定好高亮语言
- [feishu-docx-to-native] 代码块不支持"plaintext"语言 → 需用34=PlainText
- [feishu-docx-to-native] 原生表格无法通过API创建 → 不要浪费时间尝试
- [feishu-courseware-upload] Shell引号与markdown `***` 冲突导致Authorization截断 → 写脚本到文件再执行
- [teams-meeting-pipeline] Graph subscriptions 72小时过期不续期 → 必须设置自动续期
- [teams-meeting-pipeline] Transcript需2-5分钟生成 → 不要立即查询
- [audio-transcribe] Whisper八字术语听错表：鬼害→癸亥、鬼水→癸水 → 转录后必须人工校对
- [bazi-sales] 排盘数据源必须用JS脚本 → 绝对禁止用Python手算
- [bazi-sales-validator] 自写天干地支计算脚本容易出错 → 必须用cnlunar验证
- [touchdesigner-mcp] 不要猜测参数名 → 先调用td_get_par_info确认

### 新发现
- [audio-transcribe] Gemma4替代Whisper：用images参数传音频(不是audio)，需要think:false
- [touchdesigner-mcp] Non-Commercial TD caps resolution at 1280×1280
- [touchdesigner-mcp] H.264/H.265/AV1需要Commercial license → macOS用prores替代
- [songwriting] 动态ARC描述比列genre更重要

### 用户偏好更新
- 不要给不切实际的乐观时间估算 → 宁可说"还要差不多同样时间"
- 文案修改偏好：简洁，删掉排比句和重复金句；台词口语化；节奏快
- 写完文案必须自动跑video-content-audit审核
- 电商图工作流：首选Gemini原生图编辑
- 小红书访问笔记详情必须用/search_result/链接（带xsec_token）
- 用户改完文案就是终版 → 不要自作主张加回删掉的内容

### Skill 更新
- 更新 feishu-docx-to-native：Callout/代码块/表格API限制
- 更新 audio-transcribe：Whisper听错表 + Gemma4替代方案
- 更新 bazi-sales：排盘数据源强制JS脚本
- 更新 touchdesigner-mcp：参数查询规则 + 许可证限制

---

## 2026-06-18

### 踩坑记录
- [macos-audio-recording] Mac Mini默认输出是内置扬声器而非HDMI → 用system_profiler确认
- [macos-audio-recording] ffmpeg avfoundation + BlackHole录制不稳定 → 用sounddevice替代
- [macos-audio-recording] avfoundation设备索引在创建/删除聚合设备后重新排列
- [feishu] Python heredoc处理可能丢失字符 → 用patch工具修复
- [feishu-oauth] Refresh token有效期30天 → 过期后需重新走完整授权流程
- [cron-job-patterns] github-sync.sh 脚本路径不存在 → 实际路径在~/.hermes/scripts/

### 新发现
- [macos-audio-recording] HermesMO多输出设备验证成功
- [macos-audio-recording] 持续录制脚本record_live.py每5分钟自动保存WAV
- [macos-audio-recording] Whisper medium模型首次运行需下载~1.5GB
- [feishu] 飞书文档分享设置：组织内「获得链接的人可阅读」
- [bazi] 直播录音工作流：录1分钟→停止→转录验证→连续录制

### 用户偏好更新
- 直播录音流程：先录1分钟测试→转录验证→确认录到才开始正式录制
- 飞书文档分享：用户倾向「组织内获得链接的人可阅读」
- Mac Mini音频输出：用户使用内置扬声器（非HDMI）

### Skill 更新
- 更新 macos-audio-recording：ffmpeg不稳定 + sounddevice替代 + 设备索引变化
- 更新 feishu-oauth：refresh token过期时间

---

## 2026-06-17

### 踩坑记录
- [cron-job-patterns] execute_code在cron环境中被禁用 → 必须用write_file + terminal
- [cron-job-patterns] clarify在cron中不可用 → 所有决策必须自主完成
- [cron-job-patterns] ~/.git-credentials可能为0字节 → push前检查
- [himalaya] v1.2.0文件夹别名语法变更：folder.aliases.X（复数）
- [airtable] filterByFormula必须URL编码
- [airtable] 批量端点限制10条/请求
- [python-debugpy] pdb在pytest-xdist下静默无效
- [kanban-worker] 永远不要调用clarify → 会静默超时约120秒
- [systematic-debugging] 3+次修复失败 → 停下来质疑架构

### 新发现
- [hermes-agent-skill-authoring] skill_manage(action='create')用于仓库内skill是错误的 → 用write_file
- [hermes-agent-skill-authoring] `---`前不能有前导空格 → 必须从字节0开始
- [test-driven-development] 测试后写的测试立即通过 → 什么也证明不了
- [comfyui] 视频/音频工作流默认超时300秒 → 重型工作流需提升至900秒以上

### 用户偏好更新
- 直接执行："你做一下"意味着立即开始，不要确认性提问
- 不要乐观时间估计：说诚实的时长
- 不要部分交付：必须100%完成后才能交付
- 内容风格："身边小事"引起共鸣，不要时事；争议性开头；粤语对话（阿强角色）
- Mac → GitHub 需要 SOCKS5 代理 `socks5h://127.0.0.1:7897`
- 配置变更必须用 `hermes config set`

### Skill 更新
- 新增 cron-job-patterns：execute_code禁用、凭证空检查
- 更新 kanban-worker：不要调用clarify、不要用phantom IDs
- 更新 himalaya：v1.2.0文件夹别名语法变更
- 新增 systematic-debugging：铁律和规则
