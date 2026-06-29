# Hermes 使用经验日志

## 2026-06-29

### 踩坑记录
- 无新增踩坑记录

### 新发现
- [执行价采集] 第二池(成长股)追高风险显著高于第一池(稳健股)：国瓷材料+6.99%、南大光电+6.09%，第一池(稳健)滑点普遍±1%以内 → 选股执行策略应区分池子：稳健池可直接挂单，成长池需设价格上限或分批买入
- [执行价采集] 周一开盘平均滑点+0.59%，整体可控，但日内22跌vs18涨偏弱 → 开盘追高的风险在盘中暴露
- [风险监控] 佛塑科技000973大股东质押比例未披露，需关注后续公告；四川黄金/株冶集团减持已完成

### 用户偏好更新
- 无新增偏好

### Skill 更新
- 无新增Skill更新

---

## 2026-06-28

### 踩坑记录

#### Skill 内陷阱提取

- [llm-provider-fix] 充值后不重启 — credential_pool 状态缓存在内存中，必须 `hermes gateway restart` 才能生效
- [llm-provider-fix] auth.json 里的 key ≠ .env 里的 key — auth.json 的 credential_pool 可能有手动添加的 key（source="manual"），和 .env 里的环境变量 key 是两个东西
- [llm-provider-fix] 402 ≠ 401 — 402 是欠费（充值就行），401 是 key 无效（要换 key）
- [llm-provider-fix] 只有飞书报错但 CLI 正常 — CLI session 可能在报错前就建立了连接，不受 credential_pool 影响；飞书通道每次新消息都走 credential_pool 取 key
- [llm-provider-fix] "no available entries" — 所有 key 都 exhausted，不是没有 key，而是全被标记耗尽了
- [dingtalk-live] Finder 窗口遮挡钉钉 — 激活钉钉后 Finder 窗口仍在最前面，cliclick 点不到黄色提示条 → 先隐藏 Finder 再操作
- [dingtalk-live] 坐标(1607,324)不一定准确 — 窗口移动/缩放后坐标偏移 → 最可靠方法：截图→vision_analyze 定位→计算坐标→点击
- [dingtalk-live] Python3 权限弹窗阻断自动化 — macOS 首次弹出"python3.11想要控制访达.app"权限请求 → 用 AppleScript 点击"允许"按钮
- [dingtalk-live] 录音文件5分钟才出现 — record.py 每300秒保存一个文件，启动后5分钟内看不到新文件是正常的 → 不要因为看不到文件就重启录音
- [dingtalk-live] 多进程冲突 — 多次启动 record.py 导致多个进程抢占 BlackHole 音频设备 → 每次启动前 `pkill -f "record.py"` 清理
- [teams-meeting-pipeline] Graph subscriptions 72小时过期且不自动续期 — 必须设置12小时自动续订（6倍余量）
- [teams-meeting-pipeline] Transcript 未生成 — Teams 会议结束后需要2-5分钟生成转录，立即 fetch 可能返回空
- [teams-meeting-pipeline] Delivery mode 不匹配 — 摘要已生成但 Teams 未收到，检查 `platforms.teams.extra.delivery_mode` 配置
- [teams-meeting-pipeline] Graph app 权限未授权 — token-health 通过但 API 返回 401/403，需重新在 Azure portal 点击 "Grant admin consent"
- [analyze-image] MiniMax API base URL 有 `/anthropic` 后缀陷阱 — `.env` 中 `MINIMAX_CN_BASE_URL` 带 `/anthropic` 后缀，图片生成端点需去掉
- [analyze-image] 大图切割段高3000px文字太小 → 改用1500px段高，文字更清晰
- [analyze-image] exec()环境变量陷阱 — exec(open(...).read()) 不加载环境变量 → 必须用 terminal 工具调用脚本
- [analyze-image] 中文数字匹配陷阱 — "二十二"会匹配到"二" → 必须按长度降序匹配
- [analyze-image] 长图必须切割 — 长宽比>3 或高度>8000px → 用 full_extract.py 按段高切割
- [hermes-agent] Diagnostic 误报陷阱 — 平台之前报过错不代表当前还在出错，必须检查最近的日志条目而非历史记录
- [hermes-agent] Per-platform model switching 不支持 — 所有消息平台共享同一模型配置，无法按平台切换
- [hermes-agent] Auxiliary models 需单独配置 — vision/compression/session_search 失败时需手动设置 `auxiliary.vision.provider` 和 `auxiliary.vision.model`
- [ocr-courseware] 切片高度2000px是最佳平衡点 — 太大 vision 识别不清，太小效率低
- [course-notes-docx] 字号陷阱 — 新建脚本容易写成16-17pt（桌面端习惯），导致手机上文字巨大 → 务必确认正文是11pt
- [course-notes-docx] Markdown 表格转换丢失 — python-docx 脚本跳过 `|` 开头的行，导致课件表格全部丢失 → 需加入表格解析逻辑
- [course-notes-docx] 知识库.md优先于.json → JSON 可能有错误

