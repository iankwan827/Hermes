# Hermes 使用经验日志

## 2026-06-26

### 踩坑记录
- [录音] Gemini转录进程卡死：八字分析session中Gemini进程卡在0% CPU不动 → 换用Whisper替代，Gemini音频处理不稳定
- [录音] 旧录音进程未清理：6月18日的录音进程仍在后台运行（已到part2274），文件名还是旧日期 → 杀掉旧进程后用当天日期重新开始录音，定期检查后台进程

### 新发现
- 选股周报：本周多数个股冲高回落，持仓20只平均+2.8%，金房能源-9.1%建议止损
- [八字] JS脚本gender参数完全无效（始终女命），十神全错 → 必须手动重算，这是已知但未记录到经验日志的坑

### 用户偏好更新
- 无新增偏好

---

## 2026-06-25

### 踩坑记录
- [八字分析] 宫位为主、星神为辅原则搞反了——之前错误地以星为主、宫位为辅 → 用户纠正后修正 bazi-zhiduan 的"宫位星神配合判断.md"，正确逻辑：先看宫位状态→宫位上的十神判断六亲处境→星只是辅助验证
- [八字分析] 审核没跑就直接发送报告——用户指出"为啥待审核就发送出来了" → 必须完成审核Agent校验后才能发送，不能跳步
- [八字分析] 癸水十神标注错误：甲木日主见癸水=正印（异性相生），不是偏印 → 审核Agent发现并修正

### 新发现
- [八字分析] 知识点分散在多个速查表里容易漏加载——解决方案：在每个Phase标注需要加载的速查表，末尾加场景→速查表映射表（命局旺衰→天干地支取象速查、婚姻分析→四柱代表+宫位星神配合判断等）
- [八字销售] 流程优化：从旧流程（排盘→格局→用神忌神→话术→质检→成交）→八层体系（排盘/格局/性格/天赋/六亲/专项/大运/调理），中间加入"人"的刻画，诊断报告更完整
- [八字销售] 5个Agent对齐八层体系：agent1-parsing输出八层特征卡、agent1-diagnosis→八层分析、agent2-speechcraft输入输出对齐八层、agent5-speechgeneration按layer顺序生成、orchestrator状态机9步→10步、validator新增八层数据匹配验证
- [八字进阶] Day72-99学习笔记整理为"进阶断语速查"：食伤vs偏印创造方式对比（食伤主动创造、偏印先模仿后创新）、身旺抗压强vs身弱定力差易崩溃、地支刑害多人际差、印旺冷漠缺乏共情

### Skill 更新
- bazi-zhiduan：新增"进阶断语速查"参考文件（Day72-99学习笔记）、修正"宫位星神配合判断.md"（宫位为主，星神为辅）
- bazi-analysis：分析步骤模板新增每个Phase标注需要加载的速查表 + 场景→速查表映射表
- bazi-sales-agent1-parsing：输出从旧格式→八层layer1-layer8特征卡
- bazi-sales-agent1-diagnosis：4步流程→八层体系（排盘/格局/性格/天赋/六亲/专项/大运/调理）
- bazi-sales-agent2-speechcraft：输入输出对齐八层，话术按layer顺序生成
- bazi-sales-agent5-speechgeneration：开场→性格，校准→六亲，深入→运势，成交→调理
- bazi-sales-orchestrator：状态机从9步→10步，八层分析独立为状态3
- bazi-sales-validator：新增第5项八层数据匹配验证

---

## 2026-06-24

### 踩坑记录
- 无新增踩坑记录

### 新发现
- 风险监控：持仓20只无严重风险事件（株冶集团/四川黄金减持已完成或届满）

---

## 2026-06-23

### 踩坑记录
- [录音] 录音skill"失忆"——已有 macos-audio-recording skill 和 record.py，但没先查skill就自己写脚本，用了错误的采样率(44100Hz vs 16000Hz) → 用户原话"你又对录音失忆了"

### 新发现
- 选股执行价周一对比：75%的股票周一买更便宜，等待一天平均多付+3.54% → 应当日立即挂单
- 追高风险TOP3：花园生物+29.41%、株冶集团+20.99%、南大光电+15.44%
- 风险监控：持仓20只无严重风险事件，减持已释放，质押需关注比例

### 用户偏好更新
- 用户对"失忆"极度敏感 → 每次执行操作前必须先查现有skill

---

## 2026-06-22

### 踩坑记录
- [执行价采集] capture_execution.py 中文命令截断 → 用英文脚本或写文件后执行
- [录音] 录音测试后忘记继续录 → 先录1分钟测试→转录验证→确认录到才开始正式录制
- [cron] symlink路径被Hermes安全机制拦截 → 将脚本复制到 profiles/main/scripts/ 下
- [飞书] boolean值序列化问题 → 用字符串"true"/"false"替代Python布尔值
- [飞书] spreadsheet range格式错误 → 查阅API文档确认正确格式

### 新发现
- 双数据源备选策略：东方财富API优先，腾讯API备用
- 录音振幅验证：sounddevice录制15秒，最大振幅0.5484，Whisper转录确认
- 飞书执行价更新流程：OAuth→token→spreadsheet API
- 选股数据：平均滑点+0.68%（周一开盘）

### 用户偏好更新
- 录音不要反复测试，确认录到就开始
- 用户对"失忆"敏感 → 每次操作前查skill
- 字数估算时长（粤语4字/秒）

---

## 2026-06-21

