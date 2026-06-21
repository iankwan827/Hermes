# Hermes 使用经验日志

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