#### 历史踩坑记录（06-17 至 06-27）

- [录音] Gemini转录进程卡死（0% CPU不动） → 换用Whisper替代，Gemini音频处理不稳定
- [录音] 旧录音进程未清理（6月18日进程仍在后台，已到part2274） → 杀掉旧进程，定期检查后台进程
- [录音] 录音skill"失忆"——已有 skill 却自己写脚本，用了错误采样率(44100Hz vs 16000Hz) → 用户原话"你又对录音失忆了"
- [录音] 录音测试后忘记继续录 → 先录1分钟测试→转录验证→确认录到才开始正式录制
- [八字分析] 宫位为主、星神为辅原则搞反了 → 用户纠正后修正，正确逻辑：先看宫位状态→宫位上的十神判断六亲处境→星只是辅助验证
- [八字分析] 审核没跑就直接发送报告 → 必须完成审核Agent校验后才能发送
- [八字分析] 癸水十神标注错误：甲木日主见癸水=正印（异性相生），不是偏印 → 审核Agent发现并修正
- [八字] JS脚本gender参数完全无效（始终女命），十神全错 → 必须手动重算
- [执行价采集] 中文命令截断 → 用英文脚本或写文件后执行
- [cron] symlink路径被Hermes安全机制拦截 → 将脚本复制到 profiles/main/scripts/ 下
- [飞书] boolean值序列化问题 → 用字符串"true"/"false"替代Python布尔值
- [飞书] Shell引号与markdown解析冲突：`***`被解析为粗斜体导致Authorization header截断 → 写脚本到文件再执行
- [teams] Graph订阅72小时过期 → 必须设置12小时自动续订
- [feishu] Callout块语法高亮创建后不可更改
- [feishu] 原生表格(block_type=20)无法通过API创建
- [douyin] 按钮索引偏移陷阱："最新作品"和"近期作品"区域有重复按钮
- [douyin] Python+MSYS中文编码陷阱：format字符串中的中文字符触发ValueError
- [course-notes] Agent4发现匹配错误时应发回Agent2（不是Agent3）
- [course-notes] macOS sed损坏文件：BSD sed与GNU sed不同 → 用patch或write_file替代
- [pdd] 1688一键铺货的shadow DOM无法可靠触发
- [pdd] Camofox无法访问PDD后台（检测非Chrome浏览器）
- [pokemon] 必须频繁使用Vision：每2-4步截一次图
- [audio-transcribe] Whisper CLI不在PATH → 使用显式Python路径
- [ascii-video] macOS Pillow textbbox()返回错误高度 → 用font.getmetrics()
- [xurl] 省略--app my-app → token会保存到错误的profile
- [touchdesigner] 绝对不要猜测参数名 → 调用td_get_par_info先确认
- [comfyui] API format required → editor格式JSON需转换为API格式
- [comfyui] 视频/音频工作流默认超时300秒 → 重型工作流需提升至900秒以上
- [kanban-worker] 任务状态可变：dispatch和startup之间可能被blocked → 先kanban_show确认
- [kanban-worker] 永远不要调用clarify → 会静默超时约120秒
- [hermes-config] 配置变更必须用hermes config set → 永远不要直接编辑config.yaml
- [cron-job-patterns] execute_code在cron环境中被禁用 → 必须用write_file+terminal
- [cron-job-patterns] clarify在cron中不可用 → 所有决策必须自主完成
- [cron-job-patterns] ~/.git-credentials可能为0字节 → push前检查
- [himalaya] v1.2.0文件夹别名语法变更：folder.aliases.X（复数）
- [airtable] filterByFormula必须URL编码
- [airtable] 批量端点限制10条/请求
- [python-debugpy] pdb在pytest-xdist下静默无效
- [systematic-debugging] 3+次修复失败 → 停下来质疑架构
- [hermes-agent-skill-authoring] skill_manage(action='create')用于仓库内skill是错误的 → 用write_file
- [hermes-agent-skill-authoring] `---`前不能有前导空格 → 必须从字节0开始
- [test-driven-development] 测试后写的测试立即通过 → 什么也证明不了
- [analyze-image] 长图必须切割：长宽比>3或高度>8000px → 用full_extract.py按3000px分段
- [audio-transcribe] Whisper领域特定听错表：鬼害→癸亥、鬼水→癸水、人鬼水→壬癸水
- [macos-audio-recording] Mac Mini默认输出是内置扬声器而非HDMI → 用system_profiler确认
- [macos-audio-recording] ffmpeg avfoundation+BlackHole录制不稳定 → 用sounddevice替代
- [macos-audio-recording] 删除聚合设备后系统可能将默认输出重定向到无效ID → 每次操作后重新查询
- [feishu-oauth] Refresh token有效期30天 → 过期后需重新走完整授权流程
- [bazi] 排盘数据源必须用JS脚本 → 绝对禁止用Python手算或AI直接推算
- Agent错误断言"Ollama转录不了" → 给结论前必须验证，不要凭印象给断言性结论