### 踩坑记录
- [analyze-image] exec()环境变量陷阱：exec(open(...).read())不会加载环境变量 → 用terminal工具
- [analyze-image] 中文数字匹配陷阱：课程编号搜索必须从长到短匹配
- [analyze-image] 长图必须切割：长宽比>3或高度>8000px → 用full_extract.py按3000px分段
- [douyin] 按钮索引偏移陷阱："最新作品"和"近期作品"区域有重复按钮
- [douyin] Python+MSYS中文编码陷阱：format字符串中的中文字符触发ValueError
- [course-notes] 回退陷阱：Agent4发现匹配错误时应发回Agent2（不是Agent3）
- [course-notes] macOS sed损坏文件：BSD sed与GNU sed不同 → 用patch或write_file替代
- [teams] Graph订阅72小时过期 → 必须设置12小时自动续订
- [feishu] Callout块语法高亮创建后不可更改
- [feishu] 原生表格(block_type=20)无法通过API创建
- [pdd] 1688一键铺货的shadow DOM无法可靠触发
- [pdd] Camofox无法访问PDD后台（检测非Chrome浏览器）
- [pokemon] 必须频繁使用Vision：每2-4步截一次图
- [audio-transcribe] Whisper CLI不在PATH → 使用显式Python路径
- [ascii-video] macOS Pillow textbbox()返回错误高度 → 用font.getmetrics()
- [xurl] 省略--app my-app → token会保存到错误的profile

### 新发现
- bazi-muku墓库避坑规则：不见财库就说"有财库"；不见冲就说"开库"
- bazi-kongwang空亡分析：空亡查法、五行空亡断语、填实方法
- dbs-diagnosis语言陷阱检测：~25%的复杂问题是语言陷阱
- 小红书采集：必须用/search_result/链接（带xsec_token）
- 选股系统：两池(稳健/成长)，周频策略，周五15:30出信号

### 用户偏好更新
- 用hermes config set改配置，永远不要直接编辑config.yaml
- 进度汇报只在50%、80%、100%时报告
- 写完文案必须自动跑video-content-audit审核
- 栋笃笑文案用"阿强"做叙事载体，开头第一句必须是选题
- 过三关遇到女命必须额外加载bazi-fukeshengyu skill

---

## 2026-06-20

### 踩坑记录
- Agent错误断言"Ollama转录不了" → 给结论前必须验证，不要凭印象给断言性结论
- 录音skill从20KB拆分为3.2KB核心+references+scripts
- 录音测试后忘记继续录 → 确认录到才开始正式录制

### 新发现
- llama.cpp/LM Studio/Ollama三者对比：llama.cpp最灵活但需手动配置、LM Studio图形界面友好、Ollama最简单但功能有限
- Gemma4音频识别方案：用images参数传音频（不是audio参数），需要think:false
- 长音频（>30分钟）建议后台运行：CPU转录93分钟音频约需30-50分钟

---

## 2026-06-19

### 踩坑记录
- [feishu] Shell引号与markdown解析冲突：`***`会被解析为粗斜体导致Authorization header截断 → 写脚本到文件再执行
- [teams] Graph subscriptions在72小时后过期且不自动续期
- [audio-transcribe] Whisper领域特定听错表：鬼害→癸亥、鬼水→癸水、人鬼水→壬癸水
- [bazi] 排盘数据源必须用JS脚本 → 绝对禁止用Python手算或AI直接推算
- [touchdesigner] 绝对不要猜测参数名 → 调用td_get_par_info先确认
- [comfyui] API format required → editor格式JSON需转换为API格式
- [kanban-worker] 任务状态可变：dispatch和startup之间可能被blocked → 先kanban_show确认
- [hermes-config] 配置变更必须用hermes config set → 永远不要直接编辑config.yaml

### 新发现
- TouchDesigner许可证限制：Non-Commercial TD caps resolution at 1280×1280
- H.264/H.265/AV1需要Commercial license → macOS用prores替代
- 知识库.md优先于.json → JSON可能有错误
- 五行归类要按易学体系（易学本体属水/传播属火）

### 用户偏好更新
- 不要给不切实际的乐观时间估算
- 视频内容工作流：选身边小事引发共鸣，必须走完整4阶段
- 文案修改偏好：简洁删排比、台词口语化、节奏快
- 用户改完文案就是终版，不要自作主张加回删掉的内容
- 小红书访问笔记详情必须用/search_result/链接

---

## 2026-06-18

### 踩坑记录
- [macos-audio-recording] Mac Mini默认输出是内置扬声器而非HDMI → 用system_profiler确认
- [macos-audio-recording] ffmpeg avfoundation+BlackHole录制不稳定 → 用sounddevice替代
- [macos-audio-recording] 删除聚合设备后系统可能将默认输出重定向到无效ID → 每次操作后重新查询
- [feishu-oauth] Refresh token有效期30天 → 过期后需重新走完整授权流程
- [cron-job-patterns] github-sync.sh脚本路径验证问题

### 新发现
- HermesMO多输出设备（BlackHole+Mac mini扬声器）验证成功
- 持续录制脚本record_live.py每5分钟自动保存WAV文件
- Whisper medium模型首次运行需下载~1.5GB
- 浏览器工具已升级为agent-browser 0.28.0+Chrome 150

---

## 2026-06-17

### 踩坑记录
- [cron-job-patterns] execute_code在cron环境中被禁用 → 必须用write_file+terminal
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
