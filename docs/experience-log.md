# Hermes 使用经验日志

> 自动生成于 2026-07-07，汇总 Skills 经验教训 + 近期会话踩坑记录

---

## 2026-07-07

### 踩坑记录
- [课件笔记/OCR] tesseract对中文专业术语（八字命理）识别率极低，形近字错误频发（"肺痨"→"肺许"，"逢三冲"→"估三冲"）→ 正确流程：tesseract定位章节 → vision_analyze逐字识别 → 修正后写入笔记
- [课件笔记] 必须对照课件逐点核对，不能边写边传 → 写完直接上传导致遗漏整个章节（只写了3个点，实际有8个点）。正确流程：先完整OCR → 列目录确认 → 再动笔 → 每章核对 → 全部完成再传
- [课件笔记/OCR切片] 8426px高的图片用2000px切片太粗，漏了中间第4-7点 → 改用600-800px切片
- [八字笔记] 用户纠正"辛金具体知识点"不应作为通用规则 → 改为通用检查清单（目录完整性、关键词完整性、表格完整性、题外话提取、上传前格式检查）

### 新发现
- [飞书集成] 完整的token管理经验库：29条飞书相关教训，涵盖token刷新、OAuth流程、表格操作、文档block类型等
- [选股系统] 26条选股相关教训，涵盖数据源差异、飞书写入、datetime比较、risk_monitor流程等
- [八字系统] 3个八字skill的避坑指南（宫穿、直断、审核），含用户原话纠正

### Skill 更新
- 汇总14个skill的经验教训，共计~115条踩坑记录

---

## 2026-07-06

### 踩坑记录
- [八字系统] 6个八字skill目录存在但SKILL.md缺失：bazi-dinghuo、bazi-duanpeifu、bazi-gongchuan、bazi-hunyin-cishu、bazi-ganbing、bazi-xinzangbing → 需要补全SKILL.md才能正常被加载
- [八字笔记] "看skill开始录音"被误解为看八字skill一览表 → 用户原话"啥啊，我要你看录音skill啊"，应直接加载macos-audio-recording skill

### 新发现
- [执行价采集] 周一开盘数据：40只股票，平均滑点+0.10%，16涨24跌（跌多涨少）。最大正滑点+3.92%（快克智能追高），最大负滑点-4.30%（艾迪精密低开）。低开的股票开盘后继续走低（如艾迪开盘后又跌-2.8%），追高的反而可能继续走强（如快克开盘后又涨+5.3%）
- [八字系统] 完整skill架构梳理：7个Agent + 25个分析skill + 2个框架skill + 5个其他skill = 共39个八字相关skill

### 用户偏好更新
- 用户说"看skill开始录音"=加载录音skill开始录音，不是查看skill列表

---

## 2026-07-05

### 踩坑记录
- [语录追加] **第四次**忘记追加语录文件！用户发送Day81-99课程内容后，只回复了整理要点，没有自动追加到语录文件。用户原话"你又忘记语录了" → 收到课程内容必须立即追加到 `~/Pictures/八字课/语录/理华老师语录.md`，不用等用户说
- [课件笔记格式] 第十一课笔记中🎙️块内嵌套了###标题，导致飞书上传时orange块只显示几行内容 → 脚本已修复（遇到###不再break），但生成笔记时仍建议保持第十课格式（每段用---分隔，不用###嵌套在🎙️块内）
- [八字排盘错误] 案例一（木子）排盘搞错：日元庚金→应为丙火，日支寅木→应为申金。根因：没有以转录稿为准，自己推断排盘。用户原话"应该是丙火日元，丙申日柱，申金也是财星" → 案例排盘必须以转录稿为准，不能自己推断
- [飞书上传] Token过期导致上传失败 → 需先运行 `refresh_token.py` 刷新token再上传
- [飞书案例修正] 飞书文档中三个案例解释都是错的，重新上传修正版（237个block全部成功）

### 新发现
- [八字案例] 申亥穿分析修正：案例一（木子）是星宫同宫（申金既是夫妻宫也是夫妻星）被亥水穿，不是宫星相穿。案例二（孟川）有亥卯半合+申子半合化解穿害，婚姻不会动摇根基
- [八字系统] 审核agent新增侧写审核（8️⃣），逐条检查侧写文本中的每个判断是否与JSON数据一致。正印写成偏印这种错误会被拦住