### 新发现

#### Skill 内新发现

- [hermes-agent] Diagnostic 平台误报：检查最近日志条目而非历史条目，避免false positive
- [hermes-agent] Auxiliary models（vision/compression/session_search）需单独配置provider和model
- [ocr-courseware] 切片高度2000px是OCR最佳平衡点
- [course-notes-docx] Markdown表格转换：需在docx生成脚本中加入表格解析逻辑，否则课件核心表格全部丢失
- [dingtalk-live] 钉钉直播间自动化完整流程：隐藏Finder→强制钉钉前台→截图vision_analyze定位→点击黄色提示条→启动录音

#### 历史新发现（06-17 至 06-27）

- 选股周报：本周多数个股冲高回落，持仓20只平均+2.8%，金房能源-9.1%建议止损
- 八字宫位分析法新发现：分析六亲不看对应十神旺不旺，而是看宫位上的内容对十神的作用
- 八字销售流程优化：从旧流程→八层体系（排盘/格局/性格/天赋/六亲/专项/大运/调理）
- 八字进阶Day72-99学习笔记整理为"进阶断语速查"
- 选股系统V3：评分和风险完全分离，风险是诊断工具不是门卫
- 选股执行价周一对比：75%的股票周一买更便宜，等待一天平均多付+3.54%
- 双数据源备选策略：东方财富API优先，腾讯API备用
- bazi-muku墓库避坑规则：不见财库就说"有财库"；不见冲就说"开库"
- bazi-kongwang空亡分析：空亡查法、五行空亡断语、填实方法
- dbs-diagnosis语言陷阱检测：~25%的复杂问题是语言陷阱
- 小红书采集：必须用/search_result/链接（带xsec_token）
- TouchDesigner许可证限制：Non-Commercial TD caps resolution at 1280×1280
- H.264/H.265/AV1需要Commercial license → macOS用prores替代
- 知识库.md优先于.json → JSON可能有错误
- 五行归类要按易学体系（易学本体属水/传播属火）
- HermesMO多输出设备（BlackHole+Mac mini扬声器）验证成功
- 持续录制脚本record_live.py每5分钟自动保存WAV文件
- Whisper medium模型首次运行需下载~1.5GB
- 浏览器工具已升级为agent-browser 0.28.0+Chrome 150
- Gemma4音频识别方案：用images参数传音频（不是audio参数），需要think:false
- 长音频（>30分钟）建议后台运行：CPU转录93分钟音频约需30-50分钟
- llama.cpp/LM Studio/Ollama三者对比：llama.cpp最灵活但需手动配置、LM Studio图形界面友好、Ollama最简单但功能有限
- 风险监控：持仓20只无严重风险事件，减持已释放，质押需关注比例

### 用户偏好更新

- 用户对"失忆"极度敏感 → 每次执行操作前必须先查现有skill
- 不要乐观时间估计：说诚实的时长
- 不要部分交付：必须100%完成后才能交付
- 直接执行："你做一下"意味着立即开始，不要确认性提问
- 进度汇报只在50%、80%、100%时报告
- 写完文案必须自动跑video-content-audit审核
- 栋笃笑文案用"阿强"做叙事载体，开头第一句必须是选题
- 过三关遇到女命必须额外加载bazi-fukeshengyu skill
- 用户改完文案就是终版，不要自作主张加回删掉的内容
- 录音不要反复测试，确认录到就开始
- 字数估算时长（粤语4字/秒）
- 不要给不切实际的乐观时间估算
- 视频内容工作流：选身边小事引发共鸣，必须走完整4阶段
- 文案修改偏好：简洁删排比、台词口语化、节奏快
- 小红书访问笔记详情必须用/search_result/链接
- Mac → GitHub 需要 SOCKS5 代理 `socks5h://127.0.0.1:7897`
- 配置变更必须用 `hermes config set`，永远不要直接编辑config.yaml

### Skill 更新

- [06-25] bazi-zhiduan：新增"进阶断语速查"参考文件（Day72-99学习笔记）、修正"宫位星神配合判断.md"（宫位为主，星神为辅）
- [06-25] bazi-analysis：分析步骤模板新增每个Phase标注需要加载的速查表 + 场景→速查表映射表
- [06-25] bazi-sales-agent1-parsing：输出从旧格式→八层layer1-layer8特征卡
- [06-25] bazi-sales-agent1-diagnosis：4步流程→八层体系（排盘/格局/性格/天赋/六亲/专项/大运/调理）
- [06-25] bazi-sales-agent2-speechcraft：输入输出对齐八层，话术按layer顺序生成
- [06-25] bazi-sales-agent5-speechgeneration：开场→性格，校准→六亲，深入→运势，成交→调理
- [06-25] bazi-sales-orchestrator：状态机从9步→10步，八层分析独立为状态3
- [06-25] bazi-sales-validator：新增第5项八层数据匹配验证