### 用户偏好更新
- 课件笔记格式：🎙️块内不要嵌套###标题。第十课格式（每段用---分隔）是正确的
- 课件和转录要分开处理别搞混（如课件第十课、转录第十一课）
- 整理笔记时要对比前一课的格式，发现差异先修脚本或统一格式再上传

### Skill 更新
- `upload_notes.py` 脚本修复：遇到###不再break，支持🎙️块内有子标题的格式

---

## 2026-07-04

### 踩坑记录
- [GitHub 同步] clone 超时（120s）→ 使用 `--filter=blob:none` 或 `--depth 1` 解决
- [cron 环境] cron 环境 clone 大仓库超时 → 使用浅克隆 `--depth 1`

### 新发现
- 无新增

---

## 2026-07-03

### 踩坑记录
- [macos-browser-cdp] `cp -R` 复制Chrome profile会丢失cookies等登录态 → 改用 `rsync -a`（保留文件权限、时间戳和特殊属性）
- [GitHub 同步] `~/.git-credentials` 可能为空文件（0 bytes）→ 推送前先用 `wc -c` 检查
- [飞书集成] OIDC refresh endpoint要求 `tenant_access_token` 作为 `Authorization: Bearer` header，不是放在request body里。错误症状：`{"code": 20014}`
- [飞书集成] `redirect_uri` 必须精确匹配 `http://localhost:8765`，不能加 `/callback`
- [飞书集成] `refresh_token` 30天过期 + 单次使用。过期后必须重新走OAuth授权流程
- [飞书集成] Token过期 → 自动执行OAuth，不要问用户。用户原话"你是不是有毛病，授权一直都是你自己点的"
- [飞书集成] Shell引号 + markdown `***` 冲突 → 始终先写Python脚本到文件再执行
- [钉钉直播] Finder窗口遮挡DingTalk（高频！）→ 激活DingTalk前必须先隐藏Finder
- [钉钉直播] vision_analyze严重误判截图内容（将钉钉直播间识别为飞书文档）→ 截图后必须让用户确认，不要用AI描述屏幕内容
- [钉钉直播] 多进程record.py冲突BlackHole音频设备 → 启动前必须 `pkill -f "record.py"`
- [选股系统] datetime比较必须用 `.date()` → `day_date >= monday` 因时间分量失败
- [选股系统] Feishu写入必须用 `user_access_token`，`tenant_token` 只能读
- [选股系统] `update_feishu_sheet.py` O/P列数据源错误 → O列应为周一开盘价（非收盘价）
- [图片分析] 长图直接发给vision_analyze会丢失50-70%内容 → 强制流程：`Image.open → .size → h>2000? → slice → 逐段识别`，2000px切片高度最优
- [图片分析] >20M像素图片需先缩放，否则MemoryError

### 新发现
- [飞书集成] Chrome CDP连接成功方案：杀掉所有Chrome → rsync profile到 `/tmp/chrome-cdp-profile` → 用 `--remote-debugging-port=9222 --user-data-dir` 启动
- [飞书集成] 完整的block_type参考：2=段落、12=无序列表、22=分割线、34=纯文本code block
- [飞书集成] `folder_token=""` 表示根目录，不是null
- [飞书集成] `tenant` vs `user` token用途：drive操作用tenant，doc操作用user
- [飞书集成] CSV有BOM → 读取时用 `encoding='utf-8-sig'`
- [选股系统] 突破计算用60日最高价，不用120日绝对最高价
- [选股系统] B规则卖出：必须连续2周出Top20，累计触发不算
- [选股系统] 大幅回调>20%时不适用突破判断
- [选股系统] 被剔除的股票必须红色高亮 + 追加在表末尾（row 21+），字体色 `#FF0000`
- [选股系统] `risk_monitor.py` 现在会自动扫描被剔除的股票
- [选股系统] 更新飞书表格后**必须**运行risk_monitor，不能跳过
- [选股系统] 历史比较用 `recent[0]`（最早记录），不用 `recent[-2]`
- [选股系统] risk诊断不是门槛工具，只在与上周对比时触发
- [选股系统] `history.json` 需要存top20和top20_scores，不能只存top5
- [AStock数据] Sina API的 `node=hs_a` 包含北交所(92xxx)股票，必须按板块过滤
- [AStock数据] macOS系统代理(Clash 127.0.0.1:7897)导致东方财富API请求失败 → 用 `curl --noproxy '*'` 或Sina API
- [AStock数据] 腾讯实时API返回GBK编码 → 必须 `decode('gbk')`
- [AStock数据] Sina K线API只返回约300天数据（scale=240=daily），不是全量历史

### 用户偏好更新
- Mac SSH连不上（port 22 refused）→ 不要尝试SSH到Mac，有需要直接看GitHub仓库
- Chrome 反复开关很烦 → 不要无意义地重复启动/关闭浏览器
- "你是不是有毛病" = 用户不耐烦的信号，停止当前操作
- 飞书"创建表格不是文档" → 创建spreadsheet，不是document。不同API

### Skill 更新
- `macos-browser-cdp`: 复制profile命令从 `cp -R` 改成 `rsync -a`（SKILL.md + scripts + references 3个文件同步更新）

---

## 2026-07-02

### 踩坑记录
- [图片分析] 长图直接发给vision_analyze会丢失50-70%内容 → 强制流程：`Image.open → .size → h>2000? → slice → 逐段识别`，2000px切片高度最优
- [图片分析] >20M像素图片需先缩放，否则MemoryError
- [拼多多] Shadow DOM阻止自动化（sl-checkbox/sl-button）→ 必须手动操作
- [拼多多] 编辑页面必须立即提交，否则页面刷新后所有修改丢失
- [拼多多] PDD要求图片<3MB → 用PIL quality参数压缩
- [macOS] **绝不运行** `tccutil reset ScreenCapture` — 会移除所有应用的屏幕录制权限，不可逆
- [TouchDesigner] 同名节点在同一脚本中销毁+重建会导致 "Invalid OP object" → 拆分为独立MCP调用
- [Teams] Graph webhook订阅72小时后过期 → 设置12小时间隔的续期cron

### 新发现
- [选股回测] 行业分散规则（行业≤2）将第一池收益率从-5.56%提升到-2.99%（+2.57pp）
- [选股回测] 周二开盘优于周一（+1.29pp）

### 用户偏好更新
- 转录用gemma模型（不用whisper）
- 八字十天干性格分类（不用五行）
- 🎙️表情符号和内容分两行显示

### Skill 更新
- 新建 `llm-provider-fix` skill（LLM provider 401/402错误诊断）

---

## 跨日期通用经验汇总（来自 Skills）

### 飞书集成（29条教训）
- Token管理：refresh_token单次使用+30天过期，OAuth自动执行不要问用户
- 表格操作：sheet_id必须查询获取（"Sheet1"不行），批量写入可能静默失败，逐行写更安全
- 文档block：block_type=2段落、12无序列表、22分割线、34纯文本code block
- 权限：新scope需要重新授权（不只是token刷新）
- macOS OAuth：用AppleScript控制Chrome，不用headless browser

### 选股系统（26条教训）
- datetime比较必须 `.date()`
- 飞书写入用 `user_access_token`
- 被剔除股票红色高亮 + 表末尾追加
- 更新后必须运行risk_monitor
- `history.json` 存top20和top20_scores

### AStock数据（6条教训）
- 必须按板块过滤（排除北交所92xxx）
- macOS代理会干扰API请求
- 腾讯API返回GBK编码

### 钉钉直播（10条教训）
- Finder遮挡DingTalk（最高频！）
- vision_analyze误判截图（不可信）
- 多进程record.py冲突BlackHole

### 八字系统（10条教训）
- 穿≠必离婚（需宫星同穿+旺衰失衡+无制化三者同时满足）
- 直断不能只扫描28秘诀（必须扫描全部查找表）
- 审核agent逐条校验侧写文本

### 课件笔记（8条教训）
- OCR必须逐字校对（tesseract对中文专业术语不可靠）
- 不能边写边传（必须先完成再上传）
- 🎙️块内不嵌套###标题
- 长图切片600-800px（2000px太粗）

### 其他
- `write_file` 破坏Python引号 → 改用terminal heredoc
- macOS `tccutil reset ScreenCapture` 不可逆
- Teams Graph订阅72小时过期
- 代码review不要超过3个reviewer

---

*本日志由 Hermes 经验同步 cron 任务自动生成*
